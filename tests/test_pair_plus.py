import numpy as np
import importlib.util
from pathlib import Path
import tempfile

from atomwise_ris.optimization import pair_plus
from atomwise_ris.optimization.pair_plus import (ALL_METHODS, COMBINED_METHODS, FIXED_L2_METHODS, METHODS, NO_L2_METHODS,
                                                   SELECTOR_METHODS, PairPlusMemory, _elite_recombine, search)
from atomwise_ris.optimization import pair_select
from atomwise_ris.physics.network import CoupledNetwork

_runner_spec = importlib.util.spec_from_file_location(
    "benchmark_pair_plus", Path(__file__).resolve().parents[1] / "scripts" / "benchmark_pair_plus.py")
_runner = importlib.util.module_from_spec(_runner_spec)
_runner_spec.loader.exec_module(_runner)


def _timed_search(*args, **kwargs):
    """Use a deterministic monotonic clock to avoid scheduler-sensitive tests."""
    now = [1_000_000_000]
    old_clock = pair_plus.perf_counter_ns

    def fake_clock():
        now[0] += 10_000
        return now[0]

    pair_plus.perf_counter_ns = fake_clock
    try:
        return search(*args, deadline_ns=now[0] + 100_000_000, **kwargs)
    finally:
        pair_plus.perf_counter_ns = old_clock


class _State:
    def __init__(self, bits):
        self.bits = np.asarray(bits, dtype=np.int8).copy()
        # The two diagonal amplitudes encode user rates for the L4 tie-break.
        r0, r1 = _Landscape.user_rates(self.bits)
        self.field = np.diag([np.sqrt(2.0 ** r0 - 1.0), np.sqrt(2.0 ** r1 - 1.0)])


class _Landscape:
    n = 4
    noise = 1.0
    pairs = np.column_stack(np.triu_indices(n, 1))

    @staticmethod
    def user_rates(bits):
        bits = tuple(map(int, bits))
        if bits == (1, 1, 1, 1):
            return 4.0, 4.0
        if bits == (1, 1, 0, 0):
            return 0.5, 0.5
        if bits == (0, 0, 0, 0):
            return 1.0, 1.0
        # A second-user tie-break: these states share max-min zero, but differ
        # in user two's rate when the user-one rate is the bottleneck.
        if bits == (1, 0, 0, 0):
            return 1.0, 1.5
        return 0.2, 0.2

    def state(self, bits):
        return _State(bits)

    def score(self, field):
        rates = np.log2(1.0 + np.abs(field.diagonal()) ** 2 / self.noise)
        return float(min(rates))

    def moves(self, state, pairs=False):
        candidates = self.pairs if pairs else np.arange(self.n).reshape(-1, 1)
        result = []
        for indices in candidates:
            b = state.bits.copy()
            b[indices] ^= 1
            result.append(self.score(self.state(b).field))
        return np.asarray(result)

    def moves_subspace(self, state, atom_indices):
        sub = np.asarray(atom_indices, dtype=int)
        pairs = np.asarray([(sub[i], sub[j]) for i in range(len(sub))
                            for j in range(i + 1, len(sub))], dtype=int).reshape(-1, 2)
        result = []
        for pair in pairs:
            b = state.bits.copy()
            b[pair] ^= 1
            result.append(self.score(self.state(b).field))
        return np.asarray(result), pairs

    def flip(self, state, indices):
        b = state.bits.copy()
        b[np.asarray(indices, dtype=int)] ^= 1
        return self.state(b)


def test_all_ladder_levels_return_exact_valid_actions_and_expose_added_components():
    outputs = {}
    for level, method in enumerate(METHODS, start=1):
        memory = PairPlusMemory()
        if level == 6:
            memory.remember(np.array([1, 1, 0, 0], dtype=np.int8))
        trace = []
        bits, value, count, stats = _timed_search(
            _Landscape(), method, seed=17, memory=memory, trace=trace)
        bits = np.asarray(bits, dtype=np.int8)
        assert bits.shape == (4,)
        assert set(bits.tolist()) <= {0, 1}
        assert value == _Landscape().score(_Landscape().state(bits).field)
        assert count >= 1
        assert trace and trace[0][2] == 1
        outputs[method] = stats
    assert outputs["pair_plus_l1"]["restarts"] > 0
    assert outputs["pair_plus_l2"]["screened_out"] > 0
    assert outputs["pair_plus_l3"]["restart_densities"]
    assert outputs["pair_plus_l4"]["tabu_moves"] > 0
    assert outputs["pair_plus_l4"]["secondary_tie_moves"] > 0
    assert outputs["pair_plus_l5"]["elite_pool_max_size"] >= 1
    assert outputs["pair_plus_l6"]["memory_rescored"] > 0


