"""CPU controllers; every online action is timed. No post-deadline improvements.

Model construction/loading is offline. Each run reports overruns. A candidate
counts only when its entire evaluation finished before the deadline. Initial
configuration evaluation is mandatory and is reported even if budget too small.
"""
from dataclasses import dataclass, field
from time import perf_counter_ns
import numpy as np

@dataclass
class SearchResult:
    bits: np.ndarray
    value: float
    elapsed_ms: float
    evaluations: int
    trace: list
    breakdown_ms: dict
    deadline_missed: bool

@dataclass
class Memory:
    capacity: int = 8
    trajectory: object = None
    patterns: list = field(default_factory=list)

    def enter(self,trajectory):
        if trajectory != self.trajectory:
            self.patterns=[]; self.trajectory=trajectory

    def remember(self,bits):
        b=np.asarray(bits,dtype=np.int8).copy()
        self.patterns=[a for a in self.patterns if not np.array_equal(a,b)]
        self.patterns.insert(0,b);self.patterns=self.patterns[:self.capacity]

def softmax(x):
    x=np.asarray(x);z=np.exp(x-np.max(x));return z/z.sum()

def local_optimum(ev,bits,pairs=False,max_steps=1000):
    """Offline reference and label generation; NEVER called outside timed loop in benchmarks."""
    b=np.asarray(bits,dtype=np.int8).copy();u=ev.field(b);v=ev.score_field(u)
    for _ in range(max_steps):
        fs=ev.flip_fields(b,u);vs=ev.score_field(fs);j=int(np.argmax(vs))
        if vs[j]>v+1e-12:
            b[j]^=1;u=fs[j];v=vs[j];continue
        if pairs:
            fs=ev.pair_fields(b,u);vs=ev.score_field(fs);j=int(np.argmax(vs))
            if vs[j]>v+1e-12:
                b[ev.pairs[j]]^=1;u=fs[j];v=vs[j];continue
        break
    return b,float(v)

