"""Freeze validation budget, analyze paired pilot and write readable report/figures."""
import argparse,json
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atomwise_ris.core import write_json

def load(p):return [json.loads(x) for x in Path(p).read_text().splitlines()]

def select_budget(root,filename):
    if (root/'benchmark_pilot.jsonl').exists():raise RuntimeError('Budget must be frozen before pilot evaluation')
    if (root/'budget_selection.json').exists():raise FileExistsError('Budget selection already frozen')
    rows=load(root/filename);budgets=sorted(set(x['budget_ms'] for x in rows));methods=sorted(set(x['method'] for x in rows))
    summary=[]
    for b in budgets:
        per={m:np.percentile([x['elapsed_ms'] for x in rows if x['method']==m and x['budget_ms']==b],95) for m in methods}
        active={m:float(np.mean([x['breakdown_ms']['inference']>0 for x in rows if x['method']==m and x['budget_ms']==b]))
                for m in methods if m in ['mlp_ga','attention_ga']}
        # Soft real-time CPU feasibility: 95% complete <= nominal deadline.
        summary.append({'budget_ms':b,'p95_elapsed_ms':per,'neural_inference_fraction':active,
                        'feasible':all(v<=b for v in per.values()) and all(v>=.95 for v in active.values())})
    primary=next((x for x in summary if x['budget_ms']==10 and x['feasible']),None)
    chosen=primary or next((x for x in summary if x['feasible']),None)
    decision={'selected_ms':None if chosen is None else chosen['budget_ms'],'validation':summary,
              'rule':'Prefer 10 ms; otherwise smallest listed budget with every main method p95 complete runtime <= budget and neural inference active on >=95% of cases',
              'frozen_before_pilot':True,'source':filename,'hard_real_time_guarantee':False}
    write_json(root/'budget_selection.json',decision);print(json.dumps(decision,indent=2))

