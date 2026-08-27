"""Fail-hard regression tests for generated WorldProgram transition examples."""
from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_data.ingestion import ingest_world_dataset
from world_data.transitions import (
    INPUT_FEATURE_NAMES,
    TARGET_FEATURE_NAMES,
    WorldTransitionError,
    derive_transition_example,
    derive_transition_examples,
    example_set_sha256,
    train_partition_examples,
)
from world_schema.model import HoldoutSplit, OperationKind
from world_schema.trajectory_generator import TrajectoryGeneratorConfig, write_dataset


class WorldTransitionExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        output = Path(self.temporary.name) / "generated"
        receipt = write_dataset(
            output,
            TrajectoryGeneratorConfig(
                seed=719,
                train_count=8,
                held_out_object_count=1,
                held_out_operation_count=1,
                held_out_composition_count=1,
            ),
        )
        self.dataset = ingest_world_dataset(receipt.dataset_path, receipt.manifest_path)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_derivation_uses_only_declared_initial_state_and_action_delta(self):
        record = self.dataset.records[0]
        example = derive_transition_example(record)
        self.assertEqual(len(INPUT_FEATURE_NAMES), 6)
        self.assertEqual(len(TARGET_FEATURE_NAMES), 5)
        self.assertEqual(
            example.target_translation_mm,
            tuple(
                source + delta
                for source, delta in zip(
                    example.source_translation_mm,
                    example.action_delta_mm,
                )
            ),
        )
        support_effects = [
            operation.kind
            for operation in record.program.operations
            if operation.relation_id == "relation_support"
        ]
        near_effects = [
            operation.kind
            for operation in record.program.operations
            if operation.relation_id == "relation_near"
        ]
        self.assertEqual(
            example.support_present_after,
            support_effects[-1] is OperationKind.ADD_RELATION,
        )
        self.assertEqual(
            example.near_present_after,
            bool(near_effects) and near_effects[-1] is OperationKind.ADD_RELATION,
        )
        self.assertEqual(example.target_evidence_kinds, ("generated", "inferred"))
        self.assertEqual(len(example.input_vector), len(INPUT_FEATURE_NAMES))
        self.assertEqual(len(example.target_vector), len(TARGET_FEATURE_NAMES))

    def test_derivation_preserves_all_manifest_bound_splits_and_hashes(self):
        examples = derive_transition_examples(self.dataset)
        self.assertEqual(len(examples), self.dataset.receipt.program_count)
        self.assertEqual(
            {example.split for example in examples},
            {
                HoldoutSplit.TRAIN,
                HoldoutSplit.HELD_OUT_OBJECT_CLASS,
                HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
                HoldoutSplit.HELD_OUT_COMPOSITION,
            },
        )
        self.assertTrue(all(len(example.program_sha256) == 64 for example in examples))
        self.assertEqual(example_set_sha256(examples), example_set_sha256(reversed(examples)))

    def test_train_partition_filter_rejects_any_holdout_example(self):
        examples = derive_transition_examples(self.dataset)
        train_examples = tuple(
            example for example in examples if example.split is HoldoutSplit.TRAIN
        )
        self.assertEqual(train_partition_examples(train_examples), train_examples)
        with self.assertRaisesRegex(WorldTransitionError, "only the train partition"):
            train_partition_examples(examples)

    def test_generated_target_cannot_be_labeled_observed(self):
        example = derive_transition_example(self.dataset.records[0])
        invalid = replace(example, target_evidence_kinds=("observed",))
        with self.assertRaisesRegex(WorldTransitionError, "generated or inferred"):
            invalid.validate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
