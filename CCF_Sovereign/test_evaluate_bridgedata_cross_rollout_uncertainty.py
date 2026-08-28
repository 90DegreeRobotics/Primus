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

import evaluate_bridgedata_cross_rollout_uncertainty as evaluator  # noqa: E402


class CrossRolloutUncertaintyAuditIntegrityTests(unittest.TestCase):
    def test_signed_evidence_requires_file_and_payload_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "signed.json"
            payload = {
                "candidate_ids": list(evaluator.EXPECTED_CANDIDATE_IDS),
                "cross_pairs": {},
                "no_training": True,
                "no_candidate_creation": True,
                "no_checkpoint_mutation": True,
                "promotion_performed": False,
            }
            payload["payload_sha256"] = evaluator._sha256_json(payload)
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with patch.object(evaluator, "SIGNED_CROSS_EVIDENCE_SHA256", digest), patch.object(
                evaluator, "SIGNED_CROSS_PAYLOAD_SHA256", payload["payload_sha256"]
            ):
                loaded = evaluator._load_signed_cross_evidence(path)
                self.assertEqual(loaded["payload_sha256"], payload["payload_sha256"])
                path.write_text(json.dumps(dict(payload, no_training=False), sort_keys=True), encoding="utf-8")
                with self.assertRaisesRegex(evaluator.CrossRolloutUncertaintyAuditError, "file SHA-256 drifted"):
                    evaluator._load_signed_cross_evidence(path)

    def test_metric_parity_refuses_case_and_rmse_mismatch(self):
        expected = {
            "cases": 256,
            "predictions": 256,
            "coverage": 1.0,
            "finite_prediction_rate": 1.0,
            "case_set_sha256": "a" * 64,
            "aggregate_rmse": 0.2,
        }
        evaluator._require_metric_parity(dict(expected), dict(expected), label="fixture")
        wrong_cases = dict(expected, cases=255)
        with self.assertRaisesRegex(evaluator.CrossRolloutUncertaintyAuditError, "cases"):
            evaluator._require_metric_parity(wrong_cases, expected, label="fixture")
        wrong_rmse = dict(expected, aggregate_rmse=0.20000000001)
        with self.assertRaisesRegex(evaluator.CrossRolloutUncertaintyAuditError, "aggregate_rmse"):
            evaluator._require_metric_parity(wrong_rmse, expected, label="fixture")


if __name__ == "__main__":
    unittest.main(verbosity=2)
