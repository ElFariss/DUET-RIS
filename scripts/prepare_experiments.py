"""Audit channel scale/headroom, then create completed-move supervision.

Only train/validation trajectories enter labels. Pilot is exclusively evaluated
by benchmark.py and becomes development data if the method changes afterward.
"""
import argparse
from pathlib import Path
import time
import numpy as np
from atomwise_ris.core import Scenario,ResponseModel,Evaluator,write_json,sha256
from atomwise_ris.optimization.search import local_optimum,softmax

def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',default='data/processed/munich_specular_v3/scenario.npz')
    p.add_argument('--out',default='outputs/runs/specular_v5');p.add_argument('--parents',type=int,default=24)
    p.add_argument('--response',default='data/processed/responses/opensourceris_v1.csv');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    if (out/'headroom.json').exists():raise FileExistsError('Experiment labels already exist; choose a new --out')
    s=Scenario.load(a.scenario);r=ResponseModel.from_table(a.response,5.53e9)
    audit=[];rng=np.random.default_rng(20261024);start=time.perf_counter()
    for idx in np.flatnonzero(s.split!='pilot'):
        ev=Evaluator.from_scenario(s,idx,r);b=np.zeros(ev.n,dtype=np.int8)
        g,gv=local_optimum(ev,b);single=ev.score_field(ev.flip_fields(g))-gv
        gains=ev.score_field(ev.pair_fields(g))-gv;best=int(gains.argmax());pair=ev.pairs[best]
        pb,pv=local_optimum(ev,g,pairs=True)
        audit.append({'index':int(idx),'trajectory':int(s.trajectory[idx]),'split':str(s.split[idx]),
                      'initial':float(ev.score(b)),'greedy':gv,'pair_local':pv,
                      'best_pair_gain':float(gains[best]),'best_pair_bits':pair.tolist(),
                      'first_gains':single[pair].tolist(),'both_first_harmful':bool(np.all(single[pair]<-1e-10)),
                      'ris_to_direct_field_ratio':float(np.linalg.norm(ev.contribution.sum(0))/max(np.linalg.norm(ev.direct),1e-30)),
                      'nonzero_bs_ris':int(np.count_nonzero(abs(s.G)>0)),
                      'nonzero_ris_user':int(np.count_nonzero(abs(s.H[idx])>0)),
                      'cached_full_max_error':float(np.max(abs(ev.field(pb)-ev.full_field(pb))))})
    train_a=[x for x in audit if x['split']=='train']
    useful=[x for x in train_a if x['best_pair_gain']>1e-6]
    gate={'decision':'bounded_training' if useful else 'stop_training_no_pair_headroom',
          'reason':'Completed pair gain >1e-6 bit/s/Hz after single-bit local optimum on training trajectories',
          'useful_train_states':len(useful),'train_states':len(train_a),
          'median_positive_pair_gain':float(np.median([x['best_pair_gain'] for x in useful])) if useful else 0.,
          'note':'This gate establishes pair opportunity, NOT superiority over timed pair search or restarts',
          'scenario_sha256':sha256(a.scenario),'audit_seconds':time.perf_counter()-start}
    write_json(out/'headroom.json',{'gate':gate,'states':audit});print(gate,flush=True)
    if not useful:return
    for split in ['train','validation']:
        xs=[];ys=[];base=[];masks=[];ids=[];types=[];completed=[]
        for idx in np.flatnonzero(s.split==split):
            ev=Evaluator.from_scenario(s,idx,r)
            for parent_id in range(a.parents):
                b=rng.integers(2,size=ev.n,dtype=np.int8)
                if parent_id%3!=0:b,_=local_optimum(ev,b)
                if parent_id%3==2:b[rng.choice(ev.n,4,replace=False)]^=1
                u=ev.field(b);v=float(ev.score_field(u));gain1=ev.score_field(ev.flip_fields(b,u))-v
                gain2=ev.score_field(ev.pair_fields(b,u))-v
                temperature=max(float(np.std(np.r_[gain1,gain2])),1e-5)
                target1=softmax(gain1/temperature)
                pair_weight=softmax(gain2/temperature)
                marginal=np.zeros(ev.n)
                np.add.at(marginal,ev.pairs[:,0],pair_weight/2);np.add.at(marginal,ev.pairs[:,1],pair_weight/2)
                # Pair first-stage examples and single examples share observations:
                # the desired distribution is the matched 50/50 mixture.
                x,g=ev.features(b,u);xs.append(x);ys.append(.5*target1+.5*marginal)
                base.append(g/(np.std(g)+1e-6));masks.append(np.zeros(ev.n,bool));ids.append(idx);types.append('first')
                completed.append(float(gain2.max()))
                # Mix best completed pair's first bit with a sampled first choice.
                bestpair=ev.pairs[int(gain2.argmax())]
                for first in [int(rng.choice(bestpair)),int(rng.choice(ev.n,p=marginal))]:
                    valid=(ev.pairs==first).any(1);other=np.where(ev.pairs[valid,0]==first,ev.pairs[valid,1],ev.pairs[valid,0])
                    target=np.zeros(ev.n);target[other]=softmax(gain2[valid]/temperature)
                    x,g=ev.features(b,u,first=first);mask=np.zeros(ev.n,bool);mask[first]=True
                    xs.append(x);ys.append(target);base.append(g/(np.std(g)+1e-6));masks.append(mask);ids.append(idx);types.append('second')
                    completed.append(float(gain2[valid].max()))
        np.savez_compressed(out/f'{split}_labels.npz',x=np.asarray(xs),target=np.asarray(ys,dtype=np.float32),
                            analytical=np.asarray(base,dtype=np.float32),mask=np.asarray(masks),scenario_index=np.asarray(ids),
                            stage=np.asarray(types),best_completed_gain=np.asarray(completed))
        write_json(out/f'{split}_labels.json',{'rows':len(xs),'parents_per_snapshot':a.parents,'pairs_per_parent':2016,
                    'seed':20261024,'scenario_sha256':sha256(a.scenario),'trajectories':np.unique(s.trajectory[s.split==split]).tolist(),
                    'label':'Soft completed single/pair gains; original-parent features, first-bit marker for conditional actions',
                    'mutation_counts':{'one':.5,'two':.5}})
        print(split,len(xs),'rows',flush=True)

if __name__=='__main__':main()
