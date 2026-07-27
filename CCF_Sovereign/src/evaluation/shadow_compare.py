"""
Parent/candidate comparison gate for shadow-cycle evidence.

This module compares two manifest-bound baseline result artifacts. It never
uses raw response text in its output; decisions are based on existing pass/fail,
error, latency, protected-task, and hash fields.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4


COMPARE_VERSION = 1
COMPARE_RUNNER = "shadow_parent_candidate_compare"

VERDICT_IMPROVES = "CANDIDATE_IMPROVES"
VERDICT_NO_IMPROVEMENT = "NO_PROMOTION_NO_IMPROVEMENT"
VERDICT_REJECT_PROTECTED_REGRESSION = "REJECT_PROTECTED_REGRESSION"
VERDICT_REJECT_NEW_ERRORS = "REJECT_NEW_ERRORS"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_result_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_result_shape(result: dict, label: str) -> None:
    for key in ("run_id", "cycle_id", "manifest_sha256", "aggregate", "cases"):
        if key not in result:
            raise ValueError(f"{label} result missing required key: {key}")
    if not isinstance(result["cases"], list):
        raise ValueError(f"{label} result cases must be a list")

    case_ids = [str(case.get("case_id", "")) for case in result["cases"]]
    if any(not case_id for case_id in case_ids):
        raise ValueError(f"{label} result contains case without case_id")
    duplicates = sorted(
        {case_id for case_id in case_ids if case_ids.count(case_id) > 1}
    )
    if duplicates:
        raise ValueError(
            f"{label} result duplicate case IDs: {', '.join(duplicates)}"
        )


def _case_index(result: dict) -> dict[str, dict]:
    return {str(case["case_id"]): case for case in result["cases"]}


@dataclass(frozen=True)
class CaseComparison:
    case_id: str
    protected: bool
    parent_passed: bool
    candidate_passed: bool
    pass_delta: int
    parent_error: Optional[str]
    candidate_error: Optional[str]
    new_error: bool
    protected_regression: bool
    recovered_failure: bool
    latency_delta_ms: float
    parent_response_sha256: Optional[str] = None
    candidate_response_sha256: Optional[str] = None
    parent_missing_expected: tuple[str, ...] = field(default_factory=tuple)
    candidate_missing_expected: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "protected": self.protected,
            "parent_passed": self.parent_passed,
            "candidate_passed": self.candidate_passed,
            "pass_delta": self.pass_delta,
            "parent_error": self.parent_error,
            "candidate_error": self.candidate_error,
            "new_error": self.new_error,
            "protected_regression": self.protected_regression,
            "recovered_failure": self.recovered_failure,
            "latency_delta_ms": self.latency_delta_ms,
            "parent_response_sha256": self.parent_response_sha256,
            "candidate_response_sha256": self.candidate_response_sha256,
            "parent_missing_expected": list(self.parent_missing_expected),
            "candidate_missing_expected": list(self.candidate_missing_expected),
        }


@dataclass(frozen=True)
class ShadowComparison:
    comparison_id: str
    manifest_sha256: str
    cycle_id: str
    parent_run_id: str
    candidate_run_id: str
    cases: tuple[CaseComparison, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )
    comparison_version: int = COMPARE_VERSION
    runner: str = COMPARE_RUNNER

    def aggregate(self) -> dict:
        total = len(self.cases)
        pass_delta = sum(case.pass_delta for case in self.cases)
        protected_regressions = sum(
            1 for case in self.cases if case.protected_regression
        )
        new_errors = sum(1 for case in self.cases if case.new_error)
        recovered_failures = sum(
            1 for case in self.cases if case.recovered_failure
        )
        mean_latency_delta = (
            sum(case.latency_delta_ms for case in self.cases) / total
            if total
            else 0.0
        )
        return {
            "total_cases": total,
            "pass_delta": pass_delta,
            "recovered_failures": recovered_failures,
            "protected_regressions": protected_regressions,
            "new_error_cases": new_errors,
            "mean_case_latency_delta_ms": round(mean_latency_delta, 3),
        }

    def verdict(self) -> str:
        aggregate = self.aggregate()
        if aggregate["protected_regressions"] > 0:
            return VERDICT_REJECT_PROTECTED_REGRESSION
        if aggregate["new_error_cases"] > 0:
            return VERDICT_REJECT_NEW_ERRORS
        if aggregate["pass_delta"] > 0:
            return VERDICT_IMPROVES
        return VERDICT_NO_IMPROVEMENT

    def candidate_gate_passed(self) -> bool:
        return self.verdict() == VERDICT_IMPROVES

    def to_dict(self, include_comparison_sha256: bool = True) -> dict:
        payload = {
            "comparison_version": self.comparison_version,
            "comparison_id": self.comparison_id,
            "created_at_utc": self.created_at_utc,
            "runner": self.runner,
            "manifest_sha256": self.manifest_sha256,
            "cycle_id": self.cycle_id,
            "parent_run_id": self.parent_run_id,
            "candidate_run_id": self.candidate_run_id,
            "verdict": self.verdict(),
            "candidate_gate_passed": self.candidate_gate_passed(),
            "aggregate": self.aggregate(),
            "cases": [case.to_dict() for case in self.cases],
        }
        if include_comparison_sha256:
            payload["comparison_sha256"] = self.comparison_sha256()
        return payload

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(include_comparison_sha256=False),
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )

    def comparison_sha256(self) -> str:
        return sha256_text(self.canonical_json())

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                self.to_dict(include_comparison_sha256=True),
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path


def compare_shadow_results(
    parent_result: dict,
    candidate_result: dict,
    output_path: Optional[Path] = None,
    comparison_id: Optional[str] = None,
) -> ShadowComparison:
    _require_result_shape(parent_result, "parent")
    _require_result_shape(candidate_result, "candidate")

    if parent_result["manifest_sha256"] != candidate_result["manifest_sha256"]:
        raise ValueError("parent and candidate manifest SHA-256 values differ")
    if parent_result["cycle_id"] != candidate_result["cycle_id"]:
        raise ValueError("parent and candidate cycle IDs differ")

    parent_cases = _case_index(parent_result)
    candidate_cases = _case_index(candidate_result)
    if set(parent_cases) != set(candidate_cases):
        missing_candidate = sorted(set(parent_cases) - set(candidate_cases))
        missing_parent = sorted(set(candidate_cases) - set(parent_cases))
        raise ValueError(
            "parent and candidate case sets differ; "
            f"missing_candidate={missing_candidate}; "
            f"missing_parent={missing_parent}"
        )

    comparisons = tuple(
        _compare_case(parent_cases[case_id], candidate_cases[case_id])
        for case_id in sorted(parent_cases)
    )
    comparison = ShadowComparison(
        comparison_id=comparison_id or f"compare-{uuid4()}",
        manifest_sha256=str(parent_result["manifest_sha256"]),
        cycle_id=str(parent_result["cycle_id"]),
        parent_run_id=str(parent_result["run_id"]),
        candidate_run_id=str(candidate_result["run_id"]),
        cases=comparisons,
    )
    if output_path is not None:
        comparison.save(output_path)
    return comparison


def compare_shadow_result_files(
    parent_result_path: Path,
    candidate_result_path: Path,
    output_path: Optional[Path] = None,
    comparison_id: Optional[str] = None,
) -> ShadowComparison:
    return compare_shadow_results(
        load_result_json(parent_result_path),
        load_result_json(candidate_result_path),
        output_path=output_path,
        comparison_id=comparison_id,
    )


def _compare_case(parent_case: dict, candidate_case: dict) -> CaseComparison:
    parent_passed = bool(parent_case.get("passed", False))
    candidate_passed = bool(candidate_case.get("passed", False))
    protected = bool(parent_case.get("protected", True)) or bool(
        candidate_case.get("protected", True)
    )
    parent_error = parent_case.get("error")
    candidate_error = candidate_case.get("error")

    return CaseComparison(
        case_id=str(parent_case["case_id"]),
        protected=protected,
        parent_passed=parent_passed,
        candidate_passed=candidate_passed,
        pass_delta=int(candidate_passed) - int(parent_passed),
        parent_error=parent_error,
        candidate_error=candidate_error,
        new_error=parent_error is None and candidate_error is not None,
        protected_regression=protected and parent_passed and not candidate_passed,
        recovered_failure=not parent_passed and candidate_passed,
        latency_delta_ms=round(
            float(candidate_case.get("latency_ms", 0.0))
            - float(parent_case.get("latency_ms", 0.0)),
            3,
        ),
        parent_response_sha256=parent_case.get("response_sha256"),
        candidate_response_sha256=candidate_case.get("response_sha256"),
        parent_missing_expected=tuple(parent_case.get("missing_expected", [])),
        candidate_missing_expected=tuple(
            candidate_case.get("missing_expected", [])
        ),
    )
