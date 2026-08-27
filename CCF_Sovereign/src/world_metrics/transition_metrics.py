"""Per-holdout metrics for action-conditioned typed world predictions.

These metrics compare predicted WorldPrograms to manifest-bound target records.
They report each protected split separately and treat compiler validity as
unavailable unless an ``observed`` compiler receipt exists for every prediction.
No function in this module trains, renders, executes a compiler, or promotes a
candidate.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from world_data.ingestion import IngestedWorldDataset, WorldProgramRecord
from world_schema.model import EvidenceKind, HoldoutSplit, WorldProgram


METRICS_VERSION = 1
REQUIRED_SPLITS = (
    HoldoutSplit.TRAIN,
    HoldoutSplit.HELD_OUT_OBJECT_CLASS,
    HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
    HoldoutSplit.HELD_OUT_COMPOSITION,
)


class WorldMetricError(ValueError):
    """Raised when transition metrics cannot establish a valid comparison."""


@dataclass(frozen=True)
class CompilerReceipt:
    """External compiler evidence associated with one predicted world program.

    A receipt may be counted only when an actual compiler invocation produced a
    hashed artifact and is labeled ``observed``. Tests may construct receipts to
    exercise validation; they are not execution evidence outside the test.
    """

    program_id: str
    predicted_program_sha256: str
    evidence_kind: EvidenceKind
    source_uri: str
    source_sha256: str
    compiler_accepted: bool
    failure_class: str | None = None

    def validate(self) -> None:
        if not self.program_id:
            raise WorldMetricError("compiler receipt program_id is required")
        if len(self.predicted_program_sha256) != 64:
            raise WorldMetricError("compiler receipt needs a predicted program SHA-256")
        if self.evidence_kind is not EvidenceKind.OBSERVED:
            raise WorldMetricError(
                "compiler validity accepts only observed compiler receipts"
            )
        if not self.source_uri:
            raise WorldMetricError("compiler receipt needs an observed artifact URI")
        if len(self.source_sha256) != 64:
            raise WorldMetricError("compiler receipt needs an observed artifact SHA-256")
        if self.compiler_accepted and self.failure_class is not None:
            raise WorldMetricError("accepted compiler receipt may not carry a failure class")
        if not self.compiler_accepted and not self.failure_class:
            raise WorldMetricError("rejected compiler receipt requires a failure class")


@dataclass(frozen=True)
class SplitTransitionMetrics:
    """All Phase 3 metrics for exactly one source partition."""

    split: str
    cases: int
    state_accuracy: float
    relation_accuracy: float
    operation_accuracy: float
    uncertainty_accuracy: float
    exact_program_accuracy: float
    evidence_completeness: float
    compiler_evidence_completeness: float
    compiler_validity_rate: float | None
    compiler_receipts: int
    accepted_compiler_receipts: int
    rejected_compiler_receipts: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionMetricsReport:
    """Immutable per-split Phase 3 report; no aggregate hides split failures."""

    metrics_version: int
    target_manifest_sha256: str
    prediction_set_sha256: str
    by_split: dict[str, SplitTransitionMetrics]
    prediction_count: int
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics_version": self.metrics_version,
            "target_manifest_sha256": self.target_manifest_sha256,
            "prediction_set_sha256": self.prediction_set_sha256,
            "prediction_count": self.prediction_count,
            "by_split": {
                split: metrics.to_dict()
                for split, metrics in sorted(self.by_split.items())
            },
            "notes": list(self.notes),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _fraction(matches: int, total: int) -> float:
    if total == 0:
        raise WorldMetricError("metric denominator must be nonzero")
    return matches / total


def _entity_state(program: WorldProgram) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        sorted(
            (
                entity.entity_id,
                entity.kind.value,
                entity.class_label,
                entity.transform.translation_mm,
                entity.transform.rotation_centideg,
                entity.transform.scale_milli,
                entity.material_id,
                tuple(sorted(entity.attributes.items())),
            )
            for entity in program.entities
        )
    )


def _relation_state(program: WorldProgram) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        sorted(
            (
                relation.relation_id,
                relation.kind.value,
                relation.subject_id,
                relation.object_id,
                relation.confidence_q16,
                relation.evidence_ids,
            )
            for relation in program.relations
        )
    )


def _operation_state(program: WorldProgram) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (
            operation.operation_id,
            operation.kind.value,
            operation.subject_id,
            operation.object_id,
            operation.relation_id,
            operation.camera_id,
            operation.material_id,
            operation.narrative_verb.value if operation.narrative_verb else None,
            (
                (
                    operation.geometry.family.value,
                    operation.geometry.macro.value,
                    operation.geometry.target_id,
                    tuple(sorted(operation.geometry.parameters.items())),
                )
                if operation.geometry
                else None
            ),
            tuple(sorted(operation.parameters.items())),
            operation.preconditions,
            operation.evidence_ids,
            operation.capability_id,
            operation.capability_status.value if operation.capability_status else None,
        )
        for operation in program.operations
    )


def _uncertainty_state(program: WorldProgram) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        sorted(
            (
                uncertainty.uncertainty_id,
                uncertainty.target_id,
                uncertainty.reason.value,
                uncertainty.confidence_q16,
                uncertainty.evidence_ids,
            )
            for uncertainty in program.uncertainty
        )
    )


def _evidence_complete(program: WorldProgram) -> bool:
    """Check that provenance exists and every declared reference is resolvable.

    The schema permits compiler-local state operations, such as camera selection,
    to have no evidence binding. This metric therefore rejects dangling or absent
    program-level provenance without falsely requiring an observation for every
    executable operation.
    """

    evidence_ids = {binding.evidence_id for binding in program.evidence}
    if not evidence_ids:
        return False
    return all(
        set(operation.evidence_ids).issubset(evidence_ids)
        for operation in program.operations
    ) and all(
        set(uncertainty.evidence_ids).issubset(evidence_ids)
        for uncertainty in program.uncertainty
    )


def _prediction_mapping(
    predictions: Mapping[str, WorldProgram] | Iterable[WorldProgram],
) -> dict[str, WorldProgram]:
    if isinstance(predictions, Mapping):
        materialized = tuple((str(program_id), program) for program_id, program in predictions.items())
    else:
        materialized = tuple((program.program_id, program) for program in predictions)
    resolved = dict(materialized)
    if not resolved:
        raise WorldMetricError("at least one prediction is required")
    if len(resolved) != len(materialized):
        raise WorldMetricError("duplicate prediction program IDs are forbidden")
    for program_id, program in resolved.items():
        if program.program_id != program_id:
            raise WorldMetricError("prediction map key must equal WorldProgram program_id")
        program.validate()
    return resolved


def _validate_targets(targets: Iterable[WorldProgramRecord]) -> tuple[WorldProgramRecord, ...]:
    materialized = tuple(targets)
    if not materialized:
        raise WorldMetricError("at least one manifest-bound target is required")
    target_ids = [record.program.program_id for record in materialized]
    if len(target_ids) != len(set(target_ids)):
        raise WorldMetricError("duplicate target program IDs are forbidden")
    target_splits = {record.split for record in materialized}
    if target_splits != set(REQUIRED_SPLITS):
        raise WorldMetricError("target records must include every required split")
    return materialized


def _receipt_mapping(
    receipts: Iterable[CompilerReceipt] | None,
) -> dict[str, CompilerReceipt]:
    if receipts is None:
        return {}
    resolved: dict[str, CompilerReceipt] = {}
    for receipt in receipts:
        receipt.validate()
        if receipt.program_id in resolved:
            raise WorldMetricError("duplicate compiler receipt program_id")
        resolved[receipt.program_id] = receipt
    return resolved


def _prediction_set_sha256(predictions: Mapping[str, WorldProgram]) -> str:
    payload = "\n".join(
        f"{program_id}:{program.sha256()}"
        for program_id, program in sorted(predictions.items())
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def score_transition_predictions(
    dataset: IngestedWorldDataset,
    predictions: Mapping[str, WorldProgram] | Iterable[WorldProgram],
    *,
    compiler_receipts: Iterable[CompilerReceipt] | None = None,
) -> TransitionMetricsReport:
    """Score predictions against the exact manifest-bound ingested dataset.

    Each ingested target must have one prediction with the same program ID. Extra
    predictions and mismatched compiler receipts fail closed. The manifest digest
    is taken directly from the loader receipt rather than a caller-supplied
    string. State, relation, operation, uncertainty, evidence completeness, and
    compiler validity remain separate metrics; no pooled headline score is
    generated.
    """

    if not isinstance(dataset, IngestedWorldDataset):
        raise WorldMetricError("metrics require a manifest-bound IngestedWorldDataset")
    target_manifest_sha256 = dataset.receipt.manifest_sha256
    if len(target_manifest_sha256) != 64:
        raise WorldMetricError("ingested target manifest SHA-256 is invalid")
    resolved_targets = _validate_targets(dataset.records)
    resolved_predictions = _prediction_mapping(predictions)
    target_ids = {record.program.program_id for record in resolved_targets}
    prediction_ids = set(resolved_predictions)
    if prediction_ids != target_ids:
        missing = sorted(target_ids - prediction_ids)
        extra = sorted(prediction_ids - target_ids)
        raise WorldMetricError(
            f"prediction coverage mismatch: missing={missing}, extra={extra}"
        )
    receipts = _receipt_mapping(compiler_receipts)
    unknown_receipts = sorted(set(receipts) - target_ids)
    if unknown_receipts:
        raise WorldMetricError(f"compiler receipt for unknown prediction: {unknown_receipts}")
    for program_id, receipt in receipts.items():
        if receipt.predicted_program_sha256 != resolved_predictions[program_id].sha256():
            raise WorldMetricError(f"compiler receipt hash mismatch: {program_id}")

    by_split: dict[str, SplitTransitionMetrics] = {}
    for split in REQUIRED_SPLITS:
        split_targets = [record for record in resolved_targets if record.split is split]
        if not split_targets:
            raise WorldMetricError(f"no targets for required split: {split.value}")
        predicted = [resolved_predictions[record.program.program_id] for record in split_targets]
        state_matches = sum(
            _entity_state(record.program) == _entity_state(prediction)
            for record, prediction in zip(split_targets, predicted)
        )
        relation_matches = sum(
            _relation_state(record.program) == _relation_state(prediction)
            for record, prediction in zip(split_targets, predicted)
        )
        operation_matches = sum(
            _operation_state(record.program) == _operation_state(prediction)
            for record, prediction in zip(split_targets, predicted)
        )
        uncertainty_matches = sum(
            _uncertainty_state(record.program) == _uncertainty_state(prediction)
            for record, prediction in zip(split_targets, predicted)
        )
        exact_matches = sum(
            record.program == prediction
            for record, prediction in zip(split_targets, predicted)
        )
        evidence_complete = sum(_evidence_complete(prediction) for prediction in predicted)
        split_receipts = [
            receipts[record.program.program_id]
            for record in split_targets
            if record.program.program_id in receipts
        ]
        accepted = sum(receipt.compiler_accepted for receipt in split_receipts)
        rejected = len(split_receipts) - accepted
        compiler_completeness = _fraction(len(split_receipts), len(split_targets))
        compiler_validity = (
            _fraction(accepted, len(split_receipts))
            if len(split_receipts) == len(split_targets)
            else None
        )
        by_split[split.value] = SplitTransitionMetrics(
            split=split.value,
            cases=len(split_targets),
            state_accuracy=_fraction(state_matches, len(split_targets)),
            relation_accuracy=_fraction(relation_matches, len(split_targets)),
            operation_accuracy=_fraction(operation_matches, len(split_targets)),
            uncertainty_accuracy=_fraction(uncertainty_matches, len(split_targets)),
            exact_program_accuracy=_fraction(exact_matches, len(split_targets)),
            evidence_completeness=_fraction(evidence_complete, len(split_targets)),
            compiler_evidence_completeness=compiler_completeness,
            compiler_validity_rate=compiler_validity,
            compiler_receipts=len(split_receipts),
            accepted_compiler_receipts=accepted,
            rejected_compiler_receipts=rejected,
        )

    notes = (
        "Per-split report only; no pooled held-out score is emitted.",
        "Compiler validity is unavailable unless every prediction in a split has an observed receipt.",
        "This report measures supplied predictions; it does not execute a compiler, render output, train a model, or authorize promotion.",
    )
    return TransitionMetricsReport(
        metrics_version=METRICS_VERSION,
        target_manifest_sha256=target_manifest_sha256.lower(),
        prediction_set_sha256=_prediction_set_sha256(resolved_predictions),
        by_split=by_split,
        prediction_count=len(resolved_predictions),
        notes=notes,
    )
