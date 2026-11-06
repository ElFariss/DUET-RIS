"""Train fresh coupled spatial policies without reusing prior checkpoints."""
import argparse
import json
import shutil
import time
from pathlib import Path

import numpy as np
import torch

from atomwise_ris.core import sha256
from atomwise_ris.models.coupled_policy import CoupledPolicy


def recover_stages(x, mask, weight):
    """Verify prepare_coupled.py's documented weight/marker stage convention."""
    marker = x[:, :, -1]
    first = np.isclose(weight, 1.)
    conditional = np.isclose(weight, .25)
    if not np.all(first | conditional):
        raise ValueError('Coupled weights must be exactly first=1 or conditional=.25')
    if np.any(np.abs(marker[first]).sum(axis=1) != 0):
        raise ValueError('First-stage rows must have no first-bit marker')
    if np.any(np.abs(marker[conditional]).sum(axis=1) != 1):
        raise ValueError('Conditional rows must have exactly one first-bit marker')
    if np.any((marker[conditional] > .5) != mask[conditional]):
        raise ValueError('Conditional marker and masked first bit disagree')
    stages = np.empty(len(weight), dtype='<U11')
    stages[first] = 'first'
    stages[conditional] = 'conditional'
    return stages


def load_data(path, scaling, device, conditional_weight=.5, target_temperature=.25):
    with np.load(path) as archive:
        required = {'x', 'target', 'analytical', 'mask', 'weight'}
        missing = required.difference(archive.files)
        if missing:
            raise ValueError(f'{path} is missing label arrays: {sorted(missing)}')
        raw = {key: archive[key].copy() for key in required}
    stages = recover_stages(raw['x'], raw['mask'], raw['weight'])
    target = np.power(np.maximum(raw['target'].astype(np.float32), 0.), 1. / target_temperature)
    target /= np.maximum(target.sum(axis=1, keepdims=True), 1e-12)
    raw['target'] = target
    raw['x'] = (raw['x'] - scaling['mean']) / scaling['std']
    effective_weight = np.where(stages == 'first', 1., conditional_weight).astype(np.float32)
    result = {key: torch.as_tensor(value, device=device) for key, value in raw.items()}
    result['weight'] = torch.as_tensor(effective_weight, device=device)
    result['stage'] = stages
    result['source_weight'] = raw['weight']
    return result


def ranking_metrics(scores, target, mask, weight):
    scores = scores.masked_fill(mask, -1e9)
    target = target.masked_fill(mask, 0.)
    top1 = scores.argmax(-1)
    mass1 = target.gather(-1, top1[:, None]).squeeze(-1)
    maximum = target.max(-1).values
    denominator = weight.sum().clamp_min(1e-12)
    indices = scores.topk(min(5, scores.shape[-1]), dim=-1).indices
    mass5 = target.gather(-1, indices).sum(-1)
    return {
        'top1_target_mass': float((mass1 * weight).sum() / denominator),
        'top5_target_mass': float((mass5 * weight).sum() / denominator),
        'soft_target_regret': float(((maximum - mass1).clamp_min(0.) * weight).sum() / denominator),
        'target_mode_accuracy': float(((top1 == target.argmax(-1)).float() * weight).sum() / denominator),
        'rows': int(len(scores)),
    }


def stage_metrics(model, data, device):
    scores = model(data['x'], data['analytical'])
    result = {}
    for stage in ('first', 'conditional'):
        indices = torch.as_tensor(np.flatnonzero(data['stage'] == stage), device=device)
        result[stage] = ranking_metrics(scores[indices], data['target'][indices], data['mask'][indices],
                                        data['weight'][indices])
    result['balanced_top5_target_mass'] = float((result['first']['top5_target_mass'] +
                                                 result['conditional']['top5_target_mass']) / 2.)
    return result


