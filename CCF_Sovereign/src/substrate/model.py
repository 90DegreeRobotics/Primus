import torch
import torch.nn as nn
import torch.nn.functional as F
from core.config import SovereignConfig
from substrate.mamba_custom import MambaBackbone


class CCFSubstrate(nn.Module):
    """
    The CCF Sovereign Substrate — Custom Mamba SSM Backbone.

    Linear-time selective state space processing. No transformers,
    no pretrained weights. Grown from scratch through the Council corpus.

    Architecture:
        tokens → Embedding(MODEL_DIM) → FastWeights(MODEL_DIM) →
        MambaBackbone(MODEL_DIM→STATE_DIM→MODEL_DIM) → lm_head → logits

    The Mamba backbone provides:
      - O(L) sequence processing (not O(L²) like attention)
      - Content-aware state updates (selective scan)
      - Multi-timescale memory via structured state matrix A
      - Local context via causal convolution
    """
    def __init__(self, config: SovereignConfig):
        super().__init__()
        self.config = config
        self.model_dim = config.MODEL_DIM
        self.state_dim = config.STATE_DIM

        # Embedding layer
        self.embeddings = nn.Embedding(config.VOCAB_SIZE, config.MODEL_DIM)

        # The Fast Weights (Hebbian Plasticity Layer)
        # Initialized as identity — Hebbian learning shapes it during interaction
        self.fast_weights = nn.Linear(self.model_dim, self.model_dim, bias=False)
        nn.init.eye_(self.fast_weights.weight)

        # Custom Mamba SSM Backbone
        self.backbone = MambaBackbone(
            model_dim=config.MODEL_DIM,
            internal_dim=config.STATE_DIM,
            n_layers=config.NUM_LAYERS,
            d_state=config.MAMBA_D_STATE,
            d_conv=config.MAMBA_D_CONV,
            expand=config.MAMBA_EXPAND,
            dropout=config.MAMBA_DROPOUT,
        )

        # Output projection to vocabulary
        self.lm_head = nn.Linear(config.MODEL_DIM, config.VOCAB_SIZE, bias=False)

    def forward(self, input_ids, hidden_state=None, compute_surprise=True):
        """
        Process a stream of tokens through the Sovereign Mind.

        Args:
            input_ids: (batch, seq_len) — tokenized input
            hidden_state: ignored (Mamba processes full sequence)
            compute_surprise: whether to calculate Free Energy surprise

        Returns:
            logits: (batch, seq_len, vocab_size) — next-token predictions
            field_state: (batch, state_dim) — chrono-compressive field state
            surprise: (batch, seq_len) — Free Energy at each position
        """
        batch_size, seq_len = input_ids.shape

        # Embed tokens
        x = self.embeddings(input_ids)

        # Apply Fast Weights (immediate Hebbian plasticity)
        x = self.fast_weights(x)

        # Process through Mamba backbone
        output, field_state = self.backbone(x)

        # Project to vocabulary
        logits = self.lm_head(output)

        # Surprise = -log P(token_{t+1} | context_≤t). logits[t] predicts token[t+1].
        surprise = None
        if compute_surprise and seq_len >= 2:
            with torch.no_grad():
                log_probs = F.log_softmax(logits[:, :-1, :], dim=-1)
                target = input_ids[:, 1:].unsqueeze(-1)
                token_log_probs = log_probs.gather(-1, target).squeeze(-1)
                # Align to sequence length: position 0 has no predecessor prediction.
                pad = torch.zeros(batch_size, 1, device=token_log_probs.device, dtype=token_log_probs.dtype)
                surprise = torch.cat([pad, -token_log_probs], dim=1)
        elif compute_surprise:
            surprise = torch.zeros(batch_size, seq_len, device=logits.device)

        return logits, field_state, surprise

    def apply_hebbian_update(self, input_activation, output_activation, learning_rate=0.001):
        """
        Applies local Hebbian updates to Fast Weights.
        ΔW = η(Output ⊗ Input)
        """
        with torch.no_grad():
            delta_w = learning_rate * torch.einsum('bi,bj->ij',
                                                    output_activation,
                                                    input_activation)
            delta_w = delta_w / input_activation.size(0)
            self.fast_weights.weight.add_(delta_w)
