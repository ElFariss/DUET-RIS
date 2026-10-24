# Meta-atom-aware RIS proposal

IEEE conference style (IEEEtran, two columns), revised 21 October 2026 from the supplied English proposal. This is a research plan, not a results paper. No training or electromagnetic experiments were executed.

## Files

- `main.tex`: main LaTeX document.
- `references.tex`: twelve linked references.
- `figures/framework.tex`: original editable TikZ architecture figure.
- `main.pdf`: compiled reading copy, when compilation succeeds.
- `source-audit.md`: literature provenance, verification scope, and unresolved review items.

Open this directory in the Codex LaTeX editor, or compile `main.tex` with a standard LaTeX distribution supporting TikZ. References are embedded; BibTeX is not required. Tectonic command: `tectonic -X compile main.tex`.

## Main revision

The original proposal primarily learned mutation priorities for single-user RIS control. The revision identifies an analytical challenge: independent two-state scalar channels retain a signed-sum structure, and individual flip effects are cheap to calculate. The proposed contribution therefore centers on conditional groups of edits for fixed-precoder multiuser adaptation, with single-user cases retained as diagnostic controls. This is a proposed scope change, explicitly stated in the document, not an experimental finding.

The eight original references are retained in substance, with the two software entries updated to official project documentation. Four entries are added: Qian and Di Renzo, Zhang et al., Zheng et al., and openEMS boundary-condition documentation. Final total: twelve references. Eight substantive methodological changes: narrower claim, analytical flip baseline, multiuser core, specified conditional policy and supervision, physical validation levels, controlled evaluation, decision gates, and an editable system figure. Revision and source-access notes are kept outside the academic proposal.

Consensus calls failed with reauthentication errors; the user explicitly requested continuing without Consensus. Publisher, author, and official documentation sources were used instead. No exhaustive novelty or SOTA claim is made.
