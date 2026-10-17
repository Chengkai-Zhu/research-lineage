# LitDelta — Product Design

Implementation issue: [#20 — Deliver LitDelta's result-comparison reading
experience](https://github.com/Chengkai-Zhu/research-lineage/issues/20).

## Parallel implementation agreement

The owner requested parallel development on 2026-10-17. Issue #14 owns the research
contract/intake, source coverage, cutoff, and partial/completed search-plan states.
Issue #12 owns the fresh packaged-skill execution and research evidence checker.
This issue owns comparison/anchor data and guidance, reader views, exports,
branding, and preview delivery in its isolated branch. Core implementation can
start now. End-to-end research acceptance must consume the corrected contract and
actual fresh-run evidence when available; a curated example cannot substitute.

Display card counts never cap the research corpus or silently change the cutoff.
Report software, research integration, browser, and publication outcomes separately.
Reconcile shared data-guide/README/CI edits before merge; do not close #20 while
its required integration or public-preview acceptance remains pending.

The owner additionally requested author/team colors while implementation was in
progress. The explorer keeps thread colors as default and adds recorded-name and
explicit-team modes, collaboration marks, a named legend, and a focus selector.
Team assignments require evidence for their exact work/version. Color labels are
metadata for following work, not proof of influence or inferred group membership.
HTML/SVG exports retain the chosen view while preserving the complete map data.

## Decision and need

On 2026-10-17 the owner selected the name **LitDelta** and features A, B, C, E,
and F below, accepting a rough estimate of **6–10 engineering days plus 1–3
source-reading and annotation days**. Estimates assume agent-assisted development
and reuse of the existing runtime; they are not a delivery commitment. Independent
scholarly review and participant recruitment are separate work tracked in #10.

LitDelta helps graduate researchers and research groups understand what a result
changes, under which conditions it applies, and where its supporting evidence can
be inspected. A topic or paper remains enough to start. The host agent researches
and authors the explanation; the local toolkit preserves and checks its structure.
The reader receives a portable reading experience and can investigate the details
without learning the data format.

The next deliverable is one complete result-comparison reading experience. It
should answer three questions: **What changed? When does that matter? Where can I
check it?** A reader should also be able to recognize an unresolved comparison
instead of mistaking missing evidence for a result that is worse or disproved.

This document specifies future implementation. The approved scope is recorded
above; the technical choices below are engineering recommendations within it.
Creating its implementation issue does not mean the features are already built.

## Current baseline and observed gap

Baseline: `e3f815f`, after merged PR #18. The repository already has topic/paper
intake, a reading overview, turning points, reading routes, bounded discovery,
identifier reconciliation, candidate evidence gates, update proposals, study
tools, and standalone HTML/SVG/JSON exports. Rebuilding these is unnecessary.
The baseline passed 128 local tests and Ruff on 2026-10-17.

Concrete observations:

- `src/research_lineage/core.py:compare` reports four text fields as identical,
  different, or unknown. It correctly avoids inferring scientific comparability,
  but gives the reader no persistent, source-grounded explanation of the change.
- `src/research_lineage/extraction.py:assess` asks an improvement candidate for
  cost units and full text. The canonical map cannot retain that entire comparison
  record; its final gate only requires comparable, nonempty settings.
- The three worked maps have 8/8, 6/6, and 4/4 works/results respectively. None
  demonstrates multiple results from one paper or an `improves_bound` relation.
  These counts establish a demonstration gap, not an error in those annotations.
- Evidence records hold a version, locator, and annotation. Readers cannot see a
  separately labeled source excerpt beside the author's interpretation.

After installing the package, reproduce the current comparison with:

```sh
python -m pip install -e ".[dev]"
python -m research_lineage compare examples/nmt-attention/map.json r-bahdanau r-transformer
```

The output includes `different`, `unknown`, and `same_reported` fields and the
verdict that text matching does not establish comparability. The requested change
is an inspectable explanation where one has been authored, while retaining this
honest fallback when it has not.

## Prior art and landscape

This is a focused refresh of the earlier repository assessment, checked on
2026-10-17. Public descriptions are evidence of advertised capabilities, not a
head-to-head benchmark.

| Prior art | Existing capability | Implication for LitDelta |
| --- | --- | --- |
| [research-genealogy](https://github.com/unumbrela/research-genealogy) | Agent workflow for research genealogy with retrieved metadata and citations | A topic-to-lineage skill is already a baseline |
| [academic-research-graph](https://github.com/watericetangcw/academic-research-graph) | Interactive research maps, controversy, and incremental exploration | An interactive graph alone is insufficient differentiation |
| [PRIOR](https://github.com/Agents4Academia-AI/prior) | Contributions, claims, typed relations, provenance, and a standalone atlas | Result-level graphs and portable outputs are also prior art |
| [ORKG comparisons](https://academy.orkg.org/courses/comparison-course.html) | Structured comparison of research contributions and properties | Comparison tables alone are insufficient differentiation |
| [ResearchLineage](https://github.com/gautamrajur/ResearchLineage) | Research evolution under the existing project name | A distinct brand reduces naming confusion |

The proposed advantage is the complete reading task: a concise account of the
advance, explicit applicability and tradeoffs, and evidence for that account in
the same view. This is a product hypothesis, not a claim of a novel algorithm or
an exclusive feature. It will be stronger if real readers can answer comparison
questions more reliably than with a bibliography or ordinary agent report.

Reuse rather than build:

- Keep the current Python validator, candidate gates, renderer, map exports,
  host research workflow, CI, and study protocol.
- Borrow the `exact`, `prefix`, and `suffix` ideas from the
  [W3C TextQuoteSelector](https://www.w3.org/TR/annotation-model/#text-quote-selector)
  for optional text anchors. This is a small local representation, not a claim of
  complete Web Annotation or JSON-LD conformance.
- Reuse the host's document-reading tools. A new PDF/OCR stack would add cost and
  runtime dependencies without solving scientific interpretation.
- Use Python standard-library JSON, hashing, and text operations for deterministic
  local checks. String equality or a text diff never establishes entailment.
- Publish the generated static example with
  [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
  A separate hosted application is unnecessary for trying the product.

## Selected features and effort

The owner selected A+B+C+E+F. The item estimates overlap in integration and testing;
the integrated estimate is 6–10 engineering days plus 1–3 reading/annotation days.

| Feature | User outcome | Rough effort | Decision |
| --- | --- | --- | --- |
| A. Conditions and comparability | Understand the improvement, tradeoff, applicable regime, and unresolved questions | 2–4 engineering days | Selected |
| B. Question-led comparison view | Read the explanation and open the supporting conditions and evidence | 1–2 engineering days | Selected |
| C. Multi-result worked example | Distinguish results within one paper and recognize a comparison that does not hold | 1–2 engineering days + 1–3 reading days | Selected |
| D. Incremental authoring assistant | Edit one result or relation without rewriting a whole map | 1–2 engineering days | Deferred to a subsequent authoring iteration; measure friction first |
| E. Source excerpts | Separate source words, source location, and editorial interpretation | 1–2 engineering days | Selected |
| F. Brand and browser entry | Recognize LitDelta and try a complete example without installation | 0.5–1.5 engineering days | Selected |

Deferred: semantic formula/unit solvers, automatic proof or superiority judgments,
PDF highlighting/OCR, hosted accounts, collaborative editing, and background
monitoring. These would expand the research and operational burden before the
reading experience is validated. No delivery milestone is committed for them.
Independent evaluation remains #10, not a new duplicate issue or a software gate
that can be satisfied with synthetic participants.

## Reader journey

1. Open the example or ask the installed skill about a topic/paper. See a short
   overview and a suggested reading route using the existing first screen.
2. Open a development and read **What changed**, **When it applies**, and **What
   it costs or leaves unresolved**. Show a concise applicability sentence before
   any technical status vocabulary.
3. Expand **Why this comparison holds** to inspect only the relevant dimensions,
   both result versions, and the reason for the comparison assessment.
4. Expand **Check the source** to see a short excerpt or a precise locator,
   separate from the annotation. A link leads to the pinned source version.
5. Follow the result or its precursor in the reading route, or share a comparison
   deep link. Download the full offline map with its evidence and uncertainty.

Unknown information remains visibly unknown. A missing source excerpt does not
hide an otherwise useful locator. No unsupported comparison receives an invented
explanation. The first screen must remain useful without opening review metadata.
The existing skill must produce the new records from an ordinary topic/paper
request; deferring D must not make end users fill in JSON forms.

## Modules and interfaces

| Module | Input → output | Dependencies |
| --- | --- | --- |
| Comparison contract | Two result IDs, version-bound evidence, and an authored explanation → validated, persistent comparison record and diagnostics | Canonical contract, candidate assessment, map loading |
| Source anchors | Evidence record and optionally supplied local text → displayed excerpt and a recorded local anchor-check outcome | Exact work/version identity; standard-library text/hash operations |
| Reading view | Validated map and optional comparison selection → explanatory cards, detailed comparison, evidence, and deep links | Existing renderer, viewer, routes, and export machinery |
| Worked example and acceptance | Pinned primary sources and engineering control cases → a documented real example and reproducible acceptance report | Contract, anchors, reading view; existing evaluation tools |
| Brand and delivery | Existing package and generated example → LitDelta-facing docs/viewer, additive command alias, static preview, offline download | Existing packaging and CI; static hosting |

## Technical choices and alternatives

### Comparison contract

**Recommend an explicit map format 1.1 alongside the unchanged 1.0 reader.**
Version 1.1 owns persistent comparison records, with one authoritative assessment
per record. Canonical schema definitions and runtime validation stay together in
`src/research_lineage/contract.py`; do not maintain an independent handwritten
schema. Publish the new version's schema separately and dispatch by format version.
Reuse the same substantive gate from candidate assessment and final map
validation so a direct map import cannot bypass required comparison evidence.

Alternatives: silently extending 1.0 is smaller but breaks the meaning of the
existing closed schema; a separate sidecar avoids a format change but risks
losing the explanation during export or review. Explicit versioning makes these
costs and compatibility boundaries visible.

A comparison record has a stable ID, ordered left/right result IDs, an authored
summary of the change, a question/metric, an applicable regime, tradeoffs or gaps,
relevant condition rows, evidence IDs, basis, and the existing review status and
review references. Each row identifies the dimension, reported values (including
unknown), each side's evidence, and the reason that the difference matters.
One pair may have several comparisons for different questions, metrics, or regimes.
Resolve by comparison ID; when several match, expose the choices rather than pick
the first. Extend `compare` with an optional `--comparison ID` selector. A reversed
pair must not silently reuse or invert a directional improvement statement.
Dimensions may cover input/access model, assumptions, resource metric and unit,
error criterion, dataset/protocol, and domain-specific conditions. Do not require
irrelevant empirical dimensions for theoretical results, or vice versa.

Assessment is one of `comparable`, `conditional`, `incomparable`, or `unknown`:

- `comparable`: an explicit common question, regime, and metric are documented;
  this records the author's assessment, not a machine-certified judgment.
- `conditional`: comparison depends on a stated extra restriction or conversion
  that has not yet been fully established in the comparison record.
- `incomparable`: a specific mismatch blocks the requested comparison.
- `unknown`: the assessment is missing or the available evidence is insufficient.

New relations refer to a comparison by ID where needed. An `improves_bound`
relation requires a `comparable` record for its exact ordered endpoints, explicit
settings and resource units, and full-text evidence for both versions. Different
units require an explicit conversion with its assumptions and evidence; identical
unit strings alone do not establish comparable metrics or regimes. Conditional,
unknown, or incomparable records cannot justify an unconditional improvement.
Comparability itself never creates an improvement: the relation also needs a
specific, source-supported directional improvement statement for that regime.
Comparable outcomes may be equal or involve tradeoffs. Other relationship types
retain their own evidence requirements.

Version 1.1 must not carry an independent, potentially conflicting legacy
`relation.comparability` judgment. Preserve the old field only in 1.0 input/output.
Legacy maps remain readable and export without silent migration; legacy
comparability claims remain visible as legacy author annotations. Do not promote
them into new comparison assessments. The normal new-view fallback is unknown.
Do not change old result IDs, source versions, or reviewer identities on load.

An explicit migration, if supplied, writes a separate output and preserves legacy
provenance without inventing missing reasons. No automatic conversion is needed
for the deliverable. Older binaries are not promised to read 1.1; new binaries
must read both versions and report unsupported formats clearly.

### Source anchors

**Recommend optional short excerpts with quote selectors and explicit local
checks.** Keep the existing locator, version, source URL, and original annotation.
Add a source excerpt separately from the interpretation, and optional exact text,
prefix/suffix, local-text digest, extraction method, and check metadata.
Keep page/section selectors separate from the canonical evidence URL so they do
not invalidate the existing exact source-version URL binding.

Alternatives: locator-only remains the smallest fallback but leaves more search
work to readers; a full PDF highlighter offers richer navigation but brings a new
parsing and rendering surface. Host-provided text plus optional selectors fits
the offline core and lets either alternative be added later.

When explicitly given local text, match against that text and record `matched`,
`missing`, or `ambiguous`; without text, record `unchecked`. Specify the matching
normalization and hash the exact text artifact actually checked. Bind the report
to the work/version, selector, and text digest. Rechecking changed text must not
reuse an earlier successful match. A stored success is only a recorded check
unless it is reproduced; even a reproduced match says nothing by itself about
document authenticity or whether the excerpt supports the scientific claim.

Do not fetch papers while rendering, load private documents into public previews,
or redistribute full texts. Use bounded excerpts with recorded source/rights
information where available. All imported content is rendered as text.

### Reading view

**Recommend adding explanation cards to the current vanilla HTML/CSS/JS viewer.**
Keep the overview, route, and explorer; add relation/comparison deep links and a
details panel that places prose before structured dimensions. Reuse the same
comparison data in CLI output, HTML, SVG metadata, JSON, and the review report.
Include comparison and anchor edits in map diffs and temporal update proposals;
a changed premise must not disappear merely because the result IDs stayed fixed.
Comparison evidence newer than a requested cutoff must produce an explicit
unavailable/conflict outcome in the proposal. This is source availability, not
proof of what researchers knew at that time.

Alternatives: a standalone comparison dashboard would fragment the reading route;
a React application would increase deployment and dependency cost without a
demonstrated need. Neither is required for the selected reading task.

Multiple results from one paper must remain distinguishable by result label and
locator. Label a pair by its results; publication order alone does not establish
logical dependence, especially within one source version. Do not collapse their
edges into a paper-level judgment. Changing view
filters may change visible nodes, never the full exported map. Narrow screens
and keyboard navigation must expose the explanation and source controls.

### Worked example and acceptance

**Recommend a bounded primary-source case selected after checking source access.**
Start by checking whether the existing NMT sources can support the required result
distinctions; select another small case if they cannot. Reuse a second existing
map for a lightweight transfer check with the same runtime. The flagship must
contain a paper with at least two genuinely distinct results, one supported
comparison, and one source-grounded reason not to make a requested comparison.
It must not manufacture an `improves_bound` edge merely to exercise the UI.

Alternatives: synthetic-only examples give crisp engineering checks but cannot
demonstrate research usefulness; a large new field atlas raises annotation effort
before the experience has been tested. Use small, clearly labeled engineering
fixtures for gate failures alongside the real example.

Preserve proposed status until genuine independent review exists. Record exact
source versions, access limitations, annotation choices, and actual authoring
time. The transfer check must start from a normal topic/paper prompt and record
manual repair, rather than claim that a hand-polished fixture proves usability.

### Brand and delivery

**Recommend a staged, compatible brand transition.** Use **LitDelta** with the
tagline **See how research moves forward.** Explain the promise with:

> Explore what each result changes, under which conditions, and where the
> evidence comes from.

Update the English and Chinese product entry pages, viewer, and demo identity.
Add `litdelta` as an installed console alias of the same CLI. Keep
`research-lineage`, `python -m research_lineage`, the existing distribution,
canonical runtime, skill directory, ZIP layout, and historical schema IDs working
through this iteration. Document the brand/installation-name distinction plainly.

Alternatives: immediately renaming every package and repository makes installation
and link migration a separate release project; keeping the old brand permanently
retains the naming collision. The staged approach gives the product a distinct
identity with an explicit compatibility window.

Generate a public preview from the same committed example and renderer that make
the offline export. GitHub Pages can serve it without a backend or account for
readers. Record the actual reachable URL only after publication; an unconfigured
workflow or an intended URL is not acceptance. No repository/PyPI namespace rename
is part of this issue. Those changes need namespace checks and a release plan.

Name screening on 2026-10-17 covered exact public-web searches and GitHub repository
names. No same-named research product was found for LitDelta; this does not establish
global uniqueness, trademark clearance, or domain availability. PremiseTrail and
ClaimStrata were considered; LitDelta was chosen by the owner for its shorter,
broader emphasis on changes in the literature.

## Quality and compatibility requirements

- Keep Python 3.11+ and zero runtime dependencies. Retain Linux/Windows CI.
- Existing 1.0 maps, source versions, review status, exclusions, and original
  annotations survive loading and full export; new 1.1 data survives every export.
- Citation-only support cannot become a semantic edge. Source matching, structural
  validation, editorial assessment, and independent review remain separate states.
- Rendering is offline and treats imported strings as data, never executable HTML.
  Keep existing size/count limits and safe-URL checks, including new fields.
- Preserve inputs and existing output files unless the user explicitly requests
  replacement. Use the existing overwrite protections for new outputs.
- Source citations and comparison controls remain reachable with a keyboard and
  on narrow screens. Review metadata must not crowd out the explanation.
- Do not claim a speed or accuracy improvement without real observations. Study
  thresholds will be set after baseline data exists, not invented in this design.

## Verification and completion

Implementation must add this reproducible, offline acceptance entry point:

```sh
python scripts/verify_litdelta.py --out output/litdelta-acceptance
```

This command is **specified here, not implemented yet**. It must exit zero only
when its known-input checks pass, write `report.json` and `report.html`, and build
the real example into `flagship/map.html` with the complete export set. A fresh
output directory is required. Each report row names the input, expected behavior,
observed behavior, and evidence path; the report distinguishes software results
from manual browser checks and unavailable human-study outcomes.

The compound check covers one deliverable: the comparison reading experience.
Use existing map/candidate fixtures where suitable, plus small labeled engineering
controls. It must check the following behaviors rather than file existence:

1. A complete authored comparison retains its endpoints, assessment, explanation,
   condition rows, both sides' version-bound evidence, and review status in the
   CLI result and full exports. Two distinct results of one work remain distinct.
2. Removing the comparison record makes a normal pair unknown and makes a new
   `improves_bound` relation invalid. Copying identical setting text never upgrades
   an unknown pair to comparable. A conflicting assessment or wrong endpoint is
   rejected. Unknown and incomparable are observably different outcomes.
   Several records for one pair require explicit selection; reversing a pair
   cannot invert an improvement. A comparable-but-equal control is not ranked.
3. Different units without a documented conversion, citation-only semantic edges,
   and evidence from the wrong source version cannot pass the improvement gate.
   Check both candidate intake and direct map validation to prevent bypasses.
4. Exact, missing, ambiguous, unchecked, and changed-text anchor cases produce
   the expected outcomes. A text-match result never changes scholarly review
   status. Imported script-like text stays inert in the browser.
5. Unmodified legacy fixtures still load/build/export, and filtered exports retain
   all original/new evidence, comparisons, uncertainty, and review information.
   Installed `litdelta` and `research-lineage` invoke the same functionality.
   Editing only a comparison appears in the diff; evidence beyond a cutoff is
   unavailable/conflicting in an update proposal rather than silently included.

For manual acceptance, open `flagship/map.html` and the eventual public preview:

- Explain the research question and one advance without opening review metadata.
- For a supported pair and a mismatched pair, answer whether the requested
  improvement follows, identify the decisive condition, and open its source.
- Choose the relevant result among two from the same paper and follow its
  precursor without confusing the two results.
- Open a saved comparison deep link, use the keyboard/narrow layout, then download
  and reopen the offline file. The same explanation and evidence must be present.

Record expected answers and pinned source locations in the example's source note.
Agent/browser walkthroughs are engineering observations, not participant results.
Reuse `docs/evaluation-protocol.md` for later consented comparisons against a
bibliography/source baseline and an ordinary agent report. Record correctness,
source-location success, mistakes, elapsed time, and authoring effort. Extend the
study design explicitly for additional conditions rather than overloading the
existing two-condition format. Keep #10 open until genuine evidence is available.

Run the repository tests, Ruff, portable packaging checks, and browser walkthrough
when implementing. Publish a report stating what was tested, what failed, and what
remains unmeasured. This design-only change adds no runtime behavior or benchmark.
