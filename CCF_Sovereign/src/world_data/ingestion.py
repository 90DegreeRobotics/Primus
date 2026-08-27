"""Manifest-bound ingestion for deterministic Primus world trajectories.

The loader is deliberately separate from candidate training. It reads canonical
Stage 2 JSONL, verifies its hash-bound manifest, revalidates each typed world
program, preserves whole-family partitions through segments and batches, and
rejects leakage from emitted data rather than trusting manifest declarations.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from world_schema.model import HoldoutSplit, WorldProgram, WorldSchemaError
from world_schema.tokens import EncodedWorldProgram, encode_program, structural_program_signature


WORLD_DATA_MANIFEST_VERSION = 1
EXPECTED_ARTIFACT_TYPE = "primus_grounded_world_trajectories"
REQUIRED_SPLITS = (
    HoldoutSplit.TRAIN,
    HoldoutSplit.HELD_OUT_OBJECT_CLASS,
    HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
    HoldoutSplit.HELD_OUT_COMPOSITION,
)


class WorldDataError(ValueError):
    """Raised when world-trajectory ingestion cannot prove data integrity."""


@dataclass(frozen=True)
class WorldIngestionConfig:
    """Deterministic segmentation and batching controls for a frozen dataset."""

    segment_length: int = 256
    segment_stride: int = 255
    batch_size: int = 4

    def validate(self) -> None:
        if self.segment_length < 2:
            raise WorldDataError("segment_length must be at least 2")
        if not 1 <= self.segment_stride <= self.segment_length:
            raise WorldDataError(
                "segment_stride must be in [1, segment_length]"
            )
        if self.batch_size < 1:
            raise WorldDataError("batch_size must be positive")


@dataclass(frozen=True)
class WorldProgramRecord:
    """Validated source record plus its canonical sequence and split evidence."""

    program: WorldProgram
    source_path: str
    line_number: int
    program_sha256: str
    structural_signature: str
    encoded: EncodedWorldProgram
    evidence_sha256s: tuple[str, ...]

    @property
    def split(self) -> HoldoutSplit:
        if self.program.partition is None:
            raise WorldDataError("validated record has no dataset partition")
        return self.program.partition.split

    @property
    def object_class(self) -> str:
        if self.program.partition is None:
            raise WorldDataError("validated record has no dataset partition")
        return self.program.partition.object_class

    @property
    def operation_family(self) -> str:
        if self.program.partition is None:
            raise WorldDataError("validated record has no dataset partition")
        return self.program.partition.operation_family

    @property
    def generator_family(self) -> str:
        if self.program.partition is None:
            raise WorldDataError("validated record has no dataset partition")
        return self.program.partition.generator_family


@dataclass(frozen=True)
class WorldSegment:
    """One bounded token sequence with immutable source and partition lineage."""

    segment_id: str
    program_id: str
    program_sha256: str
    structural_signature: str
    split: HoldoutSplit
    object_class: str
    operation_family: str
    generator_family: str
    evidence_sha256s: tuple[str, ...]
    token_start: int
    token_stop: int
    source_token_count: int
    token_ids: tuple[int, ...]

    def validate(self) -> None:
        if not self.segment_id or not self.program_id:
            raise WorldDataError("segment and program IDs are required")
        if not 0 <= self.token_start < self.token_stop <= self.source_token_count:
            raise WorldDataError(f"invalid segment bounds: {self.segment_id}")
        if self.token_stop - self.token_start != len(self.token_ids):
            raise WorldDataError(f"token bounds disagree: {self.segment_id}")
        if len(self.token_ids) < 2:
            raise WorldDataError(
                f"segment must retain at least two tokens: {self.segment_id}"
            )
        if len(self.program_sha256) != 64:
            raise WorldDataError(f"invalid program hash: {self.segment_id}")
        if len(self.structural_signature) != 64:
            raise WorldDataError(f"invalid structural signature: {self.segment_id}")


@dataclass(frozen=True)
class WorldBatch:
    """A deterministic same-split batch of world-trajectory segments."""

    batch_id: str
    split: HoldoutSplit
    segments: tuple[WorldSegment, ...]

    def validate(self) -> None:
        if not self.batch_id:
            raise WorldDataError("batch_id is required")
        if not self.segments:
            raise WorldDataError(f"batch has no segments: {self.batch_id}")
        if any(segment.split is not self.split for segment in self.segments):
            raise WorldDataError(f"batch mixes partitions: {self.batch_id}")
        for segment in self.segments:
            segment.validate()

    @property
    def token_sequences(self) -> tuple[tuple[int, ...], ...]:
        return tuple(segment.token_ids for segment in self.segments)


@dataclass(frozen=True)
class WorldDataReceipt:
    """Immutable ingestion evidence that can be bound into a later candidate run."""

    manifest_path: str
    manifest_sha256: str
    dataset_path: str
    dataset_sha256: str
    dataset_bytes: int
    program_count: int
    segment_count: int
    batch_count: int
    split_program_counts: dict[str, int]
    split_segment_counts: dict[str, int]
    split_batch_counts: dict[str, int]
    config: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IngestedWorldDataset:
    """Complete no-training result of a successful world-data ingestion pass."""

    receipt: WorldDataReceipt
    records: tuple[WorldProgramRecord, ...]
    segments: tuple[WorldSegment, ...]
    batches: tuple[WorldBatch, ...]


def sha256_file(path: Path) -> str:
    """Return a streamed SHA-256 for an input artifact."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WorldDataError(f"{label} must be an object")
    return value


