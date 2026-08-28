"""Leakage-safe BridgeData partitions, explicit baselines, and vector metrics.

The functions in this module operate only on verified observed transitions from
``bridgedata_transitions``.  Partition allocation happens before extraction and
uses whole episodes and declared task identities, never random frames.  Baseline
fitting sees only the training partition.  Metrics require exact prediction
coverage and report each protected partition separately; no pooled held-out
headline is produced.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .bridgedata_transitions import (
    STATE_DIMENSIONS,
    BridgeDataError,
    BridgeDataTransition,
    EpisodeTask,
)


BRIDGEDATA_EVALUATION_VERSION = 1
TRAIN_SPLIT = "train"
HELD_OUT_EPISODE_SPLIT = "held_out_episode"
HELD_OUT_TASK_SPLIT = "held_out_task"
REQUIRED_SPLITS = (TRAIN_SPLIT, HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT)


class BridgeDataEvaluationError(ValueError):
    """Raised for an invalid split, baseline fit, or prediction report."""


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _finite_vector(value: Sequence[float], label: str) -> tuple[float, ...]:
    if len(value) != STATE_DIMENSIONS:
        raise BridgeDataEvaluationError(
            f"{label} must have exactly {STATE_DIMENSIONS} dimensions"
        )
    result = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in result):
        raise BridgeDataEvaluationError(f"{label} must contain only finite values")
    return result


def _stable_order_key(seed: int, prefix: str, value: int) -> tuple[str, int]:
    digest = hashlib.sha256(f"{seed}:{prefix}:{value}".encode("ascii")).hexdigest()
    return digest, value


def _transition_capacity(episode: EpisodeTask) -> int:
    return max(0, episode.length - 1)


@dataclass(frozen=True)
class BridgeDataSplitConfig:
    """Predeclared deterministic whole-group allocation ratios."""

    seed: int = 20_260_827
    held_out_task_fraction: float = 0.15
    held_out_episode_fraction: float = 0.15

    def validate(self) -> None:
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise BridgeDataEvaluationError("seed must be an integer")
        for name, value in (
            ("held_out_task_fraction", self.held_out_task_fraction),
            ("held_out_episode_fraction", self.held_out_episode_fraction),
        ):
            if not math.isfinite(value) or not 0 < value < 0.5:
                raise BridgeDataEvaluationError(f"{name} must be finite and in (0, 0.5)")


@dataclass(frozen=True)
class BridgeDataSplit:
    """Immutable explicit episode/task partition allocation before extraction."""

    split_version: int
    config: dict[str, Any]
    train_episode_indices: tuple[int, ...]
    held_out_episode_indices: tuple[int, ...]
    held_out_task_episode_indices: tuple[int, ...]
    train_task_indices: tuple[int, ...]
    held_out_episode_task_indices: tuple[int, ...]
    held_out_task_indices: tuple[int, ...]
    excluded_unmapped_episode_indices: tuple[int, ...]
    excluded_by_budget_episode_indices: tuple[int, ...]
    expected_transition_counts: dict[str, int]

    def episode_indices(self, split: str) -> tuple[int, ...]:
        if split == TRAIN_SPLIT:
            return self.train_episode_indices
        if split == HELD_OUT_EPISODE_SPLIT:
            return self.held_out_episode_indices
        if split == HELD_OUT_TASK_SPLIT:
            return self.held_out_task_episode_indices
        raise BridgeDataEvaluationError(f"unknown split: {split}")

    def task_indices(self, split: str) -> tuple[int, ...]:
        if split == TRAIN_SPLIT:
            return self.train_task_indices
        if split == HELD_OUT_EPISODE_SPLIT:
            return self.held_out_episode_task_indices
        if split == HELD_OUT_TASK_SPLIT:
            return self.held_out_task_indices
        raise BridgeDataEvaluationError(f"unknown split: {split}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return _canonical_json(self.to_dict())

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _eligible_episodes(
    episodes: Mapping[int, EpisodeTask],
) -> tuple[dict[int, EpisodeTask], tuple[int, ...]]:
    eligible: dict[int, EpisodeTask] = {}
    excluded: list[int] = []
    for episode_index, episode in sorted(episodes.items()):
        if episode.episode_index != episode_index:
            raise BridgeDataEvaluationError("episode mapping key disagrees with EpisodeTask")
        episode.validate()
        if episode.task_index is None or not episode.task:
            excluded.append(episode_index)
            continue
        if _transition_capacity(episode) < 1:
            excluded.append(episode_index)
            continue
        eligible[episode_index] = episode
    if not eligible:
        raise BridgeDataEvaluationError("no mapped episodes with at least one transition are eligible")
    return eligible, tuple(excluded)


def _choose_group_holdout(
    groups: Mapping[int, tuple[EpisodeTask, ...]],
    *,
    seed: int,
    fraction: float,
) -> set[int]:
    """Choose whole task groups near a transition-weighted target deterministically."""

    total_capacity = sum(_transition_capacity(item) for values in groups.values() for item in values)
    target = max(1, round(total_capacity * fraction))
    selected: set[int] = set()
    accumulated = 0
    for task_index in sorted(groups, key=lambda value: _stable_order_key(seed, "task", value)):
        group_capacity = sum(_transition_capacity(item) for item in groups[task_index])
        if accumulated == 0 or abs((accumulated + group_capacity) - target) <= abs(accumulated - target):
            selected.add(task_index)
            accumulated += group_capacity
        if accumulated >= target:
            break
    if not selected or len(selected) == len(groups):
        raise BridgeDataEvaluationError("unable to reserve a non-empty strict task holdout")
    return selected


def allocate_bridgedata_split(
    episodes: Mapping[int, EpisodeTask],
    config: BridgeDataSplitConfig = BridgeDataSplitConfig(),
) -> BridgeDataSplit:
    """Allocate whole episodes and wholly unseen task identities deterministically.

    ``held_out_task`` contains all eligible episodes for assigned task IDs; none
    of those IDs may occur in train or ``held_out_episode``.  ``held_out_episode``
    contains whole episodes from task IDs that retain at least one separate train
    episode, giving an explicit familiar-task, unseen-episode partition.
    """

    config.validate()
    eligible, excluded = _eligible_episodes(episodes)
    by_task: dict[int, list[EpisodeTask]] = defaultdict(list)
    for episode in eligible.values():
        assert episode.task_index is not None
        by_task[episode.task_index].append(episode)
    groups = {task: tuple(sorted(values, key=lambda item: item.episode_index)) for task, values in by_task.items()}
    if len(groups) < 2:
        raise BridgeDataEvaluationError("at least two task identities are required for a strict task holdout")
    held_out_task_indices = _choose_group_holdout(
        groups,
        seed=config.seed,
        fraction=config.held_out_task_fraction,
    )
    held_out_task_episodes = {
        item.episode_index for task in held_out_task_indices for item in groups[task]
    }

    remaining_by_task = {
        task: values for task, values in groups.items() if task not in held_out_task_indices
    }
    episode_candidates = [
        item
        for task, values in remaining_by_task.items()
        if len(values) >= 2
        for item in values
    ]
    if not episode_candidates:
        raise BridgeDataEvaluationError(
            "no remaining task has at least two episodes for an unseen-episode holdout"
        )
    target_episode_capacity = max(
        1,
        round(sum(_transition_capacity(item) for item in eligible.values()) * config.held_out_episode_fraction),
    )
    retained_per_task = {task: len(values) for task, values in remaining_by_task.items()}
    held_out_episode_episodes: set[int] = set()
    accumulated_episode_capacity = 0
    for episode in sorted(
        episode_candidates,
        key=lambda item: _stable_order_key(config.seed, "episode", item.episode_index),
    ):
        assert episode.task_index is not None
        task_index = episode.task_index
        capacity = _transition_capacity(episode)
        if retained_per_task[task_index] <= 1:
            continue
        if accumulated_episode_capacity == 0 or abs(
            (accumulated_episode_capacity + capacity) - target_episode_capacity
        ) <= abs(accumulated_episode_capacity - target_episode_capacity):
            held_out_episode_episodes.add(episode.episode_index)
            retained_per_task[task_index] -= 1
            accumulated_episode_capacity += capacity
        if accumulated_episode_capacity >= target_episode_capacity:
            break
    if not held_out_episode_episodes:
        raise BridgeDataEvaluationError("unable to reserve a non-empty unseen-episode holdout")

    train_episodes = set(eligible) - held_out_task_episodes - held_out_episode_episodes
    if not train_episodes:
        raise BridgeDataEvaluationError("task and episode holdouts leave no training episodes")
    train_tasks = {eligible[item].task_index for item in train_episodes}
    episode_holdout_tasks = {eligible[item].task_index for item in held_out_episode_episodes}
    if None in train_tasks or None in episode_holdout_tasks:
        raise BridgeDataEvaluationError("eligible split includes an unmapped task")

    split = BridgeDataSplit(
        split_version=BRIDGEDATA_EVALUATION_VERSION,
        config=asdict(config),
        train_episode_indices=tuple(sorted(train_episodes)),
        held_out_episode_indices=tuple(sorted(held_out_episode_episodes)),
        held_out_task_episode_indices=tuple(sorted(held_out_task_episodes)),
        train_task_indices=tuple(sorted(int(item) for item in train_tasks)),
        held_out_episode_task_indices=tuple(sorted(int(item) for item in episode_holdout_tasks)),
        held_out_task_indices=tuple(sorted(held_out_task_indices)),
        excluded_unmapped_episode_indices=excluded,
        excluded_by_budget_episode_indices=(),
        expected_transition_counts={
            TRAIN_SPLIT: sum(_transition_capacity(eligible[item]) for item in train_episodes),
            HELD_OUT_EPISODE_SPLIT: sum(
                _transition_capacity(eligible[item]) for item in held_out_episode_episodes
            ),
            HELD_OUT_TASK_SPLIT: sum(
                _transition_capacity(eligible[item]) for item in held_out_task_episodes
            ),
        },
    )
    validate_bridgedata_split(split, episodes)
    return split


def allocate_bridgedata_replication_split(
    episodes: Mapping[int, EpisodeTask],
    config: BridgeDataSplitConfig,
    *,
    reserved_episode_indices: Iterable[int],
) -> BridgeDataSplit:
    """Allocate a fresh split after reserving complete prior-candidate episodes.

    Reserved episode identifiers must be mapped, eligible source episodes. They
    are removed *before* fresh strict task and unseen-episode allocation, then
    recorded in the returned split as explicit pre-existing budget exclusions.
    This prevents a replication candidate from seeing any transition selected
    by the prior candidate while retaining full-source coverage validation.
    """

    config.validate()
    eligible, unmapped = _eligible_episodes(episodes)
    reserved_values = tuple(sorted(reserved_episode_indices))
    if not reserved_values:
        raise BridgeDataEvaluationError("replication requires at least one reserved prior episode")
    if len(reserved_values) != len(set(reserved_values)):
        raise BridgeDataEvaluationError("reserved prior episode IDs must be unique")
    if any(isinstance(item, bool) or not isinstance(item, int) for item in reserved_values):
        raise BridgeDataEvaluationError("reserved prior episode IDs must be integers")
    unknown = set(reserved_values) - set(eligible)
    if unknown:
        raise BridgeDataEvaluationError(
            "reserved prior episode is not an eligible mapped source episode: "
            + ", ".join(str(item) for item in sorted(unknown)[:10])
        )
    available = {
        episode_index: item
        for episode_index, item in episodes.items()
        if episode_index not in set(reserved_values)
    }
    allocated = allocate_bridgedata_split(available, config)
    replication_split = replace(
        allocated,
        config={
            **allocated.config,
            "replication_reserved_episode_indices": list(reserved_values),
        },
        excluded_unmapped_episode_indices=unmapped,
        excluded_by_budget_episode_indices=reserved_values,
    )
    validate_bridgedata_split(replication_split, episodes)
    return replication_split


def validate_bridgedata_split(
    split: BridgeDataSplit,
    episodes: Mapping[int, EpisodeTask],
) -> None:
    """Prove whole-episode and strict task-holdout non-overlap before extraction."""

    if not isinstance(split, BridgeDataSplit):
        raise BridgeDataEvaluationError("split must be a BridgeDataSplit")
    eligible, expected_excluded = _eligible_episodes(episodes)
    partitions = {
        name: set(split.episode_indices(name))
        for name in REQUIRED_SPLITS
    }
    if any(not values for values in partitions.values()):
        raise BridgeDataEvaluationError("every required split must contain at least one whole episode")
    budget_excluded = set(split.excluded_by_budget_episode_indices)
    if budget_excluded & set().union(*partitions.values()):
        raise BridgeDataEvaluationError("budget-excluded episode appears in an evaluation partition")
    if set().union(*partitions.values()) | budget_excluded != set(eligible):
        raise BridgeDataEvaluationError("split episodes and budget exclusions do not exactly cover eligible mapped episodes")
    for first_index, first_name in enumerate(REQUIRED_SPLITS):
        for second_name in REQUIRED_SPLITS[first_index + 1:]:
            if partitions[first_name] & partitions[second_name]:
                raise BridgeDataEvaluationError("episode overlap exists between split partitions")
    if tuple(split.excluded_unmapped_episode_indices) != expected_excluded:
        raise BridgeDataEvaluationError("split excluded episode list disagrees with source metadata")
    task_sets = {
        name: {eligible[episode].task_index for episode in values}
        for name, values in partitions.items()
    }
    if None in task_sets[TRAIN_SPLIT] or None in task_sets[HELD_OUT_EPISODE_SPLIT] or None in task_sets[HELD_OUT_TASK_SPLIT]:
        raise BridgeDataEvaluationError("split contains an unmapped task")
    if task_sets[HELD_OUT_TASK_SPLIT] & task_sets[TRAIN_SPLIT]:
        raise BridgeDataEvaluationError("held-out task leaked into train")
    if task_sets[HELD_OUT_TASK_SPLIT] & task_sets[HELD_OUT_EPISODE_SPLIT]:
        raise BridgeDataEvaluationError("held-out task leaked into held-out episode partition")
    if not task_sets[HELD_OUT_EPISODE_SPLIT] <= task_sets[TRAIN_SPLIT]:
        raise BridgeDataEvaluationError(
            "unseen-episode partition must retain each task identity in training"
        )
    expected_counts = {
        name: sum(_transition_capacity(eligible[item]) for item in values)
        for name, values in partitions.items()
    }
    if split.expected_transition_counts != expected_counts:
        raise BridgeDataEvaluationError("split expected transition counts disagree with source metadata")
    declared_tasks = {
        name: tuple(sorted(int(item) for item in task_sets[name])) for name in REQUIRED_SPLITS
    }
    if declared_tasks[TRAIN_SPLIT] != split.train_task_indices:
        raise BridgeDataEvaluationError("train task IDs disagree with episode allocation")
    if declared_tasks[HELD_OUT_EPISODE_SPLIT] != split.held_out_episode_task_indices:
        raise BridgeDataEvaluationError("held-out episode task IDs disagree with episode allocation")
    if declared_tasks[HELD_OUT_TASK_SPLIT] != split.held_out_task_indices:
        raise BridgeDataEvaluationError("held-out task IDs disagree with episode allocation")


def transitions_by_split(
    transitions: Iterable[BridgeDataTransition], split: BridgeDataSplit
) -> dict[str, tuple[BridgeDataTransition, ...]]:
    """Partition verified transition records with exact expected coverage checks."""

    episode_to_split: dict[int, str] = {}
    for name in REQUIRED_SPLITS:
        for episode_index in split.episode_indices(name):
            if episode_index in episode_to_split:
                raise BridgeDataEvaluationError("split maps one episode to multiple partitions")
            episode_to_split[episode_index] = name
    grouped: dict[str, list[BridgeDataTransition]] = {name: [] for name in REQUIRED_SPLITS}
    seen_ids: set[str] = set()
    unknown_episode_count = 0
    for transition in transitions:
        transition.validate()
        if transition.transition_id in seen_ids:
            raise BridgeDataEvaluationError("duplicate transition_id in evaluation input")
        seen_ids.add(transition.transition_id)
        partition = episode_to_split.get(transition.episode_index)
        if partition is None:
            unknown_episode_count += 1
            continue
        grouped[partition].append(transition)
    if unknown_episode_count:
        raise BridgeDataEvaluationError("transition input contains episodes absent from the predeclared split")
    ordered = {
        name: tuple(sorted(values, key=lambda item: (item.episode_index, item.source_index)))
        for name, values in grouped.items()
    }
    actual_counts = {name: len(values) for name, values in ordered.items()}
    if actual_counts != split.expected_transition_counts:
        raise BridgeDataEvaluationError(
            "extracted transition coverage disagrees with the predeclared whole-episode split: "
            + _canonical_json(actual_counts)
        )
    return ordered


@dataclass(frozen=True)
class BridgeDataPrediction:
    """One exact-ID state prediction for an observed BridgeData transition."""

    transition_id: str
    state_t_plus_1: tuple[float, ...]

    def validate(self) -> None:
        if not self.transition_id:
            raise BridgeDataEvaluationError("prediction transition_id is required")
        _finite_vector(self.state_t_plus_1, "prediction state_t_plus_1")

    def to_dict(self) -> dict[str, Any]:
        return {"transition_id": self.transition_id, "state_t_plus_1": list(self.state_t_plus_1)}

    def canonical_json(self) -> str:
        return _canonical_json(self.to_dict())

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _prediction_map(
    predictions: Mapping[str, BridgeDataPrediction] | Iterable[BridgeDataPrediction],
) -> dict[str, BridgeDataPrediction]:
    if isinstance(predictions, Mapping):
        pairs = tuple((str(key), value) for key, value in predictions.items())
    else:
        pairs = tuple((item.transition_id, item) for item in predictions)
    resolved = dict(pairs)
    if not resolved:
        raise BridgeDataEvaluationError("at least one prediction is required")
    if len(resolved) != len(pairs):
        raise BridgeDataEvaluationError("prediction set contains duplicate IDs")
    for key, prediction in resolved.items():
        if not isinstance(prediction, BridgeDataPrediction):
            raise BridgeDataEvaluationError("prediction set contains a non-BridgeDataPrediction")
        prediction.validate()
        if key != prediction.transition_id:
            raise BridgeDataEvaluationError("prediction mapping key must equal transition_id")
    return resolved


def prediction_set_sha256(predictions: Mapping[str, BridgeDataPrediction]) -> str:
    payload = "\n".join(
        f"{identifier}:{prediction.sha256()}"
        for identifier, prediction in sorted(predictions.items())
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def transition_set_sha256(transitions: Iterable[BridgeDataTransition]) -> str:
    materialized = tuple(transitions)
    payload = "\n".join(
        f"{item.transition_id}:{item.sha256()}" for item in materialized
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


@dataclass(frozen=True)
class SplitVectorMetrics:
    """Exact-coverage 7D state/delta error measurements for one partition."""

    split: str
    cases: int
    predictions: int
    coverage: float
    unknown_prediction_count: int
    excluded_transition_count: int
    aggregate_rmse: float
    aggregate_mae: float
    delta_rmse: float
    dimension_rmse: tuple[float, ...]
    dimension_mae: tuple[float, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["dimension_rmse"] = list(self.dimension_rmse)
        payload["dimension_mae"] = list(self.dimension_mae)
        return payload


@dataclass(frozen=True)
class BridgeDataMetricsReport:
    """Per-partition only metrics for one baseline or candidate prediction set."""

    evaluation_version: int
    prediction_label: str
    split_sha256: str
    transition_set_sha256: str
    prediction_set_sha256: str
    excluded_unmapped_episode_count: int
    by_split: dict[str, SplitVectorMetrics]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_version": self.evaluation_version,
            "prediction_label": self.prediction_label,
            "split_sha256": self.split_sha256,
            "transition_set_sha256": self.transition_set_sha256,
            "prediction_set_sha256": self.prediction_set_sha256,
            "excluded_unmapped_episode_count": self.excluded_unmapped_episode_count,
            "by_split": {name: self.by_split[name].to_dict() for name in REQUIRED_SPLITS},
            "notes": list(self.notes),
        }

    def canonical_json(self) -> str:
        return _canonical_json(self.to_dict())

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def score_bridgedata_predictions(
    partitioned_transitions: Mapping[str, Sequence[BridgeDataTransition]],
    predictions: Mapping[str, BridgeDataPrediction] | Iterable[BridgeDataPrediction],
    *,
    split: BridgeDataSplit,
    prediction_label: str,
) -> BridgeDataMetricsReport:
    """Score exact-ID predictions separately for train and protected partitions."""

    if not prediction_label:
        raise BridgeDataEvaluationError("prediction_label is required")
    if set(partitioned_transitions) != set(REQUIRED_SPLITS):
        raise BridgeDataEvaluationError("partitioned transitions must contain exactly the required splits")
    expected: dict[str, BridgeDataTransition] = {}
    for name in REQUIRED_SPLITS:
        for transition in partitioned_transitions[name]:
            transition.validate()
            if transition.transition_id in expected:
                raise BridgeDataEvaluationError("transition appears in more than one score partition")
            expected[transition.transition_id] = transition
    resolved = _prediction_map(predictions)
    expected_ids = set(expected)
    observed_ids = set(resolved)
    if expected_ids != observed_ids:
        raise BridgeDataEvaluationError(
            "prediction coverage mismatch: "
            f"missing={len(expected_ids - observed_ids)}, extra={len(observed_ids - expected_ids)}"
        )
    by_split: dict[str, SplitVectorMetrics] = {}
    for name in REQUIRED_SPLITS:
        transitions = tuple(partitioned_transitions[name])
        if not transitions:
            raise BridgeDataEvaluationError(f"required split has no transitions: {name}")
        sum_squared = 0.0
        sum_absolute = 0.0
        dimension_squared = [0.0] * STATE_DIMENSIONS
        dimension_absolute = [0.0] * STATE_DIMENSIONS
        for transition in transitions:
            prediction = resolved[transition.transition_id]
            errors = tuple(
                predicted - target
                for predicted, target in zip(prediction.state_t_plus_1, transition.state_t_plus_1)
            )
            sum_squared += sum(value * value for value in errors)
            sum_absolute += sum(abs(value) for value in errors)
            for dimension, value in enumerate(errors):
                dimension_squared[dimension] += value * value
                dimension_absolute[dimension] += abs(value)
        cases = len(transitions)
        by_split[name] = SplitVectorMetrics(
            split=name,
            cases=cases,
            predictions=cases,
            coverage=1.0,
            unknown_prediction_count=0,
            excluded_transition_count=0,
            aggregate_rmse=math.sqrt(sum_squared / (cases * STATE_DIMENSIONS)),
            aggregate_mae=sum_absolute / (cases * STATE_DIMENSIONS),
            # state prediction error equals error on (state[t+1] - state[t])
            # because state[t] is a shared observed reference for this case.
            delta_rmse=math.sqrt(sum_squared / (cases * STATE_DIMENSIONS)),
            dimension_rmse=tuple(math.sqrt(value / cases) for value in dimension_squared),
            dimension_mae=tuple(value / cases for value in dimension_absolute),
        )
    all_transitions = tuple(
        transition for name in REQUIRED_SPLITS for transition in partitioned_transitions[name]
    )
    return BridgeDataMetricsReport(
        evaluation_version=BRIDGEDATA_EVALUATION_VERSION,
        prediction_label=prediction_label,
        split_sha256=split.sha256(),
        transition_set_sha256=transition_set_sha256(all_transitions),
        prediction_set_sha256=prediction_set_sha256(resolved),
        excluded_unmapped_episode_count=len(split.excluded_unmapped_episode_indices),
        by_split=by_split,
        notes=(
            "Each partition is reported separately; no pooled held-out score is emitted.",
            "All prediction IDs were required to match observed transition IDs exactly; unknown or excluded prediction coverage is zero.",
            "Delta RMSE is algebraically identical to state RMSE for this observed one-step task because state[t] is shared.",
            "This numeric report is neither robot-policy, safety, control, renderer, nor promotion evidence.",
        ),
    )


class CopyStateBaseline:
    """No-training current-state baseline."""

    label = "copy_state"

    def predict(self, transitions: Iterable[BridgeDataTransition]) -> dict[str, BridgeDataPrediction]:
        result: dict[str, BridgeDataPrediction] = {}
        for transition in transitions:
            transition.validate()
            if transition.transition_id in result:
                raise BridgeDataEvaluationError("duplicate transition in copy-state prediction input")
            result[transition.transition_id] = BridgeDataPrediction(
                transition_id=transition.transition_id,
                state_t_plus_1=transition.state_t,
            )
        return result


@dataclass(frozen=True)
class ActionOnlyMeanDeltaBaseline:
    """Immutable train-only action-independent mean-delta baseline."""

    mean_delta: tuple[float, ...]
    train_transition_ids: frozenset[str]
    label: str = "action_only_mean_delta"

    @classmethod
    def fit(cls, train_transitions: Iterable[BridgeDataTransition]) -> "ActionOnlyMeanDeltaBaseline":
        examples = tuple(train_transitions)
        if not examples:
            raise BridgeDataEvaluationError("mean-delta baseline requires non-empty train transitions")
        identifiers = [item.transition_id for item in examples]
        if len(identifiers) != len(set(identifiers)):
            raise BridgeDataEvaluationError("mean-delta baseline training has duplicate transition IDs")
        totals = [0.0] * STATE_DIMENSIONS
        for item in examples:
            item.validate()
            for dimension, (target, source) in enumerate(zip(item.state_t_plus_1, item.state_t)):
                totals[dimension] += target - source
        return cls(
            mean_delta=tuple(value / len(examples) for value in totals),
            train_transition_ids=frozenset(identifiers),
        )

    def predict(self, transitions: Iterable[BridgeDataTransition]) -> dict[str, BridgeDataPrediction]:
        result: dict[str, BridgeDataPrediction] = {}
        for transition in transitions:
            transition.validate()
            if transition.transition_id in result:
                raise BridgeDataEvaluationError("duplicate transition in mean-delta prediction input")
            result[transition.transition_id] = BridgeDataPrediction(
                transition_id=transition.transition_id,
                state_t_plus_1=tuple(
                    value + delta for value, delta in zip(transition.state_t, self.mean_delta)
                ),
            )
        return result


@dataclass(frozen=True)
class LinearStateActionDeltaBaseline:
    """Train-only ordinary least-squares delta predictor over state and action."""

    coefficients: tuple[tuple[float, ...], ...]
    train_transition_ids: tuple[str, ...]
    label: str = "linear_state_action_delta"

    @classmethod
    def fit(cls, train_transitions: Iterable[BridgeDataTransition]) -> "LinearStateActionDeltaBaseline":
        examples = tuple(train_transitions)
        if len(examples) < 2:
            raise BridgeDataEvaluationError("linear baseline requires at least two train transitions")
        identifiers = [item.transition_id for item in examples]
        if len(identifiers) != len(set(identifiers)):
            raise BridgeDataEvaluationError("linear baseline training has duplicate transition IDs")
        features = []
        deltas = []
        for item in examples:
            item.validate()
            features.append((1.0,) + item.state_t + item.action_t)
            deltas.append(tuple(target - source for target, source in zip(item.state_t_plus_1, item.state_t)))
        coefficients, *_ = np.linalg.lstsq(
            np.asarray(features, dtype=np.float64),
            np.asarray(deltas, dtype=np.float64),
            rcond=None,
        )
        if coefficients.shape != (STATE_DIMENSIONS * 2 + 1, STATE_DIMENSIONS):
            raise BridgeDataEvaluationError("linear baseline fit produced invalid coefficients")
        if not np.all(np.isfinite(coefficients)):
            raise BridgeDataEvaluationError("linear baseline fit produced non-finite coefficients")
        return cls(
            coefficients=tuple(tuple(float(value) for value in row) for row in coefficients),
            train_transition_ids=tuple(identifiers),
        )

    def predict(self, transitions: Iterable[BridgeDataTransition]) -> dict[str, BridgeDataPrediction]:
        examples = tuple(transitions)
        identifiers = [item.transition_id for item in examples]
        if len(identifiers) != len(set(identifiers)):
            raise BridgeDataEvaluationError("duplicate transition in linear prediction input")
        coefficients = np.asarray(self.coefficients, dtype=np.float64)
        if coefficients.shape != (STATE_DIMENSIONS * 2 + 1, STATE_DIMENSIONS):
            raise BridgeDataEvaluationError("linear baseline coefficients have invalid shape")
        result: dict[str, BridgeDataPrediction] = {}
        for transition in examples:
            transition.validate()
            feature = np.asarray((1.0,) + transition.state_t + transition.action_t, dtype=np.float64)
            delta = feature @ coefficients
            if not np.all(np.isfinite(delta)):
                raise BridgeDataEvaluationError("linear baseline emitted non-finite prediction")
            result[transition.transition_id] = BridgeDataPrediction(
                transition_id=transition.transition_id,
                state_t_plus_1=tuple(
                    float(value + offset)
                    for value, offset in zip(transition.state_t, delta)
                ),
            )
        return result


@dataclass(frozen=True)
class NearestTrainStateActionBaseline:
    """Train-only nearest-neighbor delta predictor in train-standardized 14D input space."""

    train_transition_ids: tuple[str, ...]
    normalized_features: tuple[tuple[float, ...], ...]
    target_deltas: tuple[tuple[float, ...], ...]
    feature_mean: tuple[float, ...]
    feature_scale: tuple[float, ...]
    label: str = "nearest_train_state_action"

    @classmethod
    def fit(cls, train_transitions: Iterable[BridgeDataTransition]) -> "NearestTrainStateActionBaseline":
        examples = tuple(train_transitions)
        if len(examples) < 2:
            raise BridgeDataEvaluationError("nearest-neighbor baseline requires at least two train transitions")
        identifiers = [item.transition_id for item in examples]
        if len(identifiers) != len(set(identifiers)):
            raise BridgeDataEvaluationError("nearest-neighbor baseline training has duplicate transition IDs")
        features = []
        deltas = []
        for item in examples:
            item.validate()
            features.append(item.state_t + item.action_t)
            deltas.append(tuple(target - source for target, source in zip(item.state_t_plus_1, item.state_t)))
        width = STATE_DIMENSIONS * 2
        means = tuple(sum(row[index] for row in features) / len(features) for index in range(width))
        scales = []
        for index, mean in enumerate(means):
            variance = sum((row[index] - mean) ** 2 for row in features) / len(features)
            scales.append(max(math.sqrt(variance), 1e-8))
        normalized = tuple(
            tuple((value - mean) / scale for value, mean, scale in zip(row, means, scales))
            for row in features
        )
        return cls(
            train_transition_ids=tuple(identifiers),
            normalized_features=normalized,
            target_deltas=tuple(deltas),
            feature_mean=means,
            feature_scale=tuple(scales),
        )

    def predict(
        self,
        transitions: Iterable[BridgeDataTransition],
        *,
        leave_one_out_for_train: bool = True,
    ) -> dict[str, BridgeDataPrediction]:
        """Return exact-ID predictions using only the fitted train feature bank.

        Distance evaluation is NumPy-vectorized in fixed query batches. This is
        an implementation detail only: the stored bank, standardization, and
        leave-one-out exclusion remain strictly train-derived and deterministic.
        """

        try:
            import numpy as np
        except ImportError as error:
            raise BridgeDataEvaluationError("numpy is required for nearest-neighbor evaluation") from error
        examples = tuple(transitions)
        identifiers = [item.transition_id for item in examples]
        if len(identifiers) != len(set(identifiers)):
            raise BridgeDataEvaluationError("duplicate transition in nearest-neighbor prediction input")
        for transition in examples:
            transition.validate()
        train_features = np.asarray(self.normalized_features, dtype=np.float64)
        deltas = np.asarray(self.target_deltas, dtype=np.float64)
        means = np.asarray(self.feature_mean, dtype=np.float64)
        scales = np.asarray(self.feature_scale, dtype=np.float64)
        query_features = np.asarray(
            [item.state_t + item.action_t for item in examples], dtype=np.float64
        )
        queries = (query_features - means) / scales
        query_squares = np.sum(queries * queries, axis=1)
        train_squares = np.sum(train_features * train_features, axis=1)
        index_by_id = {identifier: index for index, identifier in enumerate(self.train_transition_ids)}
        nearest_indices = np.empty(len(examples), dtype=np.int64)
        batch_size = 512
        for start in range(0, len(examples), batch_size):
            stop = min(start + batch_size, len(examples))
            distances = (
                query_squares[start:stop, None]
                + train_squares[None, :]
                - 2.0 * queries[start:stop] @ train_features.T
            )
            if leave_one_out_for_train:
                for local_index, transition_id in enumerate(identifiers[start:stop]):
                    excluded_index = index_by_id.get(transition_id)
                    if excluded_index is not None:
                        distances[local_index, excluded_index] = np.inf
            best = np.argmin(distances, axis=1)
            if not np.all(np.isfinite(distances[np.arange(stop - start), best])):
                raise BridgeDataEvaluationError("nearest-neighbor baseline has no eligible train neighbor")
            nearest_indices[start:stop] = best
        result: dict[str, BridgeDataPrediction] = {}
        for transition, nearest_index in zip(examples, nearest_indices):
            delta = deltas[int(nearest_index)]
            result[transition.transition_id] = BridgeDataPrediction(
                transition_id=transition.transition_id,
                state_t_plus_1=tuple(
                    float(value + offset)
                    for value, offset in zip(transition.state_t, delta)
                ),
            )
        return result


def baseline_predictions(
    baseline: (
        CopyStateBaseline
        | ActionOnlyMeanDeltaBaseline
        | LinearStateActionDeltaBaseline
        | NearestTrainStateActionBaseline
    ),
    partitioned_transitions: Mapping[str, Sequence[BridgeDataTransition]],
) -> dict[str, BridgeDataPrediction]:
    """Predict every required partition with a train-fitted baseline exactly once."""

    if set(partitioned_transitions) != set(REQUIRED_SPLITS):
        raise BridgeDataEvaluationError("baseline input must contain exactly the required splits")
    all_transitions = tuple(
        transition for name in REQUIRED_SPLITS for transition in partitioned_transitions[name]
    )
    if isinstance(baseline, NearestTrainStateActionBaseline):
        return baseline.predict(all_transitions, leave_one_out_for_train=True)
    return baseline.predict(all_transitions)


def _budgeted_episode_selection(
    candidates: Iterable[int],
    episodes: Mapping[int, EpisodeTask],
    *,
    seed: int,
    split_name: str,
    maximum_transitions: int,
    required_episode_indices: Iterable[int] = (),
) -> set[int]:
    """Select whole episodes within a stated transition budget deterministically."""

    if isinstance(maximum_transitions, bool) or not isinstance(maximum_transitions, int):
        raise BridgeDataEvaluationError("per-split transition budget must be an integer")
    if maximum_transitions < 1:
        raise BridgeDataEvaluationError("per-split transition budget must be positive")
    candidate_set = set(candidates)
    required = set(required_episode_indices)
    if not required <= candidate_set:
        raise BridgeDataEvaluationError("required train anchor is absent from candidate episodes")
    selected: set[int] = set()
    used = 0
    for episode_index in sorted(required, key=lambda item: _stable_order_key(seed, split_name, item)):
        capacity = _transition_capacity(episodes[episode_index])
        if used + capacity > maximum_transitions:
            raise BridgeDataEvaluationError(
                f"{split_name} budget cannot retain required whole-episode task anchors"
            )
        selected.add(episode_index)
        used += capacity
    for episode_index in sorted(candidate_set - required, key=lambda item: _stable_order_key(seed, split_name, item)):
        capacity = _transition_capacity(episodes[episode_index])
        if used + capacity <= maximum_transitions:
            selected.add(episode_index)
            used += capacity
    if not selected:
        raise BridgeDataEvaluationError(
            f"{split_name} budget cannot retain any complete episode"
        )
    return selected


def bound_split_by_complete_episodes(
    split: BridgeDataSplit,
    episodes: Mapping[int, EpisodeTask],
    *,
    max_transitions_by_split: Mapping[str, int],
) -> BridgeDataSplit:
    """Reduce a predeclared split by whole episodes only, after allocation.

    This does not sample frames.  It leaves the original unmapped exclusions
    intact and records every otherwise eligible episode omitted solely to meet
    the externally declared local experiment budget.  The returned partition
    maintains the original strict held-out-task disjointness and retains a
    deterministic train anchor for every familiar task used in the held-out
    episode partition.
    """

    validate_bridgedata_split(split, episodes)
    if set(max_transitions_by_split) != set(REQUIRED_SPLITS):
        raise BridgeDataEvaluationError("budget must define exactly the required splits")
    eligible, _ = _eligible_episodes(episodes)
    seed = int(split.config["seed"])
    episode_holdout_selected = _budgeted_episode_selection(
        split.held_out_episode_indices,
        eligible,
        seed=seed,
        split_name=HELD_OUT_EPISODE_SPLIT,
        maximum_transitions=max_transitions_by_split[HELD_OUT_EPISODE_SPLIT],
    )
    required_train_tasks = {eligible[item].task_index for item in episode_holdout_selected}
    train_anchors: set[int] = set()
    for task_index in sorted(int(item) for item in required_train_tasks if item is not None):
        choices = [
            item
            for item in split.train_episode_indices
            if eligible[item].task_index == task_index
        ]
        if not choices:
            raise BridgeDataEvaluationError(
                "held-out episode task has no train episode available for bounded anchor"
            )
        train_anchors.add(
            min(choices, key=lambda item: _stable_order_key(seed, TRAIN_SPLIT, item))
        )
    train_selected = _budgeted_episode_selection(
        split.train_episode_indices,
        eligible,
        seed=seed,
        split_name=TRAIN_SPLIT,
        maximum_transitions=max_transitions_by_split[TRAIN_SPLIT],
        required_episode_indices=train_anchors,
    )
    task_holdout_selected = _budgeted_episode_selection(
        split.held_out_task_episode_indices,
        eligible,
        seed=seed,
        split_name=HELD_OUT_TASK_SPLIT,
        maximum_transitions=max_transitions_by_split[HELD_OUT_TASK_SPLIT],
    )

    partition_sets = {
        TRAIN_SPLIT: train_selected,
        HELD_OUT_EPISODE_SPLIT: episode_holdout_selected,
        HELD_OUT_TASK_SPLIT: task_holdout_selected,
    }
    task_sets = {
        name: {eligible[item].task_index for item in values}
        for name, values in partition_sets.items()
    }
    omitted = (
        set(split.train_episode_indices)
        | set(split.held_out_episode_indices)
        | set(split.held_out_task_episode_indices)
    ) - set().union(*partition_sets.values())
    bounded = replace(
        split,
        train_episode_indices=tuple(sorted(train_selected)),
        held_out_episode_indices=tuple(sorted(episode_holdout_selected)),
        held_out_task_episode_indices=tuple(sorted(task_holdout_selected)),
        train_task_indices=tuple(sorted(int(item) for item in task_sets[TRAIN_SPLIT] if item is not None)),
        held_out_episode_task_indices=tuple(
            sorted(int(item) for item in task_sets[HELD_OUT_EPISODE_SPLIT] if item is not None)
        ),
        held_out_task_indices=tuple(
            sorted(int(item) for item in task_sets[HELD_OUT_TASK_SPLIT] if item is not None)
        ),
        excluded_by_budget_episode_indices=tuple(
            sorted(set(split.excluded_by_budget_episode_indices) | omitted)
        ),
        expected_transition_counts={
            name: sum(_transition_capacity(eligible[item]) for item in values)
            for name, values in partition_sets.items()
        },
    )
    validate_bridgedata_split(bounded, episodes)
    return bounded
