"""Tests for live parent baseline helpers without requiring the real checkpoint."""
import sys
import tempfile
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from evaluation.live_parent_baseline import (
    DEFAULT_BENCHMARK_CASES,
    LIVE_BASELINE_CYCLE_ID,
    build_live_parent_manifest,
    extract_assistant_response,
    select_device,
)


class LiveParentBaselineTests(unittest.TestCase):
    def test_default_benchmark_cases_are_unique_and_outreach_safe(self):
        case_ids = [case.case_id for case in DEFAULT_BENCHMARK_CASES]

        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertGreaterEqual(len(case_ids), 3)
        for case in DEFAULT_BENCHMARK_CASES:
            self.assertTrue(case.protected)
            self.assertIn("outreach-safe", case.tags)
            self.assertIsNone(case.source_path)
            self.assertTrue(case.expected_contains)

    def test_build_live_parent_manifest_uses_real_file_evidence_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkpoint = root / "checkpoints" / "parent.pt"
            checkpoint.parent.mkdir()
            checkpoint.write_bytes(b"checkpoint bytes")

            manifest = build_live_parent_manifest(
                checkpoint_path=checkpoint,
                root=root,
            )

            self.assertEqual(manifest.cycle_id, LIVE_BASELINE_CYCLE_ID)
            self.assertEqual(manifest.parent.path, "checkpoints/parent.pt")
            self.assertEqual(manifest.parent.bytes, len(b"checkpoint bytes"))
            self.assertEqual(manifest.training_inputs, ())
            self.assertIsNone(manifest.candidate)
            self.assertEqual(manifest.leakage_warnings(), [])

    def test_extract_assistant_response_prefers_last_assistant_marker(self):
        decoded = "User: hello\n\nAssistant: first\n\nAssistant: final answer"

        self.assertEqual(
            extract_assistant_response(decoded, "User: hello\n\nAssistant:"),
            "final answer",
        )

    def test_select_device_auto_returns_available_torch_device(self):
        device = select_device("auto")

        self.assertIsInstance(device, torch.device)
        self.assertIn(device.type, {"cpu", "cuda"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
