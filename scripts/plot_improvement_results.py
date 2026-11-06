"""Plot complete matched-validation rate/runtime summaries for the 2026 improvement run.

Example after validation artifacts are complete (one scene/case per plot):
  python scripts/plot_improvement_results.py \
    --case-label 'new coupled checkpoints, default policy' \
    --coupled outputs/recovered/.../coupled_new/*.jsonl \
    --out outputs/figures/improvement-20261106/coupled-new-default-10ms.png

Only validation rows are accepted. The rate interval resamples whole trajectories,
averaging frames and optimizer seeds within each trajectory first. Runtime is the
empirical p95 of complete elapsed time. This script does not run methods, select a
method, or read held-out test results.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


LABELS = {
    'greedy': 'Greedy', 'pair': 'Pair search', 'random': 'Random',
    'population_ga': 'Population GA', 'uniform_ga': 'Uniform-ranked ILS',
    'memory_ga': 'Memory-ranked ILS', 'analytical_ga': 'Analytical-ranked ILS',
    'analytical_no_memory_ga': 'Analytical ILS, no memory',
    'mlp_ga': 'MLP-ranked ILS', 'attention_ga': 'Attention-ranked ILS',
    'attention_no_memory_ga': 'Attention ILS, no memory',
    'attention_no_physics_ga': 'Attention ILS, no extra physics features',
}
COLORS = {
    'greedy': '#777777', 'pair': '#343a40', 'random': '#aaaaaa',
    'population_ga': '#6c757d', 'uniform_ga': '#bc6c25', 'memory_ga': '#606c38',
    'analytical_ga': '#283618', 'analytical_no_memory_ga': '#dda15e',
    'mlp_ga': '#457b9d', 'attention_ga': '#7b2cbf',
    'attention_no_memory_ga': '#a8dadc', 'attention_no_physics_ga': '#e76f51',
}
DEFAULT_PLOT_METHODS = ('pair', 'analytical_ga', 'mlp_ga', 'attention_ga')


def read_rows(paths, experiment, conditional_policy):
    rows = []
    parents = set()
    configs = set()
    conditional_values = set()
    for path in paths:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(p)
        parents.add(p.resolve().parent)
        for line_no, line in enumerate(p.read_text().splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get('split') != 'validation':
                raise ValueError(f'{p}:{line_no}: expected split=validation, got {row.get("split")!r}')
            required = ('method', 'budget_ms', 'trajectory', 'rate', 'elapsed_ms')
            missing = [k for k in required if k not in row]
            if missing:
                raise ValueError(f'{p}:{line_no}: missing required fields {missing}')
            if row['method'] not in LABELS:
                raise ValueError(f'{p}:{line_no}: unrecognized method {row["method"]!r}')
            configs.add(row.get('search_config', 'medium'))
            conditional_values.add(bool(row.get('conditional_pair_policy', False)))
            rows.append(row)
    if not rows:
        raise ValueError(f'No validation rows supplied for {experiment}')
    if len(parents) != 1:
        raise ValueError(f'{experiment}: files span multiple case directories; do not mix artifact roots')
    if len(configs) != 1:
        raise ValueError(f'{experiment}: mixed search configurations')
    if conditional_values != {conditional_policy}:
        raise ValueError(f'{experiment}: rows do not match --conditional-pair-policy={conditional_policy}')
    return rows


def summarize(rows, budget_ms, bootstrap_seed, resamples):
    rows = [r for r in rows if float(r['budget_ms']) == float(budget_ms)]
    if not rows:
        raise ValueError(f'No rows at budget {budget_ms} ms')
    methods = sorted({r['method'] for r in rows}, key=lambda m: list(LABELS).index(m))
    out = {}
    rng = np.random.default_rng(bootstrap_seed)
    for method in methods:
        selected = [r for r in rows if r['method'] == method]
        by_trajectory = {}
        for row in selected:
            by_trajectory.setdefault(row['trajectory'], []).append(float(row['rate']))
        traj = np.asarray([np.mean(by_trajectory[t]) for t in sorted(by_trajectory)], dtype=float)
        if not np.all(np.isfinite(traj)):
            raise ValueError(f'Nonfinite rate for {method}')
        samples = rng.integers(0, len(traj), size=(resamples, len(traj)))
        boot = traj[samples].mean(axis=1)
        runtimes = np.asarray([float(r['elapsed_ms']) for r in selected])
        if not np.all(np.isfinite(runtimes)) or np.any(runtimes < 0):
            raise ValueError(f'Invalid elapsed_ms for {method}')
        out[method] = {
            'n_rows': len(selected), 'n_trajectories': len(traj),
            'rate_mean': float(traj.mean()),
            'rate_ci95_trajectory_bootstrap': np.percentile(boot, [2.5, 97.5]).tolist(),
            'runtime_p95_ms': float(np.percentile(runtimes, 95)),
        }
    return out


def plot(specular_rows, coupled_rows, out_path, case_label, budget_ms=10., bootstrap_seed=8251, resamples=10000,
         plot_methods=DEFAULT_PLOT_METHODS):
    summaries = {
        'Specular independent-cell simulation': summarize(specular_rows, budget_ms, bootstrap_seed, resamples),
        'Coupled thin-wire simulation': summarize(coupled_rows, budget_ms, bootstrap_seed + 1, resamples),
    }
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.4), sharey=False, constrained_layout=True)
    for ax, (title, methods) in zip(axes, summaries.items()):
        ax.set_title(title, fontsize=13, fontweight='semibold')
        for method, metrics in methods.items():
            if method not in plot_methods:
                continue
            lo, hi = metrics['rate_ci95_trajectory_bootstrap']
            xerr = np.asarray([[metrics['rate_mean'] - lo], [hi - metrics['rate_mean']]])
            ax.errorbar(metrics['rate_mean'], metrics['runtime_p95_ms'], xerr=xerr, fmt='o',
                        color=COLORS[method], ecolor=COLORS[method], elinewidth=1.2,
                        capsize=2, markersize=6, alpha=.9)
            ax.annotate(LABELS[method], (metrics['rate_mean'], metrics['runtime_p95_ms']),
                        xytext=(5, 4), textcoords='offset points', fontsize=7.5)
        ax.set_xlabel('Mean worst-user rate (bit/s/Hz)')
        ax.set_ylabel('Complete runtime p95 (ms)')
        ax.grid(True, color='#d9d9d9', linewidth=.7, alpha=.7)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle(f'{case_label}: development validation at {budget_ms:g} ms', fontsize=15, fontweight='bold')
    fig.text(.5, -.015,
             'Points show method means; horizontal bars are 95% trajectory-bootstrap intervals. '
             'Runtime includes preparation, features, inference, memory and evaluation.',
             ha='center', fontsize=9)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=220, bbox_inches='tight')
    plt.close(fig)
    # Read back the artifact to catch partial or invalid PNG writes.
    from PIL import Image
    with Image.open(out) as image:
        image.verify()
    return summaries


def plot_single(rows, experiment, out_path, case_label, budget_ms=10., bootstrap_seed=8251, resamples=10000,
               plot_methods=DEFAULT_PLOT_METHODS):
    """Plot one scene/case so unrelated checkpoint roots cannot be combined."""
    summary = summarize(rows, budget_ms, bootstrap_seed, resamples)
    title = ('Specular independent-cell simulation' if experiment == 'specular'
             else 'Coupled thin-wire simulation')
    fig, ax = plt.subplots(figsize=(9.4, 6.0), constrained_layout=True)
    ax.set_title(title, fontsize=13, fontweight='semibold')
    handles = []
    labels = []
    for method, metrics in summary.items():
        if method not in plot_methods:
            continue
        lo, hi = metrics['rate_ci95_trajectory_bootstrap']
        xerr = np.asarray([[metrics['rate_mean'] - lo], [hi - metrics['rate_mean']]])
        handle = ax.errorbar(metrics['rate_mean'], metrics['runtime_p95_ms'], xerr=xerr, fmt='o',
                             color=COLORS[method], ecolor=COLORS[method], elinewidth=1.2,
                             capsize=2, markersize=6, alpha=.9)
        handles.append(handle)
        labels.append(LABELS[method])
    ax.set_xlabel('Mean worst-user rate (bit/s/Hz)')
    ax.set_ylabel('Complete runtime p95 (ms)')
    ax.grid(True, color='#d9d9d9', linewidth=.7, alpha=.7)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(handles, labels, title='Method', loc='center left', bbox_to_anchor=(1.02, .5),
              frameon=False, fontsize=9, title_fontsize=9)
    fig.suptitle(f'{case_label} · {budget_ms:g} ms budget', fontsize=14, fontweight='bold')
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=220, bbox_inches='tight')
    plt.close(fig)
    from PIL import Image
    with Image.open(out) as image:
        image.verify()
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case-label', required=True, help='explicit checkpoint/policy case; create separate figures for other cases')
    parser.add_argument('--specular', nargs='+', help='completed specular validation JSONL files (one case directory)')
    parser.add_argument('--coupled', nargs='+', help='completed coupled validation JSONL files (one case directory)')
    parser.add_argument('--conditional-pair-policy', action='store_true', help='declare this as the conditional-policy case; mixed/default rows are rejected')
    parser.add_argument('--methods', nargs='+', default=list(DEFAULT_PLOT_METHODS), choices=tuple(LABELS),
                        help='small method set to show; defaults to pair, analytical, MLP and attention')
    parser.add_argument('--out', required=True, help='output PNG path')
    parser.add_argument('--budget', type=float, default=10.)
    parser.add_argument('--bootstrap-seed', type=int, default=8251)
    parser.add_argument('--resamples', type=int, default=10000)
    args = parser.parse_args()
    if args.resamples < 100:
        parser.error('--resamples must be at least 100')
    if bool(args.specular) == bool(args.coupled):
        parser.error('supply exactly one of --specular or --coupled; plot different scene/case roots separately')
    experiment, paths = ('specular', args.specular) if args.specular else ('coupled', args.coupled)
    rows = read_rows(paths, experiment, args.conditional_pair_policy)
    result = plot_single(rows, experiment, args.out, args.case_label, args.budget, args.bootstrap_seed,
                         args.resamples, tuple(args.methods))
    print(json.dumps({'case_label': args.case_label, 'conditional_pair_policy': args.conditional_pair_policy,
                      'experiment': experiment, 'output': str(Path(args.out)), 'budget_ms': args.budget,
                      'summaries': result}, indent=2))


if __name__ == '__main__':
    main()
