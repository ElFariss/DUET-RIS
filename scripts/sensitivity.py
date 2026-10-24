"""Fixed-action uncertainty sensitivity; no retuning against pilot perturbations.

Bounds are declared stress envelopes, not calibrated probabilistic intervals.
Also test common phase registration and aperture scaling separately.
"""
import argparse,json
from pathlib import Path
import numpy as np
from atomwise_ris.core import Scenario,ResponseModel,Evaluator,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',default='data/processed/munich_specular_v3/scenario.npz')
    p.add_argument('--run',default='outputs/runs/specular_v5');p.add_argument('--input',default='benchmark_pilot.jsonl');p.add_argument('--response',default='data/processed/responses/opensourceris_v1.csv');a=p.parse_args()
    root=Path(a.run);s=Scenario.load(a.scenario);r=ResponseModel.from_table(a.response,5.53e9)
    rows=[json.loads(line) for line in (root/a.input).read_text().splitlines()]
    budget=json.loads((root/'budget_selection.json').read_text())['selected_ms'];rows=[x for x in rows if x['budget_ms']==budget]
    rng=np.random.default_rng(8291);conditions=[('nominal',r.gamma,1.)]
    for mode,db,deg in [('digitization',.1,2),('model_envelope',1.,15.)]:
        for rep in range(20):
            # Common per-state perturbation; same response for every controller.
            gamma=r.gamma*10**(rng.uniform(-db,db,2)/20)*np.exp(1j*np.deg2rad(rng.uniform(-deg,deg,2)))
            conditions.append((f'{mode}_{rep}',gamma,1.))
    for deg in [45,90,180,270]:conditions.append((f'common_phase_{deg}',r.gamma*np.exp(1j*np.deg2rad(deg)),1.))
    for scale in [.5,2.]:conditions.append((f'aperture_{scale}',r.gamma,scale))
    result=[]
    for name,gamma,scale in conditions:
        response=ResponseModel(r.frequency_hz,gamma,r.metadata)
        cache={}
        for row in rows:
            idx=row['index']
            if idx not in cache:
                # Keep the nominal precoder and direct/cascade terms frozen;
                # perturb ONLY the response and scalar aperture uncertainty.
                nominal=Evaluator.from_scenario(s,idx,r)
                cache[idx]=Evaluator(nominal.direct,nominal.contribution*scale,gamma,nominal.noise_w,nominal.cell_positions)
            b=np.array([int(v) for v in row['bits']],dtype=np.int8)
            result.append({'condition':name,'method':row['method'],'seed':row['seed'],'trajectory':row['trajectory'],
                           'index':idx,'rate':float(cache[idx].score(b))})
    write_json(root/'sensitivity.json',{'budget_ms':budget,'semantics':'Fixed nominal actions rescored under shared perturbations; no adaptation',
                'bounds_not_confidence_intervals':True,'rows':result})
    means={name:{method:float(np.mean([x['rate'] for x in result if x['condition']==name and x['method']==method]))
                 for method in sorted({x['method'] for x in rows})} for name,_,_ in conditions}
    wins=[name for name,v in means.items() if v.get('attention_ga',-np.inf)>v['pair']]
    write_json(root/'sensitivity_summary.json',{'budget_ms':budget,'conditions':len(conditions),
               'mean_rates':means,'attention_better_than_pair_conditions':wins,
               'interpretation':'Fixed nominal actions and precoder; no retuning. Stress envelopes are not measured confidence intervals. Common phase uncertainty can change ranking.'})


if __name__=='__main__':main()
