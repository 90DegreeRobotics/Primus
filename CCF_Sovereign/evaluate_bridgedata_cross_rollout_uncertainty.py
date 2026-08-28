"""Read-only paired uncertainty audit for signed BridgeData cross-rollout evidence.

The original cross-rollout report stores aggregate metrics but not paired residual
vectors.  This evaluator reconstructs only its fixed deterministic rollout cases
from hash-verified frozen rejected candidates, refuses any aggregate mismatch,
and adds a cluster-bootstrap interpretation.  It never trains, creates a
candidate, changes a checkpoint, or permits promotion.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from evaluate_bridgedata_cross_candidate_rollout import (  # noqa: E402
    PROTECTED_SPLITS,
    cross_partitioned_transitions,
    cross_semantics_report,
)
from evaluate_bridgedata_rollout_stability import (  # noqa: E402
    EXPECTED_CANDIDATE_IDS,
    ROOT,
    FrozenRolloutEvidenceError,
    _sha256_json,
    _write_new_json,
    load_frozen_rollout_candidate,
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
    DEFAULT_HORIZONS,
    DEFAULT_MAX_CASES_PER_HORIZON,
    action_only_mean_delta_predictor,
    build_rollout_cases,
    copy_state_predictor,
    linear_state_action_delta_predictor,
    nearest_train_state_action_predictor,
    rollout_predictions,
    score_rollout_predictions,
)
from real_data.bridgedata_transitions import sha256_file  # noqa: E402
from train_bridgedata_real_transition import resolve_device  # noqa: E402


CROSS_UNCERTAINTY_AUDIT_VERSION = 1
SIGNED_CROSS_EVIDENCE_PATH = (
    ROOT
    / "evaluation"
    / "bridgedata_cross_rollouts"
    / "cross-rollout-20260828-linear-001"
    / "cross_rollout_stability.json"
)
SIGNED_CROSS_EVIDENCE_SHA256 = "2c8dd8c8930b968cebbac7c75403150a9ec1b861d14719171da6fbea088ac484"
SIGNED_CROSS_PAYLOAD_SHA256 = "60b066d31bca385a28e9ae644d359e6c64470a50495dec5520c99afad8f7635e"
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "evaluation"
    / "bridgedata_cross_rollout_uncertainty"
    / "cross-rollout-uncertainty-20260828-001"
)
ACCEPTANCE_HORIZONS = (1, 2, 5)
RMSE_PARITY_ABSOLUTE_TOLERANCE = 1e-12


class CrossRolloutUncertaintyAuditError(ValueError):
    """Raised when signed evidence or its deterministic reconstruction is invalid."""


def _load_signed_cross_evidence(path: Path) -> dict[str, Any]:
    """Load and bind the exact immutable evidence file that this audit interprets."""

    resolved = path.resolve()
    if not resolved.is_file():
        raise CrossRolloutUncertaintyAuditError("signed cross-rollout evidence file is missing")
    if sha256_file(resolved) != SIGNED_CROSS_EVIDENCE_SHA256:
        raise CrossRolloutUncertaintyAuditError("signed cross-rollout evidence file SHA-256 drifted")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CrossRolloutUncertaintyAuditError("signed cross-rollout evidence is invalid JSON") from error
    if not isinstance(payload, dict):
        raise CrossRolloutUncertaintyAuditError("signed cross-rollout evidence root must be an object")
    claimed = payload.pop("payload_sha256", None)
    if claimed != SIGNED_CROSS_PAYLOAD_SHA256 or _sha256_json(payload) != claimed:
        raise CrossRolloutUncertaintyAuditError("signed cross-rollout evidence payload hash drifted")
    payload["payload_sha256"] = claimed
    if tuple(payload.get("candidate_ids", ())) != EXPECTED_CANDIDATE_IDS:
        raise CrossRolloutUncertaintyAuditError("signed cross-rollout evidence candidate IDs disagree")
    if payload.get("no_training") is not True or payload.get("no_candidate_creation") is not True or payload.get("no_checkpoint_mutation") is not True or payload.get("promotion_performed") is not False:
        raise CrossRolloutUncertaintyAuditError("signed cross-rollout evidence violates the no-mutation boundary")
    return payload


def _metric_from_signed_report(report: Mapping[str, Any], split: str, horizon: int) -> Mapping[str, Any]:
    try:
        metric = report["by_split_and_horizon"][split][str(horizon)]
    except (KeyError, TypeError) as error:
        raise CrossRolloutUncertaintyAuditError("signed report lacks a required split/horizon metric") from error
    if not isinstance(metric, Mapping):
        raise CrossRolloutUncertaintyAuditError("signed metric has invalid structure")
    return metric


def _require_metric_parity(
    recomputed: Mapping[str, Any],
    signed: Mapping[str, Any],
    *,
    label: str,
) -> None:
    for key in ("cases", "predictions", "coverage", "finite_prediction_rate", "case_set_sha256"):
        if recomputed.get(key) != signed.get(key):
            raise CrossRolloutUncertaintyAuditError(f"{label} signed metric disagreement: {key}")
    observed = recomputed.get("aggregate_rmse")
    expected = signed.get("aggregate_rmse")
    if not isinstance(observed, (float, int)) or not isinstance(expected, (float, int)) or not math.isclose(
        float(observed), float(expected), rel_tol=0.0, abs_tol=RMSE_PARITY_ABSOLUTE_TOLERANCE
    ):
        raise CrossRolloutUncertaintyAuditError(f"{label} signed metric disagreement: aggregate_rmse")


def _strongest_signed_baseline_label(signed_pair: Mapping[str, Any], split: str, horizon: int) -> str:
    try:
        declared = signed_pair["acceptance"]["by_protected_split_and_horizon"][split][str(horizon)]
        label = declared["strongest_baseline"]
        baseline_reports = signed_pair["baseline_reports"]
    except (KeyError, TypeError) as error:
        raise CrossRolloutUncertaintyAuditError("signed cross evidence lacks an acceptance baseline") from error
    if label not in baseline_reports:
        raise CrossRolloutUncertaintyAuditError("signed acceptance baseline is not present in signed baseline reports")
    candidates = []
    for candidate_label, report in baseline_reports.items():
        metric = _metric_from_signed_report(report, split, horizon)
        value = metric.get("aggregate_rmse")
        if not isinstance(value, (float, int)) or not math.isfinite(float(value)):
            raise CrossRolloutUncertaintyAuditError("signed baseline metric is invalid")
        candidates.append((candidate_label, float(value)))
    recomputed_label, recomputed_value = min(candidates, key=lambda item: (item[1], item[0]))
    declared_value = declared.get("strongest_baseline_aggregate_rmse")
    if label != recomputed_label or not isinstance(declared_value, (float, int)) or not math.isclose(
        float(declared_value), recomputed_value, rel_tol=0.0, abs_tol=RMSE_PARITY_ABSOLUTE_TOLERANCE
    ):
        raise CrossRolloutUncertaintyAuditError("signed strongest-baseline declaration disagrees with signed reports")
    return str(label)


def _baseline_predictors(partitioned: Mapping[str, Sequence[Any]]) -> dict[str, Any]:
    train = partitioned[TRAIN_SPLIT]
    action = ActionOnlyMeanDeltaBaseline.fit(train)
    linear = LinearStateActionDeltaBaseline.fit(train)
    nearest = NearestTrainStateActionBaseline.fit(train)
    return {
        "copy_state": copy_state_predictor,
        "action_only_mean_delta": action_only_mean_delta_predictor(action),
        "linear_state_action_delta": linear_state_action_delta_predictor(linear),
        "nearest_train_state_action": nearest_train_state_action_predictor(nearest),
    }


def _audit_row(
    *,
    source_candidate_id: str,
    target_candidate_id: str,
    split: str,
    horizon: int,
    source_frozen: Mapping[str, Any],
    partitioned: Mapping[str, Sequence[Any]],
    signed_pair: Mapping[str, Any],
) -> dict[str, Any]:
    predictors = _baseline_predictors(partitioned)
    baseline_label = _strongest_signed_baseline_label(signed_pair, split, horizon)
    cases = build_rollout_cases(
        partitioned[split],
        split=split,
        horizon=horizon,
        max_cases=DEFAULT_MAX_CASES_PER_HORIZON,
        case_selection_seed=DEFAULT_CASE_SELECTION_SEED,
    )
    candidate_predictions = rollout_predictions(cases, source_frozen["model_predictor"])
    baseline_predictions = rollout_predictions(cases, predictors[baseline_label])
    candidate_metrics = score_rollout_predictions(cases, candidate_predictions).to_dict()
    baseline_metrics = score_rollout_predictions(cases, baseline_predictions).to_dict()
    _require_metric_parity(
        candidate_metrics,
        _metric_from_signed_report(signed_pair["candidate_report"], split, horizon),
        label=f"{source_candidate_id}->{target_candidate_id} candidate {split} h{horizon}",
    )
    _require_metric_parity(
        baseline_metrics,
        _metric_from_signed_report(signed_pair["baseline_reports"][baseline_label], split, horizon),
        label=f"{source_candidate_id}->{target_candidate_id} baseline {baseline_label} {split} h{horizon}",
    )
    errors = paired_rollout_case_errors(cases, candidate_predictions, baseline_predictions)
    bootstrap = episode_clustered_paired_bootstrap(
        errors,
        resamples=DEFAULT_BOOTSTRAP_RESAMPLES,
        seed=DEFAULT_BOOTSTRAP_SEED,
        minimum_distinct_episodes=DEFAULT_MIN_DISTINCT_EPISODES,
    )
    return {
        "source_candidate_id": source_candidate_id,
        "target_candidate_id": target_candidate_id,
        "target_partition": split,
        "horizon": horizon,
        "strongest_signed_baseline": baseline_label,
        "signed_metric_parity_absolute_tolerance": RMSE_PARITY_ABSOLUTE_TOLERANCE,
        "candidate_metrics": candidate_metrics,
        "baseline_metrics": baseline_metrics,
        "paired_bootstrap": bootstrap.to_dict(),
        "raw_paired_case_errors": [item.to_dict() for item in errors],
    }


def audit_cross_rollout_uncertainty(
    candidate_ids: Sequence[str],
    *,
    output_dir: Path,
    device_name: str = "cpu",
    signed_evidence_path: Path = SIGNED_CROSS_EVIDENCE_PATH,
) -> dict[str, Any]:
    """Run one bounded read-only audit against exact signed cross-rollout evidence."""

    identifiers = tuple(candidate_ids)
    if identifiers != EXPECTED_CANDIDATE_IDS:
        raise CrossRolloutUncertaintyAuditError(
            "uncertainty audit requires exactly the ordered predeclared candidates: " + ", ".join(EXPECTED_CANDIDATE_IDS)
        )
    destination = output_dir.expanduser().resolve()
    allowed_root = (ROOT / "evaluation" / "bridgedata_cross_rollout_uncertainty").resolve()
    try:
        destination.relative_to(allowed_root)
    except ValueError as error:
        raise CrossRolloutUncertaintyAuditError("uncertainty output must remain under its ignored local evaluation root") from error
    if destination.exists():
        raise CrossRolloutUncertaintyAuditError("uncertainty output destination already exists")
    signed = _load_signed_cross_evidence(signed_evidence_path)
    device = resolve_device(device_name)
    frozen = {candidate_id: load_frozen_rollout_candidate(candidate_id, device=device) for candidate_id in identifiers}
    results: dict[str, Any] = {}
    for source_id, target_id in ((identifiers[0], identifiers[1]), (identifiers[1], identifiers[0])):
        key = f"{source_id}_on_{target_id}"
        try:
            signed_pair = signed["cross_pairs"][key]
        except (KeyError, TypeError) as error:
            raise CrossRolloutUncertaintyAuditError("signed evidence lacks a required ordered cross pair") from error
        partitioned = cross_partitioned_transitions(frozen[source_id], frozen[target_id])
        rows = [
            _audit_row(
                source_candidate_id=source_id,
                target_candidate_id=target_id,
                split=split,
                horizon=horizon,
                source_frozen=frozen[source_id],
                partitioned=partitioned,
                signed_pair=signed_pair,
            )
            for split in PROTECTED_SPLITS
            for horizon in ACCEPTANCE_HORIZONS
        ]
        results[key] = {
            "semantics": cross_semantics_report(frozen[source_id], frozen[target_id]),
            "rows": rows,
        }
    payload = {
        "cross_rollout_uncertainty_audit_version": CROSS_UNCERTAINTY_AUDIT_VERSION,
        "candidate_ids": list(identifiers),
        "device": str(device),
        "signed_cross_evidence": {
            "path": str(signed_evidence_path.resolve()),
            "sha256": SIGNED_CROSS_EVIDENCE_SHA256,
            "payload_sha256": SIGNED_CROSS_PAYLOAD_SHA256,
        },
        "horizons": list(ACCEPTANCE_HORIZONS),
        "case_selection_seed": DEFAULT_CASE_SELECTION_SEED,
        "max_cases_per_horizon": DEFAULT_MAX_CASES_PER_HORIZON,
        "bootstrap": {
            "resamples": DEFAULT_BOOTSTRAP_RESAMPLES,
            "seed": DEFAULT_BOOTSTRAP_SEED,
            "minimum_distinct_episodes": DEFAULT_MIN_DISTINCT_EPISODES,
            "resampling_unit": "episode",
            "response": "candidate minus strongest-baseline case-level mean squared state error",
            "interpretation_rule": {
                "pass": "candidate point RMSE is lower and paired cluster-bootstrap 95% MSE interval upper endpoint is below zero",
                "fail": "candidate point RMSE is higher and paired cluster-bootstrap 95% MSE interval lower endpoint is above zero",
                "indistinguishable": "exact finite coverage but neither pass nor fail interval/direction condition holds",
            },
        },
        "cross_pairs": results,
        "no_training": True,
        "no_candidate_creation": True,
        "no_checkpoint_mutation": True,
        "promotion_performed": False,
        "notes": [
            "This read-only audit reconstructs deterministic cases to derive paired residuals because signed cross evidence stores aggregate metrics only.",
            "Every reconstructed candidate/baseline aggregate metric must match signed evidence before bootstrap calculation.",
            "The bootstrap resamples selected episode clusters, preserving all selected cases per drawn episode; it is descriptive uncertainty analysis, not causal or safety evidence.",
            "Cross-candidate target selections are episode-disjoint from source train selections but have source-train task overlap, so no strict unseen-task claim is made relative to source candidates.",
            "No output authorizes promotion, robot policy, control, safety, renderer, native Chronos, or product-readiness claims.",
        ],
    }
    payload["payload_sha256"] = _sha256_json(payload)
    _write_new_json(destination / "cross_rollout_uncertainty.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a paired cluster-bootstrap uncertainty audit on signed BridgeData cross-rollout evidence.")
    parser.add_argument("--candidate-id", action="append", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--device", default="cpu", choices=("cpu", "auto", "cuda"))
    arguments = parser.parse_args()
    result = audit_cross_rollout_uncertainty(
        arguments.candidate_id,
        output_dir=Path(arguments.output_dir),
        device_name=arguments.device,
    )
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
