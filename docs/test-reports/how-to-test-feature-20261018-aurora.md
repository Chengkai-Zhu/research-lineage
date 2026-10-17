# Feature Test Report: LitDelta Aurora

**Date:** 2026-10-18, Asia/Shanghai

**Project type:** Offline Python CLI, standalone HTML/SVG reader, portable agent skill

**Features tested:** Aurora chronology and corpus selection; author/team identity presentation; full-map exports; preview and bundled runtime integrity

**Use Case:** Ephemeral, explicitly scoped by the coordinating agent

**Profile:** Ephemeral researcher, comfortable reading quantum-error-correction papers and basic CLI commands

**Expected Outcome:** Explore the 54-result surface-code history chronologically; retain access to all results, evidence and conditions; distinguish recorded authors/teams; keep reusable offline exports without losing records, changing scientific metadata, or inventing relations.

**Verdict:** pass

**Critical Issues:** 0

## Summary

This is an independent simulated-user check of local commands, generated artifacts,
and production JavaScript functions. The verdict applies to that scope. It is not
an independent scientific review, a participant study, or a claim of completed
browser acceptance. Actual desktop and narrow-screen interaction was assigned to
the parent agent; this tester did not use browser tools, click controls in a real
browser, or inspect a browser screenshot.

| Feature | Discoverable | Setup | Works | Expected Outcome Met | Doc Quality |
|---------|-------------|-------|-------|---------------------|-------------|
| Chronological Aurora, Focus and All | Yes | Yes | Yes in geometry/controller checks | Yes in tested scope; visual reading delegated | Good; chronology and curated focus are explained |
| Complete results, evidence and conditions | Yes | Yes | Yes | Yes | Good; hidden results and proposed review status remain explicit |
| Author and recorded-team presentation | Yes | Yes | Yes in controller checks | Yes for author labels and absence of team records | Good; no coauthor-to-team inference promised |
| Standalone HTML/JSON/SVG and skill runtime | Yes | Yes | Yes; note-wrapping observation fixed and targeted re-test passed | Data and packaging pass; actual browser rendering remains separate | Good |
| Desktop/narrow-screen visual usability | Yes | Not attempted by this tester | Parent verification | Not asserted here | Applicable controls are documented |

No implementation, source dataset, Git state, installation, network service or
account configuration was changed. Only the report and test-owned files under
`output/aurora-user-*` were written.

## Scenario and evidence boundary

The researcher starts with the actual recorded surface-code rerun, rather than the
four-paper illustration. They want the authored reading route as an entry point,
then access to the entire corpus, exact versions and qualifications. They need an
HTML file that can be shared offline and a reusable SVG/JSON export. Author colors
must represent recorded names. Team colors must not infer affiliation or teams
from coauthorship.

The selected dataset contains **52 works, 52 recorded source versions, 54 results,
58 relations, 55 evidence records, three scope exclusions and three scope gaps**.
Its recorded research status remains **PARTIAL**, and all 112 result/relation
annotations remain proposed. This test neither checked the papers themselves nor
upgraded those statuses.

The source map SHA-256 was
`c358748018023a31860527157c3502ddf5d862015a70008f85836f2257256b47`.
The fresh preview records source revision
`e48103c53d7679ec58741adeff1689b2722d4d5d` with local changes present.

## Per-feature details

### Discoverability and local setup

- **Role:** A researcher who can run a documented command but wants the output to remain understandable without the implementation.
- **Use Case:** Build the recorded surface-code history and locate the complete graph and its export options.
- **What they tried:** Read `README.md`, `docs/litdelta.md`, repository instructions, CLI help, and relevant renderer/controller source before running local commands.
- **Discoverability:** The README introduces Aurora, and `docs/litdelta.md#explore-the-aurora-graph` explains Focus, All, List view, source checks, chronology, appearance, identity coloring and export completeness.
- **Setup:** Used the supplied Python environment and Node without installing anything. The supplied environment initially resolved another installed checkout; this was detected when `research_lineage.graph` was unavailable. Subsequent direct module commands explicitly used `PYTHONPATH=src`. Preview/package scripts select the local source themselves. The initial bare-module build is excluded from acceptance evidence.
- **Functionality:** Explicit current-source build and validation succeeded. The validation warnings about scholarly review and abstract/metadata evidence remained visible.
- **Expected vs Actual Outcome:** The documented local path is available without accounts or network access. The environment mismatch was a test precondition, not an Aurora defect.
- **Blocked steps:** None for the local scope. Installation and network/publication branches were outside scope.
- **Friction points:** See the browser SVG note-wrapping observation below.
- **Doc suggestions:** No blocking documentation change is needed for this scoped flow.

### Chronology and full-corpus access

