"""Matched spatial and temporal comparisons on identical fully coupled truth."""
import argparse,json,time,os,platform,hashlib
from pathlib import Path
import numpy as np
import torch
from atomwise_ris.physics.network import CoupledNetwork
from atomwise_ris.models.coupled_policy import CoupledPolicy,LinkGRU
from atomwise_ris.models.forecast import predict,require_forecast_checkpoint
from atomwise_ris.optimization.coupled_search import search
from atomwise_ris.optimization.search import load_search_config,Memory,ME_GA_METHODS
from select_matched_budget import load_protocol,protocol_methods,frozen_code_hashes,checkpoint_hashes,host_state,require_frozen_selection,sha256_file
from run_improvement_campaign import validate_validation_rows

def should_store_memory(method):
 # ME-GA family keeps its own memory Psi inside the controller (timed there); no post-hoc overwrite
 return method not in {'greedy','pair','random','blind_pair','population_ga','ga_risc','me_ga','me_ga_paper'} and 'no_memory' not in method

def validate_primary_selection(selection,protocol,protocol_hash,root,dataset,data_path,gate_path):
 path=root/'benchmark_spatial_validation.jsonl'
 if selection.get('protocol_sha256')!=protocol_hash:raise RuntimeError('Test is blocked: budget selection was made under another protocol')
 if (selection.get('protocol_primary_ms')!=protocol.get('primary_budget_ms')
     or selection.get('protocol_preferred_ms')!=protocol.get('preferred_budget_ms',protocol.get('primary_budget_ms'))
     or selection.get('budget_lock')!=protocol.get('budget_lock')):raise RuntimeError('Test is blocked: budget selection primary/preferred lock differs from protocol')
 if not path.exists() or selection.get('input_hashes',{}).get(path.name)!=sha256_file(path):raise RuntimeError('Test is blocked: frozen validation JSONL is missing or its hash changed')
 meta_path=path.with_suffix('.json')
 if not meta_path.exists():raise RuntimeError('Test is blocked: frozen validation metadata sidecar is missing')
 meta=json.loads(meta_path.read_text())
 if (meta.get('protocol_sha256')!=protocol_hash or meta.get('data_sha256')!=sha256_file(data_path)
     or meta.get('physics_gate_sha256')!=sha256_file(gate_path)
     or meta.get('conditional_pair_policy',False)
     or meta.get('selection_helper_sha256')!=sha256_file(Path(__file__).with_name('select_matched_budget.py'))
     or meta.get('campaign_script_sha256')!=sha256_file(Path(__file__).with_name('run_improvement_campaign.py'))
     or meta.get('frozen_code_sha256')!=selection.get('code_sha256')
     or meta.get('checkpoint_sha256')!=selection.get('checkpoint_sha256')):raise RuntimeError('Test is blocked: validation sidecar source/checkpoint identity differs from selection')
 rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
 expected=set(map(int,np.flatnonzero(dataset['split']=='validation')))
 validate_validation_rows(rows,protocol_methods(protocol),protocol['seeds'],protocol['budgets_ms'],expected,
                          protocol['primary_budget_ms'],selected_budget=selection.get('selected_ms'))

