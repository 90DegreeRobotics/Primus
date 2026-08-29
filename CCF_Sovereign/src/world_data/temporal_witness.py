"""Explicit generated temporal state witnesses for Stage 2 WorldPrograms.

The sidecar witness is derived from, and hash-bound to, a validated Stage 2
record. It preserves the program as the canonical schema/compiler artifact
while making the generated pre-state, action-context, and post-state task
explicit. It never labels a generated target as observed.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from world_data.ingestion import IngestedWorldDataset, WorldProgramRecord
from world_schema.model import HoldoutSplit, OperationKind, RelationKind


TEMPORAL_WITNESS_VERSION = 1
REQUIRED_SPLITS = (
    HoldoutSplit.TRAIN,
    HoldoutSplit.HELD_OUT_OBJECT_CLASS,
    HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
    HoldoutSplit.HELD_OUT_COMPOSITION,
)
CONTEXT_INPUT_FEATURE_NAMES = (
    "source_x_m",
    "source_y_m",
    "source_z_m",
    "geometry_extent_m",
    "geometry_bevel_fraction",
    "geometry_variant_fraction",
    "material_metallic_fraction",
    "material_roughness_fraction",
)
TEMPORAL_TARGET_FEATURE_NAMES = (
    "target_x_m",
    "target_y_m",
    "target_z_m",
    "support_present_after",
    "near_present_after",
)
_FORBIDDEN_INPUT_TERMS = (
    "target",
    "delta",
    "split",
    "class",
    "family",
    "program_id",
    "source_hash",
    "evidence_uri",
)


class TemporalWitnessError(ValueError):
    """Raised when a temporal witness cannot prove its source/target boundary."""


@dataclass(frozen=True)
class TemporalStateWitness:
    """One generated pre-state/context/post-state witness bound to a program."""

    program_id: str
    program_sha256: str
    structural_signature: str
    split: HoldoutSplit
    object_class: str
    operation_family: str
    pre_tick: int
    target_tick: int
    source_translation_mm: tuple[int, int, int]
    geometry_extent_mm: int
    geometry_bevel_q: int
    geometry_variant: int
    material_metallic_q8: int
    material_roughness_q8: int
    target_translation_mm: tuple[int, int, int]
    support_present_after: bool
    near_present_after: bool
    target_evidence_kinds: tuple[str, ...]

    def validate(self) -> None:
        if not self.program_id or len(self.program_sha256) != 64:
            raise TemporalWitnessError("witness source identity is invalid")
        if len(self.structural_signature) != 64:
            raise TemporalWitnessError("witness structural signature is invalid")
        if self.pre_tick < 0 or self.target_tick <= self.pre_tick:
            raise TemporalWitnessError("witness ticks must be ordered and non-negative")
        for label, values in (
            ("source_translation_mm", self.source_translation_mm),
            ("target_translation_mm", self.target_translation_mm),
        ):
            if len(values) != 3 or any(not isinstance(value, int) for value in values):
                raise TemporalWitnessError(f"{label} must contain exactly three integers")
        if not 0 <= self.geometry_extent_mm <= 1_000_000:
            raise TemporalWitnessError("geometry_extent_mm is out of range")
        if not 0 <= self.geometry_bevel_q <= 255:
            raise TemporalWitnessError("geometry_bevel_q is out of range")
        if not 0 <= self.geometry_variant <= 255:
            raise TemporalWitnessError("geometry_variant is out of range")
        for value in (self.material_metallic_q8, self.material_roughness_q8):
            if not 0 <= value <= 255:
                raise TemporalWitnessError("material context is out of q8 range")
        if not self.target_evidence_kinds or any(
            kind not in {"generated", "inferred"} for kind in self.target_evidence_kinds
        ):
            raise TemporalWitnessError(
                "temporal witness targets must retain generated/inferred evidence"
            )

    @property
    def context_input_vector(self) -> tuple[float, ...]:
        return (
            *(value / 1000.0 for value in self.source_translation_mm),
            self.geometry_extent_mm / 1000.0,
            self.geometry_bevel_q / 255.0,
            self.geometry_variant / 4.0,
            self.material_metallic_q8 / 255.0,
            self.material_roughness_q8 / 255.0,
        )

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
        payload["context_input_feature_names"] = list(CONTEXT_INPUT_FEATURE_NAMES)
        payload["target_feature_names"] = list(TEMPORAL_TARGET_FEATURE_NAMES)
        payload["target_evidence_label"] = "generated_temporal_state_witness"
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
        raise TemporalWitnessError(f"expected exactly one {label}, found {len(resolved)}")
    return resolved[0]


def _integer_parameter(operation: Any, name: str) -> int:
    value = operation.parameters.get(name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TemporalWitnessError(f"{operation.operation_id} {name} must be an integer")
    return value


def _relation_final_state(
    record: WorldProgramRecord,
    relation_kind: RelationKind,
    *,
    require_effect: bool = False,
) -> bool:
    """Replay only declared relation additions/removals for one relation kind."""

    relations = {
        relation.relation_id: relation
        for relation in record.program.relations
        if relation.kind is relation_kind
    }
    if len(relations) != 1:
        raise TemporalWitnessError(
            f"expected exactly one declared {relation_kind.value} relation"
        )
    relation_id = next(iter(relations))
    state = False
    effects = [
        operation
        for operation in record.program.operations
        if operation.relation_id == relation_id
        and operation.kind in (OperationKind.ADD_RELATION, OperationKind.REMOVE_RELATION)
    ]
    if not effects:
        if require_effect:
            raise TemporalWitnessError(
                f"missing declared transition for {relation_kind.value}"
            )
        return False
    for operation in effects:
        state = operation.kind is OperationKind.ADD_RELATION
    return state


def _required_tick(record: WorldProgramRecord, operation_id: str) -> int:
    matches = [
        frame.tick
        for frame in record.program.frames
        if operation_id in frame.operation_ids
    ]
    return _single(matches, f"frame containing {operation_id}")


def derive_temporal_witness(record: WorldProgramRecord) -> TemporalStateWitness:
    """Derive a generated temporal target solely from typed program operations."""

    record.program.validate()
    geometry = _single(
        (
            operation
            for operation in record.program.operations
            if operation.kind is OperationKind.GEOMETRY_MACRO
        ),
        "geometry operation",
    )
    if geometry.geometry is None:
        raise TemporalWitnessError("geometry operation must carry an invocation")
    move = _single(
        (
            operation
            for operation in record.program.operations
            if operation.kind is OperationKind.SET_TRANSFORM
        ),
        "SET_TRANSFORM operation",
    )
    if geometry.subject_id != move.subject_id:
        raise TemporalWitnessError("geometry and transform target must be the same subject")
    subject = _single(
        (
            entity
            for entity in record.program.entities
            if entity.entity_id == move.subject_id
        ),
        "transition subject entity",
    )
    if not subject.material_id:
        raise TemporalWitnessError("transition subject must have material context")
    material = _single(
        (
            item
            for item in record.program.materials
            if item.material_id == subject.material_id
        ),
        "transition subject material",
    )
    delta = tuple(
        _integer_parameter(move, name)
        for name in ("delta_x_mm", "delta_y_mm", "delta_z_mm")
    )
    target = tuple(
        source + change for source, change in zip(subject.transform.translation_mm, delta)
    )
    # Declared trajectory knobs live on the operation, not on the geometry
    # invocation. The invocation carries the executable macro contract
    # (selector/axis/distance_mm) and is deliberately not a feature source.
    geometry_parameters = geometry.parameters
    extent = geometry_parameters.get("extent_mm")
    bevel = geometry_parameters.get("bevel_q")
    variant = geometry_parameters.get("variant")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (extent, bevel, variant)):
        raise TemporalWitnessError("geometry action context must be integer-valued")
    pre_tick = _required_tick(record, "operation_observe_start")
    target_tick = _required_tick(record, "operation_observe_end")
    if _required_tick(record, move.operation_id) <= pre_tick:
        raise TemporalWitnessError("SET_TRANSFORM must occur after the pre-state witness")
    evidence_by_id = {
        binding.evidence_id: binding.kind.value for binding in record.program.evidence
    }
    target_evidence_ids = set(move.evidence_ids)
    for operation in record.program.operations:
        if operation.kind in (OperationKind.ADD_RELATION, OperationKind.REMOVE_RELATION):
            target_evidence_ids.update(operation.evidence_ids)
    target_kinds = tuple(sorted(evidence_by_id[evidence_id] for evidence_id in target_evidence_ids))
    witness = TemporalStateWitness(
        program_id=record.program.program_id,
        program_sha256=record.program_sha256,
        structural_signature=record.structural_signature,
        split=record.split,
        object_class=record.object_class,
        operation_family=record.operation_family,
        pre_tick=pre_tick,
        target_tick=target_tick,
        source_translation_mm=subject.transform.translation_mm,
        geometry_extent_mm=extent,
        geometry_bevel_q=bevel,
        geometry_variant=variant,
        material_metallic_q8=material.metallic_q8,
        material_roughness_q8=material.roughness_q8,
        target_translation_mm=target,
        support_present_after=_relation_final_state(
            record,
            RelationKind.SUPPORTS,
            require_effect=True,
        ),
        near_present_after=_relation_final_state(record, RelationKind.NEAR),
        target_evidence_kinds=target_kinds,
    )
    witness.validate()
    return witness


def derive_temporal_witnesses(
    dataset: IngestedWorldDataset,
) -> tuple[TemporalStateWitness, ...]:
    """Create exact one-per-program generated witnesses from an ingestion result."""

    if not isinstance(dataset, IngestedWorldDataset):
        raise TemporalWitnessError("temporal witness derivation requires IngestedWorldDataset")
    witnesses = tuple(derive_temporal_witness(record) for record in dataset.records)
    if len(witnesses) != dataset.receipt.program_count:
        raise TemporalWitnessError("temporal witness count disagrees with source program count")
    identifiers = [witness.program_id for witness in witnesses]
    if len(identifiers) != len(set(identifiers)):
        raise TemporalWitnessError("duplicate temporal witness program IDs are forbidden")
    if {witness.split for witness in witnesses} != set(REQUIRED_SPLITS):
        raise TemporalWitnessError("temporal witnesses must preserve all required splits")
    return witnesses


def temporal_witness_set_sha256(witnesses: Iterable[TemporalStateWitness]) -> str:
    """Hash exact temporal witnesses in stable program-ID order."""

    materialized = tuple(witnesses)
    if not materialized:
        raise TemporalWitnessError("cannot hash an empty temporal witness set")
    payload = "\n".join(
        f"{witness.program_id}:{witness.sha256()}"
        for witness in sorted(materialized, key=lambda item: item.program_id)
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def assert_context_feature_boundary() -> None:
    """Fail closed if the declared model input feature names expose target data."""

    for name in CONTEXT_INPUT_FEATURE_NAMES:
        if any(term in name for term in _FORBIDDEN_INPUT_TERMS):
            raise TemporalWitnessError(
                f"context feature leaks forbidden target or partition term: {name}"
            )
