"""Fail-closed promotion policy for Primus candidate evidence.

This module does not promote a model. It only evaluates whether a completed
candidate has enough evidence to justify an explicit operator-run promotion
command elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


VERDICT_IMPROVES = "CANDIDATE_IMPROVES"
FIFTY_M_RUNG = "50m"


def _lower_sha(value: Any) -> str:
    return str(value or "").strip().lower()


def _field(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return default
        current = current[key]
    return current


@dataclass(frozen=True)
class PromotionEvidence:
    """Evidence required before an operator may run explicit promotion."""

    candidate_manifest: Mapping[str, Any]
    comparison: Mapping[str, Any]
    expected_candidate_sha256: str
    expected_parent_sha256: str
    expected_evaluation_manifest_sha256: str
    live_parent_sha256_before: str
    live_parent_sha256_after: str
    operator_authorized: bool = False


@dataclass(frozen=True)
class PromotionDecision:
    """Pure policy decision; it never mutates checkpoint state."""

    eligible: bool
    reasons: tuple[str, ...]
    required_command: str | None = None
    performs_mutation: bool = False
    automatic_promotion: bool = False

    def require_eligible(self) -> None:
        if not self.eligible:
            raise ValueError("; ".join(self.reasons))


def evaluate_promotion_evidence(evidence: PromotionEvidence) -> PromotionDecision:
    """Evaluate promotion evidence without promoting anything."""

    reasons: list[str] = []
    manifest = evidence.candidate_manifest
    comparison = evidence.comparison
    expected_candidate_hash = _lower_sha(evidence.expected_candidate_sha256)
    expected_parent_hash = _lower_sha(evidence.expected_parent_sha256)
    expected_eval_manifest = _lower_sha(
        evidence.expected_evaluation_manifest_sha256
    )

    candidate_id = str(manifest.get("candidate_id") or "").strip()
    if not candidate_id:
        reasons.append("candidate manifest is missing candidate_id")
    if manifest.get("status") != "completed":
        reasons.append("candidate manifest status is not completed")

    latest_checkpoint = manifest.get("latest_checkpoint")
    if not isinstance(latest_checkpoint, Mapping):
        reasons.append("candidate manifest is missing latest_checkpoint")
        latest_checkpoint = {}
    latest_hash = _lower_sha(latest_checkpoint.get("sha256"))
    if latest_hash != expected_candidate_hash:
        reasons.append("candidate checkpoint hash does not match expected hash")

    promotion = manifest.get("promotion")
    if not isinstance(promotion, Mapping):
        reasons.append("candidate manifest is missing promotion policy block")
        promotion = {}
    if promotion.get("permitted_as_training_side_effect") is not False:
        reasons.append("candidate manifest permits promotion as a training side effect")
    if promotion.get("performed") is not False:
        reasons.append("candidate has already recorded a promotion")

    parent_hash = _lower_sha(_field(manifest, "parent", "sha256"))
    frozen_parent_hash = _lower_sha(_field(manifest, "frozen_parent", "sha256"))
    if parent_hash != expected_parent_hash:
        reasons.append("candidate manifest parent hash does not match expected parent")
    if frozen_parent_hash != expected_parent_hash:
        reasons.append(
            "candidate manifest frozen parent hash does not match expected parent"
        )
    if _lower_sha(evidence.live_parent_sha256_before) != expected_parent_hash:
        reasons.append("live parent hash before evaluation changed")
    if _lower_sha(evidence.live_parent_sha256_after) != expected_parent_hash:
        reasons.append("live parent hash after evaluation changed")

    if _lower_sha(comparison.get("manifest_sha256")) != expected_eval_manifest:
        reasons.append("comparison manifest hash does not match expected evaluation manifest")
    if comparison.get("candidate_gate_passed") is not True:
        reasons.append("parent/candidate comparison gate did not pass")
    if comparison.get("verdict") != VERDICT_IMPROVES:
        reasons.append("comparison verdict is not CANDIDATE_IMPROVES")
    aggregate = comparison.get("aggregate")
    if not isinstance(aggregate, Mapping):
        reasons.append("comparison aggregate is missing")
        aggregate = {}
    if int(aggregate.get("protected_regressions", 0)) != 0:
        reasons.append("comparison records protected-task regressions")
    if int(aggregate.get("new_error_cases", 0)) != 0:
        reasons.append("comparison records new candidate errors")
    if int(aggregate.get("pass_delta", 0)) <= 0:
        reasons.append("comparison pass delta is not positive")

    if not evidence.operator_authorized:
        reasons.append("operator authorization is required for promotion")

    command = None
    if candidate_id and expected_candidate_hash:
        command = (
            "python promote_candidate.py "
            f"--candidate-id {candidate_id} "
            f"--expected-candidate-sha256 {expected_candidate_hash}"
        )
    return PromotionDecision(
        eligible=not reasons,
        reasons=tuple(reasons),
        required_command=command,
        performs_mutation=False,
        automatic_promotion=False,
    )


@dataclass(frozen=True)
class BudgetSpec:
    """Resource budget for a governed training or ablation arm."""

    rung: str
    max_steps: int
    batch_size: int
    sequence_length: int
    epochs: int = 1
    learning_rate: float = 3e-4
    vocab_size: int = 2048
    promotion_permitted_by_default: bool = False

    def resource_key(self) -> tuple[Any, ...]:
        return (
            self.rung,
            int(self.max_steps),
            int(self.batch_size),
            int(self.sequence_length),
            int(self.epochs),
            float(self.learning_rate),
            int(self.vocab_size),
        )


@dataclass(frozen=True)
class AblationArm:
    name: str
    budget: BudgetSpec


@dataclass(frozen=True)
class BudgetParityDecision:
    allowed: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def require_allowed(self) -> None:
        if not self.allowed:
            raise ValueError("; ".join(self.reasons))


def _validate_budget_numbers(budget: BudgetSpec, label: str) -> list[str]:
    reasons: list[str] = []
    for field_name in ("max_steps", "batch_size", "sequence_length", "epochs"):
        if int(getattr(budget, field_name)) <= 0:
            reasons.append(f"{label} {field_name} must be positive")
    if budget.learning_rate <= 0:
        reasons.append(f"{label} learning_rate must be positive")
    if budget.vocab_size <= 0:
        reasons.append(f"{label} vocab_size must be positive")
    if budget.promotion_permitted_by_default:
        reasons.append(f"{label} permits promotion by default")
    return reasons


def validate_small_candidate_budget(
    budget: BudgetSpec,
    *,
    operator_authorized: bool,
    gate_armed: bool,
) -> BudgetParityDecision:
    """Validate the first serialized candidate run budget.

    The first run is intentionally constrained to a 50M-class rung. A 150M
    attempt must not slip through as an eager retry of the known OOM boundary.
    """

    reasons = _validate_budget_numbers(budget, "candidate budget")
    if budget.rung != FIFTY_M_RUNG:
        reasons.append("first candidate run must use the 50m rung")
    if not operator_authorized:
        reasons.append("operator authorization is required for candidate run")
    if not gate_armed:
        reasons.append("promotion/comparison gate must be armed before run")
    return BudgetParityDecision(allowed=not reasons, reasons=tuple(reasons))


def validate_ablation_budget_parity(
    arms: Sequence[AblationArm],
) -> BudgetParityDecision:
    """Require every ablation arm to use the same resource budget."""

    reasons: list[str] = []
    if len(arms) < 2:
        reasons.append("at least two ablation arms are required")
        return BudgetParityDecision(False, tuple(reasons))

    seen_names: set[str] = set()
    reference_key = arms[0].budget.resource_key()
    for arm in arms:
        if not arm.name:
            reasons.append("ablation arm name is required")
        if arm.name in seen_names:
            reasons.append(f"duplicate ablation arm name: {arm.name}")
        seen_names.add(arm.name)
        reasons.extend(_validate_budget_numbers(arm.budget, arm.name))
        if arm.budget.resource_key() != reference_key:
            reasons.append(f"{arm.name} resource budget differs from baseline")

    return BudgetParityDecision(allowed=not reasons, reasons=tuple(reasons))
