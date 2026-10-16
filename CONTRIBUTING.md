# Contributing

A useful contribution can be one corrected assumption or one better evidence
anchor. Keep it small enough for another person to inspect.

1. Identify the result/relationship ID and the pinned source version.
2. Explain the current statement, the proposed correction, and the exact source
   locator. Separate what the author states from your interpretation.
3. Modify a copy of the map and run `research-lineage validate revised.json`.
4. Run `research-lineage diff previous.json revised.json --out changes.json` and
   include the relevant changes in the pull request description.
5. Leave scientific content proposed until actual external review has occurred.

Example: replace an abstract-only evidence entry with a checked full-text anchor.
Preserve its work/version identity, set `kind` to `full_text`, record the actual
theorem/section in `locator`, and explain the supported scope in `summary`.
This improves the evidence; it does **not** automatically make the result reviewed.

For code changes, install `.[dev]`, run Ruff and pytest, and inspect the demo in a
browser if the viewer changes. Regression tests should exercise a real behavior
or failure, not duplicate implementation text.

All code, original documentation, and original map annotations are Apache-2.0.
Underlying papers retain their own copyrights. Do not commit paper PDFs, copied
full text, private notes, credentials, caches, or claims of endorsement.
