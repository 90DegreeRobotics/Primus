from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.buyer_evidence_packet import BuyerEvidencePacketError, StrictEvidenceRow, _build_html, extract_strict_evidence_rows


def digest(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def row(source: str, horizon: int, *, task_overlap: int = 0, candidate: float = 0.02, baseline: float = 0.03) -> dict:
    return {
        "source_candidate_id": source, "horizon": horizon, "source_train_task_overlap_count": task_overlap,
        "source_selected_episode_overlap_count": 0, "strongest_baseline": "linear_state_action_delta",
        "candidate_metrics": {"aggregate_rmse": candidate, "cases": 256, "predictions": 256, "coverage": 1.0, "unknown_prediction_count": 0, "excluded_case_count": 0, "finite_prediction_rate": 1.0},
        "baseline_metrics": {"linear_state_action_delta": {"aggregate_rmse": baseline}},
    }


def payload() -> dict:
    value = {
        "acceptance_horizons": [1, 2, 5], "no_training": True, "no_checkpoint_mutation": True, "promotion_performed": False,
        "source_reports": {
            "one": {"point_estimate_passed_all_horizons": True, "bootstrap_passed_all_horizons": True, "rows": [row("one", value) for value in (1, 2, 5)]},
            "two": {"point_estimate_passed_all_horizons": True, "bootstrap_passed_all_horizons": True, "rows": [row("two", value) for value in (1, 2, 5)]},
        },
    }
    value["payload_sha256"] = digest(value)
    return value


class BuyerEvidencePacketTests(unittest.TestCase):
    def test_extracts_complete_disjoint_exact_rows(self):
        rows = extract_strict_evidence_rows(payload())
        self.assertEqual(len(rows), 6)
        self.assertEqual({entry.horizon for entry in rows}, {1, 2, 5})
        self.assertTrue(all(entry.margin > 0 for entry in rows))
        self.assertTrue(all(entry.source_train_task_overlap == 0 for entry in rows))

    def test_refuses_task_overlap_and_payload_drift(self):
        unsafe = payload(); unsafe["source_reports"]["one"]["rows"][0]["source_train_task_overlap_count"] = 1; unsafe["payload_sha256"] = digest({key: value for key, value in unsafe.items() if key != "payload_sha256"})
        with self.assertRaisesRegex(BuyerEvidencePacketError, "disjointness"):
            extract_strict_evidence_rows(unsafe)
        drifted = payload(); drifted["payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(BuyerEvidencePacketError, "SHA-256"):
            extract_strict_evidence_rows(drifted)

    def test_html_retains_required_negative_boundaries(self):
        html = _build_html((StrictEvidenceRow("one", 1, 0.02, "linear_state_action_delta", 0.03, 0.01, 256, 0, 0),), safety_receipt_sha256="a" * 64, strict_evidence_sha256="b" * 64, diagnostic_filename="plot.png")
        self.assertIn("OFFLINE EVIDENCE REVIEW ONLY", html)
        self.assertIn("not a Chronos scene, render, policy, or control signal", html)
        self.assertIn("What this does not show", html)
        self.assertIn("execution authorization", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
