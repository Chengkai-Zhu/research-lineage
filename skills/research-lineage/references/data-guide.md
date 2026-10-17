# Map data guide

Use `lineage.py schema` for the complete machine-readable contract. The example
is available through `lineage.py demo`. All IDs are lowercase letters, digits,
and hyphens, and are unique within their collection; version IDs are globally unique.

| Collection | Required content |
| --- | --- |
| Root | `schema_version: "1.0"`, `id`, `title`, `question`, `scope`, `lanes`, `works`, `results`, `evidence`, `relations`, `reading_route` |
| Scope | `summary`, `cutoff` (YYYY-MM-DD), `coverage`, `search_strategy`, `exclusions` (list), `gaps` (nonempty list) |
| Lane | `id`, `label`, `color` (`teal`, `blue`, `amber`, `rose`, `violet`) |
| Work | `id`, `title`, `authors` (list), `first_published`, `versions` (nonempty list) |
| Version | `id`, `label`, `published`, `url` pointing to the version actually read |
| Result | `id`, `work_id`, `version_id`, `label`, `summary`, `lane`, `kind`, `settings`, `evidence` (IDs), `review_status`, `reviews` |
| Evidence | `id`, `work_id`, `version_id`, `url` (same as pinned version), `locator`, `kind`, `summary` (paraphrase), `checked` |
| Relationship | `id`, `source`, `target`, `type`, `summary`, `evidence` (IDs), `basis`, `comparability`, `review_status`, `reviews` |

## Optional reading overview

Add `narrative` when you have authored a concise, source-grounded account. It has
`overview` (at most 600 characters) and 1–5 `turning_points`. Each point has `title`
(80 characters), `summary` (360 characters), and `result_ids` (1–4 existing result
IDs). Prefer three clear changes in the problem, method or assumptions; every
point must be supported by the referenced results' evidence. An overview is
editorial synthesis, not a review certification. Unknown or duplicate IDs fail
validation. The narrative is preserved in JSON, HTML, SVG, reports and diffs.

Without this optional field, the opening page shows clearly labeled selections
from the reading route. It does not automatically invent turning points. All
existing version 1 maps remain valid with the current renderer.

`settings` has four required keys: `input`, `assumptions`, `cost`, `error`. Values
are a supported textual statement or `null` (not extracted). A different input
model or resource measure is not evidence of an improvement.

`kind` for results: `foundation`, `framework`, `extension`, `challenge`, `tutorial`,
`result`. Evidence kinds: `abstract`, `full_text`, `metadata`. The latter two words
do not certify correctness; record what was actually accessed.

## Relationship direction

`source` is the predecessor/context result, `target` the result making use of or
comparing with it. The sentence
is **target [type] source**. Thus for a tutorial surveying QSVT, source is QSVT,
target is the tutorial, and type is `surveys`. For a critique, source is the
criticized result and target the critique. A drawn arrow indicates map progression.

Types: `generalizes`, `uses_result`, `improves_bound`, `simplifies`, `surveys`,
`critiques`, `refutes_claim`, `addresses`, `independent_parallel`, `empirically_checks`,
`cites`. Only the `uses_result` subgraph must be acyclic.

`basis` is `author_explicit`, `editorial_inference`, or `citation_only`. An
author-explicit edge needs evidence from the target's source version. Citation-only
evidence cannot establish a semantic edge. `comparability` is `not_assessed`,
`comparable`, or `not_comparable`. An `improves_bound` edge requires fully stated
settings and a supported comparability assessment.

## Review and scope

Default `review_status` is `proposed`, with `reviews: []`. `reviewed` requires
full-text evidence from the result's pinned work and version, plus a real external
reference `{ "name": "Reviewer name",
"url": "https://..." }`. Critiques, refutations, and bound improvements require
two distinct reviewers and links. A reviewed relationship requires full-text
evidence from its target result's pinned work and version. An unrelated paper or
another version cannot supply this evidence, even when abstract evidence for the
correct version is also present. The validator cannot authenticate identities or
independence; the viewer calls these **recorded reviews**, never verified experts.

All version dates must be between first publication and the scope cutoff. Evidence
check dates may follow the cutoff, because sources can be inspected retrospectively.
The graph's horizontal axis uses first publication. A newer cited version does not
mean its content was present at the original publication date.

