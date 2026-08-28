from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import evaluate_bridgedata_context_robustness as context  # noqa: E402


def episode(index: int, *, length: int = 100, dataset_from_index: int = 0) -> SimpleNamespace:
    return SimpleNamespace(episode_index=index, length=length, dataset_from_index=dataset_from_index, dataset_to_index=dataset_from_index + length - 1)


def case(case_id: str, episode_index: int, source_frame_index: int, action_value: float) -> SimpleNamespace:
    return SimpleNamespace(
        case_id=case_id,
        episode_index=episode_index,
        source_frame_index=source_frame_index,
        horizon=1,
        actions=((action_value,) * 7,),
    )


class ContextRobustnessTests(unittest.TestCase):
    def test_source_train_action_energy_median_is_train_only_and_finite(self):
        train = [SimpleNamespace(action_t=(0.0,) * 7), SimpleNamespace(action_t=(2.0,) * 7)]
        expected = (7.0 ** 0.5)
        self.assertAlmostEqual(context.source_train_action_energy_median(train), expected)
        with self.assertRaisesRegex(context.ContextRobustnessError, "requires transitions"):
            context.source_train_action_energy_median(())

    def test_case_context_uses_declared_position_and_recorded_actions_not_targets(self):
        # source_frame_index is episode-local despite this nonzero global Parquet offset.
        episodes = {1: episode(1, dataset_from_index=1000)}
        early = case("early", 1, 20, 0.0)
        late = case("late", 1, 75, 2.0)
        self.assertEqual(context.case_context(early, episodes, source_train_action_energy_median_value=1.0), "early_low_action_energy")
        self.assertEqual(context.case_context(late, episodes, source_train_action_energy_median_value=1.0), "late_high_action_energy")

    def test_context_selection_is_deterministic_bounded_and_clustered(self):
        episodes = {index: episode(index) for index in range(20)}
        cases = tuple(case(f"case-{index}", index, 20, 0.0) for index in range(20))
        first = context.select_context_cases(cases, source_candidate_id="bridge-real-20260827-001", horizon=1, context="early_low_action_energy", episodes=episodes, source_train_action_energy_median_value=1.0, max_cases=12)
        second = context.select_context_cases(cases, source_candidate_id="bridge-real-20260827-001", horizon=1, context="early_low_action_energy", episodes=episodes, source_train_action_energy_median_value=1.0, max_cases=12)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 12)
        self.assertGreaterEqual(len({item.episode_index for item in first}), 10)

    def test_context_selection_refuses_missing_capacity_and_unknown_context(self):
        episodes = {index: episode(index) for index in range(10)}
        cases = tuple(case(f"case-{index}", index, 20, 0.0) for index in range(10))
        with self.assertRaisesRegex(context.ContextRobustnessError, "context is not predeclared"):
            context.select_context_cases(cases, source_candidate_id="bridge-real-20260827-001", horizon=1, context="unknown", episodes=episodes, source_train_action_energy_median_value=1.0, max_cases=10)
        with self.assertRaisesRegex(context.ContextRobustnessError, "fixed bounded case capacity"):
            context.select_context_cases(cases, source_candidate_id="bridge-real-20260827-001", horizon=1, context="early_low_action_energy", episodes=episodes, source_train_action_energy_median_value=1.0, max_cases=11)

    def test_evaluator_rejects_candidate_order_and_outside_evidence_root(self):
        with self.assertRaisesRegex(context.ContextRobustnessError, "ordered predeclared"):
            context.evaluate_context_robustness(tuple(reversed(context.EXPECTED_CANDIDATE_IDS)), output_dir=Path("outside"))
        with self.assertRaisesRegex(context.ContextRobustnessError, "ignored local evaluation root"):
            context.evaluate_context_robustness(context.EXPECTED_CANDIDATE_IDS, output_dir=Path("outside"))


if __name__ == "__main__":
    unittest.main(verbosity=2)


