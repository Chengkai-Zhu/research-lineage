[English](README.md) · [简体中文](README.zh-CN.md)

# LitDelta

**See how research moves forward.**

[![CI](https://github.com/Chengkai-Zhu/research-lineage/actions/workflows/ci.yml/badge.svg)](https://github.com/Chengkai-Zhu/research-lineage/actions/workflows/ci.yml)

An **agent skill** that turns a research topic or one paper into a clear, source-grounded reading history. Explore what each result changes, under which conditions, and where the evidence comes from. Give your agent one sentence; receive an interactive map you can keep, inspect and share offline.

LitDelta is the product name. Installation continues to use `research-lineage`;
both `litdelta` and `research-lineage` invoke the same local tools. The existing
skill name and `python -m research_lineage` remain supported.

[Try LitDelta in your browser](https://chengkaizhu.site/research-lineage/) ·
[Download the complete offline collection](https://chengkaizhu.site/research-lineage/offline.zip) ·
[Get the current preview skill](https://chengkaizhu.site/research-lineage/downloads/research-lineage-skill-0.2.0.zip)

The browser entry offers a focused result comparison, an author-linked reading
history, and the actual 52-paper research run with its PARTIAL status intact.
Reading needs no installation. The preview skill is built from the same source;
it is separate from the latest tagged release.

Try the new, explicitly scoped result-comparison example after installing the
checkout (it is not a completed field-history search):

```sh
litdelta demo --example comparisons --out output/comparisons
```

Open `output/comparisons/map.html` to compare parallel layer depth, total work,
generation dependencies, and translation quality. [Source notes and reader tasks](examples/attention-comparisons/README.md)
explain the distinction. [Preview build and verification](docs/litdelta.md#browser-preview)
documents how to reproduce the site and check downloaded files against its manifest.

> Please trace the development of quantum signal processing.

Or just supply a paper link, DOI, title or PDF and ask for the history behind it.

[Get the skill](docs/quickstart.md#use-the-standalone-skill) · [Worked histories](#worked-histories) · [Research tools](docs/research-tools.md)

The workflow below is available on `main`; **0.2 is not released yet**. The latest published bundle is [v0.1.1](https://github.com/Chengkai-Zhu/research-lineage/releases/tag/v0.1.1).

![The reading overview, with details revealed on demand](docs/assets/reading-overview.png)

## Understand first. Explore when ready.

- **Begin with the story.** A short overview and source-linked turning points explain what changed.
- **Know what to read next.** Follow a suggested route, then explore the complete map.
- **Check the reasoning.** Open a connection, its exact paper version, evidence and assumptions when you need them.
- **Keep the whole result.** One offline HTML, plus SVG, JSON and a review report. Filters never discard exported evidence.

The host agent does the research using its search and document tools. The bundled Python toolkit prepares inputs, validates records and builds the reading experience. No account or paid service is required by the local core. Python 3.11+ is needed for the skill; the exported HTML needs only a browser.

## Use the skill

Build the current self-contained skill with Python 3.11+:

```sh
git clone https://github.com/Chengkai-Zhu/research-lineage.git
cd research-lineage
python scripts/package_skill.py --out dist
```

Extract the `research-lineage` folder from `dist/research-lineage-skill-0.2.0.zip` into your agent's skill directory; see the [installation guide](docs/quickstart.md). Then give it a topic or paper:

> Use research-lineage to trace the history of quantum signal processing.

> Use research-lineage with https://arxiv.org/abs/2408.13687v1 and explain the developments behind this paper.

The skill chooses a bounded scope and follows your language. You do not need to supply IDs, dates, a bibliography or JSON. A paper title is resolved before its identity is asserted. Private attachments stay local unless you explicitly authorize otherwise. Viewer controls are currently English; research content can be Chinese.

Research coverage has no default paper quota. The host follows references and
follow-ups, records candidate decisions and source-grounded branches, and keeps
the researched corpus available behind the concise overview. The
[research-run audit](docs/research-tools.md#recorded-research-coverage) reports
missing evidence as partial or failed; it does not certify scientific completeness.

## Worked histories

| Start | Reading history | Evidence boundary |
| --- | --- | --- |
| A topic | [QSP to QSVT](docs/sources.md) | Eight-paper, abstract-grounded draft |
| A new question | [Sentence vectors to attention](examples/nmt-attention/README.md) | Six primary papers with section-level checks |
| One pinned paper, fresh agent | [Surface-code research run](docs/test-reports/surface-code-rerun/README.md) · [Interactive notebook](docs/test-reports/surface-code-rerun/report.html) | 52 works; real search/candidate logs; PARTIAL because one central full-text branch remains unresolved |
| Authored illustration | [Surface-code quantum memories](examples/surface-code/README.md) | Four-work reading path; single-input research acceptance reopened in #12 |

These are selected histories with proposed annotations. Source checks and passing software tests do not establish scientific truth or independent expert review. Genuine external review and participant studies remain [open work](https://github.com/Chengkai-Zhu/research-lineage/issues/10).

<details>
<summary>Use the Python tools directly</summary>

```sh
git clone https://github.com/Chengkai-Zhu/research-lineage.git
cd research-lineage
python -m pip install .
research-lineage demo --out output/demo
```

Open `output/demo/map.html`. The demo requires no network or model key.

```sh
research-lineage start "quantum signal processing" --out output/topic
# The host researches and authors the empty draft; start does not fabricate a map.
research-lineage validate output/topic/map.json
research-lineage build output/topic/map.json --out output/topic/reading
```

[Data guide](skills/research-lineage/references/data-guide.md) · [Discovery, identity and evaluation commands](docs/research-tools.md)

</details>

## Contribute

Correct an assumption, improve a source anchor, or add a carefully checked reading history. Contributions should preserve uncertainty and source versions.

```sh
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests scripts skills
node --test tests/js/reader-state.test.cjs
python scripts/package_skill.py --out dist
```

[Design](docs/design/skill-first-reading.md) · [Verification](docs/test-reports/skill-first-workflow.md) · [Roadmap](docs/roadmap.md) · [Contributing](CONTRIBUTING.md)

If it helps you understand a field, sharing your map or starring the repository helps others find it.

Viewer development tests use Node.js 18+ built-ins. Node is a development tool;
the offline Python core and exported reader do not require it.

## License

[Apache-2.0](LICENSE). Papers retain their own copyrights; the repository contains original annotations and source links, not redistributed papers.
