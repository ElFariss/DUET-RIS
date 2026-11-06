"""Train a zero-residual-start policy into a fresh, explicit run directory."""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from atomwise_ris.core import sha256
from atomwise_ris.models import EditPolicy


def load_labels(path, device, target_temperature=1., conditional_weight=.25):
    with np.load(path) as archive:
        required = {'x', 'target', 'analytical', 'mask', 'stage'}
        missing = required.difference(archive.files)
        if missing:
            raise ValueError(f'{path} is missing label arrays: {sorted(missing)}')
        values = {key: archive[key].copy() for key in required}
    if values['x'].ndim != 3 or values['target'].shape != values['x'].shape[:2]:
        raise ValueError(f'Invalid feature/target shapes in {path}')
    if values['analytical'].shape != values['target'].shape or values['mask'].shape != values['target'].shape:
        raise ValueError(f'Invalid analytical/mask shapes in {path}')
    if not np.isfinite(values['x']).all() or not np.isfinite(values['target']).all():
        raise ValueError(f'Non-finite features or targets in {path}')
    if not np.allclose(values['target'].sum(axis=1), 1., atol=1e-4):
        raise ValueError(f'Target rows must sum to one in {path}')
    target = values['target'].astype(np.float32, copy=False)
    target = np.power(np.maximum(target, 0.), 1. / target_temperature)
    target /= np.maximum(target.sum(axis=1, keepdims=True), 1e-12)
    values['target'] = target
    result = {key: torch.as_tensor(value, device=device) for key, value in values.items() if key != 'stage'}
    result['stage'] = values['stage']
    result['weight'] = torch.as_tensor(np.where(values['stage'] == 'first', 1., conditional_weight),
                                       dtype=torch.float32, device=device)
    return result


def ranking_metrics(scores, target, mask, weight, topk=(1, 5, 10)):
    """Soft-label ranking diagnostics; these are not physical gain regret."""
    scores = scores.masked_fill(mask, -1e9)
    valid = ~mask
    masked_target = target.masked_fill(mask, 0.)
    best_mass = masked_target.max(dim=-1).values
    top1 = scores.argmax(dim=-1)
    target_mode = masked_target.argmax(dim=-1)
    top1_mass = masked_target.gather(-1, top1[:, None]).squeeze(-1)
    denom = weight.sum().clamp_min(1e-12)
    output = {
        'top1_target_mass': float((top1_mass * weight).sum() / denom),
        'soft_target_regret': float(((best_mass - top1_mass).clamp_min(0.) * weight).sum() / denom),
        'target_mode_accuracy': float(((top1 == target_mode).to(weight.dtype) * weight).sum() / denom),
        'rows': int(len(scores)),
    }
    for k in topk:
        kk = min(k, scores.shape[-1])
        indices = scores.topk(kk, dim=-1).indices
        mass = masked_target.gather(-1, indices).sum(-1)
        output[f'top{k}_target_mass'] = float((mass * weight).sum() / denom)
    return output


def cross_entropy(model, data, indices):
    scores = model(data['x'][indices], data['analytical'][indices])
    scores = scores.masked_fill(data['mask'][indices], -1e9)
    per_row = -(data['target'][indices] * torch.log_softmax(scores, dim=-1)).sum(-1)
    weights = data['weight'][indices]
    return (per_row * weights).sum() / weights.sum().clamp_min(1e-12)


def stage_ranking_metrics(model, data, device):
    scores = model(data['x'], data['analytical'])
    metrics = {}
    for stage in ('first', 'second'):
        stage_indices = torch.as_tensor(np.flatnonzero(data['stage'] == stage), device=device)
        metrics[stage] = ranking_metrics(scores[stage_indices], data['target'][stage_indices],
                                         data['mask'][stage_indices], data['weight'][stage_indices])
    metrics['all'] = ranking_metrics(scores, data['target'], data['mask'], data['weight'])
    return metrics


def selection_value(metric, cross_entropy_value, ranking):
    if metric == 'validation_cross_entropy':
        return float(cross_entropy_value)
    if metric == 'validation_top5_target_mass':
        return float(ranking['all']['top5_target_mass'])
    if metric == 'balanced_top5_target_mass':
        return float((ranking['first']['top5_target_mass'] + ranking['second']['top5_target_mass']) / 2.)
    raise ValueError(f'Unknown selection metric: {metric}')


