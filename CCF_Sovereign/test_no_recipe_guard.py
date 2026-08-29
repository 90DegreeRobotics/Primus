"""Lane C anti-recipe guard for future geometry-corpus intake.

The geometry corpus contract has no place for nouns. This test keeps that true
for the Primus intake path without scanning unrelated historical CCF surfaces.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from audit_geometry_corpus import GeometryCorpusAuditError, audit_geometry_corpus

ROOT = Path(__file__).resolve().parent
GEOMETRY_CORPUS_ROOT = ROOT / "src" / "geometry_corpus"
GEOMETRY_TMP_ROOT = ROOT / "tmp"

FORBIDDEN_CORPUS_KEYS = {
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

COMMON_OBJECT_NOUNS = {
    "amphora",
    "barn",
    "bicycle",
    "bottle",
    "bowl",
    "bridge",
    "building",
    "cabin",
    "castle",
    "chair",
    "church",
    "cottage",
    "cup",
    "dagger",
    "dish",
    "goblet",
    "house",
    "hut",
    "jar",
    "lighthouse",
    "mug",
    "pagoda",
    "pot",
    "saber",
    "shed",
    "spire",
    "sword",
    "temple",
    "tower",
    "urn",
    "vase",
    "vehicle",
    "windmill",
}


def _jsonish_files() -> list[Path]:
    roots = [GEOMETRY_CORPUS_ROOT]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(root.rglob("*.json"))
            files.extend(root.rglob("*.jsonl"))
    if GEOMETRY_TMP_ROOT.exists():
        files.extend(GEOMETRY_TMP_ROOT.rglob("*geometry_corpus*.json"))
        files.extend(GEOMETRY_TMP_ROOT.rglob("*geometry_corpus*.jsonl"))
        files.extend(GEOMETRY_TMP_ROOT.rglob("*fixture*.json"))
        files.extend(GEOMETRY_TMP_ROOT.rglob("*fixture*.jsonl"))
    files.extend(ROOT.glob("*geometry_corpus*.json"))
    files.extend(ROOT.glob("*geometry_corpus*.jsonl"))
    files.extend(ROOT.glob("*fixture*.json"))
    files.extend(ROOT.glob("*fixture*.jsonl"))
    return sorted(files)


def _source_files() -> list[Path]:
    if not GEOMETRY_CORPUS_ROOT.exists():
        return []
    return sorted(GEOMETRY_CORPUS_ROOT.rglob("*.py"))


def _records(path: Path) -> list[object]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return [json.loads(text)]


def _forbidden_key_paths(value: object, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            if key in FORBIDDEN_CORPUS_KEYS:
                paths.append(child_path)
            paths.extend(_forbidden_key_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_forbidden_key_paths(child, f"{prefix}[{index}]"))
    return paths


def _string_set(node: ast.AST) -> set[str]:
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return set()
    out: set[str] = set()
    for item in node.elts:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            out.add(item.value.lower())
        elif isinstance(item, (ast.List, ast.Tuple)) and item.elts:
            first = item.elts[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                out.add(first.value.lower())
    return out


class NoRecipeGuardTests(unittest.TestCase):
    def _write_v2_fixture(
        self,
        root: Path,
        *,
        mutate_second_record: object | None = None,
    ) -> tuple[Path, Path, Path]:
        corpus = root / "geometry_program_corpus_v2_fixture_records.jsonl"
        split_definition = root / "geometry_program_corpus_v2_fixture_splits.json"
        manifest = root / "geometry_program_corpus_v2_fixture_manifest.json"

        def canonical(value: object) -> str:
            return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

        def digest_file(path: Path) -> str:
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(block)
            return digest.hexdigest()

        def record(ordinal: int, operations: list[str]) -> dict[str, object]:
            program = {
                "operations": [
                    {"operation": operation, "ordinal": index}
                    for index, operation in enumerate(operations)
                ],
                "program_ordinal": ordinal,
            }
            op_mix = {operation: operations.count(operation) for operation in sorted(set(operations))}
            return {
                "schema_version": "geometry_program_corpus_v2",
                "sample_id": hashlib.sha256(canonical(program).encode("utf-8")).hexdigest(),
                "program": program,
                "program_structure": {
                    "step_count": len(operations),
                    "op_mix": op_mix,
                    "op_signature": "|".join(sorted(op_mix)),
                },
                "executed": True,
                "mesh_metrics": {
                    "vert_count": 8 + ordinal,
                    "edge_count": 12 + ordinal,
                    "face_count": 6 + ordinal,
                    "tri_count": 12 + ordinal,
                    "loose_part_count": 1,
                    "bbox_min_mm": [-0.5, -0.5, -0.5],
                    "bbox_max_mm": [1.0 + ordinal, 1.0, 1.0],
                    "bbox_extent_mm": [1.5 + ordinal, 1.5, 1.5],
                    "volume_mm3": 2.0 + ordinal,
                    "surface_area_mm2": 6.0 + ordinal,
                    "is_closed": True,
                },
                "render": {
                    "path": f"fixture-render-{ordinal}.png",
                    "sha256": hashlib.sha256(f"fixture-render-{ordinal}".encode("utf-8")).hexdigest(),
                    "width": 960,
                    "height": 540,
                },
                "view_score": {
                    "score": 0.1 * ordinal,
                    "scorer_version": "silhouette_v0.1",
                    "note": "metadata only",
                },
            }

        records = [
            record(1, ["CreateCube"]),
            record(2, ["CreateCube", "BevelEdges"]),
            record(3, ["CreateCube", "PullFace", "TaperRegion"]),
            record(4, ["CreateCube", "PullFace", "TaperRegion", "ShellSolid"]),
            record(5, ["CreateCube", "PullFace", "BevelEdges"]),
        ]
        if mutate_second_record is not None:
            records[1] = mutate_second_record  # type: ignore[assignment]
        corpus.write_text("".join(canonical(item) + "\n" for item in records), encoding="utf-8")
        split_definition.write_text(
            canonical(
                {
                    "held_out_length": [4],
                    "held_out_op_combo": [["BevelEdges", "PullFace"]],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        manifest.write_text(
            canonical(
                {
                    "schema_version": "geometry_program_corpus_v2",
                    "corpus_sha256": digest_file(corpus),
                    "splits_sha256": digest_file(split_definition),
                    "schema_sha256": hashlib.sha256(
                        b"geometry_program_corpus_v2"
                    ).hexdigest(),
                    "record_count": len(records),
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return corpus, manifest, split_definition

    def test_forbidden_key_detector_rejects_nested_record(self) -> None:
        bad = {
            "schema_version": "geometry_program_corpus_v2",
            "sample_id": "example",
            "program": {"steps": []},
            "nested": [{"prompt": "a pagoda"}],
        }

        self.assertEqual(_forbidden_key_paths(bad), ["nested[0].prompt"])

    def test_geometry_corpus_records_have_no_forbidden_keys(self) -> None:
        failures: list[str] = []
        for path in _jsonish_files():
            for index, record in enumerate(_records(path), start=1):
                for key_path in _forbidden_key_paths(record):
                    failures.append(f"{path.relative_to(ROOT)}:{index}:{key_path}")

        self.assertEqual(
            failures,
            [],
            "geometry_program_corpus_v1/v2 records must not carry noun/class fields",
        )

    def test_geometry_corpus_source_has_no_object_noun_dictionary(self) -> None:
        failures: list[str] = []
        for path in _source_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                strings = _string_set(node)
                noun_hits = sorted(strings & COMMON_OBJECT_NOUNS)
                if len(noun_hits) >= 3:
                    failures.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}: {', '.join(noun_hits)}"
                    )

        self.assertEqual(
            failures,
            [],
            "geometry corpus intake must split by program structure, not object nouns",
        )

    def test_audit_geometry_corpus_accepts_v2_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus, manifest, split_definition = self._write_v2_fixture(Path(temporary))
            receipt = audit_geometry_corpus(corpus, manifest, split_definition)

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["schema_version"], "geometry_program_corpus_v2")
        self.assertEqual(receipt["record_count"], 5)
        self.assertEqual(
            set(receipt["split_counts"]),
            {"train", "held_out_length", "held_out_op_combo"},
        )

    def test_audit_geometry_corpus_rejects_hand_written_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            corpus, _, _ = self._write_v2_fixture(root)
            records = [json.loads(line) for line in corpus.read_text(encoding="utf-8").splitlines()]
            records[1]["program_structure"] = {
                "step_count": 99,
                "op_mix": {"CreateCube": 1, "BevelEdges": 1},
                "op_signature": "BevelEdges|CreateCube",
            }
            corpus, manifest, split_definition = self._write_v2_fixture(
                root,
                mutate_second_record=records[1],
            )
            with self.assertRaisesRegex(GeometryCorpusAuditError, "program_structure"):
                audit_geometry_corpus(corpus, manifest, split_definition)


if __name__ == "__main__":
    unittest.main()