def report(root,filename):
    rows=load(root/filename);decision=json.loads((root/'budget_selection.json').read_text());budget=decision['selected_ms']
    if budget is None:raise RuntimeError('No feasible budget selected on validation; do not claim equal feasible latency')
    chosen=[x for x in rows if x['budget_ms']==budget];methods=sorted(set(x['method'] for x in rows))
    groups=defaultdict(list)
    for x in chosen:groups[x['method']].append(x)
    summary={m:{'mean_rate':float(np.mean([x['rate'] for x in v])),
                'median_rate':float(np.median([x['rate'] for x in v])),
                'p95_elapsed_ms':float(np.percentile([x['elapsed_ms'] for x in v],95)),
                'deadline_miss_fraction':float(np.mean([x['deadline_missed'] for x in v])),
                'mean_evaluations':float(np.mean([x['evaluations'] for x in v]))} for m,v in groups.items()}
    comparisons=[];rng=np.random.default_rng(741)
    baseline={(x['seed'],x['index']):x for x in groups['pair']}
    for method in methods:
        diffs=defaultdict(list)
        for x in groups[method]:
            ref=baseline[x['seed'],x['index']];diffs[x['trajectory']].append(x['rate']-ref['rate'])
        values=np.array([np.mean(v) for v in diffs.values()]);boots=np.mean(rng.choice(values,size=(5000,len(values)),replace=True),axis=1)
        comparisons.append({'method':method,'paired_difference_vs_pair':float(values.mean()),
                            'trajectory_bootstrap_95_interval':np.percentile(boots,[2.5,97.5]).tolist(),
                            'independent_trajectories':len(values)})
    head=json.loads((root/'headroom.json').read_text())['gate']
    learned=next((x for x in comparisons if x['method']=='attention_ga'),None)
    outcome='Keep the simpler controller'
    if learned and learned['trajectory_bootstrap_95_interval'][0]>0:outcome='Investigate learned improvement; physical validation still required'
    summary_obj={'budget_ms':budget,'methods':summary,'paired_comparisons':comparisons,'decision':outcome,
                 'pilot_is_development':True,'headroom_gate':head}
    write_json(root/'summary.json',summary_obj)
    fig,ax=plt.subplots(figsize=(8,4.6))
    for method in methods:
        budgets=sorted(set(x['budget_ms'] for x in rows));means=[]
        for b in budgets:means.append(np.mean([x['rate'] for x in rows if x['method']==method and x['budget_ms']==b]))
        ax.plot(budgets,means,'o-',label=method)
    ax.set(xscale='log',xlabel='Full controller budget (ms)',ylabel='Mean minimum-user spectral efficiency (bit/s/Hz)')
    ax.text(.01,.02,'1 ms neural entries may use initialization only; check inference fractions.',transform=ax.transAxes,fontsize=7)
    ax.legend(fontsize=8,ncol=2);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(root/'rate_runtime.png',dpi=180);fig.savefig(root/'rate_runtime.pdf')
    lines=['# Simulation-only RIS feasibility report','',f'**Decision: {outcome}.**','',
           f'Primary validation-selected budget: **{budget:g} ms**. These are development pilot results, not an untouched paper test.',
           '', '| Controller | Mean worst-user rate (bit/s/Hz) | p95 complete runtime (ms) | Deadline miss fraction |',
           '|---|---:|---:|---:|']
    for m,d in summary.items():lines.append(f"| {m} | {d['mean_rate']:.8f} | {d['p95_elapsed_ms']:.3f} | {d['deadline_miss_fraction']:.3f} |")
    lines+=['','## Paired trajectory analysis','', '| Controller | Difference versus pair search | 95% trajectory bootstrap interval |', '|---|---:|---|']
    for d in comparisons:lines.append(f"| {d['method']} | {d['paired_difference_vs_pair']:.8g} | {d['trajectory_bootstrap_95_interval']} |")
    lines+=['','## Interpretation limits','',
       '- Public Munich geometry, newly traced at nominal 5.53 GHz; exact represented float32 frequency is recorded.',
       '- Independent scalar 8x8 cells. Normal-incidence uniform-panel measurements are extrapolated to a smaller mixed-state array and oblique illumination.',
       '- Cell area is included once via the physical-optics aperture conversion. Mutual coupling, element-specific calibration, and polarization conversion are unmodeled.',
       '- RZF from the all-OFF reference effective channel is fixed within each optimization episode. CSI is exact; channel acquisition and RF switching are outside controller timing.',
       '- The main data use LOS/specular reflections at 5 million rays/source. Diffraction-enabled propagation did not converge sufficiently in the checked settings and is excluded from this first comparison.',
       '- The pilot uses six evaluation trajectories and three paired seeds. This is too small for a final research claim; a future study needs untouched trajectories and more seeds.',
       '- Wall-clock limits are soft CPU deadlines; actual overruns and full timing are reported. All returned improvements were fully evaluated before the internal deadline.',
       '- Pair supervision uses full completed move gains, including harmful first flips. A positive pair-headroom gate alone does not establish a learned speed advantage.',
       '- Large common-phase registration errors can change controller ranking. Fixed-action sensitivity is a stress test, not proof of physical robustness.',
       '- See sensitivity.json, geometry/convergence audits, checkpoint histories, and raw JSONL for evidence. Physical stress envelopes are not measured confidence intervals.',
       '', '![Rate versus runtime](rate_runtime.png)','']
    (root/'REPORT.md').write_text('\n'.join(lines));print(json.dumps(summary_obj,indent=2))

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='outputs/runs/specular_v5');p.add_argument('--select-budget',action='store_true');p.add_argument('--input',default=None);a=p.parse_args();root=Path(a.run)
    if a.select_budget:select_budget(root,a.input or 'benchmark_validation.jsonl')
    else:report(root,a.input or 'benchmark_pilot.jsonl')

if __name__=='__main__':main()
