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
from atomwise_ris.optimization.search import search,Memory
from atomwise_ris.models import EditPolicy

def load_policy(root,kind,seed,no_physics=False,no_conditioning=False):
    tag=kind+('_no_physics' if no_physics else '')+('_no_conditioning' if no_conditioning else '')+f'_seed{seed}'
    path=root/'models'/tag/'best.pt'
    if not path.exists():return None
    ck=torch.load(path,map_location='cpu',weights_only=True)
    model=EditPolicy(ck['features'],ck['kind'],ck['physics'],ck['conditioning']);model.load_state_dict(ck['state_dict'])
    return model.callable_cpu()

def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',default='data/processed/munich_specular_v3/scenario.npz');p.add_argument('--run',default='outputs/runs/specular_v5')
    p.add_argument('--split',choices=['validation','pilot'],default='validation');p.add_argument('--budgets',default='1,5,10,50,100')
    p.add_argument('--seeds',default='7,19,43');p.add_argument('--output',default=None);p.add_argument('--baselines-only',action='store_true')
    p.add_argument('--ablations',action='store_true');p.add_argument('--response',default='data/processed/responses/opensourceris_v1.csv');a=p.parse_args()
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
    s=Scenario.load(a.scenario);response=ResponseModel.from_table(a.response,5.53e9)
    root=Path(a.run);root.mkdir(parents=True,exist_ok=True)
    if not a.baselines_only:
        for split_name in ['train','validation']:
            recorded=json.loads((root/f'{split_name}_labels.json').read_text())['scenario_sha256']
            if recorded!=sha256(a.scenario):raise ValueError('Benchmark scenario differs from training/validation source')
    if a.split=='pilot':
        decision=json.loads((root/'budget_selection.json').read_text())
        if decision['selected_ms'] is None:raise RuntimeError('Freeze a feasible validation budget before pilot')
    dest=root/(a.output or f'benchmark_{a.split}.jsonl')
    if dest.exists():raise FileExistsError(f'Preserving existing results: {dest}; choose a new --output')
    methods=['greedy','pair','random','memory_ga','analytical_ga']
    if not a.baselines_only:methods+=['mlp_ga','attention_ga']
    if a.ablations:methods+=['attention_no_physics_ga','attention_no_conditioning_ga','attention_no_memory_ga']
    seeds=[int(x) for x in a.seeds.split(',')];budgets=[float(x) for x in a.budgets.split(',')]
    policies={}
    for seed in seeds:
        for method in methods:
            kind='mlp' if method=='mlp_ga' else 'attention'
            if method in ['greedy','pair','random','memory_ga','analytical_ga']:continue
            policy=load_policy(root,kind,seed,'no_physics' in method,'no_conditioning' in method)
            if policy is None:raise FileNotFoundError(f'Missing checkpoint for {method}, seed {seed}')
            policies[method,seed]=policy
    indices=np.flatnonzero(s.split==a.split)
    # Warm up code/model kernels on a TRAIN case only; no timed result retained.
    warm=Evaluator.from_scenario(s,int(np.flatnonzero(s.split=='train')[0]),response)
    for policy in policies.values():
        x,g=warm.features(np.zeros(warm.n,dtype=np.int8));policy(x,g)
    write_json(dest.with_suffix('.json'),{'arguments':vars(a),'cpu_affinity':[cpu],'platform':platform.platform(),
               'hostname':platform.node(),'torch':torch.__version__,'numpy':np.__version__,
               'scenario_sha256':sha256(a.scenario),'threads':1,'methods':methods,
               'timing_includes':['channel contraction and cache creation','memory reset/retrieval/rescoring/write',
                                  'features','CPU inference','selection and mutation','candidate evaluation'],
               'timing_excludes':['one-time model load','one-time train-case warmup','disk IO','channel acquisition/ray tracing'],
               'precision':'complex128 evaluator, float32 neural inference','pilot_is_development':True,
               'precoder':'RZF on all-OFF reference, fixed within episode; includes RIS-only users',
               'source_sha256':source_versions(),
               'checkpoint_sha256':{str(p.relative_to(root)):sha256(p) for p in sorted((root/'models').glob('*/best.pt'))}})
    rng=np.random.default_rng(8251)
    with dest.open('w') as file:
        for budget in budgets:
            for seed in seeds:
                memories={m:Memory() for m in methods}
                for idx in indices:
                    # Alternate method order to reduce systematic timing drift.
                    for method in rng.permutation(methods):
                        start=time.perf_counter_ns();ev=Evaluator.from_scenario(s,int(idx),response)
                        memory=None if 'no_memory' in method else memories[method]
                        if memory is not None:memory.enter(int(s.trajectory[idx]))
                        prep=(time.perf_counter_ns()-start)/1e6
                        actual_method='attention_ga' if method.startswith('attention_') else str(method)
                        result=search(ev,actual_method,max(.001,budget-prep),seed*10000+int(idx),
                                      memory=memory,policy=policies.get((method,seed)))
                        elapsed=(time.perf_counter_ns()-start)/1e6
                        # Defensive full recomputation outside timing cannot improve returned action.
                        full=float(ev.score_field(ev.full_field(result.bits)))
                        if abs(full-result.value)>1e-8:raise AssertionError('Cached candidate disagrees with full evaluator')
                        row={'method':str(method),'seed':seed,'budget_ms':budget,'index':int(idx),
                             'trajectory':int(s.trajectory[idx]),'split':a.split,'rate':result.value,
                             'elapsed_ms':elapsed,'deadline_missed':elapsed>budget,'overrun_ms':max(0.,elapsed-budget),
                             'evaluations':result.evaluations,'bits':''.join(str(int(x)) for x in result.bits),
                             'breakdown_ms':result.breakdown_ms|{'scenario_preparation':prep},'trace':result.trace}
                        file.write(json.dumps(row)+'\n');file.flush()
            print('Completed budget',budget,flush=True)

if __name__=='__main__':main()
