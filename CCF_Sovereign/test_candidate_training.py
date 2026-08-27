"""Regression gates for isolated Primus candidate training."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from training.candidate_run import CandidateRun, CandidateSafetyError, sha256_file


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_fixture(root: Path) -> tuple[Path, str, str]:
    project_root = root / "CCF_Sovereign"
    parent_bytes = b"frozen-parent-fixture"
    manifest_bytes = b'{"fixture": true}\n'
    paths = {
        project_root / "checkpoints" / "primus_council_trained.pt": parent_bytes,
        project_root
        / "checkpoints"
        / "frozen"
        / "parent_5e36cc9a_2026-08-26.pt": parent_bytes,
        project_root
        / "training"
        / "training_data"
        / "council_turns.manifest.json": manifest_bytes,
        project_root
        / "training"
        / "training_data"
        / "council_turns.jsonl": b'{"prompt":"p","response":"r"}\n',
    }
    for path, content in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return project_root, digest(parent_bytes), digest(manifest_bytes)


class CandidateTrainingSafetyTests(unittest.TestCase):
    def create_run(self, project_root: Path, parent_hash: str, manifest_hash: str):
        with patch(
            "training.candidate_run.git_commit",
            return_value="0123456789abcdef",
        ):
            return CandidateRun.create(
                project_root=project_root,
                candidate_id="candidate-001",
                seed=7,
                expected_parent_sha256=parent_hash,
                expected_corpus_manifest_sha256=manifest_hash,
                require_clean_repo=False,
            )

    def test_candidate_checkpoint_write_cannot_overwrite_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            project_root, parent_hash, manifest_hash = build_fixture(
                Path(temporary)
            )
            parent = (
                project_root
                / "checkpoints"
                / "primus_council_trained.pt"
            )
            original_parent = parent.read_bytes()
            run = self.create_run(project_root, parent_hash, manifest_hash)

            with self.assertRaises(CandidateSafetyError):
                run.assert_candidate_output(parent)

            run.mark_training_started(
                config={"MODEL_DIM": 8},
                turns=1,
                epochs=1,
                batch_size=1,
                max_sequence_length=8,
                device="cpu",
            )
            checkpoint = run.save_checkpoint(
                {"model_state_dict": {"weight": torch.ones(1)}},
                epoch=1,
                metrics={"average_loss": 1.0},
            )
            run.mark_completed()

            self.assertTrue(checkpoint.is_relative_to(run.candidate_dir))
            self.assertNotEqual(checkpoint.resolve(), parent.resolve())
            self.assertEqual(parent.read_bytes(), original_parent)
            self.assertEqual(sha256_file(parent), parent_hash)
            manifest = json.loads(run.manifest_path.read_text("utf-8"))
            self.assertEqual(manifest["status"], "completed")
            self.assertFalse(
                manifest["promotion"]["permitted_as_training_side_effect"]
            )
            self.assertFalse(manifest["promotion"]["performed"])
            self.assertEqual(
                manifest["latest_checkpoint"]["sha256"],
                sha256_file(checkpoint),
            )

    def test_parent_hash_drift_refuses_run_before_output_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            project_root, parent_hash, manifest_hash = build_fixture(
                Path(temporary)
            )
            parent = (
                project_root
                / "checkpoints"
                / "primus_council_trained.pt"
            )
            parent.write_bytes(b"changed-parent")
            candidate_dir = (
                project_root
                / "checkpoints"
                / "candidates"
                / "candidate-001"
            )
            with patch(
                "training.candidate_run.git_commit",
                return_value="0123456789abcdef",
            ):
                with self.assertRaises(CandidateSafetyError):
                    CandidateRun.create(
                        project_root=project_root,
                        candidate_id="candidate-001",
                        seed=7,
                        expected_parent_sha256=parent_hash,
                        expected_corpus_manifest_sha256=manifest_hash,
                        require_clean_repo=False,
                    )
            self.assertFalse(candidate_dir.exists())

    def test_corpus_manifest_hash_drift_refuses_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            project_root, parent_hash, manifest_hash = build_fixture(
                Path(temporary)
            )
            corpus_manifest = (
                project_root
                / "training"
                / "training_data"
                / "council_turns.manifest.json"
            )
            corpus_manifest.write_text('{"changed": true}\n', "utf-8")
            with patch(
                "training.candidate_run.git_commit",
                return_value="0123456789abcdef",
            ):
                with self.assertRaises(CandidateSafetyError):
                    CandidateRun.create(
                        project_root=project_root,
                        candidate_id="candidate-001",
                        seed=7,
                        expected_parent_sha256=parent_hash,
                        expected_corpus_manifest_sha256=manifest_hash,
                        require_clean_repo=False,
                    )

    def test_existing_candidate_destination_is_never_reused(self):
        with tempfile.TemporaryDirectory() as temporary:
            project_root, parent_hash, manifest_hash = build_fixture(
                Path(temporary)
            )
            self.create_run(project_root, parent_hash, manifest_hash)
            with self.assertRaises(CandidateSafetyError):
                self.create_run(project_root, parent_hash, manifest_hash)

    def test_additional_frozen_input_is_manifest_bound_and_rejects_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            project_root, parent_hash, manifest_hash = build_fixture(
                Path(temporary)
            )
            world_manifest = project_root / "world" / "generated.manifest.json"
            world_manifest.parent.mkdir(parents=True)
            world_manifest.write_bytes(b'{"generated":true}\n')
            expected_world_hash = sha256_file(world_manifest)
            with patch(
                "training.candidate_run.git_commit",
                return_value="0123456789abcdef",
            ):
                run = CandidateRun.create(
                    project_root=project_root,
                    candidate_id="candidate-world-input",
                    seed=7,
                    expected_parent_sha256=parent_hash,
                    expected_corpus_manifest_sha256=manifest_hash,
                    additional_frozen_inputs={
                        "world_dataset_manifest": (
                            world_manifest,
                            expected_world_hash,
                        ),
                    },
                    require_clean_repo=False,
                )
            evidence = run.manifest["additional_frozen_inputs"]
            self.assertEqual(
                evidence["world_dataset_manifest"]["sha256"], expected_world_hash
            )
            world_manifest.write_bytes(b'{"generated":false}\n')
            with self.assertRaisesRegex(CandidateSafetyError, "hash changed"):
                run.verify_frozen_inputs()


if __name__ == "__main__":
    unittest.main(verbosity=2)
