"""Complete-controller deadline-aware search on a coupled multiport network."""
from time import perf_counter_ns
import numpy as np

def search(ev,method,deadline,seed,memory=(),policy=None,scaling=None):
    rng=np.random.default_rng(seed);start=perf_counter_ns();reserve=200_000
    best=ev.state(np.zeros(ev.n,np.int8));bestv=float(ev.score(best.field));count=1
    breakdown={'features_ms':0.,'inference_ms':0.,'memory_ms':0.}
    population=[(best,bestv)]
    def accept(st,value):
        nonlocal best,bestv,count
        count+=1
        if perf_counter_ns()<deadline and value>bestv:best=st;bestv=value
    t=perf_counter_ns()
    for bits in memory:
        if perf_counter_ns()+1_000_000>deadline:break
        st=ev.state(bits);v=float(ev.score(st.field));accept(st,v)
        if perf_counter_ns()<deadline:population.append((st,v))
    breakdown['memory_ms']=(perf_counter_ns()-t)/1e6
    st=best;v=bestv
    ga=method.endswith('_ga')
    if ga:
        while len(population)<12 and perf_counter_ns()+1_000_000<deadline:
            q=ev.state(rng.integers(0,2,ev.n,dtype=np.int8));qv=float(ev.score(q.field));accept(q,qv)
            if perf_counter_ns()<deadline:population.append((q,qv))
    estimate=2_000_000 if policy is not None else 800_000
    while perf_counter_ns()+estimate+reserve<deadline:
        t=perf_counter_ns()
        if method in ['greedy','pair']:
            scores=ev.moves(st);count+=ev.n;j=int(np.argmax(scores));indices=[j]
            if scores[j]<=v+1e-10:
                if method=='pair' and perf_counter_ns()+2_000_000+reserve<deadline:
                    scores=ev.moves(st,True);count+=len(scores);j=int(np.argmax(scores));indices=ev.pairs[j]
                if scores[j]<=v+1e-10:
                    st=ev.state(rng.integers(0,2,ev.n,dtype=np.int8));v=float(ev.score(st.field));accept(st,v)
                    estimate=max(estimate,int((perf_counter_ns()-t)*1.25));continue
            if perf_counter_ns()+300_000<deadline:
                st=ev.flip(st,indices);v=float(ev.score(st.field));accept(st,v)
        elif method=='random':
            q=ev.state(rng.integers(0,2,ev.n,dtype=np.int8));accept(q,float(ev.score(q.field)))
        elif ga:
            ids=rng.integers(len(population),size=2);parent=population[max(ids,key=lambda i:population[i][1])][0]
            if rng.random()<.25:
                donor=population[int(rng.integers(len(population)))][0];b=parent.bits.copy();mask=rng.random(ev.n)<.5;b[mask]=donor.bits[mask];parent=ev.state(b)
            chosen=[];nmove=2 if rng.random()<.5 else 1
            for _ in range(nmove):
                if method=='memory_ga':logits=np.zeros(ev.n)
                else:
                    ft=perf_counter_ns()
                    if policy is None:g=ev.moves(parent)-ev.score(parent.field)
                    else:x,g=ev.features(parent,chosen[0] if chosen else -1)
                    logits=g/max(float(np.std(g)),1e-4)
                    if policy is not None:
                        x=(x-scaling[0])/scaling[1]
                    breakdown['features_ms']+=(perf_counter_ns()-ft)/1e6
                    if policy is not None:
                        it=perf_counter_ns();logits=policy(x,logits);breakdown['inference_ms']+=(perf_counter_ns()-it)/1e6
                logits=np.asarray(logits,dtype=float).copy();logits[chosen]=-np.inf
                prob=np.exp(logits-np.max(logits));prob/=prob.sum();valid=np.isfinite(logits);prob=.95*prob+.05*valid/valid.sum()
                chosen.append(int(rng.choice(ev.n,p=prob)))
            q=ev.flip(parent,chosen);qv=float(ev.score(q.field));accept(q,qv)
            if perf_counter_ns()<deadline:
                population.append((q,qv));population.sort(key=lambda x:x[1],reverse=True);population=population[:12]
        else:raise ValueError(method)
        estimate=max(estimate,int((perf_counter_ns()-t)*1.25))
    return best.bits.copy(),bestv,count,breakdown
