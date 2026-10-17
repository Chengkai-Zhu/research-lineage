# LitDelta first-visit simulated-user test

## Date

2026-10-17 (Asia/Shanghai).

## Project type

Offline research-map generator, agent skill, and browser reader. Canonical source is `src/research_lineage` in `/private/tmp/research-lineage-issue20`.

## Features tested

Homepage entry hierarchy; authored comparison page; question navigation and URL state; source/condition disclosure; advanced result selection; map and author controls; own-paper instructions and prompt feedback; 390px CSS viewport layout.

Primary walkthrough: `http://127.0.0.1:8791/first-visit-v2/`. The initial `first-visit-after/` tab was replaced with v2 before the substantive walkthrough. A bounded follow-up checked the L1 fix in `http://127.0.0.1:8791/first-visit-v3/`. Responsive checks used `http://127.0.0.1:8791/first-visit-mobile.html`, whose two iframes were updated from v2 to v3 for that follow-up and render a 390px CSS viewport. This was not real-device testing or device emulation. The full desktop walkthrough was not repeated on v3.

## Use Case: ephemeral

A researcher opens LitDelta for the first time, wants to see what to click, compare a concrete example, inspect its evidence, explore the map, and discover how to use a personal paper.

## Profile: ephemeral

The simulated actor can read research papers but has no prior LitDelta experience. They prefer a ready-to-read example, do not know the product's data model, and need the difference between browser reading and agent research to remain clear. The actor and scenario were supplied in the test assignment; no persistent profile was created.

## Expected Outcome

One clear primary start on the homepage. One click opens an authored comparison as a page. Another question updates the answer and hash. Conditions, review status, and sources remain reachable. Map and author tools still work. Own-paper setup and a usable prompt are discoverable without suggesting that this static browser page runs a research backend.

## Verdict: pass

The expected local first-visit path completed. The one low-severity responsive discoverability issue found in v2 was fixed and checked in v3. No high-severity issue was found. This is simulated-user evidence, not human participant validation, scientific peer review, or a claim that every product path was tested.

## Critical Issues

0

## Summary table

| Feature | Actual result | Verdict |
| --- | --- | --- |
| Primary start | The filled `Open the example` button is the dominant homepage action; the preview states one paper, four results, and proposed annotations. | Pass |
| Direct comparison | One click opened `map.html#comparison=c-parallel-depth` as a full comparison page, without a setup modal. | Pass |
| Questions and URL | All four authored questions changed selected state, heading, conclusion, and comparison hash. | Pass |
| Conditions and sources | Scope conditions and review status were visible; expanded evidence included locators, excerpts, pinned v7 links, and validation caveats. | Pass |
| Advanced comparison | Unknown pairs stayed unknown; a selected authored assessment offered `Read this question`; closing preserved the prior reading page. | Pass |
| Map and authors | `See these on the map` opened the selected result inspector; author coloring and following a name worked; the NMT story opened with Yoshua Bengio selected. | Pass |
| Own paper | Header navigation reached instructions, skill link, setup disclosure, prompt, and copy-success feedback. | Pass within discovery scope |
| 390px viewport | Main entry, question picker, answer, review state, source cards, and disclosure worked. v3 visibly explains table scrolling and exposes a named keyboard-focusable region. | Pass after L1 fix |

## Per-Feature Details

### Homepage and direct comparison

- **Role:** First-time researcher.
- **Use Case:** Find a useful first action and see a comparison immediately.
- **What they tried:** Viewed the homepage, inspected its visual hierarchy, and clicked `Open the example`.
- **Discoverability:** Clear. The filled primary button and `Ready to explore. No setup needed.` text gave an obvious start. Secondary story cards appeared below it.
- **Setup:** None for reading. Used one new background IAB tab owned by this test.
- **Functionality:** The click navigated directly to `#comparison=c-parallel-depth` with the Compare mode active and the authored question selected.
- **Expected vs Actual:** Expected a reading page; received a reading page with a question list, conclusion, conditions, review state, and source disclosure.
- **Blocked steps:** None.
- **Friction points:** None material observed on this path.
- **Doc suggestions:** Preserve the short no-setup statement and the preview's one-paper/proposed-annotation scope.

### Questions, conditions, and source evidence

