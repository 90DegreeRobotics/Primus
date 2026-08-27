"""Derive narrow generated transition targets from manifest-bound WorldPrograms.

The current Stage 2 schema does not carry complete observed post-action frame
snapshots. This module therefore makes one deliberately limited generated task
explicit: predict a subject's translated position and two relation outcomes from
its initial transform and declared ``SET_TRANSFORM`` action delta. It does not
label generated targets as observed physical outcomes.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from world_data.ingestion import IngestedWorldDataset, WorldProgramRecord
from world_schema.model import HoldoutSplit, OperationKind


TRANSITION_CONTRACT_VERSION = 1
REQUIRED_SPLITS = (
    HoldoutSplit.TRAIN,
    HoldoutSplit.HELD_OUT_OBJECT_CLASS,
    HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
    HoldoutSplit.HELD_OUT_COMPOSITION,
)
INPUT_FEATURE_NAMES = (
    "source_x_m",
    "source_y_m",
    "source_z_m",
    "delta_x_m",
    "delta_y_m",
    "delta_z_m",
)
TARGET_FEATURE_NAMES = (
    "target_x_m",
    "target_y_m",
    "target_z_m",
    "support_present_after",
    "near_present_after",
)


class WorldTransitionError(ValueError):
    """Raised when generated transition examples cannot be proved unambiguous."""


@dataclass(frozen=True)
class WorldTransitionExample:
    """A hash-bound generated transition target for one typed source program."""

    program_id: str
    program_sha256: str
    structural_signature: str
    split: HoldoutSplit
    object_class: str
    operation_family: str
    source_translation_mm: tuple[int, int, int]
    action_delta_mm: tuple[int, int, int]
    target_translation_mm: tuple[int, int, int]
    support_present_after: bool
    near_present_after: bool
    target_evidence_kinds: tuple[str, ...]

    def validate(self) -> None:
        if not self.program_id:
            raise WorldTransitionError("transition program_id is required")
        if len(self.program_sha256) != 64:
            raise WorldTransitionError("transition program SHA-256 is invalid")
        if len(self.structural_signature) != 64:
            raise WorldTransitionError("transition structural signature is invalid")
        for label, values in (
            ("source_translation_mm", self.source_translation_mm),
            ("action_delta_mm", self.action_delta_mm),
            ("target_translation_mm", self.target_translation_mm),
        ):
            if len(values) != 3 or any(not isinstance(value, int) for value in values):
                raise WorldTransitionError(f"{label} must contain exactly three integers")
        if not self.object_class or not self.operation_family:
            raise WorldTransitionError("transition partition lineage is required")
        if not self.target_evidence_kinds:
            raise WorldTransitionError("generated target evidence kinds are required")
        if any(kind not in {"generated", "inferred"} for kind in self.target_evidence_kinds):
            raise WorldTransitionError("transition target evidence may only be generated or inferred")

    @property
    def input_vector(self) -> tuple[float, ...]:
        return tuple(value / 1000.0 for value in (*self.source_translation_mm, *self.action_delta_mm))

    @property
    def target_vector(self) -> tuple[float, ...]:
        return (
            *(value / 1000.0 for value in self.target_translation_mm),
            float(self.support_present_after),
            float(self.near_present_after),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["split"] = self.split.value
        payload["input_feature_names"] = list(INPUT_FEATURE_NAMES)
        payload["target_feature_names"] = list(TARGET_FEATURE_NAMES)
        payload["target_evidence_label"] = "generated_transition_target"
        return payload

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=True, sort_keys=True, separators=(",", ":")
        )

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _single(values: Iterable[Any], label: str) -> Any:
    resolved = tuple(values)
    if len(resolved) != 1:
        raise WorldTransitionError(f"expected exactly one {label}, found {len(resolved)}")
    return resolved[0]


def _integer_parameter(operation: Any, name: str) -> int:
    value = operation.parameters.get(name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise WorldTransitionError(f"SET_TRANSFORM {name} must be an integer")
    return value


def _relation_effect(
    record: WorldProgramRecord,
    *,
    relation_kind: str,
    require_add: bool = False,
) -> bool:
    """Replay declared relation edits for one relation kind from an absent state."""

    relations = {relation.relation_id: relation for relation in record.program.relations}
    effects = []
    for operation in record.program.operations:
        if operation.kind not in (
            OperationKind.ADD_RELATION,
            OperationKind.REMOVE_RELATION,
        ):
            continue
        if not operation.relation_id or operation.relation_id not in relations:
            raise WorldTransitionError("relation operation must reference a declared relation")
        if relations[operation.relation_id].kind.value == relation_kind:
            effects.append(operation)
    if require_add and not any(
        operation.kind is OperationKind.ADD_RELATION for operation in effects
    ):
        raise WorldTransitionError(f"missing add_relation {relation_kind} operation")
    state = False
    for operation in effects:
        state = operation.kind is OperationKind.ADD_RELATION
    return state


def derive_transition_example(record: WorldProgramRecord) -> WorldTransitionExample:
    """Derive an unambiguous generated target from one validated source record."""

    record.program.validate()
    move = _single(
        (
            operation
            for operation in record.program.operations
            if operation.kind is OperationKind.SET_TRANSFORM
        ),
        "SET_TRANSFORM operation",
    )
    subjects = [entity for entity in record.program.entities if entity.entity_id == move.subject_id]
    subject = _single(subjects, "SET_TRANSFORM subject entity")
    delta = tuple(
        _integer_parameter(move, name)
        for name in ("delta_x_mm", "delta_y_mm", "delta_z_mm")
    )
    target = tuple(source + change for source, change in zip(subject.transform.translation_mm, delta))
    support_present_after = _relation_effect(
        record,
        relation_kind="supports",
        require_add=True,
    )
    near_present_after = _relation_effect(
        record,
        relation_kind="near",
    )
    target_kinds = tuple(sorted({binding.kind.value for binding in record.program.evidence}))
    example = WorldTransitionExample(
        program_id=record.program.program_id,
        program_sha256=record.program_sha256,
        structural_signature=record.structural_signature,
        split=record.split,
        object_class=record.object_class,
        operation_family=record.operation_family,
        source_translation_mm=subject.transform.translation_mm,
        action_delta_mm=delta,
        target_translation_mm=target,
        support_present_after=support_present_after,
        near_present_after=near_present_after,
        target_evidence_kinds=target_kinds,
    )
    example.validate()
    return example


def derive_transition_examples(
    dataset: IngestedWorldDataset,
) -> tuple[WorldTransitionExample, ...]:
    """Derive one bounded example per exact manifest-bound source record."""

    if not isinstance(dataset, IngestedWorldDataset):
        raise WorldTransitionError("transition derivation requires an IngestedWorldDataset")
    examples = tuple(derive_transition_example(record) for record in dataset.records)
    if len(examples) != dataset.receipt.program_count:
        raise WorldTransitionError("example count disagrees with manifest-bound program count")
    identifiers = [example.program_id for example in examples]
    if len(identifiers) != len(set(identifiers)):
        raise WorldTransitionError("duplicate transition program IDs are forbidden")
    observed_splits = {example.split for example in examples}
    if observed_splits != set(REQUIRED_SPLITS):
        raise WorldTransitionError("transition examples must preserve every required split")
    return examples


def train_partition_examples(
    examples: Iterable[WorldTransitionExample],
) -> tuple[WorldTransitionExample, ...]:
    """Return only train examples, rejecting callers that attempt split mixing."""

    materialized = tuple(examples)
    if not materialized:
        raise WorldTransitionError("at least one transition example is required")
    for example in materialized:
        example.validate()
        if example.split is not HoldoutSplit.TRAIN:
            raise WorldTransitionError(
                "training examples must contain only the train partition"
            )
    return materialized


def example_set_sha256(examples: Iterable[WorldTransitionExample]) -> str:
    """Hash exact transition examples in program-ID order for run binding."""

    materialized = tuple(examples)
    if not materialized:
        raise WorldTransitionError("cannot hash an empty transition example set")
    payload = "\n".join(
        f"{example.program_id}:{example.sha256()}"
        for example in sorted(materialized, key=lambda item: item.program_id)
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()
