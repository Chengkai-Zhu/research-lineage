# Research tools behind the skill

Most users supply a topic or paper to the skill and receive `map.html`. These
commands are for the host agent and researchers who want to inspect the workflow.
All outputs are proposals or observations, not scientific certification.

```sh
research-lineage start "quantum signal processing" --out output/topic
research-lineage start "https://arxiv.org/abs/1706.03762v1" --out output/paper
research-lineage start "A paper title" --kind paper --out output/title
```

`start` writes `map.json` and `research-brief.json`, performs no network request,
and leaves works/results empty. It preserves pinned identifiers, infers Chinese
from Chinese input, and keeps the default research cutoff at the run date. It has
no default paper quota; research coverage and the concise presentation have
separate plans. Local PDFs are handled by the host locally; they are never uploaded by
this helper. A bare title needs identity resolution before any paper claim is made.

## Recorded research coverage

```sh
research-lineage research-schema --out research-schemas.json
research-lineage audit-research run-manifest.json
python scripts/verify_research_run.py run-manifest.json
```

The portable skill includes the first two commands. See the
[research record contract](../skills/research-lineage/references/research-record.md)
for actual tool traces, source-grounded branches and candidate decisions. The
audit checks provenance records, cutoff consistency, cross-file source trails
and search-plan completion. Exit 0 is PASS, 3 is PARTIAL, and 2 is FAIL. It does
not authenticate the recorded tool calls or certify scholarly completeness.
Paper count is reported separately from route length and overview density.

## Discovery and identity

```sh
research-lineage discover "quantum signal processing" --provider crossref --limit 12 --max-requests 3 --out discovery.json
research-lineage discover "all:quantum AND all:signal" --provider arxiv --limit 12 --out arxiv.json
research-lineage reconcile identities.json --out identity-proposal.json
```

Discovery is an explicit online action. Only Crossref/arXiv endpoints are fetched.
The log retains queries, times, counts, rejected candidates, truncation and
failures. HTTP errors/timeouts stop the run and preserve earlier candidates;
exit 3 means a provider failure was recorded. Reaching a configured cap is an
expected bounded result. Metadata/abstract access does not imply full-text access.

Identity input is a list such as
`[{"id":"paper-v1","arxiv":"1706.03762v1"},{"id":"paper-v2","arxiv":"1706.03762v2"}]`.
Optional `doi` and `title` fields are retained. Identical titles never merge works.
Contradictory identifiers remain separate with a conflict for manual resolution.

## Assisted extraction and measurement

```sh
research-lineage assess candidate.json --out candidate-decision.json
research-lineage evaluate examples/evaluation/gates.json --out gate-report.json
research-lineage study examples/evaluation/study-empty.json --out study-report.json
```

A candidate has `id`, `type` (`result` or a supported relation), `claim`, `source`,
and `evidence`. Source fields are `work_id`, `version_id`, `url`, and `access`
(`full_text`, `abstract`, or `unavailable`). Evidence repeats the exact identity
and URL and adds `locator`. Relations declare `basis`. A bound improvement also
needs `comparison.comparability` and `left`/`right` objects with `input`,
`assumptions`, `cost`, `error`, and `cost_unit`. Missing evidence or incomparable
units cause abstention. A successful gate returns `propose`, never `reviewed`.

The checked-in gate manifest contains engineering fixtures. Its decision metrics
measure the gate against supplied labels, not extraction accuracy in the wild.
Independent human labels need actual consent, methods and review references; the
tool records them but cannot authenticate reviewers. See [the study protocol](evaluation-protocol.md).

## Source-version-aware updates

```sh
research-lineage update previous.json revised.json --as-of 2017-01-01 --out update-proposal.json
```

Both maps must be valid revisions of the same map. The proposal retains the full
diff and separately identifies results/relations whose exact cited versions were
available by the cutoff. Later revisions and unavailable endpoints are excluded
or flagged; later evidence checks are listed. The output explicitly states that
historical knowledge reconstruction is unavailable. No input is edited, and no
critique automatically invalidates downstream results. Existing report paths are
refused to protect prior work.
