from __future__ import annotations

import tempfile
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.chronos_transition_contract import (
    ChronosTransitionContractError,
    ChronosTransitionEvidence,
    STATE_COORDINATE_SEMANTICS,
    load_verified_contract,
    write_new_contract,
)


HASH = "a" * 64


def evidence() -> ChronosTransitionEvidence:
    return ChronosTransitionEvidence(
        candidate_id="bridge-real-20260827-002",
        candidate_checkpoint_sha256=HASH,
        candidate_manifest_sha256=HASH,
        protected_parent_sha256=HASH,
        intake_manifest_sha256=HASH,
        source_evidence_sha256=HASH,
        source_evidence_payload_sha256=HASH,
        source_evidence_path="C:/Primus/CCF_Sovereign/evaluation/strict.json",
        rollout_case_id="bridgedata-rollout-held_out_task-e1-f0-i0-h2",
        episode_index=1,
        task_index=2,
        horizon=2,
        observed_initial_state=(0.0,) * 7,
        observed_action_sequence=((0.1,) * 7, (0.2,) * 7),
        predicted_state_sequence=((0.3,) * 7, (0.4,) * 7),
    )


class ChronosTransitionContractTests(unittest.TestCase):
    def test_canonical_round_trip_has_explicit_unknown_scene_semantics(self):
        payload = evidence().to_dict()
        self.assertEqual(payload["state_coordinate_semantics"], STATE_COORDINATE_SEMANTICS)
        self.assertFalse(payload["control_permitted"])
        self.assertFalse(payload["promotion_performed"])
        restored = ChronosTransitionEvidence.from_dict(payload)
        self.assertEqual(restored.payload_sha256(), payload["payload_sha256"])

    def test_unknown_render_or_control_field_is_refused(self):
        payload = evidence().to_dict()
        payload["renderer_primitive"] = "cube"
        with self.assertRaisesRegex(ChronosTransitionContractError, "unknown fields"):
            ChronosTransitionEvidence.from_dict(payload)

    def test_non_unknown_coordinate_semantics_or_control_is_refused(self):
        payload = evidence().to_dict()
        payload["state_coordinate_semantics"] = "x_y_z_scene_transform"
        with self.assertRaisesRegex(ChronosTransitionContractError, "explicitly unknown"):
            ChronosTransitionEvidence.from_dict(payload)
        payload = evidence().to_dict()
        payload["control_permitted"] = True
        with self.assertRaisesRegex(ChronosTransitionContractError, "permit control"):
            ChronosTransitionEvidence.from_dict(payload)

    def test_invalid_state_dimension_and_digest_drift_are_refused(self):
        bad = evidence()
        bad = ChronosTransitionEvidence(**{**bad.__dict__, "observed_initial_state": (0.0,) * 6})
        with self.assertRaisesRegex(ChronosTransitionContractError, "exactly 7"):
            bad.to_dict()
        payload = evidence().to_dict()
        payload["payload_sha256"] = "b" * 64
        with self.assertRaisesRegex(ChronosTransitionContractError, "SHA-256 mismatch"):
            ChronosTransitionEvidence.from_dict(payload)

    def test_write_is_local_root_bound_fresh_and_readable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "evidence"
            target = root / "witness.json"
            digest = write_new_contract(target, evidence(), allowed_root=root)
            self.assertEqual(len(digest), 64)
            self.assertEqual(load_verified_contract(target).candidate_id, "bridge-real-20260827-002")
            with self.assertRaisesRegex(ChronosTransitionContractError, "already exists"):
                write_new_contract(target, evidence(), allowed_root=root)
            with self.assertRaisesRegex(ChronosTransitionContractError, "local evidence root"):
                write_new_contract(Path(temporary) / "outside.json", evidence(), allowed_root=root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
