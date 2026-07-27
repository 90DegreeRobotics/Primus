"""Tests for shadow-cycle evidence manifests."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from evaluation.shadow_manifest import (
    BenchmarkCase,
    ShadowCycleManifest,
    create_shadow_cycle_manifest,
    sha256_file,
)


class ShadowManifestTests(unittest.TestCase):
    def test_file_hashing_matches_known_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact.txt"
            path.write_text("primus\n", encoding="utf-8")

            self.assertEqual(
                sha256_file(path),
                "83c758c45211ea671640adea8da1e2ddd17464d453d077f1b585280964c0f5ca",
            )

    def test_manifest_save_load_preserves_canonical_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = root / "parent.pt"
            train = root / "train.jsonl"
            parent.write_bytes(b"parent")
            train.write_text('{"prompt":"a","response":"b"}\n', encoding="utf-8")

            case = BenchmarkCase(
                case_id="retention-001",
                prompt="User: preserve a known skill\n\nAssistant:",
                expected_contains=("preserve",),
                tags=("retention",),
                source_path="eval/retention.jsonl",
            )
            manifest = create_shadow_cycle_manifest(
                cycle_id="shadow-001",
                parent_checkpoint=parent,
                training_inputs=[train],
                benchmark_cases=[case],
                root=root,
                notes="unit test manifest",
            )

            output = root / "manifest.json"
            manifest.save(output)
            loaded = ShadowCycleManifest.load(output)

            self.assertEqual(loaded.manifest_sha256(), manifest.manifest_sha256())
            self.assertEqual(loaded.leakage_warnings(), [])

    def test_manifest_rejects_train_eval_source_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = root / "parent.pt"
            train = root / "training" / "trace.jsonl"
            parent.write_bytes(b"parent")
            train.parent.mkdir()
            train.write_text("training trace\n", encoding="utf-8")

            case = BenchmarkCase(
                case_id="leaky-001",
                prompt="This prompt came from the training trace",
                source_path="training/trace.jsonl",
            )

            with self.assertRaisesRegex(ValueError, "uses training source"):
                create_shadow_cycle_manifest(
                    cycle_id="shadow-leak",
                    parent_checkpoint=parent,
                    training_inputs=[train],
                    benchmark_cases=[case],
                    root=root,
                )

    def test_manifest_rejects_duplicate_case_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = root / "parent.pt"
            train = root / "train.jsonl"
            parent.write_bytes(b"parent")
            train.write_text("training trace\n", encoding="utf-8")

            cases = [
                BenchmarkCase(case_id="dup", prompt="first"),
                BenchmarkCase(case_id="dup", prompt="second"),
            ]

            with self.assertRaisesRegex(ValueError, "duplicate benchmark case IDs"):
                create_shadow_cycle_manifest(
                    cycle_id="shadow-dup",
                    parent_checkpoint=parent,
                    training_inputs=[train],
                    benchmark_cases=cases,
                    root=root,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