def test_l4_user2_breaks_tied_single_flip_moves_that_strictly_improve():
    class _StrictImprovingTie(_Landscape):
        @staticmethod
        def user_rates(bits):
            bits = tuple(map(int, bits))
            if bits == (0, 0, 0, 0):
                return 0.0, 0.0
            if bits == (1, 0, 0, 0):
                return 2.0, 2.0
            if bits == (0, 1, 0, 0):
                return 2.0, 3.0
            return 0.2, 0.2

        def state(self, bits):
            class _Candidate:
                def __init__(candidate, pattern):
                    candidate.bits = np.asarray(pattern, dtype=np.int8).copy()
                    r0, r1 = self.user_rates(candidate.bits)
                    candidate.field = np.diag([np.sqrt(2.0 ** r0 - 1.0),
                                               np.sqrt(2.0 ** r1 - 1.0)])
            return _Candidate(bits)

    bits, value, _, stats = _timed_search(_StrictImprovingTie(), "pair_plus_l4", seed=1)
    assert np.isclose(value, 2.0)
    assert bits.tolist() == [0, 1, 0, 0]
    assert stats["secondary_tie_moves"] > 0


def test_l5_recombination_uses_two_elites_with_uniform_inheritance():
    class _Rng:
        def choice(self, count, size, replace):
            assert count == 2 and size == 2 and replace is False
            return np.array([0, 1])

        def random(self, n):
            return np.array([0.1, 0.9, 0.1, 0.9])[:n]

    elites = [(np.array([0, 0, 0, 0]), 1.0), (np.array([1, 1, 1, 1]), 2.0)]
    child = _elite_recombine(elites, _Rng(), 4)
    assert child.tolist() == [0, 1, 0, 1]


def test_l6_memory_resets_between_trajectories_and_has_bounded_capacity():
    memory = PairPlusMemory(capacity=4)
    memory.enter(0)
    for i in range(8):
        bits = np.zeros(8, dtype=np.int8)
        bits[i % 8] = 1
        memory.remember(bits, float(i))
    assert len(memory.patterns) == 4
    memory.enter(1)
    assert memory.patterns == []


def test_unknown_method_and_bad_memory_bits_are_rejected():
    with np.testing.assert_raises(ValueError):
        _timed_search(_Landscape(), "pair_plus_l7", seed=1)
    with np.testing.assert_raises(ValueError):
        PairPlusMemory().remember([0, 2, 1])


def test_runner_rejects_noncanonical_paths_sidecar_mismatch_and_duplicate_lists():
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
        root = tmp_path / "repo"
        canonical = root / "data/processed/coupled_wire_dev_v1"
        canonical.mkdir(parents=True)
        alias = tmp_path / "elsewhere" / "coupled_wire_dev_v1"
        alias.mkdir(parents=True)
        _runner._validate_registered_data_path(canonical.resolve(), root)
        with np.testing.assert_raises(ValueError):
            _runner._validate_registered_data_path(alias.resolve(), root)
    scenario_rows = {3: {"index": 3, "trajectory": 2, "step": 9, "split": "dev"}}
    meta = {"index": 3, "trajectory": 2, "step": 9, "split": "dev"}
    assert _runner._validate_sidecar_row(meta, scenario_rows) == 3
    bad_meta = dict(meta, trajectory=7)
    with np.testing.assert_raises(ValueError):
        _runner._validate_sidecar_row(bad_meta, scenario_rows)
    for values, label in (("10,10", "budgets"), ("7,7", "seeds")):
        with np.testing.assert_raises(ValueError):
            _runner._csv_values(values, float if label == "budgets" else int, label)


