"""Summarize the V2 development ladder. Development data only; exploratory intervals, no decisions."""
import json, sys, collections
from pathlib import Path
import numpy as np
RUN = Path('outputs/runs/pair_plus_ladder_v2')
LS = [f'pair_plus_l{i}' for i in range(1, 7)]
rows = []
for line in open(RUN / 'ladder_dev161.jsonl'):
    r = json.loads(line)
    rows.append((r['method'], r['budget_ms'], r['seed'], r['index'], r['trajectory'], r['rate'], r['elapsed_ms'],
                 r['deadline_missed'], r['evaluations'], r['on_bits']))
methods = sorted({r[0] for r in rows}); budgets = sorted({r[1] for r in rows})
cols = list(zip(*rows)); M = np.array(cols[0]); B = np.array(cols[1], float); S = np.array(cols[2]); I = np.array(cols[3])
T = np.array(cols[4]); R = np.array(cols[5]); E = np.array(cols[6]); X = np.array(cols[7], bool); N = np.array(cols[8], float); O = np.array(cols[9])
best = collections.defaultdict(float)
for i, r in zip(I, R): best[i] = max(best[i], r)
G = np.array([best[i] for i in I]) - R
out = {'cells': [], 'contrasts': []}
for m in methods:
    for b in budgets:
        k = (M == m) & (B == b)
        out['cells'].append(dict(method=m, budget_ms=b, n=int(k.sum()), rate=R[k].mean(), gap_to_best=G[k].mean(), p95_ms=float(np.percentile(E[k], 95)),
            max_ms=E[k].max(), misses=int(X[k].sum()), evals=N[k].mean(), all_off=(O[k] == 0).mean(), on_median=float(np.median(O[k]))))
def traj(m, b):
    k = (M == m) & (B == b); ts = np.unique(T); return np.array([R[k & (T == t)].mean() for t in ts])
pairs = [('pair', 'greedy'), ('pair_plus_l1', 'pair')] + [(LS[i], LS[i-1]) for i in range(1, 6)]
for l in LS:
    pairs += [(l, 'pair'), (l, 'me_ga'), (l, 'ga_risc'), (l, 'mlp_ga')]
pairs += [('me_ga', 'ga_risc'), ('pair', 'me_ga'), ('pair', 'mlp_ga')]
pairs = list(dict.fromkeys(pairs))
rng = np.random.default_rng(8251); nt = len(np.unique(T)); idx = rng.integers(0, nt, (10000, nt))
alpha = 0.05 / len(pairs)
for b in budgets:
    for a, c in pairs:
        d = traj(a, b) - traj(c, b); bs = d[idx].mean(1); lo, hi = np.percentile(bs, [100*alpha/2, 100*(1-alpha/2)])
        out['contrasts'].append(dict(a=a, b=c, budget_ms=b, diff=d.mean(), lo=lo, hi=hi, wins=int((d > 0).sum()), n=nt))
paper = [json.loads(l) for l in open(RUN / 'ladder_dev161.me-ga-paper.jsonl')]
pr = np.array([p['rate'] for p in paper]); pe = np.array([p['elapsed_ms'] for p in paper])
ptr = np.array([p['trajectory'] for p in paper])
out['me_ga_paper'] = dict(n=len(paper), rate=pr.mean(), median_ms=float(np.median(pe)), p95_ms=float(np.percentile(pe, 95)), evals=float(np.mean([p['evaluations'] for p in paper])),
    events={k: float(np.mean([p['breakdown'].get(k, 0) or 0 for p in paper])) for k in paper[0]['breakdown'] if isinstance(paper[0]['breakdown'][k], (int, float))})
d = np.array([pr[ptr == t].mean() for t in np.unique(ptr)])
out['best_known_mean'] = float(np.mean(list(best.values()))); out['family_size'] = len(pairs)
json.dump(out, open(RUN / 'analysis_dev161.json', 'w'), indent=1, default=float)
print('family', len(pairs), 'best-known mean %.3f' % out['best_known_mean'], 'paper', {k: (round(v, 2) if not isinstance(v, dict) else v) for k, v in out['me_ga_paper'].items()})
print('method budget rate gap p95 max miss evals alloff onmed')
for c in out['cells']:
    print(c['method'].replace('pair_plus_', ''), int(c['budget_ms']), '%.3f %.3f %.1f %.1f %d %.0f %.2f %.0f' % (c['rate'], c['gap_to_best'], c['p95_ms'], c['max_ms'], c['misses'], c['evals'], c['all_off'], c['on_median']))
for c in out['contrasts']:
    if c['budget_ms'] in (10, 50, 100):
        print(int(c['budget_ms']), c['a'].replace('pair_plus_', ''), '-', c['b'].replace('pair_plus_', ''), '%.3f [%.3f, %.3f] %d/%d' % (c['diff'], c['lo'], c['hi'], c['wins'], c['n']))
