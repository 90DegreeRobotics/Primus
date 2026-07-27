"""Tests for parent/candidate shadow comparison artifacts."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from evaluation.shadow_compare import (
    VERDICT_IMPROVES,
    VERDICT_REJECT_NEW_ERRORS,
    VERDICT_REJECT_PROTECTED_REGRESSION,
    compare_shadow_result_files,
    compare_shadow_results,
)


def case(
    case_id: str,
    passed: bool,
    protected: bool = True,
    latency_ms: float = 10.0,
    error=None,
    missing_expected=(),
):
    return {
        "case_id": case_id,
        "prompt_sha256": f"prompt-{case_id}",
        "response": f"raw response for {case_id}",
        "response_sha256": f"response-{case_id}-{passed}-{error}",
        "latency_ms": latency_ms,
        "passed": passed,
        "expected_contains": [],
        "missing_expected": list(missing_expected),
        "error": error,
        "protected": protected,
        "tags": ["fixture"],
    }


def result(run_id: str, cases, manifest="manifest-1", cycle="cycle-1"):
    passed = sum(1 for item in cases if item["passed"])
    errors = sum(1 for item in cases if item["error"] is not None)
    protected_cases = sum(1 for item in cases if item["protected"])
    protected_failed = sum(
        1 for item in cases if item["protected"] and not item["passed"]
    )
    mean_latency = sum(item["latency_ms"] for item in cases) / len(cases)
    return {
        "run_id": run_id,
        "cycle_id": cycle,
        "created_at_utc": "2026-07-27T00:00:00+00:00",
        "runner": "fixture",
        "manifest_sha256": manifest,
        "parent": {"path": "fixture.pt", "sha256": "parent", "bytes": 1},
        "mutation_permitted": False,
        "candidate_promotion_permitted": False,
        "aggregate": {
            "total_cases": len(cases),
            "passed_cases": passed,
            "failed_cases": len(cases) - passed,
            "error_cases": errors,
            "protected_cases": protected_cases,
            "protected_failed_cases": protected_failed,
            "mean_latency_ms": mean_latency,
        },
        "cases": list(cases),
    }


class ShadowCompareTests(unittest.TestCase):
    def test_candidate_improvement_passes_gate_without_raw_responses(self):
        parent = result(
            "parent",
            [
                case("alpha", False, missing_expected=("alpha",)),
                case("bravo", False, missing_expected=("bravo",)),
            ],
        )
        candidate = result(
            "candidate",
            [
                case("alpha", True, latency_ms=12.0),
                case("bravo", False, latency_ms=8.0, missing_expected=("bravo",)),
            ],
        )

        comparison = compare_shadow_results(parent, candidate, comparison_id="cmp")

        self.assertEqual(comparison.verdict(), VERDICT_IMPROVES)
        self.assertTrue(comparison.candidate_gate_passed())
        self.assertEqual(comparison.aggregate()["pass_delta"], 1)
        self.assertEqual(comparison.aggregate()["recovered_failures"], 1)
        self.assertEqual(comparison.aggregate()["protected_regressions"], 0)
        payload = comparison.to_dict()
        self.assertNotIn("raw response for", json.dumps(payload))
        self.assertIn("comparison_sha256", payload)

    def test_protected_regression_rejects_candidate(self):
        parent = result("parent", [case("alpha", True, protected=True)])
        candidate = result(
            "candidate",
            [case("alpha", False, protected=True, missing_expected=("alpha",))],
        )

        comparison = compare_shadow_results(parent, candidate)

        self.assertEqual(comparison.verdict(), VERDICT_REJECT_PROTECTED_REGRESSION)
        self.assertFalse(comparison.candidate_gate_passed())
        self.assertEqual(comparison.aggregate()["protected_regressions"], 1)

    def test_new_error_rejects_candidate(self):
        parent = result("parent", [case("alpha", False)])
        candidate = result(
            "candidate",
            [case("alpha", False, error="RuntimeError: boom")],
        )

        comparison = compare_shadow_results(parent, candidate)

        self.assertEqual(comparison.verdict(), VERDICT_REJECT_NEW_ERRORS)
        self.assertFalse(comparison.candidate_gate_passed())
        self.assertEqual(comparison.aggregate()["new_error_cases"], 1)

    def test_rejects_manifest_hash_mismatch(self):
        parent = result("parent", [case("alpha", False)], manifest="parent")
        candidate = result("candidate", [case("alpha", True)], manifest="candidate")

        with self.assertRaisesRegex(ValueError, "manifest SHA-256"):
            compare_shadow_results(parent, candidate)

    def test_rejects_case_set_mismatch(self):
        parent = result("parent", [case("alpha", False)])
        candidate = result("candidate", [case("bravo", True)])

        with self.assertRaisesRegex(ValueError, "case sets differ"):
            compare_shadow_results(parent, candidate)

    def test_compare_files_writes_output_artifact(self):
        parent = result("parent", [case("alpha", False)])
        candidate = result("candidate", [case("alpha", True)])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent_path = root / "parent.json"
            candidate_path = root / "candidate.json"
            output_path = root / "comparison.json"
            parent_path.write_text(json.dumps(parent), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

            comparison = compare_shadow_result_files(
                parent_path,
                candidate_path,
                output_path=output_path,
                comparison_id="file-cmp",
            )

            saved = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(comparison.comparison_sha256(), saved["comparison_sha256"])
            self.assertEqual(saved["comparison_id"], "file-cmp")
            self.assertEqual(saved["verdict"], VERDICT_IMPROVES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
