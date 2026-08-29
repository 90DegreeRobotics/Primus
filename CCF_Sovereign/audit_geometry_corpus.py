"""Fail-closed audit for geometry program corpus artifacts.

This is a Lane C verifier. It consumes an already-emitted corpus, manifest, and
split definition; it does not create samples, infer objects, train, render, or
authorize promotion.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SUPPORTED_SCHEMA_VERSIONS = frozenset(
    {"geometry_program_corpus_v1", "geometry_program_corpus_v2"}
)

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

V1_MESH_METRIC_KEYS = frozenset(
    {"vert_count", "face_count", "bbox_min_mm", "bbox_max_mm"}
)
V2_MESH_METRIC_KEYS = frozenset(
    {
        "vert_count",
        "edge_count",
        "face_count",
        "tri_count",
        "loose_part_count",
        "bbox_min_mm",
        "bbox_max_mm",
        "bbox_extent_mm",
        "volume_mm3",
        "surface_area_mm2",
        "is_closed",
    }
)


class GeometryCorpusAuditError(ValueError):
    """Raised when corpus evidence violates the geometry-corpus contract."""


@dataclass(frozen=True)
class AuditedRecord:
    sample_id: str
    program: Mapping[str, Any]
    program_structure: Mapping[str, Any]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GeometryCorpusAuditError(f"{label} must be an object")
    return value


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise GeometryCorpusAuditError(f"{label} must be a non-empty string")
    return value


def _require_nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise GeometryCorpusAuditError(f"{label} must be a non-negative integer")
    return value


def _require_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GeometryCorpusAuditError(f"{label} must be numeric")
    parsed = float(value)
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        raise GeometryCorpusAuditError(f"{label} must be finite")
    return parsed


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise GeometryCorpusAuditError(f"{label} must be boolean")
    return value


def _require_vector3(value: Any, label: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise GeometryCorpusAuditError(f"{label} must be a three-item vector")
    return tuple(_require_finite_number(item, f"{label}[{index}]") for index, item in enumerate(value))


def _assert_no_forbidden_keys(value: Any, location: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise GeometryCorpusAuditError(f"{location} has a non-string key")
            if key.lower() in FORBIDDEN_KEYS:
                raise GeometryCorpusAuditError(
                    f"{location} contains forbidden key {key!r}"
                )
            _assert_no_forbidden_keys(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_forbidden_keys(child, f"{location}[{index}]")


def _load_json_object(path: Path, label: str) -> Mapping[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GeometryCorpusAuditError(f"could not read {label}: {path}") from error
    return _require_mapping(parsed, label)


def _load_jsonl_records(path: Path) -> tuple[Mapping[str, Any], ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise GeometryCorpusAuditError(f"could not read corpus JSONL: {path}") from error
    if not lines:
        raise GeometryCorpusAuditError("corpus JSONL is empty")
    records: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            raise GeometryCorpusAuditError(f"corpus JSONL has blank line {line_number}")
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as error:
            raise GeometryCorpusAuditError(
                f"corpus JSONL line {line_number} is not valid JSON"
            ) from error
        records.append(_require_mapping(parsed, f"line {line_number}"))
    return tuple(records)


def _operation_name(step: Any, label: str) -> str:
    if isinstance(step, str):
        return _require_nonempty_string(step, label)
    raw = _require_mapping(step, label)
    for key in ("operation", "op", "variant", "type", "verb"):
        value = raw.get(key)
        if isinstance(value, str) and value:
            return value
    operation_like_keys = [
        key
        for key, value in raw.items()
        if isinstance(key, str) and isinstance(value, (Mapping, list, str, int, float, bool, type(None)))
    ]
    if len(operation_like_keys) == 1:
        return _require_nonempty_string(operation_like_keys[0], f"{label} operation key")
    raise GeometryCorpusAuditError(f"{label} does not expose a derivable operation name")


def _program_steps(program: Mapping[str, Any]) -> Sequence[Any]:
    for key in ("operations", "steps"):
        value = program.get(key)
        if isinstance(value, list):
            return value
    raise GeometryCorpusAuditError("program does not expose operations or steps")


def derive_program_structure(program: Mapping[str, Any]) -> dict[str, Any]:
    steps = _program_steps(program)
    operations = [_operation_name(step, f"program step {index}") for index, step in enumerate(steps)]
    if not operations:
        raise GeometryCorpusAuditError("program has no operations")
    op_mix = dict(sorted(Counter(operations).items()))
    return {
        "step_count": len(operations),
        "op_mix": op_mix,
        "op_signature": "|".join(sorted(op_mix)),
    }


def _normalise_program_structure(value: Any, label: str) -> dict[str, Any]:
    raw = _require_mapping(value, label)
    step_count = _require_nonnegative_int(raw.get("step_count"), f"{label}.step_count")
    raw_op_mix = _require_mapping(raw.get("op_mix"), f"{label}.op_mix")
    op_mix: dict[str, int] = {}
    for operation, count in raw_op_mix.items():
        name = _require_nonempty_string(operation, f"{label}.op_mix key")
        parsed_count = _require_nonnegative_int(count, f"{label}.op_mix.{name}")
        if parsed_count == 0:
            raise GeometryCorpusAuditError(f"{label}.op_mix.{name} must be positive")
        op_mix[name] = parsed_count
    op_signature = _require_nonempty_string(raw.get("op_signature"), f"{label}.op_signature")
    return {
        "step_count": step_count,
        "op_mix": dict(sorted(op_mix.items())),
        "op_signature": op_signature,
    }


def _assert_structure_derivable(record: Mapping[str, Any], line_number: int) -> dict[str, Any]:
    program = _require_mapping(record.get("program"), f"line {line_number}.program")
    declared = _normalise_program_structure(
        record.get("program_structure"), f"line {line_number}.program_structure"
    )
    derived = derive_program_structure(program)
    if declared != derived:
        raise GeometryCorpusAuditError(
            f"line {line_number}.program_structure is not derivable from program"
        )
    return derived


def _validate_mesh_metrics(value: Any, schema_version: str, line_number: int) -> None:
    metrics = _require_mapping(value, f"line {line_number}.mesh_metrics")
    required = V2_MESH_METRIC_KEYS if schema_version == "geometry_program_corpus_v2" else V1_MESH_METRIC_KEYS
    missing = required.difference(metrics)
    if missing:
        raise GeometryCorpusAuditError(
            f"line {line_number}.mesh_metrics lacks required keys: {sorted(missing)}"
        )
    count_keys = {"vert_count", "edge_count", "face_count", "tri_count", "loose_part_count"}
    for key in sorted(count_keys.intersection(metrics)):
        _require_nonnegative_int(metrics[key], f"line {line_number}.mesh_metrics.{key}")
    for key in ("bbox_min_mm", "bbox_max_mm", "bbox_extent_mm"):
        if key in metrics:
            _require_vector3(metrics[key], f"line {line_number}.mesh_metrics.{key}")
    for key in ("volume_mm3", "surface_area_mm2"):
        if key in metrics:
            _require_finite_number(metrics[key], f"line {line_number}.mesh_metrics.{key}")
    if "is_closed" in metrics:
        _require_bool(metrics["is_closed"], f"line {line_number}.mesh_metrics.is_closed")


def _validate_render(value: Any, line_number: int) -> None:
    render = _require_mapping(value, f"line {line_number}.render")
    for key in ("path", "sha256", "width", "height"):
        if key not in render:
            raise GeometryCorpusAuditError(f"line {line_number}.render lacks {key!r}")
    _require_nonempty_string(render["path"], f"line {line_number}.render.path")
    _require_nonempty_string(render["sha256"], f"line {line_number}.render.sha256")
    _require_nonnegative_int(render["width"], f"line {line_number}.render.width")
    _require_nonnegative_int(render["height"], f"line {line_number}.render.height")


def _validate_view_score(value: Any, schema_version: str, line_number: int) -> None:
    view_score = _require_mapping(value, f"line {line_number}.view_score")
    for key in ("score", "scorer_version"):
        if key not in view_score:
            raise GeometryCorpusAuditError(f"line {line_number}.view_score lacks {key!r}")
    _require_finite_number(view_score["score"], f"line {line_number}.view_score.score")
    _require_nonempty_string(
        view_score["scorer_version"], f"line {line_number}.view_score.scorer_version"
    )
    if schema_version == "geometry_program_corpus_v1":
        for key in ("silhouette_overlap", "bbox_iou"):
            if key not in view_score:
                raise GeometryCorpusAuditError(f"line {line_number}.view_score lacks {key!r}")
            _require_finite_number(view_score[key], f"line {line_number}.view_score.{key}")


def _validate_record(record: Mapping[str, Any], line_number: int, schema_version: str) -> AuditedRecord:
    _assert_no_forbidden_keys(record, f"line {line_number}")
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
    missing = required.difference(record)
    if missing:
        raise GeometryCorpusAuditError(f"line {line_number} lacks required keys: {sorted(missing)}")
    if record["schema_version"] != schema_version:
        raise GeometryCorpusAuditError(f"line {line_number}.schema_version does not match manifest")
    program = _require_mapping(record["program"], f"line {line_number}.program")
    sample_id = _require_nonempty_string(record["sample_id"], f"line {line_number}.sample_id")
    expected_sample_id = _sha256_text(canonical_json(program))
    if sample_id != expected_sample_id:
        raise GeometryCorpusAuditError(f"line {line_number}.sample_id does not match program hash")
    if record["executed"] is not True:
        raise GeometryCorpusAuditError(f"line {line_number}.executed must be true")
    structure = _assert_structure_derivable(record, line_number)
    _validate_mesh_metrics(record["mesh_metrics"], schema_version, line_number)
    _validate_render(record["render"], line_number)
    _validate_view_score(record["view_score"], schema_version, line_number)
    return AuditedRecord(sample_id=sample_id, program=program, program_structure=structure)


def _load_split_document(split_path: Path | None, manifest: Mapping[str, Any]) -> tuple[Path, Mapping[str, Any]] | tuple[None, None]:
    if split_path is None:
        raw_path = manifest.get("splits_path") or manifest.get("split_path")
        if raw_path is None:
            if "splits_sha256" in manifest:
                raise GeometryCorpusAuditError(
                    "manifest has splits_sha256 but no split path was supplied"
                )
            return (None, None)
        split_path = Path(_require_nonempty_string(raw_path, "manifest.splits_path"))
    resolved = split_path.expanduser().resolve()
    if not resolved.is_file():
        raise GeometryCorpusAuditError(f"split definition is missing: {resolved}")
    return (resolved, _load_json_object(resolved, "split definition"))


def _split_from_definition(
    structure: Mapping[str, Any], split_definition: Mapping[str, Any]
) -> str:
    held_out_lengths = split_definition.get("held_out_length", [])
    if not isinstance(held_out_lengths, list) or not held_out_lengths:
        raise GeometryCorpusAuditError("split definition.held_out_length must be a non-empty array")
    lengths = {_require_nonnegative_int(item, "split definition.held_out_length item") for item in held_out_lengths}
    raw_combos = split_definition.get("held_out_op_combo", [])
    if not isinstance(raw_combos, list) or not raw_combos:
        raise GeometryCorpusAuditError("split definition.held_out_op_combo must be a non-empty array")
    combos: list[frozenset[str]] = []
    for index, raw_combo in enumerate(raw_combos):
        if not isinstance(raw_combo, list) or len(raw_combo) != 2:
            raise GeometryCorpusAuditError(
                f"split definition.held_out_op_combo[{index}] must be a two-operation array"
            )
        combo = frozenset(
            _require_nonempty_string(item, f"split definition.held_out_op_combo[{index}] item")
            for item in raw_combo
        )
        if len(combo) != 2:
            raise GeometryCorpusAuditError(
                f"split definition.held_out_op_combo[{index}] must contain two operations"
            )
        combos.append(combo)
    operations = frozenset(str(operation) for operation in _require_mapping(structure["op_mix"], "program_structure.op_mix"))
    if any(combo.issubset(operations) for combo in combos):
        return "held_out_op_combo"
    if structure["step_count"] in lengths:
        return "held_out_length"
    return "train"


def _audit_splits(
    records: Sequence[AuditedRecord], split_definition: Mapping[str, Any] | None
) -> dict[str, int]:
    if split_definition is None:
        return {}
    allowed_definition_keys = {"held_out_length", "held_out_op_combo"}
    if allowed_definition_keys.issubset(split_definition.keys()):
        splits: dict[str, list[AuditedRecord]] = {
            "train": [],
            "held_out_length": [],
            "held_out_op_combo": [],
        }
        for record in records:
            splits[_split_from_definition(record.program_structure, split_definition)].append(record)
        if not splits["train"]:
            raise GeometryCorpusAuditError("structural split leaves no train records")
        if not splits["held_out_length"]:
            raise GeometryCorpusAuditError("structural split leaves no held_out_length records")
        if not splits["held_out_op_combo"]:
            raise GeometryCorpusAuditError("structural split leaves no held_out_op_combo records")
        train_signatures = {
            str(record.program_structure["op_signature"]) for record in splits["train"]
        }
        combo_signatures = {
            str(record.program_structure["op_signature"]) for record in splits["held_out_op_combo"]
        }
        overlap = train_signatures.intersection(combo_signatures)
        if overlap:
            raise GeometryCorpusAuditError(
                "held_out_op_combo signatures overlap train signatures: "
                + ", ".join(sorted(overlap))
            )
        return {name: len(items) for name, items in splits.items()}
    explicit_keys = {"train", "held_out_length", "held_out_op_combo"}
    if explicit_keys.issubset(split_definition.keys()):
        all_ids = {record.sample_id for record in records}
        assigned: set[str] = set()
        split_counts: dict[str, int] = {}
        for split_name in sorted(explicit_keys):
            raw_ids = split_definition[split_name]
            if not isinstance(raw_ids, list):
                raise GeometryCorpusAuditError(f"split {split_name} must be an array")
            ids = {_require_nonempty_string(item, f"split {split_name} item") for item in raw_ids}
            if assigned.intersection(ids):
                raise GeometryCorpusAuditError("sample_id appears in more than one split")
            assigned.update(ids)
            split_counts[split_name] = len(ids)
        if assigned != all_ids:
            raise GeometryCorpusAuditError("explicit splits do not cover exactly the corpus sample_ids")
        return split_counts
    raise GeometryCorpusAuditError("split definition has no supported split contract")


def audit_geometry_corpus(
    corpus_path: str | Path,
    manifest_path: str | Path,
    split_path: str | Path | None = None,
) -> dict[str, Any]:
    resolved_corpus = Path(corpus_path).expanduser().resolve()
    resolved_manifest = Path(manifest_path).expanduser().resolve()
    if not resolved_corpus.is_file():
        raise GeometryCorpusAuditError(f"corpus JSONL is missing: {resolved_corpus}")
    if not resolved_manifest.is_file():
        raise GeometryCorpusAuditError(f"manifest is missing: {resolved_manifest}")

    manifest = _load_json_object(resolved_manifest, "manifest")
    schema_version = _require_nonempty_string(manifest.get("schema_version"), "manifest.schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise GeometryCorpusAuditError(f"unsupported schema_version {schema_version!r}")
    expected_corpus_hash = _require_nonempty_string(
        manifest.get("corpus_sha256"), "manifest.corpus_sha256"
    )
    actual_corpus_hash = sha256_file(resolved_corpus)
    if actual_corpus_hash != expected_corpus_hash:
        raise GeometryCorpusAuditError("corpus SHA-256 does not match manifest")
    expected_schema_hash = _require_nonempty_string(
        manifest.get("schema_sha256"), "manifest.schema_sha256"
    )
    if expected_schema_hash != _sha256_text(schema_version):
        raise GeometryCorpusAuditError("schema-version SHA-256 does not match schema_version")

    resolved_split, split_document = _load_split_document(
        Path(split_path) if split_path is not None else None, manifest
    )
    actual_split_hash = None
    if resolved_split is not None:
        actual_split_hash = sha256_file(resolved_split)
        expected_split_hash = _require_nonempty_string(
            manifest.get("splits_sha256"), "manifest.splits_sha256"
        )
        if actual_split_hash != expected_split_hash:
            raise GeometryCorpusAuditError("split-definition SHA-256 does not match manifest")
        _assert_no_forbidden_keys(split_document, "split definition")

    records = _load_jsonl_records(resolved_corpus)
    if "record_count" in manifest:
        expected_count = _require_nonnegative_int(manifest["record_count"], "manifest.record_count")
        if len(records) != expected_count:
            raise GeometryCorpusAuditError("manifest.record_count does not match corpus")

    audited: list[AuditedRecord] = []
    seen_sample_ids: set[str] = set()
    for line_number, record in enumerate(records, start=1):
        audited_record = _validate_record(record, line_number, schema_version)
        if audited_record.sample_id in seen_sample_ids:
            raise GeometryCorpusAuditError(f"duplicate sample_id: {audited_record.sample_id}")
        seen_sample_ids.add(audited_record.sample_id)
        audited.append(audited_record)

    split_counts = _audit_splits(audited, split_document)
    return {
        "status": "pass",
        "schema_version": schema_version,
        "record_count": len(audited),
        "corpus_sha256": actual_corpus_hash,
        "splits_sha256": actual_split_hash,
        "split_counts": split_counts,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit a geometry program corpus.")
    parser.add_argument("--corpus", required=True, help="Path to corpus JSONL")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON")
    parser.add_argument("--splits", help="Path to split-definition JSON")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    receipt = audit_geometry_corpus(args.corpus, args.manifest, args.splits)
    print(canonical_json(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