- **Role:** Researcher checking what a claim actually says.
- **Use Case:** Compare sequential depth, total work, generation, and translation quality without conflating their metrics.
- **What they tried:** Opened `Conditions & sources` for sequential depth, then clicked each of the remaining three questions.
- **Discoverability:** The left question list and the source disclosure label were explicit.
- **Setup:** None.
- **Functionality:** The hashes became `c-total-work`, `c-decoding`, and `c-quality` with matching headings and conclusions. The last two displayed `Not a valid comparison`. All showed `Awaiting scholarly review`.
- **Expected vs Actual:** Expected scoped answers; the work answer said the tradeoff depends on n relative to d, the generation answer distinguished layer scheduling from output dependency, and the quality answer distinguished operation counts from BLEU. Conditions and caution text remained on the main page.
- **Blocked steps:** External pinned-source links were inspected but not opened because this run permitted local requests only. External source availability and quotation accuracy were not validated.
- **Friction points:** None material at the desktop viewport. Detailed evidence is intentionally behind a clearly named disclosure.
- **Doc suggestions:** Preserve pinned source versions, locators, local-match status, and the separation between authored interpretation and source excerpts.

The expanded sequential-depth evidence showed Table 1/Section 1 and Table 1/Section 4 locators, `transformer-v7`, the pinned `1706.03762v7` source, `Local text match: unchecked`, and the statement that source matching and structural checks do not certify the authored assessment. This test confirmed the UI retains those boundaries; it did not verify the scientific conclusion.

### Advanced result selection and return behavior

- **Role:** Curious reader exploring another pair of results.
- **Use Case:** Change a pair without silently replacing the current reading location.
- **What they tried:** From `c-quality`, opened `Choose other results`; selected Recurrent layer versus Translation quality; changed the second item to Self-attention layer; selected the total-work question; closed the dialog. Repeated the selection and clicked `Read this question`.
- **Discoverability:** The entry label described its purpose. The dialog showed two result menus and, when needed, a question/regime menu.
- **Setup:** None.
- **Functionality:** The unassessed pair explicitly said comparability was unknown. The recurrent/self-attention pair required a choice among two authored questions. Selection previewed total work while the URL stayed `c-quality`. Closing returned to the quality page and restored focus to `Choose other results`. The explicit read link then opened the total-work page and changed the hash to `c-total-work`.
- **Expected vs Actual:** Matched. Preview, dismissal, and committed navigation were visibly distinct.
- **Blocked steps:** None.
- **Friction points:** This branch requires several controls, but the primary authored example does not require it.
- **Doc suggestions:** Keep the explicit read action and the no-assessment message.

### Map and author exploration

- **Role:** Reader looking for connections and authors behind the example.
- **Use Case:** Move from a comparison to evidence on a map, then follow an author.
- **What they tried:** Clicked `See these on the map`, changed `Color by` to Authors, followed Ashish Vaswani, returned to the homepage, opened the NMT story card, and selected Joint alignment.
- **Discoverability:** The comparison-to-map action was explicit. `Color by` exposed Authors; the following menu and legend buttons appeared after that selection. The homepage NMT card clearly advertised following authors.
- **Setup:** None.
- **Functionality:** The comparison opened Explore map at `#result=r-attention` with a Self-attention layer evidence inspector. Author coloring exposed author marks and a `Follow a name` selector. Following Ashish Vaswani selected his name. The NMT story opened `#author=Yoshua%20Bengio` with Yoshua Bengio selected and two marked papers. Selecting Joint alignment opened its inspector at `#result=r-bahdanau`.
- **Expected vs Actual:** Matched the scoped exploration task.
- **Blocked steps:** None for local exploration. Further source openings were outside scope.
- **Friction points:** Author controls require first choosing Authors in the comparison example; the NMT card avoids that setup for the advertised author story.
- **Doc suggestions:** Preserve the story-card shortcut and the visible author-selection state.

### Own-paper discovery

