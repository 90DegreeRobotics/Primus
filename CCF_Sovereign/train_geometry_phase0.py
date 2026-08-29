"""Phase 0 geometry forward-model harness.

This module trains only a candidate-local small model that maps a geometry
program and its derived structure to v2 mesh metrics. It is fail-closed on the
hash-pinned corpus intake and has no promotion operation. Fixture execution is
an execution-safety proof, never a learning result.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile
from typing import Any, Iterable, Mapping, Sequence

import torch
from torch import nn

ROOT = Path(__file__).resolve().parent
import sys

sys.path.insert(0, str(ROOT / "src"))

from geometry_corpus import (  # noqa: E402
    TARGET_METRICS,
    GeometryCorpusError,
    GeometryCorpusIntake,
    GeometryProgramRecord,
    evaluate_declared_baselines,
    load_geometry_corpus_intake,
)

CANDIDATE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
CANDIDATE_MANIFEST_NAME = "geometry_phase0_manifest.json"
CANDIDATE_CHECKPOINT_NAME = "geometry_phase0_model.pt"
CANDIDATE_OUTPUT_DIRECTORY = "geometry_phase0_candidates"


class GeometryPhase0SafetyError(RuntimeError):
    """Raised when the Phase 0 candidate lifecycle or input contract is unsafe."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically replace the candidate manifest without a torn JSON state."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary_path = Path(handle.name)
    os.replace(temporary_path, path)


