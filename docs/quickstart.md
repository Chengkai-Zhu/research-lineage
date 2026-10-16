# Build your first research map

## Open the example

Download `research-lineage-demo.zip` from [Releases](https://github.com/Chengkai-Zhu/research-lineage/releases/latest),
extract it, and open `map.html`. It works offline, with no server or account.
The sample is a bounded, abstract-grounded research draft, not an expert-certified review.

## Use the Python package

Python 3.11 or newer is required. From a checkout:

```sh
python -m pip install .
research-lineage demo --out output/demo
```

The output contains `map.html`, `map.svg`, `map.json`, and `review.md`.
`python -m research_lineage` is equivalent to `research-lineage`.

## Use the standalone skill

Download `research-lineage-skill-0.1.0.zip` from the release. Extract the contained
`research-lineage` directory into your host's skills directory, for example
`~/.agents/skills/` for Codex or `~/.claude/skills/` for Claude Code. On Windows,
use the equivalent folder under your user profile. Preserve existing skills.
Restart/reload the host's skill discovery if required by your host.

The ZIP includes the runtime. Copying only `SKILL.md`, or copying the unbuilt skill
folder out of the repository, does not include that runtime. Within a full clone,
the skill runner automatically uses the repository's canonical source.

Try a prompt:

> Use research-lineage to trace how quantum signal processing developed into
> QSVT. Focus on changes in input models and assumptions. Give me an interactive
> offline map and make every relationship's evidence inspectable.

The skill uses your host's research tools. It does not include model credentials,
full-text subscriptions, or an autonomous search engine.

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

- Click a **result** for its statement, source version, and conditions.
- Click a **connection** for the specific evidence and whether the relationship
  is author-stated or an editorial inference.
- Use **Compare settings** before treating a later work as an improvement.
- Follow the **reading route**, or use the accessible **reading list**.
- Check **Scope & sources** for coverage, omissions, and the publication cutoff.
- Export the complete map as HTML, editable SVG, or JSON. Active filters do not
  silently delete data from exports.

Version 0.1 supports English viewer controls and Unicode content. It does not fetch
papers, reconstruct historical snapshots, authenticate reviewers, or establish
scientific correctness automatically.
