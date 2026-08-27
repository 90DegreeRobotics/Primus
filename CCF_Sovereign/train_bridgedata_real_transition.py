"""One bounded, isolated BridgeData state-transition learning gate.

The runner trains a compact MLP from scratch on a manifest-bound local slice of
observed BridgeData V2 transitions. It does not load or modify the Council
parent, emit robot actions, operate a renderer, or provide any promotion path.
Exactly one fresh candidate ID should be executed for this experiment. A result
is useful only when it has exact-coverage, split-separated evidence and beats
the strongest explicit baseline on both protected partitions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from real_data.bridgedata_evaluation import (  # noqa: E402
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    ActionOnlyMeanDeltaBaseline,
    BridgeDataMetricsReport,
    BridgeDataPrediction,
    BridgeDataSplit,
    BridgeDataSplitConfig,
    CopyStateBaseline,
    NearestTrainStateActionBaseline,
    allocate_bridgedata_replication_split,
    allocate_bridgedata_split,
    baseline_predictions,
    bound_split_by_complete_episodes,
    score_bridgedata_predictions,
    transitions_by_split,
)
from real_data.bridgedata_transitions import (  # noqa: E402
    STATE_DIMENSIONS,
    BridgeDataTransition,
    BridgeDataTransitionConfig,
    derive_bridgedata_transitions,
    load_bridgedata_intake,
    sha256_file,
)
from training.candidate_run import EXPECTED_PARENT_SHA256  # noqa: E402
from training.real_data_candidate import (  # noqa: E402
    RealDataCandidateRun,
    RealDataCandidateSafetyError,
)


EXPERIMENT_VERSION = 1
DEFAULT_SEED = 20_260_827
DEFAULT_REPLICATION_SEED = 20_260_828
DEFAULT_EPOCHS = 40
DEFAULT_BATCH_SIZE = 256
DEFAULT_LEARNING_RATE = 1e-3
DEFAULT_WEIGHT_DECAY = 1e-5
DEFAULT_HIDDEN_DIMENSIONS = 128
SPLIT_CONFIG = BridgeDataSplitConfig(
    seed=DEFAULT_SEED,
    held_out_task_fraction=0.15,
    held_out_episode_fraction=0.15,
)
TRANSITION_BUDGETS = {
    TRAIN_SPLIT: 12_000,
    HELD_OUT_EPISODE_SPLIT: 2_000,
    HELD_OUT_TASK_SPLIT: 2_000,
}


@dataclass(frozen=True)
class TrainOnlyNormalization:
    """Train-derived standardization for 14D input and 7D state deltas."""

    input_mean: tuple[float, ...]
    input_scale: tuple[float, ...]
    delta_mean: tuple[float, ...]
    delta_scale: tuple[float, ...]
    train_transition_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _finite(values: Sequence[float], label: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or not all(math.isfinite(value) for value in result):
        raise ValueError(f"{label} must contain finite values")
    return result


def fit_train_only_normalization(
    train_transitions: Sequence[BridgeDataTransition],
) -> TrainOnlyNormalization:
    """Fit population mean/scales from training transitions only."""

    if len(train_transitions) < 2:
        raise ValueError("at least two training transitions are required")
    identifiers = [item.transition_id for item in train_transitions]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("training transitions contain duplicate IDs")
    features = np.asarray([item.state_t + item.action_t for item in train_transitions], dtype=np.float64)
    deltas = np.asarray(
        [
            tuple(target - source for target, source in zip(item.state_t_plus_1, item.state_t))
            for item in train_transitions
        ],
        dtype=np.float64,
    )
    if features.shape[1] != STATE_DIMENSIONS * 2 or deltas.shape[1] != STATE_DIMENSIONS:
        raise ValueError("BridgeData transition dimensions do not match the 7D state/action contract")
    mean = features.mean(axis=0)
    scale = np.maximum(features.std(axis=0), 1e-8)
    delta_mean = deltas.mean(axis=0)
    delta_scale = np.maximum(deltas.std(axis=0), 1e-8)
    return TrainOnlyNormalization(
        input_mean=_finite(mean, "input_mean"),
        input_scale=_finite(scale, "input_scale"),
        delta_mean=_finite(delta_mean, "delta_mean"),
        delta_scale=_finite(delta_scale, "delta_scale"),
        train_transition_ids=tuple(identifiers),
    )


def arrays_for_transitions(
    transitions: Sequence[BridgeDataTransition],
    normalizer: TrainOnlyNormalization,
) -> tuple[np.ndarray, np.ndarray]:
    """Return normalizer-scaled inputs and target deltas for observed records."""

    if not transitions:
        raise ValueError("at least one transition is required")
    features = np.asarray([item.state_t + item.action_t for item in transitions], dtype=np.float32)
    deltas = np.asarray(
        [
            tuple(target - source for target, source in zip(item.state_t_plus_1, item.state_t))
            for item in transitions
        ],
        dtype=np.float32,
    )
    normalized_features = (features - np.asarray(normalizer.input_mean, dtype=np.float32)) / np.asarray(
        normalizer.input_scale, dtype=np.float32
    )
    normalized_deltas = (deltas - np.asarray(normalizer.delta_mean, dtype=np.float32)) / np.asarray(
        normalizer.delta_scale, dtype=np.float32
    )
    return normalized_features, normalized_deltas


class BridgeDataResidualMLP(nn.Module):
    """Compact from-scratch 14D conditional residual state-delta predictor."""

    def __init__(self, hidden_dimensions: int = DEFAULT_HIDDEN_DIMENSIONS) -> None:
        super().__init__()
        if hidden_dimensions < 8:
            raise ValueError("hidden_dimensions must be at least eight")
        self.network = nn.Sequential(
            nn.Linear(STATE_DIMENSIONS * 2, hidden_dimensions),
            nn.GELU(),
            nn.LayerNorm(hidden_dimensions),
            nn.Linear(hidden_dimensions, hidden_dimensions),
            nn.GELU(),
            nn.Linear(hidden_dimensions, STATE_DIMENSIONS),
        )

    def forward(self, normalized_state_action: torch.Tensor) -> torch.Tensor:
        return self.network(normalized_state_action)


def configure_seed(seed: int) -> None:
    """Set all local RNGs before construct/train without importing external models."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def resolve_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was explicitly requested but is unavailable")
    return device


