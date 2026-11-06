# Matched validation fallback gate

The original preferred budget remains 10 ms. The completed validation freeze selected 50 ms under the declared fallback rule after observing deadline misses at 10 ms. The amended protocol records that evidence and locks 50 ms as the primary for the fresh hash-gated validation rerun; 10 ms and the 1/5/100 ms curves remain secondary. If 50 ms is infeasible on the rerun, selection can advance only to the next larger listed budget, 100 ms. It cannot move backward to 10 ms even if fresh timing jitter clears the earlier miss.

The full original protocol is preserved at `configs/experiments/archive/matched_v1-pre-gatefix-lock-20261106.json` (SHA-256 `a033b2866c154ecf296c495673e810e03d6ddd594d8ab32cd8dbb3c42be1edfe`). The locked protocol is SHA-256 `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88`; it declares `preferred_budget_ms: 10`, `primary_budget_ms: 50`, and includes the lock time, rule, and original selection evidence hashes.

The lock evidence preserves both previous selection records: specular selection hash `48225d56302c92cbaf59d618fcfc44cf6f0052a4c936ba6dfef304f201d26966` frozen at `2026-11-06T09:25:22.326695+00:00` with 1 miss at 10 ms and none at 50 ms; coupled selection hash `67bc95b8808728e3fa8e24b67e89dc1b1496ead3884e9a6a509ef78006bea435` frozen at `2026-11-06T09:46:49.504213+00:00` with 6 misses at 10 ms and none at 50 ms. The corresponding unchanged input JSONL hashes are listed below.

The previous validation gate contradicted fallback selection in two places: it rejected any primary-budget miss, and it marked a freeze test-eligible only when the selected budget equaled the primary 10 ms. The corrected gate validates the complete method × seed × budget × validation-frame grid, recomputes feasibility from those rows, and requires the frozen selected budget to equal the protocol rule result. Under the original primary-10 rule, 10 ms misses with a clean 50 ms grid select 50 ms. Under the clarified primary-50 lock, a clean 50 ms grid remains selected even if 10 ms happens to be clean on rerun; 50 ms misses advance to 100 ms.

The change preserves the source JSONL and the original 10 ms misses. It does not edit deadlines or remove misses. Existing frozen selection and validation sidecars are expected to fail the source-hash checks after this gate/protocol amendment. Preserve them for audit; a fresh full validation snapshot and refreeze are required before any later test run. No remote benchmark or held-out test was run as part of this fix.

## Source hashes

| File | Before | After |
|---|---|---|
| `scripts/run_improvement_campaign.py` | `a5c1d2f3ed41999026b74579ee358574ab490bf4123cb857ac9b84ad0a643505` | `dce1afe7751ca20c73e7099d87e7850118d45785ecb6ac97ddc8d7d1e9520b83` |
| `scripts/select_matched_budget.py` | `b118f4abe3385707392797860c03a0555120b8e5e4f9e1e4e0daa8bab704600e` | `ddffc80505e621274e64f2968528ba913e90431b9657c0c8df9054fad39077f1` |
| `scripts/benchmark.py` | `10610255bca6b8acaa01d9bd0a1c7651397d4538b67918ad2c10f14b2cc7090d` | `5305c12c44e04e91c9eaf855d6b791f025d27fdd883c95139f0b7aa145122fed` |
| `scripts/benchmark_coupled.py` | `5dbfa248c3e49cbb842b2c0ec168071064e76b666caf032b3db2f44abbc18bd1` | `c2487861b0938418963261fa51bea7482b0adeb140fd9ba3b5daca59bd296f29` |
| `configs/experiments/matched_v1.json` | `a033b2866c154ecf296c495673e810e03d6ddd594d8ab32cd8dbb3c42be1edfe` | `77f880fa16c489344b0009b21e1a5ad091fd4530b8c53cb74fc83053f0dc2d88` |

The existing validation inputs were left unchanged. Their observed hashes are:

- Specular: `benchmark_validation.jsonl`, `f79fcad0d5d944bdc7cad4717372df51e92fd23e9e427683bc0c71277a0f7bb8`
- Coupled: `benchmark_spatial_validation.jsonl`, `4f0eb966d0be4da83b76b78ac83f232595a4d8f2764377b6f3ae7fa0508b72db`

## Checks

Focused checks run locally:

```sh
PYTHONPATH=src:scripts python -m unittest tests.test_campaign_gates -v
PYTHONPATH=src:scripts python -m unittest tests.test_matched.BudgetSelectionAndRefusal -v
```

The focused campaign tests cover a clean 50 ms fallback after 10 ms misses, rejection of a missed 50 ms selection, rejection of a mismatched selected budget, incomplete-grid refusal, locked-primary behavior, and dynamic rule text. The matched budget/refusal tests also pass; Python compile checks and `git diff --check` passed. After source staging is approved, the validation procedure is to rerun the full registered validation grid on the designated node into a fresh output location, verify all method/seed/budget/frame cells and hashes, run the selection helper, then confirm its selected budget and retained miss counts. Do not reuse the previous selection JSON or sidecars.
