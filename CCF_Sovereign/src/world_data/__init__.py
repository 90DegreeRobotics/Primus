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
