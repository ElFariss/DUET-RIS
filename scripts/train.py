import argparse
import json
from pathlib import Path
import time
import numpy as np
import torch
from atomwise_ris.models import EditPolicy
from atomwise_ris.core import write_json,sha256,source_versions

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='outputs/runs/specular_v5');p.add_argument('--kind',choices=['mlp','attention'],default='attention')
    p.add_argument('--seed',type=int,default=7);p.add_argument('--epochs',type=int,default=30)
    p.add_argument('--no-physics',action='store_true');p.add_argument('--no-conditioning',action='store_true');p.add_argument('--device',default='cuda')
    a=p.parse_args();root=Path(a.run);gate=json.loads((root/'headroom.json').read_text())['gate']
    if gate['decision']!='bounded_training':raise RuntimeError('Training gate did not pass')
    torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
    if a.device=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA requested but unavailable')
    def load(split):
        z=np.load(root/f'{split}_labels.npz')
        data={k:torch.as_tensor(z[k],device=a.device) for k in ['x','target','analytical','mask']}
        # One first action per mutation, half a second action on average.
        # Two sampled conditional examples each receive weight .25.
        data['weight']=torch.as_tensor(np.where(z['stage']=='first',1.,.25),device=a.device,dtype=torch.float32)
        return data
    tr=load('train');va=load('validation')
    model=EditPolicy(tr['x'].shape[-1],a.kind,not a.no_physics,not a.no_conditioning).to(a.device)
    opt=torch.optim.AdamW(model.parameters(),lr=3e-4,weight_decay=1e-3)
    tag=f'{a.kind}'+('_no_physics' if a.no_physics else '')+('_no_conditioning' if a.no_conditioning else '')+f'_seed{a.seed}'
    out=root/'models'/tag;out.mkdir(parents=True,exist_ok=True)
    if (out/'metadata.json').exists():raise FileExistsError('Completed model exists; choose a new --run to preserve it')
    def loss(data,idx):
        pred=model(data['x'][idx],data['analytical'][idx]);pred=pred.masked_fill(data['mask'][idx],-1e9)
        losses=-(data['target'][idx]*torch.log_softmax(pred,dim=-1)).sum(-1)
        return (losses*data['weight'][idx]).sum()/data['weight'][idx].sum()
    history=[];best=float('inf');start=time.perf_counter()
    for epoch in range(a.epochs):
        model.train();order=torch.randperm(len(tr['x']),device=a.device);train_loss=[]
        for idx in order.split(64):
            opt.zero_grad(set_to_none=True);l=loss(tr,idx);l.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();train_loss.append(l.item())
        model.eval()
        with torch.inference_mode():
            values=[(loss(va,idx).item(),va['weight'][idx].sum().item()) for idx in torch.arange(len(va['x']),device=a.device).split(128)]
            vl=sum(v*n for v,n in values)/sum(n for v,n in values)
        record={'epoch':epoch+1,'train_cross_entropy':float(np.mean(train_loss)),'validation_cross_entropy':vl,'seconds':time.perf_counter()-start}
        history.append(record)
        if vl<best:
            best=vl;torch.save({'state_dict':model.state_dict(),'features':model.features,'kind':a.kind,'physics':not a.no_physics,
                               'conditioning':not a.no_conditioning,'seed':a.seed,'epoch':epoch+1},out/'best.pt')
        write_json(out/'history.json',history)
        if (epoch+1)%5==0:print(tag,record,flush=True)
    write_json(out/'metadata.json',{'arguments':vars(a),'parameters':sum(p.numel() for p in model.parameters()),
                'seconds':time.perf_counter()-start,'best_validation_cross_entropy':best,
                'gpu':torch.cuda.get_device_name() if a.device=='cuda' else 'cpu','torch':torch.__version__,
                'train_sha256':sha256(root/'train_labels.npz'),'validation_sha256':sha256(root/'validation_labels.npz'),
                'source_sha256':source_versions()})

if __name__=='__main__':main()
