"""Report completed controller measurements without selecting on pilot outcomes."""
import json,csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('outputs/runs/coupled_wire_v1');figdir=root/'figures';figdir.mkdir(exist_ok=True)
selection=json.loads((root/'budget_selection.json').read_text());primary=selection['selected_ms'];rows=[]
for mode in ['spatial','temporal']:
 p=root/f'benchmark_{mode}_pilot.jsonl';rows.extend(json.loads(l) for l in p.read_text().splitlines())
summary=[]
for mode in ['spatial','temporal']:
 for method in sorted(set(r['method'] for r in rows if r['mode']==mode)):
  for budget in [1,5,10,50,100]:
   sample=[r for r in rows if r['mode']==mode and r['method']==method and r['budget_ms']==budget]
   if not sample:continue
   summary.append({'mode':mode,'method':method,'budget_ms':budget,'n':len(sample),
     'mean_rate':float(np.mean([r['rate'] for r in sample])),
     'median_ms':float(np.median([r['elapsed_ms'] for r in sample])),
     'p95_ms':float(np.quantile([r['elapsed_ms'] for r in sample],.95)),
     'deadline_misses':sum(r['deadline_missed'] for r in sample),
     'mean_forecast_ms':float(np.mean([r['breakdown_ms']['forecast_ms'] for r in sample])),
     'mean_evaluations':float(np.mean([r['evaluations'] for r in sample]))})
def comparison(mode,a,b):
 vals=[];trajs=sorted(set(r['trajectory'] for r in rows if r['mode']==mode))
 for tr in trajs:
  aa=[r['rate'] for r in rows if r['mode']==mode and r['budget_ms']==primary and r['trajectory']==tr and r['method']==a]
  bb=[r['rate'] for r in rows if r['mode']==mode and r['budget_ms']==primary and r['trajectory']==tr and r['method']==b]
  vals.append(float(np.mean(aa)-np.mean(bb)))
 rng=np.random.default_rng(13);boot=np.array(vals)[rng.integers(len(vals),size=(10000,len(vals)))].mean(1)
 return {'mode':mode,'a':a,'b':b,'mean_paired_difference':float(np.mean(vals)),'trajectory_differences':vals,'descriptive_bootstrap_95':np.quantile(boot,[.025,.975]).tolist(),'independent_trajectories':len(vals)}
contrasts=[]
if primary is not None:
 for mode,a,b in [('spatial','attention_ga','pair'),('spatial','mlp_ga','pair'),('spatial','pair','blind_pair'),('spatial','attention_ga','mlp_ga'),('spatial','attention_ga','attention_no_physics_ga'),('spatial','attention_ga','attention_no_memory_ga'),('spatial','analytical_ga','memory_ga'),('spatial','memory_ga','pair'),('temporal','gru_pair','persistence_pair'),('temporal','linear_pair','persistence_pair'),('temporal','gru_pair','linear_pair'),('temporal','oracle_pair','persistence_pair'),('temporal','gru_attention_ga','persistence_attention_ga'),('temporal','gru_attention_ga','gru_mlp_ga'),('temporal','gru_mlp_ga','gru_pair')]:contrasts.append(comparison(mode,a,b))
