"""
No-training baseline runner for shadow-cycle evidence.

This module evaluates benchmark cases from a shadow manifest through a caller
supplied parent responder. It records raw responses and pass/fail evidence. It
does not train, promote, mutate, or select a candidate model.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Protocol
from uuid import uuid4

from .shadow_manifest import BenchmarkCase, ShadowCycleManifest


RUNNER_NAME = "no_training_parent_baseline"


class BaselineResponder(Protocol):
    """Callable interface for parent-model inference."""

    def __call__(self, prompt: str) -> str:
        """Return a response for one benchmark prompt."""


def sha256_text(value: str) -> str:
    """Return the SHA-256 digest for UTF-8 text."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BenchmarkCaseResult:
    case_id: str
    prompt_sha256: str
    response: str
    response_sha256: str
    latency_ms: float
    passed: bool
    expected_contains: tuple[str, ...] = field(default_factory=tuple)
    missing_expected: tuple[str, ...] = field(default_factory=tuple)
    error: Optional[str] = None
    protected: bool = True
    tags: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "prompt_sha256": self.prompt_sha256,
            "response": self.response,
            "response_sha256": self.response_sha256,
            "latency_ms": self.latency_ms,
            "passed": self.passed,
            "expected_contains": list(self.expected_contains),
            "missing_expected": list(self.missing_expected),
            "error": self.error,
            "protected": self.protected,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class BaselineRunResult:
    run_id: str
    cycle_id: str
    manifest_sha256: str
    parent: dict
    cases: tuple[BenchmarkCaseResult, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )
    runner: str = RUNNER_NAME
    mutation_permitted: bool = False
    candidate_promotion_permitted: bool = False

    def aggregate(self) -> dict:
        total = len(self.cases)
        passed = sum(1 for case in self.cases if case.passed)
        errors = sum(1 for case in self.cases if case.error is not None)
        protected_total = sum(1 for case in self.cases if case.protected)
        protected_failed = sum(
            1 for case in self.cases if case.protected and not case.passed
        )
        mean_latency = (
            sum(case.latency_ms for case in self.cases) / total if total else 0.0
        )
        return {
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": total - passed,
            "error_cases": errors,
            "protected_cases": protected_total,
            "protected_failed_cases": protected_failed,
            "mean_latency_ms": round(mean_latency, 3),
        }

    def to_dict(self, include_result_sha256: bool = True) -> dict:
        payload = {
            "run_id": self.run_id,
            "cycle_id": self.cycle_id,
            "created_at_utc": self.created_at_utc,
            "runner": self.runner,
            "manifest_sha256": self.manifest_sha256,
            "parent": self.parent,
            "mutation_permitted": self.mutation_permitted,
            "candidate_promotion_permitted": self.candidate_promotion_permitted,
            "aggregate": self.aggregate(),
            "cases": [case.to_dict() for case in self.cases],
        }
        if include_result_sha256:
            payload["result_sha256"] = self.result_sha256()
        return payload

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(include_result_sha256=False),
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )

    def result_sha256(self) -> str:
        return sha256_text(self.canonical_json())

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                self.to_dict(include_result_sha256=True),
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path


def evaluate_benchmark_case(
    case: BenchmarkCase,
    responder: BaselineResponder,
) -> BenchmarkCaseResult:
    start = time.perf_counter()
    error = None
    try:
        response = responder(case.prompt)
        if not isinstance(response, str):
            raise TypeError(
                f"baseline responder returned {type(response).__name__}, not str"
            )
    except Exception as exc:  # pragma: no cover - exact exception path is tested.
        response = ""
        error = f"{type(exc).__name__}: {exc}"
    latency_ms = round((time.perf_counter() - start) * 1000, 3)

    missing_expected = tuple(
        expected
        for expected in case.expected_contains
        if expected not in response
    )
    passed = error is None and not missing_expected

    return BenchmarkCaseResult(
        case_id=case.case_id,
        prompt_sha256=case.prompt_sha256(),
        response=response,
        response_sha256=sha256_text(response),
        latency_ms=latency_ms,
        passed=passed,
        expected_contains=case.expected_contains,
        missing_expected=missing_expected,
        error=error,
        protected=case.protected,
        tags=case.tags,
    )


def run_no_training_parent_baseline(
    manifest: ShadowCycleManifest,
    responder: BaselineResponder,
    output_path: Optional[Path] = None,
    run_id: Optional[str] = None,
) -> BaselineRunResult:
    """
    Run a parent baseline from a validated manifest without mutating artifacts.

    The caller is responsible for binding `responder` to the real parent model
    when live model evidence is required. This function only enforces the
    evidence structure and records what happened.
    """
    manifest.validate()
    result = BaselineRunResult(
        run_id=run_id or f"baseline-{uuid4()}",
        cycle_id=manifest.cycle_id,
        manifest_sha256=manifest.manifest_sha256(),
        parent=manifest.parent.to_dict(),
        cases=tuple(
            evaluate_benchmark_case(case, responder)
            for case in manifest.benchmark_cases
        ),
    )
    if output_path is not None:
        result.save(output_path)
    return result
