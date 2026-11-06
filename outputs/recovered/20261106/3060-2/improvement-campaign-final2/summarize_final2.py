#!/usr/bin/env python3
"""Verify final2 validation campaign hashes/coverage and aggregate rate/runtime metrics."""
import csv, json, hashlib
from itertools import product
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent/'campaigns'
OUT=Path(__file__).resolve().parent
cases={}; file_manifest=[]; campaign_manifest=[]; validation_summary=[]
for p in sorted(ROOT.iterdir()):
    if not p.is_dir() or not (p.name.endswith('_10ms_final2_20261106') or p.name.endswith('_5_50_final2_20261106')): continue
    man=json.loads((p/'campaign.json').read_text())
    exp=man['experiment']; expect_units=3 if p.name.endswith('_10ms_final2_20261106') else 6
    casekey=p.name.replace('_10ms_final2_20261106','').replace('_5_50_final2_20261106','').removesuffix('_conditional')
    mode='conditional' if man['conditional_pair_policy'] else 'default'
    readable_case=casekey if mode=='default' else casekey+'_conditional'
    assert man['status']=='complete' and len(man['units'])==expect_units, (p,man['status'],len(man['units']))
    rows=[]
    for unit in man['units']:
        f=p/unit['path']; meta=f.with_suffix('.json')
        raw=f.read_bytes(); side=meta.read_bytes()
        h=hashlib.sha256(raw).hexdigest(); mh=hashlib.sha256(side).hexdigest()
        assert h==unit['sha256'] and mh==unit['metadata_sha256'], f'hash mismatch {f}'
        md=json.loads(side)
        assert md['conditional_pair_policy']==man['conditional_pair_policy']
        data=[json.loads(line) for line in raw.decode().splitlines() if line]
        assert data
        rows.extend(data)
        file_manifest.append({'campaign':p.name,'jsonl':str(f.relative_to(OUT)),'sha256':h,'sidecar':str(meta.relative_to(OUT)),'sidecar_sha256':mh,'rows':len(data)})
    methods=sorted({r['method'] for r in rows}); seeds=sorted({r['seed'] for r in rows}); budgets=sorted({float(r['budget_ms']) for r in rows})
    assert len(methods)==12 and seeds==[7,19,43], (p,len(methods),seeds)
    expected_frames={'specular':24,'coupled':48}[exp]
    frame_ids=sorted({int(r['index']) for r in rows})
    assert len(frame_ids)==expected_frames, (p,exp,'validation frame count',len(frame_ids),expected_frames)
    expected_budgets=[10.] if expect_units==3 else [5.,50.]
    assert budgets==expected_budgets,(p,budgets)
    frames_per_seed=expected_frames
    # Require the exact Cartesian method x budget x seed x validation-frame grid.
    keys=[(r['method'],float(r['budget_ms']),int(r['seed']),int(r['index'])) for r in rows]
    expected_keys=set(product(methods,budgets,seeds,frame_ids))
    actual_keys=set(keys)
    assert len(keys)==len(actual_keys),f'duplicate row keys in {p}'
    assert actual_keys==expected_keys, (p,'incomplete Cartesian grid',len(expected_keys-actual_keys),'missing',len(actual_keys-expected_keys),'unexpected')
    for method in methods:
      for budget in budgets:
       rr=[r for r in rows if r['method']==method and float(r['budget_ms'])==budget]
       assert len(rr)==len(seeds)*frames_per_seed,(p,method,budget,len(rr))
       validation_summary.append({'case':readable_case,'experiment':exp,'method':method,'budget_ms':budget,
         'rows':len(rr),'seeds':len({r['seed'] for r in rr}),'frames_per_seed':frames_per_seed,
         'unique_frames':len({r['index'] for r in rr}),'unique_trajectories':len({r['trajectory'] for r in rr}),
         'trajectory_frame_units':len({(r['trajectory'],r['index']) for r in rr}),
         'mean_rate':float(np.mean([r['rate'] for r in rr])),
         'p95_elapsed_ms':float(np.percentile([r['elapsed_ms'] for r in rr],95)),
         'mean_evaluations':float(np.mean([r['evaluations'] for r in rr])),
         'deadline_misses':int(sum(bool(r['deadline_missed']) for r in rr)),
         'max_elapsed_ms':float(max(r['elapsed_ms'] for r in rr))})
    cases[(casekey,mode)].extend(rows) if (casekey,mode) in cases else cases.update({(casekey,mode):rows})
    campaign_manifest.append({'campaign':p.name,'experiment':exp,'status':man['status'],'units':len(man['units']),
      'frames_per_seed':frames_per_seed,'methods':methods,'budgets_ms':budgets,
      'conditional_pair_policy':man['conditional_pair_policy'],'artifact_root':man['artifact_root'],
      'protocol_sha256':man['protocol_sha256'],'data_sha256':man['data_sha256'],
      'response_sha256':man.get('response_sha256'),'physics_gate_sha256':man.get('physics_gate_sha256'),
      'code_sha256':man['code_sha256'],'campaign_script_sha256':man['campaign_script_sha256'],
      'selection_helper_sha256':man['selection_helper_sha256'],'checkpoint_sha256':man['checkpoint_sha256']})