def test_fine_dev_runner_requires_complete_source_bound_ready_manifest():
    source_hash = "a" * 64
    scenario_hash = "c" * 64
    indices = set(range(480))
    scenario = {
        "fine_mesh_of": "data/processed/coupled_wire_dev_v1",
        "fine_mesh_split": "dev", "segments": 161,
        "source_scenario_sha256": source_hash,
        "rows": [{"index": i, "split": "dev"} for i in range(480)],
    }
    ready = {
        "status": "complete", "ready_for_development_evaluation": True,
        "expected_indices": list(range(480)), "verified_frame_indices": list(range(480)),
        "missing_frame_indices": [], "invalid_frames": [],
        "frame_npz_sha256": {str(i): f"{i:064x}" for i in range(480)},
        "identity": {"source_scenario_sha256": source_hash, "protocol_sha256": scenario_hash},
        "source_identity_sha256": _runner._identity_sha256(
            {"source_scenario_sha256": source_hash, "protocol_sha256": scenario_hash}),
        "physics_validation": {
            "frames_checked": 480, "minimum_resistance_eigenvalue_ohm_min": 0.0,
            "maximum_scattering_singular_value_max": 1.0,
            "reciprocity_relative_max": 1e-7,
        },
    }
    hashes, physics = _runner._validate_fine_binding(scenario, ready, scenario_hash, source_hash, indices)
    assert len(hashes) == 480
    assert physics["frames_checked"] == 480
    bad = dict(ready, ready_for_development_evaluation=False)
    with np.testing.assert_raises(ValueError):
        _runner._validate_fine_binding(scenario, bad, scenario_hash, source_hash, indices)
    bad_physics = dict(ready, physics_validation=dict(ready["physics_validation"],
                                                       maximum_scattering_singular_value_max=1.01))
    with np.testing.assert_raises(ValueError):
        _runner._validate_fine_binding(scenario, bad_physics, scenario_hash, source_hash, indices)


def test_partial_fine_smoke_requires_bound_identity_and_frame_physics():
    source_hash = "a" * 64
    scenario_hash = "c" * 64
    indices = set(range(480))
    scenario = {
        "fine_mesh_of": "data/processed/coupled_wire_dev_v1",
        "fine_mesh_split": "dev", "segments": 161,
        "source_scenario_sha256": source_hash,
        "rows": [{"index": i, "split": "dev"} for i in range(480)],
    }
    identity = {"protocol_sha256": scenario_hash,
                "source_scenario_sha256": source_hash, "segments_per_wire": 161}
    identity_hash = _runner._identity_sha256(identity)
    ready = {"status": "running", "identity": identity,
             "source_identity_sha256": identity_hash}
    bound_identity, bound_hash = _runner._validate_fine_smoke_binding(
        scenario, ready, scenario_hash, source_hash, indices)
    assert bound_identity == identity and bound_hash == identity_hash
    frame = {
        "index": 0, "split": "dev", "segments_per_wire": 161,
        "generation_identity_sha256": identity_hash,
        "generation_identity": identity, "sha256": "frame-hash",
        "minimum_resistance_eigenvalue_ohm": 0.0,
        "maximum_scattering_singular_value": 1.0,
        "reciprocity_relative": 1e-7,
    }
    old_sha256_file = _runner.sha256_file
    _runner.sha256_file = lambda _: "frame-hash"
    try:
        _runner._validate_fine_smoke_frame(frame, "unused", identity, identity_hash)
        bad = dict(frame, maximum_scattering_singular_value=1.01)
        with np.testing.assert_raises(ValueError):
            _runner._validate_fine_smoke_frame(bad, "unused", identity, identity_hash)
    finally:
        _runner.sha256_file = old_sha256_file