def train_residual_mlp(
    model: BridgeDataResidualMLP,
    train_transitions: Sequence[BridgeDataTransition],
    normalizer: TrainOnlyNormalization,
    *,
    seed: int,
    device: torch.device,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
) -> dict[str, Any]:
    """Train from scratch on the supplied train partition only."""

    if epochs < 1 or batch_size < 1 or learning_rate <= 0 or weight_decay < 0:
        raise ValueError("invalid bounded training hyperparameters")
    features, targets = arrays_for_transitions(train_transitions, normalizer)
    input_tensor = torch.from_numpy(features)
    target_tensor = torch.from_numpy(targets)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    losses: list[float] = []
    started = time.perf_counter()
    update_count = 0
    model.train()
    for _epoch in range(epochs):
        permutation = torch.randperm(len(input_tensor), generator=generator)
        for start in range(0, len(permutation), batch_size):
            indices = permutation[start : start + batch_size]
            inputs = input_tensor[indices].to(device)
            targets_batch = target_tensor[indices].to(device)
            optimizer.zero_grad(set_to_none=True)
            predictions = model(inputs)
            loss = torch.nn.functional.mse_loss(predictions, targets_batch)
            if not torch.isfinite(loss):
                raise RuntimeError("training produced a non-finite loss")
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
            update_count += 1
    elapsed = time.perf_counter() - started
    return {
        "updates": update_count,
        "epochs_completed": epochs,
        "first_batch_loss": losses[0],
        "last_batch_loss": losses[-1],
        "mean_batch_loss": sum(losses) / len(losses),
        "elapsed_seconds": elapsed,
    }


def model_predictions(
    model: BridgeDataResidualMLP,
    transitions: Sequence[BridgeDataTransition],
    normalizer: TrainOnlyNormalization,
    *,
    device: torch.device,
) -> dict[str, BridgeDataPrediction]:
    """Return finite exact-ID predictions for every supplied observed transition."""

    features, _unused = arrays_for_transitions(transitions, normalizer)
    result: dict[str, BridgeDataPrediction] = {}
    model.eval()
    with torch.no_grad():
        for start in range(0, len(transitions), 1_024):
            stop = min(start + 1_024, len(transitions))
            output = model(torch.from_numpy(features[start:stop]).to(device)).detach().cpu().numpy()
            deltas = output * np.asarray(normalizer.delta_scale) + np.asarray(normalizer.delta_mean)
            for transition, delta in zip(transitions[start:stop], deltas):
                values = tuple(float(state + offset) for state, offset in zip(transition.state_t, delta))
                if not all(math.isfinite(item) for item in values):
                    raise RuntimeError("model emitted a non-finite state prediction")
                if transition.transition_id in result:
                    raise RuntimeError("model prediction input contains duplicate transition IDs")
                result[transition.transition_id] = BridgeDataPrediction(
                    transition_id=transition.transition_id,
                    state_t_plus_1=values,
                )
    return result


