"""Paired full-controller CPU timings with incremental durable JSONL results."""
import argparse
import json
import os
from pathlib import Path
import platform
import time
import numpy as np
import torch
from atomwise_ris.core import Scenario,ResponseModel,Evaluator,write_json,sha256,source_versions
from atomwise_ris.optimization.search import search,Memory,load_search_config,ME_GA_METHODS
from atomwise_ris.models import EditPolicy
from select_matched_budget import load_protocol,protocol_methods,frozen_code_hashes,checkpoint_hashes,host_state,require_frozen_selection,sha256_file
from run_improvement_campaign import validate_validation_rows

def validate_primary_selection(selection,protocol,protocol_hash,root,scenario,scenario_path,response_path):
    path=root/'benchmark_validation.jsonl'
    if selection.get('protocol_sha256')!=protocol_hash:
        raise RuntimeError('Test is blocked: budget selection was made under another protocol')
    if (selection.get('protocol_primary_ms')!=protocol.get('primary_budget_ms')
            or selection.get('protocol_preferred_ms')!=protocol.get('preferred_budget_ms',protocol.get('primary_budget_ms'))
            or selection.get('budget_lock')!=protocol.get('budget_lock')):
        raise RuntimeError('Test is blocked: budget selection primary/preferred lock differs from protocol')
    if not path.exists() or selection.get('input_hashes',{}).get(path.name)!=sha256_file(path):
        raise RuntimeError('Test is blocked: frozen validation JSONL is missing or its hash changed')
    meta_path=path.with_suffix('.json')
    if not meta_path.exists():raise RuntimeError('Test is blocked: frozen validation metadata sidecar is missing')
    meta=json.loads(meta_path.read_text())
    if (meta.get('protocol_sha256')!=protocol_hash or meta.get('scenario_sha256')!=sha256(scenario_path)
            or meta.get('response_sha256')!=sha256_file(response_path)
            or meta.get('conditional_pair_policy',False)
            or meta.get('selection_helper_sha256')!=sha256_file(Path(__file__).with_name('select_matched_budget.py'))
            or meta.get('campaign_script_sha256')!=sha256_file(Path(__file__).with_name('run_improvement_campaign.py'))
            or meta.get('frozen_code_sha256')!=selection.get('code_sha256')
            or meta.get('checkpoint_sha256')!=selection.get('checkpoint_sha256')):
        raise RuntimeError('Test is blocked: validation sidecar source/checkpoint identity differs from selection')
    rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    expected=set(map(int,np.flatnonzero(scenario.split=='validation')))
    validate_validation_rows(rows,protocol_methods(protocol),protocol['seeds'],protocol['budgets_ms'],expected,
                             protocol['primary_budget_ms'],selected_budget=selection.get('selected_ms'))

def load_policy(root,kind,seed,no_physics=False,no_conditioning=False):
    tag=kind+('_no_physics' if no_physics else '')+('_no_conditioning' if no_conditioning else '')+f'_seed{seed}'
    path=root/'models'/tag/'best.pt'
    if not path.exists():return None
    ck=torch.load(path,map_location='cpu',weights_only=True)
    model=EditPolicy(ck['features'],ck['kind'],ck['physics'],ck['conditioning']);model.load_state_dict(ck['state_dict'])
    return model.callable_cpu()

