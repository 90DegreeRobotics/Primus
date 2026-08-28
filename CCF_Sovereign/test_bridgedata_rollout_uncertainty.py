from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.bridgedata_rollout_uncertainty import (  # noqa: E402
    BridgeDataRolloutUncertaintyError,
    PairedRolloutCaseError,
    episode_clustered_paired_bootstrap,
    paired_rollout_case_errors,
)
from real_data.bridgedata_rollouts import (  # noqa: E402
    BridgeDataRolloutCase,
    BridgeDataRolloutPrediction,
)


def vector(value: float) -> tuple[float, ...]:
    return tuple(value for _ in range(7))


def error_rows(candidate_mse: float, baseline_mse: float, *, episodes: int = 12) -> tuple[PairedRolloutCaseError, ...]:
    return tuple(
        PairedRolloutCaseError(
            case_id=f"e{episode}-case",
            episode_index=episode,
            candidate_mean_squared_error=candidate_mse,
            baseline_mean_squared_error=baseline_mse,
        )
        for episode in range(episodes)
    )


class BridgeDataRolloutUncertaintyTests(unittest.TestCase):
    def test_episode_clustered_bootstrap_pass_and_determinism(self):
        rows = error_rows(0.01, 0.04)
        first = episode_clustered_paired_bootstrap(rows, resamples=2000, seed=4)
        second = episode_clustered_paired_bootstrap(rows, resamples=2000, seed=4)
        self.assertEqual(first, second)
        self.assertEqual(first.interpretation, "pass")
        self.assertLess(first.percentile_ci_95_upper_mse, 0.0)
        self.assertEqual(first.distinct_episode_count, 12)

    def test_episode_clustered_bootstrap_fail(self):
        result = episode_clustered_paired_bootstrap(error_rows(0.09, 0.04), resamples=2000, seed=5)
        self.assertEqual(result.interpretation, "fail")
        self.assertGreater(result.percentile_ci_95_lower_mse, 0.0)

    def test_episode_clustered_bootstrap_indistinguishable(self):
        rows = tuple(
            PairedRolloutCaseError(
                case_id=f"e{episode}-case",
                episode_index=episode,
                candidate_mean_squared_error=0.03 + (0.02 if episode % 2 else -0.02),
                baseline_mean_squared_error=0.03,
            )
            for episode in range(12)
        )
        result = episode_clustered_paired_bootstrap(rows, resamples=4000, seed=6)
        self.assertEqual(result.interpretation, "indistinguishable")
        self.assertLessEqual(result.percentile_ci_95_lower_mse, 0.0)
        self.assertGreaterEqual(result.percentile_ci_95_upper_mse, 0.0)

    def test_episode_cluster_minimum_refuses_weak_sampling(self):
        with self.assertRaisesRegex(BridgeDataRolloutUncertaintyError, "at least 10"):
            episode_clustered_paired_bootstrap(error_rows(0.01, 0.04, episodes=9))

    def test_paired_case_errors_require_exact_prediction_coverage(self):
        case = BridgeDataRolloutCase(
            case_id="case",
            split="held_out_task",
            episode_index=12,
            task_index=4,
            task="task-4",
            horizon=1,
            source_transition_ids=("transition",),
            initial_state=vector(0.0),
            actions=(vector(0.1),),
            target_state=vector(0.1),
            source_index=1,
            target_index=2,
            source_frame_index=1,
            target_frame_index=2,
            source_timestamp=0.2,
            target_timestamp=0.4,
        )
        candidate = {"case": BridgeDataRolloutPrediction("case", vector(0.0))}
        baseline = {"case": BridgeDataRolloutPrediction("case", vector(0.1))}
        rows = paired_rollout_case_errors((case,), candidate, baseline)
        self.assertEqual(rows[0].candidate_mean_squared_error, 0.01)
        self.assertEqual(rows[0].baseline_mean_squared_error, 0.0)
        with self.assertRaisesRegex(BridgeDataRolloutUncertaintyError, "exact case coverage"):
            paired_rollout_case_errors((case,), {}, baseline)


if __name__ == "__main__":
    unittest.main(verbosity=2)