Limit: 250 results, 250 works, 8 lanes, 1,000 evidence entries and relationships,
5 MB JSON. These are bounded map limits, not claims about usability at the maximum.
Use several focused maps when a field is larger.

## LitDelta map format 1.1

Use `schema --format-version 1.1` or `demo --example comparisons` to inspect the
full contract and a worked input. Format 1.0 stays unchanged; never silently add
new fields to a legacy map. There is no automatic migration or invented assessment.

Format 1.1 adds the required `comparisons` collection (possibly empty). A relation
replaces legacy `comparability` with `comparison_id`, which is a comparison ID or
`null`. A comparison is directional: `left`/`right` match the relation's
`source`/`target`. Multiple records may address different questions for one pair;
select by ID. Same-paper results use separate labels and locators; their positions
do not establish chronological or logical dependence.

Each comparison records:

- `id`, `left`, `right`, `question`, `summary` (what changed), `regime` (when it
  applies), `tradeoffs`, and `rationale` (why the assessment is justified).
- `assessment`: `comparable`, `conditional`, `incomparable`, or `unknown`.
  `outcome`: `improvement`, `tradeoff`, `equal`, or `not_assessed`. Only comparable
  records may assert an outcome. Comparability alone never creates superiority.
- `improvement`: a specific directional statement for an improvement outcome,
  otherwise `null`.
- `conditions`: rows containing `dimension`, `left`, `right`, `reason`,
  `left_unit`, `right_unit`, `left_evidence`, and `right_evidence`. Values/units can
  be `null` when not extracted. Each supplied assessed value has evidence from
  that endpoint's exact work/version. Dimensions are unique within the record.
- `conversion`: `null`, or an explicit `summary`, `assumptions`, and evidence IDs.
  Different cost units need this context; equal unit strings alone do not prove a
  common metric, regime, or scientific conclusion.
- `evidence` (all condition/conversion references included), `basis`,
  `review_status`, and `reviews`. Citation-only support cannot justify an assessment.

An improvement record and a new `improves_bound` relation require explicit
`input`, `assumptions`, `cost`, and `error` condition rows, cost units, fully stated
result settings, and full-text evidence from both pinned versions. Keep an
irrelevant error dimension explicit as not applicable with its scope; do not
invent a numeric error bound. A reviewed comparison requires full text from both
versions and recorded distinct reviewer references (two for improvements, one
otherwise). Reviewer identity and independence are not authenticated.

Evidence may add `quote: {exact, prefix, suffix}` independently of `summary`.
An optional `anchor_check` contains `work_id`, `version_id`, `url`,
`selector_sha256`, `text_sha256`, `method: "nfc-whitespace-v1"`, and `outcome`
(`matched`, `missing`, `ambiguous`, `unchecked`). Use the `anchor` command to produce
this report; omit local text for unchecked. Text digests are required only when
checked. Edited selectors or source identities invalidate a stored report's
binding. The report is recorded, not reproduced without the local text, and cannot
establish semantic support or promote scholarly review. Preserve page/section
locators separately from the canonical version URL. Never use private source text
in public previews.

The host authors these records for the user; end users still provide a topic or
paper. Research completeness and cutoff/stopping guidance are owned by #14, and
fresh execution evidence by #12. The viewer's small set of overview/comparison
cards never limits the research corpus or establishes completed field coverage.

## Author and team colors

The explorer can color by research thread, recorded author labels, or recorded
teams. Multiple color marks indicate collaboration. The legend colors up to eight
frequent labels; the name selector can follow any other recorded label. Names are
used exactly as recorded, with no automatic person disambiguation or inference
that coauthors belong to one team.

Format 1.1 works may add `groups`, a list of `{id, label, version_id, evidence}`.
The ID identifies the same team across works, and must have a consistent label.
Each assignment needs evidence from that exact work/version; the viewer applies
it only to results using that version. Missing assignments remain uncolored in
team mode. An affiliation or team label is recorded metadata, not a scholarly
relationship or an authenticated membership assertion.

Current color preferences are preserved in downloaded HTML; SVG downloads include
the complete map and a color legend. These are view preferences, not new scientific
data. JSON retains the author/team metadata and all original evidence.