def search(ev,method,budget_ms,seed,initial=None,memory=None,policy=None,
           population_size=12,p_pair=.5):
    start=perf_counter_ns();deadline=start+int(budget_ms*1e6)
    work_deadline=deadline-int(min(.2,budget_ms*.2)*1e6)
    timings={'setup':0.,'features':0.,'inference':0.,'evaluation':0.,'memory':0.,'other':0.}
    rng=np.random.default_rng(seed)
    b=np.zeros(ev.n,dtype=np.int8) if initial is None else np.asarray(initial,dtype=np.int8).copy()
    best=b.copy();u=ev.field(b);v=float(ev.score_field(u));bestv=v;count=1
    trace=[((perf_counter_ns()-start)/1e6,bestv)]
    timings['setup']=(perf_counter_ns()-start)/1e6
    population=[(b.copy(),v)]
    def accept(candidate,field,value,already_counted=False):
        nonlocal best,bestv,count
        if not already_counted:count+=1
        if perf_counter_ns()<=deadline and value>bestv:
            best=candidate.copy();bestv=float(value);trace.append(((perf_counter_ns()-start)/1e6,bestv))
    # Retrieve and rescore stored configurations on the CURRENT channel.
    if memory is not None:
        t=perf_counter_ns()
        for candidate in memory.patterns:
            if perf_counter_ns()>=deadline:break
            fu=ev.field(candidate);fv=float(ev.score_field(fu));accept(candidate,fu,fv)
            if perf_counter_ns()<=deadline:population.append((candidate.copy(),fv))
        timings['memory']+=(perf_counter_ns()-t)/1e6
        b=best.copy();u=ev.field(b);v=bestv
    # Matched GA initialization, crossover, selection and mutation counts.
    ga=method in ('memory_ga','analytical_ga','mlp_ga','attention_ga','attention_no_physics_ga')
    if ga:
        while len(population)<population_size and perf_counter_ns()<deadline:
            q=rng.integers(0,2,ev.n,dtype=np.int8);t=perf_counter_ns();fu=ev.field(q);fv=float(ev.score_field(fu))
            timings['evaluation']+=(perf_counter_ns()-t)/1e6;accept(q,fu,fv)
            if perf_counter_ns()<=deadline: population.append((q,fv))
    recent=np.zeros(ev.n)
    estimated_iteration_ns=100000 if not ga else (1200000 if policy is not None else 200000)
    while perf_counter_ns()+estimated_iteration_ns<work_deadline:
        iteration_start=perf_counter_ns()
        if method in ('greedy','pair'):
            t=perf_counter_ns();fs=ev.flip_fields(b,u);values=ev.score_field(fs)
            timings['evaluation']+=(perf_counter_ns()-t)/1e6;count+=ev.n
            if perf_counter_ns()>deadline:break
            j=int(np.argmax(values))
            if values[j]>v+1e-12:
                b[j]^=1;u=fs[j];v=float(values[j]);accept(b,u,v,already_counted=True)
                estimated_iteration_ns=max(estimated_iteration_ns,int((perf_counter_ns()-iteration_start)*1.2))
                continue
            if method=='pair':
                if perf_counter_ns()+500000>work_deadline:break
                t=perf_counter_ns();fs=ev.pair_fields(b,u);values=ev.score_field(fs)
                timings['evaluation']+=(perf_counter_ns()-t)/1e6;count+=len(ev.pairs)
                if perf_counter_ns()>deadline:break
                j=int(np.argmax(values))
                if values[j]>v+1e-12:
                    b[ev.pairs[j]]^=1;u=fs[j];v=float(values[j]);accept(b,u,v,already_counted=True)
                    estimated_iteration_ns=max(estimated_iteration_ns,int((perf_counter_ns()-iteration_start)*1.2))
                    continue
            b=rng.integers(0,2,ev.n,dtype=np.int8)
            t=perf_counter_ns();u=ev.field(b);v=float(ev.score_field(u));timings['evaluation']+=(perf_counter_ns()-t)/1e6
            accept(b,u,v)
        elif method=='random':
            q=rng.integers(0,2,(16,ev.n),dtype=np.int8)
            t=perf_counter_ns();fu=ev.field(q);fv=ev.score_field(fu);timings['evaluation']+=(perf_counter_ns()-t)/1e6
            count+=len(q)-1;j=int(np.argmax(fv));accept(q[j],fu[j],fv[j])
        elif ga:
            # Two-way tournament; 25% crossover for every mutation policy.
            ids=rng.integers(len(population),size=2);parent=population[max(ids,key=lambda i:population[i][1])][0]
            q=parent.copy()
            if rng.random()<.25:
                donor=population[int(rng.integers(len(population)))][0];mask=rng.random(ev.n)<.5;q[mask]=donor[mask]
            nmove=2 if rng.random()<p_pair else 1
            chosen=[]
            fu=ev.field(q)
            for _ in range(nmove):
                if method=='memory_ga':logits=np.zeros(ev.n)
                else:
                    t=perf_counter_ns()
                    if policy is None:
                        gains=ev.score_field(ev.flip_fields(q,fu))-ev.score_field(fu)
                    else:
                        x,gains=ev.features(q,fu,first=chosen[0] if chosen else -1)
                    timings['features']+=(perf_counter_ns()-t)/1e6
                    logits=gains/(np.std(gains)+1e-6)
                    if policy is not None:
                        t=perf_counter_ns();logits=policy(x,logits);timings['inference']+=(perf_counter_ns()-t)/1e6
                logits=np.asarray(logits,dtype=float).copy();logits[chosen]=-np.inf
                prob=.95*softmax(logits)+.05*np.isfinite(logits)/np.isfinite(logits).sum()
                chosen.append(int(rng.choice(ev.n,p=prob)))
            q[chosen]^=1;recent*=.9;recent[chosen]=1
            t=perf_counter_ns();fu=ev.field(q);fv=float(ev.score_field(fu));timings['evaluation']+=(perf_counter_ns()-t)/1e6
            accept(q,fu,fv)
            if perf_counter_ns()<=deadline:
                population.append((q,fv));population.sort(key=lambda p:p[1],reverse=True);population=population[:population_size]
        else:raise ValueError(method)
        estimated_iteration_ns=max(estimated_iteration_ns,int((perf_counter_ns()-iteration_start)*1.2))
    # Memory write is online; the pattern remains the best pre-deadline one.
    if memory is not None:
        t=perf_counter_ns();memory.remember(best);timings['memory']+=(perf_counter_ns()-t)/1e6
    elapsed=(perf_counter_ns()-start)/1e6
    timings['other']=max(0.,elapsed-sum(timings.values()))
    return SearchResult(best,bestv,elapsed,count,trace,timings,elapsed>budget_ms)