def _load_manifest(path: Path) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        raise WorldDataError(f"manifest does not exist: {path}")
    manifest_sha256 = sha256_file(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WorldDataError(f"manifest is not valid UTF-8 JSON: {path}") from error
    if not isinstance(raw, dict):
        raise WorldDataError("manifest root must be an object")
    if raw.get("artifact_type") != EXPECTED_ARTIFACT_TYPE:
        raise WorldDataError("manifest artifact_type is not a Stage 2 trajectory dataset")
    if raw.get("program_count") is None:
        raise WorldDataError("manifest program_count is required")
    claims = _require_mapping(raw.get("claims"), "manifest claims")
    required_false_claims = (
        "model_training_started",
        "checkpoint_modified",
        "candidate_promoted",
        "learned_world_dynamics_proven",
        "visual_correctness_proven",
    )
    for name in required_false_claims:
        if claims.get(name) is not False:
            raise WorldDataError(f"manifest claim must remain false: {name}")
    holdouts = _require_mapping(raw.get("holdout_contract"), "holdout_contract")
    if holdouts.get("random_example_split") is not False:
        raise WorldDataError("random-example split is forbidden for world trajectories")
    return raw, manifest_sha256


def _verify_source_file(
    dataset_path: Path,
    manifest: Mapping[str, Any],
) -> tuple[str, int]:
    if not dataset_path.is_file():
        raise WorldDataError(f"dataset does not exist: {dataset_path}")
    files = _require_mapping(manifest.get("files"), "manifest files")
    evidence = _require_mapping(files.get(dataset_path.name), "dataset file evidence")
    expected_hash = str(evidence.get("sha256", "")).lower()
    expected_bytes = evidence.get("bytes")
    expected_records = evidence.get("records")
    if len(expected_hash) != 64:
        raise WorldDataError("dataset file evidence has no valid SHA-256")
    try:
        expected_bytes = int(expected_bytes)
        expected_records = int(expected_records)
    except (TypeError, ValueError) as error:
        raise WorldDataError(
            "dataset file evidence has no valid byte or record count"
        ) from error
    if expected_records != int(manifest["program_count"]):
        raise WorldDataError(
            "dataset file record count disagrees with manifest program_count"
        )
    actual_hash = sha256_file(dataset_path)
    actual_bytes = dataset_path.stat().st_size
    if actual_hash != expected_hash:
        raise WorldDataError(
            f"dataset SHA-256 mismatch: expected {expected_hash}, got {actual_hash}"
        )
    if actual_bytes != expected_bytes:
        raise WorldDataError(
            f"dataset byte count mismatch: expected {expected_bytes}, got {actual_bytes}"
        )
    return actual_hash, actual_bytes


def _parse_records(dataset_path: Path) -> tuple[WorldProgramRecord, ...]:
    records: list[WorldProgramRecord] = []
    try:
        lines = dataset_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise WorldDataError(f"cannot read dataset as UTF-8: {dataset_path}") from error
    for line_number, line in enumerate(lines, start=1):
        if not line:
            raise WorldDataError(f"blank JSONL record at line {line_number}")
        try:
            raw = json.loads(line)
            program = WorldProgram.from_dict(raw)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, WorldSchemaError) as error:
            raise WorldDataError(
                f"invalid WorldProgram at line {line_number}: {error}"
            ) from error
        if line != program.canonical_json():
            raise WorldDataError(
                f"non-canonical WorldProgram JSON at line {line_number}"
            )
        if program.partition is None:
            raise WorldDataError(f"WorldProgram has no partition at line {line_number}")
        encoded = encode_program(program)
        if encoded.program_sha256 != program.sha256():
            raise WorldDataError(f"codec digest mismatch at line {line_number}")
        records.append(
            WorldProgramRecord(
                program=program,
                source_path=str(dataset_path),
                line_number=line_number,
                program_sha256=program.sha256(),
                structural_signature=structural_program_signature(program),
                encoded=encoded,
                evidence_sha256s=tuple(
                    sorted(binding.source_sha256 for binding in program.evidence)
                ),
            )
        )
    if not records:
        raise WorldDataError("dataset contains no WorldProgram records")
    return tuple(records)


