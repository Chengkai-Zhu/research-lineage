# From sentence vectors to attention

A new research question authored from an empty draft during the v0.1.0 acceptance
audit, independently of the built-in QSP/QSVT example.

**Question:** How did neural machine translation progress from fixed-length
encoding through learned attention to the Transformer?

```sh
research-lineage validate examples/nmt-attention/map.json
research-lineage build examples/nmt-attention/map.json --out output/nmt
research-lineage compare examples/nmt-attention/map.json r-convs2s r-transformer
research-lineage review examples/nmt-attention/map.json --out output/nmt-review.md
```

Open `output/nmt/map.html`. The six-step teaching route groups fixed-vector models
together; the timeline itself uses first-submission dates. The map contains six
primary papers, seven recorded versions, six results, six evidence records, and
six proposed relationships. It is a bounded reading map, not an exhaustive history
or a benchmark leaderboard. No external reviewer has signed off.

## Research log

Checked on 2026-10-17, with a literature cutoff of 2017-12-31. The input began with
the released standalone skill's `init` command; both works and results were empty.
An attempted build of that empty input failed as expected. Sources were then
collected and annotated with the host agent's research tools. The CLI does not
perform automatic discovery or full-text extraction.

[Neubig's tutorial](https://arxiv.org/pdf/1703.01619v1), sections 8.2–8.4, provided
orientation. Reference tracing then led to these pinned primary versions. Their
arXiv submission histories and the indicated PDF sections were inspected:

| Work | First submission | Version read | Evidence locator |
| --- | --- | --- | --- |
| Cho et al., RNN Encoder-Decoder | 2014-06-03 | [1406.1078v1](https://arxiv.org/pdf/1406.1078v1) | Sections 2.2 and 3.1, PDF pp. 2–4 |
| Bahdanau et al., joint alignment | 2014-09-01 | [1409.0473v1](https://arxiv.org/pdf/1409.0473v1) | Sections 1–3, PDF pp. 1–4 |
| Sutskever et al., sequence-to-sequence | 2014-09-10 | [1409.3215v1](https://arxiv.org/pdf/1409.3215v1) | Abstract and Section 1, PDF pp. 1–2 |
| Luong et al., attention variants | 2015-08-17 | [1508.04025v1](https://arxiv.org/pdf/1508.04025v1) | Sections 3.1–3.2, PDF pp. 3–4 |
| Gehring et al., ConvS2S | 2017-05-08 | [1705.03122v2](https://arxiv.org/pdf/1705.03122v2), dated 2017-05-12 | Sections 2, 3.3, and 4.1, PDF pp. 2–5 |
| Vaswani et al., Transformer | 2017-06-12 | [1706.03762v1](https://arxiv.org/pdf/1706.03762v1) | Sections 2, 3.2.3, and 4; reference 9 |

Cho's v1 has six authors; the map preserves that version's author list. ConvS2S v1
is recorded for chronology, while v2 supports the result and evidence because
Transformer v1 explicitly cites that version. This distinction exposed the old
viewer's source-index bug and now serves as a regression example.

## Interpretation boundaries

Five edges record explicit architectural connections in the later paper. The
Luong-to-ConvS2S `generalizes` edge is explicitly an **editorial inference** about
multi-step attention, not a formal containment theorem. The Cho-to-Sutskever edge
records the latter paper's statement of parallel development, not derivation.

The Transformer cost entry is a per-layer comparison from Table 1, not an assertion
about total training or autoregressive decoding. Different language pairs,
tokenization, model sizes, and decoding settings prevent a numerical cross-paper
performance claim here. Unknown costs remain `null`.

Earlier neural language models, ByteNet, GNMT, Neural GPU, subword methods,
attention outside translation, and post-2017 work are excluded from this small
map. The source links and original paraphrases are included; paper PDFs are not
redistributed. See [the actual feature test](../../docs/test-reports/test-feature-20261017-nmt.md).
