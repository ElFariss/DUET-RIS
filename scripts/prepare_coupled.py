"""Freeze data inventory; generate pair supervision only from train/validation."""
import json,hashlib
from pathlib import Path
import numpy as np
from atomwise_ris.physics.network import CoupledNetwork
root=Path('outputs/runs/coupled_wire_v1');data=Path('data/processed/coupled_wire_v1')
gate=json.loads((root/'physics_gate.json').read_text())
if not gate['passed']:raise RuntimeError('Physical gate failed')
rows=json.loads((data/'scenario.json').read_text())['rows'];zs=[];manifest=[]
for row in rows:
 p=data/f"frame_{row['index']:04d}.npz";meta=json.loads(p.with_suffix('.json').read_text());digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if digest!=meta['sha256']:raise ValueError('Frame hash mismatch')
 zs.append(np.load(p)['z']);manifest.append({'path':str(p),'sha256':digest})
z=np.array(zs);np.savez_compressed(data/'dataset.npz',z=z,split=np.array([r['split'] for r in rows]),trajectory=np.array([r['trajectory'] for r in rows]),step=np.array([r['step'] for r in rows]))
(data/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
loads=np.array(gate['loads_real_ohm'])+1j*np.array(gate['loads_imag_ohm']);rng=np.random.default_rng(3119)
headroom=[]
for split in ['train','validation']:
 xs=[];ys=[];ans=[];masks=[];weights=[]
 for row,zz in zip(rows,z):
  if row['split']!=split:continue
  ev=CoupledNetwork(zz,loads)
  for parent in range(8):
   st=ev.state(rng.integers(0,2,64,dtype=np.int8))
   if parent>=4:
    for _ in range(100):
     scores=ev.moves(st);j=int(np.argmax(scores))
     if scores[j]<=ev.score(st.field)+1e-10:break
     st=ev.flip(st,[j])
   base=float(ev.score(st.field));singles=ev.moves(st)-base;pairs=ev.moves(st,True)-base
   marginal=singles.copy()
   for j,(i,k) in enumerate(ev.pairs):marginal[i]=max(marginal[i],pairs[j]);marginal[k]=max(marginal[k],pairs[j])
   firsttarget=.5*singles+.5*marginal
   headroom.append({'split':split,'index':row['index'],'local_parent':parent>=4,'single_gain':float(singles.max()),'pair_gain':float(pairs.max()),'harmful_first_pair':int(sum((pairs>1e-8)&(singles[ev.pairs[:,0]]<0)&(singles[ev.pairs[:,1]]<0)))})
   def add(first,gains,weight):
    x,g=ev.features(st,first);scale=max(float(np.std(g)),1e-4);an=g/scale
    mask=np.zeros(64,bool)
    if first>=0:mask[first]=True
    logits=np.clip(gains/scale,-30,30);logits[mask]=-1000;target=np.exp(logits-logits.max());target/=target.sum()
    xs.append(x);ys.append(target);ans.append(an);masks.append(mask);weights.append(weight)
   add(-1,firsttarget,1.)
   for first in [int(ev.pairs[np.argmax(pairs),0]),int(rng.integers(64))]:
    gain=np.full(64,-1e9)
    for p,(i,j) in enumerate(ev.pairs):
     if i==first:gain[j]=pairs[p]
     if j==first:gain[i]=pairs[p]
    add(first,gain,.25)
 np.savez_compressed(root/f'{split}_labels.npz',x=np.array(xs,np.float32),target=np.array(ys,np.float32),analytical=np.array(ans,np.float32),mask=np.array(masks),weight=np.array(weights,np.float32))
 print(split,len(xs),flush=True)
(root/'headroom.json').write_text(json.dumps(headroom,indent=2)+'\n')
tr=np.load(root/'train_labels.npz');mean=tr['x'].mean((0,1));std=tr['x'].std((0,1));std=np.maximum(std,1e-5)
# Preserve binary and coordinate semantics, particularly conditional marker.
mean[[0,1,2,15]]=0;std[[0,1,2,15]]=1
np.savez(root/'feature_scaling.npz',mean=mean,std=std)
summary={'parents':len(headroom),'beneficial_pairs_at_single_local_optima':sum(r['local_parent'] and r['pair_gain']>1e-8 for r in headroom),'train':sum(r['split']=='train' for r in headroom),'validation':sum(r['split']=='validation' for r in headroom),'pilot_used_for_labels':False}
(root/'headroom_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
