"""Episode-safe, evaluation-only open-loop rollouts for frozen BridgeData predictors.

A rollout begins from one observed state and advances only by the recorded action
sequence plus the predictor's preceding output.  It never feeds an observed
intermediate state back into the predictor.  This module creates no candidates,
trains no model, writes no checkpoint, and provides no policy or control path.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np

from .bridgedata_evaluation import (
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    REQUIRED_SPLITS,
    ActionOnlyMeanDeltaBaseline,
    BridgeDataEvaluationError,
    NearestTrainStateActionBaseline,
)
from .bridgedata_transitions import BridgeDataTransition, STATE_DIMENSIONS


BRIDGEDATA_ROLLOUT_VERSION = 1
DEFAULT_HORIZONS = (1, 2, 5, 10)
DEFAULT_CASE_SELECTION_SEED = 20_260_827
DEFAULT_MAX_CASES_PER_HORIZON = 256


class BridgeDataRolloutError(ValueError):
    """Raised when rollout inputs, recursion, or exact coverage are invalid."""


def _canonical_json(value: Mapping[str, Any]) -> str:
    import json

    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _finite_vector(values: Sequence[float], label: str) -> tuple[float, ...]:
    if not isinstance(values, (list, tuple)) or len(values) != STATE_DIMENSIONS:
        raise BridgeDataRolloutError(f"{label} must contain exactly {STATE_DIMENSIONS} values")
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as error:
        raise BridgeDataRolloutError(f"{label} must contain numeric values") from error
    if not all(math.isfinite(value) for value in result):
        raise BridgeDataRolloutError(f"{label} must contain finite values")
    return result


def _stable_order_key(seed: int, split: str, case_id: str) -> bytes:
    return hashlib.sha256(f"{seed}:{split}:{case_id}".encode("ascii")).digest()


@dataclass(frozen=True)
class BridgeDataRolloutCase:
    """One observed target reachable through an episode-contained action sequence."""

    case_id: str
    split: str
    episode_index: int
    task_index: int
    task: str
    horizon: int
    source_transition_ids: tuple[str, ...]
    initial_state: tuple[float, ...]
    actions: tuple[tuple[float, ...], ...]
    target_state: tuple[float, ...]
    source_index: int
    target_index: int
    source_frame_index: int
    target_frame_index: int
    source_timestamp: float
    target_timestamp: float

    def validate(self) -> None:
        if not self.case_id or self.split not in REQUIRED_SPLITS:
            raise BridgeDataRolloutError("rollout case has invalid identity or split")
        if self.episode_index < 0 or self.task_index < 0 or not self.task:
            raise BridgeDataRolloutError("rollout case has invalid episode/task lineage")
        if self.horizon < 1 or len(self.actions) != self.horizon:
            raise BridgeDataRolloutError("rollout action count must exactly equal horizon")
        if len(self.source_transition_ids) != self.horizon or not all(self.source_transition_ids):
            raise BridgeDataRolloutError("rollout transition identifiers must exactly equal horizon")
        if self.target_index != self.source_index + self.horizon:
            raise BridgeDataRolloutError("rollout global index span disagrees with horizon")
        if self.target_frame_index != self.source_frame_index + self.horizon:
            raise BridgeDataRolloutError("rollout frame span disagrees with horizon")
        if not self.target_timestamp > self.source_timestamp:
            raise BridgeDataRolloutError("rollout timestamps must increase")
        _finite_vector(self.initial_state, "rollout initial_state")
        _finite_vector(self.target_state, "rollout target_state")
        for action in self.actions:
            _finite_vector(action, "rollout action")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["initial_state"] = list(self.initial_state)
        payload["target_state"] = list(self.target_state)
        payload["actions"] = [list(action) for action in self.actions]
        payload["source_transition_ids"] = list(self.source_transition_ids)
        return payload

    def sha256(self) -> str:
        return hashlib.sha256(_canonical_json(self.to_dict()).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BridgeDataRolloutPrediction:
    """One terminal open-loop prediction keyed to exactly one rollout case."""

    case_id: str
    terminal_state: tuple[float, ...]

    def validate(self) -> None:
        if not self.case_id:
            raise BridgeDataRolloutError("rollout prediction case_id is required")
        _finite_vector(self.terminal_state, "rollout terminal_state")

    def to_dict(self) -> dict[str, Any]:
        return {"case_id": self.case_id, "terminal_state": list(self.terminal_state)}


@dataclass(frozen=True)
class RolloutHorizonMetrics:
    """Exact-coverage terminal error at one partition and prediction horizon."""

    split: str
    horizon: int
    cases: int
    predictions: int
    coverage: float
    unknown_prediction_count: int
    excluded_case_count: int
    finite_prediction_rate: float
    aggregate_rmse: float
    aggregate_mae: float
    dimension_rmse: tuple[float, ...]
    dimension_mae: tuple[float, ...]
    case_set_sha256: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["dimension_rmse"] = list(self.dimension_rmse)
        payload["dimension_mae"] = list(self.dimension_mae)
        return payload


@dataclass(frozen=True)
class BridgeDataRolloutReport:
    """Split-separated rollout measurements for one predictor."""

    rollout_version: int
    prediction_label: str
    horizons: tuple[int, ...]
    max_cases_per_horizon: int
    case_selection_seed: int
    by_split_and_horizon: dict[str, dict[int, RolloutHorizonMetrics]]
    error_growth_ratio_to_horizon_one: dict[str, dict[int, float | None]]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollout_version": self.rollout_version,
            "prediction_label": self.prediction_label,
            "horizons": list(self.horizons),
            "max_cases_per_horizon": self.max_cases_per_horizon,
            "case_selection_seed": self.case_selection_seed,
            "by_split_and_horizon": {
                split: {
                    str(horizon): self.by_split_and_horizon[split][horizon].to_dict()
                    for horizon in self.horizons
                }
                for split in REQUIRED_SPLITS
            },
            "error_growth_ratio_to_horizon_one": {
                split: {
                    str(horizon): self.error_growth_ratio_to_horizon_one[split][horizon]
                    for horizon in self.horizons
                }
                for split in REQUIRED_SPLITS
            },
            "notes": list(self.notes),
        }


def _assert_rollout_link(previous: BridgeDataTransition, current: BridgeDataTransition) -> None:
    previous.validate()
    current.validate()
    if current.episode_index != previous.episode_index:
        raise BridgeDataRolloutError("rollout sequence crosses an episode boundary")
    if current.task_index != previous.task_index or current.task != previous.task:
        raise BridgeDataRolloutError("rollout sequence changes task lineage within an episode")
    if current.source_index != previous.target_index:
        raise BridgeDataRolloutError("rollout sequence skips a global source index")
    if current.source_frame_index != previous.target_frame_index:
        raise BridgeDataRolloutError("rollout sequence skips a source frame index")
    if current.source_timestamp != previous.target_timestamp:
        raise BridgeDataRolloutError("rollout sequence has a discontinuous source timestamp")
    if current.state_t != previous.state_t_plus_1:
        raise BridgeDataRolloutError("rollout sequence has discontinuous observed state lineage")


def rollout_case_set_sha256(cases: Iterable[BridgeDataRolloutCase]) -> str:
    materialized = tuple(cases)
    identifiers = [case.case_id for case in materialized]
    if len(identifiers) != len(set(identifiers)):
        raise BridgeDataRolloutError("rollout case set contains duplicate case IDs")
    payload = "\n".join(f"{case.case_id}:{case.sha256()}" for case in materialized) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def build_rollout_cases(
    transitions: Iterable[BridgeDataTransition],
    *,
    split: str,
    horizon: int,
    max_cases: int = DEFAULT_MAX_CASES_PER_HORIZON,
    case_selection_seed: int = DEFAULT_CASE_SELECTION_SEED,
) -> tuple[BridgeDataRolloutCase, ...]:
    """Build a deterministic bounded set of episode-contained observed rollouts."""

    if split not in REQUIRED_SPLITS:
        raise BridgeDataRolloutError("unknown rollout split")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
        raise BridgeDataRolloutError("rollout horizon must be a positive integer")
    if isinstance(max_cases, bool) or not isinstance(max_cases, int) or max_cases < 1:
        raise BridgeDataRolloutError("max_cases must be a positive integer")
    if isinstance(case_selection_seed, bool) or not isinstance(case_selection_seed, int):
        raise BridgeDataRolloutError("case_selection_seed must be an integer")

    groups: dict[int, list[BridgeDataTransition]] = {}
    seen_ids: set[str] = set()
    for transition in transitions:
        transition.validate()
        if transition.transition_id in seen_ids:
            raise BridgeDataRolloutError("rollout input contains duplicate transition IDs")
        seen_ids.add(transition.transition_id)
        groups.setdefault(transition.episode_index, []).append(transition)
    if not groups:
        raise BridgeDataRolloutError("rollout input contains no transitions")

    candidates: list[BridgeDataRolloutCase] = []
    for episode_index, episode_transitions in sorted(groups.items()):
        ordered = tuple(sorted(episode_transitions, key=lambda item: item.source_index))
        for previous, current in zip(ordered, ordered[1:]):
            _assert_rollout_link(previous, current)
        for start in range(0, len(ordered) - horizon + 1):
            segment = ordered[start : start + horizon]
            first = segment[0]
            last = segment[-1]
            case = BridgeDataRolloutCase(
                case_id=(
                    f"bridgedata-rollout-{split}-e{episode_index}"
                    f"-f{first.source_frame_index}-i{first.source_index}-h{horizon}"
                ),
                split=split,
                episode_index=episode_index,
                task_index=first.task_index,
                task=first.task,
                horizon=horizon,
                source_transition_ids=tuple(item.transition_id for item in segment),
                initial_state=first.state_t,
                actions=tuple(item.action_t for item in segment),
                target_state=last.state_t_plus_1,
                source_index=first.source_index,
                target_index=last.target_index,
                source_frame_index=first.source_frame_index,
                target_frame_index=last.target_frame_index,
                source_timestamp=first.source_timestamp,
                target_timestamp=last.target_timestamp,
            )
            case.validate()
            candidates.append(case)
    if not candidates:
        raise BridgeDataRolloutError("no episode-contained sequences exist for the requested horizon")
    ordered_candidates = tuple(
        sorted(candidates, key=lambda item: (_stable_order_key(case_selection_seed, split, item.case_id), item.case_id))
    )
    selected = ordered_candidates[:max_cases]
    if len(selected) != len({case.case_id for case in selected}):
        raise BridgeDataRolloutError("selected rollout cases are not unique")
    return selected


def rollout_predictions(
    cases: Iterable[BridgeDataRolloutCase],
    predict_next_state: Callable[[tuple[float, ...], tuple[float, ...]], Sequence[float]],
) -> dict[str, BridgeDataRolloutPrediction]:
    """Recursively roll one predictor forward without observed intermediate states."""

    result: dict[str, BridgeDataRolloutPrediction] = {}
    for case in cases:
        case.validate()
        if case.case_id in result:
            raise BridgeDataRolloutError("rollout prediction input contains duplicate case IDs")
        predicted_state = case.initial_state
        for action in case.actions:
            predicted_state = _finite_vector(
                predict_next_state(predicted_state, action), "rollout predictor output"
            )
        result[case.case_id] = BridgeDataRolloutPrediction(
            case_id=case.case_id,
            terminal_state=predicted_state,
        )
    if not result:
        raise BridgeDataRolloutError("rollout prediction input contains no cases")
    return result


def copy_state_predictor(
    state: tuple[float, ...], _action: tuple[float, ...]
) -> tuple[float, ...]:
    """Open-loop persistence baseline: state remains the rollout start state."""

    return _finite_vector(state, "copy-state rollout input")


def action_only_mean_delta_predictor(
    baseline: ActionOnlyMeanDeltaBaseline,
) -> Callable[[tuple[float, ...], tuple[float, ...]], tuple[float, ...]]:
    """Return a repeated train-only mean-delta open-loop predictor."""

    if not isinstance(baseline, ActionOnlyMeanDeltaBaseline):
        raise BridgeDataRolloutError("expected an ActionOnlyMeanDeltaBaseline")
    _finite_vector(baseline.mean_delta, "mean-delta rollout baseline")

    def predict(state: tuple[float, ...], _action: tuple[float, ...]) -> tuple[float, ...]:
        current = _finite_vector(state, "mean-delta rollout state")
        return tuple(value + delta for value, delta in zip(current, baseline.mean_delta))

    return predict


def nearest_train_state_action_predictor(
    baseline: NearestTrainStateActionBaseline,
) -> Callable[[tuple[float, ...], tuple[float, ...]], tuple[float, ...]]:
    """Return a repeated train-only nearest state/action-delta predictor."""

    if not isinstance(baseline, NearestTrainStateActionBaseline):
        raise BridgeDataRolloutError("expected a NearestTrainStateActionBaseline")
    bank = np.asarray(baseline.normalized_features, dtype=np.float64)
    deltas = np.asarray(baseline.target_deltas, dtype=np.float64)
    means = np.asarray(baseline.feature_mean, dtype=np.float64)
    scales = np.asarray(baseline.feature_scale, dtype=np.float64)
    if bank.ndim != 2 or bank.shape[1] != STATE_DIMENSIONS * 2 or not len(bank):
        raise BridgeDataRolloutError("nearest rollout baseline has an invalid train-only feature bank")
    if deltas.shape != (len(bank), STATE_DIMENSIONS):
        raise BridgeDataRolloutError("nearest rollout baseline has invalid train-only delta values")

    def predict(state: tuple[float, ...], action: tuple[float, ...]) -> tuple[float, ...]:
        current = _finite_vector(state, "nearest rollout state")
        observed_action = _finite_vector(action, "nearest rollout action")
        feature = np.asarray(current + observed_action, dtype=np.float64)
        query = (feature - means) / scales
        index = int(np.argmin(np.sum((bank - query) ** 2, axis=1)))
        values = tuple(float(value + delta) for value, delta in zip(current, deltas[index]))
        return _finite_vector(values, "nearest rollout predictor output")

    return predict


def score_rollout_predictions(
    cases: Iterable[BridgeDataRolloutCase],
    predictions: Mapping[str, BridgeDataRolloutPrediction] | Iterable[BridgeDataRolloutPrediction],
) -> RolloutHorizonMetrics:
    """Score one exact case set with no pooled partitions or implicit coverage."""

    expected_cases = tuple(cases)
    if not expected_cases:
        raise BridgeDataRolloutError("at least one rollout case is required")
    for case in expected_cases:
        case.validate()
    identifiers = [case.case_id for case in expected_cases]
    if len(identifiers) != len(set(identifiers)):
        raise BridgeDataRolloutError("rollout score input contains duplicate case IDs")
    if isinstance(predictions, Mapping):
        resolved = dict(predictions)
    else:
        pairs = tuple((item.case_id, item) for item in predictions)
        resolved = dict(pairs)
        if len(pairs) != len(resolved):
            raise BridgeDataRolloutError("rollout predictions contain duplicate case IDs")
    for key, prediction in resolved.items():
        if not isinstance(prediction, BridgeDataRolloutPrediction):
            raise BridgeDataRolloutError("rollout prediction has invalid type")
        prediction.validate()
        if key != prediction.case_id:
            raise BridgeDataRolloutError("rollout prediction key disagrees with case ID")
    expected = set(identifiers)
    observed = set(resolved)
    if expected != observed:
        raise BridgeDataRolloutError(
            f"rollout prediction coverage mismatch: missing={len(expected - observed)}, extra={len(observed - expected)}"
        )
    splits = {case.split for case in expected_cases}
    horizons = {case.horizon for case in expected_cases}
    if len(splits) != 1 or len(horizons) != 1:
        raise BridgeDataRolloutError("one metric record must score one split and one horizon")
    sum_squared = 0.0
    sum_absolute = 0.0
    dimension_squared = [0.0] * STATE_DIMENSIONS
    dimension_absolute = [0.0] * STATE_DIMENSIONS
    for case in expected_cases:
        values = tuple(
            predicted - target
            for predicted, target in zip(resolved[case.case_id].terminal_state, case.target_state)
        )
        sum_squared += sum(value * value for value in values)
        sum_absolute += sum(abs(value) for value in values)
        for dimension, value in enumerate(values):
            dimension_squared[dimension] += value * value
            dimension_absolute[dimension] += abs(value)
    count = len(expected_cases)
    return RolloutHorizonMetrics(
        split=next(iter(splits)),
        horizon=next(iter(horizons)),
        cases=count,
        predictions=count,
        coverage=1.0,
        unknown_prediction_count=0,
        excluded_case_count=0,
        finite_prediction_rate=1.0,
        aggregate_rmse=math.sqrt(sum_squared / (count * STATE_DIMENSIONS)),
        aggregate_mae=sum_absolute / (count * STATE_DIMENSIONS),
        dimension_rmse=tuple(math.sqrt(value / count) for value in dimension_squared),
        dimension_mae=tuple(value / count for value in dimension_absolute),
        case_set_sha256=rollout_case_set_sha256(expected_cases),
    )


def evaluate_rollout_predictor(
    partitioned_transitions: Mapping[str, Sequence[BridgeDataTransition]],
    *,
    prediction_label: str,
    predict_next_state: Callable[[tuple[float, ...], tuple[float, ...]], Sequence[float]],
    horizons: Sequence[int] = DEFAULT_HORIZONS,
    max_cases_per_horizon: int = DEFAULT_MAX_CASES_PER_HORIZON,
    case_selection_seed: int = DEFAULT_CASE_SELECTION_SEED,
) -> BridgeDataRolloutReport:
    """Evaluate a predictor at each split/horizon on exact bounded case sets."""

    if not prediction_label:
        raise BridgeDataRolloutError("prediction_label is required")
    if set(partitioned_transitions) != set(REQUIRED_SPLITS):
        raise BridgeDataRolloutError("rollout evaluation requires exactly the declared split partitions")
    resolved_horizons = tuple(horizons)
    if resolved_horizons != tuple(sorted(set(resolved_horizons))) or not resolved_horizons:
        raise BridgeDataRolloutError("rollout horizons must be a non-empty ascending unique sequence")
    if any(isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1 for horizon in resolved_horizons):
        raise BridgeDataRolloutError("rollout horizons must be positive integers")
    by_split: dict[str, dict[int, RolloutHorizonMetrics]] = {}
    growth: dict[str, dict[int, float]] = {}
    for split in REQUIRED_SPLITS:
        transitions = tuple(partitioned_transitions[split])
        if not transitions:
            raise BridgeDataRolloutError(f"rollout partition has no transitions: {split}")
        metrics_by_horizon: dict[int, RolloutHorizonMetrics] = {}
        for horizon in resolved_horizons:
            cases = build_rollout_cases(
                transitions,
                split=split,
                horizon=horizon,
                max_cases=max_cases_per_horizon,
                case_selection_seed=case_selection_seed,
            )
            metrics_by_horizon[horizon] = score_rollout_predictions(
                cases, rollout_predictions(cases, predict_next_state)
            )
        baseline_rmse = metrics_by_horizon[1].aggregate_rmse
        if not math.isfinite(baseline_rmse) or baseline_rmse < 0:
            raise BridgeDataRolloutError("horizon-one RMSE must be finite and non-negative for growth ratios")
        by_split[split] = metrics_by_horizon
        if baseline_rmse == 0.0:
            growth[split] = {
                horizon: (1.0 if metrics.aggregate_rmse == 0.0 else None)
                for horizon, metrics in metrics_by_horizon.items()
            }
        else:
            growth[split] = {
                horizon: metrics.aggregate_rmse / baseline_rmse
                for horizon, metrics in metrics_by_horizon.items()
            }
    return BridgeDataRolloutReport(
        rollout_version=BRIDGEDATA_ROLLOUT_VERSION,
        prediction_label=prediction_label,
        horizons=resolved_horizons,
        max_cases_per_horizon=max_cases_per_horizon,
        case_selection_seed=case_selection_seed,
        by_split_and_horizon=by_split,
        error_growth_ratio_to_horizon_one=growth,
        notes=(
            "Each metric is a terminal open-loop error from one observed initial state and recorded observed actions only.",
            "Observed intermediate states are not inputs after rollout start; predicted state is recursively fed to the next step.",
            "Each split and horizon is separately reported with an exact, deterministic bounded case set; no pooled protected score is emitted.",
            "When horizon-one terminal RMSE is exactly zero, its growth ratio is 1.0 only for a zero-error horizon and otherwise is null because a finite multiplicative ratio is undefined.",
            "This report is observational prediction evidence only, not policy, control, safety, renderer, or promotion evidence.",
        ),
    )


def predeclared_rollout_acceptance(
    candidate_report: BridgeDataRolloutReport,
    baseline_reports: Mapping[str, BridgeDataRolloutReport],
) -> dict[str, Any]:
    """Apply the fixed positive-signal rule to protected horizons one, two, and five."""

    required_horizons = (1, 2, 5)
    protected_splits = (HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT)
    if not all(horizon in candidate_report.horizons for horizon in required_horizons):
        raise BridgeDataRolloutError("candidate report lacks required acceptance horizons")
    if not baseline_reports:
        raise BridgeDataRolloutError("at least one baseline report is required")
    comparisons: dict[str, dict[str, Any]] = {}
    all_passed = True
    for split in protected_splits:
        comparisons[split] = {}
        for horizon in required_horizons:
            candidates = [
                (label, report.by_split_and_horizon[split][horizon].aggregate_rmse)
                for label, report in baseline_reports.items()
                if horizon in report.horizons
            ]
            if not candidates:
                raise BridgeDataRolloutError("baseline reports lack a required acceptance horizon")
            label, baseline_rmse = min(candidates, key=lambda item: (item[1], item[0]))
            candidate_metrics = candidate_report.by_split_and_horizon[split][horizon]
            passed = candidate_metrics.coverage == 1.0 and candidate_metrics.aggregate_rmse < baseline_rmse
            all_passed = all_passed and passed
            comparisons[split][str(horizon)] = {
                "candidate_aggregate_rmse": candidate_metrics.aggregate_rmse,
                "strongest_baseline": label,
                "strongest_baseline_aggregate_rmse": baseline_rmse,
                "absolute_rmse_improvement": baseline_rmse - candidate_metrics.aggregate_rmse,
                "strict_improvement": passed,
                "coverage": candidate_metrics.coverage,
            }
    return {
        "acceptance_rule": "candidate must have exact coverage and strictly lower terminal open-loop RMSE than the strongest explicit baseline on both protected partitions at horizons 1, 2, and 5; horizon 10 is descriptive only",
        "passed": all_passed,
        "by_protected_split_and_horizon": comparisons,
        "promotion_authorized": False,
    }
