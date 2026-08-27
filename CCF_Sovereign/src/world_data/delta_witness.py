"""Manifest-bound delta-output witnesses for generated temporal context."""
from __future__ import annotations
import hashlib,json,math
from dataclasses import dataclass
from typing import Iterable
from world_data.ingestion import IngestedWorldDataset
from world_data.temporal_witness import CONTEXT_INPUT_FEATURE_NAMES,TemporalStateWitness,derive_temporal_witnesses

DELTA_TARGET_FEATURE_NAMES=('delta_x_m','delta_y_m','delta_z_m','support_present_after','near_present_after')
class DeltaWitnessError(ValueError): pass
@dataclass(frozen=True)
class DeltaWitness:
 program_id:str; split:str; context_input_vector:tuple[float,...]; delta_target_m:tuple[float,float,float]; support_present_after:bool; near_present_after:bool; target_evidence_kinds:tuple[str,...]
 @property
 def target_vector(self): return (*self.delta_target_m,float(self.support_present_after),float(self.near_present_after))
 def validate(self):
  if not self.program_id or self.split not in {'train','held_out_object_class','held_out_operation_family','held_out_composition'}: raise DeltaWitnessError('invalid witness identity or split')
  if len(self.context_input_vector)!=len(CONTEXT_INPUT_FEATURE_NAMES) or not all(math.isfinite(x) for x in self.context_input_vector): raise DeltaWitnessError('invalid context input')
  if len(self.delta_target_m)!=3 or not all(math.isfinite(x) for x in self.delta_target_m): raise DeltaWitnessError('invalid delta target')
  if not self.target_evidence_kinds or any(k not in {'generated','inferred'} for k in self.target_evidence_kinds): raise DeltaWitnessError('invalid generated evidence kinds')
def derive_delta_witness(w:TemporalStateWitness)->DeltaWitness:
 w.validate(); source=w.context_input_vector[:3]; target=w.target_translation_mm
 # temporal target is millimetres; convert before subtraction
 delta=tuple((target[i]/1000.0)-source[i] for i in range(3))
 result=DeltaWitness(w.program_id,w.split.value,w.context_input_vector,delta,w.support_present_after,w.near_present_after,w.target_evidence_kinds); result.validate(); return result
def derive_delta_witnesses(ingested:IngestedWorldDataset)->tuple[DeltaWitness,...]:
 result=tuple(derive_delta_witness(w) for w in derive_temporal_witnesses(ingested))
 if len({w.program_id for w in result})!=len(result): raise DeltaWitnessError('duplicate program ID')
 return result
def delta_witness_set_sha256(witnesses:Iterable[DeltaWitness])->str:
 rows=[]
 for w in sorted(tuple(witnesses),key=lambda x:x.program_id):
  w.validate(); rows.append({'id':w.program_id,'split':w.split,'context':w.context_input_vector,'target':w.target_vector,'evidence':w.target_evidence_kinds})
 return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
