from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import evaluate_bridgedata_strict_task_cross_rollout as strict  # noqa: E402
from real_data.bridgedata_transitions import EpisodeTask  # noqa: E402


class FakeSplit:
    def __init__(self, episodes: dict[str, tuple[int, ...]], tasks: dict[str, tuple[int, ...]]):
        self._episodes = episodes
        self._tasks = tasks

    def episode_indices(self, name: str) -> tuple[int, ...]:
        return self._episodes[name]

    def task_indices(self, name: str) -> tuple[int, ...]:
        return self._tasks[name]


def episode(index: int, task: int) -> EpisodeTask:
    return EpisodeTask(
        episode_index=index,
        task_index=task,
        task=f"task-{task}",
        length=20,
        dataset_from_index=index * 20,
        dataset_to_index=index * 20 + 19,
    )


class StrictTaskCrossRolloutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.split = FakeSplit(
            {"train": (1, 2), "held_out_episode": (3,), "held_out_task": (4,)},
            {"train": (10,), "held_out_episode": (11,), "held_out_task": (12,)},
        )
        self.pool = tuple(episode(100 + index, 1000 + index) for index in range(20))

    def test_strict_target_selection_is_deterministic_and_disjoint(self):
        with patch.object(strict, "task_disjoint_episode_pool", return_value=self.pool):
            first = strict.select_strict_target_episodes("bridge-real-20260827-001", self.split, {}, episode_budget=12)
            second = strict.select_strict_target_episodes("bridge-real-20260827-001", self.split, {}, episode_budget=12)
        self.assertEqual(first, second)
        selected_episodes = {item.episode_index for item in first}
        selected_tasks = {item.task_index for item in first}
        self.assertEqual(len(selected_episodes), 12)
        self.assertFalse(selected_episodes & {1, 2, 3, 4})
        self.assertFalse(selected_tasks & {10})

    def test_strict_target_selection_refuses_source_task_overlap(self):
        bad_pool = tuple(list(self.pool[:11]) + [episode(199, 10)])
        with patch.object(strict, "task_disjoint_episode_pool", return_value=bad_pool):
            with self.assertRaisesRegex(strict.StrictTaskCrossRolloutError, "source-train tasks"):
                strict.select_strict_target_episodes("bridge-real-20260827-001", self.split, {}, episode_budget=12)

    def test_strict_target_selection_refuses_source_episode_overlap(self):
        bad_pool = tuple(list(self.pool[:11]) + [episode(1, 1999)])
        with patch.object(strict, "task_disjoint_episode_pool", return_value=bad_pool):
            with self.assertRaisesRegex(strict.StrictTaskCrossRolloutError, "source-selected episodes"):
                strict.select_strict_target_episodes("bridge-real-20260827-001", self.split, {}, episode_budget=12)

    def test_feasibility_receipt_requires_hash_and_no_mutation_flags(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "feasibility.json"
            payload = {
                "candidate_ids": list(strict.EXPECTED_CANDIDATE_IDS),
                "no_training": True,
                "no_candidate_creation": True,
                "no_checkpoint_mutation": True,
                "promotion_performed": False,
            }
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with patch.object(strict, "FEASIBILITY_RECEIPT_SHA256", digest):
                self.assertEqual(strict._load_feasibility_receipt(path)["candidate_ids"], list(strict.EXPECTED_CANDIDATE_IDS))
                path.write_text(json.dumps(dict(payload, no_training=False), sort_keys=True), encoding="utf-8")
                with self.assertRaisesRegex(strict.StrictTaskCrossRolloutError, "SHA-256 drifted"):
                    strict._load_feasibility_receipt(path)

    def test_order_and_output_boundary_refuse_before_loading_candidates(self):
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary) / "outside"
            with self.assertRaisesRegex(strict.StrictTaskCrossRolloutError, "ordered candidates"):
                strict.evaluate_strict_task_disjoint_cross_rollouts(tuple(reversed(strict.EXPECTED_CANDIDATE_IDS)), output_dir=outside)
            with self.assertRaisesRegex(strict.StrictTaskCrossRolloutError, "ignored local evaluation root"):
                strict.evaluate_strict_task_disjoint_cross_rollouts(strict.EXPECTED_CANDIDATE_IDS, output_dir=outside)


if __name__ == "__main__":
    unittest.main(verbosity=2)