- **What they tried:** Built a fresh surface-code map, parsed its SVG, exercised production layout helpers, and ran the production graph controller in Node with minimal DOM doubles.
- **Functionality:** All 54 static SVG result IDs and all 58 relation IDs match the original map exactly. Reading positions, sorted down a column and then left to right, follow first-publication dates. The four static period labels are `1995–2021`, `2021–2024`, `2024–2025`, and `2025–2026`.
- **Controller observations:** Initial Focus shows 12 authored results; All shows 54. Selecting a non-Focus result produces 13 visible results. Selecting a relation with two non-Focus endpoints produces 14. A matching result outside Focus remains visible under a filter. Empty matching sets produce finite layout values. Hidden cards receive `tabindex=-1` and `aria-hidden=true` in the controller probe.
- **Layout checks:** Existing tests cover 280, 390, 640, 900 and 1280 pixel layout inputs, no overlapping card rectangles, complete result counts, deterministic order and separate results from the same paper. These are geometry checks, not measurements of real browser glyphs or user reading speed.
- **Expected vs Actual Outcome:** Complete data and a chronological, non-ranking layout are supported by the tested implementation. Actual text readability, connection selection and scrolling remain parent browser verification.

### Authors, teams and evidence boundaries

- **What they tried:** Used the production identity controller with the actual corpus, including a known author and rejected unknown author/team IDs; inspected evidence and relationship rendering code.
- **Functionality:** The source has 233 distinct recorded author labels and no recorded team assignments. Author coloring and following a known author keep all 54 results available. Unknown identities are rejected. Team mode displays the no-sourced-assignment explanation and does not create teams.
- **Scientific metadata:** JSON, HTML embedded data and SVG metadata each compare equal to the entire original canonical object. This comparison covers pinned versions, result conditions, uncertainty, relation types, review records, scope gaps and exclusions; no field-level exception was allowed.
- **Expected vs Actual Outcome:** Author labels remain labels, and absent team evidence stays absent. The inspector's evidence text is sourced from canonical records. This tester did not click evidence links or validate source authenticity.
- **Untested branch:** Positive, sourced-team coloring is not available in the chosen real corpus. Its implementation was inspected, but no new synthetic team was added to this scientific map.

### Portable exports and reusable skill runtime

- **What they tried:** Generated fresh HTML/SVG/JSON/review files, parsed their content, exercised actual preference-export functions, built and verified a fresh offline preview, extracted the generated skill into a test-owned directory, and used its bundled runner to build the same map.
- **Functionality:** Every generated HTML/SVG/JSON contains the complete canonical map. The SVG retains full labels in accessible names/titles even when display labels wrap or truncate. The HTML has no external auto-loaded asset references, and its CSP disallows connections. Source hyperlinks are user-initiated references.
- **Preference export:** The production controller plus `exportViewPreferences` retained light appearance, All density, the selected reading location and collection order through two complete HTML exports. Canonical data remained identical. This exercised functions with DOM doubles; it did not exercise the browser Blob/download UI.
- **Offline collection:** `verify_preview.py` returned PASS for the fresh preview, all manifest files and the offline ZIP. The recorded research status remains PARTIAL.
- **Bundled runtime:** The extracted standalone skill includes `graph.py`, `aurora-graph.js` and `aurora.css`. Its runner rebuilt `map.json`, `map.html`, `map.svg` and `review.md` byte-for-byte identically to the current checkout build.
- **Expected vs Actual Outcome:** Data preservation, packaging and portable runtime checks pass. Browser file navigation, download behavior and final pixel layout remain separate parent verification.

## Commands and artifacts

The following commands completed successfully against the intended source:

```sh
PYTHONPATH=src /private/tmp/litdelta-venv/bin/python -m research_lineage build docs/test-reports/surface-code-rerun/map.json --out output/aurora-user-test-current
/private/tmp/litdelta-venv/bin/python -m pytest -q tests/test_graph.py tests/test_reading.py tests/test_identity.py
node --test tests/js/aurora.test.cjs tests/js/reader-state.test.cjs tests/js/reading-workspace.test.cjs
/private/tmp/litdelta-venv/bin/python scripts/build_preview.py --out output/aurora-user-preview
/private/tmp/litdelta-venv/bin/python scripts/verify_preview.py --directory output/aurora-user-preview --out output/aurora-user-preview-verification.json
node output/aurora-user-test-current/controller-probe.cjs
```

The relevant Python suite passed **18 tests**; the JavaScript suites passed **27
tests**. Additional independent artifact/controller checks were performed by the
probe and local Python inspection described above.

Test-owned diagnostic artifacts:

- `output/aurora-user-test-current/integrity.json`: counts, source hash, equality checks and artifact sizes.
- `output/aurora-user-test-current/controller-probe.cjs` and `controller-probe.json`: production-function invocation trace and explicit DOM-double limitation.
- `output/aurora-user-test-current/controller-export.html`: complete HTML after repeated preference exports.
- `output/aurora-user-test-current/portable-runtime.json`: bundled-runtime byte comparisons.
- `output/aurora-user-preview-verification.json`: preview integrity PASS and preserved PARTIAL research status.

## Issues found