def is_better(metric, candidate, incumbent):
    if metric == 'validation_cross_entropy':
        return candidate < incumbent
    return candidate > incumbent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, help='existing experiment root, used for the training gate')
    parser.add_argument('--data', required=True, help='directory containing train_labels.npz and validation_labels.npz')
    parser.add_argument('--out', required=True, help='new output root; must not already exist')
    parser.add_argument('--kind', choices=['attention', 'mlp'], default='attention')
    parser.add_argument('--seeds', nargs='+', type=int, default=[7, 19, 43])
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--target-temperature', type=float, default=1.,
                        help='sharpen soft labels by raising probabilities to 1/T; evaluation always uses original labels')
    parser.add_argument('--conditional-weight', type=float, default=.25,
                        help='per-row weight for conditional second-action examples; .5 balances stages with this 1:2 row ratio')
    parser.add_argument('--selection-metric', choices=['validation_cross_entropy',
                               'validation_top5_target_mass', 'balanced_top5_target_mass'],
                        default='validation_cross_entropy',
                        help='checkpoint selection criterion; ranking metrics use original, unsharpened validation targets')
    parser.add_argument('--candidate-label', default='zero_residual_ce',
                        help='free-form compound recipe label stored with every checkpoint and metadata record')
    parser.add_argument('--device', default='cuda')
    args = parser.parse_args()

    source = Path(args.data)
    run = Path(args.run)
    out = Path(args.out)
    gate_path = run / 'headroom.json'
    if not gate_path.exists():
        raise FileNotFoundError(f'Missing training gate: {gate_path}')
    if json.loads(gate_path.read_text())['gate']['decision'] != 'bounded_training':
        raise RuntimeError(f'Training gate did not pass: {gate_path}')
    run_train_meta = run / 'train_labels.json'
    data_train_meta = source / 'train_labels.json'
    data_validation_meta = source / 'validation_labels.json'
    if data_train_meta.exists() and data_validation_meta.exists():
        train_meta = json.loads(data_train_meta.read_text())
        validation_meta = json.loads(data_validation_meta.read_text())
        if train_meta.get('scenario_sha256') != validation_meta.get('scenario_sha256'):
            raise ValueError('Training and validation labels reference different scenarios')
        if run_train_meta.exists():
            run_scenario_hash = json.loads(run_train_meta.read_text()).get('scenario_sha256')
            if train_meta.get('scenario_sha256') != run_scenario_hash:
                raise ValueError('Explicit --data labels do not match the --run training gate scenario')
    if out.exists():
        raise FileExistsError(f'Output root already exists; choose a fresh --out: {out}')
    if (args.epochs < 1 or not args.seeds or len(set(args.seeds)) != len(args.seeds)
            or args.target_temperature <= 0 or args.conditional_weight < 0):
        raise ValueError('epochs must be positive, seeds unique, temperature positive, and conditional weight nonnegative')
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA requested but unavailable')
    torch.set_num_threads(1)
    train = load_labels(source / 'train_labels.npz', args.device,
                        args.target_temperature, args.conditional_weight)
    # Preserve original validation targets for all comparable ranking metrics.
    validation = load_labels(source / 'validation_labels.npz', args.device, 1., args.conditional_weight)
    validation_original = load_labels(source / 'validation_labels.npz', args.device, 1., args.conditional_weight)
    if train['x'].shape[-1] != validation['x'].shape[-1]:
        raise ValueError('Training and validation feature dimensions differ')

    (out / 'models').mkdir(parents=True)
    for seed in args.seeds:
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = EditPolicy(train['x'].shape[-1], args.kind).to(args.device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-3)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-5)
        tag = f'{args.kind}_zero_residual_seed{seed}'
        model_dir = out / 'models' / tag
        model_dir.mkdir()
        started = time.perf_counter()
        model.eval()
        with torch.inference_mode():
            initial_values = [(float(cross_entropy(model, validation, indices)),
                               float(validation['weight'][indices].sum()))
                              for indices in torch.arange(len(validation['x']), device=args.device).split(128)]
            initial_cross_entropy = sum(value * weight for value, weight in initial_values) / sum(weight for _, weight in initial_values)
            initial_metrics = stage_ranking_metrics(model, validation_original, args.device)
        best_selection = selection_value(args.selection_metric, initial_cross_entropy, initial_metrics)
        selected_epoch = 0
        selected_ranking = initial_metrics
        validation_cross_entropies = [initial_cross_entropy]
        torch.save({'state_dict': model.state_dict(), 'features': model.features,
                    'kind': args.kind, 'physics': True, 'conditioning': True,
                    'architecture_version': model.architecture_version,
                    'seed': seed, 'epoch': 0, 'initialization': 'zero_residual',
                    'candidate_label': args.candidate_label,
                    'selection_metric': args.selection_metric, 'selection_value': best_selection},
                   model_dir / 'best.pt')
        history = [{'epoch': 0, 'train_cross_entropy': None, 'validation_cross_entropy': initial_cross_entropy,
                    'validation_ranking': initial_metrics, 'seconds': 0.}]
        for epoch in range(args.epochs):
            model.train()
            order = torch.randperm(len(train['x']), device=args.device)
            batch_losses = []
            for indices in order.split(64):
                optimizer.zero_grad(set_to_none=True)
                loss = cross_entropy(model, train, indices)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
                optimizer.step()
                batch_losses.append(float(loss.detach()))
            scheduler.step()
            model.eval()
            with torch.inference_mode():
                vals = [(float(cross_entropy(model, validation, indices)),
                         float(validation['weight'][indices].sum()))
                        for indices in torch.arange(len(validation['x']), device=args.device).split(128)]
                val_loss = sum(value * weight for value, weight in vals) / sum(weight for _, weight in vals)
                metrics = stage_ranking_metrics(model, validation_original, args.device)
            validation_cross_entropies.append(val_loss)
            record = {'epoch': epoch + 1, 'train_cross_entropy': float(np.mean(batch_losses)),
                      'validation_cross_entropy': val_loss, 'validation_ranking': metrics,
                      'seconds': time.perf_counter() - started}
            history.append(record)
            candidate_selection = selection_value(args.selection_metric, val_loss, metrics)
            if is_better(args.selection_metric, candidate_selection, best_selection):
                best_selection = candidate_selection
                selected_epoch = epoch + 1
                selected_ranking = metrics
                torch.save({'state_dict': model.state_dict(), 'features': model.features,
                            'kind': args.kind, 'physics': True, 'conditioning': True,
                            'architecture_version': model.architecture_version,
                            'seed': seed, 'epoch': epoch + 1, 'initialization': 'zero_residual',
                            'candidate_label': args.candidate_label,
                            'selection_metric': args.selection_metric, 'selection_value': best_selection},
                           model_dir / 'best.pt')
        (model_dir / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
        metadata = {'arguments': vars(args), 'seed': seed,
                    'parameters': sum(parameter.numel() for parameter in model.parameters()),
                    'best_validation_cross_entropy': min(validation_cross_entropies),
                    'selected_epoch': selected_epoch,
                    'candidate_label': args.candidate_label,
                    'architecture_version': model.architecture_version,
                    'policy_source_sha256': sha256(Path(__file__).resolve().parents[1] / 'src/atomwise_ris/models/policy.py'),
                    'trainer_source_sha256': sha256(Path(__file__).resolve()),
                    'selection_metric': args.selection_metric,
                    'selection_value': best_selection,
                    'best_validation_ranking': selected_ranking,
                    'target_temperature': args.target_temperature,
                    'conditional_weight': args.conditional_weight,
                    'training_examples': len(train['x']), 'validation_examples': len(validation['x']),
                    'train_sha256': sha256(source / 'train_labels.npz'),
                    'validation_sha256': sha256(source / 'validation_labels.npz'),
                    'gate_sha256': sha256(gate_path),
                    'torch': torch.__version__,
                    'device': torch.cuda.get_device_name() if str(args.device).startswith('cuda') else 'cpu',
                    'seconds': time.perf_counter() - started}
        (model_dir / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        print(tag, json.dumps(metadata['best_validation_ranking'], sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