def test_fixed_l2_screens_on_single_flip_history_and_still_runs_pair_search():
    class _Varied(_Landscape):
        n = 8
        pairs = np.column_stack(np.triu_indices(8, 1))

        @staticmethod
        def user_rates(bits):
            # Many distinct single-flip optima, so the history has something to rank.
            rate = 0.1 + 0.3 * float(int("".join(map(str, map(int, bits))), 2) % 11)
            return rate, rate

        def state(self, bits):
            class _Candidate:
                def __init__(candidate, pattern):
                    candidate.bits = np.asarray(pattern, dtype=np.int8).copy()
                    r0, r1 = self.user_rates(candidate.bits)
                    candidate.field = np.diag([np.sqrt(2.0 ** r0 - 1.0), np.sqrt(2.0 ** r1 - 1.0)])
            return _Candidate(bits)

    outputs = {}
    for method in FIXED_L2_METHODS:
        ev = _Varied()
        bits, value, _, stats = _timed_search(ev, method, seed=5)
        assert abs(float(ev.score(ev.state(bits).field)) - value) < 1e-7
        assert stats["restarts"] > stats["screened_out"] > 0
        assert stats["subspace_scans"] == 0 and stats["pair_scans"] > 0
        outputs[method] = stats
    share = {m: s["screened_out"] / s["restarts"] for m, s in outputs.items()}
    assert share["pair_plus_b2t"] >= share["pair_plus_b2"]


def test_b35_combines_restart_density_and_recombination_only():
    assert COMBINED_METHODS == ("pair_plus_b35",)
    spec = pair_plus._spec("pair_plus_b35")
    b3, b5 = pair_plus._spec("pair_plus_b3"), pair_plus._spec("pair_plus_b5")
    assert spec == {k: (b3[k] or b5[k]) if k in ("density", "recombine") else b3[k] for k in b3}
    ev = _Landscape()
    bits, value, _, stats = _timed_search(ev, "pair_plus_b35", seed=3)
    assert abs(float(ev.score(ev.state(bits).field)) - value) < 1e-7
    assert stats["restart_densities"] and stats["recombinations"] > 0
    assert stats["screened_out"] == 0 and stats["tabu_moves"] == 0 and stats["memory_rescored"] == 0


def test_no_l2_methods_add_one_component_each_and_never_screen():
    outputs = {}
    for method in NO_L2_METHODS:
        memory = PairPlusMemory()
        memory.remember(np.array([1] + [0] * (_Landscape().n - 1), dtype=np.int8))
        bits, value, evaluations, stats = _timed_search(_Landscape(), method, seed=3, memory=memory)
        ev = _Landscape()
        assert abs(float(ev.score(ev.state(bits).field)) - value) < 1e-7
        assert evaluations > 0
        assert stats["screened_out"] == 0 and stats["subspace_scans"] == 0
        outputs[method] = stats
    assert not outputs["pair_plus_b0"]["restart_densities"] and outputs["pair_plus_b0"]["tabu_moves"] == 0
    assert outputs["pair_plus_b3"]["restart_densities"] and outputs["pair_plus_b3"]["tabu_moves"] == 0
    assert outputs["pair_plus_b4"]["tabu_moves"] > 0 and outputs["pair_plus_b4"]["recombinations"] == 0
    assert 0 < outputs["pair_plus_b4o"]["tabu_moves"] <= outputs["pair_plus_b4"]["tabu_moves"]
    assert outputs["pair_plus_b5"]["elite_pool_max_size"] >= 1 and outputs["pair_plus_b5"]["memory_rescored"] == 0
    assert outputs["pair_plus_b6"]["memory_rescored"] > 0 and outputs["pair_plus_b6"]["recombinations"] == 0


# ---- pair shortlist selectors -------------------------------------------------------------------

def _network(n=24, seed=4):
    rng = np.random.default_rng(seed)
    m = n + 6
    b = rng.normal(size=(m, m))
    x = rng.normal(size=(m, m))
    z = 4.0 * (b @ b.T) / m + 5.0 * np.eye(m) + 3j * (x + x.T) / 2
    return CoupledNetwork(z, np.array([1.0 + 20.0j, 3.0 - 40.0j]))


class _Counting:
    """Delegating evaluator that tallies every exactly scored candidate."""

    def __init__(self, ev):
        self._ev = ev
        self.scored = 0
        self.pair_calls = []
        self.state_calls = 0

    def __getattr__(self, name):
        return getattr(self._ev, name)

    def state(self, bits):
        self.state_calls += 1
        return self._ev.state(bits)

    def moves(self, state, pairs=False, subset=None):
        out = self._ev.moves(state, pairs, subset)
        self.scored += len(out)
        return out

    def moves_pairs(self, state, pairs):
        out = self._ev.moves_pairs(state, pairs)
        self.pair_calls.append(len(out))
        self.scored += len(out)
        return out


