"""Focused tests for the isolated generated-transition candidate runner."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from train_world_transition import (
    WorldTransitionRegressor,
    model_predictions,
    train_regressor,
)
from world_data.ingestion import ingest_world_dataset
from world_data.transitions import derive_transition_examples
from world_metrics.state_transitions import score_state_transition_predictions
from world_schema.model import HoldoutSplit
from world_schema.trajectory_generator import TrajectoryGeneratorConfig, write_dataset


class WorldTransitionCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        receipt = write_dataset(
            Path(self.temporary.name) / "generated",
            TrajectoryGeneratorConfig(
                seed=721,
                train_count=16,
                held_out_object_count=2,
                held_out_operation_count=2,
                held_out_composition_count=2,
            ),
        )
        self.dataset = ingest_world_dataset(receipt.dataset_path, receipt.manifest_path)
        self.examples = derive_transition_examples(self.dataset)
        self.train_examples = tuple(
            example
            for example in self.examples
            if example.split is HoldoutSplit.TRAIN
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_train_only_regressor_emits_exact_coverage_predictions(self):
        torch.manual_seed(721)
        model = WorldTransitionRegressor()
        loss, updates, elapsed = train_regressor(
            model,
            self.train_examples,
            device=torch.device("cpu"),
            epochs=8,
            batch_size=4,
            learning_rate=0.03,
        )
        self.assertGreaterEqual(loss, 0.0)
        self.assertGreater(updates, 0)
        self.assertGreaterEqual(elapsed, 0.0)
        predictions = model_predictions(
            model,
            self.examples,
            device=torch.device("cpu"),
        )
        self.assertEqual(set(predictions), {example.program_id for example in self.examples})
        report = score_state_transition_predictions(self.dataset, predictions)
        self.assertEqual(report.prediction_count, len(self.examples))
        self.assertEqual(len(report.by_split), 4)

    def test_training_rejects_split_mixing(self):
        model = WorldTransitionRegressor()
        with self.assertRaisesRegex(ValueError, "only the train partition"):
            train_regressor(
                model,
                self.examples,
                device=torch.device("cpu"),
                epochs=1,
                batch_size=4,
                learning_rate=0.03,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
