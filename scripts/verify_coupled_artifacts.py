"""Fail on missing cases, leaking split membership or non-finite controller results."""
import json,hashlib
from pathlib import Path
import numpy as np
root=Path('outputs/runs/coupled_wire_v1');data=Path('data/processed/coupled_wire_v1');ds=np.load(data/'dataset.npz')
assert ds['z'].shape==(192,70,70)
for tr in np.unique(ds['trajectory']):assert len(np.unique(ds['split'][ds['trajectory']==tr]))==1
records=[]
for mode,nmethods,nframes in [('spatial',10,48),('temporal',8,36)]:
 for split in ['validation','pilot']:
  path=root/f'benchmark_{mode}_{split}.jsonl';rows=[json.loads(l) for l in path.read_text().splitlines()]
  assert len(rows)==nmethods*nframes*3*5,(path,len(rows))
  keys=[(r['method'],r['seed'],r['budget_ms'],r['index']) for r in rows];assert len(set(keys))==len(keys)
  for r in rows:
   assert ds['split'][r['index']]==split
   assert r['trajectory']==int(ds['trajectory'][r['index']])
   assert np.isfinite(r['rate']) and r['rate']>=0 and np.isfinite(r['elapsed_ms'])
   assert len(r['bits'])==64 and set(r['bits'])<={0,1}
   if mode=='temporal':assert ds['step'][r['index']]>=4 and ds['trajectory'][r['index']-4]==r['trajectory']
  records.append({'file':str(path),'rows':len(rows),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for p in data.glob('frame_*.npz'):
 assert hashlib.sha256(p.read_bytes()).hexdigest()==json.loads(p.with_suffix('.json').read_text())['sha256']
selection=json.loads((root/'budget_selection.json').read_text())
for name,digest in selection['input_hashes'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
out={'passed':True,'trials':sum(r['rows'] for r in records),'checkpoints':len(list(root.glob('models/*/best.pt'))),'trajectory_splits_disjoint':True,'all_frame_hashes_match':True,'validation_budget_inputs_match':True,'records':records}
assert out['checkpoints']==12
(root/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
