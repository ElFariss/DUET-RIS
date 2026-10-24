"""Reproducible, restartable 3D thin-wire trajectory generation; no learned labels."""
import argparse,json,time,hashlib,platform,os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from atomwise_ris.physics.nec import geometry,diagnostics

def trajectories():
    rng=np.random.default_rng(20261024);result=[]
    for tr in range(12):
        # Split trajectories before any fields or labels. Interleaved spatial starts
        # make this a held-out trajectory pilot, NOT held-out-environment evidence.
        split=['train','train','validation','pilot'][tr%4]
        base=np.array([[-.38-.025*(tr%3),.20+.035*(tr//3),.98],
                       [-.52-.020*(tr%3),.28+.035*(tr//3),1.05]])
        vel=rng.uniform([-.15,-.7,-.04],[.15,.7,.04],size=(2,3))
        for step in range(16):
            t=step*.02
            pos=base+vel*t
            pos[:,1]+=.006*np.sin(2*np.pi*2*t+tr)*np.array([1.,-1.])
            result.append({'index':tr*16+step,'trajectory':tr,'step':step,'time_s':t,
              'split':split,'users_m':pos.tolist()})
    return result

def work(args):
    row,out,segments=args;out=Path(out);p=out/f"frame_{row['index']:04d}.npz"
    if p.exists():return {'index':row['index'],'status':'existing'}
    g=geometry(8,np.array(row['users_m']));z,info=g.impedance(segments)
    check=diagnostics(z)
    if check['maximum_scattering_singular_value']>1.0001 or check['minimum_resistance_eigenvalue_ohm'] < -1e-6:
        raise RuntimeError('Nonpassive physical extraction')
    np.savez_compressed(p,z=z,centers=g.centers,lengths=g.lengths)
    record=row|info|check|{'hostname':platform.node(),'frequency_hz':g.frequency,'radius_m':g.radius,
       'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    p.with_suffix('.json').write_text(json.dumps(record,indent=2)+'\n')
    return {'index':row['index'],'seconds':info['seconds']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='data/processed/coupled_wire_v1');p.add_argument('--segments',type=int,default=81);p.add_argument('--workers',type=int,default=2);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1)
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=trajectories()
    protocol={'model':'PEC thin-wire NEC-2, free space, no substrate/ground/human blockers',
      'frequency_hz':5.53e9,'cells':64,'bs_antennas':4,'users':2,'segments':a.segments,
      'wire_length_m':.024,'wire_radius_m':.00005,'cell_pitch_yz_m':[.028,.030],
      'dt_s':.02,'frames_per_trajectory':16,'trajectories':12,'train':6,'validation':3,'pilot':3,
      'seed':20261024,'pilot_is_development':True,'rows':rows}
    dest=out/'scenario.json'
    if dest.exists() and json.loads(dest.read_text())!=protocol:raise ValueError('Existing protocol differs')
    dest.write_text(json.dumps(protocol,indent=2)+'\n')
    todo=[(r,str(out),a.segments) for r in rows if r['index']%a.shards==a.shard]
    with ProcessPoolExecutor(a.workers) as pool:
        for result in pool.map(work,todo):print(json.dumps(result),flush=True)
if __name__=='__main__':main()
