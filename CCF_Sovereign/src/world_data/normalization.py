"""Train-only normalization for generated temporal-context witnesses."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

from world_data.temporal_witness import (
    CONTEXT_INPUT_FEATURE_NAMES,
    TEMPORAL_TARGET_FEATURE_NAMES,
    TemporalStateWitness,
)
from world_schema.model import HoldoutSplit


NORMALIZATION_VERSION = 1
_MINIMUM_SCALE = 1e-6


class NormalizationError(ValueError):
    """Raised when a normalization receipt cannot prove a train-only fit."""


def _finite_vector(values: Sequence[float], label: str) -> tuple[float, ...]:
    normalized = tuple(float(value) for value in values)
    if not normalized or not all(math.isfinite(value) for value in normalized):
        raise NormalizationError(f"{label} must be a nonempty finite vector")
    return normalized


def _mean_and_scale(rows: tuple[tuple[float, ...], ...], label: str) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if not rows:
        raise NormalizationError(f"{label} cannot be empty")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise NormalizationError(f"{label} has inconsistent vector width")
    means = tuple(sum(row[index] for row in rows) / len(rows) for index in range(width))
    scales = tuple(
        max(
            math.sqrt(
                sum((row[index] - means[index]) ** 2 for row in rows) / len(rows)
            ),
            _MINIMUM_SCALE,
        )
        for index in range(width)
    )
    return _finite_vector(means, f"{label} means"), _finite_vector(scales, f"{label} scales")


@dataclass(frozen=True)
class TemporalContextNormalization:
    """Canonical normalization receipt fitted only from train witnesses."""

    version: int
    train_witness_count: int
    train_program_set_sha256: str
    feature_names: tuple[str, ...]
    position_target_names: tuple[str, ...]
    feature_mean: tuple[float, ...]
    feature_scale: tuple[float, ...]
    position_mean: tuple[float, ...]
    position_scale: tuple[float, ...]

    def validate(self) -> None:
        if self.version != NORMALIZATION_VERSION:
            raise NormalizationError("unsupported normalization version")
        if self.train_witness_count <= 0:
            raise NormalizationError("train_witness_count must be positive")
        if len(self.train_program_set_sha256) != 64:
            raise NormalizationError("train_program_set_sha256 is invalid")
        if self.feature_names != CONTEXT_INPUT_FEATURE_NAMES:
            raise NormalizationError("feature names do not match temporal context contract")
        if self.position_target_names != TEMPORAL_TARGET_FEATURE_NAMES[:3]:
            raise NormalizationError("position target names do not match witness contract")
        for values, expected, label in (
            (self.feature_mean, len(self.feature_names), "feature_mean"),
            (self.feature_scale, len(self.feature_names), "feature_scale"),
            (self.position_mean, 3, "position_mean"),
            (self.position_scale, 3, "position_scale"),
        ):
            if len(values) != expected or not all(math.isfinite(value) for value in values):
                raise NormalizationError(f"{label} is invalid")
        if any(value < _MINIMUM_SCALE for value in self.feature_scale + self.position_scale):
            raise NormalizationError("normalization scales must respect the positive floor")

    def normalize_features(self, values: Sequence[float]) -> tuple[float, ...]:
        self.validate()
        vector = _finite_vector(values, "feature input")
        if len(vector) != len(self.feature_names):
            raise NormalizationError("feature input width does not match receipt")
        return tuple(
            (value - mean) / scale
            for value, mean, scale in zip(vector, self.feature_mean, self.feature_scale)
        )

    def normalize_position_target(self, values: Sequence[float]) -> tuple[float, ...]:
        self.validate()
        vector = _finite_vector(values, "position target")
        if len(vector) != 3:
            raise NormalizationError("position target width must be three")
        return tuple(
            (value - mean) / scale
            for value, mean, scale in zip(vector, self.position_mean, self.position_scale)
        )

    def denormalize_position_target(self, values: Sequence[float]) -> tuple[float, ...]:
        self.validate()
        vector = _finite_vector(values, "normalized position target")
        if len(vector) != 3:
            raise NormalizationError("normalized position target width must be three")
        return tuple(
            value * scale + mean
            for value, mean, scale in zip(vector, self.position_mean, self.position_scale)
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True, separators=(",", ":"))

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def fit_train_only_normalization(
    witnesses: Iterable[TemporalStateWitness],
) -> TemporalContextNormalization:
    """Fit an immutable receipt from a nonempty all-train witness collection."""

    materialized = tuple(witnesses)
    if not materialized:
        raise NormalizationError("normalization requires at least one train witness")
    leaked = [witness.program_id for witness in materialized if witness.split is not HoldoutSplit.TRAIN]
    if leaked:
        raise NormalizationError(
            "normalization may fit only the train partition; "
            f"found protected witness {leaked[0]}"
        )
    identifiers = [witness.program_id for witness in materialized]
    if len(identifiers) != len(set(identifiers)):
        raise NormalizationError("normalization witness IDs must be unique")
    feature_rows = tuple(witness.context_input_vector for witness in materialized)
    position_rows = tuple(witness.target_vector[:3] for witness in materialized)
    feature_mean, feature_scale = _mean_and_scale(feature_rows, "feature")
    position_mean, position_scale = _mean_and_scale(position_rows, "position")
    program_payload = "\n".join(sorted(identifiers)) + "\n"
    receipt = TemporalContextNormalization(
        version=NORMALIZATION_VERSION,
        train_witness_count=len(materialized),
        train_program_set_sha256=hashlib.sha256(program_payload.encode("ascii")).hexdigest(),
        feature_names=CONTEXT_INPUT_FEATURE_NAMES,
        position_target_names=TEMPORAL_TARGET_FEATURE_NAMES[:3],
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        position_mean=position_mean,
        position_scale=position_scale,
    )
    receipt.validate()
    return receipt