def _raw_predictions_payload(predictions: Mapping[str, BridgeDataPrediction]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "prediction_count": len(predictions),
        "predictions": [
            predictions[identifier].to_dict() for identifier in sorted(predictions)
        ],
    }


def strongest_protected_baseline(
    reports: Mapping[str, BridgeDataMetricsReport], split_name: str) -> tuple[str, float]:
    choices = [
        (label, report.by_split[split_name].aggregate_rmse)
        for label, report in reports.items()
    ]
    return min(choices, key=lambda item: (item[1], item[0]))


def predeclared_acceptance(
    candidate_report: BridgeDataMetricsReport,
    baseline_reports: Mapping[str, BridgeDataMetricsReport],
) -> dict[str, Any]:
    """Compare only protected per-split RMSE without enabling promotion."""

    protected = (HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT)
    comparisons = {}
    all_improved = True
    for split_name in protected:
        label, baseline_rmse = strongest_protected_baseline(baseline_reports, split_name)
        candidate_metrics = candidate_report.by_split[split_name]
        improvement = baseline_rmse - candidate_metrics.aggregate_rmse
        improved = candidate_metrics.coverage == 1.0 and candidate_metrics.aggregate_rmse < baseline_rmse
        all_improved = all_improved and improved
        comparisons[split_name] = {
            "candidate_aggregate_rmse": candidate_metrics.aggregate_rmse,
            "strongest_baseline": label,
            "strongest_baseline_aggregate_rmse": baseline_rmse,
            "absolute_rmse_improvement": improvement,
            "strict_improvement": improved,
            "coverage": candidate_metrics.coverage,
        }
    return {
        "acceptance_rule": "candidate must have exact coverage and strictly lower aggregate RMSE than the strongest explicit baseline on both protected partitions",
        "passed": all_improved,
        "by_protected_split": comparisons,
        "promotion_authorized": False,
    }


def _pinned_inherited_untracked(repo_root: Path) -> dict[str, tuple[Path, str]]:
    """Declare only known prior root plans; arbitrary repository dirt remains blocked."""

    names = (
        "chronos_typed_operation_payload_plan.md",
        "plan_2026-08-27_0830_blender-renderer-witness.md",
        "plan_2026-08-27_1309_typed-operation-payload.md",
    )
    result: dict[str, tuple[Path, str]] = {}
    for name in names:
        path = repo_root / name
        if not path.is_file():
            raise RealDataCandidateSafetyError(
                f"expected inherited untracked plan is missing: {name}"
            )
        label = path.stem.replace("-", "_")
        result[label] = (path, sha256_file(path))
    return result


