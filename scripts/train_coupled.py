import argparse,json,time,hashlib
from pathlib import Path
import numpy as np
import torch
from atomwise_ris.models.coupled_policy import CoupledPolicy,LinkGRU

def main():
 p=argparse.ArgumentParser();p.add_argument('--kind',choices=['mlp','attention','attention_no_physics','gru'],required=True);p.add_argument('--seed',type=int,default=7);p.add_argument('--epochs',type=int,default=25);p.add_argument('--device',default='cuda');p.add_argument('--run',default='outputs/runs/coupled_wire_v1');a=p.parse_args()
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 root=Path(a.run);out=root/'models'/f'{a.kind}_seed{a.seed}';out.mkdir(parents=True,exist_ok=True)
 if (out/'metadata.json').exists():raise FileExistsError(out)
 if not json.loads((root/'physics_gate.json').read_text())['passed']:raise RuntimeError('Physics gate')
 start=time.perf_counter()
 if a.kind=='gru':
  ds=np.load('data/processed/coupled_wire_v1/dataset.npz');z=ds['z'];upper=np.triu_indices(70)
  links=z[:,upper[0],upper[1]];train=ds['split']=='train'
  mean=links[train].mean(0);scale=np.maximum(np.std(links[train],0),1e-6);normalized=(links-mean)/scale
  active_mask=(scale>0.01)
  weights=(scale/scale.mean()).clip(0.05,10.0)
  np.savez(out/'scaling.npz',mean=mean,scale=scale,upper=np.array(upper),active_mask=active_mask)
  def data(split):
   x=[];y=[];w=[]
   for idx in range(len(z)):
    if ds['split'][idx]!=split or ds['step'][idx]<4:continue
    h=normalized[idx-4:idx].T;target=normalized[idx]
    x.append(np.stack([h.real,h.imag],-1));y.append(np.stack([target.real,target.imag],-1))
    w.append(weights)
   return (torch.tensor(np.concatenate(x),dtype=torch.float32,device=a.device),
           torch.tensor(np.concatenate(y),dtype=torch.float32,device=a.device),
           torch.tensor(np.concatenate(w),dtype=torch.float32,device=a.device))
  tr=data('train');va=data('validation');model=LinkGRU().to(a.device)
  def loss(d,idx):
   diff=model(d[0][idx])-d[1][idx]
   return (((diff**2).sum(-1))*d[2][idx]).mean()
  ntr=len(tr[0]);nva=len(va[0]);batch=2048
 else:
  scaling=np.load(root/'feature_scaling.npz');mean=scaling['mean'];std=scaling['std']
  def data(split):
   ds=np.load(root/f'{split}_labels.npz');d={k:torch.tensor(ds[k],device=a.device) for k in ['target','analytical','mask','weight']};d['x']=torch.tensor((ds['x']-mean)/std,device=a.device);return d
  tr=data('train');va=data('validation');model=CoupledPolicy(kind='mlp' if a.kind=='mlp' else 'attention',physics=a.kind!='attention_no_physics').to(a.device)
  def loss(d,idx):
   pred=model(d['x'][idx],d['analytical'][idx]).masked_fill(d['mask'][idx],-1e9)
   per=-(d['target'][idx]*pred.log_softmax(-1)).sum(-1)
   return (per*d['weight'][idx]).sum()/d['weight'][idx].sum()
  ntr=len(tr['x']);nva=len(va['x']);batch=64
 opt=torch.optim.AdamW(model.parameters(),lr=3e-4,weight_decay=1e-3);best=float('inf');hist=[]
 for epoch in range(a.epochs):
  model.train();values=[]
  for ix in torch.randperm(ntr,device=a.device).split(batch):
   opt.zero_grad(set_to_none=True);l=loss(tr,ix);l.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);opt.step();values.append(l.item())
  model.eval()
  with torch.inference_mode():
   vals=[(loss(va,ix).item(),len(ix)) for ix in torch.arange(nva,device=a.device).split(batch)];vl=sum(v*n for v,n in vals)/sum(n for v,n in vals)
  hist.append({'epoch':epoch+1,'train':float(np.mean(values)),'validation':vl,'seconds':time.perf_counter()-start})
  if vl<best:best=vl;torch.save({'state_dict':model.state_dict(),'kind':a.kind,'seed':a.seed,'epoch':epoch+1,
                                'architecture_version':model.architecture_version},out/'best.pt')
  if (epoch+1)%5==0:print(a.kind,a.seed,hist[-1],flush=True)
 (out/'history.json').write_text(json.dumps(hist,indent=2)+'\n')
 (out/'metadata.json').write_text(json.dumps({'args':vars(a),'parameters':sum(p.numel() for p in model.parameters()),'best_validation':best,'seconds':time.perf_counter()-start,'training_examples':ntr,'validation_examples':nva,'torch':torch.__version__,'cuda':torch.cuda.get_device_name() if a.device=='cuda' else None,'architecture_version':model.architecture_version},indent=2)+'\n')
if __name__=='__main__':main()
