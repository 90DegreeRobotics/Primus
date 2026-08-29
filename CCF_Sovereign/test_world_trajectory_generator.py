"""Fail-hard gates for the Stage 2 world-trajectory generator."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_schema.model import EvidenceKind, HoldoutSplit, WorldProgram  # noqa: E402
from world_schema.s3v_bridge import assert_lossless_round_trip  # noqa: E402
from world_schema.tokens import decode_program, encode_program  # noqa: E402
from world_schema.trajectory_generator import (  # noqa: E402
    DATASET_FILENAME,
    FACE_SELECTOR,
    HELD_OUT_COMPOSITION,
    HELD_OUT_OBJECT_CLASS,
    HELD_OUT_OPERATION_FAMILY,
    MANIFEST_FILENAME,
    TrajectoryDatasetError,
    TrajectoryGeneratorConfig,
    generate_dataset,
    validate_holdout_integrity,
    write_dataset,
)


def small_config() -> TrajectoryGeneratorConfig:
    return TrajectoryGeneratorConfig(
        seed=424_242,
        train_count=8,
        held_out_object_count=2,
        held_out_operation_count=2,
        held_out_composition_count=2,
    )


class WorldTrajectoryGeneratorTests(unittest.TestCase):
    def test_generation_is_deterministic_and_bounded(self):
        first = generate_dataset(small_config())
        second = generate_dataset(small_config())

        self.assertEqual(first.programs, second.programs)
        self.assertEqual(first.manifest, second.manifest)
        self.assertEqual(first.jsonl_bytes(), second.jsonl_bytes())
        self.assertEqual(len(first.programs), small_config().program_count)
        self.assertEqual(
            first.manifest["split_counts"],
            {
                "held_out_composition": 2,
                "held_out_object_class": 2,
                "held_out_operation_family": 2,
                "train": 8,
            },
        )
        for program in first.programs:
            self.assertEqual(len(program.frames), 3)
            self.assertEqual(
                [frame.tick for frame in program.frames],
                [0, 1, 2],
            )
            self.assertEqual(
                {binding.kind for binding in program.evidence},
                {EvidenceKind.GENERATED, EvidenceKind.INFERRED},
            )

    def test_every_program_round_trips_codec_and_s3v(self):
        dataset = generate_dataset(small_config())
        for program in dataset.programs:
            encoded = encode_program(program)
            restored = decode_program(encoded.token_ids)
            self.assertEqual(restored, program)
            self.assertEqual(encoded.program_sha256, program.sha256())
            assert_lossless_round_trip(program)

    def test_holdouts_are_whole_family_and_composition(self):
        dataset = generate_dataset(small_config())
        partitions = tuple(program.partition for program in dataset.programs)
        train = tuple(
            partition
            for partition in partitions
            if partition.split is HoldoutSplit.TRAIN
        )
        train_objects = {partition.object_class for partition in train}
        train_operations = {partition.operation_family for partition in train}
        train_pairs = {
            (partition.object_class, partition.operation_family)
            for partition in train
        }

        self.assertNotIn(HELD_OUT_OBJECT_CLASS, train_objects)
        self.assertNotIn(HELD_OUT_OPERATION_FAMILY, train_operations)
        self.assertNotIn(HELD_OUT_COMPOSITION, train_pairs)
        self.assertIn(HELD_OUT_COMPOSITION[0], train_objects)
        self.assertIn(HELD_OUT_COMPOSITION[1], train_operations)
        validate_holdout_integrity(dataset.programs)

    def test_structural_coverage_is_measured_not_inferred_from_tokens(self):
        dataset = generate_dataset(small_config())
        coverage = dataset.manifest["structural_coverage"]
        self.assertEqual(coverage["programs"], small_config().program_count)
        self.assertEqual(coverage["unique_programs"], small_config().program_count)
        self.assertEqual(coverage["duplicate_programs"], 0)
        self.assertEqual(coverage["unique_program_fraction"], 1.0)
        self.assertGreater(
            dataset.manifest["token_sequence_lengths"]["minimum"],
            0,
        )

    def test_manifest_hashes_and_existing_destination_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_dir = root / "dataset_first"
            second_dir = root / "dataset_second"
            first = write_dataset(first_dir, small_config())
            second = write_dataset(second_dir, small_config())

            first_dataset = first_dir / DATASET_FILENAME
            first_manifest = first_dir / MANIFEST_FILENAME
            manifest = json.loads(first_manifest.read_text(encoding="utf-8"))
            dataset_sha = hashlib.sha256(first_dataset.read_bytes()).hexdigest()
            manifest_sha = hashlib.sha256(first_manifest.read_bytes()).hexdigest()

            self.assertEqual(first.dataset_sha256, dataset_sha)
            self.assertEqual(first.manifest_sha256, manifest_sha)
            self.assertEqual(
                manifest["files"][DATASET_FILENAME]["sha256"],
                dataset_sha,
            )
            self.assertEqual(
                manifest["files"][DATASET_FILENAME]["records"],
                small_config().program_count,
            )
            self.assertEqual(first_dataset.read_bytes(), (second_dir / DATASET_FILENAME).read_bytes())
            self.assertEqual(first_manifest.read_bytes(), (second_dir / MANIFEST_FILENAME).read_bytes())
            self.assertEqual(first.dataset_sha256, second.dataset_sha256)
            self.assertEqual(first.manifest_sha256, second.manifest_sha256)
            self.assertFalse(manifest["claims"]["model_training_started"])
            self.assertFalse(manifest["claims"]["candidate_promoted"])

            with self.assertRaises(FileExistsError):
                write_dataset(first_dir, small_config())

    def test_jsonl_records_are_canonical_world_programs(self):
        dataset = generate_dataset(small_config())
        records = dataset.jsonl_bytes().decode("utf-8").splitlines()
        restored = tuple(WorldProgram.from_dict(json.loads(line)) for line in records)
        self.assertEqual(restored, dataset.programs)
        self.assertTrue(
            all(line == program.canonical_json() for line, program in zip(records, restored))
        )

    def test_geometry_invocation_declares_only_the_executable_contract(self):
        """The invocation must carry what the macro needs to run, and nothing
        else. A native consumer refuses unknown keys, so an extra declared knob
        here is a cross-repo break, not a harmless addition."""
        signed_cardinals = {
            "positive_x", "negative_x",
            "positive_y", "negative_y",
            "positive_z", "negative_z",
        }
        dataset = generate_dataset(small_config())
        seen_axes = set()
        checked = 0
        for program in dataset.programs:
            for operation in program.operations:
                if operation.geometry is None:
                    continue
                checked += 1
                parameters = operation.geometry.parameters
                self.assertEqual(
                    set(parameters), {"selector", "axis", "distance_mm"}
                )
                self.assertEqual(parameters["selector"], FACE_SELECTOR)
                self.assertIn(parameters["axis"], signed_cardinals)
                seen_axes.add(parameters["axis"])
                distance = parameters["distance_mm"]
                self.assertIsInstance(distance, int)
                self.assertNotIsInstance(distance, bool)
                self.assertTrue(1 <= distance <= 10_000)
                self.assertEqual(operation.geometry.target_id, operation.subject_id)
        self.assertGreater(checked, 0)
        self.assertGreater(len(seen_axes), 1)

    def test_declared_knobs_live_on_the_operation_not_the_invocation(self):
        """Trajectory knobs are learning features, not execution arguments.
        They must stay reachable, and must stay out of the macro contract."""
        dataset = generate_dataset(small_config())
        checked = 0
        for program in dataset.programs:
            for operation in program.operations:
                if operation.geometry is None:
                    continue
                checked += 1
                self.assertEqual(
                    set(operation.parameters),
                    {"extent_mm", "bevel_q", "variant"},
                )
                # The executable distance is the declared extent, not a new
                # value invented for the consumer.
                self.assertEqual(
                    operation.geometry.parameters["distance_mm"],
                    operation.parameters["extent_mm"],
                )
                for key in ("extent_mm", "bevel_q", "variant"):
                    self.assertNotIn(key, operation.geometry.parameters)
        self.assertGreater(checked, 0)

    def test_invalid_configuration_and_holdout_leak_fail_closed(self):
        with self.assertRaises(TrajectoryDatasetError):
            generate_dataset(replace(small_config(), train_count=7))

        dataset = generate_dataset(small_config())
        leaked = list(dataset.programs)
        held_index = next(
            index
            for index, program in enumerate(leaked)
            if program.partition.split is HoldoutSplit.HELD_OUT_OBJECT_CLASS
        )
        leaked_program = leaked[held_index]
        leaked[held_index] = replace(
            leaked_program,
            partition=replace(leaked_program.partition, split=HoldoutSplit.TRAIN),
        )
        with self.assertRaises(TrajectoryDatasetError):
            validate_holdout_integrity(leaked)


if __name__ == "__main__":
    unittest.main(verbosity=2)