def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',default='data/processed/munich_specular_v3/scenario.npz');p.add_argument('--run',default=None,help='default: outputs/runs/specular_v5; with --matched the protocol run')
    p.add_argument('--split',choices=['validation','pilot','test'],default='validation');p.add_argument('--budgets',default=None)
    p.add_argument('--seeds',default=None);p.add_argument('--output',default=None);p.add_argument('--baselines-only',action='store_true')
    p.add_argument('--ablations',action='store_true');p.add_argument('--response',default='data/processed/responses/opensourceris_v1.csv')
    p.add_argument('--matched',action='store_true',help='run the registered matched protocol (methods, seeds, budgets, shared search config)')
    p.add_argument('--protocol',default='configs/experiments/matched_v1.json');p.add_argument('--search-config',choices=['small','medium','large'],default=None)
    p.add_argument('--test-data',default=None,help='scenario.npz (or its directory) holding the test frames; training/validation data stay in --scenario')
    p.add_argument('--limit',type=int,default=0);p.add_argument('--conditional-pair-policy',action='store_true')
    p.add_argument('--extra-methods',default='',help='comma list from me_ga,ga_risc,me_ga_paper (Zardi et al. reimplementation); appended to the method list, never part of the registered protocol')
    a=p.parse_args()
    if not a.matched:
        if a.split=='test' or a.test_data or a.search_config or a.conditional_pair_policy:raise SystemExit('--split test, --test-data, --search-config and conditional policy require --matched')
        a.budgets=a.budgets or '1,5,10,50,100';a.seeds=a.seeds or '7,19,43'
    else:
        if a.baselines_only or a.ablations:raise SystemExit('--matched fixes the method list; drop --baselines-only/--ablations')
        a.search_config=a.search_config or 'medium'
    if a.split=='test' and (not a.test_data or a.search_config!='medium' or a.limit or a.budgets or a.seeds):
        raise SystemExit('Test split needs --test-data, the primary (medium) config, the full protocol seeds/budgets and no --limit')
    if a.split=='test' and a.conditional_pair_policy:raise SystemExit('Conditional-pair policy is development-only')
    if a.test_data and a.split!='test':raise SystemExit('--test-data is only for --split test')
    extras=[m for m in a.extra_methods.split(',') if m]
    if set(extras)-set(ME_GA_METHODS):raise SystemExit(f'--extra-methods must be among {ME_GA_METHODS}')
    if extras and (a.split=='test' or not a.output):raise SystemExit('--extra-methods needs an explicit --output and is not allowed for --split test')
    a.run=a.run or (load_protocol(a.protocol)[0]['experiments']['specular']['run'] if a.matched else 'outputs/runs/specular_v5')
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
    s=Scenario.load(a.scenario);response=ResponseModel.from_table(a.response,5.53e9)
    root=Path(a.run);root.mkdir(parents=True,exist_ok=True)
    protocol=protocol_hash=cfg=None
    if a.matched:
        protocol,protocol_hash=load_protocol(a.protocol);cfg=load_search_config(a.search_config,a.protocol)
        if a.split=='test':
            selection=require_frozen_selection(root)
            validate_primary_selection(selection,protocol,protocol_hash,root,s,a.scenario,a.response)
    if not a.baselines_only:
        for split_name in ['train','validation']:
            recorded=json.loads((root/f'{split_name}_labels.json').read_text())['scenario_sha256']
            if recorded!=sha256(a.scenario):raise ValueError('Benchmark scenario differs from training/validation source')
    if a.split=='pilot':
        decision=json.loads((root/'budget_selection.json').read_text())
        if decision['selected_ms'] is None:raise RuntimeError('Freeze a feasible validation budget before pilot')
    suffix='' if not a.matched or a.search_config=='medium' else f'_{a.search_config}'
    dest=root/(a.output or f'benchmark_{a.split}{suffix}.jsonl')
    if dest.exists() or (a.split=='test' and dest.with_suffix('.json').exists()):raise FileExistsError(f'Preserving existing results: {dest}; choose a new --output')
    if a.matched:
        methods=protocol_methods(protocol)
        seeds=protocol['seeds'];budgets=[float(x) for x in protocol['budgets_ms']]
        if a.seeds:
            seeds=[int(x) for x in a.seeds.split(',')]
            if not set(seeds)<=set(protocol['seeds']):raise SystemExit('Seeds must be a subset of the protocol seeds')
        if a.budgets:
            budgets=[float(x) for x in a.budgets.split(',')]
            if not set(budgets)<=set(float(x) for x in protocol['budgets_ms']):raise SystemExit('Budgets must be a subset of the protocol budgets')
    else:
        methods=['greedy','pair','random','population_ga','memory_ga','analytical_ga']
        if not a.baselines_only:methods+=['mlp_ga','attention_ga']
        if a.ablations:methods+=['attention_no_physics_ga','attention_no_conditioning_ga','attention_no_memory_ga']
        seeds=[int(x) for x in a.seeds.split(',')];budgets=[float(x) for x in a.budgets.split(',')]
    methods=methods+[m for m in extras if m not in methods]
    policies={}
    for seed in seeds:
        for method in methods:
            kind='mlp' if method=='mlp_ga' else 'attention'
            if method in ['greedy','pair','random','population_ga','memory_ga','analytical_ga','uniform_ga','analytical_no_memory_ga'] or method in ME_GA_METHODS:continue
            policy=load_policy(root,kind,seed,'no_physics' in method,'no_conditioning' in method)
            if policy is None:raise FileNotFoundError(f'Missing checkpoint for {method}, seed {seed}')
            policies[method,seed]=policy
    # Frame set: the test scenario is a separate file; warm-up and checkpoints only ever see train data.
    frames=s;test_hash=None;frame_rule=f"split=={a.split}"
    if a.test_data:
        tp=Path(a.test_data);tp=tp/'scenario.npz' if tp.is_dir() else tp
        frames=Scenario.load(tp);test_hash=sha256(tp)
        if not np.any(frames.split==a.split):frame_rule='all frames of the test scenario';indices=np.arange(len(frames.trajectory))
        else:indices=np.flatnonzero(frames.split==a.split)
    else:indices=np.flatnonzero(s.split==a.split)
    if a.limit:indices=indices[:a.limit]
    # Warm up code/model kernels on a TRAIN case only; no timed result retained.
    warm=Evaluator.from_scenario(s,int(np.flatnonzero(s.split=='train')[0]),response)
    for policy in policies.values():
        x,g=warm.features(np.zeros(warm.n,dtype=np.int8));policy(x,g)
    kw={'config':cfg} if a.matched else {'legacy':True}
    if a.matched:   # calibrate each policy's cost on the TRAIN case so the controller can keep neural overhead inside the deadline
        for policy in policies.values():
            ts=[]
            for _ in range(23):
                t0=time.perf_counter_ns();x,g=warm.features(np.zeros(warm.n,dtype=np.int8));policy(x,g);ts.append((time.perf_counter_ns()-t0)/1e6)
            policy.expected_ms=float(np.percentile(ts[3:],90))
    for m in (methods if a.matched else []):   # warm every controller path once on the train case; results discarded
        method_kw={} if m=='population_ga' else kw|({'conditional_pair_policy':True} if a.conditional_pair_policy else {})
        search(warm,m,10.,1,memory=None if m in {'greedy','pair','random','population_ga','ga_risc'} or 'no_memory' in m else Memory(),policy=next((v for (mm,_),v in policies.items() if mm==m),None),**method_kw)
    write_json(dest.with_suffix('.json'),{'arguments':vars(a),'cpu_affinity':[cpu],'platform':platform.platform(),
               'hostname':platform.node(),'torch':torch.__version__,'numpy':np.__version__,
               'scenario_sha256':sha256(a.scenario),'threads':1,'methods':methods,
               'timing_includes':['channel contraction and cache creation','memory reset/retrieval/rescoring/write',
                                  'features','CPU inference','selection and mutation','candidate evaluation'],
               'timing_excludes':['one-time model load','one-time train-case warmup','disk IO','channel acquisition/ray tracing'],
               'precision':'complex128 evaluator, float32 neural inference','pilot_is_development':a.split!='test',
               'precoder':'RZF on all-OFF reference, fixed within episode; includes RIS-only users',
               'source_sha256':source_versions(),
               'response_sha256':sha256_file(a.response),
               'conditional_pair_policy':bool(a.conditional_pair_policy),
               'selection_helper_sha256':sha256_file(Path(__file__).with_name('select_matched_budget.py')),
               'campaign_script_sha256':sha256_file(Path(__file__).with_name('run_improvement_campaign.py')),
               'checkpoint_sha256':{str(p.relative_to(root)):sha256(p) for p in sorted((root/'models').glob('*/best.pt'))},
               'policy_expected_ms':{f'{m}_seed{sd}':getattr(pol,'expected_ms',None) for (m,sd),pol in policies.items()},'matched':a.matched,'frame_rule':frame_rule,'n_frames':int(len(indices)),
               **({'protocol_sha256':protocol_hash,'search_config':a.search_config,'search_config_values':{'specular':cfg.specular,'coupled':cfg.coupled,'all_variants':cfg.shared},
                   'frozen_code_sha256':frozen_code_hashes(),'test_scenario_sha256':test_hash,'budget_selection':selection if a.split=='test' else None,
                   'seeds':seeds,'budgets_ms':budgets,**host_state()} if a.matched else {})})
    rng=np.random.default_rng(8251)
    with dest.open('w') as file:
        for budget in budgets:
            for seed in seeds:
                memories={m:Memory() for m in methods}
                for idx in indices:
                    # Alternate method order to reduce systematic timing drift.
                    for method in rng.permutation(methods):
                        start=time.perf_counter_ns();ev=Evaluator.from_scenario(frames,int(idx),response)
                        memory=None if ('no_memory' in method or method in {'greedy','pair','random','population_ga','ga_risc'}) else memories[method]
                        if memory is not None:memory.enter(int(frames.trajectory[idx]))
                        prep=(time.perf_counter_ns()-start)/1e6
                        actual_method=str(method)
                        method_kw={} if actual_method=='population_ga' else kw|({'conditional_pair_policy':True} if a.conditional_pair_policy else {})
                        result=search(ev,actual_method,max(.001,budget-prep),seed*10000+int(idx),
                                      memory=memory,policy=policies.get((method,seed)),**method_kw)
                        elapsed=(time.perf_counter_ns()-start)/1e6
                        # Defensive full recomputation outside timing cannot improve returned action.
                        full=float(ev.score_field(ev.full_field(result.bits)))
                        if abs(full-result.value)>1e-8:raise AssertionError('Cached candidate disagrees with full evaluator')
                        row={'method':str(method),'seed':seed,'budget_ms':budget,'index':int(idx),
                             'trajectory':int(frames.trajectory[idx]),'split':a.split,'search_config':a.search_config,
                             'conditional_pair_policy':bool(a.conditional_pair_policy),'rate':result.value,
                             'elapsed_ms':elapsed,'deadline_missed':None if str(method)=='me_ga_paper' else elapsed>budget,'overrun_ms':None if str(method)=='me_ga_paper' else max(0.,elapsed-budget),
                             'evaluations':result.evaluations,'bits':''.join(str(int(x)) for x in result.bits),
                             'breakdown_ms':result.breakdown_ms|{'scenario_preparation':prep},'trace':result.trace}
                        if str(method)=='me_ga_paper':row['deadline_applicable']=False   # untimed reference: elapsed_ms is its true runtime
                        file.write(json.dumps(row)+'\n');file.flush()
            print('Completed budget',budget,flush=True)

if __name__=='__main__':main()
