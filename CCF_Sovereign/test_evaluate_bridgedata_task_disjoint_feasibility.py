from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import evaluate_bridgedata_task_disjoint_feasibility as feasibility  # noqa: E402
from real_data.bridgedata_evaluation import (  # noqa: E402
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    BridgeDataSplit,
)
from real_data.bridgedata_transitions import BridgeDataIntake, EpisodeTask  # noqa: E402


def episode(index: int, task_index: int, *, length: int = 8) -> EpisodeTask:
    return EpisodeTask(
        episode_index=index,
        task_index=task_index,
        task=f"task-{task_index}",
        length=length,
        dataset_from_index=index * 100,
        dataset_to_index=index * 100 + length,
    )


def split(train: tuple[int, ...], held_episode: tuple[int, ...], held_task: tuple[int, ...], episodes: dict[int, EpisodeTask]) -> BridgeDataSplit:
    return BridgeDataSplit(
        split_version=1,
        config={"seed": 1},
        train_episode_indices=train,
        held_out_episode_indices=held_episode,
        held_out_task_episode_indices=held_task,
        train_task_indices=tuple(sorted({episodes[index].task_index for index in train})),
        held_out_episode_task_indices=tuple(sorted({episodes[index].task_index for index in held_episode})),
        held_out_task_indices=tuple(sorted({episodes[index].task_index for index in held_task})),
        excluded_unmapped_episode_indices=(),
        excluded_by_budget_episode_indices=tuple(
            sorted(set(episodes) - set(train) - set(held_episode) - set(held_task))
        ),
        expected_transition_counts={
            TRAIN_SPLIT: sum(episodes[index].length - 1 for index in train),
            HELD_OUT_EPISODE_SPLIT: sum(episodes[index].length - 1 for index in held_episode),
            HELD_OUT_TASK_SPLIT: sum(episodes[index].length - 1 for index in held_task),
        },
    )


def intake(episodes: dict[int, EpisodeTask]) -> BridgeDataIntake:
    return BridgeDataIntake(
        root=Path("."),
        manifest_path=Path("intake_manifest.json"),
        manifest_sha256="a" * 64,
        data_path=Path("data.parquet"),
        episode_path=Path("episodes.parquet"),
        task_path=Path("tasks.parquet"),
        data_rows=1000,
        source_files={},
        episodes=episodes,
    )


class TaskDisjointFeasibilityTests(unittest.TestCase):
    def test_pool_excludes_source_selected_episodes_and_train_tasks(self):
        episodes = {
            1: episode(1, 10),
            2: episode(2, 10),
            3: episode(3, 11),
            4: episode(4, 12),
            5: episode(5, 99),
            6: episode(6, 99),
        }
        source = split((1, 2), (3,), (4,), episodes)
        pool = feasibility.task_disjoint_episode_pool(episodes, source)
        self.assertEqual([item.episode_index for item in pool], [5, 6])
        self.assertEqual({item.task_index for item in pool}, {99})

    def test_horizon_capacity_requires_cases_and_clusters(self):
        enough = tuple(episode(index, 100 + index, length=32) for index in range(12))
        summary = feasibility.horizon_capacity_summary(enough, required_cases=256, minimum_distinct_episodes=10)
        self.assertTrue(summary["5"]["feasible"])
        weak = tuple(episode(index, 100 + index, length=32) for index in range(9))
        weak_summary = feasibility.horizon_capacity_summary(weak, required_cases=256, minimum_distinct_episodes=10)
        self.assertFalse(weak_summary["5"]["feasible"])
        self.assertFalse(weak_summary["5"]["meets_cluster_requirement"])

    def test_source_report_marks_feasible_pool(self):
        episodes = {index: episode(index, index, length=32) for index in range(18)}
        episodes[2] = episode(2, 0, length=32)
        source = split((0, 1), (2,), (3,), episodes)
        report = feasibility.source_feasibility_report("bridge-real-20260827-001", source, intake(episodes))
        self.assertTrue(report["candidate_eligible_for_h1_h2_h5"])
        self.assertEqual(report["strict_target_pool_task_overlap_with_source_train_count"], 0)
        self.assertEqual(report["strict_target_pool_selected_episode_overlap_count"], 0)

    def test_output_boundary_and_candidate_order_are_fixed(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(feasibility, "ROOT", Path(temporary)):
                with self.assertRaisesRegex(feasibility.TaskDisjointFeasibilityError, "ordered predeclared"):
                    feasibility.evaluate_task_disjoint_feasibility(
                        ("bridge-real-20260827-002", "bridge-real-20260827-001"),
                        output_dir=Path(temporary) / "evaluation" / "bridgedata_task_disjoint_feasibility" / "fixture",
                    )
                with self.assertRaisesRegex(feasibility.TaskDisjointFeasibilityError, "ignored local evaluation root"):
                    feasibility.evaluate_task_disjoint_feasibility(
                        ("bridge-real-20260827-001", "bridge-real-20260827-002"),
                        output_dir=Path(temporary) / "outside",
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
