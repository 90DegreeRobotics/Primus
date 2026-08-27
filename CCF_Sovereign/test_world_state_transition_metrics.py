"""Fail-hard regression tests for split-separated generated transition metrics."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_data.ingestion import ingest_world_dataset
from world_data.transitions import derive_transition_examples
from world_metrics.state_transitions import (
    StateTransitionMetricError,
    StateTransitionPrediction,
    score_state_transition_predictions,
    static_no_change_baseline,
)
from world_schema.trajectory_generator import TrajectoryGeneratorConfig, write_dataset


class StateTransitionMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        receipt = write_dataset(
            Path(self.temporary.name) / "generated",
            TrajectoryGeneratorConfig(
                seed=720,
                train_count=8,
                held_out_object_count=2,
                held_out_operation_count=2,
                held_out_composition_count=2,
            ),
        )
        self.dataset = ingest_world_dataset(receipt.dataset_path, receipt.manifest_path)
        self.examples = derive_transition_examples(self.dataset)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def oracle_predictions(self) -> dict[str, StateTransitionPrediction]:
        return {
            example.program_id: StateTransitionPrediction(
                program_id=example.program_id,
                target_translation_mm=tuple(
                    float(value) for value in example.target_translation_mm
                ),
                support_present_after=example.support_present_after,
                near_present_after=example.near_present_after,
            )
            for example in self.examples
        }

    def test_oracle_scores_every_split_separately_without_pooling(self):
        report = score_state_transition_predictions(
            self.dataset,
            self.oracle_predictions(),
            position_tolerance_mm=0.1,
        )
        self.assertEqual(report.prediction_count, len(self.examples))
        self.assertEqual(set(report.by_split), {
            "train",
            "held_out_object_class",
            "held_out_operation_family",
            "held_out_composition",
        })
        self.assertNotIn("held_out", report.by_split)
        for metrics in report.by_split.values():
            self.assertEqual(metrics.position_rmse_mm, 0.0)
            self.assertEqual(metrics.position_within_tolerance_accuracy, 1.0)
            self.assertEqual(metrics.support_relation_accuracy, 1.0)
            self.assertEqual(metrics.near_relation_accuracy, 1.0)
            self.assertEqual(metrics.all_transition_accuracy, 1.0)

    def test_declared_static_baseline_is_measured_not_assumed(self):
        report = score_state_transition_predictions(
            self.dataset,
            static_no_change_baseline(self.dataset),
        )
        for metrics in report.by_split.values():
            self.assertGreater(metrics.position_rmse_mm, 0.0)
            self.assertEqual(metrics.support_relation_accuracy, 0.0)
            self.assertEqual(metrics.near_relation_accuracy, 0.0)
            self.assertEqual(metrics.all_transition_accuracy, 0.0)

    def test_missing_prediction_fails_closed(self):
        predictions = self.oracle_predictions()
        predictions.pop(next(iter(predictions)))
        with self.assertRaisesRegex(StateTransitionMetricError, "coverage mismatch"):
            score_state_transition_predictions(self.dataset, predictions)

    def test_nonpositive_tolerance_fails_closed(self):
        with self.assertRaisesRegex(StateTransitionMetricError, "positive and finite"):
            score_state_transition_predictions(
                self.dataset,
                self.oracle_predictions(),
                position_tolerance_mm=0.0,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
