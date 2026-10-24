"""Adversarial numerical audit at the frame with largest optimizer separation."""
import json
from pathlib import Path
import numpy as np
from atomwise_ris.physics.network import CoupledNetwork
root=Path('outputs/runs/coupled_wire_v1');selection=json.loads((root/'posthoc_mesh_selection.json').read_text());idx=selection['index'];gate=json.loads((root/'physics_gate.json').read_text());loads=np.array(gate['loads_real_ohm'])+1j*np.array(gate['loads_imag_ohm']);z=np.load(f'data/processed/coupled_wire_v1/frame_{idx:04d}.npz')['z'];fine=np.load(root/'mesh_audit'/f'frame_{idx:04d}_161.npz')['z'];ev=CoupledNetwork(z,loads);ref=CoupledNetwork(fine,loads,w=ev.w);rows=[json.loads(l) for l in (root/'benchmark_spatial_pilot.jsonl').read_text().splitlines()];records=[]
for r in rows:
 if r['index']!=idx or r['budget_ms']!=10:continue
 rate=float(ref.score(ref.channel(r['bits'])@ev.w));records.append({'method':r['method'],'seed':r['seed'],'coarse_rate':r['rate'],'fine_rate':rate})
def mean(kind,field):return float(np.mean([r[field] for r in records if r['method']==kind]))
result=selection|{'records':records,'fine_pair_minus_attention':mean('pair','fine_rate')-mean('attention_ga','fine_rate'),'fine_pair_rate':mean('pair','fine_rate'),'fine_attention_rate':mean('attention_ga','fine_rate')}
(root/'posthoc_mesh_audit.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='records'})
