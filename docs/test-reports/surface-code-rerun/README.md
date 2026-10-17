# Single-paper fresh-context research run

**PARTIAL — #12 remains open.** The corrected skill produced a much richer
research history, but one central full-text branch is unresolved. Passing
software checks does not close this research acceptance gap.

Open the [research notebook](report.html), then the
[actual interactive map](viewer/map.html). The short overview retains the full
corpus; it does not limit the research to nine recommended reading steps.

| Observation | Actual result |
| --- | --- |
| Sole research input | `https://arxiv.org/abs/2408.13687v1` |
| Host agent | `/root/surface_code_clean_run`, fresh conversation (`fork_turns: none`); exact model unavailable |
| Research cutoff | 2026-10-17, independently of the pinned 2024 paper version |
| Research interval | 2026-10-17 02:00:37–02:28:32 UTC; elapsed window, not measured active research effort |
| Corpus | 52 works, 54 results, 58 relationships, 55 evidence records |
| Source access | 49 works with relevant full-text passages checked by the agent; 3 abstract-only |
| Decisions | 58 candidates: 52 included, 6 excluded, none deferred |
| Coverage | 6 reference sets; 8 branches, of which 7 covered and 1 gap |
| Trace | 95 research-operation records and 109 total trace entries |
| Presentation | 5 overview moments, 9 route steps; complete corpus in embedded JSON |
| Recorded-evidence audit | Provenance, cutoff and source trail PASS; research completion PARTIAL |

The 95 records include searches, source opens/finds and metadata reads, including
49 arXiv metadata requests. They are not 95 independent search queries. All 112
results/relationships remain proposed; there was no external scholarly review.

## What changed from the withdrawn example

The [old four-work path](../../../examples/surface-code/map.json) is preserved as
an authored baseline. This run did not receive it, its authoring script, the
issue body or the parent coverage benchmark. It follows earlier work and later
developments through the actual research date, including decoder, leakage,
dynamic-code, platform and logical-operation threads. There was no paper quota.

[Coverage benchmark](coverage-benchmark.json) was created by the parent before
inspecting the outcome and was not supplied to the research agent.
[Coverage assessment](coverage-review.json) records parent passage checks and
their limits. This is implementation-side source review, not external expert
validation. The six-paper NMT baseline was also revalidated and rebuilt with the
same generic runtime; its sources were not freshly researched in this run.

## Remaining access gap

The 2025 all-microwave experiment,
[PRL 135, 260601](https://doi.org/10.1103/rqkg-dw31), is included with abstract
evidence only. Its methods, sample handling and decoder conditions were not
fully checked. Publisher security verification was completed by the user, after
which the official full-text area required authorization. The user has no
institutional access and requested an arXiv search instead.

Exact title, DOI, author and variant searches did not confirm a matching arXiv
or author manuscript. Crossref and Semantic Scholar records did not provide an
arXiv association. This does **not** prove that no public copy exists. The
OpenAlex lookup was unusable and is not negative evidence about access.

[2607.01473v1](https://arxiv.org/html/2607.01473v1) is a distinct later logical-gate
paper and explicitly cites the PRL. It was read and included separately; it
cannot replace the missing text. The gap is preserved in both the branch ledger
and stopping record. The run must not be relabeled complete to close #12.

## Execution exceptions and verification

The optional `start` helper was rejected twice by execution policy. It was not
retried through an alternative path or proxy. The agent directly authored a
minimal brief marked `manual-fallback-not-helper-generated`. Validation and
rendering subsequently succeeded as separate actions. This is a real skill
research run with an intake exception, not a flawless helper-to-output run.
See [original failures](execution-policy-events.json) and
[validation/build/browser observations](verification-record.json).

The agent exercised overview, source/version, relation and settings-comparison
controls with `mcp__cua_repl.js`. Screenshot capture returned
`Unable to capture screenshot`; no screenshot or pixel-level QA is claimed.
The parent separately [walked all nine route steps and checked the report's
candidate filter](parent-browser-observations.json); all 52 works remain in the
map. Its report screenshot attempt failed in the same way.

The packet audit JSON was PARTIAL, while the PowerShell tool reported exit 1.
The parent checked native Python subprocess return codes separately: **both the
unchanged packet and final canonical runtime return 3**, as documented.
The [original tool result](audit-packet-execution.json) remains unchanged;
[native exit-code diagnosis](audit-native-exitcodes.json) is supplementary.

The packaged skill was a pending-#14 snapshot before independent audit-code
fixes. The skill entrypoint used in research is retained verbatim. Both audits
give the same four outcomes; [canonical audit](audit.json) used committed
revision `5e8c8a599e217dd522445d1ee3182b1accb292c3`.

## Inspect and reproduce

- [Input map](map.json), [source index](source-index.md), [candidate/branch log](research-log.json)
- [Actual tool trace](tool-trace.jsonl), [original prompt](prompt.md), [used skill](SKILL.md)
- [Runner record](runner-record.json), [initial invocation](runner-invocation.txt), [interventions](runner-messages.json)
- [SHA-256 manifest](manifest.json), [agent's original report](agent-report.md)
- [Deliberately broken control results](negative-controls.json)

The seven manifest-bound artifacts are byte-identical publication copies. Raw
paper files/abstract dumps and scratch authoring scripts are not redistributed.
The manifest and traces are recorded evidence, not authenticated provider logs.

From a checkout with Python 3.11+:

```sh
python scripts/verify_research_run.py docs/test-reports/surface-code-rerun/manifest.json
# Expected native exit 3: first three checks PASS; completion PARTIAL.
python scripts/check_research_controls.py docs/test-reports/surface-code-rerun/manifest.json
# Expected exit 0: all three deliberate false-completion copies rejected.
python -m research_lineage build docs/test-reports/surface-code-rerun/map.json --out output/surface-code-expanded
python -m research_lineage build examples/nmt-attention/map.json --out output/nmt-regression
python scripts/render_research_report.py docs/test-reports/surface-code-rerun
```

The controls test relabeling the four-work baseline, missing forward records with
a false completion claim, and a hidden branch gap. Since the actual run is
already partial, the missing-forward copy also contradicts its retained gap;
isolated forward-only behavior is tested in `tests/test_research_scope.py`.
Control PASS means the false claims were rejected, not that the research is
complete. Rebuilding is deterministic; future live searches need not reproduce
the same results or access conditions.
