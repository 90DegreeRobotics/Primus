from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.bridgedata_evaluation import (  # noqa: E402
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    LinearStateActionDeltaBaseline,
)
from real_data.bridgedata_rollouts import (  # noqa: E402
    BridgeDataRolloutError,
    BridgeDataRolloutPrediction,
    build_rollout_cases,
    copy_state_predictor,
    evaluate_rollout_predictor,
    linear_state_action_delta_predictor,
    predeclared_rollout_acceptance,
    rollout_predictions,
    score_rollout_predictions,
)
from real_data.bridgedata_transitions import BridgeDataTransition  # noqa: E402


def vector(value: float) -> tuple[float, ...]:
    return tuple(value for _ in range(7))


def transition(
    episode_index: int,
    source_index: int,
    *,
    task_index: int,
    step_size: float = 0.1,
) -> BridgeDataTransition:
    return BridgeDataTransition(
        transition_id=f"e{episode_index}-i{source_index}",
        episode_index=episode_index,
        task_index=task_index,
        task=f"task-{task_index}",
        source_index=source_index,
        target_index=source_index + 1,
        source_frame_index=source_index,
        target_frame_index=source_index + 1,
        source_timestamp=source_index * 0.2,
        target_timestamp=(source_index + 1) * 0.2,
        state_t=vector(source_index * step_size),
        action_t=vector(step_size),
        state_t_plus_1=vector((source_index + 1) * step_size),
    )


class BridgeDataRolloutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.partitioned = {
            TRAIN_SPLIT: tuple(transition(10, index, task_index=1) for index in range(8)),
            HELD_OUT_EPISODE_SPLIT: tuple(transition(20, index, task_index=1) for index in range(8)),
            HELD_OUT_TASK_SPLIT: tuple(transition(30, index, task_index=2) for index in range(8)),
        }

    def test_cases_are_episode_contained_deterministic_and_bounded(self):
        first = build_rollout_cases(
            self.partitioned[HELD_OUT_EPISODE_SPLIT],
            split=HELD_OUT_EPISODE_SPLIT,
            horizon=2,
            max_cases=3,
            case_selection_seed=19,
        )
        second = build_rollout_cases(
            self.partitioned[HELD_OUT_EPISODE_SPLIT],
            split=HELD_OUT_EPISODE_SPLIT,
            horizon=2,
            max_cases=3,
            case_selection_seed=19,
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 3)
        for case in first:
            self.assertEqual(case.horizon, 2)
            self.assertEqual(case.target_index, case.source_index + 2)
            self.assertEqual(case.target_frame_index, case.source_frame_index + 2)
            self.assertEqual(len(case.actions), 2)

    def test_sequence_gap_is_rejected_before_rollout(self):
        broken = (
            transition(20, 0, task_index=1),
            transition(20, 2, task_index=1),
        )
        with self.assertRaisesRegex(BridgeDataRolloutError, "skips a global"):
            build_rollout_cases(broken, split=HELD_OUT_EPISODE_SPLIT, horizon=1)

    def test_timestamp_discontinuity_is_rejected_before_rollout(self):
        first = transition(20, 0, task_index=1)
        second = replace(
            transition(20, 1, task_index=1),
            source_timestamp=0.25,
            target_timestamp=0.45,
        )
        with self.assertRaisesRegex(BridgeDataRolloutError, "discontinuous source timestamp"):
            build_rollout_cases((first, second), split=HELD_OUT_EPISODE_SPLIT, horizon=1)

    def test_recursive_rollout_never_uses_observed_intermediate_state(self):
        cases = build_rollout_cases(
            self.partitioned[HELD_OUT_EPISODE_SPLIT],
            split=HELD_OUT_EPISODE_SPLIT,
            horizon=2,
            max_cases=1,
            case_selection_seed=1,
        )
        calls: list[tuple[float, ...]] = []

        def predictor(state: tuple[float, ...], _action: tuple[float, ...]) -> tuple[float, ...]:
            calls.append(state)
            return tuple(value + 10.0 for value in state)

        predictions = rollout_predictions(cases, predictor)
        self.assertEqual(len(predictions), 1)
        self.assertEqual(calls[0], cases[0].initial_state)
        self.assertEqual(calls[1], vector(cases[0].initial_state[0] + 10.0))
        self.assertNotEqual(calls[1], vector(cases[0].initial_state[0] + 0.1))

    def test_scoring_requires_exact_case_coverage(self):
        cases = build_rollout_cases(
            self.partitioned[HELD_OUT_EPISODE_SPLIT],
            split=HELD_OUT_EPISODE_SPLIT,
            horizon=1,
            max_cases=2,
            case_selection_seed=2,
        )
        correct = rollout_predictions(cases, copy_state_predictor)
        missing = dict(correct)
        missing.pop(next(iter(missing)))
        with self.assertRaisesRegex(BridgeDataRolloutError, "coverage mismatch"):
            score_rollout_predictions(cases, missing)
        extra = dict(correct)
        extra["unexpected"] = BridgeDataRolloutPrediction("unexpected", vector(0.0))
        with self.assertRaisesRegex(BridgeDataRolloutError, "coverage mismatch"):
            score_rollout_predictions(cases, extra)

    def test_zero_horizon_one_error_is_reported_without_abort(self):
        def perfect_predictor(state: tuple[float, ...], action: tuple[float, ...]) -> tuple[float, ...]:
            return tuple(value + delta for value, delta in zip(state, action))

        zero_partitioned = {
            split: tuple(
                replace(item, state_t=vector(0.0), action_t=vector(0.0), state_t_plus_1=vector(0.0))
                for item in transitions
            )
            for split, transitions in self.partitioned.items()
        }
        report = evaluate_rollout_predictor(
            zero_partitioned,
            prediction_label="perfect_fixture",
            predict_next_state=perfect_predictor,
            horizons=(1, 2, 5),
            max_cases_per_horizon=3,
            case_selection_seed=7,
        )
        for split in (TRAIN_SPLIT, HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT):
            self.assertEqual(report.by_split_and_horizon[split][1].aggregate_rmse, 0.0)
            self.assertEqual(report.error_growth_ratio_to_horizon_one[split][1], 1.0)
            self.assertEqual(report.error_growth_ratio_to_horizon_one[split][5], 1.0)

    def test_temporal_evaluation_reports_growth_and_applies_protected_rule(self):
        def candidate_predictor(state: tuple[float, ...], action: tuple[float, ...]) -> tuple[float, ...]:
            return tuple(value + delta + 0.001 for value, delta in zip(state, action))

        candidate = evaluate_rollout_predictor(
            self.partitioned,
            prediction_label="candidate",
            predict_next_state=candidate_predictor,
            horizons=(1, 2, 5),
            max_cases_per_horizon=3,
            case_selection_seed=7,
        )
        baseline = evaluate_rollout_predictor(
            self.partitioned,
            prediction_label="copy_state",
            predict_next_state=copy_state_predictor,
            horizons=(1, 2, 5),
            max_cases_per_horizon=3,
            case_selection_seed=7,
        )
        acceptance = predeclared_rollout_acceptance(candidate, {"copy_state": baseline})
        self.assertTrue(acceptance["passed"])
        for split in (HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT):
            self.assertEqual(candidate.by_split_and_horizon[split][5].coverage, 1.0)
            self.assertGreater(candidate.error_growth_ratio_to_horizon_one[split][5], 1.0)
            self.assertTrue(acceptance["by_protected_split_and_horizon"][split]["5"]["strict_improvement"])

    def test_linear_rollout_predictor_uses_current_predicted_state(self):
        linear_train = tuple(
            transition(10, index, task_index=1, step_size=0.1)
            for index in range(15)
        )
        baseline = LinearStateActionDeltaBaseline.fit(linear_train)
        predictor = linear_state_action_delta_predictor(baseline)
        first = predictor(vector(0.0), vector(0.1))
        second = predictor(first, vector(0.1))
        self.assertAlmostEqual(first[0], 0.1, places=10)
        self.assertAlmostEqual(second[0], 0.2, places=10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
