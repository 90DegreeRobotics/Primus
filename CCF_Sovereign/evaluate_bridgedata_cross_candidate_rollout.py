"""Evaluate frozen BridgeData candidates on each other's protected rollout splits.

This command is evaluation-only. It loads the two terminal rejected candidates
read-only, fits baselines from the source candidate's train partition, and
scores open-loop rollouts on the other candidate's protected episode sets.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
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
from real_data.bridgedata_evaluation import (  # noqa: E402
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    ActionOnlyMeanDeltaBaseline,
    LinearStateActionDeltaBaseline,
    NearestTrainStateActionBaseline,
)
from real_data.bridgedata_rollouts import (  # noqa: E402
    DEFAULT_CASE_SELECTION_SEED,
    DEFAULT_HORIZONS,
    DEFAULT_MAX_CASES_PER_HORIZON,
    action_only_mean_delta_predictor,
    copy_state_predictor,
    evaluate_rollout_predictor,
    linear_state_action_delta_predictor,
    nearest_train_state_action_predictor,
    predeclared_rollout_acceptance,
)
from train_bridgedata_real_transition import resolve_device  # noqa: E402


CROSS_ROLLOUT_EVALUATION_VERSION = 1
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "evaluation"
    / "bridgedata_cross_rollouts"
    / "cross-rollout-20260828-001"
)
PROTECTED_SPLITS = (HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT)


def _episode_set(split: Any, name: str) -> set[int]:
    return set(int(item) for item in split.episode_indices(name))


def _task_set(split: Any, name: str) -> set[int]:
    return set(int(item) for item in split.task_indices(name))


def _selected_episode_set(split: Any) -> set[int]:
    return set().union(*(_episode_set(split, name) for name in (TRAIN_SPLIT,) + PROTECTED_SPLITS))


def cross_partitioned_transitions(
    source_frozen: Mapping[str, Any],
    target_frozen: Mapping[str, Any],
) -> dict[str, tuple[Any, ...]]:
    """Combine source train transitions with target protected transitions."""

    source_split = source_frozen["split"]
    target_split = target_frozen["split"]
    source_selected = _selected_episode_set(source_split)
    source_train = _episode_set(source_split, TRAIN_SPLIT)
    for protected_split in PROTECTED_SPLITS:
        target_episodes = _episode_set(target_split, protected_split)
        if source_selected & target_episodes:
            raise FrozenRolloutEvidenceError(
                f"source selected episodes overlap target protected split: {protected_split}"
            )
        if source_train & target_episodes:
            raise FrozenRolloutEvidenceError(
                f"source train episodes overlap target protected split: {protected_split}"
            )
    return {
        TRAIN_SPLIT: tuple(source_frozen["partitioned_transitions"][TRAIN_SPLIT]),
        HELD_OUT_EPISODE_SPLIT: tuple(target_frozen["partitioned_transitions"][HELD_OUT_EPISODE_SPLIT]),
        HELD_OUT_TASK_SPLIT: tuple(target_frozen["partitioned_transitions"][HELD_OUT_TASK_SPLIT]),
    }


def cross_semantics_report(
    source_frozen: Mapping[str, Any],
    target_frozen: Mapping[str, Any],
) -> dict[str, Any]:
    """Report episode independence and task-overlap limits for cross scoring."""

    source_split = source_frozen["split"]
    target_split = target_frozen["split"]
    source_train_tasks = _task_set(source_split, TRAIN_SPLIT)
    source_selected = _selected_episode_set(source_split)
    report: dict[str, Any] = {}
    for protected_split in PROTECTED_SPLITS:
        target_episodes = _episode_set(target_split, protected_split)
        target_tasks = _task_set(target_split, protected_split)
        train_task_overlap = sorted(source_train_tasks & target_tasks)
        report[protected_split] = {
            "target_candidate_partition": protected_split,
            "target_episode_count": len(target_episodes),
            "target_task_count": len(target_tasks),
            "source_selected_episode_overlap_count": len(source_selected & target_episodes),
            "source_train_episode_overlap_count": len(_episode_set(source_split, TRAIN_SPLIT) & target_episodes),
            "source_train_task_overlap_count": len(train_task_overlap),
            "source_train_task_overlap_indices": train_task_overlap,
            "strict_unseen_task_relative_to_source_train": (
                protected_split == HELD_OUT_TASK_SPLIT and not train_task_overlap
            ),
            "note": (
                "Partition names belong to the target candidate's split. "
                "A target held-out-task split is strict for the source model only when "
                "source_train_task_overlap_count is zero."
            ),
        }
    return report


def evaluate_cross_pair(
    source_candidate_id: str,
    target_candidate_id: str,
    source_frozen: Mapping[str, Any],
    target_frozen: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate one source model against one target candidate's protected splits."""

    if source_candidate_id == target_candidate_id:
        raise FrozenRolloutEvidenceError("cross-candidate rollout requires distinct candidates")
    partitioned = cross_partitioned_transitions(source_frozen, target_frozen)
    action_baseline = ActionOnlyMeanDeltaBaseline.fit(partitioned[TRAIN_SPLIT])
    linear_baseline = LinearStateActionDeltaBaseline.fit(partitioned[TRAIN_SPLIT])
    nearest_baseline = NearestTrainStateActionBaseline.fit(partitioned[TRAIN_SPLIT])
    candidate_report = evaluate_rollout_predictor(
        partitioned,
        prediction_label=f"{source_candidate_id}_frozen_residual_mlp_on_{target_candidate_id}",
        predict_next_state=source_frozen["model_predictor"],
    )
    baseline_reports = {
        "copy_state": evaluate_rollout_predictor(
            partitioned,
            prediction_label=f"{source_candidate_id}_copy_state_on_{target_candidate_id}",
            predict_next_state=copy_state_predictor,
        ),
        "action_only_mean_delta": evaluate_rollout_predictor(
            partitioned,
            prediction_label=f"{source_candidate_id}_action_only_mean_delta_on_{target_candidate_id}",
            predict_next_state=action_only_mean_delta_predictor(action_baseline),
        ),
        "linear_state_action_delta": evaluate_rollout_predictor(
            partitioned,
            prediction_label=f"{source_candidate_id}_linear_state_action_delta_on_{target_candidate_id}",
            predict_next_state=linear_state_action_delta_predictor(linear_baseline),
        ),
        "nearest_train_state_action": evaluate_rollout_predictor(
            partitioned,
            prediction_label=f"{source_candidate_id}_nearest_train_state_action_on_{target_candidate_id}",
            predict_next_state=nearest_train_state_action_predictor(nearest_baseline),
        ),
    }
    return {
        "source_candidate_id": source_candidate_id,
        "target_candidate_id": target_candidate_id,
        "semantics": cross_semantics_report(source_frozen, target_frozen),
        "candidate_report": candidate_report.to_dict(),
        "baseline_reports": {label: report.to_dict() for label, report in baseline_reports.items()},
        "acceptance": predeclared_rollout_acceptance(candidate_report, baseline_reports),
    }


