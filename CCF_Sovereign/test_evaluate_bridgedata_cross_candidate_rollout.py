from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import evaluate_bridgedata_cross_candidate_rollout as cross  # noqa: E402
from real_data.bridgedata_evaluation import (  # noqa: E402
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    BridgeDataSplit,
)
from real_data.bridgedata_transitions import BridgeDataTransition  # noqa: E402


def vector(value: float) -> tuple[float, ...]:
    return tuple(value for _ in range(7))


def transition(
    episode_index: int,
    source_index: int,
    *,
    task_index: int,
    step_size: float,
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


def split(
    train_episode: int,
    held_episode: int,
    held_task_episode: int,
    *,
    train_task: int,
    held_task: int,
) -> BridgeDataSplit:
    return BridgeDataSplit(
        split_version=1,
        config={"seed": train_episode},
        train_episode_indices=(train_episode,),
        held_out_episode_indices=(held_episode,),
        held_out_task_episode_indices=(held_task_episode,),
        train_task_indices=(train_task,),
        held_out_episode_task_indices=(train_task,),
        held_out_task_indices=(held_task,),
        excluded_unmapped_episode_indices=(),
        excluded_by_budget_episode_indices=(),
        expected_transition_counts={
            TRAIN_SPLIT: 12,
            HELD_OUT_EPISODE_SPLIT: 12,
            HELD_OUT_TASK_SPLIT: 12,
        },
    )


def frozen(candidate_id: str, *, base_episode: int, train_task: int, held_task: int, step_size: float) -> dict:
    train_episode = base_episode
    held_episode = base_episode + 10
    strict_episode = base_episode + 20

    def perfect_predictor(state: tuple[float, ...], action: tuple[float, ...]) -> tuple[float, ...]:
        return tuple(value + delta for value, delta in zip(state, action))

    return {
        "candidate_id": candidate_id,
        "split": split(
            train_episode,
            held_episode,
            strict_episode,
            train_task=train_task,
            held_task=held_task,
        ),
        "partitioned_transitions": {
            TRAIN_SPLIT: tuple(
                transition(train_episode, index, task_index=train_task, step_size=step_size)
                for index in range(12)
            ),
            HELD_OUT_EPISODE_SPLIT: tuple(
                transition(held_episode, index, task_index=train_task, step_size=step_size)
                for index in range(12)
            ),
            HELD_OUT_TASK_SPLIT: tuple(
                transition(strict_episode, index, task_index=held_task, step_size=step_size)
                for index in range(12)
            ),
        },
        "model_predictor": perfect_predictor,
    }


class CrossCandidateRolloutTests(unittest.TestCase):
    def test_source_selected_episode_overlap_is_rejected(self):
        source = frozen("bridge-real-20260827-001", base_episode=10, train_task=1, held_task=2, step_size=0.1)
        target = frozen("bridge-real-20260827-002", base_episode=20, train_task=3, held_task=4, step_size=0.2)
        with self.assertRaisesRegex(cross.FrozenRolloutEvidenceError, "source selected episodes overlap"):
            cross.cross_partitioned_transitions(source, target)

    def test_task_overlap_is_reported_without_relabeling_strictness(self):
        source = frozen("bridge-real-20260827-001", base_episode=10, train_task=4, held_task=5, step_size=0.1)
        target = frozen("bridge-real-20260827-002", base_episode=100, train_task=6, held_task=4, step_size=0.2)
        report = cross.cross_semantics_report(source, target)
        strict = report[HELD_OUT_TASK_SPLIT]
        self.assertEqual(strict["source_train_task_overlap_indices"], [4])
        self.assertFalse(strict["strict_unseen_task_relative_to_source_train"])

    def test_cross_evaluation_writes_no_mutation_receipt_and_accepts_ordered_candidates(self):
        candidate_001 = frozen("bridge-real-20260827-001", base_episode=10, train_task=1, held_task=2, step_size=0.1)
        candidate_002 = frozen("bridge-real-20260827-002", base_episode=100, train_task=3, held_task=4, step_size=0.2)

        def fake_loader(candidate_id: str, *, device):
            return {
                "bridge-real-20260827-001": candidate_001,
                "bridge-real-20260827-002": candidate_002,
            }[candidate_id]

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_dir = root / "evaluation" / "bridgedata_cross_rollouts" / "fixture"
            with (
                patch.object(cross, "ROOT", root),
                patch.object(cross, "load_frozen_rollout_candidate", fake_loader),
            ):
                payload = cross.evaluate_cross_candidates(
                    ("bridge-real-20260827-001", "bridge-real-20260827-002"),
                    output_dir=output_dir,
                    device_name="cpu",
                )
        self.assertTrue(payload["no_training"])
        self.assertFalse(payload["promotion_performed"])
        self.assertEqual(set(payload["cross_pairs"]), {
            "bridge-real-20260827-001_on_bridge-real-20260827-002",
            "bridge-real-20260827-002_on_bridge-real-20260827-001",
        })
        self.assertTrue(
            payload["cross_pairs"]["bridge-real-20260827-001_on_bridge-real-20260827-002"]["acceptance"]["passed"]
        )
        self.assertIn("payload_sha256", payload)

    def test_candidate_order_is_fixed(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(cross.FrozenRolloutEvidenceError, "ordered predeclared"):
                cross.evaluate_cross_candidates(
                    ("bridge-real-20260827-002", "bridge-real-20260827-001"),
                    output_dir=Path(temporary) / "evaluation" / "bridgedata_cross_rollouts" / "fixture",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
