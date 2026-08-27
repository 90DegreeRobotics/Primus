"""Metrics for the narrow generated WorldProgram transition task.

The task is deliberately not a renderer or physical-world metric. Predictions
are compared only to generated transition targets derived from a verified Stage
2 dataset. Every protected partition is reported separately and no pooled
held-out score is emitted.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from world_data.ingestion import IngestedWorldDataset
from world_data.transitions import (
    REQUIRED_SPLITS,
    WorldTransitionExample,
    derive_transition_examples,
)
from world_schema.model import HoldoutSplit


STATE_TRANSITION_METRICS_VERSION = 1


class StateTransitionMetricError(ValueError):
    """Raised when a transition prediction set lacks integrity or coverage."""


@dataclass(frozen=True)
class StateTransitionPrediction:
    """One model or baseline prediction for a generated transition target."""

    program_id: str
    target_translation_mm: tuple[float, float, float]
    support_present_after: bool
    near_present_after: bool

    def validate(self) -> None:
        if not self.program_id:
            raise StateTransitionMetricError("prediction program_id is required")
        if len(self.target_translation_mm) != 3 or any(
            not math.isfinite(value) for value in self.target_translation_mm
        ):
            raise StateTransitionMetricError(
                "prediction target_translation_mm must contain three finite values"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=True, sort_keys=True, separators=(",", ":")
        )

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SplitStateTransitionMetrics:
    """Measured generated-transition behavior for exactly one source split."""

    split: str
    cases: int
    position_rmse_mm: float
    position_within_tolerance_accuracy: float
    support_relation_accuracy: float
    near_relation_accuracy: float
    all_transition_accuracy: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StateTransitionMetricsReport:
    """Immutable split-separated report for generated transition targets."""

    metrics_version: int
    target_manifest_sha256: str
    transition_example_set_sha256: str
    prediction_set_sha256: str
    position_tolerance_mm: float
    prediction_count: int
    by_split: dict[str, SplitStateTransitionMetrics]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics_version": self.metrics_version,
            "target_manifest_sha256": self.target_manifest_sha256,
            "transition_example_set_sha256": self.transition_example_set_sha256,
            "prediction_set_sha256": self.prediction_set_sha256,
            "position_tolerance_mm": self.position_tolerance_mm,
            "prediction_count": self.prediction_count,
            "by_split": {
                split: metrics.to_dict()
                for split, metrics in sorted(self.by_split.items())
            },
            "notes": list(self.notes),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=True, sort_keys=True, separators=(",", ":")
        )

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _resolved_predictions(
    predictions: Mapping[str, StateTransitionPrediction]
    | Iterable[StateTransitionPrediction],
) -> dict[str, StateTransitionPrediction]:
    if isinstance(predictions, Mapping):
        pairs = tuple((str(key), value) for key, value in predictions.items())
    else:
        pairs = tuple((prediction.program_id, prediction) for prediction in predictions)
    resolved = dict(pairs)
    if not resolved:
        raise StateTransitionMetricError("at least one transition prediction is required")
    if len(resolved) != len(pairs):
        raise StateTransitionMetricError("duplicate transition prediction program IDs")
    for program_id, prediction in resolved.items():
        prediction.validate()
        if program_id != prediction.program_id:
            raise StateTransitionMetricError(
                "prediction mapping key must equal prediction program_id"
            )
    return resolved


def prediction_set_sha256(
    predictions: Mapping[str, StateTransitionPrediction],
) -> str:
    payload = "\n".join(
        f"{program_id}:{prediction.sha256()}"
        for program_id, prediction in sorted(predictions.items())
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def transition_example_set_sha256(
    examples: Iterable[WorldTransitionExample],
) -> str:
    materialized = tuple(examples)
    payload = "\n".join(
        f"{example.program_id}:{example.sha256()}"
        for example in sorted(materialized, key=lambda item: item.program_id)
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def static_no_change_baseline(
    dataset: IngestedWorldDataset,
) -> dict[str, StateTransitionPrediction]:
    """Return the declared static pre-action baseline for every source program."""

    examples = derive_transition_examples(dataset)
    return {
        example.program_id: StateTransitionPrediction(
            program_id=example.program_id,
            target_translation_mm=tuple(float(value) for value in example.source_translation_mm),
            support_present_after=True,
            near_present_after=False,
        )
        for example in examples
    }


def score_state_transition_predictions(
    dataset: IngestedWorldDataset,
    predictions: Mapping[str, StateTransitionPrediction]
    | Iterable[StateTransitionPrediction],
    *,
    position_tolerance_mm: float = 25.0,
) -> StateTransitionMetricsReport:
    """Score exact-coverage predictions against generated targets by split only."""

    if not isinstance(dataset, IngestedWorldDataset):
        raise StateTransitionMetricError("metrics require an IngestedWorldDataset")
    if not math.isfinite(position_tolerance_mm) or position_tolerance_mm <= 0:
        raise StateTransitionMetricError("position_tolerance_mm must be positive and finite")
    examples = derive_transition_examples(dataset)
    expected_ids = {example.program_id for example in examples}
    resolved = _resolved_predictions(predictions)
    observed_ids = set(resolved)
    if observed_ids != expected_ids:
        raise StateTransitionMetricError(
            "transition prediction coverage mismatch: "
            f"missing={sorted(expected_ids - observed_ids)}, "
            f"extra={sorted(observed_ids - expected_ids)}"
        )

    by_split: dict[str, SplitStateTransitionMetrics] = {}
    for split in REQUIRED_SPLITS:
        split_examples = [example for example in examples if example.split is split]
        if not split_examples:
            raise StateTransitionMetricError(f"required split has no transition examples: {split.value}")
        squared_error = 0.0
        position_within = 0
        support_matches = 0
        near_matches = 0
        complete_matches = 0
        for example in split_examples:
            prediction = resolved[example.program_id]
            deltas = tuple(
                prediction_value - target_value
                for prediction_value, target_value in zip(
                    prediction.target_translation_mm,
                    example.target_translation_mm,
                )
            )
            squared_error += sum(delta * delta for delta in deltas)
            position_correct = all(
                abs(delta) <= position_tolerance_mm for delta in deltas
            )
            support_correct = prediction.support_present_after == example.support_present_after
            near_correct = prediction.near_present_after == example.near_present_after
            position_within += int(position_correct)
            support_matches += int(support_correct)
            near_matches += int(near_correct)
            complete_matches += int(position_correct and support_correct and near_correct)
        count = len(split_examples)
        by_split[split.value] = SplitStateTransitionMetrics(
            split=split.value,
            cases=count,
            position_rmse_mm=math.sqrt(squared_error / (count * 3)),
            position_within_tolerance_accuracy=position_within / count,
            support_relation_accuracy=support_matches / count,
            near_relation_accuracy=near_matches / count,
            all_transition_accuracy=complete_matches / count,
        )

    report = StateTransitionMetricsReport(
        metrics_version=STATE_TRANSITION_METRICS_VERSION,
        target_manifest_sha256=dataset.receipt.manifest_sha256,
        transition_example_set_sha256=transition_example_set_sha256(examples),
        prediction_set_sha256=prediction_set_sha256(resolved),
        position_tolerance_mm=position_tolerance_mm,
        prediction_count=len(resolved),
        by_split=by_split,
        notes=(
            "Generated transition targets only; no physical or observed next-state claim.",
            "Per-split report only; no pooled held-out score is emitted.",
            "Compiler and render validity are outside this numeric transition metric.",
        ),
    )
    return report
