from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from training.real_data_candidate import (  # noqa: E402
    RealDataCandidateRun,
    RealDataCandidateSafetyError,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=repo, check=True, capture_output=True, text=True)


class RealDataCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name) / "repo"
        self.project = self.repo / "CCF_Sovereign"
        self.project.mkdir(parents=True)
        (self.repo / ".gitignore").write_text("CCF_Sovereign/checkpoints/candidates/\n", encoding="utf-8")
        parent = self.project / "checkpoints" / "primus_council_trained.pt"
        frozen = self.project / "checkpoints" / "frozen" / "parent_5e36cc9a_2026-08-26.pt"
        parent.parent.mkdir(parents=True)
        frozen.parent.mkdir(parents=True)
        parent.write_bytes(b"frozen-parent")
        frozen.write_bytes(b"frozen-parent")
        self.parent_hash = sha256(parent)
        self.inputs = {}
        for label, filename in (
            ("intake_manifest", "intake_manifest.json"),
            ("data_parquet", "data.parquet"),
            ("episodes_parquet", "episodes.parquet"),
            ("tasks_parquet", "tasks.parquet"),
        ):
            path = self.project / "frozen_inputs" / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(label.encode("ascii"))
            self.inputs[label] = (path, sha256(path))
        git(self.repo, "init", "--initial-branch", "main")
        git(self.repo, "config", "user.email", "test@example.invalid")
        git(self.repo, "config", "user.name", "Test Operator")
        git(self.repo, "add", "CCF_Sovereign", ".gitignore")
        git(self.repo, "commit", "-m", "test: fixture")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _create(self, candidate_id: str = "bridge-real-001", **kwargs) -> RealDataCandidateRun:
        return RealDataCandidateRun.create(
            self.project,
            candidate_id,
            seed=73,
            expected_parent_sha256=self.parent_hash,
            additional_frozen_inputs=self.inputs,
            **kwargs,
        )

    def test_lifecycle_is_isolated_and_ends_rejected_without_promotion(self):
        run = self._create()
        self.assertTrue(run.manifest_path.is_file())
        self.assertEqual(run.manifest["status"], "prepared")
        self.assertFalse(run.manifest["promotion"]["performed"])
        self.assertFalse(run.manifest["promotion"]["interface_available"])
        self.assertFalse(run.manifest["parent_protection"]["used_as_model_input"])

        run.mark_training_started(
            config={"architecture": "mlp", "input_dimensions": 14, "output_dimensions": 7},
            examples=12,
            epochs=2,
            batch_size=4,
            device="cpu",
        )
        checkpoint = run.save_checkpoint({"test": True}, metrics={"train_loss": 0.2})
        metrics = run.write_evidence_json("metrics.json", {"by_split": {"train": {"cases": 12}}})
        predictions = run.write_evidence_json("predictions.json", {"prediction_count": 12})
        run.mark_evaluated(metrics_report=metrics, predictions=predictions)
        run.mark_rejected("test-only rejection")

        self.assertTrue(checkpoint.is_file())
        self.assertEqual(run.manifest["status"], "rejected")
        self.assertEqual(run.manifest["rejection"]["reason"], "test-only rejection")
        self.assertEqual(sha256(self.project / "checkpoints" / "primus_council_trained.pt"), self.parent_hash)
        manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "rejected")
        self.assertFalse(manifest["promotion"]["performed"])

    def test_clean_repository_is_required_before_candidate_creation(self):
        (self.repo / "untracked.txt").write_text("dirty\n", encoding="utf-8")

        with self.assertRaisesRegex(RealDataCandidateSafetyError, "clean repository"):
            self._create()

    def test_hash_pinned_inherited_untracked_file_is_allowed_but_arbitrary_dirt_is_not(self):
        inherited = self.repo / "older_plan.md"
        inherited.write_text("preserved\n", encoding="utf-8")
        run = self._create(
            permitted_preexisting_untracked={"older_plan": (inherited, sha256(inherited))}
        )
        self.assertEqual(
            run.manifest["permitted_preexisting_untracked"]["older_plan"]["sha256"],
            sha256(inherited),
        )
        (self.repo / "unexpected.md").write_text("not allowed\n", encoding="utf-8")
        with self.assertRaisesRegex(RealDataCandidateSafetyError, "exact hash-pinned"):
            run.mark_training_started(
                config={"architecture": "mlp"}, examples=1, epochs=1, batch_size=1, device="cpu"
            )

    def test_frozen_data_hash_drift_blocks_training_lifecycle(self):
        run = self._create()
        self.inputs["data_parquet"][0].write_bytes(b"drift")

        with self.assertRaisesRegex(RealDataCandidateSafetyError, "frozen real-data input hash changed"):
            run.mark_training_started(
                config={"architecture": "mlp"}, examples=1, epochs=1, batch_size=1, device="cpu"
            )

    def test_parent_destination_and_existing_candidate_are_refused(self):
        run = self._create()
        with self.assertRaisesRegex(RealDataCandidateSafetyError, "protected parent"):
            run.assert_candidate_output(self.project / "checkpoints" / "primus_council_trained.pt")
        with self.assertRaisesRegex(RealDataCandidateSafetyError, "destination already exists"):
            self._create()

    def test_required_real_data_frozen_input_cannot_be_omitted(self):
        incomplete = dict(self.inputs)
        incomplete.pop("tasks_parquet")

        with self.assertRaisesRegex(RealDataCandidateSafetyError, "lacks required frozen inputs"):
            RealDataCandidateRun.create(
                self.project,
                "bridge-real-incomplete",
                seed=73,
                expected_parent_sha256=self.parent_hash,
                additional_frozen_inputs=incomplete,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
