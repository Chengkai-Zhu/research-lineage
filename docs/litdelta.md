# LitDelta result comparisons

LitDelta is the product name; `research-lineage` remains the installation and
skill name. The two installed commands use the same runtime. There is no new
account, service, or runtime dependency.

## Read a comparison

```sh
python -m pip install -e ".[dev]"
litdelta demo --example comparisons --out output/comparisons
```

Open `output/comparisons/map.html`. Start with **What actually changed?** and choose
a question. The explanation leads with the change, its applicability, and its
tradeoffs. Expand conditions and evidence to inspect exact versions and locators.
Comparison URLs use `#comparison=<id>` and work in the downloaded HTML as well.

One pair can answer multiple questions. For example, sequential layer depth and
total arithmetic work have different outcomes. Selecting Result A and Result B
does not select a question when several exist. Reversing them never reverses a
claim of improvement.

```sh
litdelta compare output/comparisons/map.json r-recurrent r-attention
litdelta compare output/comparisons/map.json r-recurrent r-attention --comparison c-parallel-depth
```

The first command lists choices without an assessment; the second returns the
authored record. `comparable` means the author has documented a common regime,
not that one result is better. `conditional`, `incomparable`, and `unknown` retain
their distinct reasons. Equal text does not turn an unknown pair into a comparable
one. All annotations remain proposed until real reviews are recorded.

## Author and check records

Use the [data guide](../skills/research-lineage/references/data-guide.md) for the
1.1 record format. Existing 1.0 maps remain usable and are not silently migrated.
The 1.1 schema is available with:

```sh
litdelta schema --format-version 1.1 --out output/schema-1.1.json
litdelta init "A scoped comparison question" --format-version 1.1 --out output/draft.json
```

The host authors results and comparison explanations from sources. The toolkit
validates identity, references, and evidence requirements; it cannot infer or
certify scientific superiority. Candidate improvements use the complete context
`{"id": "candidate-id", "map": <1.1 map>, "relation_id": "relation-id"}` with
`assess`. Direct map validation uses the same gate. Legacy single-sided improvement
candidates abstain and ask for this context.

Evidence may contain a short quote independently from its interpretation. Local
matching is an explicit operation using UTF-8 text obtained by an authorized host
document tool:

```sh
litdelta anchor output/comparisons/map.json e-recurrent --text local-source.txt --out output/anchor-check.json
```

Omit `--text` to obtain `unchecked`. Matching uses Unicode NFC plus collapsed
whitespace, case-sensitive exact text and optional prefix/suffix. The digest binds
the exact decoded text checked (encoded as UTF-8), not an independently authenticated
paper. A stored report is labeled as recorded, not reproduced in the browser.
Changed text or selectors must be rechecked. A successful match does not upgrade
scientific review or establish that the source supports the interpretation.

Diffs include comparison and anchor edits. Cutoff-aware proposals also check every
comparison's source availability and exclude dependent relations when its evidence
is unavailable. They do not reconstruct historical knowledge.

## Browser preview

```sh
python scripts/build_preview.py --out output/litdelta-preview
python -m http.server 8765 --directory output/litdelta-preview
```

Open `http://127.0.0.1:8765/`. The builder uses the same committed example and
renderer as `demo --example comparisons`. `index.html` is the complete offline
reading file; `offline.zip` contains HTML, SVG, JSON, review report and source notes.
No original papers or local/private inputs are published.

The Pages workflow is an explicit publication path after the feature is merged.
It builds the same artifact and publishes through the repository's Pages
environment. A successful build alone does not establish public availability.
Record the actual deployment URL and browser observations before closing #20.

## Acceptance evidence

```sh
python scripts/verify_litdelta.py --out output/litdelta-acceptance
```

Use a fresh output directory. `report.html` links the real example and shows
expected and observed outcomes for software controls. `report.json` also preserves
the research-integration, browser, publication, and participant evidence states.
Exit zero means the software controls pass; it does not mean those other streams
are complete. `--require-integration` exits nonzero until actual integration passes.

`--research-manifest <path>` delegates to the actual `verify_research_run.py`
provided by #12 when present. It retains the checker output and requires its four
PASS outcomes without PARTIAL/FAIL. It never manufactures a fresh run from the
comparison fixture. Research corpus size, cutoff, backward/forward searches,
coverage, and stopping decisions belong to #14/#12. Display size never limits them.

Engineering fixtures and browser walkthroughs are not independent scholarly
review or consented participant observations. Those remain #10.
