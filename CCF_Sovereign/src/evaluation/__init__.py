"""Evaluation and evidence helpers for CCF hardening."""

from .shadow_baseline import (
    BaselineRunResult,
    BenchmarkCaseResult,
    run_no_training_parent_baseline,
)
from .shadow_manifest import (
    BenchmarkCase,
    FileEvidence,
    ShadowCycleManifest,
    create_shadow_cycle_manifest,
    sha256_file,
)

__all__ = [
    "BaselineRunResult",
    "BenchmarkCase",
    "BenchmarkCaseResult",
    "FileEvidence",
    "ShadowCycleManifest",
    "create_shadow_cycle_manifest",
    "run_no_training_parent_baseline",
    "sha256_file",
]
