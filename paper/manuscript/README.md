# Manuscript: matched-budget RIS controller comparison

IEEEtran conference paper with local geometry figures, no shell-escape. It compiles with the desktop LaTeX editor's built-in compiler; Overleaf was not edited.

| File | Purpose |
|---|---|
| `main.tex` | Root document (text, tables, TikZ step-sequence figure, and two geometry figures) |
| `results.tex` | `\newcommand` placeholders for every matched number, decision and outcome sentence; loaded by `main.tex` |
| `references.bib` | All references, each from `RIS Research.xlsx` or `paper/proposal/references.tex` |
| `figures/munich_scene.pdf` | Sionna Munich scene hull visualization exported through DeepMIMO, with original BS/RIS layout and receiver tracks |
| `figures/munich_scene.json` | Figure provenance: export/layout versions, input hashes, depiction scope and render hashes |
| `figures/coupled_wire_geometry.pdf` | NEC-2 free-space wire-model development frame, separate from the Munich scene |
| `figures/coupled_wire_geometry.provenance.json` | Source-frame and data hashes for the copied development geometry figure |
| `main.pdf` | Existing local PDF; it was not updated by the latest built-in source compile |

The Munich figure can be regenerated from the verified local exports with:

```bash
python scripts/plot_munich_scene.py --out-dir paper/manuscript/figures
```

The NEC figure source is `scripts/plot_v2_progress.py`; its development-only source frame and hashes are recorded in `figures/coupled_wire_geometry.provenance.json`.

## Overleaf notes
The existing "RIS" project holds the proposal (`main.tex`, `references.tex`, `framework.tex`). A future authorized import of this separate manuscript must also include both PDFs in `figures/`, along with `results.tex` and `references.bib`. `references.tex` and `framework.tex` are not used by this manuscript and may be deleted from that future manuscript copy. No Overleaf changes were made here.

## Status of results
The pre-registered one-shot matched benchmark (`configs/experiments/matched_v1.json`) completed on the held-out test sets on 2026-11-06 on node `3060-1` (`labkc-comm1`, AMD Ryzen 5 5600, pinned Core~3). The primary budget was locked at 50~ms following the validation feasibility gate (due to deadline misses at 10~ms in coupled wire control). All result macros in `results.tex` are populated from the frozen test summaries (`outputs/runs/matched_specular_v1/summary_test.json` and `outputs/runs/matched_coupled_v1/summary_test.json`) and validation sensitivity summaries (`summary_validation_small.json`, `summary_validation_large.json`). Zero pending markers remain in the manuscript tables or text.

The current `main.tex` source, including both PDF figures, compiled successfully with the Codex desktop editor's built-in LaTeX compiler. That tool did not export or update `main.pdf`; the file listed above is still the earlier local build.

## Open items before submission (also marked in the source)
- Authors, affiliations, contacts, target venue and page limit (the author block is a placeholder).
- Red `[TODO: ...]` markers in `main.tex`: verify the shared step-sequence paragraph against the frozen code hash;
  confirm the timing-exclusion list; state whether `greedy`/`pair`/`random` receive remembered patterns; specify how the
  Holm-corrected interval is constructed (not defined in `matched_v1.json`).
- `% NOVELTY-REVIEW` comments mark the contribution statements; revise them against `docs/novelty-analysis.md`.
- Not cited because no source entry exists: NEC-2/PyNEC and the Sionna ray tracer.

