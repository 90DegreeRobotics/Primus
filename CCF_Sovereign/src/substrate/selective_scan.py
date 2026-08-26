"""Memory-bounded associative selective scan for the Primus Mamba substrate."""
from __future__ import annotations

import math

import torch


DEFAULT_SCAN_CHUNK_SIZE = 64


def affine_prefix_scan(
    coefficients: torch.Tensor,
    additions: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Inclusive Hillis–Steele scan over affine recurrences inside one chunk.

    Each element represents ``h -> a*h + b``. The returned tensors contain the
    cumulative coefficient and zero-initial-state result at every timestep.
    Work is O(K log K) for chunk length K, while K remains independent of the
    full sequence length.
    """

    if coefficients.shape != additions.shape:
        raise ValueError("coefficients and additions must have identical shapes")
    if coefficients.ndim != 4:
        raise ValueError("scan tensors must have shape (B, K, D, N)")
    length = coefficients.shape[1]
    cumulative_a = coefficients
    cumulative_b = additions
    steps = int(math.ceil(math.log2(max(length, 2))))
    for depth in range(steps):
        stride = 2**depth
        if stride >= length:
            break
        predecessor_a = cumulative_a[:, :-stride]
        predecessor_b = cumulative_b[:, :-stride]
        current_a = cumulative_a[:, stride:]
        current_b = cumulative_b[:, stride:]
        suffix_a = predecessor_a * current_a
        suffix_b = current_a * predecessor_b + current_b
        cumulative_a = torch.cat(
            (cumulative_a[:, :stride], suffix_a),
            dim=1,
        )
        cumulative_b = torch.cat(
            (cumulative_b[:, :stride], suffix_b),
            dim=1,
        )
    return cumulative_a, cumulative_b


def chunked_selective_scan(
    x: torch.Tensor,
    delta: torch.Tensor,
    transition: torch.Tensor,
    input_projection: torch.Tensor,
    output_projection: torch.Tensor,
    skip: torch.Tensor,
    *,
    chunk_size: int = DEFAULT_SCAN_CHUNK_SIZE,
    initial_state: torch.Tensor | None = None,
    return_final_state: bool = False,
) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
    """Run the selective recurrence without a full ``(B,L,D,N)`` tensor.

    Inputs and accumulation must be FP32. The function materializes at most one
    ``(B,chunk_size,D,N)`` coefficient/state block plus the boundary state
    ``(B,D,N)``. The output remains ``(B,L,D)`` because every timestep is an
    externally observable Mamba activation.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if x.ndim != 3 or delta.shape != x.shape:
        raise ValueError("x and delta must have identical shape (B,L,D)")
    batch, sequence_length, width = x.shape
    if transition.ndim != 2 or transition.shape[0] != width:
        raise ValueError("transition must have shape (D,N)")
    state_width = transition.shape[1]
    expected_selective = (batch, sequence_length, state_width)
    if input_projection.shape != expected_selective:
        raise ValueError("input_projection must have shape (B,L,N)")
    if output_projection.shape != expected_selective:
        raise ValueError("output_projection must have shape (B,L,N)")
    if skip.shape != (width,):
        raise ValueError("skip must have shape (D,)")
    tensors = (x, delta, transition, input_projection, output_projection, skip)
    if any(tensor.dtype != torch.float32 for tensor in tensors):
        raise ValueError("chunked selective scan requires FP32 inputs")

    if initial_state is None:
        boundary_state = torch.zeros(
            (batch, width, state_width),
            dtype=x.dtype,
            device=x.device,
        )
    else:
        if initial_state.shape != (batch, width, state_width):
            raise ValueError("initial_state must have shape (B,D,N)")
        if initial_state.dtype != torch.float32:
            raise ValueError("initial_state must be FP32")
        boundary_state = initial_state

    output_chunks = []
    expanded_transition = transition.unsqueeze(0).unsqueeze(0)
    for start in range(0, sequence_length, chunk_size):
        end = min(start + chunk_size, sequence_length)
        x_chunk = x[:, start:end]
        delta_chunk = delta[:, start:end]
        input_chunk = input_projection[:, start:end]
        output_chunk = output_projection[:, start:end]

        coefficients = torch.exp(
            delta_chunk.unsqueeze(-1) * expanded_transition
        )
        additions = (
            delta_chunk.unsqueeze(-1)
            * input_chunk.unsqueeze(2)
            * x_chunk.unsqueeze(-1)
        )
        cumulative_a, zero_state = affine_prefix_scan(coefficients, additions)
        states = cumulative_a * boundary_state.unsqueeze(1) + zero_state
        chunk_output = (
            states * output_chunk.unsqueeze(2)
        ).sum(dim=-1)
        output_chunks.append(chunk_output)
        boundary_state = states[:, -1]

    if output_chunks:
        output = torch.cat(output_chunks, dim=1)
    else:
        output = x.new_empty((batch, 0, width))
    output = output + x * skip.unsqueeze(0).unsqueeze(0)
    if return_final_state:
        return output, boundary_state
    return output


def scan_state_element_ceiling(
    batch_size: int,
    sequence_length: int,
    width: int,
    state_width: int,
    *,
    chunk_size: int = DEFAULT_SCAN_CHUNK_SIZE,
) -> int:
    """Maximum coefficient/state elements materialized for one scan chunk."""

    values = (batch_size, sequence_length, width, state_width, chunk_size)
    if any(value < 0 for value in values[:2]) or any(value <= 0 for value in values[2:]):
        raise ValueError("scan dimensions must be positive; sequence may be zero")
    return batch_size * min(sequence_length, chunk_size) * width * state_width
