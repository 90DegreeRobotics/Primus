from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from geometry_corpus import canonical_json, load_geometry_corpus_intake  # noqa: E402
from test_geometry_corpus import fixture_record, sha256_file  # noqa: E402
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


class GeometryPhase0TrainerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_phase0_fixture(self, *, score_delta: float = 0.0) -> tuple[Path, Path, Path]:
        corpus = self.root / f"phase0_fixture_records_{score_delta}.jsonl"
        manifest = self.root / f"phase0_fixture_manifest_{score_delta}.json"
        splits = self.root / f"phase0_fixture_splits_{score_delta}.json"
        records = [
            fixture_record(
                1,
                operation_steps=[{"op": "create_cube", "size": 50.0}],
                vert_count=8,
                face_count=6,
                is_closed=True,
                view_score=0.1 + score_delta,
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
                view_score=0.2 + score_delta,
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
                view_score=0.3 + score_delta,
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
                view_score=0.4 + score_delta,
            ),
            fixture_record(
                5,
                operation_steps=[
                    {"op": "create_cube", "size": 120.0},
                    {"op": "extrude_region", "distance": 45.0},
                    {"op": "subdivide_face", "rows": 2, "columns": 2},
                    {"op": "taper_region", "end_scale": 0.5},
                ],
                vert_count=94,
                face_count=80,
                is_closed=False,
                view_score=0.5 + score_delta,
            ),
        ]
        corpus.write_text("".join(canonical_json(record) + "\n" for record in records), encoding="utf-8")
        splits.write_text(
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
                    "splits_sha256": sha256_file(splits),
                    "schema_sha256": hashlib.sha256(b"geometry_program_corpus_v2").hexdigest(),
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.assertTrue(all("_fixture_" in path.name for path in (corpus, manifest, splits)))
        return corpus, manifest, splits

    def test_fixture_candidate_is_isolated_hash_pinned_and_nonpromotable(self) -> None:
        corpus, manifest, splits = self.write_phase0_fixture()
        output_root = self.root / "candidate_output"
        result = run_fixture_training(
            corpus_path=corpus,
            manifest_path=manifest,
            split_path=splits,
            output_root=output_root,
            candidate_id="fixture-phase0",
            config=TrainingConfig(seed=7, epochs=5, learning_rate=0.02, hidden_width=12),
        )
        candidate_directory = output_root / CANDIDATE_OUTPUT_DIRECTORY / "fixture-phase0"
        self.assertEqual(result["state"], "evaluated")
        self.assertTrue(result["fixture_only"])
        self.assertFalse(result["promotion"]["permitted"])
        self.assertEqual(result["promotion"]["state"], "rejected_by_default")
        self.assertTrue((candidate_directory / CANDIDATE_MANIFEST_NAME).is_file())
        self.assertTrue((candidate_directory / CANDIDATE_CHECKPOINT_NAME).is_file())
        self.assertEqual(result["frozen_inputs"]["corpus"]["sha256"], sha256_file(corpus))
        with self.assertRaisesRegex(GeometryPhase0SafetyError, "already exists"):
            run_fixture_training(
                corpus_path=corpus,
                manifest_path=manifest,
                split_path=splits,
                output_root=output_root,
                candidate_id="fixture-phase0",
                config=TrainingConfig(epochs=1),
            )

    def test_view_score_is_neither_a_target_nor_an_eligibility_filter(self) -> None:
        paths_a = self.write_phase0_fixture(score_delta=0.0)
        paths_b = self.write_phase0_fixture(score_delta=1000.0)
        intake_a = load_geometry_corpus_intake(*paths_a)
        intake_b = load_geometry_corpus_intake(*paths_b)
        train_a = intake_a.structural_splits()["train"]
        train_b = intake_b.structural_splits()["train"]
        schema = feature_schema(train_a)
        self.assertEqual(schema, feature_schema(train_b))
        features_a, targets_a = build_training_tensors(train_a, schema=schema)
        features_b, targets_b = build_training_tensors(train_b, schema=schema)
        self.assertTrue(features_a.equal(features_b))
        self.assertTrue(targets_a.equal(targets_b))
        config = TrainingConfig(seed=11, epochs=5, learning_rate=0.02, hidden_width=12)
        output_root = self.root / "candidate_output"
        result_a = run_fixture_training(
            corpus_path=paths_a[0],
            manifest_path=paths_a[1],
            split_path=paths_a[2],
            output_root=output_root,
            candidate_id="view-score-a",
            config=config,
        )
        result_b = run_fixture_training(
            corpus_path=paths_b[0],
            manifest_path=paths_b[1],
            split_path=paths_b[2],
            output_root=output_root,
            candidate_id="view-score-b",
            config=config,
        )
        self.assertEqual(result_a["model_metrics"], result_b["model_metrics"])
        self.assertEqual(result_a["declared_baselines"], result_b["declared_baselines"])

    def test_nonfixture_inputs_are_refused_before_candidate_creation(self) -> None:
        corpus, manifest, splits = self.write_phase0_fixture()
        regular_paths = (self.root / "corpus.jsonl", self.root / "manifest.json", self.root / "splits.json")
        for source, destination in zip((corpus, manifest, splits), regular_paths, strict=True):
            destination.write_bytes(source.read_bytes())
        with self.assertRaisesRegex(GeometryPhase0SafetyError, "_fixture_"):
            run_fixture_training(
                corpus_path=regular_paths[0],
                manifest_path=regular_paths[1],
                split_path=regular_paths[2],
                output_root=self.root / "candidate_output",
                candidate_id="nonfixture-refusal",
                config=TrainingConfig(epochs=1),
            )


if __name__ == "__main__":
    unittest.main()
