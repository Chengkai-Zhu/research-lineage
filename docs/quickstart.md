# Build your first research map

## Open the example

Try [LitDelta online](https://chengkaizhu.site/research-lineage/) without installing
anything, or [download all three reading examples](https://chengkaizhu.site/research-lineage/offline.zip).
Extract the archive and open `START-HERE.html`. Choose a focused comparison,
follow shared author names, or inspect the actual research run with its PARTIAL
status intact. Every example also has its own standalone `map.html`.

Build the current example using the checkout commands below, then open
`output/demo/map.html`. It works offline, with no server or account.
The sample is a bounded, abstract-grounded research draft, not an expert-certified review.

Version 0.2 is available on `main` but has not been released. The latest published
[v0.1.1 bundles](https://github.com/Chengkai-Zhu/research-lineage/releases/tag/v0.1.1)
use the earlier interface.

## Use the Python package

Python 3.11 or newer is required. From a checkout:

```sh
python -m pip install .
research-lineage demo --out output/demo
```

The output contains `map.html`, `map.svg`, `map.json`, and `review.md`.
`python -m research_lineage` is equivalent to `research-lineage`.

## Use the standalone skill

You can [download the current preview skill](https://chengkaizhu.site/research-lineage/downloads/research-lineage-skill-0.2.0.zip)
directly from the product page. It includes its Python runtime and comparison
sample; this preview is not a tagged package release.

Build the current skill from the repository root using Python 3.11+:

```sh
python scripts/package_skill.py --out dist
```

No package installation is required for this build command. Extract the contained
`research-lineage` directory into your host's skills directory, for example
`~/.agents/skills/` for Codex or `~/.claude/skills/` for Claude Code. On Windows,
use the equivalent folder under your user profile. Preserve existing skills.
Restart/reload the host's skill discovery if required by your host.

The generated archive is `dist/research-lineage-skill-0.2.0.zip`; a GitHub Release
for this version is intentionally deferred.

The ZIP includes the runtime. Copying only `SKILL.md`, or copying the unbuilt skill
folder out of the repository, does not include that runtime. Within a full clone,
the skill runner automatically uses the repository's canonical source.

Try a prompt:

> Please trace the development of quantum signal processing.

Or supply one paper:

> Use research-lineage with https://arxiv.org/abs/2408.13687v1.

Chinese works too: “请整理 quantum signal processing 这个方向的发展历史。”
The host chooses a bounded scope, resolves the sources, authors the map and
opens the result. You do not need to provide IDs, dates or JSON. A bare paper
title is resolved before its identity is asserted. Private PDFs stay local
unless you explicitly authorize another destination.

The overview and reading route are selections from the researched corpus, not
paper-count limits. The host records searches, candidate decisions and coverage
branches, checks follow-ups through the cutoff, and delivers the
[research record](../skills/research-lineage/references/research-record.md) with
the map. Unfinished research must be identified as partial.

The skill uses your host's research tools. It does not include model credentials,
full-text subscriptions, or an autonomous search engine.

## Prepare a topic or paper directly

```sh
research-lineage start "quantum signal processing" --out output/topic
research-lineage start "https://arxiv.org/abs/2408.13687v1" --out output/paper
```

This deterministic helper writes an empty `map.json` and a `research-brief.json`.
It does not perform research. The host uses its research tools and the
[data guide](../skills/research-lineage/references/data-guide.md) to populate the
map from checked sources. Optional explicit discovery and evaluation commands
are documented in [Research tools](research-tools.md).

## Author a map directly

```sh
research-lineage init "How did this research question evolve?" --id my-question --cutoff 2026-10-16 --out map.json
research-lineage schema --out map.schema.json
```

Choose the cutoff appropriate to your task. The initial file is a valid **empty
draft**. Populate it using [the data guide](../skills/research-lineage/references/data-guide.md)
and your checked sources. `build` refuses an empty map rather than substituting a demo.

```sh
research-lineage validate map.json
research-lineage build map.json --out output/my-question
research-lineage compare map.json result-a result-b
research-lineage review map.json --out review.md
research-lineage diff previous.json revised.json --out changes.json
```

Use a new output directory for each revision, or `build --force` to intentionally
replace only the four generated files. A build cannot overwrite its input map.
Diffs are proposals: the command does not alter either input.

## What to inspect

- Start with the **overview**, then select **Start reading** for the suggested route.
- Select **Explore map** for filters, comparisons and the full graph.
- Click a **result**, then expand the evidence sections for its source version and conditions.
- Click a **connection** for the specific evidence and whether the relationship
  is author-stated or an editorial inference.
- Use **Compare settings** before treating a later work as an improvement.
- Follow the **reading route**, or use the accessible **reading list**.
- Check **Scope & sources** for coverage, omissions, and the publication cutoff.
- Export the complete map as HTML, editable SVG, or JSON. Active filters do not
  silently delete data from exports.

Version 0.2 supports English viewer controls and Unicode research content. Explicit
discovery retrieves metadata/available abstracts, not unrestricted paper full text.
The tools do not reconstruct historical knowledge, authenticate reviewers, or
establish scientific correctness automatically.
