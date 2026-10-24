"""Re-evaluate returned actions at a finer EM mesh without reoptimizing them."""
import json
from pathlib import Path
import numpy as np
from atomwise_ris.physics.network import CoupledNetwork
root=Path('outputs/runs/coupled_wire_v1');data=Path('data/processed/coupled_wire_v1')
gate=json.loads((root/'physics_gate.json').read_text());loads=np.array(gate['loads_real_ohm'])+1j*np.array(gate['loads_imag_ohm']);ds=np.load(data/'dataset.npz');z=ds['z'];primary=json.loads((root/'budget_selection.json').read_text())['selected_ms'];records=[]
for mode,idx in [('spatial',48),('temporal',52)]:
 fine=np.load(root/'mesh_audit'/f'frame_{idx:04d}_161.npz')['z']
 w=CoupledNetwork(z[idx if mode=='spatial' else idx-1],loads).w
 ev=CoupledNetwork(z[idx],loads,w=w);ref=CoupledNetwork(fine,loads,w=w)
 rows=[json.loads(l) for l in (root/f'benchmark_{mode}_pilot.jsonl').read_text().splitlines()]
 for row in rows:
  if row['index']!=idx or row['budget_ms']!=primary:continue
  h=ev.channel(row['bits']);hf=ref.channel(row['bits']);rate=float(ref.score(hf@w));coarse=float(ev.score(h@w))
  if abs(coarse-row['rate'])>1e-8:raise AssertionError('Action/source mismatch')
  records.append({'mode':mode,'index':idx,'method':row['method'],'seed':row['seed'],'coarse_rate':coarse,'fine_rate':rate,'rate_difference':rate-coarse,'relative_channel_error':float(np.linalg.norm(h-hf)/np.linalg.norm(hf))})
summary={'primary_budget_ms':primary,'actions':len(records),'max_channel_relative_error':max(r['relative_channel_error'] for r in records),'max_rate_absolute_error':max(abs(r['rate_difference']) for r in records),'scope':'One predeclared pilot frame per mode, all returned methods and seeds; frozen precoder; no reoptimization','records':records}
(root/'action_mesh_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:v for k,v in summary.items() if k!='records'})