def atomic_torch_save(payload: Mapping[str, Any], path: Path) -> None:
    """Atomically write a candidate-only checkpoint."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary_path = Path(handle.name)
    try:
        torch.save(dict(payload), temporary_path)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT.parent,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return result.stdout.strip() or "unavailable"


def _require_fixture_inputs(paths: Iterable[Path]) -> None:
    names = [path.name for path in paths]
    if not names or any("_fixture_" not in name for name in names):
        raise GeometryPhase0SafetyError(
            "fixture execution requires all corpus, manifest, and split filenames to contain '_fixture_'"
        )


def _candidate_directory(output_root: Path, candidate_id: str) -> Path:
    if not CANDIDATE_ID_PATTERN.fullmatch(candidate_id):
        raise GeometryPhase0SafetyError("candidate_id must be 3-64 lowercase letters, digits, or hyphens")
    resolved_root = output_root.expanduser().resolve()
    candidate_root = (resolved_root / CANDIDATE_OUTPUT_DIRECTORY).resolve()
    candidate_path = (candidate_root / candidate_id).resolve()
    if candidate_root not in candidate_path.parents:
        raise GeometryPhase0SafetyError("candidate path escapes the configured output root")
    if candidate_path.exists():
        raise GeometryPhase0SafetyError(f"candidate destination already exists: {candidate_path}")
    return candidate_path


def _collect_numeric_values(value: Any) -> list[float]:
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        numeric = float(value)
        if not torch.isfinite(torch.tensor(numeric)):
            raise GeometryPhase0SafetyError("program contains a non-finite numeric parameter")
        return [numeric]
    if isinstance(value, Mapping):
        values: list[float] = []
        for key, nested_value in value.items():
            if key in {"object_id", "plan_version", "unit", "op", "axis", "face", "kind", "shape"}:
                continue
            values.extend(_collect_numeric_values(nested_value))
        return values
    if isinstance(value, list):
        values = []
        for nested_value in value:
            values.extend(_collect_numeric_values(nested_value))
        return values
    return []


def _operation_vocabulary(records: Sequence[GeometryProgramRecord]) -> tuple[str, ...]:
    operations = {
        operation
        for record in records
        for operation, count in record.program_structure.op_mix
        if count > 0
    }
    if not operations:
        raise GeometryPhase0SafetyError("training records have no operations")
    return tuple(sorted(operations))


def feature_schema(records: Sequence[GeometryProgramRecord]) -> tuple[str, ...]:
    """Declare model features from training records only, without output metadata."""

    operation_names = _operation_vocabulary(records)
    return (
        "step_count",
        *(f"op_count:{operation}" for operation in operation_names),
        "numeric_parameter_count",
        "numeric_parameter_sum",
        "numeric_parameter_mean",
        "numeric_parameter_max_abs",
    )


def _feature_row(record: GeometryProgramRecord, schema: Sequence[str]) -> list[float]:
    op_mix = record.program_structure.op_mix_dict()
    numeric_values = _collect_numeric_values(record.program)
    parameter_count = len(numeric_values)
    parameter_sum = sum(numeric_values)
    parameter_mean = parameter_sum / parameter_count if parameter_count else 0.0
    parameter_max_abs = max((abs(value) for value in numeric_values), default=0.0)
    values = {
        "step_count": float(record.program_structure.step_count),
        "numeric_parameter_count": float(parameter_count),
        "numeric_parameter_sum": parameter_sum,
        "numeric_parameter_mean": parameter_mean,
        "numeric_parameter_max_abs": parameter_max_abs,
    }
    row: list[float] = []
    for name in schema:
        if name.startswith("op_count:"):
            row.append(float(op_mix.get(name.removeprefix("op_count:"), 0)))
        else:
            row.append(float(values[name]))
    return row


def _target_row(record: GeometryProgramRecord, target_metrics: Sequence[str]) -> list[float]:
    values: list[float] = []
    for metric in target_metrics:
        if metric.startswith("bbox_extent_") and metric.endswith("_mm"):
            axis_name = metric.removeprefix("bbox_extent_").removesuffix("_mm")
            axis_index = {"x": 0, "y": 1, "z": 2}.get(axis_name)
            if axis_index is None:
                raise GeometryPhase0SafetyError(f"unsupported target metric {metric!r}")
            raw = record.mesh_metrics["bbox_extent_mm"][axis_index]
        else:
            raw = record.mesh_metrics[metric]
        values.append(float(raw))
    return values


def build_training_tensors(
    records: Sequence[GeometryProgramRecord], *, schema: Sequence[str], target_metrics: Sequence[str] = TARGET_METRICS
) -> tuple[torch.Tensor, torch.Tensor]:
    """Build tensors from program/structure and mesh metrics only.

    ``view_score`` deliberately has no read path in this function: it is corpus
    metadata, neither a target nor an eligibility filter.
    """

    if not records:
        raise GeometryPhase0SafetyError("cannot build tensors from an empty split")
    features = torch.tensor([_feature_row(record, schema) for record in records], dtype=torch.float32)
    targets = torch.tensor(
        [_target_row(record, target_metrics) for record in records], dtype=torch.float32
    )
    return features, targets


@dataclass(frozen=True)
class TrainingConfig:
    seed: int = 17
    epochs: int = 32
    learning_rate: float = 0.01
    hidden_width: int = 32

    def validate(self) -> None:
        if self.epochs < 1 or self.epochs > 10_000:
            raise GeometryPhase0SafetyError("epochs must be in 1..10000")
        if not 0.0 < self.learning_rate <= 1.0:
            raise GeometryPhase0SafetyError("learning_rate must be in (0, 1]")
        if self.hidden_width < 1 or self.hidden_width > 4096:
            raise GeometryPhase0SafetyError("hidden_width must be in 1..4096")


class GeometryForwardModel(nn.Module):
    """Small MLP baseline for the Phase 0 program-to-mesh-metrics mapping."""

    def __init__(self, input_width: int, output_width: int, hidden_width: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_width, hidden_width),
            nn.ReLU(),
            nn.Linear(hidden_width, output_width),
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return self.network(values)


def _normalizer(values: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    mean = values.mean(dim=0)
    std = values.std(dim=0, unbiased=False).clamp_min(1e-6)
    return mean, std


def _metric_rows(
    actual: torch.Tensor, predicted: torch.Tensor, split: str, target_metrics: Sequence[str]
) -> list[dict[str, Any]]:
    errors = actual - predicted
    rows: list[dict[str, Any]] = []
    for index, metric in enumerate(target_metrics):
        column = errors[:, index]
        rows.append(
            {
                "split": split,
                "target_metric": metric,
                "count": int(actual.shape[0]),
                "mean_absolute_error": float(column.abs().mean().item()),
                "root_mean_squared_error": float(column.square().mean().sqrt().item()),
            }
        )
    return rows


def _baseline_comparison(
    model_metrics: Sequence[Mapping[str, Any]], baseline_reports: Sequence[Any]
) -> list[dict[str, Any]]:
    baseline_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for report in baseline_reports:
        for split_metric in report.split_metrics:
            baseline_by_key.setdefault((report.target_metric, split_metric.split), []).append(
                {
                    "baseline": report.baseline,
                    "root_mean_squared_error": split_metric.root_mean_squared_error,
                }
            )
    comparisons: list[dict[str, Any]] = []
    for metric in model_metrics:
        key = (str(metric["target_metric"]), str(metric["split"]))
        baselines = baseline_by_key.get(key, [])
        comparisons.append(
            {
                "target_metric": key[0],
                "split": key[1],
                "model_root_mean_squared_error": metric["root_mean_squared_error"],
                "baselines": [
                    {
                        **baseline,
                        "model_beats_baseline": metric["root_mean_squared_error"]
                        < baseline["root_mean_squared_error"],
                    }
                    for baseline in baselines
                ],
            }
        )
    return comparisons


def run_phase0_training(
    *,
    corpus_path: str | Path,
    manifest_path: str | Path,
    split_path: str | Path,
    output_root: str | Path,
    candidate_id: str,
    config: TrainingConfig = TrainingConfig(),
    fixture_only: bool = False,
) -> dict[str, Any]:
    """Run one isolated Phase 0 candidate without any promotion capability.

    Real corpus execution is available only through this explicit entry point;
    it remains candidate-local and non-promotable. Tests call
    ``run_fixture_training``, which enforces `_fixture_` filenames and therefore
    cannot be misreported as a real-corpus learning result.
    """

    config.validate()
    resolved_paths = tuple(Path(path).expanduser().resolve() for path in (corpus_path, manifest_path, split_path))
    if fixture_only:
        _require_fixture_inputs(resolved_paths)
    intake = load_geometry_corpus_intake(*resolved_paths)
    intake.verify()
    output_path = Path(output_root).expanduser().resolve()
    candidate_dir = _candidate_directory(output_path, candidate_id)
    candidate_dir.mkdir(parents=True, exist_ok=False)
    manifest_file = candidate_dir / CANDIDATE_MANIFEST_NAME
    checkpoint_file = candidate_dir / CANDIDATE_CHECKPOINT_NAME
    config_dict = asdict(config)
    manifest: dict[str, Any] = {
        "schema_version": "geometry_phase0_candidate_v1",
        "candidate_id": candidate_id,
        "state": "created",
        "fixture_only": fixture_only,
        "promotion": {
            "state": "rejected_by_default",
            "permitted": False,
            "reason": "This trainer has no promotion operation; explicit future authorization is required.",
        },
        "code_commit": _git_commit(),
        "trainer_sha256": sha256_file(Path(__file__).resolve()),
        "config": config_dict,
        "frozen_inputs": {
            "corpus": {"path": str(intake.corpus_path), "sha256": intake.corpus_sha256},
            "manifest": {"path": str(intake.manifest_path), "sha256": intake.manifest_sha256},
            "splits": {"path": str(intake.split_path), "sha256": intake.splits_sha256},
            "schema_version": {"value": "geometry_program_corpus_v2", "sha256": intake.schema_sha256},
        },
        "notes": (
            "Fixture execution proves harness execution only; it is never a learning result."
            if fixture_only
            else "Candidate is unpromoted by default; metrics require separate evidence review."
        ),
    }
    atomic_write_json(manifest_file, manifest)
    try:
        random.seed(config.seed)
        torch.manual_seed(config.seed)
        splits = intake.structural_splits()
        training_records = splits["train"]
        schema = feature_schema(training_records)
        train_features, train_targets = build_training_tensors(training_records, schema=schema)
        feature_mean, feature_std = _normalizer(train_features)
        target_mean, target_std = _normalizer(train_targets)
        model = GeometryForwardModel(
            input_width=train_features.shape[1],
            output_width=train_targets.shape[1],
            hidden_width=config.hidden_width,
        )
        optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
        criterion = nn.MSELoss()
        manifest["state"] = "training"
        manifest["feature_schema"] = list(schema)
        manifest["target_metrics"] = list(TARGET_METRICS)
        atomic_write_json(manifest_file, manifest)
        normalized_features = (train_features - feature_mean) / feature_std
        normalized_targets = (train_targets - target_mean) / target_std
        losses: list[float] = []
        for _ in range(config.epochs):
            optimizer.zero_grad(set_to_none=True)
            prediction = model(normalized_features)
            loss = criterion(prediction, normalized_targets)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        intake.verify()
        model_metrics: list[dict[str, Any]] = []
        with torch.no_grad():
            for split_name in ("held_out_length", "held_out_op_combo"):
                features, targets = build_training_tensors(splits[split_name], schema=schema)
                predicted = model((features - feature_mean) / feature_std) * target_std + target_mean
                model_metrics.extend(_metric_rows(targets, predicted, split_name, TARGET_METRICS))
        baseline_reports = evaluate_declared_baselines(intake, target_metrics=TARGET_METRICS)
        atomic_torch_save(
            {
                "model_state_dict": model.state_dict(),
                "feature_schema": list(schema),
                "target_metrics": list(TARGET_METRICS),
                "feature_mean": feature_mean,
                "feature_std": feature_std,
                "target_mean": target_mean,
                "target_std": target_std,
                "config": config_dict,
                "fixture_only": fixture_only,
            },
            checkpoint_file,
        )
        intake.verify()
        manifest["state"] = "evaluated"
        manifest["checkpoint"] = {"path": str(checkpoint_file), "sha256": sha256_file(checkpoint_file)}
        manifest["execution"] = {
            "epochs_completed": config.epochs,
            "initial_loss": losses[0],
            "final_loss": losses[-1],
        }
        manifest["model_metrics"] = model_metrics
        manifest["declared_baselines"] = [report.as_dict() for report in baseline_reports]
        manifest["baseline_comparison"] = _baseline_comparison(model_metrics, baseline_reports)
        atomic_write_json(manifest_file, manifest)
        return manifest
    except BaseException as error:
        manifest["state"] = "failed"
        manifest["error"] = f"{type(error).__name__}: {error}"
        atomic_write_json(manifest_file, manifest)
        raise


def run_fixture_training(
    *,
    corpus_path: str | Path,
    manifest_path: str | Path,
    split_path: str | Path,
    output_root: str | Path,
    candidate_id: str,
    config: TrainingConfig = TrainingConfig(),
) -> dict[str, Any]:
    """Run a fixture-marked execution test that is never a learning result."""

    return run_phase0_training(
        corpus_path=corpus_path,
        manifest_path=manifest_path,
        split_path=split_path,
        output_root=output_root,
        candidate_id=candidate_id,
        config=config,
        fixture_only=True,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fixture-only Phase 0 geometry candidate.")
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--splits", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--epochs", type=int, default=32)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--fixture-only",
        action="store_true",
        help="Require fixture-marked inputs and label the candidate as an execution-only fixture run.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_phase0_training(
        corpus_path=args.corpus,
        manifest_path=args.manifest,
        split_path=args.splits,
        output_root=args.output_root,
        candidate_id=args.candidate_id,
        config=TrainingConfig(seed=args.seed, epochs=args.epochs),
        fixture_only=args.fixture_only,
    )
    print(canonical_json({"candidate_id": result["candidate_id"], "state": result["state"], "fixture_only": True}))


if __name__ == "__main__":
    main()
