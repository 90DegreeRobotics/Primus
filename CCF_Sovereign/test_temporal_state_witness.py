"""Fail-hard regression tests for generated temporal state witnesses."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_data.ingestion import ingest_world_dataset
from world_data.temporal_witness import (
    CONTEXT_INPUT_FEATURE_NAMES,
    TEMPORAL_TARGET_FEATURE_NAMES,
    assert_context_feature_boundary,
    derive_temporal_witness,
    derive_temporal_witnesses,
    temporal_witness_set_sha256,
)
from world_schema.model import HoldoutSplit, OperationKind, RelationKind
from world_schema.trajectory_generator import TrajectoryGeneratorConfig, write_dataset


class TemporalStateWitnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        receipt = write_dataset(
            Path(self.temporary.name) / "generated",
            TrajectoryGeneratorConfig(
                seed=732,
                train_count=16,
                held_out_object_count=3,
                held_out_operation_count=3,
                held_out_composition_count=3,
            ),
        )
        self.dataset = ingest_world_dataset(receipt.dataset_path, receipt.manifest_path)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_witness_target_rederives_exact_declared_post_state(self):
        record = self.dataset.records[0]
        witness = derive_temporal_witness(record)
        move = next(
            operation
            for operation in record.program.operations
            if operation.kind is OperationKind.SET_TRANSFORM
        )
        subject = next(
            entity
            for entity in record.program.entities
            if entity.entity_id == move.subject_id
        )
        expected_target = tuple(
            source + int(move.parameters[name])
            for source, name in zip(
                subject.transform.translation_mm,
                ("delta_x_mm", "delta_y_mm", "delta_z_mm"),
            )
        )
        self.assertEqual(witness.target_translation_mm, expected_target)
        self.assertEqual(witness.pre_tick, 0)
        self.assertEqual(witness.target_tick, 2)
        self.assertEqual(witness.target_evidence_kinds, ("generated", "inferred"))

    def test_context_feature_contract_excludes_direct_target_and_partition_data(self):
        assert_context_feature_boundary()
        self.assertEqual(len(CONTEXT_INPUT_FEATURE_NAMES), 8)
        self.assertEqual(len(TEMPORAL_TARGET_FEATURE_NAMES), 5)
        forbidden = ("target", "delta", "split", "class", "family", "program_id", "hash")
        for name in CONTEXT_INPUT_FEATURE_NAMES:
            self.assertFalse(any(term in name for term in forbidden))

    def test_witnesses_preserve_all_splits_and_stable_set_hash(self):
        first = derive_temporal_witnesses(self.dataset)
        second = derive_temporal_witnesses(self.dataset)
        self.assertEqual(first, second)
        self.assertEqual(temporal_witness_set_sha256(first), temporal_witness_set_sha256(second))
        self.assertEqual(
            {witness.split for witness in first},
            {
                HoldoutSplit.TRAIN,
                HoldoutSplit.HELD_OUT_OBJECT_CLASS,
                HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
                HoldoutSplit.HELD_OUT_COMPOSITION,
            },
        )
        self.assertEqual(len(first), self.dataset.receipt.program_count)

    def test_generator_exposes_context_dependent_declared_relation_outcomes(self):
        witnesses = derive_temporal_witnesses(self.dataset)
        self.assertEqual({witness.support_present_after for witness in witnesses}, {False, True})
        self.assertEqual({witness.near_present_after for witness in witnesses}, {False, True})
        deltas = {
            tuple(
                target - source
                for target, source in zip(
                    witness.target_translation_mm,
                    witness.source_translation_mm,
                )
            )
            for witness in witnesses
        }
        self.assertGreater(len(deltas), 1)
        for witness in witnesses:
            self.assertNotIn(witness.object_class, CONTEXT_INPUT_FEATURE_NAMES)
            self.assertNotIn(witness.operation_family, CONTEXT_INPUT_FEATURE_NAMES)

    def test_relation_post_state_follows_declared_operation_history(self):
        for record in self.dataset.records:
            witness = derive_temporal_witness(record)
            relation_by_id = {
                relation.relation_id: relation for relation in record.program.relations
            }
            support_effects = [
                operation.kind
                for operation in record.program.operations
                if operation.relation_id in relation_by_id
                and relation_by_id[operation.relation_id].kind is RelationKind.SUPPORTS
            ]
            near_effects = [
                operation.kind
                for operation in record.program.operations
                if operation.relation_id in relation_by_id
                and relation_by_id[operation.relation_id].kind is RelationKind.NEAR
            ]
            self.assertEqual(
                witness.support_present_after,
                support_effects[-1] is OperationKind.ADD_RELATION,
            )
            self.assertEqual(
                witness.near_present_after,
                bool(near_effects)
                and near_effects[-1] is OperationKind.ADD_RELATION,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
