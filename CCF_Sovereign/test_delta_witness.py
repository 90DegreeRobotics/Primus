from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from world_data.delta_witness import derive_delta_witnesses,delta_witness_set_sha256
from world_data.ingestion import ingest_world_dataset
from world_data.temporal_witness import CONTEXT_INPUT_FEATURE_NAMES
from world_schema.trajectory_generator import TrajectoryGeneratorConfig,write_dataset
class DeltaWitnessTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();r=write_dataset(Path(self.t.name)/'d',TrajectoryGeneratorConfig(seed=801,train_count=12,held_out_object_count=2,held_out_operation_count=2,held_out_composition_count=2));self.d=ingest_world_dataset(r.dataset_path,r.manifest_path);self.w=derive_delta_witnesses(self.d)
 def tearDown(self):self.t.cleanup()
 def test_delta_recomposes_final_translation_and_preserves_splits(self):
  records={r.program.program_id:r for r in self.d.records};self.assertEqual({x.split for x in self.w},{'train','held_out_object_class','held_out_operation_family','held_out_composition'})
  for x in self.w:
   source=next(e for e in records[x.program_id].program.entities if e.entity_id=='entity_subject').transform.translation_mm
   params=next(o for o in records[x.program_id].program.operations if o.operation_id=='operation_move').parameters
   target=tuple(params[key] for key in ('delta_x_mm','delta_y_mm','delta_z_mm'))
   self.assertEqual(tuple(round(source[i]/1000+x.delta_target_m[i],9) for i in range(3)),tuple(round((source[i]+target[i])/1000,9) for i in range(3)))
 def test_context_contract_has_no_delta_or_target(self):
  self.assertFalse(any('delta' in name or 'target' in name for name in CONTEXT_INPUT_FEATURE_NAMES));self.assertEqual(len(delta_witness_set_sha256(self.w)),64)
if __name__=='__main__':unittest.main(verbosity=2)
