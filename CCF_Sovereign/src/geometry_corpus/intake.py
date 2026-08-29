"""Fail-closed intake for the frozen ``geometry_program_corpus_v1`` contract.

This module is deliberately limited to the learner-side contract.  It does not
create samples, infer object categories, invoke Blender, or train a model.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION = "geometry_program_corpus_v1"
FORBIDDEN_KEYS = frozenset(
    {
        "class",
        "object_class",
        "label",
        "name",
        "brief",
        "prompt",
        "category",
        "family",
        "noun",
        "kind_name",
    }
)
REQUIRED_MANIFEST_KEYS = frozenset(
    {
        "schema_version",
        "corpus_sha256",
        "splits_sha256",
        "schema_sha256",
    }
)


class GeometryCorpusError(ValueError):
    """Raised when the frozen geometry corpus contract is violated."""


def canonical_json(value: Any) -> str:
    """Return deterministic JSON suitable for canonical corpus identifiers."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_file(path: Path) -> str:
    """Hash a file incrementally so large real corpora do not need buffering."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GeometryCorpusError(f"{label} must be an object")
    return value


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise GeometryCorpusError(f"{label} must be a non-empty string")
    return value


def _require_nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise GeometryCorpusError(f"{label} must be a non-negative integer")
    return value


def _require_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GeometryCorpusError(f"{label} must be numeric")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise GeometryCorpusError(f"{label} must be finite")
    return parsed


def _require_vector(value: Any, label: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise GeometryCorpusError(f"{label} must be a three-item vector")
    return tuple(_require_finite_number(item, label) for item in value)  # type: ignore[return-value]


def _assert_no_forbidden_keys(value: Any, location: str = "record") -> None:
    """Reject noun-bearing keys at every nesting depth of a JSON value."""

    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise GeometryCorpusError(f"{location} has a non-string key")
            if key.lower() in FORBIDDEN_KEYS:
                raise GeometryCorpusError(
                    f"{location} contains forbidden key {key!r}; corpus records are noun-free"
                )
            _assert_no_forbidden_keys(nested_value, f"{location}.{key}")
    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            _assert_no_forbidden_keys(nested_value, f"{location}[{index}]")


@dataclass(frozen=True)
class ProgramStructure:
    """The only allowable basis for a learner-side structural split."""

    step_count: int
    op_mix: tuple[tuple[str, int], ...]
    op_signature: str

    @classmethod
    def from_mapping(cls, value: Any, *, label: str) -> "ProgramStructure":
        raw = _require_mapping(value, label)
        required = {"step_count", "op_mix", "op_signature"}
        missing = required.difference(raw)
        if missing:
            raise GeometryCorpusError(f"{label} lacks required keys: {sorted(missing)}")
        step_count = _require_nonnegative_int(raw["step_count"], f"{label}.step_count")
        raw_op_mix = _require_mapping(raw["op_mix"], f"{label}.op_mix")
        op_mix: list[tuple[str, int]] = []
        for operation, count in raw_op_mix.items():
            operation_name = _require_nonempty_string(operation, f"{label}.op_mix key")
            operation_count = _require_nonnegative_int(count, f"{label}.op_mix.{operation_name}")
            if operation_count == 0:
                raise GeometryCorpusError(f"{label}.op_mix.{operation_name} must be positive")
            op_mix.append((operation_name, operation_count))
        if not op_mix:
            raise GeometryCorpusError(f"{label}.op_mix must not be empty")
        if sum(count for _, count in op_mix) != step_count:
            raise GeometryCorpusError(f"{label}.step_count must equal the op_mix total")
        op_signature = _require_nonempty_string(raw["op_signature"], f"{label}.op_signature")
        expected_signature = "|".join(operation for operation, _ in sorted(op_mix))
        if op_signature != expected_signature:
            raise GeometryCorpusError(
                f"{label}.op_signature must be the sorted positive operation signature"
            )
        return cls(
            step_count=step_count,
            op_mix=tuple(sorted(op_mix)),
            op_signature=op_signature,
        )

    def op_mix_dict(self) -> dict[str, int]:
        return dict(self.op_mix)


@dataclass(frozen=True)
class GeometryProgramRecord:
    """One validated line from a ``geometry_program_corpus_v1`` JSONL file."""

    sample_id: str
    program: Mapping[str, Any]
    program_structure: ProgramStructure
    executed: bool
    mesh_metrics: Mapping[str, Any]
    render: Mapping[str, Any]
    view_score: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, value: Any, *, line_number: int) -> "GeometryProgramRecord":
        raw = _require_mapping(value, f"line {line_number}")
        _assert_no_forbidden_keys(raw, f"line {line_number}")
        required = {
            "schema_version",
            "sample_id",
            "program",
            "program_structure",
            "executed",
            "mesh_metrics",
            "render",
            "view_score",
        }
        missing = required.difference(raw)
        if missing:
            raise GeometryCorpusError(f"line {line_number} lacks required keys: {sorted(missing)}")
        if raw["schema_version"] != GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION:
            raise GeometryCorpusError(
                f"line {line_number} has unsupported schema_version {raw['schema_version']!r}"
            )
        program = _require_mapping(raw["program"], f"line {line_number}.program")
        expected_sample_id = _sha256_text(canonical_json(program))
        sample_id = _require_nonempty_string(raw["sample_id"], f"line {line_number}.sample_id")
        if sample_id != expected_sample_id:
            raise GeometryCorpusError(
                f"line {line_number}.sample_id does not match canonical program SHA-256"
            )
        if not isinstance(raw["executed"], bool) or not raw["executed"]:
            raise GeometryCorpusError(f"line {line_number}.executed must be true")
        mesh_metrics = _require_mapping(raw["mesh_metrics"], f"line {line_number}.mesh_metrics")
        for key in ("vert_count", "face_count", "bbox_min_mm", "bbox_max_mm"):
            if key not in mesh_metrics:
                raise GeometryCorpusError(f"line {line_number}.mesh_metrics lacks {key!r}")
        _require_nonnegative_int(mesh_metrics["vert_count"], f"line {line_number}.mesh_metrics.vert_count")
        _require_nonnegative_int(mesh_metrics["face_count"], f"line {line_number}.mesh_metrics.face_count")
        _require_vector(mesh_metrics["bbox_min_mm"], f"line {line_number}.mesh_metrics.bbox_min_mm")
        _require_vector(mesh_metrics["bbox_max_mm"], f"line {line_number}.mesh_metrics.bbox_max_mm")
        render = _require_mapping(raw["render"], f"line {line_number}.render")
        for key in ("path", "sha256", "width", "height"):
            if key not in render:
                raise GeometryCorpusError(f"line {line_number}.render lacks {key!r}")
        _require_nonempty_string(render["path"], f"line {line_number}.render.path")
        _require_nonempty_string(render["sha256"], f"line {line_number}.render.sha256")
        _require_nonnegative_int(render["width"], f"line {line_number}.render.width")
        _require_nonnegative_int(render["height"], f"line {line_number}.render.height")
        view_score = _require_mapping(raw["view_score"], f"line {line_number}.view_score")
        for key in ("score", "silhouette_overlap", "bbox_iou", "scorer_version"):
            if key not in view_score:
                raise GeometryCorpusError(f"line {line_number}.view_score lacks {key!r}")
        _require_finite_number(view_score["score"], f"line {line_number}.view_score.score")
        _require_finite_number(
            view_score["silhouette_overlap"], f"line {line_number}.view_score.silhouette_overlap"
        )
        _require_finite_number(view_score["bbox_iou"], f"line {line_number}.view_score.bbox_iou")
        _require_nonempty_string(view_score["scorer_version"], f"line {line_number}.view_score.scorer_version")
        return cls(
            sample_id=sample_id,
            program=dict(program),
            program_structure=ProgramStructure.from_mapping(
                raw["program_structure"], label=f"line {line_number}.program_structure"
            ),
            executed=True,
            mesh_metrics=dict(mesh_metrics),
            render=dict(render),
            view_score=dict(view_score),
        )


@dataclass(frozen=True)
class SplitDefinition:
    """Predeclared structure-only rules for a frozen evaluation partition."""

    held_out_length: frozenset[int]
    held_out_op_combo: frozenset[frozenset[str]]

    @classmethod
    def from_mapping(cls, value: Any) -> "SplitDefinition":
        raw = _require_mapping(value, "split definition")
        allowed = {"held_out_length", "held_out_op_combo"}
        unknown = set(raw).difference(allowed)
        if unknown:
            raise GeometryCorpusError(f"split definition has unsupported keys: {sorted(unknown)}")
        raw_lengths = raw.get("held_out_length", [])
        if not isinstance(raw_lengths, list) or not raw_lengths:
            raise GeometryCorpusError("split definition.held_out_length must be a non-empty array")
        lengths = frozenset(
            _require_nonnegative_int(item, "split definition.held_out_length item")
            for item in raw_lengths
        )
        raw_combos = raw.get("held_out_op_combo", [])
        if not isinstance(raw_combos, list) or not raw_combos:
            raise GeometryCorpusError("split definition.held_out_op_combo must be a non-empty array")
        combos: set[frozenset[str]] = set()
        for index, pair in enumerate(raw_combos):
            if not isinstance(pair, list) or len(pair) != 2:
                raise GeometryCorpusError(
                    f"split definition.held_out_op_combo[{index}] must be a two-operation array"
                )
            combo = frozenset(
                _require_nonempty_string(item, f"split definition.held_out_op_combo[{index}] item")
                for item in pair
            )
            if len(combo) != 2:
                raise GeometryCorpusError(
                    f"split definition.held_out_op_combo[{index}] must contain two distinct operations"
                )
            combos.add(combo)
        return cls(held_out_length=lengths, held_out_op_combo=frozenset(combos))

    def to_dict(self) -> dict[str, list[Any]]:
        return {
            "held_out_length": sorted(self.held_out_length),
            "held_out_op_combo": [sorted(pair) for pair in sorted(self.held_out_op_combo, key=lambda value: tuple(sorted(value)))],
        }


def split_for_structure(structure: ProgramStructure, definition: SplitDefinition) -> str:
    """Return one deterministic split using only declared program structure.

    Operation-combination holdouts take precedence so their operation signature
    cannot also appear in the training partition.  Records meeting both rules
    remain in that single, stronger holdout.
    """

    operations = frozenset(operation for operation, count in structure.op_mix if count > 0)
    if any(combo.issubset(operations) for combo in definition.held_out_op_combo):
        return "held_out_op_combo"
    if structure.step_count in definition.held_out_length:
        return "held_out_length"
    return "train"


def build_structural_splits(
    records: Iterable[GeometryProgramRecord], definition: SplitDefinition
) -> dict[str, tuple[GeometryProgramRecord, ...]]:
    """Partition records exactly once from ``program_structure`` alone."""

    splits: dict[str, list[GeometryProgramRecord]] = {
        "train": [],
        "held_out_length": [],
        "held_out_op_combo": [],
    }
    seen_sample_ids: set[str] = set()
    for record in records:
        if record.sample_id in seen_sample_ids:
            raise GeometryCorpusError(f"duplicate sample_id in corpus: {record.sample_id}")
        seen_sample_ids.add(record.sample_id)
        splits[split_for_structure(record.program_structure, definition)].append(record)
    if not splits["train"]:
        raise GeometryCorpusError("structural split leaves no train records")
    if not splits["held_out_length"]:
        raise GeometryCorpusError("structural split leaves no held_out_length records")
    if not splits["held_out_op_combo"]:
        raise GeometryCorpusError("structural split leaves no held_out_op_combo records")
    train_signatures = {record.program_structure.op_signature for record in splits["train"]}
    combo_signatures = {record.program_structure.op_signature for record in splits["held_out_op_combo"]}
    overlap = train_signatures.intersection(combo_signatures)
    if overlap:
        raise GeometryCorpusError(
            "held_out_op_combo signatures overlap train signatures: " + ", ".join(sorted(overlap))
        )
    return {name: tuple(items) for name, items in splits.items()}


@dataclass(frozen=True)
class GeometryCorpusIntake:
    """Verified corpus, structural split definition, and immutable receipt data."""

    corpus_path: Path
    manifest_path: Path
    split_path: Path
    records: tuple[GeometryProgramRecord, ...]
    split_definition: SplitDefinition
    corpus_sha256: str
    splits_sha256: str
    schema_sha256: str
    manifest_sha256: str

    def verify(self) -> None:
        """Re-verify every pinned artifact before evaluation or any future training."""

        if sha256_file(self.corpus_path) != self.corpus_sha256:
            raise GeometryCorpusError("corpus SHA-256 changed after intake")
        if sha256_file(self.split_path) != self.splits_sha256:
            raise GeometryCorpusError("split-definition SHA-256 changed after intake")
        expected_schema_sha256 = _sha256_text(GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION)
        if expected_schema_sha256 != self.schema_sha256:
            raise GeometryCorpusError("schema-version SHA-256 does not match geometry_program_corpus_v1")
        if sha256_file(self.manifest_path) != self.manifest_sha256:
            raise GeometryCorpusError("manifest SHA-256 changed after intake")

    def structural_splits(self) -> dict[str, tuple[GeometryProgramRecord, ...]]:
        self.verify()
        return build_structural_splits(self.records, self.split_definition)


def _load_json_object(path: Path, label: str) -> Mapping[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GeometryCorpusError(f"could not read {label} as JSON: {path}") from error
    return _require_mapping(parsed, label)


def _load_records(corpus_path: Path) -> tuple[GeometryProgramRecord, ...]:
    try:
        lines = corpus_path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise GeometryCorpusError(f"could not read corpus JSONL: {corpus_path}") from error
    if not lines:
        raise GeometryCorpusError("corpus JSONL is empty")
    records: list[GeometryProgramRecord] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            raise GeometryCorpusError(f"corpus JSONL has a blank line at {line_number}")
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as error:
            raise GeometryCorpusError(f"corpus JSONL line {line_number} is not valid JSON") from error
        records.append(GeometryProgramRecord.from_mapping(raw, line_number=line_number))
    return tuple(records)


def load_geometry_corpus_intake(
    corpus_path: str | Path, manifest_path: str | Path, split_path: str | Path
) -> GeometryCorpusIntake:
    """Load and fail closed on a hash-pinned ``geometry_program_corpus_v1`` intake."""

    resolved_corpus = Path(corpus_path).expanduser().resolve()
    resolved_manifest = Path(manifest_path).expanduser().resolve()
    resolved_split = Path(split_path).expanduser().resolve()
    for path, label in (
        (resolved_corpus, "corpus JSONL"),
        (resolved_manifest, "manifest"),
        (resolved_split, "split definition"),
    ):
        if not path.is_file():
            raise GeometryCorpusError(f"required {label} file is missing: {path}")
    manifest = _load_json_object(resolved_manifest, "manifest")
    missing = REQUIRED_MANIFEST_KEYS.difference(manifest)
    if missing:
        raise GeometryCorpusError(f"manifest lacks required keys: {sorted(missing)}")
    if manifest["schema_version"] != GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION:
        raise GeometryCorpusError("manifest schema_version does not match geometry_program_corpus_v1")
    expected_corpus_sha256 = _require_nonempty_string(manifest["corpus_sha256"], "manifest.corpus_sha256")
    expected_splits_sha256 = _require_nonempty_string(manifest["splits_sha256"], "manifest.splits_sha256")
    expected_schema_sha256 = _require_nonempty_string(manifest["schema_sha256"], "manifest.schema_sha256")
    actual_corpus_sha256 = sha256_file(resolved_corpus)
    actual_splits_sha256 = sha256_file(resolved_split)
    expected_schema_hash = _sha256_text(GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION)
    if actual_corpus_sha256 != expected_corpus_sha256:
        raise GeometryCorpusError("corpus SHA-256 does not match manifest")
    if actual_splits_sha256 != expected_splits_sha256:
        raise GeometryCorpusError("split-definition SHA-256 does not match manifest")
    if expected_schema_sha256 != expected_schema_hash:
        raise GeometryCorpusError("schema-version SHA-256 does not match geometry_program_corpus_v1")
    split_definition = SplitDefinition.from_mapping(_load_json_object(resolved_split, "split definition"))
    records = _load_records(resolved_corpus)
    intake = GeometryCorpusIntake(
        corpus_path=resolved_corpus,
        manifest_path=resolved_manifest,
        split_path=resolved_split,
        records=records,
        split_definition=split_definition,
        corpus_sha256=actual_corpus_sha256,
        splits_sha256=actual_splits_sha256,
        schema_sha256=expected_schema_hash,
        manifest_sha256=sha256_file(resolved_manifest),
    )
    intake.verify()
    intake.structural_splits()
    return intake
