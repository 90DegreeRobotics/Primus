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
from .temporal_witness import (  # noqa: F401
    CONTEXT_INPUT_FEATURE_NAMES,
    TEMPORAL_TARGET_FEATURE_NAMES,
    TemporalStateWitness,
    TemporalWitnessError,
    assert_context_feature_boundary,
    derive_temporal_witness,
    derive_temporal_witnesses,
    temporal_witness_set_sha256,
)
from .normalization import (  # noqa: F401
    NORMALIZATION_VERSION,
    NormalizationError,
    TemporalContextNormalization,
    fit_train_only_normalization,
)
from .delta_witness import (  # noqa: F401
    DELTA_TARGET_FEATURE_NAMES,
    DeltaWitness,
    DeltaWitnessError,
    delta_witness_set_sha256,
    derive_delta_witness,
    derive_delta_witnesses,
)