(root/'summary.json').write_text(json.dumps({'primary_ms':primary,'conditions':summary,'paired_comparisons':contrasts,'rows':len(rows),'trajectory_bootstrap_is_descriptive_only':True},indent=2)+'\n')
with (root/'summary.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
colors={'pair':'#1d4ed8','greedy':'#64748b','blind_pair':'#dc2626','memory_ga':'#a16207','analytical_ga':'#0f766e','mlp_ga':'#9333ea','attention_ga':'#e8790c','persistence_pair':'#64748b','linear_pair':'#16a34a','gru_pair':'#7c3aed','oracle_pair':'#1d4ed8','gru_attention_ga':'#ea580c','persistence_attention_ga':'#a16207'}
plt.rcParams.update({'font.size':10,'savefig.dpi':200})
fig,axs=plt.subplots(1,2,figsize=(12,4.8))
for ax,mode in zip(axs,['spatial','temporal']):
 methods=['pair','greedy','blind_pair','analytical_ga','mlp_ga','attention_ga'] if mode=='spatial' else ['persistence_pair','linear_pair','gru_pair','oracle_pair','persistence_attention_ga','gru_attention_ga']
 for method in methods:
  rr=sorted([r for r in summary if r['mode']==mode and r['method']==method],key=lambda r:r['budget_ms']);ax.plot([r['budget_ms'] for r in rr],[r['mean_rate'] for r in rr],'-o',label=method.replace('_',' '),color=colors[method],ms=4)
 ax.set(xscale='log',xlabel='Complete CPU budget (ms)',ylabel='Mean weakest-user rate (bit/s/Hz)',title='Spatial control: current CSI' if mode=='spatial' else 'Temporal control: 20 ms stale CSI');ax.grid(alpha=.2);ax.legend(fontsize=8)
 if primary is not None:ax.axvline(primary,color='black',alpha=.25,ls=':')
fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(figdir/f'rate_runtime.{ext}')
plt.close(fig)
if primary is not None:
 fig,axs=plt.subplots(1,2,figsize=(12,4.6))
 for ax,mode in zip(axs,['spatial','temporal']):
  methods=['pair','blind_pair','attention_ga'] if mode=='spatial' else ['persistence_pair','linear_pair','gru_pair','oracle_pair']
  for method in methods:
   sample=[r for r in rows if r['mode']==mode and r['budget_ms']==primary and r['method']==method and r['trajectory']==3]
   steps=sorted(set(r['step'] for r in sample));rates=[np.mean([r['rate'] for r in sample if r['step']==s]) for s in steps];ax.plot(np.array(steps)*20,rates,'-o',ms=3,color=colors[method],label=method.replace('_',' '))
  ax.set(xlabel='Time along trajectory 3 (ms)',ylabel='Weakest-user rate (bit/s/Hz)',title=f'{mode.title()} example at {primary} ms');ax.legend(fontsize=8);ax.grid(alpha=.2)
 fig.tight_layout()
 for ext in ['png','pdf']:fig.savefig(figdir/f'trajectory_rates.{ext}')
 plt.close(fig)
gate=json.loads((root/'physics_gate.json').read_text());head=json.loads((root/'headroom_summary.json').read_text());effect=json.loads((root/'coupling_effect.json').read_text())
lines=['# Coupled RIS: spatial and temporal feasibility report','',
 'This is a completed **development pilot**, not hardware validation or a final paper test. The original independent-cell Munich `specular_v5` run is preserved. This new experiment uses a different, fully specified wire surface and free-space geometry; its absolute rates must not be interpreted as the effect of adding coupling to Munich.','',
 '## What was simulated','',
 'A 5.53 GHz 3D PEC wire model includes all 64 RIS elements, four BS antennas and two UE antennas in a 70-port NEC-2 method-of-moments solve. Wires are 24 mm long and 50 μm in radius; the panel pitches are 28 and 30 mm. Each center port selects one of two loads: 1 − j10.799 Ω or 1 + j129.201 Ω. The production mesh has 81 segments per wire (5,670 unknowns). The reference uses 161 (11,270 unknowns). There is no substrate, ground plane, real switch model, material loss, city geometry or moving human blockage.','',
 'The channel is a power-wave transfer matrix with 50 Ω external references. The fixed all-OFF-reference RZF precoder has 0.1 W total **incident** BS power; mismatch means this is not identical to radiated power. The objective is minimum user spectral efficiency with multiuser interference, 1 MHz bandwidth, 290 K and 7 dB noise figure. Exact Schur reduction and rank-one/rank-two updates are shared by learned and analytical controllers.','',
 '![Actual geometry and coupling strength](figures/geometry_3d.png)','',
 'The 3D height map shows summed off-diagonal impedance magnitude, not received signal strength or a measured field map.','',
 '## Physics evidence','',
 f"Across 103 reference-geometry patterns, doubling the mesh changed the complex channel by at most **{100*gate['mesh_max_channel_relative_error']:.3f}%** and the rate by at most **{gate['mesh_max_rate_absolute_error']:.5f} bit/s/Hz**. Direct loaded NEC currents and network predictions differed by **{gate['direct_loaded_current_relative_error']:.2e}** relative norm. Passivity and reciprocity checks passed at the reference geometry; passivity was also checked for all 192 frames. Additional moving-frame and optimizer-action mesh audits are recorded separately below.",'',
 f"On 250 random configurations of a training frame, removing inter-element coupling changed rate predictions by **{effect['mean_absolute_rate_prediction_error']:.4f} bit/s/Hz** mean absolute error. This is evidence that the approximation matters in this geometry, not evidence that attention is needed.",'',
 '![Coupling and model mismatch](figures/coupling_effect.png)','',
 '## Experimental separation','',
 '- **Spatial:** current complete network observations; compare greedy, pair, random, memory GA, analytical-guided GA, shared MLP and two-layer atom attention. Coupling-blind pair search removes inter-RIS off-diagonal impedance only in its internal prediction; every action is scored on the same fully coupled truth. Its reference precoder is shared with the other methods.',
 '- **Temporal:** four perfect past network observations at 20 ms intervals; predict one frame ahead. Compare persistence, linear extrapolation and a shared GRU. Forecast matrices are projected to passive reciprocal matrices. All use the same precoder derived from the last observation. Current-CSI pair search is an information oracle, not a global optimization upper bound.',
 '- **Joint:** compare MLP and attention mutation with persistence versus GRU predictions. The comparison changes the forecast while holding the downstream controller fixed.',
 '- **Information limit:** complete multiport impedance observations are an idealized input. We have not demonstrated affordable channel acquisition, an IoT implementation or human-blockage prediction. Attention uses per-atom coupled-network features; this version has no explicit edge-biased graph attention.','',
 'Twelve whole receiver trajectories have 16 snapshots each. Six trajectories train, three select checkpoints/budgets, and three form a development pilot. There is no frame mixing across splits, but all trajectories share one surface and free-space scene. Three seeds (7, 19, 43) repeat each controller. The MLP has 14,113 parameters, attention 17,665 and the shared temporal GRU 1,090. Training uses 25 epochs with validation checkpoint selection.','',
 f"Training used 2,304 labeled examples and validation 1,152, derived from completed single/pair gains. Among 1,152 parents, **{head['beneficial_pairs_at_single_local_optima']}** single-flip local optima admitted improving pairs. The second-action target includes pairs with harmful individual flips; all 2,016 pairs are evaluated offline for supervision.",'',
 f"## Pilot results at the validation-selected {primary} ms budget" if primary is not None else '## No common feasible budget','',
 'CPU timing includes forecasts, feature preparation, network preparation, precoding, memory, inference and candidate evaluation. It excludes one-time model loading, EM generation, channel acquisition and the environmental evaluation of the already returned action. All methods run sequentially on the same CPU core. Any deadline misses remain reported; no late candidate improvement is accepted.','',
 '| Mode | Controller | Mean rate (bit/s/Hz) | p95 runtime (ms) | Mean evaluations | Deadline misses |','|---|---|---:|---:|---:|---:|']
for r in sorted([r for r in summary if r['budget_ms']==primary],key=lambda r:(r['mode'],-r['mean_rate'])):lines.append(f"| {r['mode']} | {r['method']} | {r['mean_rate']:.6f} | {r['p95_ms']:.3f} | {int(round(r['mean_evaluations']))} | {r['deadline_misses']}/{r['n']} |")
lines+=['','![Runtime curves](figures/rate_runtime.png)','','All budget curves include observed overruns; consult `summary.csv` and the raw records before making a deadline claim.','','## Paired differences','','Differences average optimizer seeds and frames within each trajectory first. With only three independent pilot trajectories, bootstrap intervals below are descriptive and cannot establish general superiority.','','| Comparison | Mean difference (bit/s/Hz) | Descriptive 95% interval |','|---|---:|---|']
for c in contrasts:lo,hi=c['descriptive_bootstrap_95'];lines.append(f"| {c['a']} − {c['b']} | {c['mean_paired_difference']:+.6f} | [{lo:+.6f}, {hi:+.6f}] |")
lines+=['','![Example moving trajectory](figures/trajectory_rates.png)','','## Interpretation boundaries','','Coupling-aware modeling, attention, multiport reduction and channel prediction all have existing literature. This pilot tests whether their computational tradeoffs are useful in one specified scenario. It cannot establish novelty simply by combining them. Small optimizer differences need to survive the mesh/action audit, a broader geometry/mobility study, uncertain/noisy/stale channel acquisition, and an untouched final evaluation.','','The short free-space links and high incident power produce high-SNR cases that are particularly sensitive to interference cancellation. A small complex-channel error can cause a much larger rate error; channel-norm convergence alone must not be treated as rate convergence.','',
 'The earlier Munich result and this wire-model result answer different physical questions. A more faithful OpenSourceRIS extension still needs its PCB/substrate/switch EM model or measured mixed-pattern multiport calibration. Uniform ON/OFF panel curves cannot identify that matrix.','','## References and artifacts','','The live literature matrix contains 28 papers, including all papers in the saved Consensus research document and the numerical-model references used here. The existing Zheng et al. coupling-validation entry now cites its 2024 journal version. Reading statuses were preserved.','','- [Live matrix](https://docs.google.com/spreadsheets/d/1Sa4wgYj23wOWy7-iLMHDoRCzCFPBmKHrnyzRfWbavOg/edit)','','- [Consensus research](https://consensus.app/search/we-are-extending-a-simulation-only-1-bit-ris-contr/0fUy254zRdOo9479vnAKiQ/)','','- [Multiport framework, Nerini et al.](https://doi.org/10.1109/TWC.2024.3416825)','','- [Full-wave validation, Abrardo et al.](https://doi.org/10.1109/TWC.2024.3450722)','','- [Measured coupling validation, Zheng et al.](https://doi.org/10.1109/TWC.2024.3451548)','','- [Efficient physical channel computation, Prod’homme and del Hougne](https://doi.org/10.1109/LCOMM.2023.3330527)','','- [Discrete multiport optimization, Hammami et al.](https://doi.org/10.1109/LWC.2026.3652464)','','- [Spatio-temporal channel prediction, Liu et al.](https://doi.org/10.1109/TCOMM.2022.3215198)','','`provenance.json`, `source_snapshot.tar.gz`, the dataset manifest, per-frame metadata, model histories/checkpoints and all JSONL controller records are retained. Large binary arrays/checkpoints remain in the local and lab workspace; source, reports, figures and metadata are published in Git.']
(root/'REPORT.md').write_text('\n'.join(lines)+'\n');print('Wrote',root/'REPORT.md',len(rows),'pilot trials')
