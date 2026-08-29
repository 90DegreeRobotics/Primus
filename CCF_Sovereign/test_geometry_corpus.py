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
sys.path.insert(0, str(ROOT))

from geometry_corpus import (  # noqa: E402
    DECLARED_PHASE_ZERO_BASELINES,
    FORBIDDEN_KEYS,
    TARGET_METRICS,
    GeometryCorpusError,
    build_structural_splits,
    canonical_json,
    evaluate_declared_baselines,
    load_geometry_corpus_intake,
    split_for_structure,
)
from train_geometry_phase0 import (  # noqa: E402
    CANDIDATE_CHECKPOINT_NAME,
    CANDIDATE_MANIFEST_NAME,
    CANDIDATE_OUTPUT_DIRECTORY,
    GeometryPhase0SafetyError,
    TrainingConfig,
    build_training_tensors,
    feature_schema,
    run_fixture_training,
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
    operation_steps: list[dict[str, object]],
    vert_count: int,
    face_count: int,
    is_closed: bool,
    view_score: float,
) -> dict[str, object]:
    program = {
        "base": "cube",
        "object_id": f"fixture_body_{ordinal}",
        "plan_version": "0.1",
        "steps": operation_steps,
        "unit": "millimeter",
    }
    operation_names = [str(step["op"]) for step in operation_steps]
    op_mix = {operation: operation_names.count(operation) for operation in sorted(set(operation_names))}
    sample_id = hashlib.sha256(canonical_json(program).encode("utf-8")).hexdigest()
    extent = [float(ordinal * 11 + 1), float(ordinal * 11 + 2), float(ordinal * 11 + 3)]
    return {
        "schema_version": "geometry_program_corpus_v2",
        "sample_id": sample_id,
        "program": program,
        "program_structure": {
            "step_count": len(operation_steps),
            "op_mix": op_mix,
            "op_signature": "|".join(sorted(op_mix)),
        },
        "executed": True,
        "mesh_metrics": {
            "vert_count": vert_count,
            "edge_count": vert_count * 2,
            "face_count": face_count,
            "tri_count": face_count * 2,
            "loose_part_count": 1,
            "bbox_min_mm": [-extent[0] / 2, -extent[1] / 2, -extent[2] / 2],
            "bbox_max_mm": [extent[0] / 2, extent[1] / 2, extent[2] / 2],
            "bbox_extent_mm": extent,
            "surface_area_mm2": float(ordinal * 1_000 + 50),
            "volume_mm3": float(ordinal * 10_000 + 500),
            "is_closed": is_closed,
        },
        "render": {
            "path": f"fixture-render-{ordinal}.png",
            "sha256": hashlib.sha256(f"fixture-render-{ordinal}".encode("utf-8")).hexdigest(),
            "width": 1280,
            "height": 960,
        },
        "view_score": {
            "score": view_score,
            "scorer_version": "silhouette_v0.1",
            "note": "metadata only; never a target or filter",
        },
    }


class GeometryCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_geometry_corpus_fixture(
        self, *, records: list[dict[str, object]] | None = None, view_score_delta: float = 0.0
    ) -> tuple[Path, Path, Path]:
        corpus = self.root / f"geometry_corpus_fixture_records_{view_score_delta}.jsonl"
        split_definition = self.root / f"geometry_corpus_fixture_splits_{view_score_delta}.json"
        manifest = self.root / f"geometry_corpus_fixture_manifest_{view_score_delta}.json"
        self.assertTrue(all("_fixture_" in path.name for path in (corpus, split_definition, manifest)))
        if records is None:
            records = [
                fixture_record(
                    1,
                    operation_steps=[{"op": "create_cube", "size": 50.0}],
                    vert_count=8,
                    face_count=6,
                    is_closed=True,
                    view_score=0.1 + view_score_delta,
                ),
                fixture_record(
                    2,
                    operation_steps=[
                        {"op": "create_cube", "size": 80.0},
                        {"op": "bevel_edges", "width": 4.0, "segments": 2},
                    ],
                    vert_count=32,
                    face_count=30,
                    is_closed=True,
                    view_score=0.2 + view_score_delta,
                ),
                fixture_record(
                    3,
                    operation_steps=[
                        {"op": "create_cube", "size": 90.0},
                        {"op": "pull_face", "distance": 25.0},
                        {"op": "taper_region", "end_scale": 0.7},
                    ],
                    vert_count=46,
                    face_count=38,
                    is_closed=True,
                    view_score=0.3 + view_score_delta,
                ),
                fixture_record(
                    4,
                    operation_steps=[
                        {"op": "create_cube", "size": 100.0},
                        {"op": "pull_face", "distance": 35.0},
                        {"op": "bevel_edges", "width": 6.0, "segments": 3},
                    ],
                    vert_count=61,
                    face_count=49,
                    is_closed=False,
                    view_score=0.4 + view_score_delta,
                ),
                fixture_record(
                    5,
                    operation_steps=[
                        {"op": "create_cube", "size": 70.0},
                        {"op": "union_shape", "size": [20.0, 20.0, 20.0]},
                    ],
                    vert_count=29,
                    face_count=24,
                    is_closed=True,
                    view_score=0.5 + view_score_delta,
                ),
                fixture_record(
                    6,
                    operation_steps=[
                        {"op": "create_cube", "size": 120.0},
                        {"op": "extrude_region", "distance": 45.0},
                        {"op": "subdivide_face", "rows": 2, "columns": 2},
                        {"op": "taper_region", "end_scale": 0.5},
                    ],
                    vert_count=94,
                    face_count=80,
                    is_closed=False,
                    view_score=0.6 + view_score_delta,
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
                    "held_out_op_combo": [["bevel_edges", "pull_face"]],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        manifest.write_text(
            canonical_json(
                {
                    "schema_version": "geometry_program_corpus_v2",
                    "corpus_sha256": sha256_file(corpus),
                    "splits_sha256": sha256_file(split_definition),
                    "schema_sha256": hashlib.sha256(
                        b"geometry_program_corpus_v2"
                    ).hexdigest(),
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return corpus, manifest, split_definition

    def load_fixture(self, *, view_score_delta: float = 0.0):
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture(
            view_score_delta=view_score_delta
        )
        self.assertIn("_fixture_", corpus.name)
        return load_geometry_corpus_intake(corpus, manifest, split_definition)

    def test_v2_fixture_intake_is_hash_pinned_and_noun_free(self) -> None:
        intake = self.load_fixture()
        self.assertEqual(len(intake.records), 6)
        self.assertEqual(intake.split_definition.held_out_length, frozenset({4}))
        self.assertEqual(len(intake.split_definition.held_out_op_combo), 1)
        self.assertTrue(FORBIDDEN_KEYS.isdisjoint({"steps", "op", "object_id"}))
        self.assertIn("volume_mm3", intake.records[0].mesh_metrics)
        self.assertEqual(intake.records[0].program_structure.op_signature, "create_cube")

    def test_rejects_nested_forbidden_key_even_with_matching_hashes(self) -> None:
        records = [
            fixture_record(
                1,
                operation_steps=[{"op": "create_cube", "size": 50.0}],
                vert_count=8,
                face_count=6,
                is_closed=True,
                view_score=0.1,
            ),
            fixture_record(
                2,
                operation_steps=[
                    {"op": "create_cube", "size": 80.0},
                    {"op": "bevel_edges", "width": 4.0, "segments": 2},
                ],
                vert_count=32,
                face_count=30,
                is_closed=True,
                view_score=0.2,
            ),
            fixture_record(
                3,
                operation_steps=[
                    {"op": "create_cube", "size": 90.0},
                    {"op": "pull_face", "distance": 25.0},
                    {"op": "taper_region", "end_scale": 0.7},
                ],
                vert_count=46,
                face_count=38,
                is_closed=True,
                view_score=0.3,
            ),
            fixture_record(
                4,
                operation_steps=[
                    {"op": "create_cube", "size": 100.0},
                    {"op": "pull_face", "distance": 35.0},
                    {"op": "bevel_edges", "width": 6.0, "segments": 3},
                ],
                vert_count=61,
                face_count=49,
                is_closed=False,
                view_score=0.4,
            ),
            fixture_record(
                5,
                operation_steps=[
                    {"op": "create_cube", "size": 70.0},
                    {"op": "union_shape", "size": [20.0, 20.0, 20.0]},
                ],
                vert_count=29,
                face_count=24,
                is_closed=True,
                view_score=0.5,
            ),
            fixture_record(
                6,
                operation_steps=[
                    {"op": "create_cube", "size": 120.0},
                    {"op": "extrude_region", "distance": 45.0},
                    {"op": "subdivide_face", "rows": 2, "columns": 2},
                    {"op": "taper_region", "end_scale": 0.5},
                ],
                vert_count=94,
                face_count=80,
                is_closed=False,
                view_score=0.6,
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

    def test_rejects_tampered_corpus_splits_schema_and_derived_structure(self) -> None:
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        corpus.write_text(corpus.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(GeometryCorpusError, "corpus SHA-256"):
            load_geometry_corpus_intake(corpus, manifest, split_definition)
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        split_definition.write_text(
            canonical_json({"held_out_length": [99], "held_out_op_combo": [["create_cube", "pull_face"]]})
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
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        records = [json.loads(line) for line in corpus.read_text(encoding="utf-8").splitlines()]
        records[0]["program"]["steps"].append({"op": "pull_face", "distance": 1.0})
        records[0]["sample_id"] = hashlib.sha256(
            canonical_json(records[0]["program"]).encode("utf-8")
        ).hexdigest()
        corpus.write_text("".join(canonical_json(record) + "\n" for record in records), encoding="utf-8")
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        manifest_payload["corpus_sha256"] = sha256_file(corpus)
        manifest.write_text(canonical_json(manifest_payload) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(GeometryCorpusError, "not derivable"):
            load_geometry_corpus_intake(corpus, manifest, split_definition)

    def test_structural_splits_are_disjoint_and_program_payload_independent(self) -> None:
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
            {name: tuple(record.sample_id for record in records) for name, records in splits.items()},
            {
                name: tuple(record.sample_id for record in records)
                for name, records in build_structural_splits(
                    modified_program_records, intake.split_definition
                ).items()
            },
        )

    def test_declared_baselines_cover_the_complete_v2_target_vector(self) -> None:
        intake = self.load_fixture()
        reports = evaluate_declared_baselines(intake)
        self.assertEqual(len(reports), len(DECLARED_PHASE_ZERO_BASELINES) * len(TARGET_METRICS))
        self.assertEqual({report.baseline for report in reports}, set(DECLARED_PHASE_ZERO_BASELINES))
        self.assertEqual({report.target_metric for report in reports}, set(TARGET_METRICS))
        for report in reports:
            self.assertEqual(
                {metric.split for metric in report.split_metrics},
                {"held_out_length", "held_out_op_combo"},
            )
            self.assertTrue(all(metric.count > 0 for metric in report.split_metrics))

    def test_view_score_cannot_change_training_features_targets_or_fixture_run(self) -> None:
        intake = self.load_fixture(view_score_delta=0.0)
        changed_intake = self.load_fixture(view_score_delta=1000.0)
        train_records = intake.structural_splits()["train"]
        changed_train_records = changed_intake.structural_splits()["train"]
        schema = feature_schema(train_records)
        self.assertEqual(schema, feature_schema(changed_train_records))
        features, targets = build_training_tensors(train_records, schema=schema)
        changed_features, changed_targets = build_training_tensors(changed_train_records, schema=schema)
        self.assertTrue(features.equal(changed_features))
        self.assertTrue(targets.equal(changed_targets))
        output_root = self.root / "fixture_outputs"
        config = TrainingConfig(seed=31, epochs=5, learning_rate=0.02, hidden_width=12)
        result = run_fixture_training(
            corpus_path=intake.corpus_path,
            manifest_path=intake.manifest_path,
            split_path=intake.split_path,
            output_root=output_root,
            candidate_id="fixture-run-one",
            config=config,
        )
        changed_result = run_fixture_training(
            corpus_path=changed_intake.corpus_path,
            manifest_path=changed_intake.manifest_path,
            split_path=changed_intake.split_path,
            output_root=output_root,
            candidate_id="fixture-run-two",
            config=config,
        )
        self.assertEqual(result["model_metrics"], changed_result["model_metrics"])
        self.assertEqual(result["declared_baselines"], changed_result["declared_baselines"])
        self.assertEqual(result["baseline_comparison"], changed_result["baseline_comparison"])

    def test_fixture_training_creates_an_isolated_nonpromotable_candidate(self) -> None:
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        output_root = self.root / "candidate_outputs"
        result = run_fixture_training(
            corpus_path=corpus,
            manifest_path=manifest,
            split_path=split_definition,
            output_root=output_root,
            candidate_id="fixture-phase0",
            config=TrainingConfig(seed=7, epochs=5, learning_rate=0.02, hidden_width=12),
        )
        candidate_dir = output_root / CANDIDATE_OUTPUT_DIRECTORY / "fixture-phase0"
        self.assertEqual(result["state"], "evaluated")
        self.assertTrue(result["fixture_only"])
        self.assertFalse(result["promotion"]["permitted"])
        self.assertTrue((candidate_dir / CANDIDATE_MANIFEST_NAME).is_file())
        self.assertTrue((candidate_dir / CANDIDATE_CHECKPOINT_NAME).is_file())
        self.assertEqual(len(result["model_metrics"]), len(TARGET_METRICS) * 2)
        self.assertEqual(len(result["declared_baselines"]), len(TARGET_METRICS) * 3)
        with self.assertRaisesRegex(GeometryPhase0SafetyError, "already exists"):
            run_fixture_training(
                corpus_path=corpus,
                manifest_path=manifest,
                split_path=split_definition,
                output_root=output_root,
                candidate_id="fixture-phase0",
                config=TrainingConfig(epochs=1),
            )

    def test_training_refuses_nonfixture_inputs_before_candidate_creation(self) -> None:
        corpus, manifest, split_definition = self.write_geometry_corpus_fixture()
        regular_corpus = self.root / "corpus.jsonl"
        regular_manifest = self.root / "manifest.json"
        regular_splits = self.root / "splits.json"
        regular_corpus.write_bytes(corpus.read_bytes())
        regular_manifest.write_bytes(manifest.read_bytes())
        regular_splits.write_bytes(split_definition.read_bytes())
        with self.assertRaisesRegex(GeometryPhase0SafetyError, "_fixture_"):
            run_fixture_training(
                corpus_path=regular_corpus,
                manifest_path=regular_manifest,
                split_path=regular_splits,
                output_root=self.root / "candidate_outputs",
                candidate_id="real-input-refusal",
                config=TrainingConfig(epochs=1),
            )


if __name__ == "__main__":
    unittest.main()
