"""Regression gates for the Primus typed world schema."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_schema.model import (
    CameraState,
    CapabilityStatus,
    DatasetPartition,
    EntityKind,
    EvidenceBinding,
    EvidenceKind,
    GeometryFamily,
    GeometryInvocation,
    GeometryMacro,
    HoldoutSplit,
    MaterialState,
    NarrativeVerb,
    OperationKind,
    ProjectionKind,
    QuantizedTransform,
    RelationKind,
    Uncertainty,
    UncertaintyReason,
    WorldEntity,
    WorldFrame,
    WorldOperation,
    WorldProgram,
    WorldRelation,
    WorldSchemaError,
)
from world_schema.s3v_bridge import (
    assert_lossless_round_trip,
    from_s3v_json,
    to_s3v_dict,
    to_s3v_json,
)
from world_schema.tokens import (
    BYTE_LIMIT,
    WORLD_VOCAB_SIZE,
    decode_program,
    encode_program,
    structural_program_signature,
    unique_program_coverage,
    vocabulary_manifest,
)


def sample_program(
    *,
    program_id: str = "program_one",
    subject_id: str = "entity_relic",
    class_label: str = "unknown_relic",
) -> WorldProgram:
    source_hash = hashlib.sha256(b"fixture observation").hexdigest()
    material = MaterialState(
        material_id="material_primary",
        role="surface",
        base_color_rgba8=(18, 32, 51, 255),
        metallic_q8=192,
        roughness_q8=64,
        emission_q8=12,
        compiler_hint="metal",
    )
    camera = CameraState(
        camera_id="camera_oblique",
        projection=ProjectionKind.PERSPECTIVE,
        transform=QuantizedTransform(
            translation_mm=(2100, -1700, 1300),
            rotation_centideg=(6300, 0, 5100),
        ),
        focal_length_micrometres=50_000,
        sensor_width_micrometres=36_000,
        image_width_px=512,
        image_height_px=512,
        near_mm=10,
        far_mm=100_000,
    )
    evidence = EvidenceBinding(
        evidence_id="evidence_front",
        kind=EvidenceKind.OBSERVED,
        source_uri="sha256://fixture-observation",
        source_sha256=source_hash,
        confidence_q16=60_000,
        frame_id="frame_one",
        camera_id=camera.camera_id,
    )
    entities = (
        WorldEntity(
            entity_id=subject_id,
            display_name="Relic",
            kind=EntityKind.OBJECT,
            class_label=class_label,
            transform=QuantizedTransform(scale_milli=(800, 1200, 600)),
            material_id=material.material_id,
            attributes={"editable": True, "lod": 1},
        ),
        WorldEntity(
            entity_id="entity_pedestal",
            display_name="Pedestal",
            kind=EntityKind.OBJECT,
            class_label="support_surface",
            transform=QuantizedTransform(translation_mm=(0, 0, -500)),
        ),
        WorldEntity(
            entity_id="entity_room",
            display_name="Room",
            kind=EntityKind.LOCATION,
            class_label="interior_space",
        ),
    )
    relation = WorldRelation(
        relation_id="relation_support",
        kind=RelationKind.SUPPORTS,
        subject_id="entity_pedestal",
        object_id=subject_id,
        confidence_q16=62_000,
        evidence_ids=(evidence.evidence_id,),
    )
    operations = (
        WorldOperation(
            operation_id="operation_geometry",
            kind=OperationKind.GEOMETRY_MACRO,
            subject_id=subject_id,
            geometry=GeometryInvocation(
                family=GeometryFamily.BOX_GRAMMAR,
                macro=GeometryMacro.EXTRUDE_FACE,
                target_id=subject_id,
                parameters={"distance_mm": 240},
            ),
            evidence_ids=(evidence.evidence_id,),
            capability_id="geometry_core_primitives",
            capability_status=CapabilityStatus.AVAILABLE,
        ),
        WorldOperation(
            operation_id="operation_support",
            kind=OperationKind.ADD_RELATION,
            subject_id="entity_pedestal",
            object_id=subject_id,
            relation_id=relation.relation_id,
        ),
        WorldOperation(
            operation_id="operation_observe",
            kind=OperationKind.OBSERVE,
            subject_id=subject_id,
            camera_id=camera.camera_id,
            evidence_ids=(evidence.evidence_id,),
        ),
        WorldOperation(
            operation_id="operation_look",
            kind=OperationKind.NARRATIVE_ACTION,
            subject_id=subject_id,
            object_id="entity_room",
            narrative_verb=NarrativeVerb.LOOK_AT,
        ),
    )
    frame = WorldFrame(
        frame_id="frame_one",
        tick=0,
        camera_id=camera.camera_id,
        operation_ids=tuple(operation.operation_id for operation in operations),
        observed_entity_ids=(subject_id, "entity_pedestal"),
    )
    uncertainty = Uncertainty(
        uncertainty_id="uncertainty_back",
        target_id=subject_id,
        reason=UncertaintyReason.UNOBSERVED,
        confidence_q16=18_000,
        evidence_ids=(evidence.evidence_id,),
    )
    program = WorldProgram(
        program_id=program_id,
        world_id="world_fixture",
        title="Domain-general fixture",
        entities=entities,
        relations=(relation,),
        operations=operations,
        frames=(frame,),
        cameras=(camera,),
        materials=(material,),
        evidence=(evidence,),
        uncertainty=(uncertainty,),
        partition=DatasetPartition(
            split=HoldoutSplit.HELD_OUT_COMPOSITION,
            object_class=class_label,
            operation_family="geometry_and_observation",
            generator_family="fixture_generator",
        ),
    )
    program.validate()
    return program


class WorldSchemaTests(unittest.TestCase):
    def test_canonical_json_round_trip_is_exact(self):
        program = sample_program()
        restored = WorldProgram.from_dict(json.loads(program.canonical_json()))
        self.assertEqual(restored, program)
        self.assertEqual(restored.sha256(), program.sha256())

    def test_four_k_token_stream_is_lossless_and_bounded(self):
        program = sample_program()
        encoded = encode_program(program)
        self.assertGreater(encoded.semantic_token_count, 0)
        self.assertGreater(encoded.payload_byte_count, 0)
        self.assertTrue(all(0 <= token < WORLD_VOCAB_SIZE for token in encoded.token_ids))
        self.assertLessEqual(BYTE_LIMIT, WORLD_VOCAB_SIZE)
        restored = decode_program(encoded.token_ids)
        self.assertEqual(restored, program)
        self.assertEqual(encoded.program_sha256, restored.sha256())
        manifest = vocabulary_manifest()
        self.assertEqual(manifest["vocabulary_size"], 4096)

    def test_schema_to_s3v_to_schema_is_lossless(self):
        program = sample_program()
        payload = to_s3v_json(program)
        s3v = json.loads(payload)
        self.assertEqual(s3v["version"], 1)
        self.assertEqual(set(s3v), {"version", "title", "created_at", "entities", "actions", "frames"})
        self.assertEqual(len(s3v["entities"]), len(program.entities))
        self.assertEqual(len(s3v["actions"]), len(program.operations))
        restored = from_s3v_json(payload)
        self.assertEqual(restored, program)
        assert_lossless_round_trip(program)

    def test_explicit_camera_pose_and_evidence_survive_s3v(self):
        program = sample_program()
        restored = from_s3v_json(to_s3v_json(program))
        camera = restored.cameras[0]
        self.assertEqual(camera.transform.translation_mm, (2100, -1700, 1300))
        self.assertEqual(camera.transform.rotation_centideg, (6300, 0, 5100))
        self.assertEqual(camera.focal_length_micrometres, 50_000)
        self.assertEqual(restored.evidence[0].camera_id, camera.camera_id)
        self.assertEqual(restored.uncertainty[0].reason, UncertaintyReason.UNOBSERVED)

    def test_structural_signature_ignores_names_and_object_class(self):
        original = sample_program()
        renamed = sample_program(
            program_id="program_two",
            subject_id="entity_artifact",
            class_label="unseen_machine",
        )
        self.assertEqual(
            structural_program_signature(original),
            structural_program_signature(renamed),
        )
        coverage = unique_program_coverage((original, renamed))
        self.assertEqual(coverage["programs"], 2)
        self.assertEqual(coverage["unique_programs"], 1)
        self.assertEqual(coverage["unique_program_fraction"], 0.5)

    def test_operation_order_changes_structural_signature(self):
        original = sample_program()
        reordered = replace(original, operations=tuple(reversed(original.operations)))
        reordered.validate()
        self.assertNotEqual(
            structural_program_signature(original),
            structural_program_signature(reordered),
        )

    def test_unknown_entity_reference_is_rejected(self):
        program = sample_program()
        broken = replace(
            program,
            relations=(
                replace(program.relations[0], object_id="entity_missing"),
            ),
        )
        with self.assertRaises(WorldSchemaError):
            broken.validate()

    def test_capability_status_is_explicit_in_s3v_action_receipt(self):
        program = sample_program()
        s3v = to_s3v_dict(program)
        notes = [json.loads(action["notes"]) for action in s3v["actions"]]
        geometry = next(note for note in notes if note["kind"] == "geometry_macro")
        self.assertEqual(geometry["capability_status"], "available")
        self.assertEqual(geometry["capability_id"], "geometry_core_primitives")


if __name__ == "__main__":
    unittest.main(verbosity=2)
