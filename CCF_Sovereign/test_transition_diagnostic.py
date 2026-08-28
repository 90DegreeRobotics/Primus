from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.chronos_transition_contract import ChronosTransitionEvidence
from real_data.transition_diagnostic import TransitionDiagnosticError, component_absolute_errors, resolve_observed_sequence


HASH = "a" * 64


def evidence() -> ChronosTransitionEvidence:
    return ChronosTransitionEvidence(
        candidate_id="bridge-real-20260827-002", candidate_checkpoint_sha256=HASH,
        candidate_manifest_sha256=HASH, protected_parent_sha256=HASH,
        intake_manifest_sha256=HASH, source_evidence_sha256=HASH,
        source_evidence_payload_sha256=HASH, source_evidence_path="strict.json",
        rollout_case_id="case", episode_index=4, task_index=8, horizon=2,
        observed_initial_state=(0.0,) * 7,
        observed_action_sequence=((1.0,) * 7, (2.0,) * 7),
        predicted_state_sequence=((0.5,) * 7, (1.0,) * 7),
    )


def transition(frame: int, action: float, target: float) -> SimpleNamespace:
    return SimpleNamespace(
        transition_id=f"t-{frame}", episode_index=4, task_index=8,
        source_frame_index=frame, state_t=(0.0,) * 7 if frame == 0 else (target - 1.0,) * 7,
        action_t=(action,) * 7, state_t_plus_1=(target,) * 7,
    )


class TransitionDiagnosticTests(unittest.TestCase):
    def test_exact_unique_lineage_and_absolute_errors(self):
        observed = resolve_observed_sequence((transition(0, 1.0, 1.0), transition(1, 2.0, 2.0)), evidence())
        self.assertEqual(observed.source_transition_ids, ("t-0", "t-1"))
        self.assertEqual(observed.observed_state_sequence, ((1.0,) * 7, (2.0,) * 7))
        self.assertEqual(component_absolute_errors(observed, evidence()), ((0.5,) * 7, (1.0,) * 7))

    def test_lineage_refuses_action_disagreement_or_missing_transition(self):
        with self.assertRaisesRegex(TransitionDiagnosticError, "no unique"):
            resolve_observed_sequence((transition(0, 9.0, 1.0), transition(1, 2.0, 2.0)), evidence())
        with self.assertRaisesRegex(TransitionDiagnosticError, "no unique"):
            resolve_observed_sequence((transition(0, 1.0, 1.0),), evidence())

    def test_lineage_refuses_duplicate_candidate_sequences(self):
        duplicated = (transition(0, 1.0, 1.0), transition(1, 2.0, 2.0), transition(0, 1.0, 1.0), transition(1, 2.0, 2.0))
        with self.assertRaisesRegex(TransitionDiagnosticError, "duplicate transition identifiers"):
            resolve_observed_sequence(duplicated, evidence())


if __name__ == "__main__":
    unittest.main(verbosity=2)
