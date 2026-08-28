"""Read-only strict source-train-task-disjoint BridgeData rollout evaluation.

This evaluator intentionally does not use the target candidate's split.  For
both frozen rejected source candidates it deterministically selects complete
BridgeData episodes that are outside the source candidate's selected episodes
and whose task identities are absent from the source candidate's train split.
It derives those observed transitions read-only, rolls each frozen source model
open-loop under recorded actions, compares only source-train fitted baselines,
and records a point estimate plus paired episode-clustered bootstrap label.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from evaluate_bridgedata_rollout_stability import (  # noqa: E402
    EXPECTED_CANDIDATE_IDS,
    ROOT,
    FrozenRolloutEvidenceError,
    _sha256_json,
    _write_new_json,
    load_frozen_rollout_candidate,
)
from evaluate_bridgedata_task_disjoint_feasibility import (  # noqa: E402
    task_disjoint_episode_pool,
)
from real_data.bridgedata_evaluation import (  # noqa: E402
    TRAIN_SPLIT,
    ActionOnlyMeanDeltaBaseline,
    LinearStateActionDeltaBaseline,
    NearestTrainStateActionBaseline,
)
from real_data.bridgedata_rollout_uncertainty import (  # noqa: E402
    DEFAULT_BOOTSTRAP_RESAMPLES,
    DEFAULT_BOOTSTRAP_SEED,
    DEFAULT_MIN_DISTINCT_EPISODES,
    episode_clustered_paired_bootstrap,
    paired_rollout_case_errors,
)
from real_data.bridgedata_rollouts import (  # noqa: E402
    DEFAULT_CASE_SELECTION_SEED,
    DEFAULT_MAX_CASES_PER_HORIZON,
    action_only_mean_delta_predictor,
    build_rollout_cases,
    copy_state_predictor,
    linear_state_action_delta_predictor,
    nearest_train_state_action_predictor,
    rollout_predictions,
    score_rollout_predictions,
)
from real_data.bridgedata_transitions import (  # noqa: E402
    BridgeDataTransitionConfig,
    derive_bridgedata_transitions,
    load_bridgedata_intake,
    sha256_file,
)
from train_bridgedata_real_transition import resolve_device  # noqa: E402


STRICT_TASK_CROSS_ROLLOUT_VERSION = 1
ACCEPTANCE_HORIZONS = (1, 2, 5)
STRICT_TARGET_EPISODE_BUDGET = 128
STRICT_TARGET_SELECTION_SEED = 20_260_828
FEASIBILITY_RECEIPT_PATH = (
    ROOT
    / "evaluation"
    / "bridgedata_task_disjoint_feasibility"
    / "task-disjoint-feasibility-20260828-001"
    / "task_disjoint_feasibility.json"
)
FEASIBILITY_RECEIPT_SHA256 = "c56fb16e1fa6a45691af1d95240721c949d0bdcf3641a951315538fad8bcff54"
INTAKE_MANIFEST_PATH = (
    ROOT
    / "data"
    / "external"
    / "bridgedata2_lerobot_v3_metadata_20260827"
    / "intake_manifest.json"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "evaluation"
    / "bridgedata_strict_task_cross_rollouts"
    / "strict-task-cross-rollout-20260828-001"
)


class StrictTaskCrossRolloutError(ValueError):
    """Raised when strict task-disjoint rollout evaluation is ineligible."""


def _episode_set(split: Any, name: str) -> set[int]:
    return {int(value) for value in split.episode_indices(name)}


def _task_set(split: Any, name: str) -> set[int]:
    return {int(value) for value in split.task_indices(name)}


def _selected_episode_set(split: Any) -> set[int]:
    names = (TRAIN_SPLIT, "held_out_episode", "held_out_task")
    return set().union(*(_episode_set(split, name) for name in names))


def _stable_episode_key(source_candidate_id: str, episode_index: int) -> tuple[str, int]:
    digest = hashlib.sha256(
        f"{STRICT_TARGET_SELECTION_SEED}:strict-task-target:{source_candidate_id}:{episode_index}".encode("ascii")
    ).hexdigest()
    return digest, episode_index


def _canonical_target_pool_sha256(pool: Sequence[Any]) -> str:
    if not pool:
        raise StrictTaskCrossRolloutError("strict target pool is empty")
    material = "\n".join(
        f"{item.episode_index}:{item.task_index}:{item.length}:{item.dataset_from_index}:{item.dataset_to_index}"
        for item in sorted(pool, key=lambda item: item.episode_index)
    ) + "\n"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def select_strict_target_episodes(
    source_candidate_id: str,
    source_split: Any,
    episodes: Mapping[int, Any],
    *,
    episode_budget: int = STRICT_TARGET_EPISODE_BUDGET,
) -> tuple[Any, ...]:
    """Deterministically select complete source-task-unseen target episodes."""

    if source_candidate_id not in EXPECTED_CANDIDATE_IDS:
        raise StrictTaskCrossRolloutError("source candidate ID is not predeclared")
    if isinstance(episode_budget, bool) or not isinstance(episode_budget, int) or episode_budget < 1:
        raise StrictTaskCrossRolloutError("strict target episode budget must be a positive integer")
    pool = tuple(task_disjoint_episode_pool(episodes, source_split))
    if len(pool) < episode_budget:
        raise StrictTaskCrossRolloutError("strict target pool cannot satisfy the fixed complete-episode budget")
    selected = tuple(sorted(pool, key=lambda item: _stable_episode_key(source_candidate_id, item.episode_index))[:episode_budget])
    selected_episode_ids = {int(item.episode_index) for item in selected}
    selected_task_ids = {int(item.task_index) for item in selected if item.task_index is not None}
    source_selected = _selected_episode_set(source_split)
    source_train_tasks = _task_set(source_split, TRAIN_SPLIT)
    if len(selected_episode_ids) != episode_budget:
        raise StrictTaskCrossRolloutError("strict target selection contains duplicate episodes")
    if source_selected & selected_episode_ids:
        raise StrictTaskCrossRolloutError("strict target episodes overlap source-selected episodes")
    if source_train_tasks & selected_task_ids:
        raise StrictTaskCrossRolloutError("strict target tasks overlap source-train tasks")
    if any(item.task_index is None or not item.task for item in selected):
        raise StrictTaskCrossRolloutError("strict target selection contains unmapped task metadata")
    return selected


def _load_feasibility_receipt(path: Path = FEASIBILITY_RECEIPT_PATH) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise StrictTaskCrossRolloutError("strict feasibility receipt is missing")
    if sha256_file(resolved) != FEASIBILITY_RECEIPT_SHA256:
        raise StrictTaskCrossRolloutError("strict feasibility receipt SHA-256 drifted")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StrictTaskCrossRolloutError("strict feasibility receipt is invalid JSON") from error
    if not isinstance(payload, dict):
        raise StrictTaskCrossRolloutError("strict feasibility receipt root must be an object")
    if tuple(payload.get("candidate_ids", ())) != EXPECTED_CANDIDATE_IDS:
        raise StrictTaskCrossRolloutError("strict feasibility receipt candidate IDs disagree")
    if payload.get("no_training") is not True or payload.get("no_candidate_creation") is not True or payload.get("no_checkpoint_mutation") is not True or payload.get("promotion_performed") is not False:
        raise StrictTaskCrossRolloutError("strict feasibility receipt violates no-mutation boundary")
    return payload


def _baseline_predictors(train_transitions: Sequence[Any]) -> dict[str, Any]:
    action = ActionOnlyMeanDeltaBaseline.fit(train_transitions)
    linear = LinearStateActionDeltaBaseline.fit(train_transitions)
    nearest = NearestTrainStateActionBaseline.fit(train_transitions)
    return {
        "copy_state": copy_state_predictor,
        "action_only_mean_delta": action_only_mean_delta_predictor(action),
        "linear_state_action_delta": linear_state_action_delta_predictor(linear),
        "nearest_train_state_action": nearest_train_state_action_predictor(nearest),
    }


def _row_for_horizon(
    *,
    source_candidate_id: str,
    source_frozen: Mapping[str, Any],
    target_transitions: Sequence[Any],
    target_episode_ids: Sequence[int],
    target_task_ids: Sequence[int],
    target_pool_sha256: str,
    horizon: int,
) -> dict[str, Any]:
    """Score one strict source-task-unseen deterministic rollout horizon."""

    cases = build_rollout_cases(
        target_transitions,
        split="held_out_task",
        horizon=horizon,
        max_cases=DEFAULT_MAX_CASES_PER_HORIZON,
        case_selection_seed=DEFAULT_CASE_SELECTION_SEED,
    )
    actual_case_episode_ids = {case.episode_index for case in cases}
    if len(actual_case_episode_ids) < DEFAULT_MIN_DISTINCT_EPISODES:
        raise StrictTaskCrossRolloutError("strict selected rollout cases do not meet the minimum episode-cluster count")
    source_train_tasks = _task_set(source_frozen["split"], TRAIN_SPLIT)
    actual_case_task_ids = {case.task_index for case in cases}
    source_selected = _selected_episode_set(source_frozen["split"])
    if source_train_tasks & actual_case_task_ids:
        raise StrictTaskCrossRolloutError("selected rollout cases overlap source-train task IDs")
    if source_selected & actual_case_episode_ids:
        raise StrictTaskCrossRolloutError("selected rollout cases overlap source-selected episode IDs")
    predictors = _baseline_predictors(source_frozen["partitioned_transitions"][TRAIN_SPLIT])
    candidate_predictions = rollout_predictions(cases, source_frozen["model_predictor"])
    candidate_metrics = score_rollout_predictions(cases, candidate_predictions).to_dict()
    baseline_data: dict[str, dict[str, Any]] = {}
    baseline_predictions: dict[str, Any] = {}
    for label, predictor in predictors.items():
        predictions = rollout_predictions(cases, predictor)
        baseline_predictions[label] = predictions
        baseline_data[label] = score_rollout_predictions(cases, predictions).to_dict()
    strongest_label, strongest_metrics = min(
        baseline_data.items(), key=lambda item: (float(item[1]["aggregate_rmse"]), item[0])
    )
    if candidate_metrics["coverage"] != 1.0 or candidate_metrics["finite_prediction_rate"] != 1.0:
        raise StrictTaskCrossRolloutError("candidate lacks exact finite strict target coverage")
    if any(metrics["coverage"] != 1.0 or metrics["finite_prediction_rate"] != 1.0 for metrics in baseline_data.values()):
        raise StrictTaskCrossRolloutError("baseline lacks exact finite strict target coverage")
    paired_errors = paired_rollout_case_errors(cases, candidate_predictions, baseline_predictions[strongest_label])
    bootstrap = episode_clustered_paired_bootstrap(
        paired_errors,
        resamples=DEFAULT_BOOTSTRAP_RESAMPLES,
        seed=DEFAULT_BOOTSTRAP_SEED,
        minimum_distinct_episodes=DEFAULT_MIN_DISTINCT_EPISODES,
    )
    return {
        "source_candidate_id": source_candidate_id,
        "target_definition": "complete episodes absent from source selected episodes and with zero source-train task identity overlap",
        "horizon": horizon,
        "strict_target_pool_sha256": target_pool_sha256,
        "strict_target_selected_episode_count": len(target_episode_ids),
        "strict_target_selected_task_count": len(target_task_ids),
        "strict_target_selected_episode_indices": list(target_episode_ids),
        "strict_target_selected_task_indices": list(target_task_ids),
        "source_selected_episode_overlap_count": len(source_selected & set(target_episode_ids)),
        "source_train_task_overlap_count": len(source_train_tasks & set(target_task_ids)),
        "selected_case_episode_count": len(actual_case_episode_ids),
        "selected_case_task_count": len(actual_case_task_ids),
        "selected_case_source_selected_episode_overlap_count": len(source_selected & actual_case_episode_ids),
        "selected_case_source_train_task_overlap_count": len(source_train_tasks & actual_case_task_ids),
        "candidate_metrics": candidate_metrics,
        "baseline_metrics": baseline_data,
        "strongest_baseline": strongest_label,
        "point_estimate_strict_improvement": candidate_metrics["aggregate_rmse"] < strongest_metrics["aggregate_rmse"],
        "paired_bootstrap": bootstrap.to_dict(),
        "raw_paired_case_errors": [error.to_dict() for error in paired_errors],
    }


def evaluate_strict_task_disjoint_cross_rollouts(
    candidate_ids: Sequence[str],
    *,
    output_dir: Path,
    device_name: str = "cpu",
) -> dict[str, Any]:
    """Evaluate fixed frozen sources on strictly source-train-task-unseen targets."""

    identifiers = tuple(candidate_ids)
    if identifiers != EXPECTED_CANDIDATE_IDS:
        raise StrictTaskCrossRolloutError(
            "strict task evaluator requires exactly ordered candidates: " + ", ".join(EXPECTED_CANDIDATE_IDS)
        )
    destination = output_dir.expanduser().resolve()
    allowed_root = (ROOT / "evaluation" / "bridgedata_strict_task_cross_rollouts").resolve()
    try:
        destination.relative_to(allowed_root)
    except ValueError as error:
        raise StrictTaskCrossRolloutError("strict task output must remain under its ignored local evaluation root") from error
    if destination.exists():
        raise StrictTaskCrossRolloutError("strict task output destination already exists")
    feasibility = _load_feasibility_receipt()
    device = resolve_device(device_name)
    frozen = {candidate_id: load_frozen_rollout_candidate(candidate_id, device=device) for candidate_id in identifiers}
    intake = load_bridgedata_intake(INTAKE_MANIFEST_PATH)
    source_reports: dict[str, Any] = {}
    for source_id in identifiers:
        source = frozen[source_id]
        target_episodes = select_strict_target_episodes(source_id, source["split"], intake.episodes)
        target_ids = tuple(sorted(item.episode_index for item in target_episodes))
        target_task_ids = tuple(sorted({int(item.task_index) for item in target_episodes if item.task_index is not None}))
        extracted = derive_bridgedata_transitions(
            intake,
            BridgeDataTransitionConfig(selected_episode_indices=frozenset(target_ids)),
        )
        if extracted.receipt.capped:
            raise StrictTaskCrossRolloutError("strict target transition extraction unexpectedly capped")
        target_transitions = tuple(extracted.transitions)
        if not target_transitions:
            raise StrictTaskCrossRolloutError("strict target selection produced no transitions")
        pool = tuple(task_disjoint_episode_pool(intake.episodes, source["split"]))
        pool_sha256 = _canonical_target_pool_sha256(pool)
        rows = [
            _row_for_horizon(
                source_candidate_id=source_id,
                source_frozen=source,
                target_transitions=target_transitions,
                target_episode_ids=target_ids,
                target_task_ids=target_task_ids,
                target_pool_sha256=pool_sha256,
                horizon=horizon,
            )
            for horizon in ACCEPTANCE_HORIZONS
        ]
        source_reports[source_id] = {
            "strict_target_transition_receipt": extracted.receipt.to_dict(),
            "strict_target_transition_receipt_sha256": extracted.receipt.sha256(),
            "rows": rows,
            "point_estimate_passed_all_horizons": all(row["point_estimate_strict_improvement"] for row in rows),
            "bootstrap_passed_all_horizons": all(row["paired_bootstrap"]["interpretation"] == "pass" for row in rows),
        }
    payload = {
        "strict_task_cross_rollout_version": STRICT_TASK_CROSS_ROLLOUT_VERSION,
        "candidate_ids": list(identifiers),
        "device": str(device),
        "feasibility_receipt": {
            "path": str(FEASIBILITY_RECEIPT_PATH.resolve()),
            "sha256": FEASIBILITY_RECEIPT_SHA256,
            "payload_sha256": feasibility.get("payload_sha256"),
        },
        "intake_manifest": {"path": str(INTAKE_MANIFEST_PATH.resolve()), "sha256": intake.manifest_sha256},
        "acceptance_horizons": list(ACCEPTANCE_HORIZONS),
        "case_selection_seed": DEFAULT_CASE_SELECTION_SEED,
        "strict_target_selection_seed": STRICT_TARGET_SELECTION_SEED,
        "strict_target_episode_budget": STRICT_TARGET_EPISODE_BUDGET,
        "max_cases_per_horizon": DEFAULT_MAX_CASES_PER_HORIZON,
        "bootstrap": {
            "resamples": DEFAULT_BOOTSTRAP_RESAMPLES,
            "seed": DEFAULT_BOOTSTRAP_SEED,
            "minimum_distinct_episodes": DEFAULT_MIN_DISTINCT_EPISODES,
            "resampling_unit": "episode",
            "response": "candidate minus strongest source-train baseline case-level mean squared state error",
        },
        "source_reports": source_reports,
        "no_training": True,
        "no_candidate_creation": True,
        "no_checkpoint_mutation": True,
        "promotion_performed": False,
        "notes": [
            "This evaluation is strict relative to the source candidate: target selected task IDs have zero source-train task overlap and target episodes have zero source-selected episode overlap.",
            "The target allocation is fixed by a source-ID-specific stable hash order and a 128 complete-episode budget, then bounded deterministic cases are selected without performance tuning.",
            "The frozen source model receives an observed initial state and recorded actions only; all later rollout state inputs are recursively predicted.",
            "This is observed state-transition prediction evidence only, not policy, control, safety, causality, visual modeling, renderer, native Chronos, product readiness, or promotion evidence.",
        ],
    }
    payload["payload_sha256"] = _sha256_json(payload)
    _write_new_json(destination / "strict_task_cross_rollout.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate frozen BridgeData candidates on strict source-train-task-disjoint rollouts.")
    parser.add_argument("--candidate-id", action="append", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--device", default="cpu", choices=("cpu", "auto", "cuda"))
    arguments = parser.parse_args()
    result = evaluate_strict_task_disjoint_cross_rollouts(
        arguments.candidate_id,
        output_dir=Path(arguments.output_dir),
        device_name=arguments.device,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

