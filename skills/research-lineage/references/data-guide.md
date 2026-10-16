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

`settings` has four required keys: `input`, `assumptions`, `cost`, `error`. Values
are a supported textual statement or `null` (not extracted). A different input
model or resource measure is not evidence of an improvement.

`kind` for results: `foundation`, `framework`, `extension`, `challenge`, `tutorial`,
`result`. Evidence kinds: `abstract`, `full_text`, `metadata`. The latter two words
do not certify correctness; record what was actually accessed.

## Relationship direction

`source` is the predecessor/context result, `target` the later result. The sentence
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
