# Research record and completion

A readable first screen is an editorial choice. Research coverage depends on
the question and the evidence, not on a preset number of papers. Keep the full
candidate ledger, and retain all included works even when the introductory route
visits only a selection.

## During research

1. Run `start` and preserve its original `research-brief.json`. It pins the input
   and research cutoff. Record an explicit user request before changing either.
2. Record each actual search/open/read operation as a JSONL trace entry while it
   happens: tool, exact query or URL, time, observed source URLs, a concise
   paraphrase of the observation, and success/failure. Several searches returned
   by one batched tool call may share an entry if its query records the batch.
   Logs are agent-recorded observations, not authenticated provider telemetry.
3. Use the seed bibliography and a relevant review as reference sets. Identify
   historical/methodological branches from their actual contents; record the
   source and locator justifying each branch. A review or bibliography is a
   coverage aid, not evidence for every primary result.
4. Search backward and forward, recording queries, access failures, candidates
   and decisions. Check recent work through the research cutoff even when the
   input specifies an older paper version. A search with no relevant results
   still has an observed finding and trace. A failed lookup is not a successful
   search. Branches must remain visible when the chosen search tool is limited.
5. Include candidates because they explain the scoped development. Exclude
   duplicates, out-of-scope work and unneeded peripheral material with specific
   reasons. Defer relevant candidates that still need reading or verification.
   Do not mark central missing work excluded merely to pass an audit.
6. Reconcile the corpus with the reference sets and branches. Continue when a
   central branch lacks support or a newly identified central candidate remains
   unread. Record the final follow-up checks and the reason for stopping. Use
   `partial` when material coverage/evidence remains unfinished. A completed
   search plan can still have scholarly uncertainty; describe it without
   pretending independent review has happened.

## Record contract

Export the exact schemas (no external dependencies):

```sh
python <skill-directory>/scripts/lineage.py research-schema --out research-schemas.json
```

The output has `manifest`, `research_log` and `trace_entry` schemas. All listed
fields are required; use `null` only where the schema permits it. Use stable
lowercase IDs. The records are separate from map-v1 JSON so existing maps keep
working. Read the schema before writing the files.

- **`research-log.json`**: `schema_version: "1.0"`, `cutoff`, `scope`,
  `reference_sets`, `searches`, `candidates`, `branches`, `stop`.
- **`tool-trace.jsonl`**: one `trace_entry` JSON object per line. `query` contains
  the actual query/URL or batched call arguments; `urls` contains observed source
  URLs. `at` is a timezone-aware ISO timestamp. Keep observations short and
  paraphrased; do not copy whole copyrighted documents or include credentials.
- **`run-manifest.json`**: input, execution provenance and SHA-256-bound artifacts.

Trace timestamps must fall inside the recorded execution interval, and tool names
must appear in `execution.tools`. Included source and reference-set URLs must
occur in successful trace entries. Excluded/deferred candidates may link failed
opens, retaining the failed attempt without claiming content access.

### Research log fields

| Record | Fields and meaning |
| --- | --- |
| Scope | `mode: history` by default, `summary`, `request: null`. `reading_path` requires the actual user request for that narrower task. |
| Reference set | `id`, `url`, `locator`, `purpose`, `candidate_ids`. Record relevant candidates considered from that source, including exclusions; explain the scope of the reference set in `purpose`. |
| Search | `id`, `direction` (`seed`, `review`, `backward`, `forward`), `query`, `checked` date, `status` (`ok`, `failed`), `trace_ids`, `candidate_ids`, `finding`. Candidate links are reciprocal. |
| Candidate | `id`, `title`, exact source `url`, `access` (`full_text`, `abstract`, `metadata`, `unavailable`), `locator`, `decision` (`include`, `exclude`, `defer`), specific `reason`, `work_id`, `search_ids`, `branch_ids`, `trace_ids`. Included candidates map one-to-one to map works and have content access; other candidates use `work_id: null`. Trace URLs must include the source URL. |
| Branch | `id`, `label`, source-grounded `basis`, `reference_set_ids`, `candidate_ids`, `search_ids`, `status` (`covered`, `gap`), `gap` (explanation or `null`). Link candidate membership in both directions. A covered branch needs included evidence. |
| Stop | `status` (`complete`, `partial`), `reason`, `unresolved_candidate_ids`, `unresolved_branch_ids`. These must exactly match deferred candidates and gap branches. Deleting a gap from the stopping summary does not resolve it. |

URLs identify what was actually inspected. If a discovery page points to a
different version, add the final source-read operation to the trace. A candidate
with several read versions uses a mapped version URL and explains the others in
its reason; result-level evidence still pins each exact version in the map.

### Run manifest

`input` has `seed`, `cutoff`, `cutoff_request` (the explicit user request, or
`null` when using the run date). `execution` has `host`, `agent_id`, `model`
(the exposed exact model, otherwise `null`), `context` (`fresh` or `existing`),
`isolation`, `research_date`, timezone-aware `started_at` and `finished_at`,
`skill_revision`, and `tools` (tool names actually used). State context isolation
accurately: a fresh conversation does not imply an operating-system sandbox.
Do not invent an agent/model identifier or measured reading time. Elapsed run
time includes tool waits and is not active research time.

`artifacts` has seven entries: `brief`, `map`, `research_log`, `trace`, `html`,
`skill`, `prompt`. Each is `{ "path": "relative-file", "sha256": "..." }`.
All paths stay within the run folder and refer to distinct files. Preserve the
original brief, the actual skill entrypoint used, and the full invocation prompt
including harness instructions. Bind the final generated HTML and map to the
same corpus. When publishing a run, copy these files into one self-contained
folder and calculate hashes after the copies; do not silently edit the logs.

The `fresh` context is needed for independent workflow acceptance. An ordinary
user's ongoing conversation may correctly use `existing`; the audit will show
that an independent run was not established, without invalidating the map itself.

## Audit and delivery

```sh
python <skill-directory>/scripts/lineage.py audit-research run-manifest.json
```

Exit 0 means PASS for the **recorded evidence**; 3 means PARTIAL and 2 means FAIL.
The report separates execution provenance, cutoff consistency, source trail and
research-plan completion, and counts corpus works separately from route steps
and overview cards. It rejects missing records, inconsistent cross-references,
unrequested cutoff changes, hidden unresolved items and HTML missing map works.
There is no minimum or maximum scholarly paper quota in this assessment.

For a field history the recorded search plan needs seed, review, backward and
forward checks. An explicitly requested narrow ancestry reading path needs seed
and backward checks; it need not become a present-day field survey. Preserve that
request and its cutoff instead of inferring this narrower mode from a paper link.

The checker cannot authenticate a host tool call, prove that the reference sets
cover every important branch, validate scientific claims, or replace an external
researcher. Inspect the source-grounded coverage rationale and representative
claims against primary passages. Publish any independent runner record alongside
the agent log. Do not turn a traceable but poorly researched map into a quality
claim by giving it a PASS label.

Deliver the generated map with a compact evidence report: input and scope,
actual searches and failures, reference-set/branch coverage, included/excluded/
deferred candidates, central uncertainties, and the stopping judgment. Use a
short orientation and a few turning points on the first screen; expose the full
corpus, branch filters and evidence on demand. A partial run remains partial in
the map, report and user-facing handoff.
