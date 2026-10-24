"""Refine predeclared train/validation/pilot frames; retain matrices for action audit."""
import argparse,json
from pathlib import Path
import numpy as np
from atomwise_ris.physics.nec import geometry,diagnostics
from atomwise_ris.physics.network import CoupledNetwork
p=argparse.ArgumentParser();p.add_argument('--indices',default='0,32,48');a=p.parse_args()
data=Path('data/processed/coupled_wire_v1');out=Path('outputs/runs/coupled_wire_v1/mesh_audit');out.mkdir(parents=True,exist_ok=True)
gate=json.loads(Path('outputs/runs/coupled_wire_v1/physics_gate.json').read_text());loads=np.array(gate['loads_real_ohm'])+1j*np.array(gate['loads_imag_ohm'])
for idx in map(int,a.indices.split(',')):
 ds=np.load(data/f'frame_{idx:04d}.npz');z=ds['z'];users=ds['centers'][-2:];path=out/f'frame_{idx:04d}_161.npz'
 if path.exists():fine=np.load(path)['z'];timing={'reused':True}
 else:fine,timing=geometry(8,users).impedance(161);np.savez_compressed(path,z=fine)
 ev=CoupledNetwork(z,loads);ref=CoupledNetwork(fine,loads,w=ev.w);rng=np.random.default_rng(4901)
 errors=[];rates=[]
 for b in [np.zeros(64,int),np.ones(64,int),np.arange(64)%2]+[rng.integers(0,2,64) for _ in range(30)]:
  h=ev.channel(b);hf=ref.channel(b);errors.append(float(np.linalg.norm(h-hf)/np.linalg.norm(hf)));rates.append(float(abs(ev.score(h@ev.w)-ref.score(hf@ev.w))))
 result={'index':idx,'timing':timing,'diagnostics':diagnostics(fine),'max_channel_relative_error':max(errors),'max_rate_absolute_error':max(rates),'patterns':len(errors),'passed':max(errors)<.01}
 path.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
