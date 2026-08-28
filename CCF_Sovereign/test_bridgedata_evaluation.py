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
    ActionOnlyMeanDeltaBaseline,
    BridgeDataEvaluationError,
    BridgeDataSplitConfig,
    CopyStateBaseline,
    LinearStateActionDeltaBaseline,
    NearestTrainStateActionBaseline,
    allocate_bridgedata_replication_split,
    allocate_bridgedata_split,
    baseline_predictions,
    bound_split_by_complete_episodes,
    score_bridgedata_predictions,
    transitions_by_split,
    validate_bridgedata_split,
)
from real_data.bridgedata_transitions import BridgeDataTransition, EpisodeTask  # noqa: E402


def vec(seed: float) -> tuple[float, ...]:
    return tuple(seed + dimension * 0.01 for dimension in range(7))


def episode(episode_index: int, task_index: int, *, length: int = 4) -> EpisodeTask:
    return EpisodeTask(
        episode_index=episode_index,
        task_index=task_index,
        task=f"task-{task_index}",
        length=length,
        dataset_from_index=episode_index * length,
        dataset_to_index=(episode_index + 1) * length,
    )


def transition_for(episode_item: EpisodeTask, step: int) -> BridgeDataTransition:
    source_index = episode_item.dataset_from_index + step
    source_state = vec(float(episode_item.episode_index * 10 + step))
    action = vec(float(episode_item.task_index) / 10 + step / 100)
    delta = tuple(0.1 * (dimension + 1) + action[dimension] * 0.01 for dimension in range(7))
    return BridgeDataTransition(
        transition_id=f"e{episode_item.episode_index}-s{step}",
        episode_index=episode_item.episode_index,
        task_index=int(episode_item.task_index),
        task=str(episode_item.task),
        source_index=source_index,
        target_index=source_index + 1,
        source_frame_index=step,
        target_frame_index=step + 1,
        source_timestamp=step * 0.2,
        target_timestamp=(step + 1) * 0.2,
        state_t=source_state,
        action_t=action,
        state_t_plus_1=tuple(value + offset for value, offset in zip(source_state, delta)),
    )


class BridgeDataEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.episodes = {
            0: episode(0, 0),
            1: episode(1, 0),
            2: episode(2, 1),
            3: episode(3, 1),
            4: episode(4, 2),
            5: episode(5, 2),
            6: EpisodeTask(
                episode_index=6,
                task_index=None,
                task=None,
                length=4,
                dataset_from_index=24,
                dataset_to_index=28,
            ),
        }
        self.config = BridgeDataSplitConfig(
            seed=71,
            held_out_task_fraction=0.2,
            held_out_episode_fraction=0.2,
        )

    def _all_transitions(self):
        return tuple(
            transition_for(item, step)
            for item in self.episodes.values()
            if item.task_index is not None
            for step in range(item.length - 1)
        )

    def test_group_allocation_is_deterministic_and_prevents_episode_or_task_leakage(self):
        first = allocate_bridgedata_split(self.episodes, self.config)
        second = allocate_bridgedata_split(self.episodes, self.config)

        self.assertEqual(first, second)
        self.assertEqual(first.excluded_unmapped_episode_indices, (6,))
        validate_bridgedata_split(first, self.episodes)
        train_episodes = set(first.train_episode_indices)
        episode_holdout = set(first.held_out_episode_indices)
        task_holdout = set(first.held_out_task_episode_indices)
        self.assertFalse(train_episodes & episode_holdout)
        self.assertFalse(train_episodes & task_holdout)
        self.assertFalse(episode_holdout & task_holdout)
        self.assertFalse(set(first.train_task_indices) & set(first.held_out_task_indices))
        self.assertFalse(set(first.held_out_episode_task_indices) & set(first.held_out_task_indices))
        self.assertTrue(set(first.held_out_episode_task_indices) <= set(first.train_task_indices))

    def test_complete_episode_budget_is_applied_only_after_group_split(self):
        split = allocate_bridgedata_split(self.episodes, self.config)
        bounded = bound_split_by_complete_episodes(
            split,
            self.episodes,
            max_transitions_by_split={
                TRAIN_SPLIT: 6,
                HELD_OUT_EPISODE_SPLIT: 3,
                HELD_OUT_TASK_SPLIT: 3,
            },
        )

        validate_bridgedata_split(bounded, self.episodes)
        self.assertTrue(bounded.excluded_by_budget_episode_indices)
        self.assertTrue(
            all(count <= {TRAIN_SPLIT: 6, HELD_OUT_EPISODE_SPLIT: 3, HELD_OUT_TASK_SPLIT: 3}[name]
                for name, count in bounded.expected_transition_counts.items())
        )
        self.assertFalse(set(bounded.train_task_indices) & set(bounded.held_out_task_indices))

    def test_replication_allocation_excludes_all_prior_selected_episodes(self):
        expanded = {
            index: episode(index, index // 2)
            for index in range(18)
        }
        prior_full = allocate_bridgedata_split(
            expanded,
            BridgeDataSplitConfig(seed=71, held_out_task_fraction=0.15, held_out_episode_fraction=0.15),
        )
        prior_bounded = bound_split_by_complete_episodes(
            prior_full,
            expanded,
            max_transitions_by_split={
                TRAIN_SPLIT: 9,
                HELD_OUT_EPISODE_SPLIT: 3,
                HELD_OUT_TASK_SPLIT: 3,
            },
        )
        reserved = set().union(
            prior_bounded.train_episode_indices,
            prior_bounded.held_out_episode_indices,
            prior_bounded.held_out_task_episode_indices,
        )
        replication = allocate_bridgedata_replication_split(
            expanded,
            BridgeDataSplitConfig(seed=87, held_out_task_fraction=0.15, held_out_episode_fraction=0.15),
            reserved_episode_indices=reserved,
        )

        validate_bridgedata_split(replication, expanded)
        replication_selected = set().union(
            replication.train_episode_indices,
            replication.held_out_episode_indices,
            replication.held_out_task_episode_indices,
        )
        self.assertFalse(reserved & replication_selected)
        self.assertTrue(reserved <= set(replication.excluded_by_budget_episode_indices))
        self.assertFalse(set(replication.train_task_indices) & set(replication.held_out_task_indices))
        self.assertFalse(
            set(replication.held_out_episode_task_indices)
            & set(replication.held_out_task_indices)
        )

    def test_replication_allocation_rejects_unknown_or_empty_reservation(self):
        with self.assertRaisesRegex(BridgeDataEvaluationError, "requires at least one"):
            allocate_bridgedata_replication_split(self.episodes, self.config, reserved_episode_indices=())
        with self.assertRaisesRegex(BridgeDataEvaluationError, "not an eligible mapped"):
            allocate_bridgedata_replication_split(self.episodes, self.config, reserved_episode_indices=(999,))

    def test_transition_partition_requires_exact_predeclared_coverage(self):
        split = allocate_bridgedata_split(self.episodes, self.config)
        partitions = transitions_by_split(self._all_transitions(), split)

        self.assertEqual(
            {name: len(items) for name, items in partitions.items()},
            split.expected_transition_counts,
        )
        with self.assertRaisesRegex(BridgeDataEvaluationError, "coverage disagrees"):
            transitions_by_split(self._all_transitions()[:-1], split)

    def test_baselines_are_train_only_and_score_exactly_each_partition(self):
        split = allocate_bridgedata_split(self.episodes, self.config)
        partitions = transitions_by_split(self._all_transitions(), split)
        train = partitions[TRAIN_SPLIT]
        baselines = (
            CopyStateBaseline(),
            ActionOnlyMeanDeltaBaseline.fit(train),
            LinearStateActionDeltaBaseline.fit(train),
            NearestTrainStateActionBaseline.fit(train),
        )
        expected_ids = {item.transition_id for values in partitions.values() for item in values}

        for baseline in baselines:
            predictions = baseline_predictions(baseline, partitions)
            self.assertEqual(set(predictions), expected_ids)
            report = score_bridgedata_predictions(
                partitions,
                predictions,
                split=split,
                prediction_label=baseline.label,
            )
            self.assertEqual(set(report.by_split), {TRAIN_SPLIT, HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT})
            self.assertTrue(all(metrics.coverage == 1.0 for metrics in report.by_split.values()))
            self.assertTrue(all(metrics.unknown_prediction_count == 0 for metrics in report.by_split.values()))
            self.assertTrue(all(metrics.excluded_transition_count == 0 for metrics in report.by_split.values()))
            self.assertTrue(all(len(metrics.dimension_rmse) == 7 for metrics in report.by_split.values()))
            self.assertTrue(all(len(metrics.dimension_mae) == 7 for metrics in report.by_split.values()))

    def test_mean_delta_is_fit_from_train_examples_only(self):
        left = transition_for(self.episodes[0], 0)
        right = transition_for(self.episodes[1], 0)
        baseline = ActionOnlyMeanDeltaBaseline.fit((left, right))
        expected = tuple(
            ((left.state_t_plus_1[index] - left.state_t[index]) + (right.state_t_plus_1[index] - right.state_t[index])) / 2
            for index in range(7)
        )

        self.assertEqual(baseline.mean_delta, expected)
        self.assertEqual(baseline.train_transition_ids, frozenset({left.transition_id, right.transition_id}))

    def test_linear_delta_baseline_learns_train_only_state_action_map(self):
        train = tuple(
            replace(
                transition_for(episode(index, index % 4, length=5), step),
                state_t_plus_1=tuple(
                    source
                    + 0.5
                    + source * 0.1
                    + action * 0.2
                    + dimension * 0.01
                    for dimension, (source, action) in enumerate(
                        zip(
                            transition_for(episode(index, index % 4, length=5), step).state_t,
                            transition_for(episode(index, index % 4, length=5), step).action_t,
                        )
                    )
                ),
            )
            for index in range(6)
            for step in range(3)
        )
        baseline = LinearStateActionDeltaBaseline.fit(train)
        predictions = baseline.predict(train[:3])
        for transition in train[:3]:
            self.assertEqual(predictions[transition.transition_id].transition_id, transition.transition_id)
            for predicted, expected in zip(
                predictions[transition.transition_id].state_t_plus_1,
                transition.state_t_plus_1,
            ):
                self.assertAlmostEqual(predicted, expected, places=10)

    def test_metric_coverage_is_fail_hard(self):
        split = allocate_bridgedata_split(self.episodes, self.config)
        partitions = transitions_by_split(self._all_transitions(), split)
        predictions = baseline_predictions(CopyStateBaseline(), partitions)
        predictions.pop(next(iter(predictions)))

        with self.assertRaisesRegex(BridgeDataEvaluationError, "coverage mismatch"):
            score_bridgedata_predictions(
                partitions,
                predictions,
                split=split,
                prediction_label="copy_state",
            )

    def test_task_leakage_is_rejected(self):
        split = allocate_bridgedata_split(self.episodes, self.config)
        leaked_episode = next(
            episode_index
            for episode_index in split.train_episode_indices
            if self.episodes[episode_index].task_index in set(split.held_out_task_indices)
        ) if any(
            self.episodes[episode_index].task_index in set(split.held_out_task_indices)
            for episode_index in split.train_episode_indices
        ) else split.train_episode_indices[0]
        corrupted = replace(
            split,
            held_out_task_episode_indices=tuple(sorted(set(split.held_out_task_episode_indices) | {leaked_episode})),
            train_episode_indices=tuple(item for item in split.train_episode_indices if item != leaked_episode),
            expected_transition_counts={
                TRAIN_SPLIT: sum(
                    max(0, self.episodes[item].length - 1)
                    for item in split.train_episode_indices if item != leaked_episode
                ),
                HELD_OUT_EPISODE_SPLIT: split.expected_transition_counts[HELD_OUT_EPISODE_SPLIT],
                HELD_OUT_TASK_SPLIT: split.expected_transition_counts[HELD_OUT_TASK_SPLIT] + self.episodes[leaked_episode].length - 1,
            },
        )

        with self.assertRaisesRegex(BridgeDataEvaluationError, "held-out task IDs disagree|held-out task leaked"):
            validate_bridgedata_split(corrupted, self.episodes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
