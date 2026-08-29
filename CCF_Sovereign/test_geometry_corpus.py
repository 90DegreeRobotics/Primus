from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from geometry_corpus import (  # noqa: E402
    DECLARED_PHASE_ZERO_BASELINES,
    FORBIDDEN_KEYS,
    GeometryCorpusError,
    build_structural_splits,
    canonical_json,
    evaluate_declared_baselines,
    load_geometry_corpus_intake,
    split_for_structure,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fixture_record(
    ordinal: int,
    *,
    operations: list[str],
    step_count: int,
    vert_count: int,
    face_count: int,
) -> dict[str, object]:
    program = {
        "operations": [
            {"operation": operation, "ordinal": position}
            for position, operation in enumerate(operations)
        ],
        "program_ordinal": ordinal,
    }
    return {
        "schema_version": "geometry_program_corpus_v1",
        "sample_id": hashlib.sha256(canonical_json(program).encode("utf-8")).hexdigest(),
        "program": program,
        "program_structure": {
            "step_count": step_count,
            "op_mix": {
                operation: operations.count(operation)
                for operation in sorted(set(operations))
            },
            "op_signature": "|".join(sorted(set(operations))),
        },
        "executed": True,
        "mesh_metrics": {
            "vert_count": vert_count,
            "face_count": face_count,
            "bbox_min_mm": [-0.5, -0.5, -0.5],
            "bbox_max_mm": [1.0, 1.0, 1.0],
        },
        "render": {
            "path": f"fixture-render-{ordinal}.png",
            "sha256": hashlib.sha256(f"fixture-render-{ordinal}".encode("utf-8")).hexdigest(),
            "width": 960,
            "height": 540,
        },
        "view_score": {
            "score": 0.4 + ordinal / 100,
            "silhouette_overlap": 0.45 + ordinal / 100,
            "bbox_iou": 0.35 + ordinal / 100,
            "scorer_version": "silhouette_v0.1",
        },
    }


class GeometryCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_geometry_corpus_fixture(
        self, *, records: list[dict[str, object]] | None = None
    ) -> tuple[Path, Path, Path]:
        corpus = self.root / "geometry_corpus_fixture_records.jsonl"
        split_definition = self.root / "geometry_corpus_fixture_splits.json"
        manifest = self.root / "geometry_corpus_fixture_manifest.json"
        self.assertIn("_fixture_", corpus.name)
        self.assertIn("_fixture_", split_definition.name)
        self.assertIn("_fixture_", manifest.name)
        if records is None:
            records = [
                fixture_record(1, operations=["CreateCube"], step_count=1, vert_count=10, face_count=6),
                fixture_record(
                    2,
                    operations=["CreateCube", "BevelEdges"],
                    step_count=2,
                    vert_count=14,
                    face_count=10,
                ),
                fixture_record(
                    3,
                    operations=["CreateCube", "PullFace", "TaperRegion"],
                    step_count=3,
                    vert_count=20,
                    face_count=14,
                ),
                fixture_record(
                    4,
                    operations=["CreateCube", "PullFace", "TaperRegion", "ShellSolid"],
                    step_count=4,
                    vert_count=26,
                    face_count=18,
                ),
                fixture_record(
                    5,
                    operations=["CreateCube", "PullFace", "BevelEdges"],
                    step_count=3,
                    vert_count=30,
                    face_count=22,
                ),
            ]
        corpus.write_text(
            "".join(canonical_json(record) + "\n" for record in records),
            encoding="utf-8",
        )
        split_definition.write_text(
            canonical_json(
                {
                    "held_out_length": [4],
                    "held_out_op_combo": [["BevelEdges", "PullFace"]],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        manifest.write_text(
            canonical_json(
                {
                    "schema_version": "geometry_program_corpus_v1",
                    "corpus_sha256": sha256_file(corpus),
                    "splits_sha256": sha256_file(split_definition),
                    "schema_sha256": hashlib.sha256(
                        b"geometry_program_corpus_v1"
                    ).hexdigest(),
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return corpus, manifest, split_definition

    def load_fixture(self):
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        self.assertIn("_fixture_", corpus.name)
        return load_geometry_corpus_intake(corpus, manifest, split_definition)

    def test_fixture_intake_is_hash_pinned_and_noun_free(self) -> None:
        intake = self.load_fixture()
        self.assertEqual(len(intake.records), 5)
        self.assertEqual(intake.split_definition.held_out_length, frozenset({4}))
        self.assertEqual(len(intake.split_definition.held_out_op_combo), 1)
        self.assertTrue(FORBIDDEN_KEYS.isdisjoint({"operations", "program_ordinal"}))

    def test_rejects_nested_forbidden_key_even_with_matching_hashes(self) -> None:
        records = [
            fixture_record(1, operations=["CreateCube"], step_count=1, vert_count=10, face_count=6),
            fixture_record(
                2,
                operations=["CreateCube", "BevelEdges"],
                step_count=2,
                vert_count=14,
                face_count=10,
            ),
            fixture_record(
                3,
                operations=["CreateCube", "PullFace", "TaperRegion"],
                step_count=3,
                vert_count=20,
                face_count=14,
            ),
            fixture_record(
                4,
                operations=["CreateCube", "PullFace", "TaperRegion", "ShellSolid"],
                step_count=4,
                vert_count=26,
                face_count=18,
            ),
            fixture_record(
                5,
                operations=["CreateCube", "PullFace", "BevelEdges"],
                step_count=3,
                vert_count=30,
                face_count=22,
            ),
        ]
        nested_program = dict(records[0]["program"])
        nested_program["nested"] = {"label": "rejected-by-fixture"}
        records[0]["program"] = nested_program
        records[0]["sample_id"] = hashlib.sha256(
            canonical_json(nested_program).encode("utf-8")
        ).hexdigest()
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture(records=records)
        self.assertIn("_fixture_", corpus.name)
        with self.assertRaisesRegex(GeometryCorpusError, "forbidden key"):
            load_geometry_corpus_intake(corpus, manifest, split_definition)

    def test_rejects_tampered_corpus_at_load_and_reverification(self) -> None:
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        self.assertIn("_fixture_", corpus.name)
        corpus.write_text(corpus.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(GeometryCorpusError, "corpus SHA-256"):
            load_geometry_corpus_intake(corpus, manifest, split_definition)
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        intake = load_geometry_corpus_intake(corpus, manifest, split_definition)
        corpus.write_text(corpus.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaisesRegex(GeometryCorpusError, "corpus SHA-256 changed after intake"):
            evaluate_declared_baselines(intake)

    def test_rejects_tampered_splits_and_schema_hash(self) -> None:
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        self.assertIn("_fixture_", split_definition.name)
        split_definition.write_text(
            canonical_json({"held_out_length": [99], "held_out_op_combo": [["CreateCube", "PullFace"]]})
            + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(GeometryCorpusError, "split-definition SHA-256"):
            load_geometry_corpus_intake(corpus, manifest, split_definition)
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        manifest_payload["schema_sha256"] = "0" * 64
        manifest.write_text(canonical_json(manifest_payload) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(GeometryCorpusError, "schema-version SHA-256"):
            load_geometry_corpus_intake(corpus, manifest, split_definition)

    def test_structural_splits_are_disjoint_and_signature_safe(self) -> None:
        intake = self.load_fixture()
        splits = intake.structural_splits()
        split_ids = [set(record.sample_id for record in records) for records in splits.values()]
        self.assertEqual(sum(len(ids) for ids in split_ids), len(set().union(*split_ids)))
        train_signatures = {record.program_structure.op_signature for record in splits["train"]}
        held_out_combo_signatures = {
            record.program_structure.op_signature for record in splits["held_out_op_combo"]
        }
        self.assertTrue(train_signatures.isdisjoint(held_out_combo_signatures))
        for split_name, records in splits.items():
            for record in records:
                self.assertEqual(
                    split_for_structure(record.program_structure, intake.split_definition), split_name
                )
        modified_program_records = tuple(
            replace(record, program={"opaque_program_payload": record.sample_id})
            for record in intake.records
        )
        self.assertEqual(
            {
                name: tuple(record.sample_id for record in records)
                for name, records in splits.items()
            },
            {
                name: tuple(record.sample_id for record in records)
                for name, records in build_structural_splits(
                    modified_program_records, intake.split_definition
                ).items()
            },
        )

    def test_declared_baselines_emit_split_separated_metrics(self) -> None:
        intake = self.load_fixture()
        reports = evaluate_declared_baselines(intake)
        self.assertEqual(len(reports), len(DECLARED_PHASE_ZERO_BASELINES) * 2)
        self.assertEqual({report.baseline for report in reports}, set(DECLARED_PHASE_ZERO_BASELINES))
        self.assertEqual({report.target_metric for report in reports}, {"vert_count", "face_count"})
        for report in reports:
            self.assertEqual(
                {metric.split for metric in report.split_metrics},
                {"held_out_length", "held_out_op_combo"},
            )
            self.assertTrue(all(metric.count > 0 for metric in report.split_metrics))
        step_count_report = next(
            report
            for report in reports
            if report.baseline == "step_count_only" and report.target_metric == "vert_count"
        )
        combo_metric = next(
            metric
            for metric in step_count_report.split_metrics
            if metric.split == "held_out_op_combo"
        )
        self.assertEqual(combo_metric.mean_absolute_error, 10.0)


if __name__ == "__main__":
    unittest.main()
