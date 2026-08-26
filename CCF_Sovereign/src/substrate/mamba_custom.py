"""
Custom Mamba Selective State Space Model — Pure PyTorch Implementation.

Built from the foundational logic of the Mamba architecture (Gu & Dao, 2023)
without dependency on mamba_ssm or platform-specific CUDA kernels.

Core Insight: State Space Models use a linear recurrence with INPUT-DEPENDENT
parameters (Selective Scan). This makes the model content-aware — it chooses
what to remember and what to forget based on the input itself.

The recurrence at each timestep:
    h[t] = Ā[t] · h[t-1] + B̄[t] · x[t]     (state update)
    y[t] = C[t] · h[t]                        (output)

Where Ā = exp(Δ·A), B̄ = Δ·B, and Δ, B, C are all projected from the input.
A is the only purely learned parameter — the state transition matrix.

Architecture of each MambaBlock:
    input → RMSNorm → Linear → [x_path, z_gate]
                                    ↓          ↓
                              Conv1d→SiLU   SiLU
                                    ↓          ↓
                            Selective_Scan     ↓
                                    ↓          ↓
                                  (multiply)───┘
                                    ↓
                                 Linear → + residual → output

Sovereign Mind Application:
    This replaces the LSTM fallback as the temporal backbone of the CCF Substrate.
    The selective scan IS the attention mechanism — but O(L) instead of O(L²).
    The hidden state h IS the chrono-compressive field — a living compression
    of everything the mind has seen, continuously overwritten and refined.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple

from .selective_scan import DEFAULT_SCAN_CHUNK_SIZE, chunked_selective_scan


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization.

    More stable than LayerNorm for SSMs — no mean subtraction,
    just scale normalization. The mind doesn't center itself,
    it scales its awareness.
    """
    def __init__(self, d_model: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(d_model))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        rms = torch.sqrt(torch.mean(x * x, dim=-1, keepdim=True) + self.eps)
        return (x / rms) * self.weight


