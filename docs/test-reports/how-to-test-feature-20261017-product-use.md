# Feature Test Report: LitDelta

**Date:** 2026-10-17 15:24 Asia/Shanghai
**Project type:** Offline research-map web reader and research-agent skill handoff
**Features tested:** Personal research request; comparison note export and clipboard feedback; comparison/map state preservation; 390px responsive layout
**Use Case:** ephemeral
**Profile:** ephemeral returning researcher
**Expected Outcome:** A researcher who has seen a LitDelta example can prepare a request for their own paper and journal club, then carry an authored comparison into Markdown notes with its conditions, source pins, review status and limits intact.
**Verdict:** pass
**Critical Issues:** 0

## Summary

| Feature | Discoverable | Setup | Works | Expected Outcome Met | Doc Quality |
|---------|-------------|-------|-------|---------------------|-------------|
| Personal research request | yes | yes, existing local preview | yes | yes | good |
| Save this explanation / Copy Markdown | yes | yes, existing local preview | yes | yes | good |
| Comparison/map state preservation | yes | yes, existing local preview | yes | yes | good |
| 390px responsive check | yes | yes, local development iframe | yes | yes within tested interactions | good |

This is an agent-simulated user test of a working local interface. It is not a participant study, evidence of actual adoption, an independent scholarly review, or validation of the scientific claims. The authored example remains awaiting scholarly review.

The desktop flow ran against `http://127.0.0.1:8792/product-use-v1/`. The final 390px check used `product-use-v2`, whose runtime is unchanged apart from the product homepage link in the note footer. That footer was observed in the v2 note. All browser interactions used a dedicated IAB tab through `mcp__cua_repl`.

## Per-Feature Details

### Personal research request

- **Role:** A returning researcher familiar with one example, preparing a journal club and wanting to start from a public paper or a Chinese research question.
- **Use Case:** Turn the researcher's own input and reading goal into a concrete handoff to their research agent.
- **What they tried:** Found the landing-page personal-input section; tested the empty state; entered `https://arxiv.org/abs/1706.03762v7`; chose **Prepare a journal club**; opened **Preview request**; copied the request; replaced the paper with `表面码量子存储的逻辑错误率随码距如何变化？`; changed the goal to **Compare approaches** in the 390px check; cleared the input.
- **Discoverability:** The header's **Use your own paper** and section heading led directly to the form. README instructions matched the interface.
- **Setup:** Existing preview was sufficient. **How to set it up** exposes extract-skill, copy-request and open-generated-map steps, plus Python 3.11+ and agent research-tool prerequisites. Installation was intentionally outside this test.
- **Functionality:** Empty input visibly disabled **Copy research request**. The exact public version link and Chinese question appeared in the preview. Journal-club and comparison goals changed the first task paragraph. Copy displayed **Copied. Paste it into your research agent.**; the browser clipboard matched the preview. Editing the input and changing the goal cleared the old success message and refreshed the request. Clearing the input emptied the request and disabled copying.
- **Expected vs Actual Outcome:** Met. The interface states that input stays in the tab and tells the researcher to take the request to an agent. It did not show a completed research result or imply the submitted input had already been researched. The request explicitly asks the agent to resolve identity, bound scope and retain gaps.
- **Blocked steps:** Actual agent execution, skill installation and opening external installation or paper links were not attempted, by the authorized test scope.
- **Friction points:** No concrete first-use defect observed on this path. Actual usefulness of a generated personal research map remains outside this interface test.
- **Doc suggestions:** None required for the tested path.

### Save this explanation and Markdown handoff

- **Role:** The same researcher preparing a journal-club outline and wanting to keep a comparison with its evidence boundary.
- **Use Case:** Export the selected explanation without stripping its conditions or uncertainty.
- **What they tried:** Opened the authored comparison from **Open the example**; chose **Save this explanation** for `c-parallel-depth`; copied Markdown; closed the note; selected the quality question (`c-quality`); opened and copied its note. Repeated the quality-note action in the final v2 build at 390px.
- **Discoverability:** **Save this explanation** sits next to the selected answer. The dialog explains that conditions, sources, review status and map gaps travel together.
- **Setup:** No installation required for reading or copying.
- **Functionality:** The depth note contains the selected question, layer-level condition, separate-work/quality caution, authored assessment and outcome, review status, compared results, pinned arXiv v7 (2023-08-02) sources, Table 1/section locators, recorded source-check dates, unchecked local text-match status, map scope, field-history exclusion and known gaps. **Copy Markdown** displayed **Copied. Paste it into your notes or journal-club outline.** and clipboard content matched the note. `c-quality` retains **incomparable; outcome: not assessed**, **editorial inference**, and the unextracted cost **Not extracted**. It preserves the distinction between operation counts and BLEU. The final v2 footer contains the product homepage link.
- **Expected vs Actual Outcome:** Met. The comparison is useful as an authored, source-linked note while retaining the fact that it awaits independent scholarly review. No new scientific checking was performed by saving it.
- **Blocked steps:** An actual browser-file download was not attempted. Read-only link inspection established a local `blob:` URL and `download="comparison-c-parallel-depth.md"`; this verifies link semantics only, not successful file saving. External paper links were not opened.
- **Friction points:** No concrete first-use defect observed. The full note is deliberately longer than the on-screen answer because it includes evidence and limits.
- **Doc suggestions:** None required for the tested path.

