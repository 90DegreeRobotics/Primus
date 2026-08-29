"""Frozen, noun-free intake and evaluation tools for geometry-program corpora."""

from .baselines import (
    DECLARED_PHASE_ZERO_BASELINES,
    TARGET_METRICS,
    DeclaredBaselineReport,
    SplitMetric,
    evaluate_declared_baselines,
)
from .intake import (
    FORBIDDEN_KEYS,
    GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION,
    REQUIRED_MESH_METRIC_KEYS,
    GeometryCorpusError,
    GeometryCorpusIntake,
    GeometryProgramRecord,
    ProgramStructure,
    SplitDefinition,
    build_structural_splits,
    canonical_json,
    load_geometry_corpus_intake,
    sha256_file,
    split_for_structure,
)

__all__ = [
    "DECLARED_PHASE_ZERO_BASELINES",
    "FORBIDDEN_KEYS",
    "GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION",
    "REQUIRED_MESH_METRIC_KEYS",
    "TARGET_METRICS",
    "DeclaredBaselineReport",
    "GeometryCorpusError",
    "GeometryCorpusIntake",
    "GeometryProgramRecord",
    "ProgramStructure",
    "SplitDefinition",
    "SplitMetric",
    "build_structural_splits",
    "canonical_json",
    "evaluate_declared_baselines",
    "load_geometry_corpus_intake",
    "sha256_file",
    "split_for_structure",
]
