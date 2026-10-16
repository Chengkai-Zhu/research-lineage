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

## v0.2 — Auditable discovery and assisted authoring

- A bounded Crossref/arXiv adapter with a retrieval log, pagination, timeouts,
  rate-limit handling, and explicit access failure. No paid provider by default.
- Identifier-based identity/version reconciliation and safe optional document
  retrieval; no merging by title similarity alone.
- Assisted extraction evaluated on independently labeled examples. Report errors
  and abstention separately for each relation type, including incomparable settings.

Exit: a retrieval failure cannot silently become a fabricated paper or relation.
Source budgets and actual coverage must remain observable.

## v0.3 — Reviewed maps and accountable updates

- An independent review pilot and a small reading-task study with real participants.
- A source-version-aware update proposal and historical snapshot policy.
- Transfer to a second quantum topic and one non-quantum topic, reporting failures.
- Community evidence corrections and review attestations with conflict handling.

Exit: publish actual review/evaluation artifacts. Do not mark these complete based
on unit tests, an agent's self-review, or the number of GitHub stars.