### Comparison and map state preservation

- **Role:** The same researcher alternating between a concise comparison and its underlying evidence.
- **Use Case:** Close a saved-note dialog and continue inspecting the same research map.
- **What they tried:** Closed depth and quality notes; checked selected question and URL; used **See these on the map** for quality; expanded **PAPER & VERSION** and **THE EVIDENCE**; returned to **Compare**, opened and closed the note, then returned to **Explore map**.
- **Discoverability:** Comparison links and reading-mode controls support the return path.
- **Setup:** Existing preview only.
- **Functionality:** Closing each note restored its selected comparison and unchanged `#comparison=c-parallel-depth` or `#comparison=c-quality` URL. Focus returned to **Save this explanation**. After the note round trip, **Explore map** retained the **Translation quality** inspector and both expanded paper/version and evidence sections, including the precise EN-DE Table 2 locator. The map mode URL became `#explore` as expected for that reading-mode action.
- **Expected vs Actual Outcome:** Met. Saving did not erase the reader's selected explanation or later evidence-inspection state.
- **Blocked steps:** None within scope.
- **Friction points:** None observed.
- **Doc suggestions:** None required.

### 390px responsive development check

- **Role:** The same researcher using a narrow browser layout.
- **Use Case:** Read the selected comparison and copy a personal research request or Markdown note at a narrow width.
- **What they tried:** Used a test-created local harness with separate 390px by 844px CSS iframes for the final v2 homepage and `c-quality` comparison. Inspected the initial layouts, entered a Chinese question, chose the journal-club goal, copied the request, opened the saved note, copied Markdown and closed it. Changed goal and cleared input afterward.
- **Discoverability:** The narrow header retained **Use your own paper**. Comparison questions became a labeled select control. Save/copy controls and close button remained visible and usable when reached.
- **Setup:** Harness at `/private/tmp/research-lineage-issue20/output/product-use-responsive-test.html`. This is a local CSS viewport check, explicitly labeled **not device emulation**.
- **Functionality:** Screenshots showed legible wrapping, usable form controls and a contained note dialog. The rendered document width and scroll width were both 390px for each iframe, with no horizontal page overflow. Clipboard success was visible for both copy actions. Closing returned to the quality comparison. Goal changes and clearing continued to reset stale request state.
- **Expected vs Actual Outcome:** Met for tested interactions. Real mobile-device input, native download behavior and a full accessibility audit were not tested.
- **Blocked steps:** A Playwright click inside the iframe returned a browser-tool targeting error. The same visible control worked through the tool's documented accessibility action, after a fresh state read. This was not counted as a product defect.
- **Friction points:** No concrete product friction observed in the checked narrow layout.
- **Doc suggestions:** None required.

## Issues Found

No blocking, high-severity or other concrete product issue was found in the authorized paths. **Critical Issues: 0.**

The first local-origin browser-access attempt timed out in automatic approval review. A supported retry exposed that explicit IAB visibility options are unavailable in subagents; creating a dedicated tab with default visibility succeeded. These recovered environment/tool limitations are separate from the product verdict.

## Suggestions

1. Preserve the current distinction between request preparation and actual research execution.
2. Preserve the note's explicit review state, unknown values and scope exclusions as the feature expands.
3. Use actual researchers and their own papers to evaluate adoption and journal-club usefulness; this simulation establishes that the tested interface path works, not that users will adopt it.

## Evidence retention

The local run retained five browser screenshots and copied Markdown notes in its
test-evidence directory. Generated screenshots and scratch notes are not source
artifacts and are not included in this repository. The observed interactions and
limits are recorded above; no actual download or participant result is claimed.

Only test artifacts and an ignored responsive harness were written. No product
source changes, external account actions, installations, privileged commands or
destructive commands were performed by the simulated tester.
