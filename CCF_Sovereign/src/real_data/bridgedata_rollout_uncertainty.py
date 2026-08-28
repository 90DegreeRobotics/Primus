"""Episode-clustered paired uncertainty utilities for frozen BridgeData rollouts.

The module makes no model, policy, action, or promotion decision.  It describes
sampling uncertainty in an already fixed observed rollout comparison by
resampling whole selected episodes and retaining all selected rollout cases in
each drawn episode.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .bridgedata_rollouts import (
    BridgeDataRolloutCase,
    BridgeDataRolloutError,
    BridgeDataRolloutPrediction,
)


PAIRED_BOOTSTRAP_VERSION = 1
DEFAULT_BOOTSTRAP_RESAMPLES = 10_000
DEFAULT_BOOTSTRAP_SEED = 20_260_828
DEFAULT_MIN_DISTINCT_EPISODES = 10


class BridgeDataRolloutUncertaintyError(ValueError):
    """Raised when paired rollout residuals cannot support the declared audit."""


def _canonical_json(value: Mapping[str, Any]) -> str:
    import json

    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _finite_vector(values: Sequence[float], label: str) -> tuple[float, ...]:
    if len(values) != 7:
        raise BridgeDataRolloutUncertaintyError(f"{label} must contain exactly seven values")
    result = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in result):
        raise BridgeDataRolloutUncertaintyError(f"{label} must be finite")
    return result


@dataclass(frozen=True)
class PairedRolloutCaseError:
    """Exact paired terminal squared-error values for one rollout case."""

    case_id: str
    episode_index: int
    candidate_mean_squared_error: float
    baseline_mean_squared_error: float

    @property
    def candidate_minus_baseline_mse(self) -> float:
        return self.candidate_mean_squared_error - self.baseline_mean_squared_error

    def validate(self) -> None:
        if not self.case_id or self.episode_index < 0:
            raise BridgeDataRolloutUncertaintyError("paired rollout case identity is invalid")
        for label, value in (
            ("candidate mean squared error", self.candidate_mean_squared_error),
            ("baseline mean squared error", self.baseline_mean_squared_error),
        ):
            if not math.isfinite(value) or value < 0.0:
                raise BridgeDataRolloutUncertaintyError(f"{label} must be finite and non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "episode_index": self.episode_index,
            "candidate_mean_squared_error": self.candidate_mean_squared_error,
            "baseline_mean_squared_error": self.baseline_mean_squared_error,
            "candidate_minus_baseline_mse": self.candidate_minus_baseline_mse,
        }


@dataclass(frozen=True)
class EpisodeClusteredBootstrapResult:
    """Point and cluster-bootstrap uncertainty for one paired rollout row."""

    bootstrap_version: int
    cases: int
    distinct_episode_count: int
    resamples: int
    seed: int
    point_candidate_mse: float
    point_baseline_mse: float
    point_candidate_minus_baseline_mse: float
    point_candidate_rmse: float
    point_baseline_rmse: float
    point_candidate_minus_baseline_rmse: float
    bootstrap_standard_error_mse: float
    percentile_ci_95_lower_mse: float
    percentile_ci_95_upper_mse: float
    interpretation: str
    case_error_set_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def paired_rollout_case_errors(
    cases: Iterable[BridgeDataRolloutCase],
    candidate_predictions: Mapping[str, BridgeDataRolloutPrediction] | Iterable[BridgeDataRolloutPrediction],
    baseline_predictions: Mapping[str, BridgeDataRolloutPrediction] | Iterable[BridgeDataRolloutPrediction],
) -> tuple[PairedRolloutCaseError, ...]:
    """Construct exact-ID paired residuals from a shared fixed rollout case set."""

    expected = tuple(cases)
    if not expected:
        raise BridgeDataRolloutUncertaintyError("at least one rollout case is required")
    case_ids = [case.case_id for case in expected]
    if len(case_ids) != len(set(case_ids)):
        raise BridgeDataRolloutUncertaintyError("rollout case set contains duplicate IDs")
    for case in expected:
        try:
            case.validate()
        except BridgeDataRolloutError as error:
            raise BridgeDataRolloutUncertaintyError("rollout case failed validation") from error

    def normalize(
        values: Mapping[str, BridgeDataRolloutPrediction] | Iterable[BridgeDataRolloutPrediction],
        label: str,
    ) -> dict[str, BridgeDataRolloutPrediction]:
        if isinstance(values, Mapping):
            result = dict(values)
        else:
            pairs = tuple((item.case_id, item) for item in values)
            result = dict(pairs)
            if len(result) != len(pairs):
                raise BridgeDataRolloutUncertaintyError(f"{label} predictions contain duplicate IDs")
        if set(result) != set(case_ids):
            raise BridgeDataRolloutUncertaintyError(f"{label} predictions do not have exact case coverage")
        for key, prediction in result.items():
            if not isinstance(prediction, BridgeDataRolloutPrediction):
                raise BridgeDataRolloutUncertaintyError(f"{label} prediction type is invalid")
            try:
                prediction.validate()
            except BridgeDataRolloutError as error:
                raise BridgeDataRolloutUncertaintyError(f"{label} prediction failed validation") from error
            if key != prediction.case_id:
                raise BridgeDataRolloutUncertaintyError(f"{label} prediction key disagrees with case ID")
        return result

    candidate = normalize(candidate_predictions, "candidate")
    baseline = normalize(baseline_predictions, "baseline")
    result = []
    for case in expected:
        target = _finite_vector(case.target_state, "rollout target")
        candidate_state = _finite_vector(candidate[case.case_id].terminal_state, "candidate terminal state")
        baseline_state = _finite_vector(baseline[case.case_id].terminal_state, "baseline terminal state")
        candidate_mse = sum((predicted - observed) ** 2 for predicted, observed in zip(candidate_state, target)) / 7.0
        baseline_mse = sum((predicted - observed) ** 2 for predicted, observed in zip(baseline_state, target)) / 7.0
        item = PairedRolloutCaseError(
            case_id=case.case_id,
            episode_index=case.episode_index,
            candidate_mean_squared_error=candidate_mse,
            baseline_mean_squared_error=baseline_mse,
        )
        item.validate()
        result.append(item)
    return tuple(result)


def paired_case_error_set_sha256(errors: Iterable[PairedRolloutCaseError]) -> str:
    materialized = tuple(errors)
    identifiers = [item.case_id for item in materialized]
    if not materialized or len(identifiers) != len(set(identifiers)):
        raise BridgeDataRolloutUncertaintyError("paired error set must be non-empty with unique case IDs")
    for item in materialized:
        item.validate()
    payload = "\n".join(
        f"{item.case_id}:{hashlib.sha256(_canonical_json(item.to_dict()).encode('utf-8')).hexdigest()}"
        for item in materialized
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def episode_clustered_paired_bootstrap(
    errors: Iterable[PairedRolloutCaseError],
    *,
    resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    seed: int = DEFAULT_BOOTSTRAP_SEED,
    minimum_distinct_episodes: int = DEFAULT_MIN_DISTINCT_EPISODES,
) -> EpisodeClusteredBootstrapResult:
    """Apply the declared case-weighted whole-episode paired bootstrap.

    Each replicate samples selected episode IDs with replacement.  All selected
    rollout cases within a drawn episode are retained, so the replicate statistic
    is case-weighted while the resampling unit remains the episode.
    """

    materialized = tuple(errors)
    if not materialized:
        raise BridgeDataRolloutUncertaintyError("paired bootstrap requires at least one paired error")
    if isinstance(resamples, bool) or not isinstance(resamples, int) or resamples < 1:
        raise BridgeDataRolloutUncertaintyError("bootstrap resamples must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise BridgeDataRolloutUncertaintyError("bootstrap seed must be an integer")
    if isinstance(minimum_distinct_episodes, bool) or not isinstance(minimum_distinct_episodes, int) or minimum_distinct_episodes < 1:
        raise BridgeDataRolloutUncertaintyError("minimum distinct episodes must be a positive integer")
    identifiers = [item.case_id for item in materialized]
    if len(identifiers) != len(set(identifiers)):
        raise BridgeDataRolloutUncertaintyError("paired bootstrap input has duplicate case IDs")
    for item in materialized:
        item.validate()
    clusters: dict[int, list[PairedRolloutCaseError]] = {}
    for item in materialized:
        clusters.setdefault(item.episode_index, []).append(item)
    episode_ids = tuple(sorted(clusters))
    if len(episode_ids) < minimum_distinct_episodes:
        raise BridgeDataRolloutUncertaintyError(
            f"paired bootstrap requires at least {minimum_distinct_episodes} distinct selected episodes; found {len(episode_ids)}"
        )

    cluster_candidate_sums = np.asarray(
        [sum(item.candidate_mean_squared_error for item in clusters[episode]) for episode in episode_ids],
        dtype=np.float64,
    )
    cluster_baseline_sums = np.asarray(
        [sum(item.baseline_mean_squared_error for item in clusters[episode]) for episode in episode_ids],
        dtype=np.float64,
    )
    cluster_case_counts = np.asarray([len(clusters[episode]) for episode in episode_ids], dtype=np.float64)
    candidate_mse = float(cluster_candidate_sums.sum() / cluster_case_counts.sum())
    baseline_mse = float(cluster_baseline_sums.sum() / cluster_case_counts.sum())
    difference_mse = candidate_mse - baseline_mse
    generator = np.random.default_rng(seed)
    selected = generator.integers(0, len(episode_ids), size=(resamples, len(episode_ids)), endpoint=False)
    replicate_candidate = cluster_candidate_sums[selected].sum(axis=1)
    replicate_baseline = cluster_baseline_sums[selected].sum(axis=1)
    replicate_counts = cluster_case_counts[selected].sum(axis=1)
    differences = (replicate_candidate - replicate_baseline) / replicate_counts
    if not np.all(np.isfinite(differences)):
        raise BridgeDataRolloutUncertaintyError("paired bootstrap produced a non-finite replicate")
    lower, upper = (float(value) for value in np.quantile(differences, (0.025, 0.975), method="linear"))
    standard_error = float(np.std(differences, ddof=1)) if resamples > 1 else 0.0
    candidate_rmse = math.sqrt(candidate_mse)
    baseline_rmse = math.sqrt(baseline_mse)
    if candidate_rmse < baseline_rmse and upper < 0.0:
        interpretation = "pass"
    elif candidate_rmse > baseline_rmse and lower > 0.0:
        interpretation = "fail"
    else:
        interpretation = "indistinguishable"
    return EpisodeClusteredBootstrapResult(
        bootstrap_version=PAIRED_BOOTSTRAP_VERSION,
        cases=len(materialized),
        distinct_episode_count=len(episode_ids),
        resamples=resamples,
        seed=seed,
        point_candidate_mse=candidate_mse,
        point_baseline_mse=baseline_mse,
        point_candidate_minus_baseline_mse=difference_mse,
        point_candidate_rmse=candidate_rmse,
        point_baseline_rmse=baseline_rmse,
        point_candidate_minus_baseline_rmse=candidate_rmse - baseline_rmse,
        bootstrap_standard_error_mse=standard_error,
        percentile_ci_95_lower_mse=lower,
        percentile_ci_95_upper_mse=upper,
        interpretation=interpretation,
        case_error_set_sha256=paired_case_error_set_sha256(materialized),
    )
