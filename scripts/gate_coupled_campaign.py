"""Confirm production mesh against a finer mesh, without touching pilot labels."""
import json,time
from pathlib import Path
import numpy as np
from atomwise_ris.physics.nec import geometry,WireGeometry,diagnostics
from atomwise_ris.physics.network import CoupledNetwork
out=Path('outputs/runs/coupled_wire_v1');out.mkdir(parents=True,exist_ok=True)
z81=np.load('outputs/runs/coupling_halfwave64_v1/z_side8_segments81.npy')
p=out/'z_reference161.npy'
if p.exists():z161=np.load(p);timing={'reused':True}
else:z161,timing=geometry(8).impedance(161);np.save(p,z161)
scalar=WireGeometry(np.array([[0.,0.,1.]]),np.array([.024]));zz=scalar.impedance(161)[0].item()
loads=np.array([1+1j*(-zz.imag-70),1+1j*(-zz.imag+70)])
e81=CoupledNetwork(z81,loads);e161=CoupledNetwork(z161,loads,w=e81.w)
rng=np.random.default_rng(43019);errors=[];rate_errors=[]
patterns=[np.zeros(64,int),np.ones(64,int),np.arange(64)%2]+[rng.integers(0,2,64) for _ in range(100)]
for b in patterns:
 h81=e81.channel(b);h161=e161.channel(b)
 errors.append(float(np.linalg.norm(h81-h161)/np.linalg.norm(h161)))
 rate_errors.append(float(abs(e81.score(h81@e81.w)-e161.score(h161@e81.w))))
# Direct loaded solve at production mesh verifies selected load convention.
bl=patterns[3];ld=np.r_[loads[bl],np.full(6,50.)];rhs=np.zeros(70,complex);rhs[64]=1
pred=np.linalg.solve(z81+np.diag(ld),rhs);direct=geometry(8).loaded_current(ld,64,81)
loaded_error=float(np.linalg.norm(pred-direct)/np.linalg.norm(direct))
check=diagnostics(z81);finecheck=diagnostics(z161)
result={'geometry':'3D PEC wire reference, NOT OpenSourceRIS calibration','meshes':[81,161],
 'mesh_max_channel_relative_error':max(errors),'mesh_max_rate_absolute_error':max(rate_errors),
 'mesh_channel_relative_errors':errors,'mesh_rate_absolute_errors':rate_errors,
 'direct_loaded_current_relative_error':loaded_error,'diagnostics':check,'fine_diagnostics':finecheck,
 'fine_timing':timing,'loads_real_ohm':loads.real.tolist(),'loads_imag_ohm':loads.imag.tolist(),
 'thresholds':{'channel_relative':.01,'reciprocity_relative':1e-7,'passivity_singular':1.0001,'loaded_current':1e-5},
 'validation_patterns':len(patterns),'model_validation_not_hardware_validation':True}
result['passed']=bool(max(errors)<.01 and loaded_error<1e-5 and check['reciprocity_relative']<1e-7 and finecheck['reciprocity_relative']<1e-7 and max(check['maximum_scattering_singular_value'],finecheck['maximum_scattering_singular_value'])<1.0001)
(out/'physics_gate.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list) or len(v)<5}),flush=True)
if not result['passed']:raise SystemExit(2)
