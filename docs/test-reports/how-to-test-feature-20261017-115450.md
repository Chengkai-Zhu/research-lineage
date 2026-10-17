# Test Report: research-lineage skill and LitDelta final delivery

**Date:** 2026-10-17
**Persona:** Simulated ML PhD, comfortable with terminal/Python, new to this repository, seeking a reading aid with inspectable evidence
**Profile:** ephemeral
**Use Case:** ephemeral, owner-selected issue20 offline and agent delivery paths
**Expected Outcome:** Understand host versus toolkit responsibilities, extract and run the portable skill without a global install, generate the comparison demo, choose supported/cost/incomparable questions, and retain all three complete map outputs and their evidence boundaries.
**Phases tested:** Read delivery documentation; inspect landing and source-note links statically; extract/check offline collection; extract/run portable skill; generate, validate, compare and review; inspect preserved research audit
**Decision points exercised:** Three owner-selected comparison choices; no conversational role-play questions were required
**Verdict:** pass
**Critical Issues:** 0
**Final tested revision:** d0f225d5e8e6bae932a53ef877bb6f28515716e5
**Final tested build:** `/private/tmp/research-lineage-issue20/output/litdelta-delivery-d0f225d`

This is simulated downstream-user evidence. The verdict covers actual offline commands and static artifact checks. It does not establish browser behavior, scientific correctness, independent review, participant experience, or measured reading benefit.

## Flow Completeness

- **Phases reached:** Portable installation into a fresh temporary host-like folder; isolated runtime execution; example generation; explicit comparison selection; structural validation; complete-output inspection; source-note portability recheck after repair.
- **Phases skipped:** Global skill installation and host reload were intentionally excluded by the test guardrails. New research, source retrieval, accounts and external services were outside the selected offline scope. This subagent performed no external network access, secret access, escalation, source edits or commits.
- **Choices exercised:** Pair-only abstention; authored sequential-depth improvement; authored total-work tradeoff; authored quality incomparability.
- **Untested branches:** Fresh paper research; model/host integrations; actual browser clicks, downloads, repeated saves and Explore restoration. The decoding comparison was exercised at baseline, rather than repeated on this final revision.

## Interaction Trace

1. At baseline `11d262e`, README, quickstart, LitDelta docs, comparison source notes and canonical skill explained that the host researches while the toolkit prepares, validates and renders. A one-paper start returned awaiting_host_research with an empty draft; build refused to replace it with an example. See `baseline-report.md`.
2. Tested the `ff6033d` delivery and found 22 optional source-note links that assumed the checkout directory structure. The parent repaired delivery-link rewriting and skill discoverability, then supplied a fresh final build.
3. Inspected final clean revision `d0f225d5e8e6bae932a53ef877bb6f28515716e5`. Checked every declared manifest SHA-256 and byte count, safe relative ZIP entry names, complete intended inventory and archived bytes, then extracted the collection into a fresh temporary subdirectory.
4. Parsed index.html and extracted START-HERE.html as static source. All local landing targets exist. Supported/quality comparison, author and research-history deep links are present. START-HERE omits the unavailable archive self-download and says the collection is already present.
5. Parsed all three source-note Markdown files. Each has a working local map.html reader link. The remaining repository references use absolute GitHub blob URLs pinned to the final revision; all 24 such references name Git objects present at that revision. Their external reachability was not fetched or verified. Notes explicitly distinguish online source-record references from files included in the ZIP and explain that historical issue-status statements belong to the source record.
6. Compared all three delivered JSON maps with canonical repository inputs and their HTML-embedded map-data. All are equal as JSON, including the entire surface-code corpus.
7. Extracted the final delivered skill ZIP into a fresh temporary folder and actually ran `/private/tmp/litdelta-venv/bin/python -I -S .../scripts/lineage.py demo --example comparisons --out .../generated`. No package installation, account or key was supplied. The runtime was Python 3.13.5, isolated and no-site mode; this run does not independently establish every supported Python version.
8. Ran validate, pair-only compare, chosen depth/cost/quality compare, explicit review and recorded audit through the same final extracted isolated runner. Preserved command stdout/stderr and generated outputs.

## Output Validation

| Output/check | Expected | Observed on final d0f225d build |
| --- | --- | --- |
| Manifest | All declared checksums and bytes match | 20 entries, 0 mismatches; clean final revision provenance |
| Offline collection | Complete selected inventory plus manifest | 20 files, 395,413 bytes; exact inventory and byte equality |
| Portable skill | Runtime and example included | 30 archive files, 88,717 bytes; vendored CLI present |
| Comparison map | Complete data retained | 1 work, 4 results, 1 relation, 4 evidence records, 4 comparisons, 4 route steps |
| Author map | Complete data retained | 6 works, 6 results, 6 relations, 6 evidence records, 6 route steps |
| Actual research map | Full corpus distinct from short route | 52 works, 54 results, 58 relations, 55 evidence records, 9 route steps |
| Map equality | Canonical and HTML data preserved | All 3 delivered JSON maps equal canonical JSON and HTML embeddings |
| HTML dependencies | No external script needed | No external script reference in the 3 generated maps |
| Local landing/source-note links | Present after extraction | 0 missing targets; START-HERE has no offline.zip link |
| Online repository references | Explicit, pinned source-record destinations | 24 valid local Git-object references, pinned to final revision; no network reachability claim |
| Pair-only comparison | Ask which question rather than assert improvement | unknown, two choices, selection_required=true |
| c-parallel-depth | Scoped improvement | comparable/improvement; input-availability and Table 1 regime retained |
| c-total-work | Separate total-cost question | comparable/tradeoff; n/d dependence retained |
| c-quality | Different criteria do not imply improvement | incomparable/not_assessed |
| Validation | Structure valid and review limit retained | Exit 0; scholarly-review warning retained |
| Research audit | Preserve PARTIAL and component outcomes | Exit 3; JSON equals delivered audit |
| Review units | Human-readable missing units | No `[None]` in delivered reviews or new/explicit comparison review |