def main():
 p=argparse.ArgumentParser();p.add_argument('--split',choices=['validation','pilot','test'],required=True);p.add_argument('--budgets',default=None);p.add_argument('--seeds',default=None);p.add_argument('--mode',choices=['spatial','temporal'],required=True);p.add_argument('--output');p.add_argument('--limit',type=int,default=0);p.add_argument('--conditional-pair-policy',action='store_true')
 p.add_argument('--extra-methods',default='',help='comma list from me_ga,ga_risc,me_ga_paper (Zardi et al. reimplementation); spatial mode only, never part of the registered protocol')
 p.add_argument('--run',default=None,help='default: outputs/runs/coupled_wire_v1; with --matched the protocol run');p.add_argument('--data',default='data/processed/coupled_wire_v1/dataset.npz',help='train/validation (and legacy pilot) dataset')
 p.add_argument('--matched',action='store_true',help='run the registered matched protocol (methods, seeds, budgets, shared search config)')
 p.add_argument('--protocol',default='configs/experiments/matched_v1.json');p.add_argument('--search-config',choices=['small','medium','large'],default=None)
 p.add_argument('--test-data',default=None,help='dataset.npz (or its directory) holding the test frames; --data stays train/validation only')
 p.add_argument('--physics-gate',default=None,help='default: <run>/physics_gate.json, else outputs/runs/coupled_wire_v1/physics_gate.json (same physics)');a=p.parse_args()
 if not a.matched:
  if a.split=='test' or a.test_data or a.search_config or a.conditional_pair_policy:raise SystemExit('--split test, --test-data, --search-config and conditional policy require --matched')
  a.budgets=a.budgets or '1,5,10,50,100';a.seeds=a.seeds or '7,19,43'
 else:
  if a.mode!='spatial':raise SystemExit('The matched protocol is spatial control only')
  a.search_config=a.search_config or 'medium'
 if a.split=='test' and (not a.test_data or a.search_config!='medium' or a.limit or a.budgets or a.seeds):raise SystemExit('Test split needs --test-data, the primary (medium) config, the full protocol seeds/budgets and no --limit')
 if a.split=='test' and a.conditional_pair_policy:raise SystemExit('Conditional-pair policy is development-only')
 if a.test_data and a.split!='test':raise SystemExit('--test-data is only for --split test')
 extras=[m for m in a.extra_methods.split(',') if m]
 if set(extras)-set(ME_GA_METHODS):raise SystemExit(f'--extra-methods must be among {ME_GA_METHODS}')
 if extras and (a.split=='test' or not a.output or a.mode!='spatial'):raise SystemExit('--extra-methods needs --mode spatial, an explicit --output and is not allowed for --split test')
 a.run=a.run or (load_protocol(a.protocol)[0]['experiments']['coupled']['run'] if a.matched else 'outputs/runs/coupled_wire_v1')
 torch.set_num_threads(1);torch.set_num_interop_threads(1);cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
 root=Path(a.run);root.mkdir(parents=True,exist_ok=True)
 gate_path=Path(a.physics_gate) if a.physics_gate else (root/'physics_gate.json' if (root/'physics_gate.json').exists() else Path('outputs/runs/coupled_wire_v1/physics_gate.json'))
 gate=json.loads(gate_path.read_text())
 if not gate['passed']:raise ValueError('Physics gate failed')
 if a.split=='pilot' and not (root/'budget_selection.json').exists():raise ValueError('Freeze validation budget first')
 protocol=protocol_hash=cfg=selection=None
 if a.matched:
  protocol,protocol_hash=load_protocol(a.protocol);cfg=load_search_config(a.search_config,a.protocol)
  if a.split=='test':selection=require_frozen_selection(root)
 loads=np.array(gate['loads_real_ohm'])+1j*np.array(gate['loads_imag_ohm']);ds=np.load(a.data);z=ds['z']
 if a.matched and a.split=='test':validate_primary_selection(selection,protocol,protocol_hash,root,ds,a.data,gate_path)
 test_hash=None;frame_rule=f'split=={a.split}'
 if a.test_data:   # frame set only; z/ds above (train+validation) feed warm-up and nothing else
  tp=Path(a.test_data);tp=tp/'dataset.npz' if tp.is_dir() else tp
  fs=np.load(tp);test_hash=sha256_file(tp)
 else:fs=ds
 fz=fs['z']
 scale=np.load(root/'feature_scaling.npz');feature_scale=(scale['mean'],scale['std'])
 if a.matched:
  seeds=list(protocol['seeds']);budgets=[float(x) for x in protocol['budgets_ms']]
  if a.seeds:
   seeds=list(map(int,a.seeds.split(',')))
   if not set(seeds)<=set(protocol['seeds']):raise SystemExit('Seeds must be a subset of the protocol seeds')
  if a.budgets:
   budgets=list(map(float,a.budgets.split(',')))
   if not set(budgets)<=set(float(x) for x in protocol['budgets_ms']):raise SystemExit('Budgets must be a subset of the protocol budgets')
 else:seeds=list(map(int,a.seeds.split(',')));budgets=list(map(float,a.budgets.split(',')))
 policies={};forecasters={}
 for seed in seeds:
  for kind in ['mlp','attention','attention_no_physics']:
   ck=torch.load(root/'models'/f'{kind}_seed{seed}'/'best.pt',map_location='cpu',weights_only=True)
   m=CoupledPolicy(kind='mlp' if kind=='mlp' else 'attention',physics=kind!='attention_no_physics');m.load_state_dict(ck['state_dict']);m.eval()
   def call(x,g,m=m):
    with torch.inference_mode():return m(torch.tensor(x,dtype=torch.float32)[None],torch.tensor(g,dtype=torch.float32)[None])[0].numpy()
   policies[kind,seed]=call
  if a.mode=='temporal':
   base=root/'models'/f'gru_seed{seed}';ck=torch.load(base/'best.pt',map_location='cpu',weights_only=True);require_forecast_checkpoint(ck);m=LinkGRU();m.load_state_dict(ck['state_dict']);m.eval();sc=np.load(base/'scaling.npz');act=sc['active_mask'] if 'active_mask' in sc else None;forecasters[seed]=(m,(sc['mean'],sc['scale'],sc['upper'],act))
 if a.matched:methods=protocol_methods(protocol)
 else:methods=['greedy','pair','blind_pair','random','population_ga','memory_ga','analytical_ga','mlp_ga','attention_ga','attention_no_physics_ga','attention_no_memory_ga'] if a.mode=='spatial' else ['persistence_pair','linear_pair','gru_pair','oracle_pair','persistence_mlp_ga','gru_mlp_ga','persistence_attention_ga','gru_attention_ga']
 methods=methods+[m for m in extras if m not in methods]
 if a.test_data and not np.any(fs['split']==a.split):indices=np.arange(len(fz));frame_rule='all frames of the test dataset'
 else:indices=np.flatnonzero((fs['split']==a.split)&((fs['step']>=4) if a.mode=='temporal' else True))
 if a.limit:indices=indices[:a.limit]
 # Train-only warmup. Forecasts never see the target frame.
 warm=CoupledNetwork(z[4],loads);st=warm.state(np.zeros(64,np.int8));x,g=warm.features(st)
 for policy in policies.values():policy((x-feature_scale[0])/feature_scale[1],g/max(np.std(g),1e-4))
 for m,sc in forecasters.values():predict(z[:4],'gru',m,sc)
 skw={'config':cfg} if a.matched else {'legacy':True}
 for pol in list(policies.values())[:1]:search(warm,'attention_ga',time.perf_counter_ns()+10_000_000,1,policy=pol,scaling=feature_scale,**skw)
 search(warm,'greedy',time.perf_counter_ns()+10_000_000,1,**skw)
 if a.matched:   # calibrate each policy's cost on the TRAIN case so the controller can keep neural overhead inside the deadline
  for call in policies.values():
   ts=[]
   for _ in range(23):
    t0=time.perf_counter_ns();x,g=warm.features(st);call((x-feature_scale[0])/feature_scale[1],g/max(np.std(g),1e-4));ts.append((time.perf_counter_ns()-t0)/1e6)
   call.expected_ms=float(np.percentile(ts[3:],90))
 if a.matched:   # warm every controller path once on the train case; results discarded
  for mth in methods:
   kind=mth.removesuffix('_ga');kind='attention' if kind=='attention_no_memory' else kind
   method_kw={} if mth=='population_ga' else skw|({'conditional_pair_policy':True} if a.conditional_pair_policy else {})
   search(warm,mth,time.perf_counter_ns()+10_000_000,1,memory=(),policy=next((v for (kk,_),v in policies.items() if kk==kind),None),scaling=feature_scale,**method_kw)
 suffix='' if not a.matched or a.search_config=='medium' else f'_{a.search_config}'
 dest=root/(a.output or f'benchmark_{a.mode}_{a.split}{suffix}.jsonl')
 if dest.exists() or (a.split=='test' and dest.with_suffix('.json').exists()):raise FileExistsError(dest)
 metadata={'args':vars(a),'hostname':platform.node(),'cpu_affinity':[cpu],'numpy':np.__version__,'torch':torch.__version__,'methods':methods,'threads':1,'seeds':seeds,'budgets':budgets,'data_sha256':hashlib.sha256(Path(a.data).read_bytes()).hexdigest(),'timing_includes':['forecast/history preprocessing','passivity projection','fixed reference precoder','network contraction','memory retrieval/rescoring/write','features','inference','candidate evaluation'],'timing_excludes':['one-time model load','train-case warmup','EM generation','channel acquisition','environmental rescore of chosen action','disk IO'],'csi_age_s':.02 if a.mode=='temporal' else 0,'history_frames':4 if a.mode=='temporal' else 0,'oracle':'current impedance with shared stale-reference precoder' if a.mode=='temporal' else None,'incident_source_wave_power_w':.1,'pilot_is_development':a.split!='test',
 'policy_expected_ms':{f'{kk}_seed{sd}':getattr(call,'expected_ms',None) for (kk,sd),call in policies.items()},'matched':a.matched,'conditional_pair_policy':bool(a.conditional_pair_policy),'frame_rule':frame_rule,'n_frames':int(len(indices)),'physics_gate':str(gate_path),'physics_gate_sha256':sha256_file(gate_path),'selection_helper_sha256':sha256_file(Path(__file__).with_name('select_matched_budget.py')),'campaign_script_sha256':sha256_file(Path(__file__).with_name('run_improvement_campaign.py')),'run':str(root)}
 if a.matched:metadata.update({'protocol_sha256':protocol_hash,'search_config':a.search_config,'search_config_values':{'specular':cfg.specular,'coupled':cfg.coupled,'all_variants':cfg.shared},'frozen_code_sha256':frozen_code_hashes(),'checkpoint_sha256':checkpoint_hashes(root),'test_data_sha256':test_hash,'budget_selection':selection,**host_state()})
 dest.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n');order=np.random.default_rng(9901)
 with dest.open('w') as f:
  for budget in budgets:
   for seed in seeds:
    memory={m:(Memory() if m in ME_GA_METHODS else []) for m in methods};last_tr=None
    for idx in indices:
     trajectory=int(fs['trajectory'][idx])
     if trajectory!=last_tr:memory={m:(Memory() if m in ME_GA_METHODS else []) for m in methods};last_tr=trajectory
     for method in order.permutation(methods):
      start=time.perf_counter_ns();deadline=start+int(budget*1e6);mname=str(method);prediction_ms=0.
      if a.mode=='temporal':
       forecast,controller=mname.split('_',1)
       # Same stale observed reference precoder for all causal methods and oracle.
       w=CoupledNetwork(fz[idx-1],loads).w
       pt=time.perf_counter_ns()
       if forecast=='oracle':belief=fz[idx]
       else:
        model,sc=forecasters[seed];belief=predict(fz[idx-4:idx],forecast,model,sc)
       prediction_ms=(time.perf_counter_ns()-pt)/1e6
       ev=CoupledNetwork(belief,loads,w=w)
      else:
       controller=mname;w=CoupledNetwork(fz[idx],loads).w
       ev=CoupledNetwork(fz[idx],loads,w=w,coupled=mname!='blind_pair')
       if mname=='blind_pair':controller='pair'
      prep_ms=(time.perf_counter_ns()-start)/1e6
      kind=controller.removesuffix('_ga');kind='attention' if kind=='attention_no_memory' else kind
      policy=policies.get((kind,seed));actual=controller
      trace=[]
      baseline_no_memory=mname in {'greedy','pair','random','blind_pair','population_ga','ga_risc'}
      method_kw={} if actual=='population_ga' else skw|({'conditional_pair_policy':True} if a.conditional_pair_policy else {})
      bits,value,evaluations,breakdown=search(ev,actual,deadline,seed*10000+int(idx),memory=() if ('no_memory' in controller or baseline_no_memory) else memory[mname],policy=policy,scaling=feature_scale,trace=trace,**method_kw)
      mt=time.perf_counter_ns()
      if should_store_memory(mname): memory[mname]=[bits.copy()]+[b for b in memory[mname] if not np.array_equal(b,bits)][:11]
      memory_ms=(time.perf_counter_ns()-mt)/1e6 if should_store_memory(mname) else 0.0
      elapsed=(time.perf_counter_ns()-start)/1e6
      full=float(ev.score(ev.channel(bits)@w))
      if abs(full-value)>1e-7:raise AssertionError('Cached and full channel disagree')
      truth=CoupledNetwork(fz[idx],loads,w=w);rate=float(truth.score(truth.channel(bits)@w))
      row={'mode':a.mode,'split':a.split,'method':mname,'seed':seed,'budget_ms':budget,'index':int(idx),'trajectory':trajectory,'step':int(fs['step'][idx]),'search_config':a.search_config,'conditional_pair_policy':bool(a.conditional_pair_policy),'rate':rate,'belief_rate':value,'elapsed_ms':elapsed,'deadline_missed':None if mname=='me_ga_paper' else elapsed>budget,'evaluations':evaluations,'trace':trace,'bits':bits.tolist(),'breakdown_ms':breakdown|{'preparation_ms':prep_ms,'forecast_ms':prediction_ms,'memory_write_ms':memory_ms}}
      if mname=='me_ga_paper':row['deadline_applicable']=False   # untimed reference: elapsed_ms is its true runtime
      f.write(json.dumps(row)+'\n');f.flush()
   print(a.mode,a.split,'completed',budget,flush=True)
if __name__=='__main__':main()