def test_selector_methods_are_registered_and_only_add_a_selector_to_b35():
    assert SELECTOR_METHODS == tuple(f"pair_plus_b35_m0_k{k}" for k in (8, 32, 128, 512)) + (
        "pair_plus_b35_rand_k32", "pair_plus_b35_rand_k128")
    assert set(SELECTOR_METHODS) <= set(ALL_METHODS)
    base = pair_plus._spec("pair_plus_b35")
    assert "selector" not in base
    for method in SELECTOR_METHODS:
        spec = dict(pair_plus._spec(method))
        name, k = spec.pop("selector")
        assert spec == base and name in ("m0", "rand") and method.endswith(f"_k{k}")


def test_selectors_return_unique_valid_pair_indices_deterministically():
    ev = _network()
    state = ev.state(np.random.default_rng(1).integers(0, 2, ev.n))
    gains = ev.moves(state) - ev.score(state.field)
    pairs = len(ev.pairs)
    for k in (1, 8, 128, pairs, pairs + 50):
        for selector in (pair_select.analytic_topk, pair_select.random_topk):
            idx = np.asarray(selector(ev, state, gains, k, np.random.default_rng(7)))
            assert len(idx) == len(set(idx.tolist())) == min(k, pairs)
            assert idx.min() >= 0 and idx.max() < pairs
    a = pair_select.random_topk(ev, state, None, 32, np.random.default_rng(7))
    b = pair_select.random_topk(ev, state, None, 32, np.random.default_rng(7))
    c = pair_select.random_topk(ev, state, None, 32, np.random.default_rng(8))
    assert np.array_equal(a, b) and not np.array_equal(a, c)
    assert np.array_equal(pair_select.analytic_topk(ev, state, gains, 32),
                          pair_select.analytic_topk(ev, state, gains, 32))


