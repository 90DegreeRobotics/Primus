"""Evaluate frozen rejected BridgeData candidates over observed open-loop action sequences.

This command is evaluation-only. It verifies recorded candidate evidence, loads
existing checkpoints read-only, recursively predicts from observed start states
and observed actions, and writes a new local result receipt. It creates no
candidate, trains no model, emits no action, and exposes no promotion path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from real_data.bridgedata_evaluation import (  # noqa: E402
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    ActionOnlyMeanDeltaBaseline,
    BridgeDataSplit,
    NearestTrainStateActionBaseline,
    transitions_by_split,
    validate_bridgedata_split,
)
from real_data.bridgedata_rollouts import (  # noqa: E402
    DEFAULT_CASE_SELECTION_SEED,
    DEFAULT_HORIZONS,
    DEFAULT_MAX_CASES_PER_HORIZON,
    BridgeDataRolloutError,
    action_only_mean_delta_predictor,
    copy_state_predictor,
    evaluate_rollout_predictor,
    nearest_train_state_action_predictor,
    predeclared_rollout_acceptance,
)
from real_data.bridgedata_transitions import (  # noqa: E402
    STATE_DIMENSIONS,
    BridgeDataTransitionConfig,
    derive_bridgedata_transitions,
    load_bridgedata_intake,
    sha256_file,
)
from train_bridgedata_real_transition import (  # noqa: E402
    BridgeDataResidualMLP,
    TrainOnlyNormalization,
    resolve_device,
)


ROLLOUT_EVALUATION_VERSION = 1
EXPECTED_CANDIDATE_IDS = ("bridge-real-20260827-001", "bridge-real-20260827-002")
DEFAULT_OUTPUT_DIR = ROOT / "evaluation" / "bridgedata_rollouts" / "rollout-20260827-001"


class FrozenRolloutEvidenceError(ValueError):
    """Raised when a supposedly frozen candidate/evidence input is invalid or drifts."""


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _sha256_json(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _safe_repo_path(relative_path: str, label: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        raise FrozenRolloutEvidenceError(f"{label} path is required")
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise FrozenRolloutEvidenceError(f"{label} path escapes the repository")
    path = (REPO_ROOT / relative).resolve()
    try:
        path.relative_to(REPO_ROOT.resolve())
    except ValueError as error:
        raise FrozenRolloutEvidenceError(f"{label} path escapes the repository") from error
    return path


def _verify_file_evidence(evidence: Mapping[str, Any], label: str) -> Path:
    if not isinstance(evidence, Mapping):
        raise FrozenRolloutEvidenceError(f"{label} evidence must be an object")
    path = _safe_repo_path(evidence.get("path"), label)
    if not path.is_file():
        raise FrozenRolloutEvidenceError(f"{label} file is missing")
    expected_bytes = evidence.get("bytes")
    expected_hash = evidence.get("sha256")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes < 0:
        raise FrozenRolloutEvidenceError(f"{label} evidence bytes are invalid")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise FrozenRolloutEvidenceError(f"{label} evidence SHA-256 is invalid")
    if path.stat().st_size != expected_bytes:
        raise FrozenRolloutEvidenceError(f"{label} byte count drifted")
    actual_hash = sha256_file(path)
    if actual_hash != expected_hash:
        raise FrozenRolloutEvidenceError(f"{label} SHA-256 drifted")
    return path


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FrozenRolloutEvidenceError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise FrozenRolloutEvidenceError(f"{label} root must be an object")
    return value


def _split_from_payload(payload: Mapping[str, Any]) -> BridgeDataSplit:
    try:
        split = BridgeDataSplit(
            split_version=int(payload["split_version"]),
            config=dict(payload["config"]),
            train_episode_indices=tuple(int(item) for item in payload["train_episode_indices"]),
            held_out_episode_indices=tuple(int(item) for item in payload["held_out_episode_indices"]),
            held_out_task_episode_indices=tuple(int(item) for item in payload["held_out_task_episode_indices"]),
            train_task_indices=tuple(int(item) for item in payload["train_task_indices"]),
            held_out_episode_task_indices=tuple(int(item) for item in payload["held_out_episode_task_indices"]),
            held_out_task_indices=tuple(int(item) for item in payload["held_out_task_indices"]),
            excluded_unmapped_episode_indices=tuple(int(item) for item in payload["excluded_unmapped_episode_indices"]),
            excluded_by_budget_episode_indices=tuple(int(item) for item in payload["excluded_by_budget_episode_indices"]),
            expected_transition_counts={str(key): int(value) for key, value in payload["expected_transition_counts"].items()},
        )
    except (KeyError, TypeError, ValueError) as error:
        raise FrozenRolloutEvidenceError("candidate bounded split evidence has an invalid shape") from error
    return split


def _normalizer_from_payload(payload: Mapping[str, Any]) -> TrainOnlyNormalization:
    try:
        normalizer = TrainOnlyNormalization(
            input_mean=tuple(float(item) for item in payload["input_mean"]),
            input_scale=tuple(float(item) for item in payload["input_scale"]),
            delta_mean=tuple(float(item) for item in payload["delta_mean"]),
            delta_scale=tuple(float(item) for item in payload["delta_scale"]),
            train_transition_ids=tuple(str(item) for item in payload["train_transition_ids"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise FrozenRolloutEvidenceError("checkpoint normalization has an invalid shape") from error
    if any(
        len(values) != STATE_DIMENSIONS
        for values in (normalizer.delta_mean, normalizer.delta_scale)
    ) or any(
        len(values) != STATE_DIMENSIONS * 2
        for values in (normalizer.input_mean, normalizer.input_scale)
    ):
        raise FrozenRolloutEvidenceError("checkpoint normalization dimensions disagree with the 7D contract")
    if not normalizer.train_transition_ids or len(normalizer.train_transition_ids) != len(set(normalizer.train_transition_ids)):
        raise FrozenRolloutEvidenceError("checkpoint normalization train IDs are missing or non-unique")
    if not all(
        math.isfinite(value)
        for values in (
            normalizer.input_mean,
            normalizer.input_scale,
            normalizer.delta_mean,
            normalizer.delta_scale,
        )
        for value in values
    ) or any(value <= 0 for values in (normalizer.input_scale, normalizer.delta_scale) for value in values):
        raise FrozenRolloutEvidenceError("checkpoint normalization contains invalid values")
    return normalizer


def load_frozen_rollout_candidate(candidate_id: str, *, device: torch.device) -> dict[str, Any]:
    """Verify and reconstruct one terminal rejected candidate without mutation."""

    if candidate_id not in EXPECTED_CANDIDATE_IDS:
        raise FrozenRolloutEvidenceError("candidate ID is not a predeclared rollout subject")
    candidate_dir = ROOT / "checkpoints" / "candidates" / candidate_id
    manifest_path = candidate_dir / "real_data.run.manifest.json"
    if not manifest_path.is_file():
        raise FrozenRolloutEvidenceError("candidate lifecycle manifest is missing")
    manifest = _load_json_object(manifest_path, "candidate lifecycle manifest")
    if manifest.get("candidate_id") != candidate_id:
        raise FrozenRolloutEvidenceError("candidate lifecycle manifest ID disagrees with requested candidate")
    if manifest.get("candidate_kind") != "bridgedata_observed_state_transition":
        raise FrozenRolloutEvidenceError("candidate kind is not the declared BridgeData transition experiment")
    if manifest.get("status") != "rejected" or manifest.get("promotion", {}).get("performed") is not False:
        raise FrozenRolloutEvidenceError("rollout evaluation requires a terminal rejected no-promotion candidate")
    if manifest.get("parent_protection", {}).get("touched_by_training") is not False:
        raise FrozenRolloutEvidenceError("candidate lifecycle indicates protected parent mutation")

    checkpoint_path = _verify_file_evidence(manifest.get("checkpoint"), "candidate checkpoint")
    metrics_path = _verify_file_evidence(manifest.get("evaluation", {}).get("metrics_report"), "candidate metrics")
    predictions_path = _verify_file_evidence(manifest.get("evaluation", {}).get("predictions"), "candidate raw predictions")
    frozen_inputs = manifest.get("additional_frozen_inputs")
    if not isinstance(frozen_inputs, Mapping):
        raise FrozenRolloutEvidenceError("candidate lacks frozen input evidence")
    input_paths = {
        name: _verify_file_evidence(evidence, f"candidate frozen input {name}")
        for name, evidence in frozen_inputs.items()
    }
    for label in ("intake_manifest", "data_parquet", "episodes_parquet", "tasks_parquet"):
        if label not in input_paths:
            raise FrozenRolloutEvidenceError(f"candidate lacks required frozen input: {label}")
    for label, evidence in manifest.get("parent_protection", {}).items():
        if label in ("live_parent", "frozen_parent"):
            _verify_file_evidence(evidence, f"candidate parent protection {label}")

    split_path = candidate_dir / "evidence" / "split.json"
    if not split_path.is_file():
        raise FrozenRolloutEvidenceError("candidate bounded split evidence is missing")
    split_payload = _load_json_object(split_path, "candidate split evidence")
    bounded_payload = split_payload.get("bounded_group_split")
    if not isinstance(bounded_payload, Mapping):
        raise FrozenRolloutEvidenceError("candidate split evidence lacks bounded group split")
    split = _split_from_payload(bounded_payload)
    config = manifest.get("config")
    if not isinstance(config, Mapping) or config.get("split_sha256") != split.sha256():
        raise FrozenRolloutEvidenceError("candidate split evidence does not match manifest-bound split hash")

    manifest_path_from_input = input_paths["intake_manifest"]
    intake = load_bridgedata_intake(manifest_path_from_input)
    selected = frozenset(
        split.train_episode_indices
        + split.held_out_episode_indices
        + split.held_out_task_episode_indices
    )
    validate_bridgedata_split(split, intake.episodes)
    extracted = derive_bridgedata_transitions(
        intake,
        BridgeDataTransitionConfig(selected_episode_indices=selected),
    )
    if config.get("extraction_receipt_sha256") != extracted.receipt.sha256():
        raise FrozenRolloutEvidenceError("re-extracted transition receipt does not match candidate manifest")
    partitioned = transitions_by_split(extracted.transitions, split)

    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    if not isinstance(checkpoint, Mapping) or not isinstance(checkpoint.get("state_dict"), Mapping):
        raise FrozenRolloutEvidenceError("candidate checkpoint lacks a state dictionary")
    checkpoint_config = checkpoint.get("training_config")
    if not isinstance(checkpoint_config, Mapping) or checkpoint_config != config:
        raise FrozenRolloutEvidenceError("checkpoint training configuration differs from lifecycle manifest")
    normalizer_payload = checkpoint.get("normalization")
    if not isinstance(normalizer_payload, Mapping):
        raise FrozenRolloutEvidenceError("candidate checkpoint lacks train-only normalization")
    normalizer = _normalizer_from_payload(normalizer_payload)
    if len(normalizer.train_transition_ids) != config.get("normalization_train_transition_count"):
        raise FrozenRolloutEvidenceError("checkpoint normalization train count disagrees with manifest")
    expected_train_ids = {transition.transition_id for transition in partitioned[TRAIN_SPLIT]}
    if set(normalizer.train_transition_ids) != expected_train_ids:
        raise FrozenRolloutEvidenceError("checkpoint normalization does not bind exactly the candidate training transitions")
    hidden_dimensions = config.get("hidden_dimensions")
    if isinstance(hidden_dimensions, bool) or not isinstance(hidden_dimensions, int):
        raise FrozenRolloutEvidenceError("candidate hidden dimension is invalid")
    model = BridgeDataResidualMLP(hidden_dimensions=hidden_dimensions)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()

    def model_predictor(state: tuple[float, ...], action: tuple[float, ...]) -> tuple[float, ...]:
        if len(state) != STATE_DIMENSIONS or len(action) != STATE_DIMENSIONS:
            raise BridgeDataRolloutError("frozen model rollout state/action dimensions are invalid")
        features = np.asarray(state + action, dtype=np.float32)
        normalized = (features - np.asarray(normalizer.input_mean, dtype=np.float32)) / np.asarray(
            normalizer.input_scale, dtype=np.float32
        )
        with torch.no_grad():
            output = model(torch.from_numpy(normalized[None, :]).to(device)).detach().cpu().numpy()[0]
        delta = output * np.asarray(normalizer.delta_scale) + np.asarray(normalizer.delta_mean)
        result = tuple(float(value + offset) for value, offset in zip(state, delta))
        if not all(math.isfinite(value) for value in result):
            raise BridgeDataRolloutError("frozen model emitted a non-finite rollout state")
        return result

    return {
        "candidate_id": candidate_id,
        "candidate_dir": candidate_dir,
        "manifest_path": manifest_path,
        "manifest_sha256": sha256_file(manifest_path),
        "split_path": split_path,
        "split_evidence_sha256": sha256_file(split_path),
        "checkpoint_path": checkpoint_path,
        "checkpoint_sha256": manifest["checkpoint"]["sha256"],
        "metrics_path": metrics_path,
        "metrics_sha256": manifest["evaluation"]["metrics_report"]["sha256"],
        "predictions_path": predictions_path,
        "predictions_sha256": manifest["evaluation"]["predictions"]["sha256"],
        "intake_manifest_sha256": intake.manifest_sha256,
        "transition_receipt_sha256": extracted.receipt.sha256(),
        "transition_set_sha256": extracted.receipt.transition_set_sha256,
        "split": split,
        "partitioned_transitions": partitioned,
        "model_predictor": model_predictor,
    }


def _write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists():
        raise FrozenRolloutEvidenceError("rollout evidence destination already exists")
    path.parent.mkdir(parents=True, exist_ok=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
        handle.write("\n")
    os.replace(temporary, path)


def evaluate_frozen_candidates(
    candidate_ids: Sequence[str],
    *,
    output_dir: Path,
    device_name: str = "cpu",
) -> dict[str, Any]:
    """Evaluate both predeclared frozen candidates once and atomically preserve evidence."""

    identifiers = tuple(candidate_ids)
    if identifiers != EXPECTED_CANDIDATE_IDS:
        raise FrozenRolloutEvidenceError(
            "rollout evaluation requires exactly the ordered predeclared candidates: "
            + ", ".join(EXPECTED_CANDIDATE_IDS)
        )
    destination = output_dir.expanduser().resolve()
    allowed_root = (ROOT / "evaluation" / "bridgedata_rollouts").resolve()
    try:
        destination.relative_to(allowed_root)
    except ValueError as error:
        raise FrozenRolloutEvidenceError("rollout output must remain under the ignored local evaluation directory") from error
    if destination.exists():
        raise FrozenRolloutEvidenceError("rollout output destination already exists")
    device = resolve_device(device_name)
    candidate_results: dict[str, Any] = {}
    for candidate_id in identifiers:
        frozen = load_frozen_rollout_candidate(candidate_id, device=device)
        partitioned = frozen["partitioned_transitions"]
        action_baseline = ActionOnlyMeanDeltaBaseline.fit(partitioned[TRAIN_SPLIT])
        nearest_baseline = NearestTrainStateActionBaseline.fit(partitioned[TRAIN_SPLIT])
        candidate_report = evaluate_rollout_predictor(
            partitioned,
            prediction_label="frozen_residual_mlp",
            predict_next_state=frozen["model_predictor"],
        )
        baseline_reports = {
            "copy_state": evaluate_rollout_predictor(
                partitioned,
                prediction_label="copy_state",
                predict_next_state=copy_state_predictor,
            ),
            "action_only_mean_delta": evaluate_rollout_predictor(
                partitioned,
                prediction_label="action_only_mean_delta",
                predict_next_state=action_only_mean_delta_predictor(action_baseline),
            ),
            "nearest_train_state_action": evaluate_rollout_predictor(
                partitioned,
                prediction_label="nearest_train_state_action",
                predict_next_state=nearest_train_state_action_predictor(nearest_baseline),
            ),
        }
        candidate_results[candidate_id] = {
            "frozen_inputs": {
                key: frozen[key]
                for key in (
                    "manifest_sha256",
                    "split_evidence_sha256",
                    "checkpoint_sha256",
                    "metrics_sha256",
                    "predictions_sha256",
                    "intake_manifest_sha256",
                    "transition_receipt_sha256",
                    "transition_set_sha256",
                )
            },
            "split": frozen["split"].to_dict(),
            "candidate_report": candidate_report.to_dict(),
            "baseline_reports": {label: report.to_dict() for label, report in baseline_reports.items()},
            "acceptance": predeclared_rollout_acceptance(candidate_report, baseline_reports),
        }
    payload = {
        "rollout_evaluation_version": ROLLOUT_EVALUATION_VERSION,
        "candidate_ids": list(identifiers),
        "device": str(device),
        "horizons": list(DEFAULT_HORIZONS),
        "case_selection_seed": DEFAULT_CASE_SELECTION_SEED,
        "max_cases_per_horizon": DEFAULT_MAX_CASES_PER_HORIZON,
        "candidates": candidate_results,
        "no_training": True,
        "no_candidate_creation": True,
        "no_checkpoint_mutation": True,
        "promotion_performed": False,
        "notes": [
            "Read-only open-loop evaluation over frozen terminal rejected candidates.",
            "Each rollout begins at an observed state and uses recorded observed actions; only the predictor output feeds the next step.",
            "Metrics are split- and horizon-separated over deterministic bounded case selections. No pooled protected result is emitted.",
            "This is not robot-policy, control, safety, renderer, native Chronos, or promotion evidence.",
        ],
    }
    payload["payload_sha256"] = _sha256_json(payload)
    _write_new_json(destination / "rollout_stability.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate frozen BridgeData candidates over observed open-loop action sequences.")
    parser.add_argument("--candidate-id", action="append", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--device", default="cpu", choices=("cpu", "auto", "cuda"))
    arguments = parser.parse_args()
    result = evaluate_frozen_candidates(
        arguments.candidate_id,
        output_dir=Path(arguments.output_dir),
        device_name=arguments.device,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
