"""Typed, domain-general world-state contract for the Primus world core.

The schema models persistent entities, relations, observations, cameras,
materials, compiler-owned geometry operations, uncertainty, and evidence. It is
intentionally object-class agnostic: class labels are data, never recipes.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any


WORLD_SCHEMA_VERSION = "1.0.0"
WORLD_VOCAB_SIZE = 4096
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class WorldSchemaError(ValueError):
    """Raised when a world program violates a schema invariant."""


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class EntityKind(StrEnum):
    CHARACTER = "character"
    OBJECT = "object"
    LOCATION = "location"
    ABSTRACT = "abstract"


class RelationKind(StrEnum):
    PART_OF = "part_of"
    ATTACHED_TO = "attached_to"
    SUPPORTS = "supports"
    OCCLUDES = "occludes"
    CONSTRAINED_BY = "constrained_by"
    AT = "at"
    ON = "on"
    HOLDING = "holding"
    NEAR = "near"


class GeometryFamily(StrEnum):
    PRIMITIVE = "primitive"
    BOX_GRAMMAR = "box_grammar"
    LATHE = "lathe"
    SWEEP = "sweep"
    COMPOUND = "compound"
    SDF = "sdf"
    VOXEL_FALLBACK = "voxel_fallback"


class GeometryMacro(StrEnum):
    MAKE_RECT_BODY = "make_rect_body"
    SELECT_FACE_BY_NORMAL = "select_face_by_normal"
    EXTRUDE_FACE = "extrude_face"
    INSET_FACE = "inset_face"
    BEVEL_EDGES = "bevel_edges"
    MAKE_GABLED_ROOF = "make_gabled_roof"
    ADD_DOOR_PANEL = "add_door_panel"
    ADD_WINDOW_GRID = "add_window_grid"
    ADD_SHELF_ARRAY = "add_shelf_array"
    ADD_LEG_ARRAY = "add_leg_array"
    LATHE_PROFILE = "lathe_profile"
    HOLLOW_LIP = "hollow_lip"
    SWEEP_PROFILE = "sweep_profile"
    EXTRUDE_TAPER_BLADE = "extrude_taper_blade"
    BRANCH_TAPER = "branch_taper"
    ASSEMBLE_PARTS = "assemble_parts"
    SDF_UNION = "sdf_union"
    EXTRACT_VOXEL_HULL = "extract_voxel_hull"


class OperationKind(StrEnum):
    CREATE_ENTITY = "create_entity"
    REMOVE_ENTITY = "remove_entity"
    ADD_RELATION = "add_relation"
    REMOVE_RELATION = "remove_relation"
    SET_TRANSFORM = "set_transform"
    SET_MATERIAL = "set_material"
    SET_CAMERA = "set_camera"
    GEOMETRY_MACRO = "geometry_macro"
    ASSERT_CONSTRAINT = "assert_constraint"
    OBSERVE = "observe"
    NARRATIVE_ACTION = "narrative_action"


class NarrativeVerb(StrEnum):
    APPROACH = "approach"
    REACH_FOR = "reach_for"
    PAUSE = "pause"
    HESITATE = "hesitate"
    GRASP = "grasp"
    DROP = "drop"
    DEPART_FROM = "depart_from"
    SPEAK = "speak"
    LOOK_AT = "look_at"
    STRIKE = "strike"


class EvidenceKind(StrEnum):
    OBSERVED = "observed"
    MEASURED = "measured"
    COMPILER = "compiler"
    OPERATOR = "operator"
    INFERRED = "inferred"
    GENERATED = "generated"


class UncertaintyReason(StrEnum):
    UNOBSERVED = "unobserved"
    OCCLUDED = "occluded"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    EXTRAPOLATED = "extrapolated"
    QUANTIZED = "quantized"


class ProjectionKind(StrEnum):
    PERSPECTIVE = "perspective"
    ORTHOGRAPHIC = "orthographic"


class CapabilityStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    EXPERIMENTAL = "experimental"


class HoldoutSplit(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    HELD_OUT_OBJECT_CLASS = "held_out_object_class"
    HELD_OUT_OPERATION_FAMILY = "held_out_operation_family"
    HELD_OUT_COMPOSITION = "held_out_composition"


def _primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_primitive(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        _primitive(value),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def require_identifier(field_name: str, value: str) -> None:
    if not IDENTIFIER_RE.fullmatch(value):
        raise WorldSchemaError(
            f"{field_name} must match {IDENTIFIER_RE.pattern}: {value!r}"
        )


def require_q16(field_name: str, value: int) -> None:
    if not 0 <= value <= 65_535:
        raise WorldSchemaError(f"{field_name} must be in [0, 65535]")


@dataclass(frozen=True)
class QuantizedTransform:
    """Deterministic transform: millimetres, centidegrees, and scale/1000."""

    translation_mm: tuple[int, int, int] = (0, 0, 0)
    rotation_centideg: tuple[int, int, int] = (0, 0, 0)
    scale_milli: tuple[int, int, int] = (1000, 1000, 1000)

    def validate(self) -> None:
        if len(self.translation_mm) != 3 or len(self.rotation_centideg) != 3:
            raise WorldSchemaError("transform vectors must have three components")
        if len(self.scale_milli) != 3 or any(value <= 0 for value in self.scale_milli):
            raise WorldSchemaError("scale_milli must contain three positive values")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "QuantizedTransform":
        return cls(
            translation_mm=tuple(int(v) for v in raw.get("translation_mm", (0, 0, 0))),
            rotation_centideg=tuple(int(v) for v in raw.get("rotation_centideg", (0, 0, 0))),
            scale_milli=tuple(int(v) for v in raw.get("scale_milli", (1000, 1000, 1000))),
        )


@dataclass(frozen=True)
class CameraState:
    camera_id: str
    projection: ProjectionKind
    transform: QuantizedTransform
    focal_length_micrometres: int
    sensor_width_micrometres: int
    image_width_px: int
    image_height_px: int
    near_mm: int
    far_mm: int

    def validate(self) -> None:
        require_identifier("camera_id", self.camera_id)
        self.transform.validate()
        positive = (
            self.focal_length_micrometres,
            self.sensor_width_micrometres,
            self.image_width_px,
            self.image_height_px,
            self.near_mm,
            self.far_mm,
        )
        if any(value <= 0 for value in positive):
            raise WorldSchemaError("camera dimensions and clipping values must be positive")
        if self.near_mm >= self.far_mm:
            raise WorldSchemaError("camera near_mm must be less than far_mm")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CameraState":
        return cls(
            camera_id=str(raw["camera_id"]),
            projection=ProjectionKind(raw["projection"]),
            transform=QuantizedTransform.from_dict(raw["transform"]),
            focal_length_micrometres=int(raw["focal_length_micrometres"]),
            sensor_width_micrometres=int(raw["sensor_width_micrometres"]),
            image_width_px=int(raw["image_width_px"]),
            image_height_px=int(raw["image_height_px"]),
            near_mm=int(raw["near_mm"]),
            far_mm=int(raw["far_mm"]),
        )


@dataclass(frozen=True)
class MaterialState:
    material_id: str
    role: str
    base_color_rgba8: tuple[int, int, int, int]
    metallic_q8: int
    roughness_q8: int
    emission_q8: int = 0
    compiler_hint: str = ""

    def validate(self) -> None:
        require_identifier("material_id", self.material_id)
        require_identifier("material role", self.role)
        if len(self.base_color_rgba8) != 4 or any(
            not 0 <= value <= 255 for value in self.base_color_rgba8
        ):
            raise WorldSchemaError("base_color_rgba8 must contain four bytes")
        for name, value in (
            ("metallic_q8", self.metallic_q8),
            ("roughness_q8", self.roughness_q8),
            ("emission_q8", self.emission_q8),
        ):
            if not 0 <= value <= 255:
                raise WorldSchemaError(f"{name} must be in [0, 255]")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MaterialState":
        return cls(
            material_id=str(raw["material_id"]),
            role=str(raw["role"]),
            base_color_rgba8=tuple(int(v) for v in raw["base_color_rgba8"]),
            metallic_q8=int(raw["metallic_q8"]),
            roughness_q8=int(raw["roughness_q8"]),
            emission_q8=int(raw.get("emission_q8", 0)),
            compiler_hint=str(raw.get("compiler_hint", "")),
        )


@dataclass(frozen=True)
class EvidenceBinding:
    evidence_id: str
    kind: EvidenceKind
    source_uri: str
    source_sha256: str
    confidence_q16: int
    frame_id: str | None = None
    camera_id: str | None = None

    def validate(self) -> None:
        require_identifier("evidence_id", self.evidence_id)
        require_q16("confidence_q16", self.confidence_q16)
        if len(self.source_sha256) != 64 or any(
            char not in "0123456789abcdef" for char in self.source_sha256.lower()
        ):
            raise WorldSchemaError("source_sha256 must be a 64-character hex digest")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EvidenceBinding":
        return cls(
            evidence_id=str(raw["evidence_id"]),
            kind=EvidenceKind(raw["kind"]),
            source_uri=str(raw["source_uri"]),
            source_sha256=str(raw["source_sha256"]),
            confidence_q16=int(raw["confidence_q16"]),
            frame_id=raw.get("frame_id"),
            camera_id=raw.get("camera_id"),
        )


@dataclass(frozen=True)
class Uncertainty:
    uncertainty_id: str
    target_id: str
    reason: UncertaintyReason
    confidence_q16: int
    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        require_identifier("uncertainty_id", self.uncertainty_id)
        require_q16("confidence_q16", self.confidence_q16)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Uncertainty":
        return cls(
            uncertainty_id=str(raw["uncertainty_id"]),
            target_id=str(raw["target_id"]),
            reason=UncertaintyReason(raw["reason"]),
            confidence_q16=int(raw["confidence_q16"]),
            evidence_ids=tuple(str(v) for v in raw.get("evidence_ids", ())),
        )


@dataclass(frozen=True)
class WorldEntity:
    entity_id: str
    display_name: str
    kind: EntityKind
    class_label: str
    transform: QuantizedTransform = field(default_factory=QuantizedTransform)
    material_id: str | None = None
    harmonic_signature: str | None = None
    attributes: dict[str, bool | int | str] = field(default_factory=dict)

    def validate(self) -> None:
        require_identifier("entity_id", self.entity_id)
        require_identifier("class_label", self.class_label)
        self.transform.validate()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "WorldEntity":
        return cls(
            entity_id=str(raw["entity_id"]),
            display_name=str(raw["display_name"]),
            kind=EntityKind(raw["kind"]),
            class_label=str(raw["class_label"]),
            transform=QuantizedTransform.from_dict(raw.get("transform", {})),
            material_id=raw.get("material_id"),
            harmonic_signature=raw.get("harmonic_signature"),
            attributes=dict(raw.get("attributes", {})),
        )


@dataclass(frozen=True)
class WorldRelation:
    relation_id: str
    kind: RelationKind
    subject_id: str
    object_id: str
    confidence_q16: int
    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        require_identifier("relation_id", self.relation_id)
        require_q16("confidence_q16", self.confidence_q16)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "WorldRelation":
        return cls(
            relation_id=str(raw["relation_id"]),
            kind=RelationKind(raw["kind"]),
            subject_id=str(raw["subject_id"]),
            object_id=str(raw["object_id"]),
            confidence_q16=int(raw["confidence_q16"]),
            evidence_ids=tuple(str(v) for v in raw.get("evidence_ids", ())),
        )


@dataclass(frozen=True)
class GeometryInvocation:
    family: GeometryFamily
    macro: GeometryMacro
    target_id: str
    parameters: dict[str, bool | int | str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "GeometryInvocation":
        return cls(
            family=GeometryFamily(raw["family"]),
            macro=GeometryMacro(raw["macro"]),
            target_id=str(raw["target_id"]),
            parameters=dict(raw.get("parameters", {})),
        )


@dataclass(frozen=True)
class WorldOperation:
    operation_id: str
    kind: OperationKind
    subject_id: str
    object_id: str | None = None
    relation_id: str | None = None
    camera_id: str | None = None
    material_id: str | None = None
    narrative_verb: NarrativeVerb | None = None
    geometry: GeometryInvocation | None = None
    parameters: dict[str, bool | int | str] = field(default_factory=dict)
    preconditions: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    capability_id: str | None = None
    capability_status: CapabilityStatus | None = None

    def validate(self) -> None:
        require_identifier("operation_id", self.operation_id)
        if self.kind is OperationKind.GEOMETRY_MACRO and self.geometry is None:
            raise WorldSchemaError("geometry_macro operation requires geometry")
        if self.kind is OperationKind.NARRATIVE_ACTION and self.narrative_verb is None:
            raise WorldSchemaError("narrative_action requires narrative_verb")
        if self.capability_id and self.capability_status is None:
            raise WorldSchemaError("capability_id requires capability_status")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "WorldOperation":
        geometry = raw.get("geometry")
        narrative = raw.get("narrative_verb")
        status = raw.get("capability_status")
        return cls(
            operation_id=str(raw["operation_id"]),
            kind=OperationKind(raw["kind"]),
            subject_id=str(raw["subject_id"]),
            object_id=raw.get("object_id"),
            relation_id=raw.get("relation_id"),
            camera_id=raw.get("camera_id"),
            material_id=raw.get("material_id"),
            narrative_verb=NarrativeVerb(narrative) if narrative else None,
            geometry=GeometryInvocation.from_dict(geometry) if geometry else None,
            parameters=dict(raw.get("parameters", {})),
            preconditions=tuple(str(v) for v in raw.get("preconditions", ())),
            evidence_ids=tuple(str(v) for v in raw.get("evidence_ids", ())),
            capability_id=raw.get("capability_id"),
            capability_status=CapabilityStatus(status) if status else None,
        )


@dataclass(frozen=True)
class WorldFrame:
    frame_id: str
    tick: int
    camera_id: str | None
    operation_ids: tuple[str, ...]
    observed_entity_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        require_identifier("frame_id", self.frame_id)
        if self.tick < 0:
            raise WorldSchemaError("frame tick must be non-negative")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "WorldFrame":
        return cls(
            frame_id=str(raw["frame_id"]),
            tick=int(raw["tick"]),
            camera_id=raw.get("camera_id"),
            operation_ids=tuple(str(v) for v in raw.get("operation_ids", ())),
            observed_entity_ids=tuple(str(v) for v in raw.get("observed_entity_ids", ())),
        )


@dataclass(frozen=True)
class DatasetPartition:
    split: HoldoutSplit
    object_class: str
    operation_family: str
    generator_family: str

    def validate(self) -> None:
        for name, value in (
            ("object_class", self.object_class),
            ("operation_family", self.operation_family),
            ("generator_family", self.generator_family),
        ):
            require_identifier(name, value)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "DatasetPartition":
        return cls(
            split=HoldoutSplit(raw["split"]),
            object_class=str(raw["object_class"]),
            operation_family=str(raw["operation_family"]),
            generator_family=str(raw["generator_family"]),
        )


@dataclass(frozen=True)
class WorldProgram:
    program_id: str
    world_id: str
    title: str
    entities: tuple[WorldEntity, ...]
    relations: tuple[WorldRelation, ...]
    operations: tuple[WorldOperation, ...]
    frames: tuple[WorldFrame, ...] = ()
    cameras: tuple[CameraState, ...] = ()
    materials: tuple[MaterialState, ...] = ()
    evidence: tuple[EvidenceBinding, ...] = ()
    uncertainty: tuple[Uncertainty, ...] = ()
    partition: DatasetPartition | None = None
    schema_version: str = WORLD_SCHEMA_VERSION

    def validate(self) -> None:
        if self.schema_version != WORLD_SCHEMA_VERSION:
            raise WorldSchemaError(f"unsupported schema version: {self.schema_version}")
        require_identifier("program_id", self.program_id)
        require_identifier("world_id", self.world_id)
        entity_ids = {entity.entity_id for entity in self.entities}
        if len(entity_ids) != len(self.entities):
            raise WorldSchemaError("duplicate entity IDs")
        material_ids = {material.material_id for material in self.materials}
        camera_ids = {camera.camera_id for camera in self.cameras}
        evidence_ids = {binding.evidence_id for binding in self.evidence}
        relation_ids = {relation.relation_id for relation in self.relations}
        operation_ids = {operation.operation_id for operation in self.operations}
        identifier_sets = (
            ("material", material_ids, len(self.materials)),
            ("camera", camera_ids, len(self.cameras)),
            ("evidence", evidence_ids, len(self.evidence)),
            ("relation", relation_ids, len(self.relations)),
            ("operation", operation_ids, len(self.operations)),
        )
        for label, identifiers, count in identifier_sets:
            if len(identifiers) != count:
                raise WorldSchemaError(f"duplicate {label} IDs")
        for item in self.entities:
            item.validate()
            if item.material_id and item.material_id not in material_ids:
                raise WorldSchemaError(f"unknown material: {item.material_id}")
        for item in self.materials:
            item.validate()
        for item in self.cameras:
            item.validate()
        for item in self.evidence:
            item.validate()
            if item.camera_id and item.camera_id not in camera_ids:
                raise WorldSchemaError(f"unknown evidence camera: {item.camera_id}")
        for item in self.relations:
            item.validate()
            if item.subject_id not in entity_ids or item.object_id not in entity_ids:
                raise WorldSchemaError(f"relation references unknown entity: {item.relation_id}")
            if any(value not in evidence_ids for value in item.evidence_ids):
                raise WorldSchemaError(f"relation references unknown evidence: {item.relation_id}")
        for item in self.operations:
            item.validate()
            if item.subject_id not in entity_ids:
                raise WorldSchemaError(f"operation subject is unknown: {item.subject_id}")
            if item.object_id and item.object_id not in entity_ids:
                raise WorldSchemaError(f"operation object is unknown: {item.object_id}")
            if item.relation_id and item.relation_id not in relation_ids:
                raise WorldSchemaError(f"operation relation is unknown: {item.relation_id}")
            if item.camera_id and item.camera_id not in camera_ids:
                raise WorldSchemaError(f"operation camera is unknown: {item.camera_id}")
            if item.material_id and item.material_id not in material_ids:
                raise WorldSchemaError(f"operation material is unknown: {item.material_id}")
            if item.geometry and item.geometry.target_id not in entity_ids:
                raise WorldSchemaError(f"geometry target is unknown: {item.geometry.target_id}")
            if any(value not in evidence_ids for value in item.evidence_ids):
                raise WorldSchemaError(f"operation references unknown evidence: {item.operation_id}")
        for item in self.frames:
            item.validate()
            if item.camera_id and item.camera_id not in camera_ids:
                raise WorldSchemaError(f"frame camera is unknown: {item.camera_id}")
            if any(value not in operation_ids for value in item.operation_ids):
                raise WorldSchemaError(f"frame references unknown operation: {item.frame_id}")
            if any(value not in entity_ids for value in item.observed_entity_ids):
                raise WorldSchemaError(f"frame references unknown entity: {item.frame_id}")
        for item in self.uncertainty:
            item.validate()
            valid_targets = entity_ids | relation_ids | operation_ids
            if item.target_id not in valid_targets:
                raise WorldSchemaError(f"uncertainty target is unknown: {item.target_id}")
            if any(value not in evidence_ids for value in item.evidence_ids):
                raise WorldSchemaError(f"uncertainty references unknown evidence: {item.uncertainty_id}")
        if self.partition:
            self.partition.validate()

    def to_dict(self) -> dict[str, Any]:
        return _primitive(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "WorldProgram":
        partition = raw.get("partition")
        program = cls(
            program_id=str(raw["program_id"]),
            world_id=str(raw["world_id"]),
            title=str(raw["title"]),
            entities=tuple(WorldEntity.from_dict(v) for v in raw.get("entities", ())),
            relations=tuple(WorldRelation.from_dict(v) for v in raw.get("relations", ())),
            operations=tuple(WorldOperation.from_dict(v) for v in raw.get("operations", ())),
            frames=tuple(WorldFrame.from_dict(v) for v in raw.get("frames", ())),
            cameras=tuple(CameraState.from_dict(v) for v in raw.get("cameras", ())),
            materials=tuple(MaterialState.from_dict(v) for v in raw.get("materials", ())),
            evidence=tuple(EvidenceBinding.from_dict(v) for v in raw.get("evidence", ())),
            uncertainty=tuple(Uncertainty.from_dict(v) for v in raw.get("uncertainty", ())),
            partition=DatasetPartition.from_dict(partition) if partition else None,
            schema_version=str(raw.get("schema_version", WORLD_SCHEMA_VERSION)),
        )
        program.validate()
        return program

    def canonical_json(self) -> str:
        self.validate()
        return canonical_json(self)

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
