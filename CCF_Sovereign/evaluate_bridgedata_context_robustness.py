"""Read-only temporal and action-context robustness audit for frozen BridgeData predictors.

The evaluator reuses source-specific strict task-ID-disjoint target episode
selection. It partitions only observed, episode-contained rollout cases by
relative episode position and by recorded action energy against a threshold fit
solely on that source candidate's training transitions. It neither trains nor
creates, mutates, promotes, or controls any candidate.
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
    _sha256_json,
    _write_new_json,
    load_frozen_rollout_candidate,
)
from evaluate_bridgedata_strict_task_cross_rollout import (  # noqa: E402
    INTAKE_MANIFEST_PATH,
    _baseline_predictors,
    _canonical_target_pool_sha256,
    _load_feasibility_receipt,
    _selected_episode_set,
    _task_set,
    select_strict_target_episodes,
)
from evaluate_bridgedata_task_disjoint_feasibility import task_disjoint_episode_pool  # noqa: E402
from real_data.bridgedata_evaluation import TRAIN_SPLIT  # noqa: E402
from real_data.bridgedata_rollout_uncertainty import (  # noqa: E402
    DEFAULT_BOOTSTRAP_RESAMPLES,
    DEFAULT_BOOTSTRAP_SEED,
    DEFAULT_MIN_DISTINCT_EPISODES,
    episode_clustered_paired_bootstrap,
    paired_rollout_case_errors,
)
from real_data.bridgedata_rollouts import (  # noqa: E402
    DEFAULT_CASE_SELECTION_SEED,
    BridgeDataRolloutCase,
    build_rollout_cases,
    rollout_predictions,
    score_rollout_predictions,
)
from real_data.bridgedata_transitions import (  # noqa: E402
    BridgeDataTransitionConfig,
    derive_bridgedata_transitions,
    load_bridgedata_intake,
)
from train_bridgedata_real_transition import resolve_device  # noqa: E402


CONTEXT_ROBUSTNESS_VERSION = 1
ACCEPTANCE_HORIZONS = (1, 2, 5)
CONTEXTS = ("early_low_action_energy", "early_high_action_energy", "late_low_action_energy", "late_high_action_energy")
STRICT_TARGET_EPISODE_BUDGET = 128
MAX_CASES_PER_CONTEXT = 128
CONTEXT_CASE_SELECTION_SEED = 20_260_828
ALL_CASE_CAP = 1_000_000
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "evaluation"
    / "bridgedata_context_robustness"
    / "context-robustness-20260828-001"
)


class ContextRobustnessError(ValueError):
    """Raised when an evidence boundary or context partition is ineligible."""


def _action_norm(action: Sequence[float]) -> float:
    values = tuple(float(value) for value in action)
    if len(values) != 7 or not all(math.isfinite(value) for value in values):
        raise ContextRobustnessError("action energy requires a finite 7D action")
    return math.sqrt(sum(value * value for value in values))


def source_train_action_energy_median(train_transitions: Sequence[Any]) -> float:
    """Fit the only action-context threshold from source-train transitions."""

    values = sorted(_action_norm(item.action_t) for item in train_transitions)
    if not values:
        raise ContextRobustnessError("source-train action energy threshold requires transitions")
    middle = len(values) // 2
    threshold = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2.0
    if not math.isfinite(threshold) or threshold < 0.0:
        raise ContextRobustnessError("source-train action energy threshold is invalid")
    return threshold


def _relative_episode_position(case: BridgeDataRolloutCase, episodes: Mapping[int, Any]) -> float:
    episode = episodes.get(int(case.episode_index))
    if episode is None:
        raise ContextRobustnessError("rollout case episode is absent from declared metadata")
    length = int(episode.length)
    if length <= case.horizon:
        raise ContextRobustnessError("declared episode is too short for its rollout case")
    # BridgeData rollout source_frame_index is episode-local; dataset_from_index is a global Parquet offset.
    offset = int(case.source_frame_index)
    maximum = length - case.horizon - 1
    if maximum < 0 or offset < 0 or offset > maximum:
        raise ContextRobustnessError("rollout case frame is outside its declared episode range")
    return 0.0 if maximum == 0 else offset / maximum


def case_context(case: BridgeDataRolloutCase, episodes: Mapping[int, Any], *, source_train_action_energy_median_value: float) -> str:
    """Return a deterministic temporal/action context without using targets."""

    if not math.isfinite(source_train_action_energy_median_value) or source_train_action_energy_median_value < 0.0:
        raise ContextRobustnessError("source-train median threshold is invalid")
    relative_position = _relative_episode_position(case, episodes)
    average_action_energy = sum(_action_norm(action) for action in case.actions) / len(case.actions)
    temporal = "early" if relative_position < 0.5 else "late"
    energy = "low_action_energy" if average_action_energy < source_train_action_energy_median_value else "high_action_energy"
    return f"{temporal}_{energy}"


def _stable_case_key(source_candidate_id: str, horizon: int, context: str, case_id: str) -> tuple[str, str]:
    digest = hashlib.sha256(
        f"{CONTEXT_CASE_SELECTION_SEED}:context:{source_candidate_id}:{horizon}:{context}:{case_id}".encode("utf-8")
    ).hexdigest()
    return digest, case_id


def select_context_cases(
    cases: Sequence[BridgeDataRolloutCase],
    *,
    source_candidate_id: str,
    horizon: int,
    context: str,
    episodes: Mapping[int, Any],
    source_train_action_energy_median_value: float,
    max_cases: int = MAX_CASES_PER_CONTEXT,
) -> tuple[BridgeDataRolloutCase, ...]:
    """Deterministically select bounded cases from one declared context cell."""

    if context not in CONTEXTS:
        raise ContextRobustnessError("context is not predeclared")
    if isinstance(max_cases, bool) or not isinstance(max_cases, int) or max_cases < 1:
        raise ContextRobustnessError("context case budget must be a positive integer")
    classified = tuple(
        case for case in cases
        if case_context(case, episodes, source_train_action_energy_median_value=source_train_action_energy_median_value) == context
    )
    if len(classified) < max_cases:
        raise ContextRobustnessError("context lacks the fixed bounded case capacity")
    selected = tuple(sorted(classified, key=lambda case: _stable_case_key(source_candidate_id, horizon, context, case.case_id))[:max_cases])
    if len({case.case_id for case in selected}) != max_cases:
        raise ContextRobustnessError("context selection has duplicate case IDs")
    if len({case.episode_index for case in selected}) < DEFAULT_MIN_DISTINCT_EPISODES:
        raise ContextRobustnessError("context selection lacks minimum distinct episode clusters")
    return selected


def _verify_strict_case_overlap(cases: Sequence[BridgeDataRolloutCase], source_split: Any) -> tuple[int, int]:
    source_selected = _selected_episode_set(source_split)
    source_train_tasks = _task_set(source_split, TRAIN_SPLIT)
    target_episodes = {case.episode_index for case in cases}
    target_tasks = {case.task_index for case in cases}
    episode_overlap = len(source_selected & target_episodes)
    task_overlap = len(source_train_tasks & target_tasks)
    if episode_overlap or task_overlap:
        raise ContextRobustnessError("context cases violate strict source episode or task separation")
    return episode_overlap, task_overlap


def _score_context(
    *,
    source_candidate_id: str,
    source: Mapping[str, Any],
    episodes: Mapping[int, Any],
    cases: Sequence[BridgeDataRolloutCase],
    context: str,
    horizon: int,
    source_train_action_energy_median_value: float,
) -> dict[str, Any]:
    episode_overlap, task_overlap = _verify_strict_case_overlap(cases, source["split"])
    predictors = _baseline_predictors(source["partitioned_transitions"][TRAIN_SPLIT])
    candidate_predictions = rollout_predictions(cases, source["model_predictor"])
    candidate_metrics = score_rollout_predictions(cases, candidate_predictions).to_dict()
    baseline_metrics: dict[str, dict[str, Any]] = {}
    baseline_predictions: dict[str, Any] = {}
    for label, predictor in predictors.items():
        predictions = rollout_predictions(cases, predictor)
        baseline_predictions[label] = predictions
        baseline_metrics[label] = score_rollout_predictions(cases, predictions).to_dict()
    strongest_label, strongest = min(
        baseline_metrics.items(), key=lambda item: (float(item[1]["aggregate_rmse"]), item[0])
    )
    for label, metrics in {"candidate": candidate_metrics, **baseline_metrics}.items():
        if metrics["coverage"] != 1.0 or metrics["finite_prediction_rate"] != 1.0:
            raise ContextRobustnessError(f"{label} lacks exact finite context coverage")
    errors = paired_rollout_case_errors(cases, candidate_predictions, baseline_predictions[strongest_label])
    bootstrap = episode_clustered_paired_bootstrap(
        errors,
        resamples=DEFAULT_BOOTSTRAP_RESAMPLES,
        seed=DEFAULT_BOOTSTRAP_SEED,
        minimum_distinct_episodes=DEFAULT_MIN_DISTINCT_EPISODES,
    )
    return {
        "source_candidate_id": source_candidate_id,
        "horizon": horizon,
        "context": context,
        "source_train_action_energy_median": source_train_action_energy_median_value,
        "selected_case_count": len(cases),
        "selected_case_episode_count": len({case.episode_index for case in cases}),
        "selected_case_task_count": len({case.task_index for case in cases}),
        "source_selected_episode_overlap_count": episode_overlap,
        "source_train_task_overlap_count": task_overlap,
        "candidate_metrics": candidate_metrics,
        "baseline_metrics": baseline_metrics,
        "strongest_baseline": strongest_label,
        "point_estimate_strict_improvement": candidate_metrics["aggregate_rmse"] < strongest["aggregate_rmse"],
        "paired_bootstrap": bootstrap.to_dict(),
        "raw_paired_case_errors": [item.to_dict() for item in errors],
    }


def evaluate_context_robustness(
    candidate_ids: Sequence[str],
    *,
    output_dir: Path,
    device_name: str = "cpu",
) -> dict[str, Any]:
    """Run one bounded read-only strict-target temporal/action-context audit."""

    identifiers = tuple(candidate_ids)
    if identifiers != EXPECTED_CANDIDATE_IDS:
        raise ContextRobustnessError("context audit requires exactly ordered predeclared candidate IDs")
    destination = output_dir.expanduser().resolve()
    allowed_root = (ROOT / "evaluation" / "bridgedata_context_robustness").resolve()
    try:
        destination.relative_to(allowed_root)
    except ValueError as error:
        raise ContextRobustnessError("context audit output must remain under the ignored local evaluation root") from error
    if destination.exists():
        raise ContextRobustnessError("context audit output destination already exists")
    feasibility = _load_feasibility_receipt()
    device = resolve_device(device_name)
    frozen = {candidate_id: load_frozen_rollout_candidate(candidate_id, device=device) for candidate_id in identifiers}
    intake = load_bridgedata_intake(INTAKE_MANIFEST_PATH)
    reports: dict[str, Any] = {}
    for source_id in identifiers:
        source = frozen[source_id]
        strict_episodes = select_strict_target_episodes(source_id, source["split"], intake.episodes, episode_budget=STRICT_TARGET_EPISODE_BUDGET)
        episode_ids = tuple(sorted(item.episode_index for item in strict_episodes))
        task_ids = tuple(sorted({int(item.task_index) for item in strict_episodes if item.task_index is not None}))
        extracted = derive_bridgedata_transitions(
            intake,
            BridgeDataTransitionConfig(selected_episode_indices=frozenset(episode_ids)),
        )
        if extracted.receipt.capped:
            raise ContextRobustnessError("strict target transition extraction unexpectedly capped")
        threshold = source_train_action_energy_median(source["partitioned_transitions"][TRAIN_SPLIT])
        pool_sha256 = _canonical_target_pool_sha256(task_disjoint_episode_pool(intake.episodes, source["split"]))
        rows: list[dict[str, Any]] = []
        for horizon in ACCEPTANCE_HORIZONS:
            all_cases = build_rollout_cases(
                extracted.transitions,
                split="held_out_task",
                horizon=horizon,
                max_cases=ALL_CASE_CAP,
                case_selection_seed=DEFAULT_CASE_SELECTION_SEED,
            )
            for context in CONTEXTS:
                cases = select_context_cases(
                    all_cases,
                    source_candidate_id=source_id,
                    horizon=horizon,
                    context=context,
                    episodes=intake.episodes,
                    source_train_action_energy_median_value=threshold,
                )
                rows.append(_score_context(
                    source_candidate_id=source_id,
                    source=source,
                    episodes=intake.episodes,
                    cases=cases,
                    context=context,
                    horizon=horizon,
                    source_train_action_energy_median_value=threshold,
                ))
        reports[source_id] = {
            "strict_target_episode_indices": list(episode_ids),
            "strict_target_task_indices": list(task_ids),
            "strict_target_pool_sha256": pool_sha256,
            "strict_target_transition_receipt": extracted.receipt.to_dict(),
            "strict_target_transition_receipt_sha256": extracted.receipt.sha256(),
            "rows": rows,
            "point_estimate_passed_all_cells": all(row["point_estimate_strict_improvement"] for row in rows),
            "bootstrap_passed_all_cells": all(row["paired_bootstrap"]["interpretation"] == "pass" for row in rows),
        }
    payload = {
        "context_robustness_version": CONTEXT_ROBUSTNESS_VERSION,
        "candidate_ids": list(identifiers),
        "device": str(device),
        "feasibility_receipt": {"payload_sha256": feasibility.get("payload_sha256")},
        "intake_manifest_sha256": intake.manifest_sha256,
        "acceptance_horizons": list(ACCEPTANCE_HORIZONS),
        "contexts": list(CONTEXTS),
        "context_threshold_definition": "source-train median one-step action L2 norm; each rollout context uses mean recorded action L2 norm across its actions",
        "strict_target_episode_budget": STRICT_TARGET_EPISODE_BUDGET,
        "max_cases_per_context": MAX_CASES_PER_CONTEXT,
        "case_selection_seed": CONTEXT_CASE_SELECTION_SEED,
        "bootstrap": {"resamples": DEFAULT_BOOTSTRAP_RESAMPLES, "seed": DEFAULT_BOOTSTRAP_SEED, "minimum_distinct_episodes": DEFAULT_MIN_DISTINCT_EPISODES, "resampling_unit": "episode"},
        "source_reports": reports,
        "no_training": True,
        "no_candidate_creation": True,
        "no_checkpoint_mutation": True,
        "promotion_performed": False,
        "notes": [
            "Target task separation is strict only relative to each source candidate's source-train task IDs, with zero source-selected episode overlap.",
            "Temporal/action context labels use no target-state value: declared episode position and recorded actions only, with the action-energy threshold fit only from source-train transitions.",
            "A pass/indistinguishable/fail label is reported per source, horizon, and context cell. This audit has no pooled all-context score and no promotion path.",
            "This is bounded observational transition prediction evidence only, not policy, control, safety, causality, visual modeling, renderer, Chronos, product readiness, or promotion evidence.",
        ],
    }
    payload["payload_sha256"] = _sha256_json(payload)
    _write_new_json(destination / "context_robustness.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit frozen BridgeData predictions across strict temporal/action contexts.")
    parser.add_argument("--candidate-id", action="append", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--device", default="cpu", choices=("cpu", "auto", "cuda"))
    arguments = parser.parse_args()
    print(json.dumps(evaluate_context_robustness(arguments.candidate_id, output_dir=Path(arguments.output_dir), device_name=arguments.device), ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

