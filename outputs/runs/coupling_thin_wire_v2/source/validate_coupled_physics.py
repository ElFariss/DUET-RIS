"""Fail-closed numerical gate before a coupled controller campaign."""
import argparse,json,time
from pathlib import Path
import numpy as np
from atomwise_ris.physics.nec import WireGeometry,geometry,diagnostics,scattering

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='outputs/runs/coupling_physics_v1');p.add_argument('--side',type=int,default=2);p.add_argument('--segments',default='7,11,15,21')
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    meshes=list(map(int,a.segments.split(',')));geom=geometry(a.side);nr=a.side**2
    zs=[];record=[]
    for mesh in meshes:
        z,timing=geom.impedance(mesh);zs.append(z)
        row={'segments':mesh,**timing,**diagnostics(z)};record.append(row)
        np.save(out/f'z_side{a.side}_segments{mesh}.npy',z)
        print(json.dumps(row),flush=True)
    # Single-wire resonance defines loads; no optimization labels used.
    single=WireGeometry(np.array([[0.,0.,1.]]),np.array([.011]))
    zself,_=single.impedance(meshes[-1]);resonance=-zself[0,0].imag
    states=np.array([1+1j*(resonance-20),1+1j*(resonance+20)])
    rng=np.random.default_rng(1907);validation=[]
    for q in range(5):
        bits=rng.integers(0,2,nr);loads=np.r_[states[bits],np.full(6,50.)]
        rhs=np.zeros(len(loads),complex);rhs[nr]=1
        predicted=np.linalg.solve(zs[-1]+np.diag(loads),rhs)
        full=geom.loaded_current(loads,nr,meshes[-1])
        rel=float(np.linalg.norm(predicted-full)/np.linalg.norm(full))
        validation.append({'bits':bits.tolist(),'relative_current_error':rel})
    # Loaded transfer converges more meaningfully than mostly reactive raw Z.
    channel_errors=[]
    for z0,z1 in zip(zs[:-1],zs[1:]):
        errors=[]
        for bits in [np.zeros(nr,int),np.ones(nr,int),np.arange(nr)%2]:
            loads=np.r_[states[bits],np.full(6,50.)]
            rhs=np.eye(len(loads))[:,nr:nr+4]
            h0=np.linalg.solve(z0+np.diag(loads),rhs)[-2:]
            h1=np.linalg.solve(z1+np.diag(loads),rhs)[-2:]
            errors.append(float(np.linalg.norm(h0-h1)/np.linalg.norm(h1)))
        channel_errors.append({'meshes':[record[len(channel_errors)]['segments'],record[len(channel_errors)+1]['segments']], 'max_loaded_channel_relative_error':max(errors),'pattern_errors':errors})
    result={'geometry':'3D free-space PEC thin-wire MoM; no PCB, substrate, switch or measured calibration',
       'frequency_hz':geom.frequency,'radius_m':geom.radius,'side':a.side,
       'loads_real_ohm':states.real.tolist(),'loads_imag_ohm':states.imag.tolist(),
       'mesh':record,'loaded_solver_validation':validation,'mesh_channel_comparison':channel_errors,
       'thresholds':{'reciprocity':1e-7,'passivity_singular':1.0001,'loaded_solver':1e-5,'mesh_channel':.01}}
    result['passed']=bool(all(r['reciprocity_relative']<1e-7 and r['maximum_scattering_singular_value']<1.0001 for r in record)
        and max(v['relative_current_error'] for v in validation)<1e-5 and channel_errors[-1]['max_loaded_channel_relative_error']<.01)
    (out/f'gate_side{a.side}.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASSED',result['passed'],'loaded validation',validation,'mesh',channel_errors,flush=True)
    if not result['passed']:raise SystemExit(2)
if __name__=='__main__':main()
