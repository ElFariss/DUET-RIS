"""Attach interpretation and physical sensitivity to the generated pilot report."""
import json
from pathlib import Path
root=Path('outputs/runs/coupled_wire_v1');s=json.loads((root/'summary.json').read_text());audit=json.loads((root/'action_mesh_audit.json').read_text());budget=s['primary_ms']
def row(mode,method):return next(x for x in s['conditions'] if x['mode']==mode and x['method']==method and x['budget_ms']==budget)
sp=row('spatial','pair');att=row('spatial','attention_ga');lin=row('temporal','linear_pair');gp=row('temporal','gru_pair');pp=row('temporal','persistence_pair');ga=row('temporal','gru_attention_ga')
lead=f'''## Result in plain language

- **Spatial:** exact pair search achieved {sp['mean_rate']:.4f} bit/s/Hz, compared with {att['mean_rate']:.4f} for attention at {budget} ms. The current attention policy did not beat analytical search after its overhead.
- **Temporal:** linear prediction plus pair search achieved {lin['mean_rate']:.4f}; persistence plus pair search {pp['mean_rate']:.4f}; GRU plus pair search {gp['mean_rate']:.4f}. GRU prediction therefore did not provide a consistent advantage just by being learned.
- **Combined:** GRU plus attention achieved {ga['mean_rate']:.4f}. It must be compared with both the same attention controller under persistence and the simpler linear predictor plus pair search; combining two learned components is not automatically the best option.

These findings select a simpler controller for this pilot. They do not establish that attention can never help. The dataset is small, the attention model has no explicit pairwise edge bias, and training parents are random configurations and their single-flip local optima rather than a full distribution of online memory states. A redesigned model would need a new untouched evaluation set.

'''
p=root/'REPORT.md';text=p.read_text();pos=text.index('## What was simulated');text=text[:pos]+lead+text[pos:]
lines=['## Additional mesh and selected-action audit','',
 '| Frame | Split/use | Maximum channel change | Maximum rate change (bit/s/Hz) |','|---|---|---:|---:|']
for idx,use in [(0,'Training'),(32,'Validation'),(48,'Pilot spatial'),(52,'Pilot temporal')]:
 a=json.loads((root/'mesh_audit'/f'frame_{idx:04d}_161.json').read_text());lines.append(f"| {idx} | {use} | {100*a['max_channel_relative_error']:.3f}% | {a['max_rate_absolute_error']:.5f} |")
lines+=['',f"All four random-pattern channel-norm checks passed the 1% threshold. The rate changes reveal why that threshold alone cannot certify optimizer rankings. For **{audit['actions']} actual returned actions** at one pilot frame per mode, the maximum channel change was **{100*audit['max_channel_relative_error']:.3f}%** and maximum rate change **{audit['max_rate_absolute_error']:.5f} bit/s/Hz** with the original precoder frozen.",'','| Mode | Controller | Coarse rate | Fine rate |','|---|---|---:|---:|']
for mode in ['spatial','temporal']:
 for method in sorted(set(r['method'] for r in audit['records'] if r['mode']==mode)):
  rr=[r for r in audit['records'] if r['mode']==mode and r['method']==method]
  lines.append(f"| {mode} | {method} | {sum(r['coarse_rate'] for r in rr)/len(rr):.5f} | {sum(r['fine_rate'] for r in rr)/len(rr):.5f} |")
lines+=['','These are frame-level checks, not replacements for the trajectory-average tables. No selected configuration was optimized on the finer mesh. Near-tied methods remain unresolved until a larger, finer-mesh and lower-SNR study.']
text=text.replace('## Interpretation boundaries','\n'.join(lines)+'\n\n## Interpretation boundaries')
text=text.replace('two-layer atom attention. Coupling-blind','two-layer atom attention. The no-physics ablation removes additional complex/coupling features but retains exact analytical flip gains. Coupling-blind')
p.write_text(text)
