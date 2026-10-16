# Feature Test Report: a new research question

**Date:** 2026-10-17  
**Project type:** offline CLI, agent skill, and interactive viewer  
**Features tested:** initialization, validation, build, compare, review, diff, viewer, exports  
**Use Case:** ephemeral — prepare a reading-group map of the transition to attention in neural machine translation  
**Profile:** ephemeral — a researcher comfortable with Python, unfamiliar with this toolkit  
**Expected Outcome:** author a new question from an empty draft and inspect/share its complete source-grounded map  
**Verdict:** pass after fixes; v0.1.0 failed the export and viewer edge cases below  
**Critical Issues:** 0 remaining in the tested paths

## Setup and research

The actual published v0.1.0 skill ZIP was downloaded from GitHub, its SHA-256
verified, and extracted outside the checkout. `python -I .../scripts/lineage.py
init` created the new NMT question with empty works/results. Building the empty
draft returned exit 2. No bundled quantum results were inserted.

The host agent followed the skill's evidence-first workflow using the six pinned
primary PDFs in [the research log](../../examples/nmt-attention/README.md).
This was a real authoring run, with targeted reference tracing and section-level
reading. It was not an automated retrieval benchmark or an external expert review.

The resulting input has 6 works, 7 recorded versions, 6 results, 6 evidence records,
and 6 proposed relationships. Five connections are author-explicit and one is
marked editorial inference. Both the published runtime and the corrected runtime
accept the same input. All costs except the extracted Transformer layer cost stay
unknown; no BLEU leaderboard is inferred.

## Expected and observed

| Feature | Expected | Observed |
| --- | --- | --- |
| New input | No hidden example substitution | Empty draft; empty build rejected |
| Validation/build | Accept checked non-demo data | Four files produced, 12 unreviewed-item warning |
| Comparison | Preserve differing settings and unknowns | ConvS2S cost remains unknown beside the Transformer layer cost; pinned v2/v1 links appear |
| Review report | Keep scope and provenance | All exclusions, search strategy, evidence kinds, settings, and review context retained after fix |
| Revision diff | Describe rather than approve edits | Proposal includes changed fields and collection order; inputs preserved |
| Keyboard | Activate results, relations, and list entries | Enter activated result/edge; Space activated a reading-list item |
| Relation filter recovery | Restore valid selection after empty search | Reproduced v0.1.0 failure; Reset and manual search clearing both restore details after fix |
| Version index | Identify the actually cited version | ConvS2S v1 is “Recorded version; not cited”; v2 is “Cited in this map” after fix |
| Reading route | Every step reachable with safe bounds | 6/6 steps visited in order; first Previous and last Next disabled; Exit hides controls |
| Narrow viewport | No page-level horizontal overflow | Actual 389 CSS px viewport: client width 367, scroll width 367; graph scrolls within its pane |
| Filtered exports | Export the complete dataset | With 2/6 results selected by lane, actual downloaded HTML/SVG/JSON each recover all 6 works/results/relations/evidence, equal to input |
| Portable HTML | Embedded assets, complete graph, closed dialogs | Downloaded HTML has no external runtime asset, retains six nodes, closed dialog, and offline CSP |
| SVG evidence | Readable context and recoverable complete data | Actual downloaded SVG includes visible scope/evidence appendix and a JSON metadata record equal to input |

The browser was Chromium-based and served the generated files over loopback HTTP.
The browser tool's viewport override is affected by its zoom factor; the actual
measured width is reported above. Browser `file:` navigation is unavailable in
this environment, so reopening downloaded HTML through that protocol is not
claimed. Exported bytes were inspected directly. No assistive-technology or
two-host field certification is claimed.

## Failures that changed the implementation

The run and independent issue audits found three failed acceptance areas:

- #2: unrelated or different-version full text could incorrectly satisfy the
  reviewed-content requirement. The corrected guard binds full text to the
  result's exact version, or the relationship target's exact version.
- #3: report/SVG evidence context was incomplete; input names other than map.json
  could bypass the build overwrite guard; lane reorder diffs were missing; raw
  imported HTML was emitted in Markdown reports. Regressions now cover each case.
- #4: a relationship selection did not recover after empty search, and the scope
  index linked only the first recorded paper version. Both were reproduced on the
  new map before correction and exercised again afterward.

Discovery and setup were clear from the README and data guide. Authoring still
requires the host's research capabilities and explicit evidence entry, as
documented. The additional worked example makes that boundary concrete.

## Reproduce the new-question workflow

```sh
research-lineage init "How did neural machine translation progress from fixed-length encoding through learned attention to the Transformer?" --id nmt-attention --cutoff 2017-12-31 --out output/nmt-empty.json
# Empty drafts intentionally cannot build. Author checked evidence using the data guide.
research-lineage validate examples/nmt-attention/map.json
research-lineage build examples/nmt-attention/map.json --out output/nmt
research-lineage compare examples/nmt-attention/map.json r-convs2s r-transformer
research-lineage review examples/nmt-attention/map.json --out output/nmt-review.md
research-lineage diff output/nmt-empty.json examples/nmt-attention/map.json --out output/nmt-proposal.json
```

Keep the cutoff, gaps, and proposed review status when reusing this map.
