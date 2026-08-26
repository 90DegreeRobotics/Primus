"""Focused tests for the Primus GPU scaling-ladder harness."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.benchmarks.scaling_ladder import (
    LadderRung,
    TiedLadderModel,
    fixed_blocks,
    parameter_count,
    tokenize_corpus,
    train_small_bpe,
)


class ScalingLadderTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)

    def test_small_bpe_and_fixed_blocks_are_deterministic(self):
        texts = [
            "User: move the camera\n\nAssistant: camera moved",
            "User: add a light\n\nAssistant: light added",
        ]
        tokenizer_a = train_small_bpe(texts, vocab_size=320)
        tokenizer_b = train_small_bpe(texts, vocab_size=320)
        ids_a = tokenize_corpus(tokenizer_a, texts)
        ids_b = tokenize_corpus(tokenizer_b, texts)
        self.assertEqual(ids_a, ids_b)
        self.assertLessEqual(tokenizer_a.get_vocab_size(), 320)
        self.assertGreater(tokenizer_a.get_vocab_size(), 4)
        blocks = fixed_blocks(ids_a * 8, sequence_length=8)
        self.assertEqual(blocks.shape[1], 9)
        self.assertEqual(blocks.dtype, torch.long)

    def test_tied_model_has_no_bottleneck_and_backpropagates(self):
        rung = LadderRung(
            name="tiny",
            target_parameters=10_000,
            model_dim=32,
            layers=1,
            d_state=4,
            d_conv=2,
            expand=1,
        )
        model = TiedLadderModel(rung, vocab_size=300)
        self.assertEqual(model.backbone.model_dim, rung.model_dim)
        self.assertEqual(model.backbone.internal_dim, rung.model_dim)
        self.assertNotIn("lm_head", dict(model.named_modules()))
        self.assertIs(model.tied_weight, model.embedding.weight)

        tokens = torch.randint(0, 300, (2, 9), dtype=torch.long)
        logits = model(tokens[:, :-1])
        self.assertEqual(tuple(logits.shape), (2, 8, 300))
        loss = F.cross_entropy(
            logits.reshape(-1, logits.size(-1)),
            tokens[:, 1:].reshape(-1),
        )
        loss.backward()
        self.assertGreater(parameter_count(model), 0)
        gradients = [
            parameter.grad
            for parameter in model.parameters()
            if parameter.grad is not None
        ]
        self.assertTrue(gradients)
        self.assertTrue(all(torch.isfinite(gradient).all() for gradient in gradients))


if __name__ == "__main__":
    unittest.main(verbosity=2)
