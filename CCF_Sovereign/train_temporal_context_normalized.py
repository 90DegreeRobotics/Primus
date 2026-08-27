"""Equal-budget train-only normalization ablation for temporal context."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from train_temporal_context import (
    EXPERIMENT_VERSION,
    TemporalContextMLP,
    parse_args,
    resolve_device,
    seed_everything,
    train_partition_witnesses,
)
from training.candidate_run import CandidateRun, atomic_write_json, sha256_file
from world_data.ingestion import WorldIngestionConfig, ingest_world_dataset
from world_data.normalization import TemporalContextNormalization, fit_train_only_normalization
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


def _features(witnesses: tuple[TemporalStateWitness, ...], receipt: TemporalContextNormalization, device: torch.device) -> torch.Tensor:
    return torch.tensor([receipt.normalize_features(w.context_input_vector) for w in witnesses], dtype=torch.float32, device=device)


def _targets(witnesses: tuple[TemporalStateWitness, ...], receipt: TemporalContextNormalization, device: torch.device) -> torch.Tensor:
    rows = []
    for witness in witnesses:
        position = receipt.normalize_position_target(witness.target_vector[:3])
        rows.append((*position, *witness.target_vector[3:]))
    return torch.tensor(rows, dtype=torch.float32, device=device)


def train_normalized_model(model: TemporalContextMLP, witnesses: Iterable[TemporalStateWitness], receipt: TemporalContextNormalization, *, device: torch.device, epochs: int, batch_size: int, learning_rate: float) -> tuple[float, int, float]:
    training = train_partition_witnesses(witnesses)
    features, targets = _features(training, receipt, device), _targets(training, receipt, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.0)
    started, updates, last_loss = time.perf_counter(), 0, float("nan")
    model.train()
    for _ in range(epochs):
        for start in range(0, len(training), batch_size):
            stop = min(start + batch_size, len(training))
            output = model(features[start:stop])
            loss = F.mse_loss(output[:, :3], targets[start:stop, :3]) + F.binary_cross_entropy_with_logits(output[:, 3:], targets[start:stop, 3:])
            if not torch.isfinite(loss):
                raise RuntimeError("normalized temporal-context loss became non-finite")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            last_loss, updates = float(loss.detach().cpu().item()), updates + 1
    return last_loss, updates, time.perf_counter() - started


def normalized_predictions(model: TemporalContextMLP, witnesses: Iterable[TemporalStateWitness], receipt: TemporalContextNormalization, *, device: torch.device) -> dict[str, StateTransitionPrediction]:
    materialized = tuple(witnesses)
    if not materialized:
        raise ValueError("prediction witness set cannot be empty")
    model.eval()
    with torch.no_grad():
        output = model(_features(materialized, receipt, device)).detach().cpu()
    predictions: dict[str, StateTransitionPrediction] = {}
    for witness, row in zip(materialized, output):
        if witness.program_id in predictions:
            raise ValueError(f"duplicate witness ID: {witness.program_id}")
        position_m = receipt.denormalize_position_target(tuple(float(value) for value in row[:3]))
        predictions[witness.program_id] = StateTransitionPrediction(
            program_id=witness.program_id,
            target_translation_mm=tuple(value * 1000.0 for value in position_m),
            support_present_after=bool(torch.sigmoid(row[3]).item() >= 0.5),
            near_present_after=bool(torch.sigmoid(row[4]).item() >= 0.5),
        )
    return predictions


def _evidence(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def _write_predictions(path: Path, predictions: dict[str, StateTransitionPrediction]) -> None:
    atomic_write_json(path, {"experiment_version": EXPERIMENT_VERSION, "prediction_count": len(predictions), "prediction_input_feature_names": list(CONTEXT_INPUT_FEATURE_NAMES), "predictions": [predictions[key].to_dict() for key in sorted(predictions)]})


def _write_report(path: Path, report: Any) -> None:
    payload = report.to_dict(); payload["report_sha256"] = report.sha256(); atomic_write_json(path, payload)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    assert_context_feature_boundary(); seed_everything(args.seed); device = resolve_device(args.device)
    dataset_path, manifest_path = Path(args.dataset).expanduser().resolve(), Path(args.manifest).expanduser().resolve()
    if not dataset_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("--dataset and --manifest must name existing files")
    ingested = ingest_world_dataset(dataset_path, manifest_path, WorldIngestionConfig(segment_length=256, segment_stride=255, batch_size=args.batch_size))
    witnesses = derive_temporal_witnesses(ingested)
    training = tuple(w for w in witnesses if w.split.value == "train")
    train_partition_witnesses(training)
    receipt = fit_train_only_normalization(training)
    run: CandidateRun | None = None
    try:
        run = CandidateRun.create(project_root=ROOT, candidate_id=args.candidate_id, seed=args.seed, additional_frozen_inputs={"world_dataset_jsonl": (dataset_path, sha256_file(dataset_path)), "world_dataset_manifest": (manifest_path, sha256_file(manifest_path))})
        config = {"experiment_version": EXPERIMENT_VERSION, "experiment_kind": "generated_temporal_context_normalization_ablation", "target_evidence_label": "generated_temporal_state_witness", "input_feature_names": list(CONTEXT_INPUT_FEATURE_NAMES), "target_feature_names": list(TEMPORAL_TARGET_FEATURE_NAMES), "excluded_input_feature_classes": ["target_translation", "action_delta", "target_relations", "partition", "object_class", "operation_family", "program_id", "source_hash", "evidence_uri"], "model": "mlp_8_32_32_5", "position_tolerance_mm": args.position_tolerance_mm, "learning_rate": args.learning_rate, "normalization": receipt.to_dict(), "normalization_sha256": receipt.sha256(), "world_dataset_receipt": ingested.receipt.to_dict(), "temporal_witness_set_sha256": temporal_witness_set_sha256(witnesses), "fixed_budget_reference": "temporal-context-20260827-0742-mlp", "no_world_model_claim": True, "no_automatic_promotion": True}
        run.mark_training_started(config=config, turns=len(training), epochs=args.epochs, batch_size=args.batch_size, max_sequence_length=len(CONTEXT_INPUT_FEATURE_NAMES), device=str(device))
        model = TemporalContextMLP(args.hidden_width).to(device)
        baseline = static_no_change_baseline(ingested)
        baseline_report = score_state_transition_predictions(ingested, baseline, position_tolerance_mm=args.position_tolerance_mm)
        loss, updates, elapsed = train_normalized_model(model, training, receipt, device=device, epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.learning_rate)
        predictions = normalized_predictions(model, witnesses, receipt, device=device)
        candidate_report = score_state_transition_predictions(ingested, predictions, position_tolerance_mm=args.position_tolerance_mm)
        paths = {name: run.assert_candidate_output(run.candidate_dir / filename) for name, filename in {"normalization": "normalization.json", "baseline_predictions": "baseline_predictions.json", "baseline_metrics": "baseline_metrics.json", "candidate_predictions": "candidate_predictions.json", "candidate_metrics": "candidate_metrics.json", "run_summary": "temporal_context_normalized_run.json"}.items()}
        payload = receipt.to_dict(); payload["normalization_sha256"] = receipt.sha256(); atomic_write_json(paths["normalization"], payload)
        _write_predictions(paths["baseline_predictions"], baseline); _write_report(paths["baseline_metrics"], baseline_report); _write_predictions(paths["candidate_predictions"], predictions); _write_report(paths["candidate_metrics"], candidate_report)
        atomic_write_json(paths["run_summary"], {"experiment_version": EXPERIMENT_VERSION, "experiment_kind": config["experiment_kind"], "candidate_id": args.candidate_id, "code_commit": run.manifest["code_commit"], "target_manifest_sha256": ingested.receipt.manifest_sha256, "temporal_witness_set_sha256": temporal_witness_set_sha256(witnesses), "normalization": _evidence(paths["normalization"]), "normalization_sha256": receipt.sha256(), "fixed_budget_reference": config["fixed_budget_reference"], "train_witness_count": len(training), "all_partition_witness_count": len(witnesses), "device": str(device), "training": {"epochs": args.epochs, "batch_size": args.batch_size, "learning_rate": args.learning_rate, "hidden_width": args.hidden_width, "updates": updates, "last_loss": loss, "elapsed_seconds": elapsed}, "artifacts": {name: _evidence(path) for name, path in paths.items() if name not in {"run_summary", "normalization"}}, "claims": {"generated_temporal_context_normalization_tested": True, "observed_world_dynamics_proven": False, "physical_dynamics_proven": False, "candidate_promoted": False}})
        checkpoint = run.save_checkpoint({"model_state_dict": model.state_dict(), "experiment_config": config, "normalization": receipt.to_dict(), "candidate_id": args.candidate_id, "seed": args.seed}, epoch=args.epochs, metrics={"last_train_loss": loss, "updates": updates, "elapsed_seconds": elapsed, "normalization_sha256": receipt.sha256(), "baseline_metrics_sha256": baseline_report.sha256(), "candidate_metrics_sha256": candidate_report.sha256(), "run_summary": _evidence(paths["run_summary"])})
        run.mark_completed()
        print(json.dumps({"candidate_id": args.candidate_id, "candidate_dir": str(run.candidate_dir), "checkpoint": _evidence(checkpoint), "normalization": _evidence(paths["normalization"]), "baseline_metrics": _evidence(paths["baseline_metrics"]), "candidate_metrics": _evidence(paths["candidate_metrics"]), "run_summary": _evidence(paths["run_summary"]), "promotion_performed": False, "observed_world_dynamics_proven": False}, indent=2, sort_keys=True))
        return 0
    except BaseException as error:
        if run is not None: run.mark_failed(error)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