# Paired exact-frame deltas.
contrasts=[]
def add_pair(left,right,label):
    a={(r['method'],float(r['budget_ms']),r['seed'],r['index']):r for r in cases[left]}
    b={(r['method'],float(r['budget_ms']),r['seed'],r['index']):r for r in cases[right]}
    assert a.keys()==b.keys(),f'paired grid mismatch {left} {right}'
    for method in sorted({k[0] for k in a}):
      for budget in sorted({k[1] for k in a}):
       ks=[k for k in a if k[0]==method and k[1]==budget]
       ds=[(b[k]['rate']-a[k]['rate'],b[k]['elapsed_ms']-a[k]['elapsed_ms'],b[k]['evaluations']-a[k]['evaluations'],int(b[k]['deadline_missed'])-int(a[k]['deadline_missed'])) for k in ks]
       contrasts.append({'contrast':label,'method':method,'budget_ms':budget,'paired_rows':len(ds),
         'mean_delta_rate':float(np.mean([d[0] for d in ds])),'mean_delta_elapsed_ms':float(np.mean([d[1] for d in ds])),
         'mean_delta_evaluations':float(np.mean([d[2] for d in ds])),'deadline_miss_delta':int(sum(d[3] for d in ds))})
for c in ['specular_incumbent','specular_newA','specular_newB','coupled_incumbent','coupled_new']:
    add_pair((c,'default'),(c,'conditional'),c+' conditional minus default')
for new,old in [('specular_newA','specular_incumbent'),('specular_newB','specular_incumbent'),('coupled_new','coupled_incumbent')]:
    for mode in ['default','conditional']:
      add_pair((old,mode),(new,mode),new+' minus incumbent ('+mode+')')
for name,rows in [('method_summary_final2.csv',validation_summary),('paired_contrasts_final2.csv',contrasts)]:
    with (OUT/name).open('w',newline='') as f:
      w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
assert len({json.dumps(c['code_sha256'],sort_keys=True) for c in campaign_manifest})==1, 'campaign source hashes differ'
assert len({c['protocol_sha256'] for c in campaign_manifest})==1, 'protocol hash differs'
assert len({c['campaign_script_sha256'] for c in campaign_manifest})==1
assert len({c['selection_helper_sha256'] for c in campaign_manifest})==1
for experiment in ('specular','coupled'):
    subset=[c for c in campaign_manifest if c['experiment']==experiment]
    assert len({c['data_sha256'] for c in subset})==1, f'{experiment} dataset hash differs'
    ext='response_sha256' if experiment=='specular' else 'physics_gate_sha256'
    assert len({c[ext] for c in subset})==1, f'{experiment} response/gate hash differs'
(OUT/'campaign_manifest_final2.json').write_text(json.dumps({'campaigns':campaign_manifest,'files':file_manifest},indent=2)+'\n')
first=campaign_manifest[0]
(OUT/'source_hashes_final2.json').write_text(json.dumps({'protocol_sha256':first['protocol_sha256'],'source_code_sha256':first['code_sha256'],'campaign_script_sha256':first['campaign_script_sha256'],'selection_helper_sha256':first['selection_helper_sha256'],'data_sha256_by_experiment':{e:next(c['data_sha256'] for c in campaign_manifest if c['experiment']==e) for e in ('specular','coupled')},'response_sha256':next(c['response_sha256'] for c in campaign_manifest if c['experiment']=='specular'),'physics_gate_sha256':next(c['physics_gate_sha256'] for c in campaign_manifest if c['experiment']=='coupled'),'checkpoint_hashes_by_campaign':{c['campaign']:c['checkpoint_sha256'] for c in campaign_manifest}},indent=2)+'\n')
print('campaigns',len(campaign_manifest),'units',sum(c['units'] for c in campaign_manifest),'jsonls',len(file_manifest))
print('cases',len(cases),'budgets',sorted({r['budget_ms'] for r in validation_summary}),'methods',len({r['method'] for r in validation_summary}))
for r in validation_summary:
    if r['method'] in {'analytical_ga','pair','mlp_ga','attention_ga','population_ga'}:
      print(r['case'],r['method'],f"{r['budget_ms']:g}ms",f"rate={r['mean_rate']:.4f}",f"p95={r['p95_elapsed_ms']:.3f}ms",f"eval={r['mean_evaluations']:.1f}",f"miss={r['deadline_misses']}/{r['rows']}",f"trajectories={r['unique_trajectories']}")
