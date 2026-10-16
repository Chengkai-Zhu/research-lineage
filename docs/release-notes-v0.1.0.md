# Research Lineage v0.1.0

The first usable local release: trace a research question through results,
assumptions, and evidence, then share an interactive map as one offline HTML file.

## Included

- A portable agent skill with its Python runtime and data guide.
- A dependency-free Python CLI: `init`, `schema`, `validate`, `build`, `compare`,
  `review`, `diff`, and `demo`.
- Chronological lanes, inspectable connections, source versions, setting
  comparisons, guided reading, search, filters, and a text reading list.
- Self-contained HTML, editable SVG, JSON, and Markdown review reports.
- A checked eight-paper QSP/QSVT draft example, with six proposed connections.
- Product audit, three milestones, twelve verifiable issues, and contribution guidance.

## Downloads

- `research-lineage-demo.zip`: extract and open `map.html`; no installation needed.
- `research-lineage-skill-0.1.0.zip`: extract the skill into your agent's skills folder.
- `research_lineage-0.1.0-py3-none-any.whl`: install with `python -m pip install <wheel>`.
- `research_lineage-0.1.0.tar.gz`: Python source distribution.
- `SHA256SUMS.txt`: checksums of the release assets.

Python 3.11+ is required for CLI/skill commands. The exported viewer does not need Python.

## Verification and limitations

62 automated tests pass locally, with 96% Python line coverage. The portable ZIP
and installed wheel are tested outside the checkout. GitHub CI passes on Windows
and Linux with Python 3.11 and 3.14. The actual viewer was inspected for result and
relationship selection, comparison, route navigation, empty search, narrow screens,
and exported files. See the repository's verification record for the test boundaries.

The software is usable; the sample is still an abstract-grounded research draft.
No expert certification, comprehensive literature retrieval, automatic full-text
extraction, historical as-of reconstruction, or two-host field certification is claimed.
The skill uses the research capabilities of its host agent.
