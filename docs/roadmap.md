# Roadmap

Software readiness and scientific certification are separate milestones. No
calendar deadlines or reviewer assignments are implied. See [the audit](product-audit.md)
for the disposition of all 28 original tasks.

## v0.1 — A usable local research workflow

1. Correct the product baseline and define a distinct first-use experience.
2. Bind results and relationships to versioned evidence; reject misleading data.
3. Build deterministic HTML/SVG/JSON and a review report from one map.
4. Explore the map, inspect evidence, compare settings, and follow a reading route.
5. Recheck the bounded QSP/QSVT sample against primary sources.
6. Ship a standalone skill and a local CLI with a tested isolated install.
7. Validate failures, run Windows/Linux CI, and publish a usable release bundle.

Exit: a new user can download/open the demo and run the standalone skill without
accounts or network access. Scientific claims in the example remain proposed.

## v0.2 — Simple inputs and readable research histories

- A bounded Crossref/arXiv adapter with a retrieval log, pagination, timeouts,
  rate-limit handling, and explicit access failure. No paid provider by default.
- A topic or one paper is enough to start the skill; the host handles research
  and authoring. The local helper never substitutes a built-in example.
- A calm reading overview, source-linked turning points and a suggested route,
  with the explorer and full evidence available on demand.
- Identifier-based identity/version reconciliation; no title-only merging.
- Evidence gates for host-authored proposals, with engineering decision metrics
  separated from independent scientific accuracy.
- Source-version-aware update proposals; availability is not a historical snapshot.
- A second quantum map from a paper seed and the non-quantum NMT map using the
  same runtime, with source checks and observed workflow records.
- Equivalent English/Chinese READMEs and tools for consented paired reading studies.

Exit: verify software issues #8, #9, #11, #12 and #14–#17 with their stated commands
and actual browser runs. Source budgets, failures and evidence boundaries remain
observable. See [the workflow record](test-reports/skill-first-workflow.md).

## External validation — independent review and user study

- An independent review pilot and a small reading-task study with real participants.
- Independently labeled extraction examples with real reviewer references.
- Human judgments of transfer quality across topics, reporting failures.
- Community evidence corrections and review attestations with conflict handling.

Exit: publish actual review/evaluation artifacts. Do not mark these complete based
on unit tests, an agent's self-review, or the number of GitHub stars.

Issue #10 remains open: no external researchers or participant observations have
been supplied. The software and protocol can be completed without inventing them.
