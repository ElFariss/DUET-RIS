"""Mechanism check for the fixed L2 screen on development frames. No deadline is applied.

Does a restart's value after single-flip descent predict its value after pair search, and how
much of a restart's time does pair search take? Development data only.
"""
import argparse, json
from bisect import insort
from pathlib import Path
from time import perf_counter
import numpy as np
from atomwise_ris.physics.network import CoupledNetwork

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data/processed/coupled_wire_dev_fine161')
ap.add_argument('--gate', default='outputs/runs/coupled_wire_v1/physics_gate.json')
ap.add_argument('--frames', type=int, default=60)
ap.add_argument('--restarts', type=int, default=64)
ap.add_argument('--output', required=True)
a = ap.parse_args()
gate = json.loads(Path(a.gate).read_text())
loads = np.asarray(gate['loads_real_ohm'], float) + 1j * np.asarray(gate['loads_imag_ohm'], float)
paths = sorted(Path(a.data).glob('frame_*.npz'))
picked = [paths[i] for i in np.linspace(0, len(paths) - 1, a.frames).astype(int)]


def climb(ev, st, v, pairs):
    while True:
        s = ev.moves(st, pairs)
        j = int(np.argmax(s))
        if s[j] <= v + 1e-12:
            return st, v
        st = ev.flip(st, ev.pairs[j] if pairs else [j])
        v = float(s[j])


rows = []
for path in picked:
    with np.load(path, allow_pickle=False) as d:
        ev = CoupledNetwork(np.asarray(d['z'], np.complex128), loads)
    rng = np.random.default_rng(8251 + int(path.stem.split('_')[1]))
    v1s, v2s, t1s, t2s = [], [], [], []
    for _ in range(a.restarts):
        st = ev.state(rng.integers(0, 2, ev.n, dtype=np.int8))
        v = float(ev.score(st.field))
        t = perf_counter()
        st, v = climb(ev, st, v, False)
        t1 = perf_counter() - t
        v1 = v
        t = perf_counter()
        while True:
            st2, v2 = climb(ev, st, v, True)
            if v2 <= v + 1e-12:
                break
            st, v = climb(ev, st2, v2, False)
        t2 = perf_counter() - t
        v1s.append(v1); v2s.append(v); t1s.append(t1); t2s.append(t2)
    v1s, v2s = np.array(v1s), np.array(v2s)
    rho = np.corrcoef(np.argsort(np.argsort(v1s)), np.argsort(np.argsort(v2s)))[0, 1] if v1s.std() and v2s.std() else float('nan')
    row = dict(frame=path.name, spearman=float(rho), v1=float(v1s.mean()), v2=float(v2s.mean()), best=float(v2s.max()),
               t1_ms=1e3 * float(np.mean(t1s)), t2_ms=1e3 * float(np.mean(t2s)))
    for q in (0.50, 0.75):
        hist, admitted = [], np.zeros(len(v1s), bool)
        for i, x in enumerate(v1s):
            admitted[i] = not hist or x >= hist[int(q * len(hist))]
            insort(hist, x)
        # Same time spent, more restarts: scale the admitted set up to the time of an unscreened run.
        cost = np.array(t1s) + admitted * np.array(t2s)
        row[f'q{int(q*100)}'] = dict(admitted=float(admitted.mean()), kept_best=bool(v2s[admitted].max() >= v2s.max() - 1e-9),
                                     best_kept=float(v2s[admitted].max()), time_share=float(cost.sum() / (np.sum(t1s) + np.sum(t2s))),
                                     mean_v2_admitted=float(v2s[admitted].mean()), mean_v2_rejected=float(v2s[~admitted].mean()) if (~admitted).any() else None)
    rows.append(row)
Path(a.output).parent.mkdir(parents=True, exist_ok=True)
json.dump(rows, open(a.output, 'w'), indent=1)
print('frames', len(rows), 'median within-frame spearman %.3f, mean %.3f' % (np.nanmedian([r['spearman'] for r in rows]), np.nanmean([r['spearman'] for r in rows])))
print('single climb ms %.2f, pair stage ms %.2f, mean v1 %.3f v2 %.3f' % tuple(np.mean([r[k] for r in rows]) for k in ('t1_ms', 't2_ms', 'v1', 'v2')))
for q in ('q50', 'q75'):
    x = [r[q] for r in rows]
    print(q, 'admitted %.3f kept_best_frames %.3f best_lost %.3f time_share %.3f v2_admitted %.3f v2_rejected %.3f' % (
        np.mean([i['admitted'] for i in x]), np.mean([i['kept_best'] for i in x]),
        np.mean([r['best'] - r[q]['best_kept'] for r in rows]), np.mean([i['time_share'] for i in x]),
        np.mean([i['mean_v2_admitted'] for i in x]), np.mean([i['mean_v2_rejected'] for i in x])))
