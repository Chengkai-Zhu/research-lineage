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

In **Explore map**, switch **Color by** between research threads, authors, and
recorded teams. Multiple color marks show collaboration. Click a legend name or
use **Follow a name** to trace that label across papers; other work stays visible
in gray. Team mode uses explicit version-bound assignments from the data guide.
It never infers a team from shared coauthors. Recorded names may be ambiguous.
HTML downloads retain the selected mode; SVG downloads include its legend.
Author and team links use `#author=<recorded name>` and `#team=<group ID>`.
They select only labels already present in the map. Saved HTML also records the
reading view and selected comparison or result; a URL fragment takes precedence
over the saved location. Filters never remove data from the downloaded file.

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

Open `http://127.0.0.1:8765/`. The same product is published at
[LitDelta](https://chengkaizhu.site/research-lineage/). The landing page offers
three fixed public examples: the one-paper comparisons, the NMT author history,
and the actual 52-work research run, explicitly labeled PARTIAL.

Every reader uses the canonical renderer. The complete `offline.zip` preserves
all three maps, their HTML/SVG/JSON/review exports, source notes, the recorded
research audit and the current standalone skill. Extract it, then open
`START-HERE.html`; individual `map.html` files also work independently. The online
landing page is omitted from the archive so its download link cannot become a
broken link back to the archive itself. No original papers or private inputs are
published. Browser file-navigation restrictions may require a manual check in
the user's own browser.

`manifest.json` records source revision, local-change status, sizes and SHA-256
checksums. Verify local files or explicitly check the published downloads:

```sh
python scripts/verify_preview.py --directory output/litdelta-preview --out output/local-preview-check.json
python scripts/verify_preview.py --url https://chengkaizhu.site/research-lineage/ --out output/public-preview-check.json
```

The URL check makes bounded, explicit HTTP requests. It checks availability and
byte integrity, not scientific truth. Tampered files and inconsistent offline
archives fail with exit 2; an existing report is never overwritten.

Publication is explicit. For this PR, dispatch the existing CI workflow against
the product branch with its publication input:

```sh
gh workflow run ci.yml --repo Chengkai-Zhu/research-lineage --ref issue-20-litdelta -f publish_preview=true
```

All four Windows/Linux test jobs must pass before the reusable Pages job runs.
After merge, the standalone **Publish LitDelta preview** workflow can also be
dispatched; it runs tests and local artifact verification before deployment.
The `github-pages` environment controls allowed branches. Normal pushes and PR
checks never publish the site. Deployment does not merge a PR or tag a release.

## Acceptance evidence

```sh
python scripts/verify_litdelta.py --out output/litdelta-acceptance
```

Use a fresh output directory. `report.html` links the real example and shows
expected and observed outcomes for software controls. `report.json` also preserves
the research-integration, browser, publication, and participant evidence states.
Exit zero means the software controls pass; it does not mean those other streams
are complete. `--require-integration` exits nonzero until actual integration passes.

The default integration manifest is the actual committed #12 surface-code rerun;
`--research-manifest <path>` can select another recorded run. The script uses the
canonical `audit_run` API, preserves every component outcome, and distinguishes
adapter/provenance/source-trail success from research completion. The committed
run has a central access gap and remains PARTIAL; issue closure does not change
that evidence. It never manufactures a fresh run from the comparison fixture.
Research corpus size, cutoff, backward/forward searches,
coverage, and stopping decisions belong to #14/#12. Display size never limits them.

Engineering fixtures and browser walkthroughs are not independent scholarly
review or consented participant observations. Those remain #10.