def evaluate_cross_candidates(
    candidate_ids: Sequence[str],
    *,
    output_dir: Path,
    device_name: str = "cpu",
) -> dict[str, Any]:
    """Run the fixed cross-candidate robustness audit and atomically write evidence."""

    identifiers = tuple(candidate_ids)
    if identifiers != EXPECTED_CANDIDATE_IDS:
        raise FrozenRolloutEvidenceError(
            "cross rollout requires exactly the ordered predeclared candidates: "
            + ", ".join(EXPECTED_CANDIDATE_IDS)
        )
    destination = output_dir.expanduser().resolve()
    allowed_root = (ROOT / "evaluation" / "bridgedata_cross_rollouts").resolve()
    try:
        destination.relative_to(allowed_root)
    except ValueError as error:
        raise FrozenRolloutEvidenceError("cross rollout output must remain under the ignored local evaluation directory") from error
    if destination.exists():
        raise FrozenRolloutEvidenceError("cross rollout output destination already exists")
    device = resolve_device(device_name)
    frozen = {
        candidate_id: load_frozen_rollout_candidate(candidate_id, device=device)
        for candidate_id in identifiers
    }
    cross_pairs: dict[str, Any] = {}
    for source_candidate_id, target_candidate_id in (
        (identifiers[0], identifiers[1]),
        (identifiers[1], identifiers[0]),
    ):
        key = f"{source_candidate_id}_on_{target_candidate_id}"
        cross_pairs[key] = evaluate_cross_pair(
            source_candidate_id,
            target_candidate_id,
            frozen[source_candidate_id],
            frozen[target_candidate_id],
        )
    payload = {
        "cross_rollout_evaluation_version": CROSS_ROLLOUT_EVALUATION_VERSION,
        "candidate_ids": list(identifiers),
        "device": str(device),
        "horizons": list(DEFAULT_HORIZONS),
        "case_selection_seed": DEFAULT_CASE_SELECTION_SEED,
        "max_cases_per_horizon": DEFAULT_MAX_CASES_PER_HORIZON,
        "cross_pairs": cross_pairs,
        "no_training": True,
        "no_candidate_creation": True,
        "no_checkpoint_mutation": True,
        "promotion_performed": False,
        "notes": [
            "Read-only cross-candidate open-loop evaluation over frozen terminal rejected candidates.",
            "The source candidate supplies the frozen model and train-only baseline bank.",
            "The target candidate supplies protected rollout episode sets.",
            "Target partition names are not automatically strict relative to the source model; task overlap is reported explicitly.",
            "This is robustness evidence only, not policy, control, safety, renderer, native Chronos, or promotion evidence.",
        ],
    }
    payload["payload_sha256"] = _sha256_json(payload)
    _write_new_json(destination / "cross_rollout_stability.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate frozen BridgeData candidates on each other's protected rollout splits.")
    parser.add_argument("--candidate-id", action="append", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--device", default="cpu", choices=("cpu", "auto", "cuda"))
    arguments = parser.parse_args()
    result = evaluate_cross_candidates(
        arguments.candidate_id,
        output_dir=Path(arguments.output_dir),
        device_name=arguments.device,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
