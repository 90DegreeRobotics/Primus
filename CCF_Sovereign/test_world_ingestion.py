"""Fail-hard gates for manifest-bound Stage 2 world-data ingestion."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_data.ingestion import (  # noqa: E402
    WorldDataError,
    WorldIngestionConfig,
    ingest_world_dataset,
    verify_emitted_batches,
)
from world_schema.model import HoldoutSplit  # noqa: E402
from world_schema.trajectory_generator import (  # noqa: E402
    DATASET_FILENAME,
    MANIFEST_FILENAME,
    TrajectoryGeneratorConfig,
    generate_dataset,
    write_dataset,
)


def generator_config() -> TrajectoryGeneratorConfig:
    return TrajectoryGeneratorConfig(
        seed=987_654,
        train_count=8,
        held_out_object_count=2,
        held_out_operation_count=2,
        held_out_composition_count=2,
    )


def ingestion_config() -> WorldIngestionConfig:
    return WorldIngestionConfig(segment_length=256, segment_stride=255, batch_size=3)


def canonical_jsonl(programs) -> bytes:
    return b"".join(program.canonical_json().encode("utf-8") + b"\n" for program in programs)


def write_dataset_copy(
    root: Path,
    programs,
    base_manifest: dict,
) -> tuple[Path, Path]:
    root.mkdir()
    dataset_path = root / DATASET_FILENAME
    manifest_path = root / MANIFEST_FILENAME
    dataset_bytes = canonical_jsonl(programs)
    manifest = copy.deepcopy(base_manifest)
    split_counts: dict[str, int] = {}
    for program in programs:
        split = program.partition.split.value
        split_counts[split] = split_counts.get(split, 0) + 1
    signatures = [
        program.sha256()  # manifest integrity is checked separately from structural coverage
        for program in programs
    ]
    manifest["program_count"] = len(programs)
    manifest["split_counts"] = dict(sorted(split_counts.items()))
    manifest["files"] = {
        DATASET_FILENAME: {
            "bytes": len(dataset_bytes),
            "records": len(programs),
            "sha256": hashlib.sha256(dataset_bytes).hexdigest(),
        }
    }
    # The normal dataset has full unique structural coverage; modified tests can
    # deliberately override this field when they need to reach a later gate.
    manifest["program_hash_set_sha256"] = hashlib.sha256(
        ("\n".join(signatures) + "\n").encode("ascii")
    ).hexdigest()
    dataset_path.write_bytes(dataset_bytes)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return dataset_path, manifest_path


class WorldIngestionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source_dir = self.root / "source"
        self.source_receipt = write_dataset(self.source_dir, generator_config())
        self.dataset_path = self.source_dir / DATASET_FILENAME
        self.manifest_path = self.source_dir / MANIFEST_FILENAME
        self.config = ingestion_config()

    def tearDown(self):
        self.temporary.cleanup()

    def _ingest(self):
        return ingest_world_dataset(self.dataset_path, self.manifest_path, self.config)

    def _manifest(self) -> dict:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def test_ingests_manifest_bound_records_and_emits_split_safe_batches(self):
        ingested = self._ingest()
        receipt = ingested.receipt

        self.assertEqual(receipt.dataset_sha256, self.source_receipt.dataset_sha256)
        self.assertEqual(receipt.manifest_sha256, self.source_receipt.manifest_sha256)
        self.assertEqual(receipt.program_count, generator_config().program_count)
        self.assertGreater(receipt.segment_count, receipt.program_count)
        self.assertGreater(receipt.batch_count, 4)
        self.assertEqual(
            receipt.split_program_counts,
            {
                "held_out_composition": 2,
                "held_out_object_class": 2,
                "held_out_operation_family": 2,
                "train": 8,
            },
        )
        self.assertEqual(
            {batch.split for batch in ingested.batches},
            {
                HoldoutSplit.TRAIN,
                HoldoutSplit.HELD_OUT_OBJECT_CLASS,
                HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
                HoldoutSplit.HELD_OUT_COMPOSITION,
            },
        )
        self.assertTrue(all(len(batch.segments) <= 3 for batch in ingested.batches))
        self.assertTrue(
            all(
                all(segment.split is batch.split for segment in batch.segments)
                for batch in ingested.batches
            )
        )

    def test_segmentation_and_batching_are_deterministic_from_the_same_input(self):
        first = self._ingest()
        second = self._ingest()

        self.assertEqual(first.receipt, second.receipt)
        self.assertEqual(first.segments, second.segments)
        self.assertEqual(first.batches, second.batches)
        by_program = {}
        for segment in first.segments:
            by_program.setdefault(segment.program_id, []).append(segment)
        for segments in by_program.values():
            ordered = sorted(segments, key=lambda segment: segment.token_start)
            self.assertEqual(ordered[0].token_start, 0)
            self.assertEqual(ordered[-1].token_stop, ordered[-1].source_token_count)
            for previous, current in zip(ordered, ordered[1:]):
                self.assertEqual(current.token_start - previous.token_start, 255)
                self.assertLessEqual(current.token_start, previous.token_stop)

    def test_dataset_hash_drift_fails_before_record_parsing(self):
        with self.dataset_path.open("ab") as handle:
            handle.write(b"\n")
        with self.assertRaisesRegex(WorldDataError, "SHA-256 mismatch"):
            self._ingest()

    def test_manifest_nontraining_claim_drift_fails_closed(self):
        manifest = self._manifest()
        manifest["claims"]["candidate_promoted"] = True
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(WorldDataError, "candidate_promoted"):
            self._ingest()

    def test_program_hash_set_drift_fails_after_file_evidence_verification(self):
        manifest = self._manifest()
        manifest["program_hash_set_sha256"] = "0" * 64
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(WorldDataError, "program hash-set digest"):
            self._ingest()

    def test_malformed_json_is_rejected_after_file_evidence_verification(self):
        modified_dir = self.root / "malformed"
        manifest = self._manifest()
        dataset_path = modified_dir / DATASET_FILENAME
        modified_dir.mkdir()
        dataset_path.write_text("{not-json}\n", encoding="utf-8")
        manifest["program_count"] = 1
        manifest["files"] = {
            DATASET_FILENAME: {
                "bytes": dataset_path.stat().st_size,
                "records": 1,
                "sha256": hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
            }
        }
        manifest_path = modified_dir / MANIFEST_FILENAME
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(WorldDataError, "invalid WorldProgram"):
            ingest_world_dataset(dataset_path, manifest_path, self.config)

    def test_whole_object_holdout_leakage_is_rejected_from_records(self):
        dataset = generate_dataset(generator_config())
        programs = list(dataset.programs)
        index = next(
            i
            for i, program in enumerate(programs)
            if program.partition.split is HoldoutSplit.HELD_OUT_OBJECT_CLASS
        )
        target = programs[index]
        programs[index] = replace(
            target,
            partition=replace(target.partition, split=HoldoutSplit.TRAIN),
        )
        data_path, manifest_path = write_dataset_copy(
            self.root / "object_leak",
            programs,
            dataset.manifest,
        )
        with self.assertRaisesRegex(WorldDataError, "held-out object class leaked"):
            ingest_world_dataset(data_path, manifest_path, self.config)

    def test_structural_signature_overlap_is_rejected_from_records(self):
        dataset = generate_dataset(generator_config())
        programs = list(dataset.programs)
        train = next(
            program
            for program in programs
            if program.partition.split is HoldoutSplit.TRAIN
        )
        index = next(
            i
            for i, program in enumerate(programs)
            if program.partition.split is HoldoutSplit.HELD_OUT_OBJECT_CLASS
        )
        target = programs[index]
        programs[index] = replace(
            train,
            program_id=target.program_id,
            world_id=target.world_id,
            title=target.title,
            partition=target.partition,
        )
        data_path, manifest_path = write_dataset_copy(
            self.root / "signature_leak",
            programs,
            dataset.manifest,
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["structural_coverage"] = {
            "programs": len(programs),
            "unique_programs": len(programs) - 1,
            "duplicate_programs": 1,
            "unique_program_fraction": (len(programs) - 1) / len(programs),
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(WorldDataError, "structural signature overlap"):
            ingest_world_dataset(data_path, manifest_path, self.config)

    def test_source_evidence_overlap_is_rejected_from_records(self):
        dataset = generate_dataset(generator_config())
        programs = list(dataset.programs)
        train = next(
            program
            for program in programs
            if program.partition.split is HoldoutSplit.TRAIN
        )
        index = next(
            i
            for i, program in enumerate(programs)
            if program.partition.split is HoldoutSplit.HELD_OUT_OPERATION_FAMILY
        )
        target = programs[index]
        programs[index] = replace(
            target,
            evidence=tuple(
                replace(binding, source_sha256=train.evidence[offset].source_sha256)
                for offset, binding in enumerate(target.evidence)
            ),
        )
        data_path, manifest_path = write_dataset_copy(
            self.root / "evidence_leak",
            programs,
            dataset.manifest,
        )
        with self.assertRaisesRegex(WorldDataError, "source-evidence hash overlap"):
            ingest_world_dataset(data_path, manifest_path, self.config)

    def test_emitted_batch_object_holdout_leak_is_rejected_independently(self):
        ingested = self._ingest()
        train_batch_index = next(
            index
            for index, batch in enumerate(ingested.batches)
            if batch.split is HoldoutSplit.TRAIN
        )
        held_segment = next(
            segment
            for batch in ingested.batches
            if batch.split is HoldoutSplit.HELD_OUT_OBJECT_CLASS
            for segment in batch.segments
        )
        train_batch = ingested.batches[train_batch_index]
        leaked_segment = replace(
            held_segment,
            segment_id="leaked_object_segment",
            program_id="leaked_object_program",
            program_sha256="f" * 64,
            structural_signature="e" * 64,
            evidence_sha256s=("a" * 64, "b" * 64),
            split=HoldoutSplit.TRAIN,
            token_start=0,
            token_stop=len(held_segment.token_ids),
            source_token_count=len(held_segment.token_ids),
        )
        batches = list(ingested.batches)
        batches[train_batch_index] = replace(
            train_batch,
            segments=train_batch.segments + (leaked_segment,),
        )
        with self.assertRaisesRegex(
            WorldDataError,
            "batch held-out object class leaked",
        ):
            verify_emitted_batches(batches, self.config)

    def test_missing_split_and_invalid_config_fail_closed(self):
        ingested = self._ingest()
        without_composition = tuple(
            batch
            for batch in ingested.batches
            if batch.split is not HoldoutSplit.HELD_OUT_COMPOSITION
        )
        with self.assertRaisesRegex(WorldDataError, "preserve every required split"):
            verify_emitted_batches(without_composition, self.config)
        with self.assertRaisesRegex(WorldDataError, "segment_stride"):
            WorldIngestionConfig(segment_length=16, segment_stride=17).validate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
