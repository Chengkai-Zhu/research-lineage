# Verification record

Dates: 2026-10-16–17. This report distinguishes executable software checks from
scientific validation. It does not certify the mathematical content of the sample.

## Local tooling

Windows, Python 3.14.4. Development dependencies are pinned in `pyproject.toml`.

```sh
python -m ruff check src tests scripts skills
python -m pytest --cov=research_lineage --cov-report=term-missing --cov-report=xml
python scripts/package_skill.py --out dist
python -m build
```

The 62 tests pass. Measured Python line coverage: **96%**. This includes contracts,
negative inputs, version references, unsafe links, markup escaping, deterministic
builds, empty-draft refusal, setting comparisons, revision diffs, overwrite guards,
and an extracted skill running in Python isolated mode outside the checkout.
The host's skill validator also accepts the skill.

The final wheel was installed into a separate target directory with `pip --no-deps
--no-index`. Its runtime generated the four demo files outside the checkout using
Python isolated mode with site packages disabled. The wheel was built from the
source distribution, which includes the tests, schema, scripts, and skill sources.

The local sandbox cannot use the default pytest temporary directory. Local checks
used a fresh `--basetemp output/test-run-N` inside the workspace; this is an execution
environment constraint, not a runtime requirement for users.

## Browser observations

The actual generated HTML was inspected in a Chromium-based browser:

| User action | Observed behavior |
| --- | --- |
| Open example | Eight results, six relationships, draft status, and cutoff are visible. |
| Select a result | Evidence, pinned source link, publication/version dates, and unknown settings appear. |
| Activate a relationship with Enter | The inspector shows the relationship's basis, evidence, and comparability. |
| Compare settings | Different reported values are highlighted; missing values remain not extracted. |
| Search for a nonexistent result | Zero results and an actionable reset appear; no stale result is presented. |
| Start route and move forward | Progress advances and the corresponding result/source is selected. |
| Narrow screen (389 CSS pixels) | The page stays within its viewport; the graph scrolls within its own pane. |
| Switch to reading list | All results are available as readable text controls. |
| Export JSON after filtering to Foundations | The downloaded file retains all eight results, six relationships, and eight evidence records. |
| Export SVG | The saved file parses as SVG, retains all eight nodes, and includes the coverage, known gaps, and source index. |
| Export HTML | The saved file retains eight results and six relationships, closed dialogs, embedded assets, and the offline content policy. |

Browser download-event waits were intermittent, so saved files were checked directly.
The browser automation environment blocks `file:` navigation; reopening the downloaded
HTML through that surface was not tested. The generated viewer was exercised over a
local server, and standalone assets were inspected without adding network dependencies.

The screenshot in `docs/assets/map-preview.jpg` is captured from the running output,
not a design mockup. Reduced-motion styling is implemented; no independent assistive
technology audit or participant study is claimed.

## Boundaries

The sample's sources were checked at metadata/abstract level. No external expert
review, autonomous search benchmark, independent extraction benchmark, or complete
historical reconstruction has been performed. The skill's bundled commands are
tested; this is not a claim of completed user field tests on two different agent hosts.

GitHub CI passed all four Windows/Linux and Python 3.11/3.14 jobs in
[the initial release-candidate run](https://github.com/Chengkai-Zhu/research-lineage/actions/runs/38929251145).
See [current workflow results](https://github.com/Chengkai-Zhu/research-lineage/actions/workflows/ci.yml)
for subsequent commits. Coverage uploads to Codecov are configured but optional; a
service-account connection may be needed. There is no unverified Codecov badge.
