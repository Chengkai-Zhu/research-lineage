# Attention: a scoped result-comparison reading example

This is a reading task within one pinned paper. It is not a completed field
history or the fresh research execution required by #12. Its research cutoff stays
at the actual authoring date, 2026-10-17. Source corpus and display size are separate.

Canonical input:
`src/research_lineage/data/attention-comparisons.json`. Build it with
`litdelta demo --example comparisons --out output/comparisons`.

## Source and access record

[Attention Is All You Need, arXiv v7](https://arxiv.org/html/1706.03762v7),
published 2023-08-02; [version history](https://arxiv.org/abs/1706.03762)
records first publication on 2017-06-12. The authoring agent accessed the primary
HTML and inspected Sections 1, 3, 4/Table 1, and 6.1/Table 2 on 2026-10-17.
Section locators are stored separately from the pinned URL.

Annotations are original summaries and explicit editorial comparisons. Two short
excerpts total 23 words from this source; full text and figures are not redistributed.
The source retains its copyright and arXiv non-exclusive distribution license.
No automated local full-text match is claimed: the example has no stored match
reports. A source check is separate from independent scientific review; every
result, relationship, and comparison remains proposed.

## Reader tasks and expected answers

| Question | Expected answer and decisive source |
| --- | --- |
| Which layer needs fewer sequential operations? | The declared Table 1 layer comparison has O(n) versus O(1) depth. Open `c-parallel-depth`; keep its all-input-positions-available regime. |
| Is the total-work conclusion the same? | Keep n and d visible. Table 1 lists O(n d²) and O(n² d); Section 4 identifies n < d. Open `c-total-work`. |
| Does the layer argument establish parallel output generation? | The selected tasks differ; Section 3 conditions each generated output on previous outputs. Open `c-decoding`. |
| Does the layer bound establish better translation quality? | Operation counts and the Table 2 empirical BLEU score use different criteria. Open `c-quality`; inspect each result separately. |

The same paper supplies four distinct result IDs and several questions for one
ordered pair. Their diagram positions do not establish a chronological sequence.
The sequential-depth relation is limited to the explicit Table 1 metric; it does
not assert an unconditional improvement in training, inference, or total work.

## Limits and follow-up evidence

This curated example tests whether the reader can inspect a narrow comparison.
It does not establish search completeness, independent scientific validity, or
benefit to real users. The #14 contract and #12 fresh host execution supply the
research-workflow evidence. The actual surface-code run is now integrated, with
its recorded completion still PARTIAL due to an access gap; #10 remains the
independent review/user-study work.
The implementation report records actual agent authoring and browser-check effort.
