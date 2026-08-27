from __future__ import annotations
import json,sys,time
from pathlib import Path
from typing import Iterable
import torch
import torch.nn.functional as F
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from train_temporal_context import TemporalContextMLP,parse_args,resolve_device,seed_everything
from training.candidate_run import CandidateRun,atomic_write_json,sha256_file
from world_data.delta_witness import DeltaWitness,derive_delta_witnesses,delta_witness_set_sha256
from world_data.ingestion import WorldIngestionConfig,ingest_world_dataset
from world_data.temporal_witness import CONTEXT_INPUT_FEATURE_NAMES,derive_temporal_witnesses
from world_metrics.state_transitions import StateTransitionPrediction,score_state_transition_predictions,static_no_change_baseline

def train_only(w:Iterable[DeltaWitness]):
 x=tuple(w)
 if not x: raise ValueError('training delta witnesses cannot be empty')
 if any(v.split!='train' for v in x): raise ValueError('delta training accepts only the train partition')
 return x
def ft(w,device): return torch.tensor([x.context_input_vector for x in w],dtype=torch.float32,device=device)
def tt(w,device): return torch.tensor([x.target_vector for x in w],dtype=torch.float32,device=device)
def fit(model,w,*,device,epochs,batch_size,learning_rate):
 train=train_only(w);x,y=ft(train,device),tt(train,device);opt=torch.optim.AdamW(model.parameters(),lr=learning_rate,weight_decay=0.0);start=time.perf_counter();updates=0;loss=float('nan');model.train()
 for _ in range(epochs):
  for i in range(0,len(train),batch_size):
   out=model(x[i:i+batch_size]);loss=F.mse_loss(out[:,:3],y[i:i+batch_size,:3])+F.binary_cross_entropy_with_logits(out[:,3:],y[i:i+batch_size,3:])
   if not torch.isfinite(loss):raise RuntimeError('delta loss became non-finite')
   opt.zero_grad(set_to_none=True);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step();updates+=1
 return float(loss.detach().cpu()),updates,time.perf_counter()-start
def predict(model,w,*,device):
 allw=tuple(w);model.eval()
 with torch.no_grad():out=model(ft(allw,device)).detach().cpu()
 result={}
 for v,row in zip(allw,out):
  if v.program_id in result:raise ValueError('duplicate delta witness ID')
  source=v.context_input_vector[:3];delta=tuple(float(k) for k in row[:3]);result[v.program_id]=StateTransitionPrediction(program_id=v.program_id,target_translation_mm=tuple((source[i]+delta[i])*1000 for i in range(3)),support_present_after=bool(torch.sigmoid(row[3])>=.5),near_present_after=bool(torch.sigmoid(row[4])>=.5))
 return result
def ev(p):return {'path':str(p),'sha256':sha256_file(p),'bytes':p.stat().st_size}
def writep(p,items):atomic_write_json(p,{'prediction_count':len(items),'prediction_input_feature_names':list(CONTEXT_INPUT_FEATURE_NAMES),'predictions':[items[k].to_dict() for k in sorted(items)]})
def writer(p,r):d=r.to_dict();d['report_sha256']=r.sha256();atomic_write_json(p,d)
def main(argv=None):
 a=parse_args(argv);seed_everything(a.seed);device=resolve_device(a.device);dataset,manifest=Path(a.dataset).resolve(),Path(a.manifest).resolve();ing=ingest_world_dataset(dataset,manifest,WorldIngestionConfig(segment_length=256,segment_stride=255,batch_size=a.batch_size));dw=derive_delta_witnesses(ing);train=tuple(v for v in dw if v.split=='train');train_only(train);run=None
 try:
  run=CandidateRun.create(project_root=ROOT,candidate_id=a.candidate_id,seed=a.seed,additional_frozen_inputs={'world_dataset_jsonl':(dataset,sha256_file(dataset)),'world_dataset_manifest':(manifest,sha256_file(manifest))});cfg={'experiment_kind':'generated_temporal_delta_representation_ablation','input_feature_names':list(CONTEXT_INPUT_FEATURE_NAMES),'delta_is_output_only':True,'excluded_input_feature_classes':['target_translation','action_delta','target_relations','partition','object_class','operation_family','program_id','source_hash','evidence_uri'],'model':'mlp_8_32_32_5','fixed_budget_reference':'temporal-context-20260827-0742-mlp','delta_witness_set_sha256':delta_witness_set_sha256(dw),'no_world_model_claim':True,'no_automatic_promotion':True};run.mark_training_started(config=cfg,turns=len(train),epochs=a.epochs,batch_size=a.batch_size,max_sequence_length=8,device=str(device));model=TemporalContextMLP(a.hidden_width).to(device);base=static_no_change_baseline(ing);br=score_state_transition_predictions(ing,base,position_tolerance_mm=a.position_tolerance_mm);loss,updates,elapsed=fit(model,train,device=device,epochs=a.epochs,batch_size=a.batch_size,learning_rate=a.learning_rate);pred=predict(model,dw,device=device);cr=score_state_transition_predictions(ing,pred,position_tolerance_mm=a.position_tolerance_mm);paths={n:run.assert_candidate_output(run.candidate_dir/f) for n,f in {'baseline_predictions':'baseline_predictions.json','baseline_metrics':'baseline_metrics.json','candidate_predictions':'candidate_predictions.json','candidate_metrics':'candidate_metrics.json','run_summary':'temporal_delta_run.json'}.items()};writep(paths['baseline_predictions'],base);writer(paths['baseline_metrics'],br);writep(paths['candidate_predictions'],pred);writer(paths['candidate_metrics'],cr);atomic_write_json(paths['run_summary'],{'candidate_id':a.candidate_id,'code_commit':run.manifest['code_commit'],'target_manifest_sha256':ing.receipt.manifest_sha256,'delta_witness_set_sha256':delta_witness_set_sha256(dw),'train_count':len(train),'total_count':len(dw),'training':{'epochs':a.epochs,'batch_size':a.batch_size,'learning_rate':a.learning_rate,'hidden_width':a.hidden_width,'updates':updates,'last_loss':loss,'elapsed_seconds':elapsed},'claims':{'generated_delta_rule_tested':True,'observed_world_dynamics_proven':False,'candidate_promoted':False}});ck=run.save_checkpoint({'model_state_dict':model.state_dict(),'candidate_id':a.candidate_id,'config':cfg},epoch=a.epochs,metrics={'last_loss':loss,'updates':updates,'baseline_metrics_sha256':br.sha256(),'candidate_metrics_sha256':cr.sha256(),'run_summary':ev(paths['run_summary'])});run.mark_completed();print(json.dumps({'candidate_id':a.candidate_id,'checkpoint':ev(ck),'candidate_metrics':ev(paths['candidate_metrics']),'promotion_performed':False},indent=2));return 0
 except BaseException as e:
  if run is not None:run.mark_failed(e)
  raise
if __name__=='__main__':raise SystemExit(main())
