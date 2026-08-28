"""Measure whether strict task-disjoint BridgeData rollout evaluation is feasible.

This command is metadata/capacity-only. It verifies frozen rejected candidate
manifests and the frozen BridgeData intake, then counts source-train-task-
disjoint target episode capacity. It does not derive predictions, train,
evaluate a model, create a candidate, mutate a checkpoint, or authorize
promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from evaluate_bridgedata_rollout_stability import (  # noqa: E402
    EXPECTED_CANDIDATE_IDS,
    ROOT,
    _load_json_object,
    _sha256_json,
    _split_from_payload,
    _verify_file_evidence,
)
from real_data.bridgedata_evaluation import (  # noqa: E402
    HELD_OUT_EPISODE_SPLIT,
    HELD_OUT_TASK_SPLIT,
    TRAIN_SPLIT,
    BridgeDataSplit,
    validate_bridgedata_split,
)
from real_data.bridgedata_rollout_uncertainty import DEFAULT_MIN_DISTINCT_EPISODES
from real_data.bridgedata_rollouts import (
    DEFAULT_MAX_CASES_PER_HORIZON,
)
from real_data.bridgedata_transitions import (
    BridgeDataIntake,
    EpisodeTask,
    load_bridgedata_intake,
    sha256_file,
)


TASK_DISJOINT_FEASIBILITY_VERSION = 1
ACCEPTANCE_HORIZONS = (1, 2, 5)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "evaluation"
    / "bridgedata_task_disjoint_feasibility"
    / "task-disjoint-feasibility-20260828-001"
)
PROTECTED_SPLITS = (HELD_OUT_EPISODE_SPLIT, HELD_OUT_TASK_SPLIT)


class TaskDisjointFeasibilityError(ValueError):
    """Raised when feasibility inputs or output boundaries are invalid."""


def _write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists():
        raise TaskDisjointFeasibilityError("feasibility evidence destination already exists")
    path.parent.mkdir(parents=True, exist_ok=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
        handle.write("\n")
    os.replace(temporary, path)


def _stable_order_key(seed: int, prefix: str, value: int) -> tuple[str, int]:
    digest = hashlib.sha256(f"{seed}:{prefix}:{value}".encode("ascii")).hexdigest()
    return digest, value


def _episode_set(split: BridgeDataSplit, name: str) -> set[int]:
    return set(int(item) for item in split.episode_indices(name))


def _task_set(split: BridgeDataSplit, name: str) -> set[int]:
    return set(int(item) for item in split.task_indices(name))


def _selected_episode_set(split: BridgeDataSplit) -> set[int]:
    return set().union(*(_episode_set(split, name) for name in (TRAIN_SPLIT,) + PROTECTED_SPLITS))


def rollout_case_capacity(episode: EpisodeTask, horizon: int) -> int:
    """Return episode-contained rollout case capacity for one horizon."""

    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
        raise TaskDisjointFeasibilityError("horizon must be a positive integer")
    episode.validate()
    return max(0, episode.length - horizon)


def task_disjoint_episode_pool(
    episodes: Mapping[int, EpisodeTask],
    source_split: BridgeDataSplit,
) -> tuple[EpisodeTask, ...]:
    """Return mapped episodes outside source selection and source train tasks."""

    source_selected = _selected_episode_set(source_split)
    source_train_tasks = _task_set(source_split, TRAIN_SPLIT)
    pool = []
    for episode_index, episode in sorted(episodes.items()):
        if episode.episode_index != episode_index:
            raise TaskDisjointFeasibilityError("episode mapping key disagrees with EpisodeTask")
        episode.validate()
        if episode.task_index is None or not episode.task:
            continue
        if episode.episode_index in source_selected:
            continue
        if int(episode.task_index) in source_train_tasks:
            continue
        if rollout_case_capacity(episode, 1) < 1:
            continue
        pool.append(episode)
    return tuple(pool)


def horizon_capacity_summary(
    pool: Sequence[EpisodeTask],
    *,
    horizons: Sequence[int] = ACCEPTANCE_HORIZONS,
    required_cases: int = DEFAULT_MAX_CASES_PER_HORIZON,
    minimum_distinct_episodes: int = DEFAULT_MIN_DISTINCT_EPISODES,
) -> dict[str, Any]:
    """Count capacity by horizon without opening state/action rows."""

    if isinstance(required_cases, bool) or not isinstance(required_cases, int) or required_cases < 1:
        raise TaskDisjointFeasibilityError("required case count must be a positive integer")
    if isinstance(minimum_distinct_episodes, bool) or not isinstance(minimum_distinct_episodes, int) or minimum_distinct_episodes < 1:
        raise TaskDisjointFeasibilityError("minimum distinct episode count must be a positive integer")
    summaries: dict[str, Any] = {}
    for horizon in horizons:
        capacities = [
            rollout_case_capacity(episode, int(horizon))
            for episode in pool
        ]
        eligible_capacities = [value for value in capacities if value > 0]
        summaries[str(horizon)] = {
            "horizon": int(horizon),
            "eligible_episode_clusters": len(eligible_capacities),
            "rollout_case_capacity": sum(eligible_capacities),
            "required_cases": required_cases,
            "minimum_distinct_episode_clusters": minimum_distinct_episodes,
            "meets_case_requirement": sum(eligible_capacities) >= required_cases,
            "meets_cluster_requirement": len(eligible_capacities) >= minimum_distinct_episodes,
            "feasible": (
                sum(eligible_capacities) >= required_cases
                and len(eligible_capacities) >= minimum_distinct_episodes
            ),
        }
    return summaries


def source_feasibility_report(
    candidate_id: str,
    split: BridgeDataSplit,
    intake: BridgeDataIntake,
) -> dict[str, Any]:
    """Measure strict task-disjoint target capacity for one source candidate."""

    validate_bridgedata_split(split, intake.episodes)
    pool = task_disjoint_episode_pool(intake.episodes, split)
    source_train_tasks = _task_set(split, TRAIN_SPLIT)
    source_selected = _selected_episode_set(split)
    pool_task_indices = sorted({int(episode.task_index) for episode in pool if episode.task_index is not None})
    by_horizon = horizon_capacity_summary(pool)
    feasible = all(item["feasible"] for item in by_horizon.values())
    return {
        "source_candidate_id": candidate_id,
        "source_train_task_count": len(source_train_tasks),
        "source_selected_episode_count": len(source_selected),
        "strict_target_pool_episode_count": len(pool),
        "strict_target_pool_task_count": len(pool_task_indices),
        "strict_target_pool_task_overlap_with_source_train_count": len(set(pool_task_indices) & source_train_tasks),
        "strict_target_pool_selected_episode_overlap_count": len({episode.episode_index for episode in pool} & source_selected),
        "candidate_eligible_for_h1_h2_h5": feasible,
        "by_horizon": by_horizon,
        "task_sample": pool_task_indices[:25],
        "episode_sample": [episode.episode_index for episode in sorted(pool, key=lambda item: _stable_order_key(20_260_828, candidate_id, item.episode_index))[:25]],
        "notes": [
            "Target pool excludes all source-selected episodes and all source-train task IDs.",
            "Counts are metadata-derived from frozen episode lengths; no state/action predictions are computed.",
            "Feasible only means enough candidate target cases exist for a later separately planned evaluation.",
        ],
    }


def load_candidate_split_and_intake(candidate_id: str) -> dict[str, Any]:
    """Verify one frozen rejected candidate and return its split plus intake."""

    if candidate_id not in EXPECTED_CANDIDATE_IDS:
        raise TaskDisjointFeasibilityError("candidate ID is not a predeclared feasibility subject")
    candidate_dir = ROOT / "checkpoints" / "candidates" / candidate_id
    manifest_path = candidate_dir / "real_data.run.manifest.json"
    if not manifest_path.is_file():
        raise TaskDisjointFeasibilityError("candidate lifecycle manifest is missing")
    manifest = _load_json_object(manifest_path, "candidate lifecycle manifest")
    if manifest.get("candidate_id") != candidate_id:
        raise TaskDisjointFeasibilityError("candidate lifecycle manifest ID disagrees with requested candidate")
    if manifest.get("candidate_kind") != "bridgedata_observed_state_transition":
        raise TaskDisjointFeasibilityError("candidate kind is not BridgeData transition evidence")
    if manifest.get("status") != "rejected" or manifest.get("promotion", {}).get("performed") is not False:
        raise TaskDisjointFeasibilityError("feasibility audit requires terminal rejected no-promotion candidates")
    if manifest.get("parent_protection", {}).get("touched_by_training") is not False:
        raise TaskDisjointFeasibilityError("candidate lifecycle indicates protected parent mutation")
    for evidence_label in ("checkpoint",):
        _verify_file_evidence(manifest.get(evidence_label), f"candidate {evidence_label}")
    for evidence_label in ("metrics_report", "predictions"):
        _verify_file_evidence(manifest.get("evaluation", {}).get(evidence_label), f"candidate {evidence_label}")
    for evidence_label, evidence in manifest.get("parent_protection", {}).items():
        if evidence_label in ("live_parent", "frozen_parent"):
            _verify_file_evidence(evidence, f"candidate parent protection {evidence_label}")
    frozen_inputs = manifest.get("additional_frozen_inputs")
    if not isinstance(frozen_inputs, Mapping) or "intake_manifest" not in frozen_inputs:
        raise TaskDisjointFeasibilityError("candidate lacks frozen intake manifest evidence")
    intake_manifest_path = _verify_file_evidence(frozen_inputs["intake_manifest"], "candidate frozen input intake_manifest")
    for evidence_label in ("data_parquet", "episodes_parquet", "tasks_parquet"):
        if evidence_label not in frozen_inputs:
            raise TaskDisjointFeasibilityError(f"candidate lacks frozen input: {evidence_label}")
        _verify_file_evidence(frozen_inputs[evidence_label], f"candidate frozen input {evidence_label}")
    split_path = candidate_dir / "evidence" / "split.json"
    if not split_path.is_file():
        raise TaskDisjointFeasibilityError("candidate bounded split evidence is missing")
    split_payload = _load_json_object(split_path, "candidate split evidence")
    bounded_payload = split_payload.get("bounded_group_split")
    if not isinstance(bounded_payload, Mapping):
        raise TaskDisjointFeasibilityError("candidate split evidence lacks bounded group split")
    split = _split_from_payload(bounded_payload)
    config = manifest.get("config")
    if not isinstance(config, Mapping) or config.get("split_sha256") != split.sha256():
        raise TaskDisjointFeasibilityError("candidate split evidence does not match manifest-bound split hash")
    intake = load_bridgedata_intake(intake_manifest_path)
    validate_bridgedata_split(split, intake.episodes)
    return {
        "candidate_id": candidate_id,
        "manifest_sha256": sha256_file(manifest_path),
        "split_sha256": split.sha256(),
        "intake_manifest_sha256": intake.manifest_sha256,
        "split": split,
        "intake": intake,
    }


def evaluate_task_disjoint_feasibility(
    candidate_ids: Sequence[str],
    *,
    output_dir: Path,
) -> dict[str, Any]:
    """Write one read-only feasibility receipt for strict task-disjoint targets."""

    identifiers = tuple(candidate_ids)
    if identifiers != EXPECTED_CANDIDATE_IDS:
        raise TaskDisjointFeasibilityError(
            "feasibility audit requires exactly the ordered predeclared candidates: "
            + ", ".join(EXPECTED_CANDIDATE_IDS)
        )
    destination = output_dir.expanduser().resolve()
    allowed_root = (ROOT / "evaluation" / "bridgedata_task_disjoint_feasibility").resolve()
    try:
        destination.relative_to(allowed_root)
    except ValueError as error:
        raise TaskDisjointFeasibilityError("feasibility output must remain under its ignored local evaluation root") from error
    if destination.exists():
        raise TaskDisjointFeasibilityError("feasibility output destination already exists")
    candidates = {
        candidate_id: load_candidate_split_and_intake(candidate_id)
        for candidate_id in identifiers
    }
    intake_hashes = {item["intake_manifest_sha256"] for item in candidates.values()}
    if len(intake_hashes) != 1:
        raise TaskDisjointFeasibilityError("candidate intakes disagree")
    source_reports = {
        candidate_id: source_feasibility_report(
            candidate_id,
            item["split"],
            item["intake"],
        )
        for candidate_id, item in candidates.items()
    }
    payload = {
        "task_disjoint_feasibility_version": TASK_DISJOINT_FEASIBILITY_VERSION,
        "candidate_ids": list(identifiers),
        "intake_manifest_sha256": next(iter(intake_hashes)),
        "horizons": list(ACCEPTANCE_HORIZONS),
        "required_cases_per_horizon": DEFAULT_MAX_CASES_PER_HORIZON,
        "minimum_distinct_episode_clusters": DEFAULT_MIN_DISTINCT_EPISODES,
        "candidate_frozen_inputs": {
            candidate_id: {
                key: item[key]
                for key in ("manifest_sha256", "split_sha256", "intake_manifest_sha256")
            }
            for candidate_id, item in candidates.items()
        },
        "source_reports": source_reports,
        "overall_feasible": all(report["candidate_eligible_for_h1_h2_h5"] for report in source_reports.values()),
        "no_training": True,
        "no_candidate_creation": True,
        "no_checkpoint_mutation": True,
        "promotion_performed": False,
        "notes": [
            "This is feasibility evidence only; it does not evaluate candidate predictions.",
            "A later strict cross-candidate audit still requires a separately planned deterministic allocation and signed metric evidence.",
            "The strict target pool excludes source-train task IDs and all source-selected episodes.",
            "No policy, control, safety, renderer, native Chronos, or product-readiness claim is made.",
        ],
    }
    payload["payload_sha256"] = _sha256_json(payload)
    _write_new_json(destination / "task_disjoint_feasibility.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure strict source-train-task-disjoint BridgeData rollout feasibility.")
    parser.add_argument("--candidate-id", action="append", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    arguments = parser.parse_args()
    result = evaluate_task_disjoint_feasibility(
        arguments.candidate_id,
        output_dir=Path(arguments.output_dir),
    )
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