1. **Resolved after targeted re-test (original severity: medium): Chinese export notes used different wrapping in browser SVG downloads.** The inspected `viewer.js` `svgExport()` path splits notes only on spaces and wraps at 145 JavaScript code units. The real surface-code overview contains a single 151-character, mostly Chinese token, approximately 295 width units under the renderer's CJK-aware metric. That token is emitted intact in a 1240-wide SVG at 12px, so it is likely to run beyond the reusable canvas. The new Python SVG exporter uses CJK-aware wrapping and does not have the same issue. Metadata remains complete in either path. This observation was sent to the parent; it was not represented as a clicked/downloaded browser failure. The parent unified note wrapping, and the targeted resolution below confirms the implementation change against the real corpus. The observation is closed at the source/function/artifact level; final downloaded SVG pixel layout remains distinct browser evidence.

No blocking or high-severity issue was found in the executed local scope.

## Suggestions

1. The CJK note-wrapping defect is resolved by the targeted checks below. A newly downloaded SVG can provide final browser pixel-layout confirmation; the earlier HTML download predates this fix.
2. Complete parent browser verification for desktop/narrow-screen text, edge clicks, filtering, identity controls, saved HTML reopening and downloads. Keep those observations separate from this report's VM and artifact evidence.
3. Preserve the current explanations that Focus is authored guidance, color is identity and spacing is schematic. They make the display's scientific limits discoverable without hiding the complete corpus.


## Resolution and targeted re-test, 2026-10-18

The parent replaced the browser-only, space-based note wrapping with shared
`export_lines(data)` in `render.py`. That helper uses the existing CJK-aware
`wrap_label(line, 185)` and supplies both CLI SVG text and the HTML's embedded
`export-notes`. The production browser `svgExport()` consumes those prewrapped
lines directly.

This tester inspected the revised paths and ran only the relevant graph suite:

```sh
/private/tmp/litdelta-venv/bin/python -m pytest -q tests/test_graph.py
```

All **8 targeted tests passed**. An additional independent check of the actual
surface-code corpus confirmed:

- All 842 prewrapped appendix lines are identical in the shared helper, generated HTML export notes and CLI SVG appendix.
- No line exceeds 185 display-width units; the original note content is preserved after normalizing whitespace introduced by line wrapping.
- Executing the production `svgExport()` function under Node with DOMParser/XMLSerializer doubles emitted exactly those 842 text nodes, preserved the complete canonical map metadata and allocated viewBox height for every line. This is function evidence, not a real browser SVG download or pixel measurement.
- Canonical data in the current generated HTML remains unchanged.

The diagnostic records are `output/aurora-user-svg-retest/retest.json` and
`output/aurora-user-svg-retest/browser-export-function.json`. The report remains
**Verdict: pass**, **Critical Issues: 0**. No broad re-test was performed for this
localized change.

### Downloaded HTML and parent browser observations

The parent supplied a real downloaded HTML copy at
`output/aurora-evidence/downloaded-map.html`. This tester read it as text and
confirmed complete canonical-map equality and these exact saved preferences:

```json
{
  "graph-preference": {"density": "all", "theme": "light"},
  "reading-preference": {
    "mode": "explore",
    "view": "map",
    "fragment": "#result=logical-cliffords-result"
  },
  "color-preference": {"mode": "thread", "focus": "all"},
  "collection-preference": []
}
```

The selected result label is `距离3表面码组合出完整Clifford生成集`. The downloaded file
predates the final wrapping fix; its data/preferences are evidence of saved state,
not evidence that it contains the repaired SVG exporter.

The following actual UI observations were reported by the parent, not independently
performed by this tester: at 1280 pixels, Focus showed 12 results and All showed
54 with no card overlap or label overflow; search selected the logical-Clifford
result and exposed the exact pinned source
`https://arxiv.org/html/2607.01473v1`; following Gidney kept all 54 results and the
same identity marks. Narrow-screen verification was still being performed by the
parent when this addendum was written.

**Browser offline reopening was not tested.** The browser URL policy blocked the
file-protocol reopen. No alternative method was used to bypass that block. Local
artifact inspection above confirms content and preferences only.

### Final parent UI verification

The parent completed the following browser checks after the fixes. These are
actual UI observations, separate from this tester's CLI and VM checks:

- At 1280 CSS pixels, Focus (12 results) and All (54 results) have no intersecting
  card rectangles or overflowing title spans. Search reaches results outside
  Focus, and an unmatched query reports `0 of 54` with disabled density controls.
- At a 390 CSS pixel iframe width, the document has no horizontal overflow and
  Focus has no overlapping cards or overflowing titles. This is a responsive
  container test, not mobile-device emulation.
- Pressing Enter on the Dennis result opens its evidence inspector, scrolls it
  into view in the narrow layout, and exposes the pinned source
  `https://arxiv.org/pdf/quant-ph/0110143v1`.
- Both appearance choices render successfully. SVG focus uses an accent dashed
  card border for keyboard navigation, avoiding a browser-native rectangular
  outline around the selected graph group.
- The small demo was also built and inspected in the browser. English titles now
  wrap at word boundaries (`Quantum signal` / `processing`), with splitting
  reserved for tokens wider than the entire card. A focused regression covers
  word boundaries, long tokens, CJK and the three-line limit.
- The final full gate passed: 188 Python tests, 31 Node tests, Ruff, and all 21
  software acceptance checks. Scholarly review and public deployment remain
  separate from these engineering checks.