def loss(model, data, indices):
    scores = model(data['x'][indices], data['analytical'][indices]).masked_fill(data['mask'][indices], -1e9)
    per_row = -(data['target'][indices] * torch.log_softmax(scores, dim=-1)).sum(-1)
    weights = data['weight'][indices]
    return (per_row * weights).sum() / weights.sum().clamp_min(1e-12)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, help='base coupled run with physics_gate and feature_scaling')
    parser.add_argument('--data', required=True, help='directory containing train_labels.npz and validation_labels.npz')
    parser.add_argument('--physics-data', required=True, help='immutable coupled dataset.npz used by the labels')
    parser.add_argument('--out', required=True, help='new run root; must not exist')
    parser.add_argument('--kinds', nargs='+', choices=['attention', 'mlp'], default=['attention', 'mlp'])
    parser.add_argument('--seeds', nargs='+', type=int, default=[7, 19, 43])
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--target-temperature', type=float, default=.25)
    parser.add_argument('--conditional-weight', type=float, default=.5)
    parser.add_argument('--device', default='cuda')
    args = parser.parse_args()

    run, source, out = Path(args.run), Path(args.data), Path(args.out)
    gate_path = run / 'physics_gate.json'
    scaling_path = run / 'feature_scaling.npz'
    if not json.loads(gate_path.read_text())['passed']:
        raise RuntimeError('Coupled physics gate did not pass')
    if out.exists():
        raise FileExistsError(f'Output root already exists; choose a fresh --out: {out}')
    if args.epochs < 1 or args.target_temperature <= 0 or args.conditional_weight < 0:
        raise ValueError('epochs and target temperature must be positive; conditional weight nonnegative')
    if not args.seeds or len(set(args.seeds)) != len(args.seeds) or not args.kinds:
        raise ValueError('Seeds and model kinds must be nonempty and seeds unique')
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA requested but unavailable')
    torch.set_num_threads(1)
    scaling_archive = np.load(scaling_path)
    scaling = {'mean': scaling_archive['mean'], 'std': scaling_archive['std']}
    data_hash = sha256(args.physics_data)
    provenance_path = run / 'provenance.json'
    if provenance_path.exists():
        expected_hash = json.loads(provenance_path.read_text()).get('data_sha256')
        if expected_hash and expected_hash != data_hash:
            raise ValueError('The explicit physics dataset hash differs from the coupled run provenance')
    train = load_data(source / 'train_labels.npz', scaling, args.device,
                      args.conditional_weight, args.target_temperature)
    validation = load_data(source / 'validation_labels.npz', scaling, args.device,
                           args.conditional_weight, 1.)
    validation_original = load_data(source / 'validation_labels.npz', scaling, args.device,
                                    args.conditional_weight, 1.)
    out.mkdir(parents=True)
    shutil.copy2(gate_path, out / 'physics_gate.json')
    shutil.copy2(scaling_path, out / 'feature_scaling.npz')
    (out / 'models').mkdir()
    reused_control_hashes = {}
    for seed in args.seeds:
        baseline = run / 'models' / f'attention_no_physics_seed{seed}'
        if not baseline.is_dir():
            raise FileNotFoundError(f'Missing frozen attention-no-physics control for seed {seed}: {baseline}')
        destination = out / 'models' / baseline.name
        shutil.copytree(baseline, destination)
        reused_control_hashes[str(seed)] = sha256(destination / 'best.pt')
    start_total = time.perf_counter()
    for kind in args.kinds:
        for seed in args.seeds:
            torch.manual_seed(seed)
            np.random.seed(seed)
            model = CoupledPolicy(kind=kind, physics=True).to(args.device)
            optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-3)
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-5)
            model_dir = out / 'models' / f'{kind}_seed{seed}'
            model_dir.mkdir()
            started = time.perf_counter()
            with torch.inference_mode():
                initial_metrics = stage_metrics(model, validation_original, args.device)
                initial_loss_parts = [(float(loss(model, validation, ix)), float(validation['weight'][ix].sum()))
                                      for ix in torch.arange(len(validation['x']), device=args.device).split(128)]
                initial_ce = sum(v * n for v, n in initial_loss_parts) / sum(n for _, n in initial_loss_parts)
            best = initial_metrics['balanced_top5_target_mass']
            selected_epoch = 0
            selected_metrics = initial_metrics
            history = [{'epoch': 0, 'train_cross_entropy': None, 'validation_cross_entropy': initial_ce,
                        'validation_ranking': initial_metrics, 'seconds': 0.}]
            torch.save({'state_dict': model.state_dict(), 'kind': kind, 'seed': seed, 'epoch': 0,
                        'architecture_version': model.architecture_version,
                        'initialization': 'zero_residual', 'selection_metric': 'balanced_top5_target_mass',
                        'selection_value': best}, model_dir / 'best.pt')
            for epoch in range(args.epochs):
                model.train()
                losses = []
                for indices in torch.randperm(len(train['x']), device=args.device).split(64):
                    optimizer.zero_grad(set_to_none=True)
                    value = loss(model, train, indices)
                    value.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
                    optimizer.step()
                    losses.append(float(value.detach()))
                scheduler.step()
                model.eval()
                with torch.inference_mode():
                    parts = [(float(loss(model, validation, ix)), float(validation['weight'][ix].sum()))
                             for ix in torch.arange(len(validation['x']), device=args.device).split(128)]
                    val_ce = sum(v * n for v, n in parts) / sum(n for _, n in parts)
                    metrics = stage_metrics(model, validation_original, args.device)
                history.append({'epoch': epoch + 1, 'train_cross_entropy': float(np.mean(losses)),
                                'validation_cross_entropy': val_ce, 'validation_ranking': metrics,
                                'seconds': time.perf_counter() - started})
                score = metrics['balanced_top5_target_mass']
                if score > best:
                    best = score
                    selected_epoch = epoch + 1
                    selected_metrics = metrics
                    torch.save({'state_dict': model.state_dict(), 'kind': kind, 'seed': seed,
                                'epoch': selected_epoch, 'architecture_version': model.architecture_version,
                                'initialization': 'zero_residual',
                                'selection_metric': 'balanced_top5_target_mass', 'selection_value': best},
                               model_dir / 'best.pt')
            (model_dir / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
            metadata = {
                'args': vars(args), 'candidate_label': 'coupled_sharp_balanced_conditional_rank_dev',
                'architecture_version': model.architecture_version, 'selected_epoch': selected_epoch,
                'selection_metric': 'balanced_top5_target_mass', 'selection_value': best,
                'best_validation_ranking': selected_metrics,
                'best_validation_cross_entropy': min(item['validation_cross_entropy'] for item in history),
                'training_examples': len(train['x']), 'validation_examples': len(validation['x']),
                'effective_training_weight_by_stage': {'first': 1., 'conditional': args.conditional_weight},
                'source_label_weight_counts': {str(value): int(count) for value, count in
                                               zip(*np.unique(train['source_weight'], return_counts=True))},
                'stage_recovery': 'prepare_coupled.py add(-1,...,1) has no marker; add(first,...,.25) marks and masks exactly first bit',
                'train_sha256': sha256(source / 'train_labels.npz'),
                'validation_sha256': sha256(source / 'validation_labels.npz'),
                'physics_data_sha256': data_hash, 'feature_scaling_sha256': sha256(scaling_path),
                'physics_gate_sha256': sha256(gate_path),
                'policy_source_sha256': sha256(Path(__file__).resolve().parents[1] / 'src/atomwise_ris/models/coupled_policy.py'),
                'trainer_source_sha256': sha256(Path(__file__).resolve()),
                'seconds': time.perf_counter() - started,
                'device': torch.cuda.get_device_name() if str(args.device).startswith('cuda') else 'cpu',
            }
            (model_dir / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
            print(kind, seed, json.dumps({'selected_epoch': selected_epoch,
                                          'selection_value': best, 'validation': selected_metrics}, sort_keys=True),
                  flush=True)
    (out / 'run_metadata.json').write_text(json.dumps({
        'candidate_label': 'coupled_sharp_balanced_conditional_rank_dev',
        'source_data_sha256': data_hash, 'train_sha256': sha256(source / 'train_labels.npz'),
        'validation_sha256': sha256(source / 'validation_labels.npz'),
        'epochs_per_model': args.epochs, 'model_kinds': args.kinds, 'seeds': args.seeds,
        'reused_attention_no_physics_checkpoint_sha256': reused_control_hashes,
        'seconds': time.perf_counter() - start_total,
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
