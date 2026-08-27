"""Train one isolated candidate on generated temporal-context witnesses.

This is a narrow generated benchmark. The MLP receives a pre-state and safe
geometry/material/action-intent context, never a generated target delta or
post-state. It does not prove observed/physical dynamics and cannot promote.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from training.candidate_run import CandidateRun, atomic_write_json, sha256_file
from world_data.ingestion import WorldIngestionConfig, ingest_world_dataset
from world_data.temporal_witness import (
    CONTEXT_INPUT_FEATURE_NAMES,
    TEMPORAL_TARGET_FEATURE_NAMES,
    TemporalStateWitness,
    assert_context_feature_boundary,
    derive_temporal_witnesses,
    temporal_witness_set_sha256,
)
from world_metrics.state_transitions import (
    StateTransitionPrediction,
    score_state_transition_predictions,
    static_no_change_baseline,
)


EXPERIMENT_VERSION = 1


class TemporalContextMLP(torch.nn.Module):
    """Small nonlinear regressor for generated contextual transition targets."""

    def __init__(self, hidden_width: int = 32) -> None:
        super().__init__()
        if hidden_width <= 0:
            raise ValueError("hidden_width must be positive")
        self.layers = torch.nn.Sequential(
            torch.nn.Linear(len(CONTEXT_INPUT_FEATURE_NAMES), hidden_width),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_width, hidden_width),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_width, len(TEMPORAL_TARGET_FEATURE_NAMES)),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.layers(features)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train one isolated generated temporal-context candidate. "
            "No parent mutation or promotion occurs."
        )
    )
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--dataset", required=True, help="Frozen v1.1 Stage 2 JSONL")
    parser.add_argument("--manifest", required=True, help="Frozen v1.1 Stage 2 manifest")
    parser.add_argument("--seed", type=int, default=20260827)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--hidden-width", type=int, default=32)
    parser.add_argument("--position-tolerance-mm", type=float, default=25.0)
    args = parser.parse_args(argv)
    if args.seed < 0:
        parser.error("--seed must be non-negative")
    for name in ("epochs", "batch_size", "hidden_width"):
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    for name in ("learning_rate", "position_tolerance_mm"):
        value = getattr(args, name)
        if not math.isfinite(value) or value <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive and finite")
    return args


def resolve_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")
    return torch.device(requested)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_partition_witnesses(
    witnesses: Iterable[TemporalStateWitness],
) -> tuple[TemporalStateWitness, ...]:
    materialized = tuple(witnesses)
    if not materialized:
        raise ValueError("training witness set cannot be empty")
    leaked = [witness.program_id for witness in materialized if witness.split.value != "train"]
    if leaked:
        raise ValueError(
            "temporal-context training accepts only the train partition; "
            f"found protected witness {leaked[0]}"
        )
    return materialized


def _feature_tensor(
    witnesses: tuple[TemporalStateWitness, ...], device: torch.device
) -> torch.Tensor:
    return torch.tensor(
        [witness.context_input_vector for witness in witnesses],
        dtype=torch.float32,
        device=device,
    )


def _target_tensor(
    witnesses: tuple[TemporalStateWitness, ...], device: torch.device
) -> torch.Tensor:
    return torch.tensor(
        [witness.target_vector for witness in witnesses],
        dtype=torch.float32,
        device=device,
    )


def train_model(
    model: TemporalContextMLP,
    witnesses: Iterable[TemporalStateWitness],
    *,
    device: torch.device,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> tuple[float, int, float]:
    """Fit only generated train witnesses and report finite measured work."""

    training = train_partition_witnesses(witnesses)
    features = _feature_tensor(training, device)
    targets = _target_tensor(training, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.0)
    model.train()
    started = time.perf_counter()
    last_loss = float("nan")
    updates = 0
    for _ in range(epochs):
        for start in range(0, len(training), batch_size):
            stop = min(start + batch_size, len(training))
            output = model(features[start:stop])
            position_loss = F.mse_loss(output[:, :3], targets[start:stop, :3])
            relation_loss = F.binary_cross_entropy_with_logits(
                output[:, 3:], targets[start:stop, 3:]
            )
            loss = position_loss + relation_loss
            if not torch.isfinite(loss):
                raise RuntimeError("temporal-context loss became non-finite")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            last_loss = float(loss.detach().cpu().item())
            updates += 1
    return last_loss, updates, time.perf_counter() - started


def model_predictions(
    model: TemporalContextMLP,
    witnesses: Iterable[TemporalStateWitness],
    *,
    device: torch.device,
) -> dict[str, StateTransitionPrediction]:
    materialized = tuple(witnesses)
    if not materialized:
        raise ValueError("prediction witness set cannot be empty")
    model.eval()
    features = _feature_tensor(materialized, device)
    with torch.no_grad():
        output = model(features).detach().cpu()
    predictions: dict[str, StateTransitionPrediction] = {}
    for witness, row in zip(materialized, output):
        if witness.program_id in predictions:
            raise ValueError(f"duplicate witness ID: {witness.program_id}")
        predictions[witness.program_id] = StateTransitionPrediction(
            program_id=witness.program_id,
            target_translation_mm=tuple(float(value * 1000.0) for value in row[:3]),
            support_present_after=bool(torch.sigmoid(row[3]).item() >= 0.5),
            near_present_after=bool(torch.sigmoid(row[4]).item() >= 0.5),
        )
    return predictions


def _evidence(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def _write_predictions(
    path: Path, predictions: dict[str, StateTransitionPrediction]
) -> None:
    atomic_write_json(
        path,
        {
            "experiment_version": EXPERIMENT_VERSION,
            "prediction_count": len(predictions),
            "prediction_input_feature_names": list(CONTEXT_INPUT_FEATURE_NAMES),
            "predictions": [
                predictions[program_id].to_dict() for program_id in sorted(predictions)
            ],
        },
    )


def _write_report(path: Path, report: Any) -> None:
    payload = report.to_dict()
    payload["report_sha256"] = report.sha256()
    atomic_write_json(path, payload)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    assert_context_feature_boundary()
    seed_everything(args.seed)
    device = resolve_device(args.device)
    dataset_path = Path(args.dataset).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    if not dataset_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("--dataset and --manifest must name existing files")
    ingested = ingest_world_dataset(
        dataset_path,
        manifest_path,
        WorldIngestionConfig(segment_length=256, segment_stride=255, batch_size=args.batch_size),
    )
    witnesses = derive_temporal_witnesses(ingested)
    training = tuple(witness for witness in witnesses if witness.split.value == "train")
    train_partition_witnesses(training)

    run: CandidateRun | None = None
    try:
        run = CandidateRun.create(
            project_root=ROOT,
            candidate_id=args.candidate_id,
            seed=args.seed,
            additional_frozen_inputs={
                "world_dataset_jsonl": (dataset_path, sha256_file(dataset_path)),
                "world_dataset_manifest": (manifest_path, sha256_file(manifest_path)),
            },
        )
        config = {
            "experiment_version": EXPERIMENT_VERSION,
            "experiment_kind": "generated_temporal_context_positive_control",
            "target_evidence_label": "generated_temporal_state_witness",
            "input_feature_names": list(CONTEXT_INPUT_FEATURE_NAMES),
            "target_feature_names": list(TEMPORAL_TARGET_FEATURE_NAMES),
            "excluded_input_feature_classes": [
                "target_translation",
                "action_delta",
                "target_relations",
                "partition",
                "object_class",
                "operation_family",
                "program_id",
                "source_hash",
                "evidence_uri",
            ],
            "model": "mlp_8_32_32_5",
            "position_tolerance_mm": args.position_tolerance_mm,
            "learning_rate": args.learning_rate,
            "world_dataset_receipt": ingested.receipt.to_dict(),
            "temporal_witness_set_sha256": temporal_witness_set_sha256(witnesses),
            "no_world_model_claim": True,
            "no_automatic_promotion": True,
        }
        run.mark_training_started(
            config=config,
            turns=len(training),
            epochs=args.epochs,
            batch_size=args.batch_size,
            max_sequence_length=len(CONTEXT_INPUT_FEATURE_NAMES),
            device=str(device),
        )
        model = TemporalContextMLP(args.hidden_width).to(device)
        baseline = static_no_change_baseline(ingested)
        baseline_report = score_state_transition_predictions(
            ingested,
            baseline,
            position_tolerance_mm=args.position_tolerance_mm,
        )
        loss, updates, elapsed = train_model(
            model,
            training,
            device=device,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )
        predictions = model_predictions(model, witnesses, device=device)
        candidate_report = score_state_transition_predictions(
            ingested,
            predictions,
            position_tolerance_mm=args.position_tolerance_mm,
        )
        paths = {
            "baseline_predictions": run.assert_candidate_output(run.candidate_dir / "baseline_predictions.json"),
            "baseline_metrics": run.assert_candidate_output(run.candidate_dir / "baseline_metrics.json"),
            "candidate_predictions": run.assert_candidate_output(run.candidate_dir / "candidate_predictions.json"),
            "candidate_metrics": run.assert_candidate_output(run.candidate_dir / "candidate_metrics.json"),
            "run_summary": run.assert_candidate_output(run.candidate_dir / "temporal_context_run.json"),
        }
        _write_predictions(paths["baseline_predictions"], baseline)
        _write_report(paths["baseline_metrics"], baseline_report)
        _write_predictions(paths["candidate_predictions"], predictions)
        _write_report(paths["candidate_metrics"], candidate_report)
        atomic_write_json(
            paths["run_summary"],
            {
                "experiment_version": EXPERIMENT_VERSION,
                "experiment_kind": "generated_temporal_context_positive_control",
                "candidate_id": args.candidate_id,
                "code_commit": run.manifest["code_commit"],
                "target_manifest_sha256": ingested.receipt.manifest_sha256,
                "temporal_witness_set_sha256": temporal_witness_set_sha256(witnesses),
                "train_witness_count": len(training),
                "all_partition_witness_count": len(witnesses),
                "device": str(device),
                "training": {
                    "epochs": args.epochs,
                    "batch_size": args.batch_size,
                    "learning_rate": args.learning_rate,
                    "hidden_width": args.hidden_width,
                    "updates": updates,
                    "last_loss": loss,
                    "elapsed_seconds": elapsed,
                },
                "artifacts": {
                    name: _evidence(path)
                    for name, path in paths.items()
                    if name != "run_summary"
                },
                "claims": {
                    "generated_temporal_context_learnability_tested": True,
                    "observed_world_dynamics_proven": False,
                    "physical_dynamics_proven": False,
                    "renderer_correctness_proven": False,
                    "candidate_promoted": False,
                },
            },
        )
        checkpoint = run.save_checkpoint(
            {
                "model_state_dict": model.state_dict(),
                "experiment_config": config,
                "candidate_id": args.candidate_id,
                "seed": args.seed,
            },
            epoch=args.epochs,
            metrics={
                "last_train_loss": loss,
                "updates": updates,
                "elapsed_seconds": elapsed,
                "baseline_metrics_sha256": baseline_report.sha256(),
                "candidate_metrics_sha256": candidate_report.sha256(),
                "run_summary": _evidence(paths["run_summary"]),
            },
        )
        run.mark_completed()
        print(
            json.dumps(
                {
                    "candidate_id": args.candidate_id,
                    "candidate_dir": str(run.candidate_dir),
                    "checkpoint": _evidence(checkpoint),
                    "baseline_metrics": _evidence(paths["baseline_metrics"]),
                    "candidate_metrics": _evidence(paths["candidate_metrics"]),
                    "run_summary": _evidence(paths["run_summary"]),
                    "promotion_performed": False,
                    "generated_temporal_context_target": True,
                    "observed_world_dynamics_proven": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except BaseException as error:
        if run is not None:
            run.mark_failed(error)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
