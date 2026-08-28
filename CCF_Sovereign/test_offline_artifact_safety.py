from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.chronos_transition_contract import ChronosTransitionEvidence, write_new_contract
from real_data.offline_artifact_safety import (
    OFFLINE_INTENT,
    REQUIRED_DIAGNOSTIC_LABEL,
    OfflineArtifactSafetyError,
    validate_offline_artifact_pair,
    write_new_safety_receipt,
)


HASH = "b" * 64


def canonical(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def fixture(root: Path) -> tuple[Path, Path, Path]:
    evidence_root = root / "contract"
    witness_path = evidence_root / "witness.json"
    evidence = ChronosTransitionEvidence(
        candidate_id="candidate", candidate_checkpoint_sha256=HASH, candidate_manifest_sha256=HASH,
        protected_parent_sha256=HASH, intake_manifest_sha256=HASH, source_evidence_sha256=HASH,
        source_evidence_payload_sha256=HASH, source_evidence_path="strict.json", rollout_case_id="case",
        episode_index=2, task_index=3, horizon=2, observed_initial_state=(0.0,) * 7,
        observed_action_sequence=((1.0,) * 7, (2.0,) * 7), predicted_state_sequence=((0.1,) * 7, (0.2,) * 7),
    )
    write_new_contract(witness_path, evidence, allowed_root=evidence_root)
    png_path = root / "plot.png"
    png_path.write_bytes(b"not-a-real-png-fixture-but-hash-bound")
    receipt = {
        "diagnostic_version": 1, "diagnostic_scope": "offline_opaque_7d_state_trajectory_plot",
        "png_path": str(png_path), "png_sha256": hashlib.sha256(png_path.read_bytes()).hexdigest(), "png_bytes": png_path.stat().st_size,
        "png_dimensions": [1600, 1050], "witness_path": str(witness_path),
        "witness_sha256": hashlib.sha256(witness_path.read_bytes()).hexdigest(), "witness_payload_sha256": evidence.payload_sha256(),
        "intake_manifest_sha256": HASH, "episode_index": 2, "task_index": 3, "horizon": 2,
        "observed_transition_ids": ["t0", "t1"], "component_mean_absolute_error": [0.1] * 7,
        "overall_mean_absolute_error": 0.1, "chronos_invoked": False, "renderer_invoked": False,
        "control_permitted": False, "promotion_performed": False, "required_label": REQUIRED_DIAGNOSTIC_LABEL,
    }
    receipt["payload_sha256"] = canonical(receipt)
    receipt_path = root / "diagnostic_receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    return witness_path, receipt_path, png_path


class OfflineArtifactSafetyTests(unittest.TestCase):
    def test_valid_pair_reports_offline_only_and_writes_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            witness, receipt, png = fixture(root)
            report = validate_offline_artifact_pair(witness_path=witness, diagnostic_receipt_path=receipt, diagnostic_png_path=png)
            self.assertFalse(report["execution_authorized"])
            self.assertFalse(report["renderer_permitted"])
            receipt_root = root / "safety"
            destination = receipt_root / "report.json"
            digest = write_new_safety_receipt(destination, report, allowed_root=receipt_root)
            self.assertEqual(digest, hashlib.sha256(destination.read_bytes()).hexdigest())
            with self.assertRaisesRegex(OfflineArtifactSafetyError, "destination already exists"):
                write_new_safety_receipt(destination, report, allowed_root=receipt_root)

    def test_refuses_unsafe_intent_and_nonfalse_flag(self):
        with tempfile.TemporaryDirectory() as temporary:
            witness, receipt, png = fixture(Path(temporary))
            with self.assertRaisesRegex(OfflineArtifactSafetyError, "consumer intent"):
                validate_offline_artifact_pair(witness_path=witness, diagnostic_receipt_path=receipt, diagnostic_png_path=png, consumer_intent="render_scene")
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["renderer_invoked"] = True
            payload["payload_sha256"] = canonical({key: value for key, value in payload.items() if key != "payload_sha256"})
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(OfflineArtifactSafetyError, "renderer_invoked"):
                validate_offline_artifact_pair(witness_path=witness, diagnostic_receipt_path=receipt, diagnostic_png_path=png, consumer_intent=OFFLINE_INTENT)

    def test_refuses_unknown_field_and_digest_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            witness, receipt, png = fixture(Path(temporary))
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["program"] = "unsafe"
            payload["payload_sha256"] = canonical({key: value for key, value in payload.items() if key != "payload_sha256"})
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(OfflineArtifactSafetyError, "schema"):
                validate_offline_artifact_pair(witness_path=witness, diagnostic_receipt_path=receipt, diagnostic_png_path=png)
            payload.pop("program")
            payload["payload_sha256"] = "0" * 64
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(OfflineArtifactSafetyError, "SHA-256"):
                validate_offline_artifact_pair(witness_path=witness, diagnostic_receipt_path=receipt, diagnostic_png_path=png)


if __name__ == "__main__":
    unittest.main(verbosity=2)