def _split_counter(values: Iterable[HoldoutSplit]) -> dict[str, int]:
    return dict(sorted(Counter(value.value for value in values).items()))


def _expected_strings(value: Any, label: str) -> set[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise WorldDataError(f"{label} must be a non-empty list of strings")
    return set(value)


def validate_record_integrity(
    records: Iterable[WorldProgramRecord],
    manifest: Mapping[str, Any],
) -> tuple[WorldProgramRecord, ...]:
    """Re-verify program and source-evidence separation from parsed records."""

    materialized = tuple(records)
    if not materialized:
        raise WorldDataError("no parsed records to validate")
    if len(materialized) != int(manifest["program_count"]):
        raise WorldDataError("manifest program_count disagrees with JSONL records")
    record_counts = _split_counter(record.split for record in materialized)
    declared_counts = _require_mapping(manifest.get("split_counts"), "split_counts")
    normalized_declared = dict(
        sorted((str(name), int(count)) for name, count in declared_counts.items())
    )
    if record_counts != normalized_declared:
        raise WorldDataError(
            f"emitted split counts disagree with manifest: {record_counts} != {normalized_declared}"
        )
    if set(record_counts) != {split.value for split in REQUIRED_SPLITS}:
        raise WorldDataError("every required train and whole-family holdout split is required")

    program_hashes = [record.program_sha256 for record in materialized]
    if len(program_hashes) != len(set(program_hashes)):
        raise WorldDataError("duplicate canonical WorldProgram hash in dataset")
    program_hash_set_sha256 = hashlib.sha256(
        ("\n".join(program_hashes) + "\n").encode("ascii")
    ).hexdigest()
    if manifest.get("program_hash_set_sha256") != program_hash_set_sha256:
        raise WorldDataError("program hash-set digest disagrees with manifest")
    signatures = [record.structural_signature for record in materialized]
    coverage = _require_mapping(manifest.get("structural_coverage"), "structural_coverage")
    actual_coverage = {
        "programs": len(signatures),
        "unique_programs": len(set(signatures)),
        "duplicate_programs": len(signatures) - len(set(signatures)),
        "unique_program_fraction": len(set(signatures)) / len(signatures),
    }
    for name, value in actual_coverage.items():
        if coverage.get(name) != value:
            raise WorldDataError(f"structural coverage mismatch: {name}")

    grouped: dict[HoldoutSplit, tuple[WorldProgramRecord, ...]] = {
        split: tuple(record for record in materialized if record.split is split)
        for split in REQUIRED_SPLITS
    }
    train = grouped[HoldoutSplit.TRAIN]
    train_objects = {record.object_class for record in train}
    train_operations = {record.operation_family for record in train}
    train_generators = {record.generator_family for record in train}
    train_pairs = {(record.object_class, record.operation_family) for record in train}
    train_hashes = {record.program_sha256 for record in train}
    train_signatures = {record.structural_signature for record in train}
    train_evidence = {
        source_hash for record in train for source_hash in record.evidence_sha256s
    }

    contract = _require_mapping(manifest.get("holdout_contract"), "holdout_contract")
    held_objects = _expected_strings(
        contract.get("held_out_object_classes"), "held_out_object_classes"
    )
    held_operations = _expected_strings(
        contract.get("held_out_operation_families"), "held_out_operation_families"
    )
    raw_compositions = contract.get("held_out_compositions")
    if not isinstance(raw_compositions, list) or not raw_compositions:
        raise WorldDataError("held_out_compositions must be a non-empty list")
    held_compositions = {
        tuple(str(value) for value in pair)
        for pair in raw_compositions
        if isinstance(pair, list) and len(pair) == 2
    }
    if len(held_compositions) != len(raw_compositions):
        raise WorldDataError("each held-out composition must contain object and operation")

    held_object_records = grouped[HoldoutSplit.HELD_OUT_OBJECT_CLASS]
    if {record.object_class for record in held_object_records} != held_objects:
        raise WorldDataError("emitted held-out object classes disagree with contract")
    if train_objects & held_objects:
        raise WorldDataError("held-out object class leaked into emitted training records")

    held_operation_records = grouped[HoldoutSplit.HELD_OUT_OPERATION_FAMILY]
    if {record.operation_family for record in held_operation_records} != held_operations:
        raise WorldDataError("emitted held-out operation families disagree with contract")
    if train_operations & held_operations:
        raise WorldDataError("held-out operation family leaked into emitted training records")

    held_composition_records = grouped[HoldoutSplit.HELD_OUT_COMPOSITION]
    actual_compositions = {
        (record.object_class, record.operation_family)
        for record in held_composition_records
    }
    if actual_compositions != held_compositions:
        raise WorldDataError("emitted held-out compositions disagree with contract")
    if train_pairs & held_compositions:
        raise WorldDataError("held-out composition leaked into emitted training records")
    for object_class, operation_family in held_compositions:
        if object_class not in train_objects or operation_family not in train_operations:
            raise WorldDataError("held-out composition is not composed from training families")
    if train_generators & {record.generator_family for record in held_composition_records}:
        raise WorldDataError("held-out composition generator family leaked into training")

    for split in REQUIRED_SPLITS[1:]:
        held = grouped[split]
        held_hashes = {record.program_sha256 for record in held}
        held_signatures = {record.structural_signature for record in held}
        held_evidence = {
            source_hash for record in held for source_hash in record.evidence_sha256s
        }
        if train_hashes & held_hashes:
            raise WorldDataError(f"program hash overlap between train and {split.value}")
        if train_signatures & held_signatures:
            raise WorldDataError(
                f"structural signature overlap between train and {split.value}"
            )
        if train_evidence & held_evidence:
            raise WorldDataError(
                f"source-evidence hash overlap between train and {split.value}"
            )
    return materialized


def segment_records(
    records: Iterable[WorldProgramRecord],
    config: WorldIngestionConfig | None = None,
) -> tuple[WorldSegment, ...]:
    """Segment records deterministically while retaining one-token continuity."""

    resolved = config or WorldIngestionConfig()
    resolved.validate()
    segments: list[WorldSegment] = []
    for record in records:
        tokens = record.encoded.token_ids
        if len(tokens) < 2:
            raise WorldDataError(f"program token stream is too short: {record.program.program_id}")
        segment_index = 0
        for start in range(0, len(tokens), resolved.segment_stride):
            stop = min(start + resolved.segment_length, len(tokens))
            token_ids = tokens[start:stop]
            if len(token_ids) < 2:
                break
            segment = WorldSegment(
                segment_id=f"{record.program.program_id}_segment_{segment_index:05d}",
                program_id=record.program.program_id,
                program_sha256=record.program_sha256,
                structural_signature=record.structural_signature,
                split=record.split,
                object_class=record.object_class,
                operation_family=record.operation_family,
                generator_family=record.generator_family,
                evidence_sha256s=record.evidence_sha256s,
                token_start=start,
                token_stop=stop,
                source_token_count=len(tokens),
                token_ids=tuple(token_ids),
            )
            segment.validate()
            segments.append(segment)
            segment_index += 1
    if not segments:
        raise WorldDataError("segmentation produced no learnable token sequences")
    return tuple(segments)


def make_batches(
    segments: Iterable[WorldSegment],
    config: WorldIngestionConfig | None = None,
) -> tuple[WorldBatch, ...]:
    """Create stable same-split batches without reordering source lineage."""

    resolved = config or WorldIngestionConfig()
    resolved.validate()
    grouped: dict[HoldoutSplit, list[WorldSegment]] = defaultdict(list)
    for segment in segments:
        segment.validate()
        grouped[segment.split].append(segment)
    batches: list[WorldBatch] = []
    for split in REQUIRED_SPLITS:
        split_segments = grouped.get(split, [])
        for offset in range(0, len(split_segments), resolved.batch_size):
            members = tuple(split_segments[offset : offset + resolved.batch_size])
            batch = WorldBatch(
                batch_id=f"{split.value}_batch_{offset // resolved.batch_size:05d}",
                split=split,
                segments=members,
            )
            batch.validate()
            batches.append(batch)
    if not batches:
        raise WorldDataError("batching produced no batches")
    return tuple(batches)


def verify_emitted_batches(
    batches: Iterable[WorldBatch],
    config: WorldIngestionConfig | None = None,
) -> tuple[WorldBatch, ...]:
    """Prove split isolation and segment continuity from emitted batches alone."""

    resolved = config or WorldIngestionConfig()
    resolved.validate()
    materialized = tuple(batches)
    if not materialized:
        raise WorldDataError("no emitted batches to verify")
    observed_splits = {batch.split for batch in materialized}
    if observed_splits != set(REQUIRED_SPLITS):
        raise WorldDataError("emitted batches do not preserve every required split")

    all_segments = tuple(segment for batch in materialized for segment in batch.segments)
    segment_ids = [segment.segment_id for segment in all_segments]
    if len(segment_ids) != len(set(segment_ids)):
        raise WorldDataError("duplicate segment ID in emitted batches")
    train_segments = [segment for segment in all_segments if segment.split is HoldoutSplit.TRAIN]
    train_hashes = {segment.program_sha256 for segment in train_segments}
    train_signatures = {segment.structural_signature for segment in train_segments}
    train_evidence = {
        source_hash for segment in train_segments for source_hash in segment.evidence_sha256s
    }
    grouped_segments = {
        split: [segment for segment in all_segments if segment.split is split]
        for split in REQUIRED_SPLITS
    }
    for split in REQUIRED_SPLITS[1:]:
        held = grouped_segments[split]
        if not held:
            raise WorldDataError(f"no emitted batches for {split.value}")
        if train_hashes & {segment.program_sha256 for segment in held}:
            raise WorldDataError(f"batch program-hash overlap for {split.value}")
        if train_signatures & {segment.structural_signature for segment in held}:
            raise WorldDataError(f"batch structural-signature overlap for {split.value}")
        held_evidence = {
            source_hash for segment in held for source_hash in segment.evidence_sha256s
        }
        if train_evidence & held_evidence:
            raise WorldDataError(f"batch evidence overlap for {split.value}")

    train_objects = {segment.object_class for segment in train_segments}
    train_operations = {segment.operation_family for segment in train_segments}
    train_pairs = {
        (segment.object_class, segment.operation_family)
        for segment in train_segments
    }
    train_generators = {segment.generator_family for segment in train_segments}
    held_object_classes = {
        segment.object_class
        for segment in grouped_segments[HoldoutSplit.HELD_OUT_OBJECT_CLASS]
    }
    if train_objects & held_object_classes:
        raise WorldDataError("batch held-out object class leaked into training")
    held_operation_families = {
        segment.operation_family
        for segment in grouped_segments[HoldoutSplit.HELD_OUT_OPERATION_FAMILY]
    }
    if train_operations & held_operation_families:
        raise WorldDataError("batch held-out operation family leaked into training")
    held_compositions = {
        (segment.object_class, segment.operation_family)
        for segment in grouped_segments[HoldoutSplit.HELD_OUT_COMPOSITION]
    }
    if train_pairs & held_compositions:
        raise WorldDataError("batch held-out composition leaked into training")
    for object_class, operation_family in held_compositions:
        if object_class not in train_objects or operation_family not in train_operations:
            raise WorldDataError("batch composition is not assembled from training families")
    held_composition_generators = {
        segment.generator_family
        for segment in grouped_segments[HoldoutSplit.HELD_OUT_COMPOSITION]
    }
    if train_generators & held_composition_generators:
        raise WorldDataError("batch composition generator family leaked into training")

    by_program: dict[str, list[WorldSegment]] = defaultdict(list)
    for segment in all_segments:
        if len(segment.token_ids) > resolved.segment_length:
            raise WorldDataError(f"segment exceeds configured length: {segment.segment_id}")
        by_program[segment.program_sha256].append(segment)
    for program_hash, program_segments in by_program.items():
        ordered = sorted(program_segments, key=lambda item: item.token_start)
        if ordered[0].token_start != 0:
            raise WorldDataError(f"program does not start at token zero: {program_hash}")
        for previous, current in zip(ordered, ordered[1:]):
            if current.token_start > previous.token_stop:
                raise WorldDataError(f"segment gap for program: {program_hash}")
            if current.token_start - previous.token_start != resolved.segment_stride:
                raise WorldDataError(f"non-deterministic segment stride: {program_hash}")
        if ordered[-1].token_stop != ordered[-1].source_token_count:
            raise WorldDataError(f"program is not covered through final token: {program_hash}")
    return materialized


def ingest_world_dataset(
    dataset_path: str | Path,
    manifest_path: str | Path,
    config: WorldIngestionConfig | None = None,
) -> IngestedWorldDataset:
    """Read one frozen Stage 2 dataset without starting training or mutating it."""

    resolved = config or WorldIngestionConfig()
    resolved.validate()
    data_path = Path(dataset_path).expanduser().resolve()
    source_manifest_path = Path(manifest_path).expanduser().resolve()
    manifest, manifest_sha256 = _load_manifest(source_manifest_path)
    dataset_sha256, dataset_bytes = _verify_source_file(data_path, manifest)
    records = validate_record_integrity(_parse_records(data_path), manifest)
    segments = segment_records(records, resolved)
    batches = verify_emitted_batches(make_batches(segments, resolved), resolved)
    receipt = WorldDataReceipt(
        manifest_path=str(source_manifest_path),
        manifest_sha256=manifest_sha256,
        dataset_path=str(data_path),
        dataset_sha256=dataset_sha256,
        dataset_bytes=dataset_bytes,
        program_count=len(records),
        segment_count=len(segments),
        batch_count=len(batches),
        split_program_counts=_split_counter(record.split for record in records),
        split_segment_counts=_split_counter(segment.split for segment in segments),
        split_batch_counts=_split_counter(batch.split for batch in batches),
        config=asdict(resolved),
    )
    return IngestedWorldDataset(
        receipt=receipt,
        records=records,
        segments=segments,
        batches=batches,
    )
