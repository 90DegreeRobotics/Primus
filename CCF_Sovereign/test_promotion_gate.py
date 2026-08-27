"""Fail-hard tests for explicit Primus promotion governance."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from promotion.gate import PromotionEvidence, evaluate_promotion_evidence


PARENT_HASH = "5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b"
CANDIDATE_HASH = "a" * 64
EVAL_MANIFEST_HASH = "b" * 64


def completed_manifest() -> dict:
    return {
        "candidate_id": "candidate-050m",
        "status": "completed",
        "parent": {"sha256": PARENT_HASH},
        "frozen_parent": {"sha256": PARENT_HASH},
        "latest_checkpoint": {
            "path": "CCF_Sovereign/checkpoints/candidates/candidate-050m/checkpoints/candidate_epoch_0001.pt",
            "sha256": CANDIDATE_HASH,
        },
        "promotion": {
            "permitted_as_training_side_effect": False,
            "performed": False,
        },
    }


def improving_comparison() -> dict:
    return {
        "manifest_sha256": EVAL_MANIFEST_HASH,
        "verdict": "CANDIDATE_IMPROVES",
        "candidate_gate_passed": True,
        "aggregate": {
            "pass_delta": 1,
            "protected_regressions": 0,
            "new_error_cases": 0,
        },
    }


def evidence(**overrides) -> PromotionEvidence:
    values = {
        "candidate_manifest": completed_manifest(),
        "comparison": improving_comparison(),
        "expected_candidate_sha256": CANDIDATE_HASH,
        "expected_parent_sha256": PARENT_HASH,
        "expected_evaluation_manifest_sha256": EVAL_MANIFEST_HASH,
        "live_parent_sha256_before": PARENT_HASH,
        "live_parent_sha256_after": PARENT_HASH,
        "operator_authorized": True,
    }
    values.update(overrides)
    return PromotionEvidence(**values)


class PromotionGateTests(unittest.TestCase):
    def test_hash_gated_promotion_returns_explicit_command_without_mutation(self):
        decision = evaluate_promotion_evidence(evidence())

        self.assertTrue(decision.eligible)
        self.assertEqual(decision.reasons, ())
        self.assertIn("python promote_candidate.py", decision.required_command)
        self.assertIn("--candidate-id candidate-050m", decision.required_command)
        self.assertIn(CANDIDATE_HASH, decision.required_command)
        self.assertFalse(decision.performs_mutation)
        self.assertFalse(decision.automatic_promotion)

    def test_operator_authorization_is_required_even_when_evidence_is_green(self):
        decision = evaluate_promotion_evidence(
            evidence(operator_authorized=False)
        )

        self.assertFalse(decision.eligible)
        self.assertIn("operator authorization is required for promotion", decision.reasons)
        self.assertFalse(decision.performs_mutation)

    def test_protected_regression_rejects_candidate(self):
        comparison = improving_comparison()
        comparison["verdict"] = "REJECT_PROTECTED_REGRESSION"
        comparison["candidate_gate_passed"] = False
        comparison["aggregate"]["protected_regressions"] = 1

        decision = evaluate_promotion_evidence(evidence(comparison=comparison))

        self.assertFalse(decision.eligible)
        self.assertIn("comparison records protected-task regressions", decision.reasons)
        self.assertIn("parent/candidate comparison gate did not pass", decision.reasons)

    def test_new_candidate_error_rejects_candidate(self):
        comparison = improving_comparison()
        comparison["verdict"] = "REJECT_NEW_ERRORS"
        comparison["candidate_gate_passed"] = False
        comparison["aggregate"]["new_error_cases"] = 1

        decision = evaluate_promotion_evidence(evidence(comparison=comparison))

        self.assertFalse(decision.eligible)
        self.assertIn("comparison records new candidate errors", decision.reasons)

    def test_manifest_parity_is_required(self):
        comparison = improving_comparison()
        comparison["manifest_sha256"] = "c" * 64

        decision = evaluate_promotion_evidence(evidence(comparison=comparison))

        self.assertFalse(decision.eligible)
        self.assertIn(
            "comparison manifest hash does not match expected evaluation manifest",
            decision.reasons,
        )

    def test_parent_hash_must_remain_immutable_before_and_after_evaluation(self):
        decision = evaluate_promotion_evidence(
            evidence(live_parent_sha256_after="d" * 64)
        )

        self.assertFalse(decision.eligible)
        self.assertIn("live parent hash after evaluation changed", decision.reasons)

    def test_candidate_manifest_cannot_record_training_side_effect_promotion(self):
        manifest = copy.deepcopy(completed_manifest())
        manifest["promotion"]["permitted_as_training_side_effect"] = True

        decision = evaluate_promotion_evidence(evidence(candidate_manifest=manifest))

        self.assertFalse(decision.eligible)
        self.assertIn(
            "candidate manifest permits promotion as a training side effect",
            decision.reasons,
        )

    def test_candidate_checkpoint_hash_must_match_operator_supplied_hash(self):
        manifest = copy.deepcopy(completed_manifest())
        manifest["latest_checkpoint"]["sha256"] = "e" * 64

        decision = evaluate_promotion_evidence(evidence(candidate_manifest=manifest))

        self.assertFalse(decision.eligible)
        self.assertIn(
            "candidate checkpoint hash does not match expected hash",
            decision.reasons,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
