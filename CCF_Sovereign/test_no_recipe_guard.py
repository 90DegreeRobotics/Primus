"""Lane C anti-recipe guard for future geometry-corpus intake.

The geometry corpus contract has no place for nouns. This test keeps that true
for the Primus intake path without scanning unrelated historical CCF surfaces.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest


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
    def test_forbidden_key_detector_rejects_nested_record(self) -> None:
        bad = {
            "schema_version": "geometry_program_corpus_v1",
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
            "geometry_program_corpus_v1 records must not carry noun/class fields",
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


if __name__ == "__main__":
    unittest.main()
