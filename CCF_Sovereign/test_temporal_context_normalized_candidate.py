"""Focused tests for normalized temporal-context candidate functions."""
from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/"src"))
from train_temporal_context import TemporalContextMLP
from train_temporal_context_normalized import normalized_predictions, train_normalized_model
from world_data.ingestion import ingest_world_dataset
from world_data.normalization import fit_train_only_normalization
from world_data.temporal_witness import derive_temporal_witnesses
from world_metrics.state_transitions import score_state_transition_predictions
from world_schema.model import HoldoutSplit
from world_schema.trajectory_generator import TrajectoryGeneratorConfig, write_dataset
class NormalizedCandidateTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); r=write_dataset(Path(self.temp.name)/"d",TrajectoryGeneratorConfig(seed=753,train_count=20,held_out_object_count=3,held_out_operation_count=3,held_out_composition_count=3)); self.data=ingest_world_dataset(r.dataset_path,r.manifest_path); self.all=derive_temporal_witnesses(self.data); self.train=tuple(w for w in self.all if w.split is HoldoutSplit.TRAIN); self.receipt=fit_train_only_normalization(self.train)
 def tearDown(self): self.temp.cleanup()
 def test_normalized_model_emits_exact_coverage(self):
  torch.manual_seed(753); model=TemporalContextMLP(16); loss,updates,_=train_normalized_model(model,self.train,self.receipt,device=torch.device("cpu"),epochs=8,batch_size=4,learning_rate=.01); self.assertGreaterEqual(loss,0); self.assertGreater(updates,0); predictions=normalized_predictions(model,self.all,self.receipt,device=torch.device("cpu")); self.assertEqual(set(predictions),{w.program_id for w in self.all}); self.assertEqual(score_state_transition_predictions(self.data,predictions).prediction_count,len(self.all))
 def test_normalized_training_rejects_holdouts(self):
  with self.assertRaisesRegex(ValueError,"only the train partition"): train_normalized_model(TemporalContextMLP(8),self.all,self.receipt,device=torch.device("cpu"),epochs=1,batch_size=4,learning_rate=.01)
if __name__=='__main__': unittest.main(verbosity=2)
