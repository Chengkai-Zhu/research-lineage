# Research Lineage — Product Design

Decision date: 2026-10-16. First software release: v0.1.0.

## Need

Researchers entering a specific question need to understand how results evolved,
which assumptions changed, and where to check each connection. A lab needs a map
it can maintain, use in a reading group, and share without a hosted account. The
first release delivers an agent skill and deterministic local tools, with QSP/QSVT
as a bounded worked example. It does not certify the example as expert reviewed.

Success means a new user can open the example, follow a reading route, inspect the
source of a relationship, compare assumptions, and build a map of their own.
GitHub stars measure distribution, not evidence quality or a promised outcome.

## Prior art and landscape

Survey checked on 2026-10-16 using primary sources:

| Product | Existing capability | Product implication |
| --- | --- | --- |
| [Connected Papers](https://www.connectedpapers.com/about) | Similarity maps, prior and derivative works | A connected paper graph is table stakes. |
| [ResearchRabbit](https://www.researchrabbit.ai/) | Seed-based exploration and literature recommendations | Do not rebuild a discovery platform for v0.1. |
| [Litmaps](https://www.litmaps.com/) | Visualize, share, discover, monitor | Visual polish alone is not a defensible novelty claim. |
| [research-genealogy](https://github.com/unumbrela/research-genealogy) | Agent skill with metadata, lineage narrative, citation checks | A research-history skill already exists; acknowledge it. |
| [Academic Research Graph](https://github.com/watericetangcw/academic-research-graph) | Skill producing research maps | Differentiate through explicit result settings and inspectable evidence. |

Proposed advantage is the combination of **result-level relationships, setting
comparisons, visible evidence limits, and a portable interactive reading experience**.
This is a product hypothesis, not a claim of global novelty or validated superiority.

Reuse Python's JSON, HTML, zip, and command-line libraries; use browser SVG and DOM
APIs for portable rendering. Use pytest, Ruff, JSON Schema, and GitHub Actions for
development checks. No graph database is justified by the first map.

[Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) exposes
public metadata without registration. [OpenAlex](https://help.openalex.org/api/authentication/)
has an authentication policy that must be checked before implementing an adapter.
Host search tools remain the v0.1 discovery mechanism; the skill supplies evidence
discipline and deterministic output tools, not search credentials.

## Feature selection

The owner explicitly selected the recommended first-release scope and requested
direct completion. The scope below was presented with rough engineering effort;
the existing PRD's core loop is retained.
Estimates are planning ranges, not measured delivery times.

| Feature | Rough effort | Decision and rationale |
| --- | --- | --- |
| Skill and local CLI | 0.5–1 day | In: the requested entrypoint and repeatable workflow. |
| Result/evidence contract and comparison | 1–2 days | In: meaningful difference from paper-only maps. |
| Interactive map, reading route, offline HTML/JSON/SVG | 1–2 days | In: immediate utility and shareability. |
| Grounded QSP/QSVT example, docs, tests, release | 1–2 days | In: first-run experience and usable distribution. |
| Deterministic review report and map diff | 0.5 day | In: low cost using structured data; preserves the original maintenance loop. |
| Automated search adapter | 1–3 days | v0.2: separate upstream failure handling from local tool quality. |
| Full-text extraction, scientific relation scoring | Weeks | v0.2+: needs source access and an independently reviewed evaluation set. |
| Expert-certified Atlas and user study | Weeks + reviewer availability | v0.3: real external reviews cannot be manufactured by implementation. |
| Temporal reconstruction and continuous monitoring | 1–2 weeks | v0.3: chronological filtering is not a historical snapshot. |
| SaaS, accounts, proprietary database, autonomous publishing | Unpriced | Out: unnecessary for the initial user need. |

## Modules and approaches

| Module and interface | Chosen approach | Alternatives and trade-offs |
| --- | --- | --- |
| Data: JSON in, diagnostics out | Small versioned JSON contract with standard-library validation and published JSON Schema | Pydantic adds installation dependencies; a graph database adds operational burden. |
| Renderer: validated JSON to bundle | Static HTML with embedded CSS/JS/data, deterministic SVG layout | React adds a build toolchain; D3/force layout can improve large maps but complicates stability and offline packaging. |
| Comparison: two result IDs to a table | Field-by-field setting comparison; unknown stays unknown | Numeric automatic ranking is misleading without normalized units; LLM comparison belongs in reviewed content. |
| Maintenance: old/new maps to JSON diff | Stable ID comparison including changed fields and deletions | Text diff is noisy; semantic model scoring adds nondeterminism. |
| Workflow: question to map/review/bundle | Host-neutral skill, documented schema, bundled CLI | MCP requires a running service; a hosted agent requires credentials and infrastructure. |
| Content: worked example | Primary-source paraphrases and version-specific anchors, proposed review state | Synthetic maps do not prove source workflow; expert certification requires real people. |

Dependencies: skill → data authoring → validation → comparison/report/render.
The renderer never retrieves sources. Packaging copies the canonical runtime into
the distributable skill; generated copies are not maintained as a second source.

## Quality requirements

- Same input produces byte-identical HTML/SVG/report; no wall-clock timestamps in rendering.
- No external requests, fonts, scripts, or accounts to view the exported map.
- Every semantic edge has evidence, a scope, and an explicit basis. Citation alone
  is not proof of inheritance. Unknown settings do not imply comparability.
- Validate IDs, references, dates, URL schemes, source versions, and dependency cycles.
- Raw source content is text, never trusted HTML. Refuse unsafe links and oversized input.
- Keyboard controls, a text alternative, readable narrow screens, and reduced-motion support.
- Exports keep the cutoff, known omissions, and review disclaimer.
- Unit/integration tests cover real failures; browser checks exercise the complete user path.

## Release boundary

v0.1.0 is a usable software release. The sample remains an explicitly labeled,
bounded research draft. No expert endorsement, extraction accuracy, complete
history, host certification, or star target is claimed. See the product audit and
roadmap for the original 28-item disposition and future acceptance criteria.
