"""Lossless bridge between the Primus world schema and ChronoSophia S3V v1.

S3V remains the compiler-facing artifact. A compact, versioned canonical
WorldProgram envelope is carried in the document title so state that S3V v1 does
not yet model (explicit cameras, evidence, uncertainty, quantized transforms)
is preserved without inventing unsupported S3V fields. Entities, actions, and
frames are also lowered into their native S3V counterparts for interoperability.
"""
from __future__ import annotations

import base64
import binascii
import json
import uuid
import zlib
from typing import Any

from .model import EntityKind, NarrativeVerb, OperationKind, WorldProgram


S3V_VERSION = 1
TYPED_ACTION_OPERATION_SCHEMA_VERSION = 1
BRIDGE_PREFIX = "world_core_v1:"
BRIDGE_UUID_NAMESPACE = uuid.UUID("a1d6ad78-7d7c-4a9e-980a-322237eb5ef7")


class S3vBridgeError(ValueError):
    """Raised when S3V cannot satisfy the lossless bridge contract."""


def _pack(program: WorldProgram) -> str:
    compressed = zlib.compress(program.canonical_json().encode("utf-8"), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return f"{BRIDGE_PREFIX}{encoded}"


def _unpack(title: str) -> WorldProgram:
    if not title.startswith(BRIDGE_PREFIX):
        raise S3vBridgeError("S3V title does not carry a world_core_v1 envelope")
    encoded = title[len(BRIDGE_PREFIX) :]
    padded = encoded + "=" * (-len(encoded) % 4)
    try:
        raw = zlib.decompress(base64.urlsafe_b64decode(padded)).decode("utf-8")
        return WorldProgram.from_dict(json.loads(raw))
    except (
        ValueError,
        binascii.Error,
        zlib.error,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        raise S3vBridgeError("invalid world_core_v1 envelope") from error


def _entity_kind(kind: EntityKind) -> str:
    return kind.value


def _s3v_verb(operation) -> str | dict[str, str]:
    if operation.kind is OperationKind.NARRATIVE_ACTION and operation.narrative_verb:
        return operation.narrative_verb.value
    if operation.geometry:
        return {"other": operation.geometry.macro.value}
    return {"other": operation.kind.value}


def _typed_action_operation(operation) -> dict[str, Any] | None:
    """Emit declared geometry meaning directly; never derive it from notes."""

    if operation.geometry is None:
        return None
    if operation.kind is not OperationKind.GEOMETRY_MACRO:
        raise S3vBridgeError("geometry invocation requires geometry_macro operation kind")

    parameters: dict[str, bool | int | str] = {}
    for key, value in sorted(operation.geometry.parameters.items()):
        if not isinstance(key, str) or not key:
            raise S3vBridgeError("geometry parameter names must be nonempty strings")
        if type(value) not in (bool, int, str):
            raise S3vBridgeError("geometry parameters must be declared primitive values")
        parameters[key] = value

    return {
        "schema_version": TYPED_ACTION_OPERATION_SCHEMA_VERSION,
        "kind": operation.kind.value,
        "macro": operation.geometry.macro.value,
        "family": operation.geometry.family.value,
        "subject_id": operation.subject_id,
        "target_id": operation.geometry.target_id,
        "parameters": parameters,
    }


def _action_uuid(program: WorldProgram, operation_id: str) -> str:
    return str(uuid.uuid5(BRIDGE_UUID_NAMESPACE, f"{program.program_id}:op:{operation_id}"))


def _frame_uuid(program: WorldProgram, frame_id: str) -> str:
    return str(uuid.uuid5(BRIDGE_UUID_NAMESPACE, f"{program.program_id}:frame:{frame_id}"))


def _operation_notes(operation) -> str:
    payload = {
        "bridge": "world_core_v1",
        "operation_id": operation.operation_id,
        "kind": operation.kind.value,
        "capability_id": operation.capability_id,
        "capability_status": (
            operation.capability_status.value if operation.capability_status else None
        ),
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def to_s3v_dict(program: WorldProgram) -> dict[str, Any]:
    """Lower a validated program into a canonical S3V-v1-compatible dictionary."""

    program.validate()
    action_id_by_operation = {
        operation.operation_id: _action_uuid(program, operation.operation_id)
        for operation in program.operations
    }
    entities = {
        entity.entity_id: {
            "id": entity.entity_id,
            "display_name": entity.display_name,
            "kind": _entity_kind(entity.kind),
            "description": json.dumps(
                {
                    "world_core": {
                        "class_label": entity.class_label,
                        "transform": {
                            "translation_mm": entity.transform.translation_mm,
                            "rotation_centideg": entity.transform.rotation_centideg,
                            "scale_milli": entity.transform.scale_milli,
                        },
                        "material_id": entity.material_id,
                        "attributes": entity.attributes,
                    }
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ),
            "harmonic_signature": entity.harmonic_signature,
        }
        for entity in program.entities
    }

    actions = []
    for operation in program.operations:
        effects = []
        if operation.relation_id:
            relation = next(
                relation
                for relation in program.relations
                if relation.relation_id == operation.relation_id
            )
            effects.append(
                {
                    "name": relation.kind.value,
                    "args": [relation.subject_id, relation.object_id],
                    "value": {"confidence_q16": relation.confidence_q16},
                    "negated": operation.kind is OperationKind.REMOVE_RELATION,
                }
            )
        actions.append(
            {
                "action_id": action_id_by_operation[operation.operation_id],
                "subject": operation.subject_id,
                "object": operation.object_id,
                "verb": _s3v_verb(operation),
                "operation": _typed_action_operation(operation),
                "preconditions": [
                    {
                        "name": "world_precondition",
                        "args": [operation.subject_id, f"literal:{precondition}"],
                        "value": None,
                        "negated": False,
                    }
                    for precondition in operation.preconditions
                ],
                "effects": effects,
                "emotional_tone": {},
                "cinematic": {
                    "camera": "medium_shot",
                    "lighting": "natural",
                    "pacing": "normal",
                    "duration_s": None,
                },
                "notes": _operation_notes(operation),
            }
        )

    frames = [
        {
            "frame_id": _frame_uuid(program, frame.frame_id),
            "actions": [
                next(
                    action
                    for action in actions
                    if action["action_id"] == action_id_by_operation[operation_id]
                )
                for operation_id in frame.operation_ids
            ],
            "cinematic_directive": (
                f"camera:{frame.camera_id}" if frame.camera_id else None
            ),
        }
        for frame in program.frames
    ]

    return {
        "version": S3V_VERSION,
        "title": _pack(program),
        "created_at": "1970-01-01T00:00:00Z",
        "entities": entities,
        "actions": actions,
        "frames": frames,
    }


def from_s3v_dict(s3v: dict[str, Any]) -> WorldProgram:
    """Recover the exact WorldProgram carried by a bridge-authored S3V."""

    if int(s3v.get("version", -1)) != S3V_VERSION:
        raise S3vBridgeError(f"unsupported S3V version: {s3v.get('version')}")
    if not isinstance(s3v.get("entities"), dict):
        raise S3vBridgeError("S3V entities must be a keyed object")
    if not isinstance(s3v.get("actions"), list) or not isinstance(s3v.get("frames"), list):
        raise S3vBridgeError("S3V actions and frames must be arrays")
    program = _unpack(str(s3v.get("title", "")))
    program.validate()
    return program


def to_s3v_json(program: WorldProgram) -> str:
    return json.dumps(to_s3v_dict(program), indent=2, sort_keys=True) + "\n"


def from_s3v_json(payload: str) -> WorldProgram:
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as error:
        raise S3vBridgeError("S3V payload is not valid JSON") from error
    return from_s3v_dict(raw)


def assert_lossless_round_trip(program: WorldProgram) -> None:
    recovered = from_s3v_json(to_s3v_json(program))
    if recovered.canonical_json() != program.canonical_json():
        raise S3vBridgeError("WorldProgram changed during schema -> S3V -> schema")
