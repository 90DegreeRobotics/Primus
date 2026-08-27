"""Budget and parity tests for serialized Primus candidate experiments."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from promotion.gate import (
    AblationArm,
    BudgetSpec,
    validate_ablation_budget_parity,
    validate_small_candidate_budget,
)


def budget(**overrides) -> BudgetSpec:
    values = {
        "rung": "50m",
        "max_steps": 3940,
        "batch_size": 1,
        "sequence_length": 256,
        "epochs": 1,
        "learning_rate": 3e-4,
        "vocab_size": 2048,
        "promotion_permitted_by_default": False,
    }
    values.update(overrides)
    return BudgetSpec(**values)


class BudgetParityTests(unittest.TestCase):
    def test_small_candidate_run_allows_only_50m_with_gate_and_operator(self):
        decision = validate_small_candidate_budget(
            budget(),
            operator_authorized=True,
            gate_armed=True,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reasons, ())

    def test_small_candidate_run_rejects_150m_attempt(self):
        decision = validate_small_candidate_budget(
            budget(rung="150m"),
            operator_authorized=True,
            gate_armed=True,
        )

        self.assertFalse(decision.allowed)
        self.assertIn("first candidate run must use the 50m rung", decision.reasons)

    def test_small_candidate_run_requires_gate_and_operator_authorization(self):
        decision = validate_small_candidate_budget(
            budget(),
            operator_authorized=False,
            gate_armed=False,
        )

        self.assertFalse(decision.allowed)
        self.assertIn(
            "operator authorization is required for candidate run",
            decision.reasons,
        )
        self.assertIn(
            "promotion/comparison gate must be armed before run",
            decision.reasons,
        )

    def test_ablation_arms_must_keep_equal_resource_budgets(self):
        arms = [
            AblationArm("A-baseline", budget()),
            AblationArm("B-world-data", budget()),
            AblationArm("C-world-data-metrics", budget()),
        ]

        decision = validate_ablation_budget_parity(arms)

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reasons, ())

    def test_ablation_budget_drift_is_rejected(self):
        arms = [
            AblationArm("A-baseline", budget()),
            AblationArm("B-extra-steps", budget(max_steps=5000)),
        ]

        decision = validate_ablation_budget_parity(arms)

        self.assertFalse(decision.allowed)
        self.assertIn(
            "B-extra-steps resource budget differs from baseline",
            decision.reasons,
        )

    def test_promotion_default_is_rejected_for_every_experiment_budget(self):
        small_run = validate_small_candidate_budget(
            budget(promotion_permitted_by_default=True),
            operator_authorized=True,
            gate_armed=True,
        )
        ablation = validate_ablation_budget_parity(
            [
                AblationArm("A", budget()),
                AblationArm(
                    "B",
                    budget(promotion_permitted_by_default=True),
                ),
            ]
        )

        self.assertFalse(small_run.allowed)
        self.assertIn("candidate budget permits promotion by default", small_run.reasons)
        self.assertFalse(ablation.allowed)
        self.assertIn("B permits promotion by default", ablation.reasons)


if __name__ == "__main__":
    unittest.main(verbosity=2)
