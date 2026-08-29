"""Declared, model-free Phase 0 baselines for geometry-program metrics.

The baselines are intentionally defined before any learner exists.  They provide
comparison points only; a successful baseline run is not a learned result.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import fmean
from typing import Iterable, Mapping, Sequence

from .intake import GeometryCorpusError, GeometryCorpusIntake, GeometryProgramRecord

DECLARED_PHASE_ZERO_BASELINES = (
    "training_mean",
    "step_count_only",
    "op_mix_nearest_neighbour",
)
TARGET_METRICS = ("vert_count", "face_count")
EVALUATION_SPLITS = ("held_out_length", "held_out_op_combo")


@dataclass(frozen=True)
class SplitMetric:
    """One baseline metric calculated only on a named held-out partition."""

    split: str
    count: int
    mean_absolute_error: float
    root_mean_squared_error: float


@dataclass(frozen=True)
class DeclaredBaselineReport:
    """Metric result for one declared baseline, separated by structural split."""

    baseline: str
    target_metric: str
    split_metrics: tuple[SplitMetric, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "baseline": self.baseline,
            "target_metric": self.target_metric,
            "split_metrics": [
                {
                    "split": result.split,
                    "count": result.count,
                    "mean_absolute_error": result.mean_absolute_error,
                    "root_mean_squared_error": result.root_mean_squared_error,
                }
                for result in self.split_metrics
            ],
        }


def _target(record: GeometryProgramRecord, metric: str) -> float:
    raw = record.mesh_metrics.get(metric)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise GeometryCorpusError(f"record {record.sample_id} lacks numeric mesh metric {metric!r}")
    return float(raw)


def _mean_target(records: Sequence[GeometryProgramRecord], metric: str) -> float:
    if not records:
        raise GeometryCorpusError("declared baselines require at least one training record")
    return fmean(_target(record, metric) for record in records)


def _step_count_means(records: Sequence[GeometryProgramRecord], metric: str) -> dict[int, float]:
    values: dict[int, list[float]] = {}
    for record in records:
        values.setdefault(record.program_structure.step_count, []).append(_target(record, metric))
    return {step_count: fmean(targets) for step_count, targets in values.items()}


def _op_mix_distance(left: GeometryProgramRecord, right: GeometryProgramRecord) -> float:
    left_mix = left.program_structure.op_mix_dict()
    right_mix = right.program_structure.op_mix_dict()
    return float(sum(abs(left_mix.get(operation, 0) - right_mix.get(operation, 0)) for operation in set(left_mix) | set(right_mix)))


def _nearest_op_mix_target(
    record: GeometryProgramRecord, training: Sequence[GeometryProgramRecord], metric: str
) -> float:
    nearest = min(
        training,
        key=lambda candidate: (_op_mix_distance(record, candidate), candidate.sample_id),
    )
    return _target(nearest, metric)


def _split_metric(
    split: str, predictions: Iterable[float], records: Sequence[GeometryProgramRecord], metric: str
) -> SplitMetric:
    expected = [_target(record, metric) for record in records]
    predicted = list(predictions)
    if len(expected) != len(predicted) or not expected:
        raise GeometryCorpusError(f"baseline output for {split} does not align with held-out records")
    errors = [abs(actual - estimate) for actual, estimate in zip(expected, predicted, strict=True)]
    return SplitMetric(
        split=split,
        count=len(errors),
        mean_absolute_error=fmean(errors),
        root_mean_squared_error=sqrt(fmean(error * error for error in errors)),
    )


def _evaluate_baseline(
    baseline: str,
    training: Sequence[GeometryProgramRecord],
    held_out: Mapping[str, Sequence[GeometryProgramRecord]],
    metric: str,
) -> DeclaredBaselineReport:
    training_mean = _mean_target(training, metric)
    step_count_means = _step_count_means(training, metric)
    split_metrics: list[SplitMetric] = []
    for split_name in EVALUATION_SPLITS:
        records = held_out[split_name]
        if baseline == "training_mean":
            predictions = [training_mean] * len(records)
        elif baseline == "step_count_only":
            predictions = [
                step_count_means.get(record.program_structure.step_count, training_mean)
                for record in records
            ]
        elif baseline == "op_mix_nearest_neighbour":
            predictions = [_nearest_op_mix_target(record, training, metric) for record in records]
        else:
            raise GeometryCorpusError(f"undeclared baseline {baseline!r}")
        split_metrics.append(_split_metric(split_name, predictions, records, metric))
    return DeclaredBaselineReport(
        baseline=baseline,
        target_metric=metric,
        split_metrics=tuple(split_metrics),
    )


def evaluate_declared_baselines(
    intake: GeometryCorpusIntake, *, target_metrics: Sequence[str] = TARGET_METRICS
) -> tuple[DeclaredBaselineReport, ...]:
    """Run the three declared baselines with fresh hash verification.

    Evaluation is intentionally fail-closed: it re-verifies the corpus,
    manifest, and split definition before calculating any metric, then emits a
    result for each baseline/metric pair on each structural holdout separately.
    """

    intake.verify()
    splits = intake.structural_splits()
    training = splits["train"]
    held_out = {name: splits[name] for name in EVALUATION_SPLITS}
    reports: list[DeclaredBaselineReport] = []
    for metric in target_metrics:
        if not isinstance(metric, str) or not metric:
            raise GeometryCorpusError("target metrics must be non-empty strings")
        for baseline in DECLARED_PHASE_ZERO_BASELINES:
            reports.append(_evaluate_baseline(baseline, training, held_out, metric))
    return tuple(reports)
