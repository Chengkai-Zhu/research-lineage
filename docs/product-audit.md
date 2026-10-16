# Product audit of the supplied plans

Audited 2026-10-16. Inputs: the owner's shared idea conversation, `PRD.zh-CN.md`,
`MILESTONES.zh-CN.md`, and `research-lineage-demo.html`, supplied outside this clone.
These original files are preserved in the parent folder.

## Findings and corrections

| Severity | Finding | Correction |
| --- | --- | --- |
| High | The PRD describes source, a schema, tests, CI, and 28 machine-readable issues as already delivered, but only two plans and an HTML demo were present locally. | Treat supplied artifacts as planning/prototype evidence; implement and verify the actual repository. Never inherit prior test counts as current results. |
| High | All six milestones are chained before public release, including unavailable expert double review and a user study. | Separate software readiness from map certification. Ship a useful local tool with draft content; keep human studies explicitly open. |
| High | Source version binding is deferred until RL-015, after extraction and identity work. | Establish source-version references in the first contract, avoiding a breaking provenance retrofit. |
| High | Most issues describe ideals without executable acceptance or a negative case. | File fewer, outcome-based issues with actual commands, observable results, and failure cases. |
| Medium | Presentation and accessibility arrive after automation although first-use comprehension is central. | Move evidence inspection, setting comparison, route navigation, and accessible export into v0.1. |
| Medium | No installable, isolated skill is demonstrated. | Ship a ZIP containing the skill, CLI, schema, and sample; test it outside the repository. |
| Medium | Two developers, reviewers, 8–12 users, and a 10–12 week plan are assumed without commitments. | Use dependency gates and rough effort; do not assign fictional people or calendar deadlines. |
| Medium | Competitor claims could overstate novelty. | Cite existing genealogy/map skills and frame the differentiation as a hypothesis. |
| Medium | First public date and source-version availability can be confused in a timeline. | Label publication chronology explicitly and show the cited version separately. No as-of claim. |

## What was retained

Question-first scope; results instead of paper-only nodes; evidence for semantic
edges; unknown assumptions; narrowly scoped critiques; local output; reproducible
builds; review status; and bounded, honest examples are strong requirements.

## Disposition of the original 28 tasks

| Original tasks | Revised placement | Rationale |
| --- | --- | --- |
| RL-001 | v0.1 product baseline | Resolve scope and status claims before implementation. |
| RL-002, RL-015 | v0.1 data/evidence contract | Provenance must precede automation. |
| RL-003, RL-022, RL-023 | v0.1 reading experience | The map is the first value users see. |
| RL-004 | v0.1 verification and CI | Required for a public reusable tool. |
| RL-005, RL-006, RL-007 | v0.1 bounded sample; v0.3 gold set | Source-grounded sample now, full expert gold set later. |
| RL-008, RL-009, RL-019 | v0.3 independent review and evaluation | Requires real reviewers/users; cannot be completed by self-certification. |
| RL-010, RL-011, RL-012, RL-014 | v0.2 auditable discovery | Needs provider-specific error, identity, and access handling. |
| RL-013, RL-026 | v0.1 portable skill; later host field tests | Ship runnable tools now; do not invent two-host certification. |
| RL-016, RL-017, RL-018 | v0.1 manual settings; v0.2 assisted extraction | Deterministic comparison now; scientific judgments await independent evaluation. |
| RL-020, RL-021 | v0.1 explicit diff; v0.3 temporal updates | A map diff is useful without pretending to reconstruct source history. |
| RL-024 | v0.1 contribution example; v0.3 attestations | Small evidence corrections now, trust governance after real review. |
| RL-025 | v0.3 cross-domain transfer | Do not claim generalization from a single example. |
| RL-027, RL-028 | v0.1 public software release | Authorized by the owner; no fabricated research certification. |

## Distribution hypothesis

Lead the README with a real map preview, a downloadable offline demo, and a short
working command. Let a visitor understand the result before asking them to install.
Use honest topic tags and a concrete evidence-correction example. Future growth
work should measure completed maps, external corrections, and reuse in reading
groups; do not buy stars or send unsolicited promotional issues.