def _load_prior_candidate_selection(prior_candidate_id: str) -> dict[str, Any]:
    """Read and hash-bind a terminal prior candidate without modifying it."""

    if not prior_candidate_id or Path(prior_candidate_id).name != prior_candidate_id:
        raise RealDataCandidateSafetyError("prior candidate ID must be a simple candidate directory name")
    prior_dir = ROOT / "checkpoints" / "candidates" / prior_candidate_id
    manifest_path = prior_dir / "real_data.run.manifest.json"
    split_path = prior_dir / "evidence" / "split.json"
    if not manifest_path.is_file() or not split_path.is_file():
        raise RealDataCandidateSafetyError("prior candidate manifest or split evidence is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("candidate_id") != prior_candidate_id or manifest.get("status") != "rejected":
        raise RealDataCandidateSafetyError("prior candidate must be a terminal rejected evidence record")
    split_evidence = json.loads(split_path.read_text(encoding="utf-8"))
    bounded = split_evidence.get("bounded_group_split")
    if not isinstance(bounded, dict):
        raise RealDataCandidateSafetyError("prior candidate lacks bounded split evidence")
    selected: list[int] = []
    for key in (
        "train_episode_indices",
        "held_out_episode_indices",
        "held_out_task_episode_indices",
    ):
        values = bounded.get(key)
        if not isinstance(values, list) or not values:
            raise RealDataCandidateSafetyError(f"prior candidate split has no {key}")
        if any(isinstance(item, bool) or not isinstance(item, int) for item in values):
            raise RealDataCandidateSafetyError("prior candidate split has a non-integer episode ID")
        selected.extend(values)
    if len(selected) != len(set(selected)):
        raise RealDataCandidateSafetyError("prior candidate split overlaps its own episode partitions")
    return {
        "candidate_id": prior_candidate_id,
        "manifest_path": manifest_path,
        "manifest_sha256": sha256_file(manifest_path),
        "split_path": split_path,
        "split_sha256": sha256_file(split_path),
        "selected_episode_indices": tuple(sorted(selected)),
    }


def run_once(
    candidate_id: str,
    *,
    prior_candidate_id: str,
    split_seed: int,
    device_name: str = "auto",
) -> dict[str, Any]:
    """Execute one fresh episode-disjoint replication candidate and reject promotion."""

    if isinstance(split_seed, bool) or not isinstance(split_seed, int):
        raise ValueError("split_seed must be an integer")
    prior = _load_prior_candidate_selection(prior_candidate_id)
    configure_seed(split_seed)
    device = resolve_device(device_name)
    manifest_path = (
        ROOT
        / "data"
        / "external"
        / "bridgedata2_lerobot_v3_metadata_20260827"
        / "intake_manifest.json"
    )
    intake = load_bridgedata_intake(manifest_path)
    replication_split_config = BridgeDataSplitConfig(
        seed=split_seed,
        held_out_task_fraction=SPLIT_CONFIG.held_out_task_fraction,
        held_out_episode_fraction=SPLIT_CONFIG.held_out_episode_fraction,
    )
    full_split = allocate_bridgedata_replication_split(
        intake.episodes,
        replication_split_config,
        reserved_episode_indices=prior["selected_episode_indices"],
    )
    split = bound_split_by_complete_episodes(
        full_split,
        intake.episodes,
        max_transitions_by_split=TRANSITION_BUDGETS,
    )
    selected_episodes = frozenset(
        split.train_episode_indices
        + split.held_out_episode_indices
        + split.held_out_task_episode_indices
    )
    extracted = derive_bridgedata_transitions(
        intake,
        BridgeDataTransitionConfig(selected_episode_indices=selected_episodes)
    )
    partitions = transitions_by_split(extracted.transitions, split)
    normalizer = fit_train_only_normalization(partitions[TRAIN_SPLIT])
    baselines = (
        CopyStateBaseline(),
        ActionOnlyMeanDeltaBaseline.fit(partitions[TRAIN_SPLIT]),
        NearestTrainStateActionBaseline.fit(partitions[TRAIN_SPLIT]),
    )
    baseline_reports = {
        baseline.label: score_bridgedata_predictions(
            partitions,
            baseline_predictions(baseline, partitions),
            split=split,
            prediction_label=baseline.label,
        )
        for baseline in baselines
    }
    candidate = RealDataCandidateRun.create(
        ROOT,
        candidate_id,
        split_seed,
        expected_parent_sha256=EXPECTED_PARENT_SHA256,
        additional_frozen_inputs={
            "intake_manifest": (manifest_path, intake.manifest_sha256),
            "data_parquet": (intake.data_path, intake.source_files["data_chunk-000_file-000.parquet"]["sha256"]),
            "episodes_parquet": (intake.episode_path, intake.source_files["meta_episodes_chunk-000_file-000.parquet"]["sha256"]),
            "tasks_parquet": (intake.task_path, intake.source_files["meta_tasks.parquet"]["sha256"]),
            "prior_candidate_manifest": (prior["manifest_path"], prior["manifest_sha256"]),
            "prior_candidate_split": (prior["split_path"], prior["split_sha256"]),
        },
        permitted_preexisting_untracked=_pinned_inherited_untracked(ROOT.parent),
    )
    split_path = candidate.write_evidence_json(
        "split.json",
        {
            "prior_candidate": {
                "candidate_id": prior["candidate_id"],
                "manifest_sha256": prior["manifest_sha256"],
                "split_evidence_sha256": prior["split_sha256"],
                "reserved_selected_episode_count": len(prior["selected_episode_indices"]),
                "reserved_selected_episode_indices": list(prior["selected_episode_indices"]),
            },
            "full_group_split": full_split.to_dict(),
            "bounded_group_split": split.to_dict(),
            "extraction_receipt": extracted.receipt.to_dict(),
            "normalization": normalizer.to_dict(),
        },
    )
    model = BridgeDataResidualMLP()
    model_parameter_count = sum(parameter.numel() for parameter in model.parameters())
    training_config = {
                    "experiment_version": EXPERIMENT_VERSION,
            "replication_of_candidate_id": prior["candidate_id"],
            "prior_candidate_manifest_sha256": prior["manifest_sha256"],
            "prior_candidate_split_evidence_sha256": prior["split_sha256"],
            "reserved_prior_episode_count": len(prior["selected_episode_indices"]),
            "split_seed": split_seed,

        "architecture": "from_scratch_residual_mlp",
        "input_dimensions": STATE_DIMENSIONS * 2,
        "output_dimensions": STATE_DIMENSIONS,
        "hidden_dimensions": DEFAULT_HIDDEN_DIMENSIONS,
        "parameters": model_parameter_count,
        "epochs": DEFAULT_EPOCHS,
        "batch_size": DEFAULT_BATCH_SIZE,
        "learning_rate": DEFAULT_LEARNING_RATE,
        "weight_decay": DEFAULT_WEIGHT_DECAY,
        "split_sha256": split.sha256(),
        "extraction_receipt_sha256": extracted.receipt.sha256(),
        "normalization_train_transition_count": len(normalizer.train_transition_ids),
    }
    candidate.mark_training_started(
        config=training_config,
        examples=len(partitions[TRAIN_SPLIT]),
        epochs=DEFAULT_EPOCHS,
        batch_size=DEFAULT_BATCH_SIZE,
        device=str(device),
    )
    try:
        training = train_residual_mlp(
            model,
            partitions[TRAIN_SPLIT],
            normalizer,
            seed=split_seed,
            device=device,
            epochs=DEFAULT_EPOCHS,
            batch_size=DEFAULT_BATCH_SIZE,
            learning_rate=DEFAULT_LEARNING_RATE,
            weight_decay=DEFAULT_WEIGHT_DECAY,
        )
        candidate.save_checkpoint(
            {
                "state_dict": model.state_dict(),
                "normalization": normalizer.to_dict(),
                "training_config": training_config,
                "training": training,
            },
            metrics=training,
        )
        all_transitions = tuple(
            transition for name in (TRAIN_SPLIT, HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT)
            for transition in partitions[name]
        )
        predictions = model_predictions(model, all_transitions, normalizer, device=device)
        candidate_report = score_bridgedata_predictions(
            partitions,
            predictions,
            split=split,
            prediction_label="from_scratch_residual_mlp",
        )
        predictions_path = candidate.write_evidence_json(
            "raw_predictions.json", _raw_predictions_payload(predictions)
        )
        acceptance = predeclared_acceptance(candidate_report, baseline_reports)
        metrics_path = candidate.write_evidence_json(
            "metrics.json",
            {
                "candidate_report": candidate_report.to_dict(),
                "baseline_reports": {label: report.to_dict() for label, report in baseline_reports.items()},
                "acceptance": acceptance,
                "split_evidence_path": split_path.name,
            },
        )
        candidate.mark_evaluated(metrics_report=metrics_path, predictions=predictions_path)

        restored = BridgeDataResidualMLP()
        checkpoint = torch.load(candidate.checkpoint_path(), map_location=device, weights_only=False)
        restored.load_state_dict(checkpoint["state_dict"])
        restored_predictions = model_predictions(restored, all_transitions, normalizer, device=device)
        if restored_predictions != predictions:
            raise RuntimeError("checkpoint restore smoke prediction mismatch")
        candidate.mark_rejected(
            "No promotion is authorized: this bounded real-data result is retained only as evidence, regardless of the acceptance comparison."
        )
        return {
            "candidate_id": candidate_id,
            "replication_of_candidate_id": prior["candidate_id"],
            "prior_candidate_manifest_sha256": prior["manifest_sha256"],
            "prior_candidate_split_evidence_sha256": prior["split_sha256"],
            "reserved_prior_episode_count": len(prior["selected_episode_indices"]),
            "candidate_dir": str(candidate.candidate_dir),
            "split_sha256": split.sha256(),
            "extraction_receipt_sha256": extracted.receipt.sha256(),
            "acceptance": acceptance,
            "candidate_report": candidate_report.to_dict(),
            "baseline_reports": {label: report.to_dict() for label, report in baseline_reports.items()},
            "checkpoint_restore_smoke": "passed",
            "promotion_performed": False,
            "candidate_status": candidate.manifest["status"],
        }
    except BaseException as error:
        candidate.mark_failed(error)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one bounded real BridgeData transition candidate.")
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--prior-candidate-id", required=True)
    parser.add_argument("--split-seed", type=int, required=True)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    arguments = parser.parse_args()
    result = run_once(
        arguments.candidate_id,
        prior_candidate_id=arguments.prior_candidate_id,
        split_seed=arguments.split_seed,
        device_name=arguments.device,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