class SelectiveScan(nn.Module):
    """
    The Core Algorithm — Selective State Space Scan.

    This is where the magic lives. A parallel scan that implements
    the discretized state space recurrence with input-dependent parameters.

    Every timestep, the model decides:
      - HOW MUCH to remember (via Δ — the discretization step)
      - WHAT to let in (via B — the input gate)
      - WHAT to output (via C — the output gate)
      - WHAT the state dynamics are (via A — the state transition)

    This is content-aware linear recurrence. Not a fixed filter.
    The mind selects what matters.

    Uses Hillis-Steele parallel inclusive scan for O(log L) sequential
    steps instead of O(L). The binary operator is:
        (a1, b1) ⊗ (a2, b2) = (a1·a2, a2·b1 + b2)
    """

    @staticmethod
    def _parallel_scan(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        """
        Parallel prefix scan for linear recurrence h[t] = a[t]*h[t-1] + b[t].

        Uses Hillis-Steele inclusive scan: O(L log L) work, O(log L) steps.

        Args:
            a: (B, L, D, N) — multiplicative coefficients (deltaA, all in [0,1])
            b: (B, L, D, N) — additive terms (deltaB_x)
        Returns:
            h: (B, L, D, N) — all hidden states
        """
        L = a.shape[1]
        num_steps = int(math.ceil(math.log2(max(L, 2))))

        for d in range(num_steps):
            stride = 2 ** d
            if stride >= L:
                break

            # Predecessors and current elements
            a_pred = a[:, :-stride]   # (B, L-stride, D, N)
            b_pred = b[:, :-stride]
            a_curr = a[:, stride:]    # (B, L-stride, D, N)
            b_curr = b[:, stride:]

            # Associative operator: (a_pred, b_pred) ⊗ (a_curr, b_curr)
            new_a = a_pred * a_curr
            new_b = a_curr * b_pred + b_curr

            # Rebuild full sequence (prefix unchanged, suffix updated)
            a = torch.cat([a[:, :stride], new_a], dim=1)
            b = torch.cat([b[:, :stride], new_b], dim=1)

        return b

    @staticmethod
    def forward_scan_reference(
        x: torch.Tensor,       # (B, L, D) — input sequence
        delta: torch.Tensor,    # (B, L, D) — discretization step
        A: torch.Tensor,        # (D, N) — state transition (negative, learned)
        B: torch.Tensor,        # (B, L, N) — input projection (selective)
        C: torch.Tensor,        # (B, L, N) — output projection (selective)
        D: torch.Tensor,        # (D,) — skip connection
    ) -> torch.Tensor:
        """
        Execute the selective scan using parallel prefix algorithm.

        Discretization (Zero-Order Hold):
            Ā[t] = exp(Δ[t] · A)          — how much old state survives
            B̄[t] = Δ[t] · B[t]           — how much new input enters

        Scan (computed in parallel via associative scan):
            h[t] = Ā[t] ⊙ h[t-1] + B̄[t] ⊙ x[t]   — state update
            y[t] = (C[t] · h[t]).sum()                — read from state

        Returns: y — (B, L, D)
        """
        batch, seq_len, d_inner = x.shape
        d_state = A.shape[1]

        # Discretize A: Ā = exp(Δ · A)
        # delta: (B, L, D, 1) * A: (1, 1, D, N) → (B, L, D, N)
        deltaA = torch.exp(
            delta.unsqueeze(-1) * A.unsqueeze(0).unsqueeze(0)
        )

        # Discretize B·x: B̄·x = Δ · B · x
        # delta: (B, L, D, 1) * B: (B, L, 1, N) * x: (B, L, D, 1) → (B, L, D, N)
        deltaB_x = (
            delta.unsqueeze(-1) *
            B.unsqueeze(2) *
            x.unsqueeze(-1)
        )

        # --- Parallel Associative Scan ---
        # h[t] = deltaA[t] * h[t-1] + deltaB_x[t]
        # This is computed for ALL t simultaneously using log(L) parallel steps
        h = SelectiveScan._parallel_scan(deltaA, deltaB_x)  # (B, L, D, N)

        # Output: y[t] = C[t] · h[t] (contract over state dimension)
        # h: (B, L, D, N), C: (B, L, N) → (B, L, 1, N) for broadcast
        y = (h * C.unsqueeze(2)).sum(dim=-1)  # (B, L, D)

        # Skip connection: y += D · x
        y = y + x * D.unsqueeze(0).unsqueeze(0)

        return y

    @staticmethod
    def forward_scan(
        x: torch.Tensor,
        delta: torch.Tensor,
        A: torch.Tensor,
        B: torch.Tensor,
        C: torch.Tensor,
        D: torch.Tensor,
        *,
        chunk_size: int = DEFAULT_SCAN_CHUNK_SIZE,
    ) -> torch.Tensor:
        """Execute the memory-bounded production scan.

        The full-state Hillis–Steele implementation remains available only as
        ``forward_scan_reference`` for differential tests.
        """
        return chunked_selective_scan(
            x,
            delta,
            A,
            B,
            C,
            D,
            chunk_size=chunk_size,
        )


class MambaBlock(nn.Module):
    """
    Single Mamba Block — the fundamental unit of the Sovereign Mind's backbone.

    This block replaces a Transformer layer or LSTM layer. It provides:
      - Content-aware (selective) sequence processing via SSM
      - Local context via causal depthwise convolution
      - Gated output for controlling information flow
      - Residual connection for gradient health

    All in O(L) time complexity. No quadratic attention.

    Parameters:
        d_model: Input/output dimension of the block
        d_state: SSM state expansion factor (N). Higher = more memory capacity.
                 Each channel maintains N parallel state variables.
        d_conv: Causal convolution kernel width. Provides local context
                before the SSM processes the sequence globally.
        expand: Block expansion factor. d_inner = expand * d_model.
                Higher = more expressive but more parameters.
    """

    def __init__(
        self,
        d_model: int,
        d_state: int = 16,
        d_conv: int = 4,
        expand: int = 2
    ):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_conv = d_conv
        self.d_inner = int(expand * d_model)
        self.dt_rank = max(1, d_model // 16)

        # ── Pre-normalization ──
        self.norm = RMSNorm(d_model)

        # ── Input projection: d_model → 2·d_inner ──
        # Splits into x_path (goes through conv+SSM) and z (gate)
        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)

        # ── Causal Depthwise Conv1d ──
        # Provides local positional context before the global SSM scan.
        # Depthwise = each channel convolved independently.
        self.conv1d = nn.Conv1d(
            in_channels=self.d_inner,
            out_channels=self.d_inner,
            kernel_size=d_conv,
            groups=self.d_inner,  # Depthwise
            padding=d_conv - 1,   # Left-pad for causality (trim later)
            bias=True
        )

        # ── SSM Parameter Projections ──
        # From x, project to (dt, B, C) — all input-dependent
        self.x_proj = nn.Linear(
            self.d_inner,
            self.dt_rank + self.d_state * 2,  # dt_rank for Δ, d_state for B, d_state for C
            bias=False
        )

        # dt bottleneck: dt_rank → d_inner
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)

        # ── A: State Transition Matrix (learned in log-space) ──
        # Initialized as structured matrix: A[i,j] = -(j+1) for all channels i
        # This creates a natural exponential decay with different timescales
        # per state dimension — short memory in low states, long in high states.
        A = torch.arange(1, d_state + 1, dtype=torch.float32)
        A = A.unsqueeze(0).expand(self.d_inner, -1)  # (d_inner, d_state)
        self.A_log = nn.Parameter(torch.log(A))

        # ── D: Skip Connection ──
        self.D = nn.Parameter(torch.ones(self.d_inner))

        # ── Output Projection ──
        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)

        # ── Initialization ──
        self._init_weights()

    def _init_weights(self):
        """Mamba-specific weight initialization."""
        # dt_proj bias: initialize so initial Δ values are in [0.001, 0.1]
        # This ensures the SSM starts with reasonable time-step sizes
        dt_init_std = self.dt_rank ** -0.5
        nn.init.uniform_(self.dt_proj.weight, -dt_init_std, dt_init_std)

        # Inverse softplus of uniform samples in [0.001, 0.1]
        dt = torch.exp(
            torch.rand(self.d_inner) * (math.log(0.1) - math.log(0.001))
            + math.log(0.001)
        )
        inv_dt = dt + torch.log(-torch.expm1(-dt))
        with torch.no_grad():
            self.dt_proj.bias.copy_(inv_dt)

        # x_proj: small init for stability
        nn.init.normal_(self.x_proj.weight, std=0.01)

        # in_proj and out_proj: Xavier
        nn.init.xavier_uniform_(self.in_proj.weight)
        nn.init.xavier_uniform_(self.out_proj.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through one Mamba block.

        Args:
            x: (batch, seq_len, d_model)
        Returns:
            output: (batch, seq_len, d_model)
        """
        residual = x

        # Pre-normalize
        x = self.norm(x)

        # Project and split: x → [x_path, z_gate]
        xz = self.in_proj(x)                      # (B, L, 2·d_inner)
        x_path, z = xz.chunk(2, dim=-1)           # each (B, L, d_inner)

        # ── x_path: Conv1d → SiLU → SSM ──

        # Causal conv1d (transpose for Conv1d's channel-first format)
        x_conv = x_path.transpose(1, 2)           # (B, d_inner, L)
        x_conv = self.conv1d(x_conv)               # (B, d_inner, L + d_conv - 1)
        x_conv = x_conv[:, :, :x_path.shape[1]]   # Trim future (causal)
        x_conv = x_conv.transpose(1, 2)            # (B, L, d_inner)

        x_ssm = F.silu(x_conv)

        # SSM: project x to (Δ, B, C), then selective scan
        y = self._ssm(x_ssm)

        # ── Gated output ──
        y = y * F.silu(z)

        # Project back + residual
        output = self.out_proj(y) + residual

        return output

    def _ssm(self, x: torch.Tensor) -> torch.Tensor:
        """
        The Selective State Space Model core.

        Projects input to (Δ, B, C), discretizes, runs scan.
        ALL SSM operations run in float32 for numerical stability,
        bypassing mixed-precision autocast.

        Args:
            x: (B, L, d_inner) — post-conv, post-SiLU
        Returns:
            y: (B, L, d_inner)
        """
        dtype = x.dtype

        # Force float32 for entire SSM — softplus and exp overflow in fp16
        with torch.amp.autocast('cuda', enabled=False):
            x = x.float()

            # A (negative for stability — ensures exponential decay)
            A = -torch.exp(self.A_log.float())   # (d_inner, d_state)
            D = self.D.float()

            # Project x → (delta_raw, B, C) in float32
            x_proj = self.x_proj(x)  # (B, L, dt_rank + 2·d_state)
            delta_raw, B, C = x_proj.split(
                [self.dt_rank, self.d_state, self.d_state], dim=-1
            )

            # Δ: project from bottleneck to full width, then softplus for positivity
            # softplus(x) = log(1 + exp(x)) — MUST be float32 to avoid fp16 exp overflow
            delta = F.softplus(self.dt_proj(delta_raw))  # (B, L, d_inner)

            # Run memory-bounded selective scan (all accumulation in float32)
            y = SelectiveScan.forward_scan(x, delta, A, B, C, D)

        return y.to(dtype)


class MambaBackbone(nn.Module):
    """
    The Sovereign Mind's Temporal Backbone.

    A stack of MambaBlock layers with input/output projections.
    Projects from the embedding dimension (MODEL_DIM) to the working
    dimension (STATE_DIM), processes through N selective state space
    layers, then projects back.

    This is the replacement for the LSTM fallback — same interface,
    vastly superior sequential modeling capacity.

    Architecture:
        input(MODEL_DIM) → proj_in(STATE_DIM) → [MambaBlock × N] →
        RMSNorm → proj_out(MODEL_DIM) → output

    Parameters:
        model_dim: External dimension (embedding/output space)
        internal_dim: Working dimension for SSM processing
        n_layers: Number of stacked Mamba blocks
        d_state: SSM state expansion (memory capacity per channel)
        d_conv: Local convolution width
        expand: Block expansion factor
    """

    def __init__(
        self,
        model_dim: int,
        internal_dim: int,
        n_layers: int,
        d_state: int = 16,
        d_conv: int = 4,
        expand: int = 2,
        dropout: float = 0.0
    ):
        super().__init__()
        self.model_dim = model_dim
        self.internal_dim = internal_dim
        self.n_layers = n_layers

        # ── Dimension Projections ──
        if model_dim != internal_dim:
            self.proj_in = nn.Linear(model_dim, internal_dim, bias=False)
            self.proj_out = nn.Linear(internal_dim, model_dim, bias=False)
        else:
            self.proj_in = nn.Identity()
            self.proj_out = nn.Identity()

        # ── Mamba Block Stack ──
        self.layers = nn.ModuleList([
            MambaBlock(
                d_model=internal_dim,
                d_state=d_state,
                d_conv=d_conv,
                expand=expand,
            )
            for _ in range(n_layers)
        ])

        # ── Dropout between layers ──
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

        # ── Final Normalization ──
        self.final_norm = RMSNorm(internal_dim)

        self._print_stats()

    def _print_stats(self):
        """Report backbone statistics."""
        total_params = sum(p.numel() for p in self.parameters())
        layer_params = sum(p.numel() for p in self.layers[0].parameters()) if self.layers else 0

        print(f"[Mamba] Custom SSM backbone initialized:")
        print(f"  Layers: {self.n_layers}")
        print(f"  Working dim: {self.internal_dim} (from model dim {self.model_dim})")
        print(f"  d_state: {self.layers[0].d_state if self.layers else 'N/A'}")
        print(f"  d_conv: {self.layers[0].d_conv if self.layers else 'N/A'}")
        print(f"  d_inner: {self.layers[0].d_inner if self.layers else 'N/A'}")
        print(f"  dt_rank: {self.layers[0].dt_rank if self.layers else 'N/A'}")
        print(f"  Params per block: {layer_params:,}")
        print(f"  Total backbone params: {total_params:,}")

    def forward(
        self,
        x: torch.Tensor,
        return_field_state: bool = True
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Process a sequence through the Mamba backbone.

        Args:
            x: (batch, seq_len, model_dim) — embedded token sequence
            return_field_state: Whether to extract the field state

        Returns:
            output: (batch, seq_len, model_dim) — processed sequence
            field_state: (batch, internal_dim) — last-timestep state
                         for CCF consciousness tracking. This is the
                         chrono-compressive field at the end of the sequence.
        """
        # Project to working dimension
        x = self.proj_in(x)

        # Process through Mamba blocks
        for layer in self.layers:
            x = layer(x)
            x = self.dropout(x)

        # Normalize
        x = self.final_norm(x)

        # Extract field state (last timestep's representation)
        field_state = x[:, -1, :] if return_field_state else None

        # Project back to model dimension
        x = self.proj_out(x)

        return x, field_state
