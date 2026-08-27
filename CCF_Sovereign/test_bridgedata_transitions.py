from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.bridgedata_transitions import (  # noqa: E402
    BridgeDataError,
    BridgeDataTransitionConfig,
    derive_bridgedata_transitions,
    load_bridgedata_intake,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector(value: float) -> list[float]:
    return [value + dimension / 10 for dimension in range(7)]


class BridgeDataTransitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "intake"
        self.root.mkdir()
        self._write_valid_fixture()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def manifest_path(self) -> Path:
        return self.root / "intake_manifest.json"

    def _write_valid_fixture(self, *, rows: list[dict] | None = None) -> None:
        (self.root / "meta_info.json").write_text("{}\n", encoding="utf-8")
        (self.root / "meta_stats.json").write_text("{}\n", encoding="utf-8")
        (self.root / "intake_receipt.json").write_text("{}\n", encoding="utf-8")
        pq.write_table(
            pa.Table.from_pylist(
                [
                    {"task": "alpha task", "task_index": 0},
                    {"task": "beta task", "task_index": 1},
                    {"task": "", "task_index": 2},
                ]
            ),
            self.root / "meta_tasks.parquet",
        )
        pq.write_table(
            pa.Table.from_pylist(
                [
                    {
                        "episode_index": 7,
                        "tasks": ["alpha task"],
                        "length": 3,
                        "data/chunk_index": 0,
                        "data/file_index": 0,
                        "dataset_from_index": 0,
                        "dataset_to_index": 3,
                    },
                    {
                        "episode_index": 8,
                        "tasks": ["beta task"],
                        "length": 3,
                        "data/chunk_index": 0,
                        "data/file_index": 0,
                        "dataset_from_index": 3,
                        "dataset_to_index": 6,
                    },
                ]
            ),
            self.root / "meta_episodes_chunk-000_file-000.parquet",
        )
        if rows is None:
            rows = [
                {
                    "observation.state": vector(0.0),
                    "action": vector(10.0),
                    "timestamp": 0.0,
                    "frame_index": 0,
                    "episode_index": 7,
                    "index": 0,
                    "task_index": 0,
                },
                {
                    "observation.state": vector(1.0),
                    "action": vector(11.0),
                    "timestamp": 0.2,
                    "frame_index": 1,
                    "episode_index": 7,
                    "index": 1,
                    "task_index": 0,
                },
                {
                    "observation.state": vector(2.0),
                    "action": vector(12.0),
                    "timestamp": 0.4,
                    "frame_index": 2,
                    "episode_index": 7,
                    "index": 2,
                    "task_index": 0,
                },
                {
                    "observation.state": vector(3.0),
                    "action": vector(13.0),
                    "timestamp": 0.0,
                    "frame_index": 0,
                    "episode_index": 8,
                    "index": 3,
                    "task_index": 1,
                },
                {
                    "observation.state": vector(4.0),
                    "action": vector(14.0),
                    "timestamp": 0.2,
                    "frame_index": 1,
                    "episode_index": 8,
                    "index": 4,
                    "task_index": 1,
                },
                {
                    "observation.state": vector(5.0),
                    "action": vector(15.0),
                    "timestamp": 0.4,
                    "frame_index": 2,
                    "episode_index": 8,
                    "index": 5,
                    "task_index": 1,
                },
            ]
        pq.write_table(pa.Table.from_pylist(rows), self.root / "data_chunk-000_file-000.parquet")
        self._write_manifest()

    def _write_manifest(self) -> None:
        file_names = (
            "intake_receipt.json",
            "meta_info.json",
            "meta_stats.json",
            "meta_tasks.parquet",
            "meta_episodes_chunk-000_file-000.parquet",
            "data_chunk-000_file-000.parquet",
        )
        files = []
        for name in file_names:
            path = self.root / name
            files.append(
                {
                    "relative_path": name,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        manifest = {
            "schema_version": "bridgedata-intake-v1",
            "source": {"upstream": "BridgeData V2"},
            "files": files,
            "initial_evaluation_design": {
                "source_partition": "one acquired data shard; split must be derived by episode_id, never random frame split",
                "input": ["observation.state[t]", "action[t]"],
                "target": "observation.state[t+1]",
            },
        }
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _config(self, **kwargs) -> BridgeDataTransitionConfig:
        values = {"selected_episode_indices": frozenset({7, 8}), "parquet_batch_size": 2}
        values.update(kwargs)
        return BridgeDataTransitionConfig(**values)

    def _derive(self, **kwargs):
        return derive_bridgedata_transitions(load_bridgedata_intake(self.manifest_path), self._config(**kwargs))

    def test_manifest_bound_extraction_is_episode_safe_and_deterministic(self):
        first = self._derive()
        second = self._derive()

        self.assertEqual(first, second)
        self.assertEqual(first.receipt.selected_episode_count, 2)
        self.assertEqual(first.receipt.selected_frame_count, 6)
        self.assertEqual(first.receipt.expected_selected_frame_count, 6)
        self.assertEqual(first.receipt.transition_count, 4)
        self.assertEqual(first.receipt.expected_unbounded_transition_count, 4)
        self.assertFalse(first.receipt.capped)
        self.assertEqual(first.receipt.rejected_cross_episode_pairs, 1)
        self.assertEqual(first.receipt.rejected_nonconsecutive_frame_pairs, 0)
        self.assertEqual(first.receipt.rejected_nonconsecutive_index_pairs, 0)
        self.assertEqual(first.receipt.rejected_timestamp_pairs, 0)
        self.assertEqual({item.episode_index for item in first.transitions}, {7, 8})
        self.assertTrue(
            all(
                item.target_index == item.source_index + 1
                and item.target_frame_index == item.source_frame_index + 1
                for item in first.transitions
            )
        )
        self.assertFalse(
            any(
                item.source_index == 2 and item.target_index == 3
                for item in first.transitions
            )
        )

    def test_cap_has_explicit_exact_coverage_semantics(self):
        dataset = self._derive(max_transitions=1)

        self.assertEqual(dataset.receipt.transition_count, 1)
        self.assertEqual(dataset.receipt.expected_unbounded_transition_count, 4)
        self.assertTrue(dataset.receipt.capped)
        self.assertEqual(dataset.receipt.selected_frame_count, 6)
        self.assertEqual(len(dataset.transitions), 1)

    def test_source_hash_drift_fails_before_parquet_open(self):
        with (self.root / "data_chunk-000_file-000.parquet").open("ab") as handle:
            handle.write(b"drift")

        with self.assertRaisesRegex(BridgeDataError, "byte count mismatch|SHA-256 mismatch"):
            load_bridgedata_intake(self.manifest_path)

    def test_unsupported_manifest_contract_is_refused(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["schema_version"] = "unknown-version"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(BridgeDataError, "schema_version"):
            load_bridgedata_intake(self.manifest_path)

    def test_skipped_frame_inside_selected_complete_episode_is_refused(self):
        rows = [
            {
                "observation.state": vector(0.0), "action": vector(10.0), "timestamp": 0.0,
                "frame_index": 0, "episode_index": 7, "index": 0, "task_index": 0,
            },
            {
                "observation.state": vector(1.0), "action": vector(11.0), "timestamp": 0.2,
                "frame_index": 2, "episode_index": 7, "index": 1, "task_index": 0,
            },
            {
                "observation.state": vector(2.0), "action": vector(12.0), "timestamp": 0.4,
                "frame_index": 3, "episode_index": 7, "index": 2, "task_index": 0,
            },
            {
                "observation.state": vector(3.0), "action": vector(13.0), "timestamp": 0.0,
                "frame_index": 0, "episode_index": 8, "index": 3, "task_index": 1,
            },
            {
                "observation.state": vector(4.0), "action": vector(14.0), "timestamp": 0.2,
                "frame_index": 1, "episode_index": 8, "index": 4, "task_index": 1,
            },
            {
                "observation.state": vector(5.0), "action": vector(15.0), "timestamp": 0.4,
                "frame_index": 2, "episode_index": 8, "index": 5, "task_index": 1,
            },
        ]
        self._write_valid_fixture(rows=rows)

        with self.assertRaisesRegex(BridgeDataError, "non-consecutive frame"):
            self._derive()

    def test_nonfinite_vector_is_refused_even_with_matching_source_hash(self):
        rows = [
            {
                "observation.state": [float("nan")] + vector(0.0)[1:], "action": vector(10.0), "timestamp": 0.0,
                "frame_index": 0, "episode_index": 7, "index": 0, "task_index": 0,
            },
            {
                "observation.state": vector(1.0), "action": vector(11.0), "timestamp": 0.2,
                "frame_index": 1, "episode_index": 7, "index": 1, "task_index": 0,
            },
            {
                "observation.state": vector(2.0), "action": vector(12.0), "timestamp": 0.4,
                "frame_index": 2, "episode_index": 7, "index": 2, "task_index": 0,
            },
            {
                "observation.state": vector(3.0), "action": vector(13.0), "timestamp": 0.0,
                "frame_index": 0, "episode_index": 8, "index": 3, "task_index": 1,
            },
            {
                "observation.state": vector(4.0), "action": vector(14.0), "timestamp": 0.2,
                "frame_index": 1, "episode_index": 8, "index": 4, "task_index": 1,
            },
            {
                "observation.state": vector(5.0), "action": vector(15.0), "timestamp": 0.4,
                "frame_index": 2, "episode_index": 8, "index": 5, "task_index": 1,
            },
        ]
        self._write_valid_fixture(rows=rows)

        with self.assertRaisesRegex(BridgeDataError, "finite"):
            self._derive()

    def test_unknown_episode_selection_is_refused(self):
        with self.assertRaisesRegex(BridgeDataError, "absent from frozen metadata"):
            derive_bridgedata_transitions(
                load_bridgedata_intake(self.manifest_path),
                BridgeDataTransitionConfig(selected_episode_indices=frozenset({99})),
            )

    def test_selected_episode_without_exact_task_catalog_mapping_is_refused(self):
        episode_path = self.root / "meta_episodes_chunk-000_file-000.parquet"
        rows = pq.read_table(episode_path).to_pylist()
        rows[0]["tasks"] = ["unmapped task"]
        pq.write_table(pa.Table.from_pylist(rows), episode_path)
        self._write_manifest()

        with self.assertRaisesRegex(BridgeDataError, "exact non-empty frozen task-table mapping"):
            self._derive()


if __name__ == "__main__":
    unittest.main(verbosity=2)
