"""Differential gates for the Primus chunked selective scan."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from substrate.mamba_custom import MambaBlock, SelectiveScan
from substrate.selective_scan import (
    chunked_selective_scan,
    scan_state_element_ceiling,
)


def recurrent_reference(
    x: torch.Tensor,
    delta: torch.Tensor,
    transition: torch.Tensor,
    input_projection: torch.Tensor,
    output_projection: torch.Tensor,
    skip: torch.Tensor,
    initial_state: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    batch, sequence_length, width = x.shape
    state_width = transition.shape[1]
    state = (
        torch.zeros(batch, width, state_width, dtype=x.dtype, device=x.device)
        if initial_state is None
        else initial_state
    )
    outputs = []
    for index in range(sequence_length):
        coefficient = torch.exp(
            delta[:, index].unsqueeze(-1) * transition.unsqueeze(0)
        )
        addition = (
            delta[:, index].unsqueeze(-1)
            * input_projection[:, index].unsqueeze(1)
            * x[:, index].unsqueeze(-1)
        )
        state = coefficient * state + addition
        output = (
            state * output_projection[:, index].unsqueeze(1)
        ).sum(dim=-1)
        outputs.append(output)
    stacked = (
        torch.stack(outputs, dim=1)
        if outputs
        else x.new_empty((batch, 0, width))
    )
    return stacked + x * skip.unsqueeze(0).unsqueeze(0), state


def inputs(shape: tuple[int, int, int, int], seed: int):
    batch, sequence_length, width, state_width = shape
    generator = torch.Generator().manual_seed(seed)
    x = torch.randn(batch, sequence_length, width, generator=generator) * 0.25
    delta = torch.rand(batch, sequence_length, width, generator=generator) * 0.08 + 0.001
    transition = -(torch.rand(width, state_width, generator=generator) * 2.0 + 0.1)
    input_projection = torch.randn(
        batch, sequence_length, state_width, generator=generator
    ) * 0.2
    output_projection = torch.randn(
        batch, sequence_length, state_width, generator=generator
    ) * 0.2
    skip = torch.randn(width, generator=generator) * 0.1
    return x, delta, transition, input_projection, output_projection, skip


class ChunkedSelectiveScanTests(unittest.TestCase):
    def test_forward_and_final_state_match_recurrence_across_shapes(self):
        cases = (
            ((1, 1, 3, 2), 1),
            ((2, 7, 5, 3), 3),
            ((1, 17, 8, 4), 8),
            ((2, 65, 6, 5), 16),
            ((1, 129, 4, 7), 64),
        )
        for case, (shape, chunk_size) in enumerate(cases):
            with self.subTest(shape=shape, chunk_size=chunk_size):
                values = inputs(shape, seed=100 + case)
                reference_output, reference_state = recurrent_reference(*values)
                output, state = chunked_selective_scan(
                    *values,
                    chunk_size=chunk_size,
                    return_final_state=True,
                )
                self.assertTrue(
                    torch.allclose(output, reference_output, rtol=2e-5, atol=2e-6),
                    (output - reference_output).abs().max().item(),
                )
                self.assertTrue(
                    torch.allclose(state, reference_state, rtol=2e-5, atol=2e-6),
                    (state - reference_state).abs().max().item(),
                )

    def test_nonzero_initial_state_matches_recurrence(self):
        shape = (2, 33, 7, 4)
        values = inputs(shape, seed=500)
        initial = torch.randn(shape[0], shape[2], shape[3]) * 0.1
        reference_output, reference_state = recurrent_reference(
            *values,
            initial_state=initial,
        )
        output, state = chunked_selective_scan(
            *values,
            chunk_size=8,
            initial_state=initial,
            return_final_state=True,
        )
        self.assertTrue(torch.allclose(output, reference_output, rtol=2e-5, atol=2e-6))
        self.assertTrue(torch.allclose(state, reference_state, rtol=2e-5, atol=2e-6))

    def test_backward_gradients_match_recurrence(self):
        shape = (2, 19, 6, 5)
        reference_values = [value.requires_grad_(True) for value in inputs(shape, seed=900)]
        chunked_values = [value.detach().clone().requires_grad_(True) for value in reference_values]
        reference_output, reference_state = recurrent_reference(*reference_values)
        (reference_output.square().mean() + reference_state.square().mean()).backward()
        chunked_output, chunked_state = chunked_selective_scan(
            *chunked_values,
            chunk_size=7,
            return_final_state=True,
        )
        (chunked_output.square().mean() + chunked_state.square().mean()).backward()
        self.assertTrue(torch.allclose(chunked_output, reference_output, rtol=2e-5, atol=2e-6))
        for index, (reference, chunked) in enumerate(zip(reference_values, chunked_values)):
            with self.subTest(input_index=index):
                self.assertTrue(
                    torch.allclose(chunked.grad, reference.grad, rtol=3e-4, atol=3e-6),
                    (chunked.grad - reference.grad).abs().max().item(),
                )

    def test_long_sequence_matches_with_bounded_state_ceiling(self):
        shape = (1, 513, 16, 8)
        values = inputs(shape, seed=1200)
        reference_output, _ = recurrent_reference(*values)
        output = chunked_selective_scan(*values, chunk_size=32)
        self.assertTrue(torch.allclose(output, reference_output, rtol=3e-5, atol=3e-6))
        full_elements = shape[0] * shape[1] * shape[2] * shape[3]
        ceiling = scan_state_element_ceiling(*shape, chunk_size=32)
        self.assertEqual(ceiling, shape[0] * 32 * shape[2] * shape[3])
        self.assertLess(ceiling, full_elements // 10)

    def test_invalid_shapes_and_dtypes_fail_closed(self):
        values = inputs((1, 4, 3, 2), seed=1)
        with self.assertRaises(ValueError):
            chunked_selective_scan(*values, chunk_size=0)
        half_values = list(values)
        half_values[0] = half_values[0].half()
        with self.assertRaises(ValueError):
            chunked_selective_scan(*half_values)

    def test_scan_matches_preserved_parallel_reference(self):
        for case_index, shape in enumerate(
            ((1, 3, 4, 2), (2, 9, 7, 4), (1, 33, 8, 8), (2, 65, 5, 3))
        ):
            with self.subTest(shape=shape):
                values = inputs(shape, seed=1700 + case_index)
                reference = SelectiveScan.forward_scan_reference(*values)
                chunked = SelectiveScan.forward_scan(*values, chunk_size=7)
                self.assertTrue(
                    torch.allclose(chunked, reference, rtol=2e-5, atol=2e-6),
                    (chunked - reference).abs().max().item(),
                )

    def test_complete_mamba_block_forward_and_gradients_match(self):
        cases = (
            (1, 9, 16, 4, 2),
            (2, 17, 24, 8, 4),
            (1, 31, 32, 5, 3),
        )
        for case_index, (batch, length, width, state_width, conv_width) in enumerate(cases):
            with self.subTest(
                batch=batch,
                length=length,
                width=width,
                state_width=state_width,
                conv_width=conv_width,
            ):
                torch.manual_seed(2000 + case_index)
                chunked_block = MambaBlock(width, state_width, conv_width, expand=2)
                reference_block = copy.deepcopy(chunked_block)
                chunked_input = torch.randn(batch, length, width, requires_grad=True)
                reference_input = chunked_input.detach().clone().requires_grad_(True)
                chunked_output = chunked_block(chunked_input)
                chunked_output.square().mean().backward()
                with patch.object(
                    SelectiveScan,
                    "forward_scan",
                    side_effect=SelectiveScan.forward_scan_reference,
                ):
                    reference_output = reference_block(reference_input)
                    reference_output.square().mean().backward()
                self.assertTrue(
                    torch.allclose(chunked_output, reference_output, rtol=3e-5, atol=3e-6),
                    (chunked_output - reference_output).abs().max().item(),
                )
                self.assertTrue(
                    torch.allclose(
                        chunked_input.grad,
                        reference_input.grad,
                        rtol=5e-4,
                        atol=5e-6,
                    ),
                    (chunked_input.grad - reference_input.grad).abs().max().item(),
                )
                chunked_parameters = dict(chunked_block.named_parameters())
                reference_parameters = dict(reference_block.named_parameters())
                self.assertEqual(chunked_parameters.keys(), reference_parameters.keys())
                for name in chunked_parameters:
                    with self.subTest(parameter=name):
                        chunked_gradient = chunked_parameters[name].grad
                        reference_gradient = reference_parameters[name].grad
                        self.assertTrue(
                            torch.allclose(
                                chunked_gradient,
                                reference_gradient,
                                rtol=8e-4,
                                atol=8e-6,
                            ),
                            (chunked_gradient - reference_gradient).abs().max().item(),
                        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
