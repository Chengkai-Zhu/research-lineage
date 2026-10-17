# LitDelta result comparisons

LitDelta is the repository and product name; `research-lineage` remains the installation and
skill name. The two installed commands use the same runtime. There is no new
account, service, or runtime dependency.

The canonical repository is `Chengkai-Zhu/litdelta` (formerly
`Chengkai-Zhu/research-lineage`). Existing issue and PR numbers are preserved.
Use the new `/litdelta/` website URL; project Pages URLs are not repository
redirects. Legacy package, skill, module and schema identifiers remain stable.

## Read a comparison

```sh
python -m pip install -e ".[dev]"
litdelta demo --example comparisons --out output/comparisons
```

Open `output/comparisons/map.html`. Maps with authored comparisons start with a
question and its answer. Choose another question in the left column, or use the
question picker on a narrow screen. The answer keeps its applicability, tradeoffs
and review status visible. Expand **Conditions & sources** for exact versions,
locators and the complete assessment. **Choose other results** opens the advanced
pair comparison; **Read this question** returns an authored answer to the page.
**Explore map** opens the graph, while **Overview** provides a reading route and
an optional **About this map** summary.
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

## Use an explanation outside the map

In **Compare**, choose **Save this explanation**. Copy the Markdown into your
notes or download the `.md` file for a journal club or collaborator. The note
includes the selected question, applicability, tradeoffs, compared result
settings, conditions, source versions and locators, rationale, recorded reviews,
exclusions and gaps. Unknown values remain **Not extracted**; an incomparable
question stays incomparable. Source-check outcomes are recorded, not rerun.

The note is a selected explanation, not the complete map or an independent
scientific review. The full HTML/JSON exports remain available. Imported strings
are escaped as Markdown data; they are never inserted as executable HTML. Saving
does not publish a map or create a shared account.

## Keep a personal reading collection

Open any result and choose **Add to My reading**. From a comparison, **Add both
to My reading** keeps its two results; repeated additions do not duplicate them.
The **My reading** button shows your count. An empty collection can start with
the authored reading route. Move items up/down, remove them, or select their
titles to inspect the exact source in the map. **List view** in the explorer is
the complete searchable map, separate from your personal collection.

**Export research note** previews and downloads Markdown containing your order,
conditions, pinned source versions, evidence locators, review status and scope.
Related comparison questions point back to their complete authored assessments.
**Prepare evidence check** creates a request to give your research agent, with
the same source-linked note as data. It asks for a task-by-task report on missing
conditions, abstract/metadata-only support, unresolved excerpt checks and the
map's recorded limits. These follow-ups are not automatically scientific open
questions; neither action resolves them or upgrades scholarly review.

The collection has no paper limit and does not change the research corpus.
There is no automatic storage: reloading discards unsaved changes. To keep your
selection, choose **Export map → Interactive HTML**. Reopening that full file
restores the order, and subsequent HTML exports retain it. Canonical JSON and
all full-map exports still contain every result and source. The browser never
starts research or uploads the collection. The standalone skill builds the same
reader for new maps; no new agent or API is required.

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
[LitDelta](https://chengkaizhu.site/litdelta/). The landing page offers
three fixed public examples: the one-paper comparisons, the NMT author history,
and the actual 52-work research run, explicitly labeled PARTIAL.

The homepage's **Open the example** button opens the comparison directly, without
a setup dialog. Other research stories, the skill and offline download follow.
**Use your own paper** accepts a paper link, title, DOI or research question.
Optionally choose a goal: trace developments, compare approaches or prepare a
journal club. **Copy research request** includes your input and the selected
goal, ready to paste into an agent with the skill installed. Preview it before
copying if desired. Empty inputs cannot be copied; clearing the field also clears
the generated request. Clipboard failure reveals and selects it for manual copying.
The page processes input in memory, without sending it to a server or saving it
to browser storage. It does not run new research. Setup instructions remain
available beside the request.

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
python scripts/verify_preview.py --url https://chengkaizhu.site/litdelta/ --out output/public-preview-check.json
```

The URL check makes bounded, explicit HTTP requests. It checks availability and
byte integrity, not scientific truth. Tampered files and inconsistent offline
archives fail with exit 2; an existing report is never overwritten.

Publication is explicit. For this PR, dispatch the existing CI workflow against
the product branch with its publication input:

```sh
gh workflow run ci.yml --repo Chengkai-Zhu/litdelta --ref issue-20-litdelta -f publish_preview=true
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

## Explore the Aurora graph

Choose **Explore map** for a chronological atlas. **Focus** shows up to twelve
results from the authored reading route and overview, plus any selected result
or relationship endpoints. It is a reading aid, not a scientific importance
ranking. Maps without authored reading guidance show all results.

Choose **All** to display every result, or **List view** for a compact reading
list. Search and filters always search the complete map. **Filters & colors**
contains thread/review filters and the existing author/recorded-team controls.
Author or team coloring shows the full matching graph so the focus view cannot
hide another work by that name. Color marks describe identity, not inheritance.

Click a card to highlight its direct connections and open the pinned evidence.
Time runs down each column, then left to right across labeled periods; spacing
is schematic. A dashed edge still means proposed, not independently reviewed.
Use the **Dark / Light** selector for appearance and **Fit** to reset zoom.
On a narrow screen the cards stack into a readable chronological column.

Interactive HTML retains the appearance and focus/all preference on export.
Every export still contains the complete underlying map, including hidden
results, source versions, conditions, uncertainty and exclusions. The standalone
SVG uses a light background and the full chronology for reuse and printing.
