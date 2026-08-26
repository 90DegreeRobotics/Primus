"""Finite 4K token vocabulary and lossless codec for ``WorldProgram``.

The stream carries typed semantic markers followed by a canonical byte payload.
Semantic markers make the operation/entity/relation structure directly learnable;
the byte payload keeps the representation exactly round-trippable without an
open-ended tokenizer or object-specific vocabulary.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .model import (
    CapabilityStatus,
    EntityKind,
    EvidenceKind,
    GeometryFamily,
    GeometryMacro,
    HoldoutSplit,
    NarrativeVerb,
    OperationKind,
    ProjectionKind,
    RelationKind,
    UncertaintyReason,
    WORLD_VOCAB_SIZE,
    WorldProgram,
)


PAD = 0
PROGRAM_BOS = 1
PROGRAM_EOS = 2
SEMANTIC_BOS = 3
SEMANTIC_EOS = 4
PAYLOAD_BOS = 5
PAYLOAD_EOS = 6
ENTITY = 7
RELATION = 8
OPERATION = 9
FRAME = 10
CAMERA = 11
MATERIAL = 12
EVIDENCE = 13
UNCERTAINTY = 14
PARTITION = 15
BYTE_BASE = 1024
BYTE_LIMIT = BYTE_BASE + 256


def _enum_values(enum_type: type[Enum]) -> list[str]:
    return [str(member.value) for member in enum_type]


_TYPED_VALUES = sorted(
    {
        *(_enum_values(EntityKind)),
        *(_enum_values(RelationKind)),
        *(_enum_values(GeometryFamily)),
        *(_enum_values(GeometryMacro)),
        *(_enum_values(OperationKind)),
        *(_enum_values(NarrativeVerb)),
        *(_enum_values(EvidenceKind)),
        *(_enum_values(UncertaintyReason)),
        *(_enum_values(ProjectionKind)),
        *(_enum_values(CapabilityStatus)),
        *(_enum_values(HoldoutSplit)),
    }
)
TYPED_TOKEN_BASE = 64
TYPED_TOKEN_BY_VALUE = {
    value: TYPED_TOKEN_BASE + index for index, value in enumerate(_TYPED_VALUES)
}
VALUE_BY_TYPED_TOKEN = {token: value for value, token in TYPED_TOKEN_BY_VALUE.items()}

if max(VALUE_BY_TYPED_TOKEN, default=0) >= BYTE_BASE:
    raise RuntimeError("typed token inventory overlaps the byte-token band")
if BYTE_LIMIT > WORLD_VOCAB_SIZE:
    raise RuntimeError("byte-token band exceeds the declared world vocabulary")


@dataclass(frozen=True)
class EncodedWorldProgram:
    token_ids: tuple[int, ...]
    semantic_token_count: int
    payload_byte_count: int
    program_sha256: str
    structural_signature: str


def _semantic_tokens(program: WorldProgram) -> list[int]:
    tokens = [SEMANTIC_BOS]
    for entity in program.entities:
        tokens.extend((ENTITY, TYPED_TOKEN_BY_VALUE[entity.kind.value]))
    for relation in program.relations:
        tokens.extend((RELATION, TYPED_TOKEN_BY_VALUE[relation.kind.value]))
    for operation in program.operations:
        tokens.extend((OPERATION, TYPED_TOKEN_BY_VALUE[operation.kind.value]))
        if operation.narrative_verb:
            tokens.append(TYPED_TOKEN_BY_VALUE[operation.narrative_verb.value])
        if operation.geometry:
            tokens.extend(
                (
                    TYPED_TOKEN_BY_VALUE[operation.geometry.family.value],
                    TYPED_TOKEN_BY_VALUE[operation.geometry.macro.value],
                )
            )
        if operation.capability_status:
            tokens.append(TYPED_TOKEN_BY_VALUE[operation.capability_status.value])
    for camera in program.cameras:
        tokens.extend((CAMERA, TYPED_TOKEN_BY_VALUE[camera.projection.value]))
    tokens.extend([MATERIAL] * len(program.materials))
    tokens.extend([FRAME] * len(program.frames))
    for evidence in program.evidence:
        tokens.extend((EVIDENCE, TYPED_TOKEN_BY_VALUE[evidence.kind.value]))
    for uncertainty in program.uncertainty:
        tokens.extend(
            (UNCERTAINTY, TYPED_TOKEN_BY_VALUE[uncertainty.reason.value])
        )
    if program.partition:
        tokens.extend(
            (PARTITION, TYPED_TOKEN_BY_VALUE[program.partition.split.value])
        )
    tokens.append(SEMANTIC_EOS)
    return tokens


def encode_program(program: WorldProgram) -> EncodedWorldProgram:
    program.validate()
    canonical = program.canonical_json()
    payload = canonical.encode("utf-8")
    semantic = _semantic_tokens(program)
    token_ids = (
        PROGRAM_BOS,
        *semantic,
        PAYLOAD_BOS,
        *(BYTE_BASE + byte for byte in payload),
        PAYLOAD_EOS,
        PROGRAM_EOS,
    )
    if any(token < 0 or token >= WORLD_VOCAB_SIZE for token in token_ids):
        raise ValueError("encoded program contains a token outside the 4K vocabulary")
    return EncodedWorldProgram(
        token_ids=tuple(token_ids),
        semantic_token_count=len(semantic),
        payload_byte_count=len(payload),
        program_sha256=program.sha256(),
        structural_signature=structural_program_signature(program),
    )


def decode_program(token_ids: Iterable[int]) -> WorldProgram:
    tokens = tuple(int(token) for token in token_ids)
    if not tokens or tokens[0] != PROGRAM_BOS or tokens[-1] != PROGRAM_EOS:
        raise ValueError("world token stream is missing program boundaries")
    try:
        start = tokens.index(PAYLOAD_BOS) + 1
        end = tokens.index(PAYLOAD_EOS, start)
    except ValueError as error:
        raise ValueError("world token stream is missing payload boundaries") from error
    byte_values = []
    for token in tokens[start:end]:
        if not BYTE_BASE <= token < BYTE_LIMIT:
            raise ValueError(f"non-byte token in canonical payload: {token}")
        byte_values.append(token - BYTE_BASE)
    raw = json.loads(bytes(byte_values).decode("utf-8"))
    return WorldProgram.from_dict(raw)


def _normalized_reference_map(program: WorldProgram) -> dict[str, str]:
    return {
        entity.entity_id: f"entity_{index}"
        for index, entity in enumerate(program.entities)
    }


def structural_program_signature(program: WorldProgram) -> str:
    """Hash program structure while ignoring names and concrete object class.

    This detects repeated generator templates even when prompts, IDs, display
    names, or object classes differ. Operation order, relation structure,
    compiler macro families, and quantized parameter keys/values remain visible.
    """

    program.validate()
    references = _normalized_reference_map(program)

    def ref(value: str | None) -> str | None:
        if value is None:
            return None
        return references.get(value, value)

    normalized = {
        "entities": [
            {
                "ref": ref(entity.entity_id),
                "kind": entity.kind.value,
                "transform": {
                    "translation_mm": entity.transform.translation_mm,
                    "rotation_centideg": entity.transform.rotation_centideg,
                    "scale_milli": entity.transform.scale_milli,
                },
                "has_material": entity.material_id is not None,
                "attribute_keys": sorted(entity.attributes),
            }
            for entity in program.entities
        ],
        "relations": [
            {
                "kind": relation.kind.value,
                "subject": ref(relation.subject_id),
                "object": ref(relation.object_id),
            }
            for relation in program.relations
        ],
        "operations": [
            {
                "kind": operation.kind.value,
                "subject": ref(operation.subject_id),
                "object": ref(operation.object_id),
                "narrative_verb": (
                    operation.narrative_verb.value
                    if operation.narrative_verb
                    else None
                ),
                "geometry": (
                    {
                        "family": operation.geometry.family.value,
                        "macro": operation.geometry.macro.value,
                        "target": ref(operation.geometry.target_id),
                        "parameters": operation.geometry.parameters,
                    }
                    if operation.geometry
                    else None
                ),
                "parameter_keys": sorted(operation.parameters),
                "capability_status": (
                    operation.capability_status.value
                    if operation.capability_status
                    else None
                ),
            }
            for operation in program.operations
        ],
        "frames": [
            {
                "tick": frame.tick,
                "operation_count": len(frame.operation_ids),
                "observed_entity_count": len(frame.observed_entity_ids),
                "has_camera": frame.camera_id is not None,
            }
            for frame in program.frames
        ],
    }
    encoded = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def unique_program_coverage(programs: Iterable[WorldProgram]) -> dict[str, int | float]:
    signatures = [structural_program_signature(program) for program in programs]
    total = len(signatures)
    unique = len(set(signatures))
    return {
        "programs": total,
        "unique_programs": unique,
        "duplicate_programs": total - unique,
        "unique_program_fraction": unique / total if total else 0.0,
    }


def vocabulary_manifest() -> dict[str, object]:
    return {
        "vocabulary_size": WORLD_VOCAB_SIZE,
        "fixed_control_tokens": {
            "pad": PAD,
            "program_bos": PROGRAM_BOS,
            "program_eos": PROGRAM_EOS,
            "semantic_bos": SEMANTIC_BOS,
            "semantic_eos": SEMANTIC_EOS,
            "payload_bos": PAYLOAD_BOS,
            "payload_eos": PAYLOAD_EOS,
        },
        "typed_tokens": dict(sorted(TYPED_TOKEN_BY_VALUE.items())),
        "byte_band": {"start": BYTE_BASE, "end_exclusive": BYTE_LIMIT},
        "reserved": [
            {"start": 16, "end_exclusive": 64, "purpose": "future control"},
            {
                "start": max(VALUE_BY_TYPED_TOKEN, default=63) + 1,
                "end_exclusive": BYTE_BASE,
                "purpose": "future typed and quantized symbols",
            },
            {
                "start": BYTE_LIMIT,
                "end_exclusive": WORLD_VOCAB_SIZE,
                "purpose": "future learned world symbols",
            },
        ],
    }
