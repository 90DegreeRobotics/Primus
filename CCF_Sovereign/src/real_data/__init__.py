"""Manifest-bound real observational-data utilities for bounded Primus experiments.

This package is intentionally separate from the deterministic synthetic
``world_data`` package.  It contains no robot-policy, control, actuation,
renderer, or promotion functionality.
"""

from .bridgedata_evaluation import (  # noqa: F401
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    ActionOnlyMeanDeltaBaseline,
    BridgeDataEvaluationError,
    BridgeDataMetricsReport,
    BridgeDataPrediction,
    BridgeDataSplit,
    BridgeDataSplitConfig,
    CopyStateBaseline,
    NearestTrainStateActionBaseline,
    allocate_bridgedata_split,
    baseline_predictions,
    bound_split_by_complete_episodes,
    score_bridgedata_predictions,
    transitions_by_split,
    validate_bridgedata_split,
)
from .bridgedata_transitions import (  # noqa: F401
    BRIDGEDATA_TRANSITION_VERSION,
    BridgeDataError,
    BridgeDataReceipt,
    BridgeDataTransition,
    BridgeDataTransitionConfig,
    BridgeDataTransitionDataset,
    EpisodeTask,
    derive_bridgedata_transitions,
    load_bridgedata_intake,
    sha256_file,
)
