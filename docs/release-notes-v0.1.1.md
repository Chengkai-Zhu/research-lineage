# Research Lineage v0.1.1

This patch corrects acceptance failures found by independently re-auditing all
seven v0.1.0 issues and running a new research question from an empty draft.
The v0.1.0 tag remains unchanged. Issues #2, #3, and #4 were reopened and their
original failures reproduced before fixes were made.

## Corrected behavior

- A recorded review now requires full-text evidence from the exact cited work
  and version. A relationship uses its target result's version; unrelated full
  text cannot satisfy that requirement.
- SVG and Markdown exports retain scope, exclusions, source versions, evidence
  limitations, conditions, and recorded-review provenance. Both SVG exporters
  include the complete dataset as metadata and share one readable appendix.
- All generated filenames and existing file aliases are checked before writing
  over an input. Revision proposals record collection-order changes. Imported
  report text remains literal rather than raw HTML/Markdown structure.
- Relationship details recover after empty filters, and the source index
  distinguishes cited versions from other recorded versions.

## A genuinely new question

The new worked map asks how neural machine translation progressed from fixed
vectors through learned attention to the Transformer. It contains six primary
papers, seven recorded versions, six results, six evidence records, and six
proposed relationships. Pinned PDF sections were read and documented; no expert
signoff or exhaustive retrieval claim is made.

Download `research-lineage-nmt-example.zip` and open `map.html`. The original
QSP/QSVT draft remains available in `research-lineage-demo.zip`.

## Validation

The corrected suite collects 82 tests. The restricted local Windows sandbox
passes 79 and skips three hard-link creation cases, with 97% Python line coverage.
GitHub CI passes all 82 tests on each Windows/Linux and Python 3.11/3.14 combination,
including those three hard-link cases.
Independent reviewers reran the original failing fixtures. Actual browser checks
covered keyboard access, the complete 6/6 reading route, condition comparisons,
multi-version sources, empty-filter recovery, and a measured 389 CSS px layout.
Actual HTML/SVG/JSON downloads after filtering to 2/6 results retain data equal
to the complete input. Repeated builds are byte-identical.

See [the verification record](https://github.com/Chengkai-Zhu/research-lineage/blob/v0.1.1/docs/verification.md)
and [new-question feature test](https://github.com/Chengkai-Zhu/research-lineage/blob/v0.1.1/docs/test-reports/test-feature-20261017-nmt.md).

## Downloads

- `research-lineage-skill-0.1.1.zip`: self-contained agent skill and Python runtime.
- `research_lineage-0.1.1-py3-none-any.whl`: install with `python -m pip install <wheel>`.
- `research_lineage-0.1.1.tar.gz`: source distribution with tests and worked examples.
- `research-lineage-demo.zip`: the QSP/QSVT draft, rebuilt with the corrected runtime.
- `research-lineage-nmt-example.zip`: the new question's full offline bundle and research log.
- `SHA256SUMS.txt`: release artifact checksums.

Python 3.11+ is required for CLI/skill commands. The viewer is self-contained.
This is a GitHub artifact release; no PyPI publication or two-host certification
is claimed. Research annotations remain proposals for scholarly review.
