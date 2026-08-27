"""Manifest-bound ingestion for Primus Stage 2 world trajectories."""

from .ingestion import (  # noqa: F401
    WorldBatch,
    WorldDataError,
    WorldDataReceipt,
    WorldIngestionConfig,
    WorldProgramRecord,
    WorldSegment,
    ingest_world_dataset,
    make_batches,
    segment_records,
    verify_emitted_batches,
)
from .transitions import (  # noqa: F401
    INPUT_FEATURE_NAMES,
    TARGET_FEATURE_NAMES,
    WorldTransitionError,
    WorldTransitionExample,
    derive_transition_example,
    derive_transition_examples,
    example_set_sha256,
    train_partition_examples,
)
