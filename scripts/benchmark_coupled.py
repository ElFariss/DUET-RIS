"""Matched spatial and temporal comparisons on identical fully coupled truth."""
import argparse,json,time,os,platform,hashlib
from pathlib import Path
import numpy as np
import torch
from atomwise_ris.physics.network import CoupledNetwork
from atomwise_ris.models.coupled_policy import CoupledPolicy,LinkGRU
from atomwise_ris.models.forecast import predict
from atomwise_ris.optimization.coupled_search import search

def main():
 p=argparse.ArgumentParser();p.add_argument('--split',choices=['validation','pilot'],required=True);p.add_argument('--budgets',default='1,5,10,50,100');p.add_argument('--seeds',default='7,19,43');p.add_argument('--mode',choices=['spatial','temporal'],required=True);p.add_argument('--output');p.add_argument('--limit',type=int,default=0);a=p.parse_args()
 torch.set_num_threads(1);torch.set_num_interop_threads(1);cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
 root=Path('outputs/runs/coupled_wire_v1');gate=json.loads((root/'physics_gate.json').read_text())
 if not gate['passed']:raise ValueError('Physics gate failed')
 if a.split=='pilot' and not (root/'budget_selection.json').exists():raise ValueError('Freeze validation budget first')
 loads=np.array(gate['loads_real_ohm'])+1j*np.array(gate['loads_imag_ohm']);ds=np.load('data/processed/coupled_wire_v1/dataset.npz');z=ds['z']
 scale=np.load(root/'feature_scaling.npz');feature_scale=(scale['mean'],scale['std'])
 seeds=list(map(int,a.seeds.split(',')));budgets=list(map(float,a.budgets.split(',')))
 policies={};forecasters={}
 for seed in seeds:
  for kind in ['mlp','attention','attention_no_physics']:
   ck=torch.load(root/'models'/f'{kind}_seed{seed}'/'best.pt',map_location='cpu',weights_only=True)
   m=CoupledPolicy(kind='mlp' if kind=='mlp' else 'attention',physics=kind!='attention_no_physics');m.load_state_dict(ck['state_dict']);m.eval()
   def call(x,g,m=m):
    with torch.inference_mode():return m(torch.tensor(x,dtype=torch.float32)[None],torch.tensor(g,dtype=torch.float32)[None])[0].numpy()
   policies[kind,seed]=call
  if a.mode=='temporal':
   base=root/'models'/f'gru_seed{seed}';ck=torch.load(base/'best.pt',map_location='cpu',weights_only=True);m=LinkGRU();m.load_state_dict(ck['state_dict']);m.eval();sc=np.load(base/'scaling.npz');forecasters[seed]=(m,(sc['mean'],sc['scale'],sc['upper']))
 methods=['greedy','pair','blind_pair','random','memory_ga','analytical_ga','mlp_ga','attention_ga','attention_no_physics_ga','attention_no_memory_ga'] if a.mode=='spatial' else ['persistence_pair','linear_pair','gru_pair','oracle_pair','persistence_mlp_ga','gru_mlp_ga','persistence_attention_ga','gru_attention_ga']
 indices=np.flatnonzero((ds['split']==a.split)&((ds['step']>=4) if a.mode=='temporal' else True))
 if a.limit:indices=indices[:a.limit]
 # Train-only warmup. Forecasts never see the target frame.
 warm=CoupledNetwork(z[4],loads);st=warm.state(np.zeros(64,np.int8));x,g=warm.features(st)
 for policy in policies.values():policy((x-feature_scale[0])/feature_scale[1],g/max(np.std(g),1e-4))
 for m,sc in forecasters.values():predict(z[:4],'gru',m,sc)
 dest=root/(a.output or f'benchmark_{a.mode}_{a.split}.jsonl')
 if dest.exists():raise FileExistsError(dest)
 metadata={'args':vars(a),'hostname':platform.node(),'cpu_affinity':[cpu],'numpy':np.__version__,'torch':torch.__version__,'methods':methods,'threads':1,'seeds':seeds,'budgets':budgets,'data_sha256':hashlib.sha256(Path('data/processed/coupled_wire_v1/dataset.npz').read_bytes()).hexdigest(),'timing_includes':['forecast/history preprocessing','passivity projection','fixed reference precoder','network contraction','memory retrieval/rescoring/write','features','inference','candidate evaluation'],'timing_excludes':['one-time model load','train-case warmup','EM generation','channel acquisition','environmental rescore of chosen action','disk IO'],'csi_age_s':.02 if a.mode=='temporal' else 0,'history_frames':4 if a.mode=='temporal' else 0,'oracle':'current impedance with shared stale-reference precoder' if a.mode=='temporal' else None,'incident_source_wave_power_w':.1,'pilot_is_development':True}
 dest.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n');order=np.random.default_rng(9901)
 with dest.open('w') as f:
  for budget in budgets:
   for seed in seeds:
    memory={m:[] for m in methods};last_tr=None
    for idx in indices:
     trajectory=int(ds['trajectory'][idx])
     if trajectory!=last_tr:memory={m:[] for m in methods};last_tr=trajectory
     for method in order.permutation(methods):
      start=time.perf_counter_ns();deadline=start+int(budget*1e6);mname=str(method);prediction_ms=0.
      if a.mode=='temporal':
       forecast,controller=mname.split('_',1)
       # Same stale observed reference precoder for all causal methods and oracle.
       w=CoupledNetwork(z[idx-1],loads).w
       pt=time.perf_counter_ns()
       if forecast=='oracle':belief=z[idx]
       else:
        model,sc=forecasters[seed];belief=predict(z[idx-4:idx],forecast,model,sc)
       prediction_ms=(time.perf_counter_ns()-pt)/1e6
       ev=CoupledNetwork(belief,loads,w=w)
      else:
       controller=mname;w=CoupledNetwork(z[idx],loads).w
       ev=CoupledNetwork(z[idx],loads,w=w,coupled=mname!='blind_pair')
       if mname=='blind_pair':controller='pair'
      prep_ms=(time.perf_counter_ns()-start)/1e6
      kind=controller.removesuffix('_ga');kind='attention' if kind=='attention_no_memory' else kind
      policy=policies.get((kind,seed));actual='attention_ga' if controller in ['attention_no_memory_ga','attention_no_physics_ga'] else controller
      bits,value,evaluations,breakdown=search(ev,actual,deadline,seed*10000+int(idx),memory=() if controller=='attention_no_memory_ga' else memory[mname],policy=policy,scaling=feature_scale)
      mt=time.perf_counter_ns();memory[mname]=[bits.copy()]+[b for b in memory[mname] if not np.array_equal(b,bits)][:7];memory_ms=(time.perf_counter_ns()-mt)/1e6
      elapsed=(time.perf_counter_ns()-start)/1e6
      full=float(ev.score(ev.channel(bits)@w))
      if abs(full-value)>1e-7:raise AssertionError('Cached and full channel disagree')
      truth=CoupledNetwork(z[idx],loads,w=w);rate=float(truth.score(truth.channel(bits)@w))
      row={'mode':a.mode,'split':a.split,'method':mname,'seed':seed,'budget_ms':budget,'index':int(idx),'trajectory':trajectory,'step':int(ds['step'][idx]),'rate':rate,'belief_rate':value,'elapsed_ms':elapsed,'deadline_missed':elapsed>budget,'evaluations':evaluations,'bits':bits.tolist(),'breakdown_ms':breakdown|{'preparation_ms':prep_ms,'forecast_ms':prediction_ms,'memory_write_ms':memory_ms}}
      f.write(json.dumps(row)+'\n');f.flush()
   print(a.mode,a.split,'completed',budget,flush=True)
if __name__=='__main__':main()
