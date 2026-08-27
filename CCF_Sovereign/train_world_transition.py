"""Train one isolated candidate on explicit generated WorldProgram transitions.

This is a narrow positive-control experiment. It learns generated arithmetic and
relation-transition targets from the train partition only; it is not a renderer,
physical dynamics learner, observed-world result, or promotion path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from training.candidate_run import CandidateRun, atomic_write_json, sha256_file
from world_data.ingestion import WorldIngestionConfig, ingest_world_dataset
from world_data.transitions import (
    INPUT_FEATURE_NAMES,
    TARGET_FEATURE_NAMES,
    derive_transition_examples,
    example_set_sha256,
    train_partition_examples,
)
from world_metrics.state_transitions import (
    StateTransitionPrediction,
    score_state_transition_predictions,
    static_no_change_baseline,
)


EXPERIMENT_VERSION = 1


class WorldTransitionRegressor(torch.nn.Module):
    """Small direct regressor for the explicit generated transition target."""

    def __init__(self) -> None:
        super().__init__()
        self.projection = torch.nn.Linear(
            len(INPUT_FEATURE_NAMES), len(TARGET_FEATURE_NAMES)
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.projection(features)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train one isolated, generated-transition positive-control candidate. "
            "No parent mutation or promotion occurs."
        )
    )
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--dataset", required=True, help="Frozen Stage 2 JSONL")
    parser.add_argument("--manifest", required=True, help="Frozen Stage 2 manifest")
    parser.add_argument("--seed", type=int, default=20260827)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.03)
    parser.add_argument("--position-tolerance-mm", type=float, default=25.0)
    args = parser.parse_args(argv)
    if args.seed < 0:
        parser.error("--seed must be non-negative")
    for name in ("epochs", "batch_size"):
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


def _feature_tensor(examples: tuple[Any, ...], device: torch.device) -> torch.Tensor:
    return torch.tensor(
        [example.input_vector for example in examples],
        dtype=torch.float32,
        device=device,
    )


def _target_tensor(examples: tuple[Any, ...], device: torch.device) -> torch.Tensor:
    return torch.tensor(
        [example.target_vector for example in examples],
        dtype=torch.float32,
        device=device,
    )


def train_regressor(
    model: WorldTransitionRegressor,
    examples: tuple[Any, ...],
    *,
    device: torch.device,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> tuple[float, int, float]:
    """Fit only verified train-partition examples and return measured work."""

    train_partition_examples(examples)
    features = _feature_tensor(examples, device)
    targets = _target_tensor(examples, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.0)
    model.train()
    started = time.perf_counter()
    last_loss = float("nan")
    updates = 0
    for _ in range(epochs):
        for start in range(0, len(examples), batch_size):
            stop = min(start + batch_size, len(examples))
            predicted = model(features[start:stop])
            position_loss = F.mse_loss(predicted[:, :3], targets[start:stop, :3])
            relation_loss = F.binary_cross_entropy_with_logits(
                predicted[:, 3:], targets[start:stop, 3:]
            )
            loss = position_loss + relation_loss
            if not torch.isfinite(loss):
                raise RuntimeError("generated-transition loss became non-finite")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            last_loss = float(loss.detach().cpu().item())
            updates += 1
    elapsed = time.perf_counter() - started
    return last_loss, updates, elapsed


def model_predictions(
    model: WorldTransitionRegressor,
    examples: tuple[Any, ...],
    *,
    device: torch.device,
) -> dict[str, StateTransitionPrediction]:
    """Convert model outputs into exact-coverage typed transition predictions."""

    model.eval()
    features = _feature_tensor(examples, device)
    with torch.no_grad():
        outputs = model(features).detach().cpu()
    predictions: dict[str, StateTransitionPrediction] = {}
    for example, row in zip(examples, outputs):
        predictions[example.program_id] = StateTransitionPrediction(
            program_id=example.program_id,
            target_translation_mm=tuple(float(value * 1000.0) for value in row[:3]),
            support_present_after=bool(torch.sigmoid(row[3]).item() >= 0.5),
            near_present_after=bool(torch.sigmoid(row[4]).item() >= 0.5),
        )
    return predictions


def _json_evidence(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def _write_predictions(
    path: Path,
    predictions: dict[str, StateTransitionPrediction],
) -> None:
    atomic_write_json(
        path,
        {
            "experiment_version": EXPERIMENT_VERSION,
            "prediction_count": len(predictions),
            "predictions": [
                predictions[program_id].to_dict()
                for program_id in sorted(predictions)
            ],
        },
    )


def _write_report(path: Path, report: Any) -> None:
    payload = report.to_dict()
    payload["report_sha256"] = report.sha256()
    atomic_write_json(path, payload)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
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
    examples = derive_transition_examples(ingested)
    training_examples = tuple(
        example for example in examples if example.split.value == "train"
    )
    train_partition_examples(training_examples)

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
            "experiment_kind": "generated_world_transition_positive_control",
            "target_evidence_label": "generated_transition_target",
            "input_feature_names": list(INPUT_FEATURE_NAMES),
            "target_feature_names": list(TARGET_FEATURE_NAMES),
            "model": "linear_6_to_5",
            "position_tolerance_mm": args.position_tolerance_mm,
            "learning_rate": args.learning_rate,
            "world_dataset_receipt": ingested.receipt.to_dict(),
            "transition_example_set_sha256": example_set_sha256(examples),
            "no_world_model_claim": True,
            "no_automatic_promotion": True,
        }
        run.mark_training_started(
            config=config,
            turns=len(training_examples),
            epochs=args.epochs,
            batch_size=args.batch_size,
            max_sequence_length=len(INPUT_FEATURE_NAMES),
            device=str(device),
        )
        model = WorldTransitionRegressor().to(device)
        baseline = static_no_change_baseline(ingested)
        baseline_report = score_state_transition_predictions(
            ingested,
            baseline,
            position_tolerance_mm=args.position_tolerance_mm,
        )
        loss, updates, elapsed = train_regressor(
            model,
            training_examples,
            device=device,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )
        predictions = model_predictions(model, examples, device=device)
        candidate_report = score_state_transition_predictions(
            ingested,
            predictions,
            position_tolerance_mm=args.position_tolerance_mm,
        )

        paths = {
            "baseline_predictions": run.assert_candidate_output(
                run.candidate_dir / "baseline_predictions.json"
            ),
            "baseline_metrics": run.assert_candidate_output(
                run.candidate_dir / "baseline_metrics.json"
            ),
            "candidate_predictions": run.assert_candidate_output(
                run.candidate_dir / "candidate_predictions.json"
            ),
            "candidate_metrics": run.assert_candidate_output(
                run.candidate_dir / "candidate_metrics.json"
            ),
            "run_summary": run.assert_candidate_output(
                run.candidate_dir / "world_transition_run.json"
            ),
        }
        _write_predictions(paths["baseline_predictions"], baseline)
        _write_report(paths["baseline_metrics"], baseline_report)
        _write_predictions(paths["candidate_predictions"], predictions)
        _write_report(paths["candidate_metrics"], candidate_report)
        atomic_write_json(
            paths["run_summary"],
            {
                "experiment_version": EXPERIMENT_VERSION,
                "experiment_kind": "generated_world_transition_positive_control",
                "candidate_id": args.candidate_id,
                "code_commit": run.manifest["code_commit"],
                "target_manifest_sha256": ingested.receipt.manifest_sha256,
                "transition_example_set_sha256": example_set_sha256(examples),
                "train_example_count": len(training_examples),
                "all_partition_example_count": len(examples),
                "device": str(device),
                "training": {
                    "epochs": args.epochs,
                    "batch_size": args.batch_size,
                    "learning_rate": args.learning_rate,
                    "updates": updates,
                    "last_loss": loss,
                    "elapsed_seconds": elapsed,
                },
                "artifacts": {name: _json_evidence(path) for name, path in paths.items() if name != "run_summary"},
                "claims": {
                    "generated_transition_learnability_tested": True,
                    "observed_world_dynamics_proven": False,
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
                "run_summary": _json_evidence(paths["run_summary"]),
            },
        )
        run.mark_completed()
        print(
            json.dumps(
                {
                    "candidate_id": args.candidate_id,
                    "candidate_dir": str(run.candidate_dir),
                    "checkpoint": _json_evidence(checkpoint),
                    "baseline_metrics": _json_evidence(paths["baseline_metrics"]),
                    "candidate_metrics": _json_evidence(paths["candidate_metrics"]),
                    "run_summary": _json_evidence(paths["run_summary"]),
                    "promotion_performed": False,
                    "generated_transition_target": True,
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
