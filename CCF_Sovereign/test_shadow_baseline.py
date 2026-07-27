"""Tests for no-training shadow baseline result artifacts."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from evaluation.shadow_baseline import (
    RUNNER_NAME,
    run_no_training_parent_baseline,
    sha256_text,
)
from evaluation.shadow_manifest import (
    BenchmarkCase,
    create_shadow_cycle_manifest,
)


def build_manifest(root: Path):
    parent = root / "parent.pt"
    train = root / "train.jsonl"
    parent.write_bytes(b"parent checkpoint bytes")
    train.write_text('{"prompt":"training only"}\n', encoding="utf-8")
    cases = [
        BenchmarkCase(
            case_id="retention-alpha",
            prompt="Return the alpha retention token.",
            expected_contains=("alpha",),
            tags=("retention",),
        ),
        BenchmarkCase(
            case_id="protected-bravo",
            prompt="Return the bravo protected token.",
            expected_contains=("bravo",),
            protected=True,
            tags=("protected",),
        ),
    ]
    return create_shadow_cycle_manifest(
        cycle_id="shadow-unit",
        parent_checkpoint=parent,
        training_inputs=[train],
        benchmark_cases=cases,
        root=root,
        notes="unit test shadow baseline",
    )


class ShadowBaselineTests(unittest.TestCase):
    def test_baseline_records_pass_fail_and_artifact_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = build_manifest(root)
            output = root / "baseline.json"

            def responder(prompt: str) -> str:
                if "alpha" in prompt:
                    return "alpha retained"
                return "not the expected token"

            result = run_no_training_parent_baseline(
                manifest,
                responder,
                output_path=output,
                run_id="baseline-unit",
            )

            self.assertTrue(output.exists())
            self.assertEqual(result.runner, RUNNER_NAME)
            self.assertEqual(result.manifest_sha256, manifest.manifest_sha256())
            self.assertEqual(result.aggregate()["passed_cases"], 1)
            self.assertEqual(result.aggregate()["failed_cases"], 1)
            self.assertEqual(result.aggregate()["protected_failed_cases"], 1)

            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["run_id"], "baseline-unit")
            self.assertFalse(saved["mutation_permitted"])
            self.assertFalse(saved["candidate_promotion_permitted"])
            self.assertEqual(saved["manifest_sha256"], manifest.manifest_sha256())
            self.assertEqual(
                saved["cases"][0]["response_sha256"],
                sha256_text("alpha retained"),
            )
            self.assertEqual(saved["result_sha256"], result.result_sha256())

    def test_baseline_preserves_manifest_hash_and_no_mutation_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = build_manifest(root)
            before_hash = manifest.manifest_sha256()
            parent_before = manifest.parent.to_dict()

            result = run_no_training_parent_baseline(
                manifest,
                lambda _prompt: "alpha bravo",
            )

            self.assertEqual(manifest.manifest_sha256(), before_hash)
            self.assertEqual(result.parent, parent_before)
            self.assertFalse(result.mutation_permitted)
            self.assertFalse(result.candidate_promotion_permitted)
            self.assertEqual(result.aggregate()["failed_cases"], 0)

    def test_responder_exception_is_captured_as_failed_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = build_manifest(root)

            def failing_responder(_prompt: str) -> str:
                raise RuntimeError("boom")

            result = run_no_training_parent_baseline(
                manifest,
                failing_responder,
                run_id="baseline-errors",
            )

            self.assertEqual(result.aggregate()["passed_cases"], 0)
            self.assertEqual(result.aggregate()["error_cases"], 2)
            self.assertTrue(result.cases[0].error.startswith("RuntimeError: boom"))
            self.assertEqual(result.cases[0].response, "")

    def test_non_string_response_is_captured_as_failed_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = build_manifest(root)

            result = run_no_training_parent_baseline(
                manifest,
                lambda _prompt: {"not": "text"},
            )

            self.assertEqual(result.aggregate()["error_cases"], 2)
            self.assertIn("not str", result.cases[0].error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
