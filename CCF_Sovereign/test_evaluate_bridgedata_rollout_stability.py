from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import evaluate_bridgedata_rollout_stability as evaluator  # noqa: E402


class FrozenRolloutEvidenceTests(unittest.TestCase):
    def test_file_evidence_refuses_byte_or_hash_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            artifact = repo / "evidence.json"
            artifact.write_text("frozen", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            evidence = {"path": "evidence.json", "bytes": artifact.stat().st_size, "sha256": digest}
            with patch.object(evaluator, "REPO_ROOT", repo):
                self.assertEqual(evaluator._verify_file_evidence(evidence, "fixture"), artifact.resolve())
                artifact.write_text("drifted", encoding="utf-8")
                with self.assertRaisesRegex(evaluator.FrozenRolloutEvidenceError, "byte count drifted"):
                    evaluator._verify_file_evidence(evidence, "fixture")
                artifact.write_text("frozen", encoding="utf-8")
                altered_hash = dict(evidence, sha256="0" * 64)
                with self.assertRaisesRegex(evaluator.FrozenRolloutEvidenceError, "SHA-256 drifted"):
                    evaluator._verify_file_evidence(altered_hash, "fixture")

    def test_candidate_loader_rejects_nonterminal_or_promoted_manifest_before_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate_dir = root / "checkpoints" / "candidates" / "bridge-real-20260827-001"
            candidate_dir.mkdir(parents=True)
            manifest = {
                "candidate_id": "bridge-real-20260827-001",
                "candidate_kind": "bridgedata_observed_state_transition",
                "status": "completed",
                "promotion": {"performed": False},
                "parent_protection": {"touched_by_training": False},
            }
            (candidate_dir / "real_data.run.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(evaluator, "ROOT", root), patch.object(evaluator, "REPO_ROOT", root.parent):
                with self.assertRaisesRegex(evaluator.FrozenRolloutEvidenceError, "terminal rejected"):
                    evaluator.load_frozen_rollout_candidate("bridge-real-20260827-001", device=evaluator.torch.device("cpu"))

    def test_split_payload_reconstructs_exact_contract(self):
        payload = {
            "split_version": 1,
            "config": {"seed": 7},
            "train_episode_indices": [1, 2],
            "held_out_episode_indices": [3],
            "held_out_task_episode_indices": [4],
            "train_task_indices": [10],
            "held_out_episode_task_indices": [10],
            "held_out_task_indices": [11],
            "excluded_unmapped_episode_indices": [0],
            "excluded_by_budget_episode_indices": [5],
            "expected_transition_counts": {"train": 3, "held_out_episode": 1, "held_out_task": 1},
        }
        split = evaluator._split_from_payload(payload)
        self.assertEqual(split.train_episode_indices, (1, 2))
        self.assertEqual(split.held_out_episode_indices, (3,))
        self.assertEqual(split.held_out_task_episode_indices, (4,))
        self.assertEqual(split.expected_transition_counts, payload["expected_transition_counts"])
        self.assertEqual(split.sha256(), evaluator._split_from_payload(json.loads(json.dumps(payload))).sha256())


if __name__ == "__main__":
    unittest.main(verbosity=2)
