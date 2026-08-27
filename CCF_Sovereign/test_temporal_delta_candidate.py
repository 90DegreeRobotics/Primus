from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from train_temporal_context import TemporalContextMLP
from train_temporal_delta import fit,predict,train_only
from world_data.delta_witness import derive_delta_witnesses
from world_data.ingestion import ingest_world_dataset
from world_metrics.state_transitions import score_state_transition_predictions
from world_schema.trajectory_generator import TrajectoryGeneratorConfig,write_dataset
class DeltaCandidateTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();r=write_dataset(Path(self.t.name)/'d',TrajectoryGeneratorConfig(seed=802,train_count=20,held_out_object_count=3,held_out_operation_count=3,held_out_composition_count=3));self.d=ingest_world_dataset(r.dataset_path,r.manifest_path);self.all=derive_delta_witnesses(self.d);self.train=tuple(x for x in self.all if x.split=='train')
 def tearDown(self):self.t.cleanup()
 def test_delta_output_composes_exact_coverage(self):
  torch.manual_seed(802);m=TemporalContextMLP(16);loss,updates,_=fit(m,self.train,device=torch.device('cpu'),epochs=8,batch_size=4,learning_rate=.01);self.assertGreaterEqual(loss,0);self.assertGreater(updates,0);p=predict(m,self.all,device=torch.device('cpu'));self.assertEqual(set(p),{x.program_id for x in self.all});self.assertEqual(score_state_transition_predictions(self.d,p).prediction_count,len(self.all))
 def test_delta_fit_refuses_holdouts(self):
  with self.assertRaisesRegex(ValueError,'only the train partition'):train_only(self.all)
if __name__=='__main__':unittest.main(verbosity=2)