The isolated final skill generated exactly four files: map.html (100,307 bytes), map.svg (39,882 bytes), map.json (14,281 bytes), and review.md (8,393 bytes). Generated comparison JSON equals delivered example JSON.

The actual research audit retains provenance/cutoff/source-trail PASS and research-completion PARTIAL. It records 58 candidates, 52 included works, 6 exclusions, 95 research-operation records and 109 trace entries. Unresolved central coverage and declared partial stopping state remain present. These counts are recorded evidence, not independently authenticated execution or scientific completeness.

## Defects Fixed

1. **Fixed — source-note portability:** The 22 missing optional relative links observed at ff6033d are no longer missing local targets. Every source note now begins with its delivered reader link; checkout references are explicit revision-pinned online source-record links. The historical-status caveat is present in all three notes.
2. **Fixed — skill-only discoverability:** Canonical SKILL.md now explicitly names `demo --example comparisons --out output/comparisons` for the focused LitDelta reader.
3. **Fixed — missing-unit presentation:** `[None]` observed in the baseline review is absent from all three delivered reviews and the newly generated/explicit comparison review.

No unresolved product defect was found in this subagent's selected offline/static path.

## Broken References and Verification Limits

No missing local link target remains in the final landing pages or packaged source notes. Online repository/source links were inspected as strings and checked against local Git objects where applicable; none was fetched.

At baseline, browser-file navigation was rejected by browser URL security policy because file:// is unsupported. This subagent did not attempt a workaround or another browser surface and performed no browser navigation in either final artifact check. Actual filter/download interactions, repeated-save behavior and Explore preference restoration remain outside this subagent's evidence. Parent HTTP browser checks are independent evidence and are not certified here.

## Persona Interview

The following is an in-character retrospective generated by the simulated-user test agent, not feedback from a human participant.

1. **Most useful:** I can inspect why sequential depth, total work and translation quality answer different questions, and keep the full files.
2. **Confusing:** The initial checkout-relative source notes were confusing after extraction. The repaired notes now show how to open the local reader and which supporting records require an online source link.
3. **Pacing:** The selected offline path needed no unresolved decision. This does not evaluate a real host research run's pace.
4. **Could not do:** I did not obtain a new researched paper history without host research tools; the empty-draft behavior stated that limit clearly.
5. **Walk-away result:** Three preserved map collections, a current portable skill and four newly generated comparison outputs.
6. **Other thoughts:** Keep proposed review states and the actual run's PARTIAL status visible. A passing CLI run should not become a scientific-certification claim.

## Expected vs Actual Outcome

The scoped offline outcome was met. The final delivered skill ran in isolation, comparison choices preserved their different meanings, all three complete maps and evidence states were retained, and the archive inventory/checksums matched. All defects found during this simulation were repaired and rechecked. No critical issue remains in the tested primary path.

## Structural Observations

- Documentation distinguishes host research from deterministic tooling.
- Actual research completion remains PARTIAL across landing, manifest, README and audit.
- Complete map outputs preserve the corpus independently of short reading routes.
- START-HERE avoids a broken self-download link.
- Source notes distinguish local readers from revision-bound online source records.

## Suggestions

No further change is required by this simulated offline test. Keep browser behavior, new research execution and participant evidence as separate validation streams.

## Evidence and Retained Files

- `/private/tmp/litdelta-delivery-user-test/baseline-report.md`
- `/private/tmp/litdelta-delivery-user-test/final-report-ff6033d.md` (historical pre-repair report)
- `/private/tmp/litdelta-delivery-user-test/final-d0f225d/artifact-inspection.json`
- `/private/tmp/litdelta-delivery-user-test/final-d0f225d/command-results.json`
- `/private/tmp/litdelta-delivery-user-test/final-d0f225d/offline/` (final extracted collection)
- `/private/tmp/litdelta-delivery-user-test/final-d0f225d/skill/` (final extracted skill)
- `/private/tmp/litdelta-delivery-user-test/final-d0f225d/generated/` (four new final demo outputs)
- `/private/tmp/litdelta-delivery-user-test/final-d0f225d/*.stdout` and `*.stderr`

Only this report and test artifacts under `/private/tmp/litdelta-delivery-user-test` were written by the subagent; no repository source was modified.