def test_m0_priority_is_single_gains_plus_a_pairwise_correction_and_finds_top_pairs():
    ev = _network()
    state = ev.state(np.random.default_rng(2).integers(0, 2, ev.n))
    gains = ev.moves(state) - ev.score(state.field)
    priority = pair_select.m0_priority(ev, state, gains)
    i, j = ev.pairs.T
    assert priority.shape == (len(ev.pairs),) and np.isfinite(priority).all()
    exact = ev.moves(state, True) - ev.score(state.field)
    # The proxy must carry real signal about the exact pair gain.
    assert np.corrcoef(priority, exact)[0, 1] > 0.9
    top = np.argsort(exact)[::-1][:1]
    shortlist = pair_select.analytic_topk(ev, state, gains, len(ev.pairs) // 4)
    assert set(top.tolist()) <= set(shortlist.tolist())


def test_pair_features_are_symmetric_vectorized_and_never_use_the_pair_gain():
    ev = _network()
    state = ev.state(np.random.default_rng(3).integers(0, 2, ev.n))
    gains = ev.moves(state) - ev.score(state.field)

    class _NoPairGain:
        def __init__(self, inner):
            self.__dict__["_i"] = inner

        def __getattr__(self, name):
            if name in ("moves_pairs", "moves_subspace", "moves_anchors", "moves", "flip", "state"):
                raise AssertionError(f"feature builder must not call {name}")
            return getattr(self._i, name)

    pf = pair_select.pair_features(_NoPairGain(ev), state, gains)
    flat = pf.flat()
    d, e = pf.atom.shape[1], pf.edge.shape[1]
    assert flat.shape == (len(ev.pairs), 3 * d + e) and e == 8 and np.isfinite(flat).all()
    swapped = pair_select.pair_features(ev, state, gains, pairs=ev.pairs[:, ::-1]).flat()
    np.testing.assert_allclose(swapped, flat, atol=1e-6)
    gi, gj = gains[ev.pairs[:, 0]], gains[ev.pairs[:, 1]]
    np.testing.assert_allclose(pf.edge[:, 4], gi + gj, rtol=1e-5, atol=1e-6)
    np.testing.assert_allclose(pf.edge[:, 5], gi * gj, rtol=1e-5, atol=1e-6)


def test_neural_topk_adapter_uses_a_numpy_scorer_and_returns_only_indices():
    ev = _network()
    state = ev.state(np.zeros(ev.n, dtype=np.int8))
    gains = ev.moves(state) - ev.score(state.field)
    target = 123

    def scorer(pf):
        assert isinstance(pf.flat(), np.ndarray)
        s = np.zeros(len(pf.pairs))
        s[target] = 1.0
        return s

    idx = pair_select.neural_topk(scorer)(ev, state, gains, 4, None)
    assert target in idx and len(idx) == 4
    mlp = pair_select.NumpyPairMLP.random(3 * pair_select.atom_features(ev, state, gains).shape[1] + 8, seed=1)
    idx = pair_select.neural_topk(mlp)(ev, state, gains, 16, None)
    assert len(set(idx.tolist())) == 16
    attn = pair_select.NumpyAttentionPairScorer.random(pair_select.atom_features(ev, state, gains).shape[1], 8, seed=1)
    assert attn(pair_select.pair_features(ev, state, gains)).shape == (len(ev.pairs),)
    with np.testing.assert_raises(ValueError):
        pair_select.neural_topk(lambda pf: np.zeros(3))(ev, state, gains, 4, None)


def test_selector_methods_return_exact_values_count_only_scored_candidates_and_record_stats():
    for method in SELECTOR_METHODS:
        ev = _Counting(_network())
        bits, value, count, stats = _timed_search(ev, method, seed=5)
        exact = float(ev.score(ev.state(np.asarray(bits)).field))
        assert abs(exact - value) < 1e-9
        assert stats["late_scans"] == 0
        for key in ("shortlist_scans", "fallback_scans", "selector_ms"):
            assert key in stats
        assert stats["shortlist_scans"] == len(ev.pair_calls) > 0
        assert max(ev.pair_calls) <= int(method.rsplit("_k", 1)[1])
        # state() was called once per scored start; everything else counted is a batch score.
        ev.state_calls -= 1  # the verification state() above
        assert count == ev.scored + ev.state_calls, (method, count, ev.scored, ev.state_calls)
        full_scans = stats["pair_scans"]
        assert full_scans == stats["fallback_scans"]


def test_a_shortlist_that_misses_every_improvement_falls_back_to_the_exact_full_scan():
    base = _network()

    def run(selector):
        old = pair_select.SELECTORS["m0"]
        pair_select.SELECTORS["m0"] = selector
        try:
            ev = _Counting(base)
            out = _timed_search(ev, "pair_plus_b35_m0_k8", seed=9)
            return ev, out
        finally:
            pair_select.SELECTORS["m0"] = old

    # A selector that always returns the first 8 pair indices usually misses every improving pair,
    # so the exact fallback must still reach a verified local optimum.
    def worst(ev, state, gains, k, rng):
        return np.arange(k)
    worst.needs_gains = False
    ev, (bits, value, _, stats) = run(worst)
    assert stats["fallback_scans"] > 0 and stats["pair_scans"] >= stats["fallback_scans"]
    assert abs(float(base.score(base.state(bits).field)) - value) < 1e-9


def test_a_lying_pair_scorer_is_rejected_by_full_verification():
    class _Liar(CoupledNetwork):
        def moves_pairs(self, state, pairs):
            return super().moves_pairs(state, pairs) + 5.0

    base = _network()
    liar = _Liar.__new__(_Liar)
    liar.__dict__.update(base.__dict__)
    with np.testing.assert_raises(AssertionError):
        _timed_search(liar, "pair_plus_b35_m0_k32", seed=2)


def test_invalid_selector_indices_are_rejected():
    old = pair_select.SELECTORS["rand"]
    pair_select.SELECTORS["rand"] = lambda ev, state, gains, k, rng: np.array([len(ev.pairs)])
    pair_select.SELECTORS["rand"].needs_gains = False
    try:
        with np.testing.assert_raises(ValueError):
            _timed_search(_network(), "pair_plus_b35_rand_k32", seed=1)
    finally:
        pair_select.SELECTORS["rand"] = old
