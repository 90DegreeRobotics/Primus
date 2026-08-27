"""Focused tests for the generated temporal-context candidate runner."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from train_temporal_context import (
    TemporalContextMLP,
    model_predictions,
    train_model,
    train_partition_witnesses,
)
from world_data.ingestion import ingest_world_dataset
from world_data.temporal_witness import (
    CONTEXT_INPUT_FEATURE_NAMES,
    assert_context_feature_boundary,
    derive_temporal_witnesses,
)
from world_metrics.state_transitions import score_state_transition_predictions
from world_schema.model import HoldoutSplit
from world_schema.trajectory_generator import TrajectoryGeneratorConfig, write_dataset


class TemporalContextCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        receipt = write_dataset(
            Path(self.temporary.name) / "generated",
            TrajectoryGeneratorConfig(
                seed=742,
                train_count=20,
                held_out_object_count=3,
                held_out_operation_count=3,
                held_out_composition_count=3,
            ),
        )
        self.dataset = ingest_world_dataset(receipt.dataset_path, receipt.manifest_path)
        self.witnesses = derive_temporal_witnesses(self.dataset)
        self.train_witnesses = tuple(
            witness for witness in self.witnesses if witness.split is HoldoutSplit.TRAIN
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_train_only_nonlinear_candidate_emits_exact_coverage(self):
        torch.manual_seed(742)
        model = TemporalContextMLP(hidden_width=16)
        loss, updates, elapsed = train_model(
            model,
            self.train_witnesses,
            device=torch.device("cpu"),
            epochs=12,
            batch_size=4,
            learning_rate=0.01,
        )
        self.assertGreaterEqual(loss, 0.0)
        self.assertGreater(updates, 0)
        self.assertGreaterEqual(elapsed, 0.0)
        predictions = model_predictions(model, self.witnesses, device=torch.device("cpu"))
        self.assertEqual(set(predictions), {witness.program_id for witness in self.witnesses})
        report = score_state_transition_predictions(self.dataset, predictions)
        self.assertEqual(report.prediction_count, len(self.witnesses))
        self.assertEqual(len(report.by_split), 4)

    def test_training_rejects_held_out_witnesses(self):
        with self.assertRaisesRegex(ValueError, "only the train partition"):
            train_partition_witnesses(self.witnesses)

    def test_context_contract_excludes_direct_deltas_and_targets(self):
        assert_context_feature_boundary()
        forbidden = ("delta", "target", "split", "class", "family", "program_id", "hash")
        for name in CONTEXT_INPUT_FEATURE_NAMES:
            self.assertFalse(any(term in name for term in forbidden))


if __name__ == "__main__":
    unittest.main(verbosity=2)
