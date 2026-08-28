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
    LinearStateActionDeltaBaseline,
    NearestTrainStateActionBaseline,
    allocate_bridgedata_replication_split,
    allocate_bridgedata_split,
    baseline_predictions,
    bound_split_by_complete_episodes,
    score_bridgedata_predictions,
    transitions_by_split,
    validate_bridgedata_split,
)
from .bridgedata_rollout_uncertainty import (  # noqa: F401
    DEFAULT_BOOTSTRAP_RESAMPLES,
    DEFAULT_BOOTSTRAP_SEED,
    DEFAULT_MIN_DISTINCT_EPISODES,
    PAIRED_BOOTSTRAP_VERSION,
    BridgeDataRolloutUncertaintyError,
    EpisodeClusteredBootstrapResult,
    PairedRolloutCaseError,
    episode_clustered_paired_bootstrap,
    paired_case_error_set_sha256,
    paired_rollout_case_errors,
)
from .bridgedata_rollouts import (  # noqa: F401
    BRIDGEDATA_ROLLOUT_VERSION,
    DEFAULT_CASE_SELECTION_SEED,
    DEFAULT_HORIZONS,
    DEFAULT_MAX_CASES_PER_HORIZON,
    BridgeDataRolloutCase,
    BridgeDataRolloutError,
    BridgeDataRolloutPrediction,
    BridgeDataRolloutReport,
    RolloutHorizonMetrics,
    action_only_mean_delta_predictor,
    build_rollout_cases,
    copy_state_predictor,
    evaluate_rollout_predictor,
    linear_state_action_delta_predictor,
    nearest_train_state_action_predictor,
    predeclared_rollout_acceptance,
    rollout_predictions,
    score_rollout_predictions,
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
