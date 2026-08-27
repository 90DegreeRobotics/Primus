"""Tests for train-only temporal-context normalization receipts."""
from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/"src"))
from world_data.ingestion import ingest_world_dataset
from world_data.normalization import NormalizationError, fit_train_only_normalization
from world_data.temporal_witness import derive_temporal_witnesses
from world_schema.model import HoldoutSplit
from world_schema.trajectory_generator import TrajectoryGeneratorConfig, write_dataset

class NormalizationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); r=write_dataset(Path(self.temp.name)/"d",TrajectoryGeneratorConfig(seed=752,train_count=16,held_out_object_count=2,held_out_operation_count=2,held_out_composition_count=2)); self.data=ingest_world_dataset(r.dataset_path,r.manifest_path); self.all=derive_temporal_witnesses(self.data); self.train=tuple(w for w in self.all if w.split is HoldoutSplit.TRAIN)
 def tearDown(self): self.temp.cleanup()
 def test_train_receipt_round_trips_features_and_position(self):
  receipt=fit_train_only_normalization(self.train); w=self.train[0]; self.assertEqual(tuple(round(x,9) for x in receipt.denormalize_position_target(receipt.normalize_position_target(w.target_vector[:3]))),tuple(round(x,9) for x in w.target_vector[:3])); self.assertEqual(receipt.train_witness_count,len(self.train)); self.assertEqual(len(receipt.sha256()),64)
 def test_holdout_witness_refuses_fit(self):
  with self.assertRaisesRegex(NormalizationError,"only the train partition"): fit_train_only_normalization(self.all)
if __name__=='__main__': unittest.main(verbosity=2)
