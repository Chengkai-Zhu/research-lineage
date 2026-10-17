# Changelog

## Unreleased — 0.2.0

- Replace the default paper quota with adaptive, source-grounded coverage and
  preserve the research-date cutoff independently of the seed's version date.
- Add portable research-record schemas and an offline audit of execution
  provenance, cutoff consistency, source trails and research-plan completion.
- Make the skill the primary entry point: start with a topic or one paper, with
  bounded defaults, language inference and preserved source identifiers.
- Lead with a reading overview and source-linked turning points. Reveal the
  graph, filters and collapsible evidence when readers choose to explore.
- Add explicit bounded Crossref/arXiv discovery, conservative identity grouping,
  evidence gates and non-mutating source-version availability proposals.
- Add reproducible engineering evaluation and consent-aware reading-study tools;
  real independent review and participant validation remain open in #10.
- Add a surface-code history from one paper seed and recheck the NMT workflow.
- Provide equivalent English and Simplified Chinese READMEs with language links.

## 0.1.1 — 2026-10-17

- Bind recorded-review full-text evidence to the result's pinned work/version or
  the relationship target's pinned work/version.
- Preserve complete scope, source versions, evidence limitations, conditions,
  relationship basis, comparability, and reviewer references in static exports.
  Both SVG exporters use the same readable appendix and include complete JSON
  metadata. Escape imported Markdown report text.
- Reject build output that aliases any input filename, including existing hard
  links; apply alias protection to review and diff output as well.
- Include collection-order changes in revision proposals.
- Restore relationship details after empty filters and identify each source
  version as cited or merely recorded.
- Add a new six-paper neural-machine-translation map, research log, and actual
  feature-test record. Preserve the original v0.1.0 audit failures in verification
  history rather than replacing the old tag.

## 0.1.0 — 2026-10-17

Initial skill, Python CLI, offline viewer, and QSP/QSVT draft. See
[original release notes](docs/release-notes-v0.1.0.md). The later acceptance audit
identified the defects corrected in 0.1.1 above.
