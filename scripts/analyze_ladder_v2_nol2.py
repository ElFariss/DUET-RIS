"""Summarize a V2 one-component development round. Development data only; exploratory intervals.

Default: the no-L2 round (docs/ladder-v2-nol2-design-20261107.md). ``--round fixedl2`` reads the
fixed-L2 round (docs/ladder-v2-fixed-l2-design-20261107.md), ``--round combined`` the b3+b5 round
(docs/ladder-v2-combined-design-20261107.md). Contrasts are the declared family: b0-pair, each
component minus b0, each component minus pair, plus any round-specific extras.
"""
import argparse
import collections
import json
from pathlib import Path

import numpy as np

ROUNDS = {'nol2': ('outputs/runs/pair_plus_ladder_v2_nol2', 'nol2_dev161', ('b3', 'b4', 'b4o', 'b5', 'b6'), ()),
          'fixedl2': ('outputs/runs/pair_plus_ladder_v2_fixedl2', 'fixedl2_dev161', ('b2', 'b2t'), ()),
          'combined': ('outputs/runs/pair_plus_ladder_v2_combined', 'combined_dev161', ('b3', 'b5', 'b35'),
                       (('b35', 'b3'), ('b35', 'b5'))),
          'combined_n3': ('outputs/runs/pair_plus_ladder_v2_combined_n3', 'combined_dev161', ('b3', 'b5', 'b35'),
                          (('b35', 'b3'), ('b35', 'b5')))}
ap = argparse.ArgumentParser()
ap.add_argument('--round', choices=sorted(ROUNDS), default='nol2')
run_dir, stem, components, extras = ROUNDS[ap.parse_args().round]
RUN = Path(run_dir)
PREFIX = 'pair_plus_'
COMPONENTS = [PREFIX + x for x in components]
BASE = PREFIX + 'b0'
FAMILY = [(BASE, 'pair')] + [(c, BASE) for c in COMPONENTS] + [(c, 'pair') for c in COMPONENTS]
FAMILY += [(PREFIX + a, PREFIX + b) for a, b in extras]
assert len(FAMILY) == 1 + 2 * len(COMPONENTS) + len(extras)

rows = []
for line in open(RUN / f'{stem}.jsonl'):
    r = json.loads(line)
    bd = r.get('breakdown') or {}
    rows.append((r['method'], r['budget_ms'], r['seed'], r['index'], r['trajectory'], r['rate'], r['elapsed_ms'],
                 r['deadline_missed'], r['evaluations'], r['on_bits'], bd.get('restarts', np.nan), bd.get('tabu_moves', np.nan),
                 bd.get('screened_out', np.nan), bd.get('pair_scans', np.nan)))
cols = list(zip(*rows))
M = np.array(cols[0])
B = np.array(cols[1], float)
I = np.array(cols[3])
T = np.array(cols[4])
R = np.array(cols[5])
E = np.array(cols[6])
X = np.array(cols[7], bool)
N = np.array(cols[8], float)
O = np.array(cols[9])
RS = np.array(cols[10], float)
TB = np.array(cols[11], float)
SO = np.array(cols[12], float)
PS = np.array(cols[13], float)
methods = ['pair', BASE] + COMPONENTS
budgets = sorted(set(B.tolist()))
trajectories = np.unique(T)

best = collections.defaultdict(float)
for i, r in zip(I, R):
    best[i] = max(best[i], r)
G = np.array([best[i] for i in I]) - R


def nanmean(a):
    return float(np.mean(a)) if len(a) and not np.isnan(a).all() else None


out = {'cells': [], 'contrasts': [], 'family_size': len(FAMILY), 'best_known_mean_this_round': float(np.mean(list(best.values())))}
for m in methods:
    for b in budgets:
        k = (M == m) & (B == b)
        out['cells'].append(dict(method=m, budget_ms=b, n=int(k.sum()), rate=float(R[k].mean()), gap_to_best=float(G[k].mean()),
                                 p95_ms=float(np.percentile(E[k], 95)), max_ms=float(E[k].max()), misses=int(X[k].sum()),
                                 evals=float(N[k].mean()), all_off=float((O[k] == 0).mean()), on_median=float(np.median(O[k])),
                                 restarts=nanmean(RS[k]), tabu_moves=nanmean(TB[k]),
                                 screened_out=nanmean(SO[k]), pair_scans=nanmean(PS[k])))

rate_by_traj = {}
for m in methods:
    for b in budgets:
        k = (M == m) & (B == b)
        rate_by_traj[m, b] = np.array([R[k & (T == t)].mean() for t in trajectories])

rng = np.random.default_rng(8251)
idx = rng.integers(0, len(trajectories), (10000, len(trajectories)))
alpha = 0.05 / len(FAMILY)
for b in budgets:
    for a, c in FAMILY:
        d = rate_by_traj[a, b] - rate_by_traj[c, b]
        lo, hi = np.percentile(d[idx].mean(1), [100 * alpha / 2, 100 * (1 - alpha / 2)])
        out['contrasts'].append(dict(a=a, b=c, budget_ms=b, diff=float(d.mean()), lo=float(lo), hi=float(hi),
                                     wins=int((d > 0).sum()), n=len(trajectories)))

reading = []
for b in budgets:
    get = {(c['a'], c['b']): c for c in out['contrasts'] if c['budget_ms'] == b}
    for c in COMPONENTS:
        cand = get[c, BASE]['lo'] > 0
        reading.append(dict(budget_ms=b, method=c, candidate=cand, over_pair=cand and get[c, 'pair']['lo'] > 0))
out['reading'] = reading
json.dump(out, open(RUN / f'analysis_{stem}.json', 'w'), indent=1)

short = lambda m: m.replace(PREFIX, '')
print('method budget rate gap p95 max miss evals restarts tabu alloff onmed screened pairscans')
for c in out['cells']:
    print(short(c['method']), int(c['budget_ms']) if c['budget_ms'] >= 1 else c['budget_ms'],
          '%.3f %.3f %.2f %.1f %d %.0f %s %s %.3f %.0f' % (
              c['rate'], c['gap_to_best'], c['p95_ms'], c['max_ms'], c['misses'], c['evals'],
              'na' if c['restarts'] is None else '%.1f' % c['restarts'],
              'na' if c['tabu_moves'] is None else '%.1f' % c['tabu_moves'], c['all_off'], c['on_median']),
          'na' if c['screened_out'] is None else '%.1f' % c['screened_out'], 'na' if c['pair_scans'] is None else '%.1f' % c['pair_scans'])
for c in out['contrasts']:
    print(int(c['budget_ms']), short(c['a']), '-', short(c['b']), '%+.3f [%+.3f, %+.3f] %d/%d' % (c['diff'], c['lo'], c['hi'], c['wins'], c['n']))
print('candidates:', [(int(r['budget_ms']), short(r['method']), 'over_pair' if r['over_pair'] else 'b0_only') for r in reading if r['candidate']])
print('best-known mean this round %.3f' % out['best_known_mean_this_round'])
