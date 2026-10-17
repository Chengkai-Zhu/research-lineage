# Research Lineage: one input, a clear reading experience

## Product decision

The primary product is an agent skill. A researcher supplies a topic sentence or
one paper. The host agent resolves the scope, researches sources, writes original
annotations, and uses the bundled Python tools. The user receives an offline
reading experience. The CLI is supporting infrastructure, not a requirement to
learn JSON before asking a question.

The user selected this scope on 2026-10-17 and authorized implementation through
issues, PR, CI and merge. Real external review remains open in #10 because no
participants or review materials are available. Engineering fixtures do not
replace that work.

## Researcher and product perspectives

A researcher first needs orientation: what problem was being solved, which
changes mattered, what to read next, and which claims deserve checking. A dense
graph is useful later. A product should expose one obvious next action and let
the reader choose when to see the underlying detail.

The opening view therefore has a concise overview and a small set of source-linked
turning points. A reading action leads through a bounded route. A separate explore
view retains the full map, filters, comparisons and evidence. Proposed status and
scope remain visible in quiet text, while the detailed audit trail opens on demand.
The exported files always retain the complete input, regardless of the visible view.

## Lightweight landscape check

- [ResearchRabbit](https://www.researchrabbit.ai/help/guide) starts discovery with
  seed articles and lets users follow references and citing work.
- [Connected Papers](https://www.connectedpapers.com/) starts from a paper and
  exposes similar, prior and derivative work.
- [Litmaps](https://docs.litmaps.com/en/articles/9092911-search-for-articles-with-litmaps)
  accepts a research topic or known paper.

These make simple entry a baseline expectation. Research Lineage's intended
distinction is a readable account of result/assumption changes with inspectable
evidence, delivered as a portable file. This is a product choice, not a verified
claim that no other product offers it.

Reuse the host's research and PDF tools rather than build a hosted agent or PDF
parser. Use Python standard-library HTTP/XML/JSON for bounded metadata retrieval.
Provider contracts: [Crossref](https://github.com/CrossRef/rest-api-doc) and
[arXiv](https://info.arxiv.org/help/api/user-manual.html). No new runtime dependency,
account or paid service is required by the local core.

## Selected work and rough effort

These are order-of-magnitude engineering estimates, not a delivery promise.

| Selected outcome | Rough effort | Why |
| --- | --- | --- |
| Topic/paper intake and skill instructions | 1–2 hours | Remove setup burden |
| Progressive reading and visual hierarchy | 2–4 hours | Make the first screen understandable |
| Discovery, identity, proposal/evaluation tools | 3–5 hours | Complete bounded software backlog |
| Real second quantum example and transfer checks | 1–3 hours | Avoid a demo-only design |
| Equivalent English/Chinese README | 0.5–1 hour | Make entry accessible |
| Browser checks, fresh review and CI fixes | 1–2 hours | Verify the actual delivery |

External scholarly review and a participant study require recruitment and consent;
their duration cannot be estimated from software work. Keep #10 open.

## Modules and choices

- Intake emits an empty draft and a research brief. Host reasoning resolves topic
  ambiguity and paper titles. A template-only fake research answer is excluded.
- Discovery is an explicit network command with request/candidate bounds, logs,
  provider failures and access levels. Automatic background retrieval is excluded.
- Identity groups only compatible persistent identifiers. Title similarity is
  useful for a human search, never sufficient for automatic merging.
- Extraction accepts host-authored candidates and gates evidence sufficiency.
  It cannot establish semantic truth; independent labels remain future evidence.
- Reading uses an optional, source-linked narrative in the existing map format.
  Legacy maps fall back to a clearly labeled selection from their reading route,
  with no invented historical turning points. A framework rewrite or hosted web
  app would add deployment cost without improving the portable deliverable.
- Temporal proposals report exact source-version availability and conflicts.
  First-publication filtering is not a reconstruction of historical knowledge.
- Evaluation reports provenance and unavailable measurements explicitly. The
  paired study template remains empty until real consenting observations exist.

## Acceptance

Behavioral tests cover failure paths, not just file presence. Build and inspect
QSP/QSVT, NMT and the new paper-seed map. Exercise the first view, route, explorer,
source versions, empty-filter recovery, narrow layout, deep links and filtered
exports. Install the skill archive outside the checkout. Merge only after fresh
review and the Windows/Linux × Python 3.11/3.14 CI matrix pass.
