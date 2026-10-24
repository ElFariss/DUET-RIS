"""Bounded, sequential research campaign with frozen input/source identity."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from atomwise_ris.core import sha256,source_versions,write_json

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',default='configs/experiments/pilot.json')
    p.add_argument('--run');p.add_argument('--device',choices=['cpu','cuda'],default='cuda')
    p.add_argument('--stage',choices=['all','prepare','train','validate','pilot','report'],default='all')
    a=p.parse_args();os.chdir(ROOT)
    cfg=json.loads(Path(a.config).read_text())
    dataset=json.loads(Path(cfg['dataset_config']).read_text());method=json.loads(Path(cfg['method_config']).read_text())
    if cfg['preferred_budget_ms']!=10:raise ValueError('Current budget-selection protocol prefers 10 ms')
    for key in ['scenario','response']:
        if sha256(dataset[key])!=dataset[key+'_sha256']:raise ValueError(f'{key} hash mismatch; freeze a new dataset/config')
    run=Path(a.run or cfg['run']);run.mkdir(parents=True,exist_ok=True);(run/'logs').mkdir(exist_ok=True)
    resolved={'experiment':cfg,'dataset':dataset,'method':method,'run':str(run),'device':a.device}
    manifest=run/'manifest.json';sources=source_versions()
    identity={'resolved_config':resolved,'source_sha256':sources}
    if manifest.exists():
        prior=json.loads(manifest.read_text())
        if any(prior[k]!=v for k,v in identity.items()):raise RuntimeError('Run source/config changed; choose a new run directory')
    else:
        try:commit=subprocess.check_output(['git','rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
        except subprocess.CalledProcessError:commit=None
        identity.update({'created_utc':datetime.now(timezone.utc).isoformat(),'git_commit':commit,
                         'python':sys.version,'platform':platform.platform(),
                         'packages':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
                         'claim_scope':'Development pilot; not an untouched final evaluation'})
        write_json(manifest,identity);write_json(run/'resolved_config.json',resolved)
        with tarfile.open(run/'source_snapshot.tar.gz','w:gz') as archive:
            for rel in sorted(sources):archive.add(ROOT/rel,arcname=rel)
            for rel in ['pyproject.toml','uv.lock','requirements-lock.txt']:
                archive.add(ROOT/rel,arcname=rel)
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONPATH=str(ROOT/'src'))
    def command(script,*args,tag=None):
        cmd=[sys.executable,'-u',f'scripts/{script}',*map(str,args)]
        label=tag or script.removesuffix('.py')
        print('Running',label,flush=True)
        # Exclusive creation preserves failed logs and prevents accidental overwrite.
        with (run/'logs'/f'{label}.log').open('x') as log:
            subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    shared=['--scenario',dataset['scenario'],'--response',dataset['response']]
    if a.stage in ['all','prepare']:
        command('audit_scenario.py','--scenario',dataset['scenario'])
        command('prepare_experiments.py',*shared,'--out',run,'--parents',method['parents_per_snapshot'])
    if a.stage in ['all','train']:
        gate=json.loads((run/'headroom.json').read_text())['gate']
        if gate['decision']!='bounded_training':
            print('Training stopped by headroom gate. See headroom.json.');return
        for variant in method['variants']:
            for seed in method['seeds']:
                flags=[f'--{k.replace("_","-")}' for k,v in variant.items() if k!='kind' and v]
                tag=variant['kind']+''.join('_'+f[2:].replace('-','_') for f in flags)+f'_seed{seed}'
                command('train.py','--run',run,'--kind',variant['kind'],'--seed',seed,'--epochs',method['epochs'],'--device',a.device,*flags,tag=tag)
    budgets=','.join(map(str,cfg['budgets_ms']));seeds=','.join(map(str,method['seeds']))
    if a.stage in ['all','validate']:
        command('benchmark.py',*shared,'--run',run,'--split','validation','--budgets',budgets,'--seeds',seeds,tag='benchmark_validation')
        command('analyze.py','--run',run,'--select-budget',tag='budget_selection')
    if a.stage in ['all','pilot']:
        choice=json.loads((run/'budget_selection.json').read_text())
        if choice['selected_ms'] is None:raise RuntimeError('No feasible validation budget; stop before pilot')
        command('benchmark.py',*shared,'--run',run,'--split','pilot','--ablations','--budgets',budgets,'--seeds',seeds,tag='benchmark_pilot')
    if a.stage in ['all','report']:
        command('sensitivity.py',*shared,'--run',run)
        command('analyze.py','--run',run,tag='report')
        print('Completed:',run/'REPORT.md',flush=True)

if __name__=='__main__':main()
