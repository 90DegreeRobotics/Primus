"""Deterministic, evidence-labeled world-trajectory dataset generation.

This module is Stage 2 data infrastructure. It emits validated ``WorldProgram``
trajectories with whole-family holdouts and deterministic evidence manifests. It
does not train a model, execute a renderer, or authorize checkpoint promotion.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import shutil
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .model import (
    WORLD_SCHEMA_VERSION,
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
from .s3v_bridge import assert_lossless_round_trip
from .tokens import encode_program, unique_program_coverage


GENERATOR_VERSION = "1.0.0"
DATASET_FILENAME = "world_trajectories.jsonl"
MANIFEST_FILENAME = "world_trajectories.manifest.json"

TRAIN_OBJECT_CLASSES = ("chair", "lamp", "bowl", "tower")
HELD_OUT_OBJECT_CLASS = "relic"
TRAIN_OPERATION_FAMILIES = (
    "box_dynamics",
    "lathe_dynamics",
    "compound_dynamics",
)
HELD_OUT_OPERATION_FAMILY = "sweep_dynamics"
HELD_OUT_COMPOSITION = ("chair", "lathe_dynamics")

_OPERATION_SPECS: dict[str, tuple[GeometryFamily, GeometryMacro, str]] = {
    "box_dynamics": (
        GeometryFamily.BOX_GRAMMAR,
        GeometryMacro.EXTRUDE_FACE,
        "parametric_box_v1",
    ),
    "lathe_dynamics": (
        GeometryFamily.LATHE,
        GeometryMacro.LATHE_PROFILE,
        "revolved_profile_v1",
    ),
    "compound_dynamics": (
        GeometryFamily.COMPOUND,
        GeometryMacro.ASSEMBLE_PARTS,
        "assembled_parts_v1",
    ),
    "sweep_dynamics": (
        GeometryFamily.SWEEP,
        GeometryMacro.SWEEP_PROFILE,
        "swept_profile_v1",
    ),
}

# The first entries cover every train object class and operation family while
# deliberately excluding the held-out (chair, lathe_dynamics) composition.
_TRAINING_SCHEDULE = (
    ("chair", "box_dynamics"),
    ("lamp", "lathe_dynamics"),
    ("bowl", "compound_dynamics"),
    ("tower", "box_dynamics"),
    ("lamp", "compound_dynamics"),
    ("bowl", "lathe_dynamics"),
    ("tower", "compound_dynamics"),
    ("chair", "compound_dynamics"),
)


class TrajectoryDatasetError(ValueError):
    """Raised when a generated dataset violates its Stage 2 contract."""


@dataclass(frozen=True)
class TrajectoryGeneratorConfig:
    """Bounded deterministic dataset configuration."""

    seed: int = 20_260_826
    train_count: int = 12
    held_out_object_count: int = 3
    held_out_operation_count: int = 3
    held_out_composition_count: int = 3

    def validate(self) -> None:
        if self.seed < 0:
            raise TrajectoryDatasetError("seed must be non-negative")
        if self.train_count < len(_TRAINING_SCHEDULE):
            raise TrajectoryDatasetError(
                f"train_count must be at least {len(_TRAINING_SCHEDULE)} to cover "
                "every training family and isolate the composition holdout"
            )
        for field_name in (
            "held_out_object_count",
            "held_out_operation_count",
            "held_out_composition_count",
        ):
            if getattr(self, field_name) < 1:
                raise TrajectoryDatasetError(f"{field_name} must be at least 1")

    @property
    def program_count(self) -> int:
        return (
            self.train_count
            + self.held_out_object_count
            + self.held_out_operation_count
            + self.held_out_composition_count
        )


@dataclass(frozen=True)
class GeneratedTrajectoryDataset:
    """In-memory deterministic dataset and evidence summary."""

    programs: tuple[WorldProgram, ...]
    manifest: dict[str, Any]

    def jsonl_bytes(self) -> bytes:
        return b"".join(
            program.canonical_json().encode("utf-8") + b"\n"
            for program in self.programs
        )


@dataclass(frozen=True)
class DatasetWriteReceipt:
    """Hash receipt for an atomically published local dataset."""

    output_dir: str
    dataset_path: str
    manifest_path: str
    dataset_sha256: str
    manifest_sha256: str
    program_count: int

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


def _stable_json(value: Any, *, pretty: bool = False) -> str:
    options: dict[str, Any] = {
        "ensure_ascii": True,
        "sort_keys": True,
    }
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return json.dumps(value, **options)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _source_hash(payload: dict[str, Any]) -> str:
    return _sha256_bytes(_stable_json(payload).encode("utf-8"))


def _rng_for(seed: int, split: HoldoutSplit, index: int) -> random.Random:
    digest = hashlib.sha256(
        f"{seed}:{split.value}:{index}".encode("utf-8")
    ).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _training_pair(index: int) -> tuple[str, str]:
    return _TRAINING_SCHEDULE[index % len(_TRAINING_SCHEDULE)]


def _partition_for(
    split: HoldoutSplit,
    index: int,
) -> DatasetPartition:
    if split is HoldoutSplit.TRAIN:
        object_class, operation_family = _training_pair(index)
        generator_family = _OPERATION_SPECS[operation_family][2]
    elif split is HoldoutSplit.HELD_OUT_OBJECT_CLASS:
        object_class = HELD_OUT_OBJECT_CLASS
        operation_family = TRAIN_OPERATION_FAMILIES[
            index % len(TRAIN_OPERATION_FAMILIES)
        ]
        generator_family = _OPERATION_SPECS[operation_family][2]
    elif split is HoldoutSplit.HELD_OUT_OPERATION_FAMILY:
        object_class = TRAIN_OBJECT_CLASSES[index % len(TRAIN_OBJECT_CLASSES)]
        operation_family = HELD_OUT_OPERATION_FAMILY
        generator_family = _OPERATION_SPECS[operation_family][2]
    elif split is HoldoutSplit.HELD_OUT_COMPOSITION:
        object_class, operation_family = HELD_OUT_COMPOSITION
        generator_family = "composed_revolution_support_v1"
    else:
        raise TrajectoryDatasetError(f"unsupported trajectory split: {split.value}")
    return DatasetPartition(
        split=split,
        object_class=object_class,
        operation_family=operation_family,
        generator_family=generator_family,
    )


def _identifier(prefix: str, split: HoldoutSplit, index: int) -> str:
    return f"{prefix}_{split.value}_{index:05d}"


def _make_program(
    *,
    config: TrajectoryGeneratorConfig,
    split: HoldoutSplit,
    index: int,
) -> WorldProgram:
    partition = _partition_for(split, index)
    rng = _rng_for(config.seed, split, index)
    geometry_family, geometry_macro, _ = _OPERATION_SPECS[
        partition.operation_family
    ]

    subject_id = "entity_subject"
    actor_id = "entity_actor"
    support_id = "entity_support"
    room_id = "entity_room"
    material_id = "material_subject"
    camera_start_id = "camera_start"
    camera_end_id = "camera_end"
    frame_start_id = "frame_start"
    frame_move_id = "frame_move"
    frame_end_id = "frame_end"

    base_x = rng.randint(-900, 900)
    base_y = rng.randint(-900, 900)
    base_z = rng.randint(120, 720)
    delta_x = rng.randint(180, 620)
    delta_y = rng.randint(-240, 240)
    delta_z = rng.randint(40, 260)
    geometry_extent = rng.randint(120, 680)
    bevel_q = rng.randint(8, 72)
    start_yaw = rng.randint(-18_000, 18_000)
    end_yaw = start_yaw + rng.choice((-4500, -3000, 3000, 4500))

    generated_descriptor = {
        "generator_version": GENERATOR_VERSION,
        "seed": config.seed,
        "split": split.value,
        "index": index,
        "object_class": partition.object_class,
        "operation_family": partition.operation_family,
        "initial_translation_mm": [base_x, base_y, base_z],
    }
    inferred_descriptor = {
        **generated_descriptor,
        "transition_delta_mm": [delta_x, delta_y, delta_z],
        "relation_after": "near",
    }
    generated_evidence = EvidenceBinding(
        evidence_id="evidence_generated_start",
        kind=EvidenceKind.GENERATED,
        source_uri=(
            f"urn:neurocognica:stage2:{config.seed}:{split.value}:{index}:start"
        ),
        source_sha256=_source_hash(generated_descriptor),
        confidence_q16=52_000,
        frame_id=frame_start_id,
        camera_id=camera_start_id,
    )
    inferred_evidence = EvidenceBinding(
        evidence_id="evidence_inferred_transition",
        kind=EvidenceKind.INFERRED,
        source_uri=(
            f"urn:neurocognica:stage2:{config.seed}:{split.value}:{index}:transition"
        ),
        source_sha256=_source_hash(inferred_descriptor),
        confidence_q16=43_000,
        frame_id=frame_end_id,
        camera_id=camera_end_id,
    )

    material = MaterialState(
        material_id=material_id,
        role="surface",
        base_color_rgba8=(
            rng.randint(24, 220),
            rng.randint(24, 220),
            rng.randint(24, 220),
            255,
        ),
        metallic_q8=rng.randint(0, 220),
        roughness_q8=rng.randint(24, 224),
        compiler_hint="generated_material",
    )
    cameras = (
        CameraState(
            camera_id=camera_start_id,
            projection=ProjectionKind.PERSPECTIVE,
            transform=QuantizedTransform(
                translation_mm=(base_x + 1800, base_y - 1500, base_z + 900),
                rotation_centideg=(6200, 0, start_yaw),
            ),
            focal_length_micrometres=50_000,
            sensor_width_micrometres=36_000,
            image_width_px=512,
            image_height_px=512,
            near_mm=10,
            far_mm=100_000,
        ),
        CameraState(
            camera_id=camera_end_id,
            projection=ProjectionKind.PERSPECTIVE,
            transform=QuantizedTransform(
                translation_mm=(
                    base_x + delta_x + 1500,
                    base_y + delta_y - 1200,
                    base_z + delta_z + 760,
                ),
                rotation_centideg=(5800, 0, end_yaw),
            ),
            focal_length_micrometres=45_000,
            sensor_width_micrometres=36_000,
            image_width_px=512,
            image_height_px=512,
            near_mm=10,
            far_mm=100_000,
        ),
    )
    entities = (
        WorldEntity(
            entity_id=subject_id,
            display_name=f"Generated {partition.object_class}",
            kind=EntityKind.OBJECT,
            class_label=partition.object_class,
            transform=QuantizedTransform(
                translation_mm=(base_x, base_y, base_z),
                rotation_centideg=(0, 0, start_yaw),
                scale_milli=(
                    rng.randint(650, 1450),
                    rng.randint(650, 1450),
                    rng.randint(650, 1450),
                ),
            ),
            material_id=material_id,
            attributes={
                "editable": True,
                "trajectory_seed": config.seed,
            },
        ),
        WorldEntity(
            entity_id=actor_id,
            display_name="Trajectory actor",
            kind=EntityKind.CHARACTER,
            class_label="agent",
            transform=QuantizedTransform(
                translation_mm=(base_x - 900, base_y, base_z)
            ),
        ),
        WorldEntity(
            entity_id=support_id,
            display_name="Support surface",
            kind=EntityKind.OBJECT,
            class_label="support_surface",
            transform=QuantizedTransform(
                translation_mm=(base_x, base_y, base_z - 240),
                scale_milli=(1600, 1600, 300),
            ),
        ),
        WorldEntity(
            entity_id=room_id,
            display_name="Generated room",
            kind=EntityKind.LOCATION,
            class_label="interior_space",
        ),
    )
    relations = (
        WorldRelation(
            relation_id="relation_support",
            kind=RelationKind.SUPPORTS,
            subject_id=support_id,
            object_id=subject_id,
            confidence_q16=54_000,
            evidence_ids=(generated_evidence.evidence_id,),
        ),
        WorldRelation(
            relation_id="relation_near",
            kind=RelationKind.NEAR,
            subject_id=actor_id,
            object_id=subject_id,
            confidence_q16=43_000,
            evidence_ids=(inferred_evidence.evidence_id,),
        ),
    )

    operations = (
        WorldOperation(
            operation_id="operation_geometry",
            kind=OperationKind.GEOMETRY_MACRO,
            subject_id=subject_id,
            geometry=GeometryInvocation(
                family=geometry_family,
                macro=geometry_macro,
                target_id=subject_id,
                parameters={
                    "extent_mm": geometry_extent,
                    "bevel_q": bevel_q,
                    "variant": index % 5,
                },
            ),
            evidence_ids=(generated_evidence.evidence_id,),
            capability_id="geometry_core_primitives",
            capability_status=CapabilityStatus.AVAILABLE,
        ),
        WorldOperation(
            operation_id="operation_add_support",
            kind=OperationKind.ADD_RELATION,
            subject_id=support_id,
            object_id=subject_id,
            relation_id="relation_support",
            evidence_ids=(generated_evidence.evidence_id,),
        ),
        WorldOperation(
            operation_id="operation_observe_start",
            kind=OperationKind.OBSERVE,
            subject_id=subject_id,
            camera_id=camera_start_id,
            evidence_ids=(generated_evidence.evidence_id,),
        ),
        WorldOperation(
            operation_id="operation_move",
            kind=OperationKind.SET_TRANSFORM,
            subject_id=subject_id,
            parameters={
                "delta_x_mm": delta_x,
                "delta_y_mm": delta_y,
                "delta_z_mm": delta_z,
                "target_tick": 1,
            },
            evidence_ids=(inferred_evidence.evidence_id,),
        ),
        WorldOperation(
            operation_id="operation_set_camera",
            kind=OperationKind.SET_CAMERA,
            subject_id=actor_id,
            camera_id=camera_end_id,
            parameters={"target_tick": 1},
        ),
        WorldOperation(
            operation_id="operation_approach",
            kind=OperationKind.NARRATIVE_ACTION,
            subject_id=actor_id,
            object_id=subject_id,
            narrative_verb=NarrativeVerb.APPROACH,
            parameters={"distance_mm": rng.randint(300, 900)},
            evidence_ids=(inferred_evidence.evidence_id,),
        ),
        WorldOperation(
            operation_id="operation_remove_support",
            kind=OperationKind.REMOVE_RELATION,
            subject_id=support_id,
            object_id=subject_id,
            relation_id="relation_support",
            evidence_ids=(inferred_evidence.evidence_id,),
        ),
        WorldOperation(
            operation_id="operation_add_near",
            kind=OperationKind.ADD_RELATION,
            subject_id=actor_id,
            object_id=subject_id,
            relation_id="relation_near",
            evidence_ids=(inferred_evidence.evidence_id,),
        ),
        WorldOperation(
            operation_id="operation_observe_end",
            kind=OperationKind.OBSERVE,
            subject_id=subject_id,
            camera_id=camera_end_id,
            evidence_ids=(inferred_evidence.evidence_id,),
        ),
    )
    frames = (
        WorldFrame(
            frame_id=frame_start_id,
            tick=0,
            camera_id=camera_start_id,
            operation_ids=(
                "operation_geometry",
                "operation_add_support",
                "operation_observe_start",
            ),
            observed_entity_ids=(subject_id, support_id, actor_id),
        ),
        WorldFrame(
            frame_id=frame_move_id,
            tick=1,
            camera_id=camera_end_id,
            operation_ids=(
                "operation_move",
                "operation_set_camera",
                "operation_approach",
            ),
            observed_entity_ids=(subject_id, actor_id),
        ),
        WorldFrame(
            frame_id=frame_end_id,
            tick=2,
            camera_id=camera_end_id,
            operation_ids=(
                "operation_remove_support",
                "operation_add_near",
                "operation_observe_end",
            ),
            observed_entity_ids=(subject_id, actor_id, room_id),
        ),
    )
    uncertainty = (
        Uncertainty(
            uncertainty_id="uncertainty_transition",
            target_id="operation_move",
            reason=UncertaintyReason.EXTRAPOLATED,
            confidence_q16=22_000,
            evidence_ids=(inferred_evidence.evidence_id,),
        ),
    )
    program = WorldProgram(
        program_id=_identifier("trajectory", split, index),
        world_id=_identifier("world", split, index),
        title=(
            f"Stage 2 {partition.object_class} {partition.operation_family} "
            f"trajectory {index}"
        ),
        entities=entities,
        relations=relations,
        operations=operations,
        frames=frames,
        cameras=cameras,
        materials=(material,),
        evidence=(generated_evidence, inferred_evidence),
        uncertainty=uncertainty,
        partition=partition,
    )
    program.validate()
    assert_lossless_round_trip(program)
    return program


def _iter_requested_programs(
    config: TrajectoryGeneratorConfig,
) -> Iterable[WorldProgram]:
    requests = (
        (HoldoutSplit.TRAIN, config.train_count),
        (HoldoutSplit.HELD_OUT_OBJECT_CLASS, config.held_out_object_count),
        (
            HoldoutSplit.HELD_OUT_OPERATION_FAMILY,
            config.held_out_operation_count,
        ),
        (HoldoutSplit.HELD_OUT_COMPOSITION, config.held_out_composition_count),
    )
    for split, count in requests:
        for index in range(count):
            yield _make_program(config=config, split=split, index=index)


def validate_holdout_integrity(programs: Iterable[WorldProgram]) -> None:
    """Fail closed when a reserved whole-family holdout leaks into training."""

    materialized = tuple(programs)
    if not materialized:
        raise TrajectoryDatasetError("trajectory dataset must contain programs")
    if any(program.partition is None for program in materialized):
        raise TrajectoryDatasetError("every trajectory requires a dataset partition")

    partitions = tuple(program.partition for program in materialized)
    train = tuple(
        partition for partition in partitions if partition.split is HoldoutSplit.TRAIN
    )
    held_object = tuple(
        partition
        for partition in partitions
        if partition.split is HoldoutSplit.HELD_OUT_OBJECT_CLASS
    )
    held_operation = tuple(
        partition
        for partition in partitions
        if partition.split is HoldoutSplit.HELD_OUT_OPERATION_FAMILY
    )
    held_composition = tuple(
        partition
        for partition in partitions
        if partition.split is HoldoutSplit.HELD_OUT_COMPOSITION
    )
    if not all((train, held_object, held_operation, held_composition)):
        raise TrajectoryDatasetError("all Stage 2 train and holdout splits are required")

    train_objects = {partition.object_class for partition in train}
    train_operations = {partition.operation_family for partition in train}
    train_generators = {partition.generator_family for partition in train}
    train_pairs = {
        (partition.object_class, partition.operation_family) for partition in train
    }

    held_object_classes = {partition.object_class for partition in held_object}
    if train_objects & held_object_classes:
        raise TrajectoryDatasetError("held-out object class leaked into training")

    held_operation_families = {
        partition.operation_family for partition in held_operation
    }
    if train_operations & held_operation_families:
        raise TrajectoryDatasetError("held-out operation family leaked into training")

    for partition in held_composition:
        pair = (partition.object_class, partition.operation_family)
        if pair in train_pairs:
            raise TrajectoryDatasetError("held-out composition leaked into training")
        if partition.object_class not in train_objects:
            raise TrajectoryDatasetError(
                "composition holdout object class is not independently present in training"
            )
        if partition.operation_family not in train_operations:
            raise TrajectoryDatasetError(
                "composition holdout operation family is not independently present in training"
            )
        if partition.generator_family in train_generators:
            raise TrajectoryDatasetError(
                "composition holdout generator family leaked into training"
            )


def validate_dataset(
    programs: Iterable[WorldProgram],
    *,
    expected_count: int | None = None,
) -> tuple[WorldProgram, ...]:
    """Validate schemas, unique identities, codecs, bridges, and holdouts."""

    materialized = tuple(programs)
    if expected_count is not None and len(materialized) != expected_count:
        raise TrajectoryDatasetError(
            f"expected {expected_count} programs, found {len(materialized)}"
        )
    program_ids = [program.program_id for program in materialized]
    if len(program_ids) != len(set(program_ids)):
        raise TrajectoryDatasetError("trajectory program IDs must be unique")
    for program in materialized:
        try:
            program.validate()
            encoded = encode_program(program)
            if encoded.program_sha256 != program.sha256():
                raise TrajectoryDatasetError(
                    f"codec hash mismatch for {program.program_id}"
                )
            assert_lossless_round_trip(program)
        except (ValueError, WorldSchemaError) as error:
            raise TrajectoryDatasetError(
                f"invalid trajectory {program.program_id}: {error}"
            ) from error
    validate_holdout_integrity(materialized)
    return materialized


def _manifest_for(
    programs: tuple[WorldProgram, ...],
    config: TrajectoryGeneratorConfig,
) -> dict[str, Any]:
    partitions = tuple(program.partition for program in programs)
    split_counts = Counter(partition.split.value for partition in partitions)
    token_lengths = [len(encode_program(program).token_ids) for program in programs]
    program_hashes = [program.sha256() for program in programs]
    evidence_kinds = sorted(
        {
            binding.kind.value
            for program in programs
            for binding in program.evidence
        }
    )
    capability_statuses = sorted(
        {
            operation.capability_status.value
            for program in programs
            for operation in program.operations
            if operation.capability_status is not None
        }
    )
    return {
        "artifact_type": "primus_grounded_world_trajectories",
        "generator_version": GENERATOR_VERSION,
        "world_schema_version": WORLD_SCHEMA_VERSION,
        "config": asdict(config),
        "program_count": len(programs),
        "split_counts": dict(sorted(split_counts.items())),
        "holdout_contract": {
            "held_out_object_classes": [HELD_OUT_OBJECT_CLASS],
            "held_out_operation_families": [HELD_OUT_OPERATION_FAMILY],
            "held_out_compositions": [list(HELD_OUT_COMPOSITION)],
            "random_example_split": False,
        },
        "structural_coverage": unique_program_coverage(programs),
        "token_sequence_lengths": {
            "minimum": min(token_lengths),
            "maximum": max(token_lengths),
            "mean": round(sum(token_lengths) / len(token_lengths), 3),
        },
        "program_hash_set_sha256": _sha256_bytes(
            ("\n".join(program_hashes) + "\n").encode("ascii")
        ),
        "evidence_kinds": evidence_kinds,
        "capability_statuses": capability_statuses,
        "claims": {
            "model_training_started": False,
            "checkpoint_modified": False,
            "candidate_promoted": False,
            "learned_world_dynamics_proven": False,
            "visual_correctness_proven": False,
        },
    }


def generate_dataset(
    config: TrajectoryGeneratorConfig | None = None,
) -> GeneratedTrajectoryDataset:
    """Generate and validate a deterministic in-memory Stage 2 dataset."""

    resolved = config or TrajectoryGeneratorConfig()
    resolved.validate()
    programs = validate_dataset(
        tuple(_iter_requested_programs(resolved)),
        expected_count=resolved.program_count,
    )
    return GeneratedTrajectoryDataset(
        programs=programs,
        manifest=_manifest_for(programs, resolved),
    )


def write_dataset(
    output_dir: str | os.PathLike[str],
    config: TrajectoryGeneratorConfig | None = None,
) -> DatasetWriteReceipt:
    """Atomically publish a deterministic dataset to a new explicit directory."""

    destination = Path(output_dir).expanduser().resolve()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"refusing existing output destination: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    dataset = generate_dataset(config)
    dataset_bytes = dataset.jsonl_bytes()
    dataset_sha256 = _sha256_bytes(dataset_bytes)
    manifest = dict(dataset.manifest)
    manifest["files"] = {
        DATASET_FILENAME: {
            "bytes": len(dataset_bytes),
            "records": len(dataset.programs),
            "sha256": dataset_sha256,
        }
    }
    manifest_bytes = (_stable_json(manifest, pretty=True) + "\n").encode("utf-8")
    manifest_sha256 = _sha256_bytes(manifest_bytes)

    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.tmp-",
            dir=str(destination.parent),
        )
    )
    try:
        dataset_path = temporary / DATASET_FILENAME
        manifest_path = temporary / MANIFEST_FILENAME
        dataset_path.write_bytes(dataset_bytes)
        manifest_path.write_bytes(manifest_bytes)
        if _sha256_bytes(dataset_path.read_bytes()) != dataset_sha256:
            raise OSError("dataset hash changed during write")
        if _sha256_bytes(manifest_path.read_bytes()) != manifest_sha256:
            raise OSError("manifest hash changed during write")
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(
                f"refusing destination created during generation: {destination}"
            )
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    return DatasetWriteReceipt(
        output_dir=str(destination),
        dataset_path=str(destination / DATASET_FILENAME),
        manifest_path=str(destination / MANIFEST_FILENAME),
        dataset_sha256=dataset_sha256,
        manifest_sha256=manifest_sha256,
        program_count=len(dataset.programs),
    )