- **Role:** First-time reader ready to try a personal paper.
- **Use Case:** Learn the next action without assuming the website can run research itself.
- **What they tried:** Used the header's `Use your own paper` link, expanded `How to set it up`, read the prompt, and clicked `Copy prompt`. Also expanded `About the examples & sources`.
- **Discoverability:** The header link reached `#your-research`. The section clearly said to use the skill in a research agent. The prompt and copy button were visible alongside setup.
- **Setup:** Instructions specified extracting `research-lineage` into the agent's skills folder, sending the prompt, and opening the generated `map.html`; Python 3.11+ and an agent with research tools were stated.
- **Functionality:** The button produced `Copied. Paste it into your research agent.` feedback. Clipboard content was not independently read. About text retained the scholarly-review caveat and PARTIAL source-gap explanation.
- **Expected vs Actual:** Discovery completed. The page points to an agent workflow and does not present a browser upload or research-execution control.
- **Blocked steps:** Skill download, installation, external installation guide, and a real research run were intentionally untested. No download or installation was attempted.
- **Friction points:** A reader unfamiliar with agent skills will need the linked installation guide to identify their agent's skill folder. That guide was not opened under the local-only constraint.
- **Doc suggestions:** An optional local or bundled copy of agent-specific installation guidance would make this handoff easier to assess offline.

### 390px CSS viewport

- **Role:** Reader using a narrow layout.
- **Use Case:** Keep the same primary path and scientific caveats reachable when the sidebar becomes a picker.
- **What they tried:** Opened the development fixture, inspected both 390px iframes, changed the comparison picker from quality to sequential depth with Home/Return, expanded sources, scrolled down, and horizontally scrolled the conditions table.
- **Discoverability:** The homepage primary button remained prominent. The comparison's labeled Question picker was clear. Horizontal table scrolling lacked a persistent cue in v2; v3 added `Swipe or scroll sideways for all columns →` immediately above the table.
- **Setup:** The provided local iframe fixture; no device emulation.
- **Functionality:** The comparison iframe changed to `#comparison=c-parallel-depth`, with the matching picker value, heading, answer, conditions, and review status. Evidence cards wrapped within the viewport. Horizontal scrolling revealed the table's right-hand columns.
- **Expected vs Actual:** Main reading path matched. In v2, a novice could mistake the clipped table's right side for missing content. The bounded v3 check confirmed the visible cue and that three Tab presses from the expanded disclosure reached the named `Full comparison conditions; scroll horizontally` region.
- **Blocked steps:** No permanent block. Real-device, touch, zoom, and assistive-technology behavior were not tested.
- **Friction points:** Low issue L1 was fixed during this run.
- **Doc suggestions:** Retain the new cue beside the table.

## Issues Found

### L1 — Low, fixed in v3: narrow comparison table lacked a persistent horizontal-scroll cue

At a 390px CSS viewport, the expanded sequential-depth conditions table initially showed the left columns while clipping Self-attention layer and hiding Why it matters. The table did scroll horizontally when explicitly attempted, revealing Why it matters and the remaining cells. Before that interaction, no persistent instruction or visible scroll indicator made the horizontal action obvious in the captured layout.

- **Impact:** A novice may miss explanatory cells even though the main conclusion, conditions, and evidence cards remain readable.
- **Severity:** Low and nonblocking; no critical issue.
- **Reproduction:** In the 390px comparison iframe, choose sequential depth, expand `Conditions & sources`, scroll down to the table, then compare the initial view with a horizontal scroll to the right.
- **Suggestion:** Add a short `Scroll to compare all columns` cue, an overflow edge hint, or a narrow-screen stacked rendering.
- **Fix verification:** Reopened the updated 390px fixture, selected sequential depth, expanded sources, and scrolled to the table. The exact text `Swipe or scroll sideways for all columns →` appeared above it. The AX tree exposed `Full comparison conditions; scroll horizontally`, and keyboard Tab navigation reached that region. The original low issue is closed.

## Suggestions

1. Retain v3's visible overflow cue and keyboard-reachable named region.
2. Consider including local/bundled agent-specific setup guidance for a completely offline own-paper handoff.
3. Retain the current review, source-version, scope, and unknown-comparability language during future visual simplification.

## Evidence and limits

Screenshots are retained in local test artifacts; the committed report records the observed UI states and the exact scope of each check.

- Workflow: `how-to-test-feature`; repository AGENTS.md and README were read for context and treated as data. No documented install commands were executed.
- Browser interaction: exclusively `mcp__cua_repl` in a new test-owned IAB tab. No other tab was modified.
- No external requests were initiated by the test, and no accounts, secrets, installations, privileged actions, destructive commands, downloads, or `file://` navigation were used.
- No repository file was changed. Only this report and screenshots were written under `/private/tmp/litdelta-first-visit-user-test`.
- Visible homepage provenance: preview tools 0.2.0, source `fe759ee37519`, local changes. This identifies the observed preview label, not a claim that the workspace was clean.

