"""Fail-hard gates for per-split action-conditioned WorldProgram metrics."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_data.ingestion import WorldIngestionConfig, ingest_world_dataset  # noqa: E402
from world_metrics.transition_metrics import (  # noqa: E402
    CompilerReceipt,
    WorldMetricError,
    score_transition_predictions,
)
from world_schema.model import EvidenceKind, HoldoutSplit  # noqa: E402
from world_schema.trajectory_generator import (  # noqa: E402
    DATASET_FILENAME,
    MANIFEST_FILENAME,
    TrajectoryGeneratorConfig,
    write_dataset,
)


def generator_config() -> TrajectoryGeneratorConfig:
    return TrajectoryGeneratorConfig(
        seed=313_131,
        train_count=8,
        held_out_object_count=2,
        held_out_operation_count=2,
        held_out_composition_count=2,
    )


def ingestion_config() -> WorldIngestionConfig:
    return WorldIngestionConfig(segment_length=256, segment_stride=255, batch_size=3)


class TransitionMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        output = root / "source"
        write_dataset(output, generator_config())
        self.ingested = ingest_world_dataset(
            output / DATASET_FILENAME,
            output / MANIFEST_FILENAME,
            ingestion_config(),
        )
        self.targets = self.ingested.records
        self.predictions = {
            record.program.program_id: record.program
            for record in self.targets
        }

    def tearDown(self):
        self.temporary.cleanup()

    def _receipts(self, *, accepted: bool = True):
        receipts = []
        for record in self.targets:
            payload = f"test-observed-compiler:{record.program.program_id}".encode("utf-8")
            receipts.append(
                CompilerReceipt(
                    program_id=record.program.program_id,
                    predicted_program_sha256=record.program.sha256(),
                    evidence_kind=EvidenceKind.OBSERVED,
                    source_uri=f"test://compiler/{record.program.program_id}",
                    source_sha256=hashlib.sha256(payload).hexdigest(),
                    compiler_accepted=accepted,
                    failure_class=None if accepted else "compiler_rejected",
                )
            )
        return tuple(receipts)

    def test_perfect_predictions_score_every_split_separately(self):
        report = score_transition_predictions(
            self.ingested,
            self.predictions,
            compiler_receipts=self._receipts(),
        )

        self.assertEqual(report.prediction_count, len(self.targets))
        self.assertEqual(
            set(report.by_split),
            {
                "train",
                "held_out_object_class",
                "held_out_operation_family",
                "held_out_composition",
            },
        )
        self.assertNotIn("overall", report.to_dict())
        for metrics in report.by_split.values():
            self.assertEqual(metrics.state_accuracy, 1.0)
            self.assertEqual(metrics.relation_accuracy, 1.0)
            self.assertEqual(metrics.operation_accuracy, 1.0)
            self.assertEqual(metrics.uncertainty_accuracy, 1.0)
            self.assertEqual(metrics.exact_program_accuracy, 1.0)
            self.assertEqual(metrics.evidence_completeness, 1.0)
            self.assertEqual(metrics.compiler_evidence_completeness, 1.0)
            self.assertEqual(metrics.compiler_validity_rate, 1.0)
            self.assertEqual(metrics.rejected_compiler_receipts, 0)

    def test_action_program_delta_is_scored_without_hiding_the_affected_split(self):
        target = next(
            record
            for record in self.targets
            if record.split is HoldoutSplit.HELD_OUT_COMPOSITION
        )
        operation_index = next(
            index
            for index, operation in enumerate(target.program.operations)
            if operation.operation_id == "operation_move"
        )
        operations = list(target.program.operations)
        operations[operation_index] = replace(
            operations[operation_index],
            parameters={**operations[operation_index].parameters, "delta_x_mm": 999_999},
        )
        self.predictions[target.program.program_id] = replace(
            target.program,
            operations=tuple(operations),
        )
        report = score_transition_predictions(
            self.ingested,
            self.predictions,
        )

        affected = report.by_split[HoldoutSplit.HELD_OUT_COMPOSITION.value]
        self.assertEqual(affected.state_accuracy, 1.0)
        self.assertEqual(affected.relation_accuracy, 1.0)
        self.assertLess(affected.operation_accuracy, 1.0)
        self.assertLess(affected.exact_program_accuracy, 1.0)
        self.assertIsNone(affected.compiler_validity_rate)
        self.assertEqual(affected.compiler_evidence_completeness, 0.0)
        self.assertEqual(
            report.by_split[HoldoutSplit.TRAIN.value].operation_accuracy,
            1.0,
        )

    def test_missing_or_partial_compiler_evidence_is_reported_unavailable(self):
        report = score_transition_predictions(
            self.ingested,
            self.predictions,
        )
        for metrics in report.by_split.values():
            self.assertEqual(metrics.compiler_receipts, 0)
            self.assertEqual(metrics.compiler_evidence_completeness, 0.0)
            self.assertIsNone(metrics.compiler_validity_rate)

        partial = self._receipts()[:1]
        report = score_transition_predictions(
            self.ingested,
            self.predictions,
            compiler_receipts=partial,
        )
        train = report.by_split[HoldoutSplit.TRAIN.value]
        self.assertGreater(train.compiler_evidence_completeness, 0.0)
        self.assertLess(train.compiler_evidence_completeness, 1.0)
        self.assertIsNone(train.compiler_validity_rate)

    def test_observed_compiler_rejection_is_scored_separately_from_prediction_accuracy(self):
        report = score_transition_predictions(
            self.ingested,
            self.predictions,
            compiler_receipts=self._receipts(accepted=False),
        )
        for metrics in report.by_split.values():
            self.assertEqual(metrics.exact_program_accuracy, 1.0)
            self.assertEqual(metrics.compiler_evidence_completeness, 1.0)
            self.assertEqual(metrics.compiler_validity_rate, 0.0)
            self.assertEqual(metrics.accepted_compiler_receipts, 0)
            self.assertEqual(metrics.rejected_compiler_receipts, metrics.cases)

    def test_synthetic_compiler_receipt_is_rejected(self):
        record = self.targets[0]
        receipt = CompilerReceipt(
            program_id=record.program.program_id,
            predicted_program_sha256=record.program.sha256(),
            evidence_kind=EvidenceKind.GENERATED,
            source_uri="test://generated",
            source_sha256="a" * 64,
            compiler_accepted=True,
        )
        with self.assertRaisesRegex(WorldMetricError, "observed compiler receipts"):
            score_transition_predictions(
                self.ingested,
                self.predictions,
                    compiler_receipts=(receipt,),
            )

    def test_coverage_and_receipt_hash_mismatch_fail_closed(self):
        incomplete = dict(self.predictions)
        incomplete.pop(next(iter(incomplete)))
        with self.assertRaisesRegex(WorldMetricError, "prediction coverage mismatch"):
            score_transition_predictions(
                self.ingested,
                incomplete,
                )

        record = self.targets[0]
        receipt = CompilerReceipt(
            program_id=record.program.program_id,
            predicted_program_sha256="0" * 64,
            evidence_kind=EvidenceKind.OBSERVED,
            source_uri="test://observed",
            source_sha256="b" * 64,
            compiler_accepted=True,
        )
        with self.assertRaisesRegex(WorldMetricError, "compiler receipt hash mismatch"):
            score_transition_predictions(
                self.ingested,
                self.predictions,
                    compiler_receipts=(receipt,),
            )

    def test_raw_records_are_rejected_without_an_ingestion_receipt(self):
        with self.assertRaisesRegex(WorldMetricError, "manifest-bound IngestedWorldDataset"):
            score_transition_predictions(tuple(self.targets), self.predictions)

    def test_prediction_iterable_duplicate_ids_are_rejected(self):
        duplicate = tuple(self.predictions.values()) + (next(iter(self.predictions.values())),)
        with self.assertRaisesRegex(WorldMetricError, "duplicate prediction program IDs"):
            score_transition_predictions(
                self.ingested,
                duplicate,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
