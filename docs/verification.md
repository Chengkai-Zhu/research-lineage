# Verification record

Dates: 2026-10-16–17. This report distinguishes executable software checks from
scientific validation. It does not certify the mathematical content of the sample.

The [v0.2 workflow record](test-reports/skill-first-workflow.md) covers the later
skill-first inputs, reading interface, research tools and bilingual documentation.
The release-specific observations below remain historical records.

## Acceptance re-audit and corrections

The immutable v0.1.0 commit `4b64f0d15fdc743bd1afa0370ccf375b9b4d691d` was
re-audited against all seven issue bodies and comments, using separate review
contexts. The published assets were downloaded and tested, rather than assuming
the current checkout represented the release.

| Issue | v0.1.0 verdict | Corrective result |
| --- | --- | --- |
| #1 Product scope and plan | Pass | All 28 original task dispositions accounted for |
| #2 Contract and validation | Fail | Version-bound full-text review evidence; original invalid fixtures now reject |
| #3 Portable bundles | Fail | Complete static provenance, all output-name guards, safe Markdown text, ordered revision diffs |
| #4 Inspectable viewer | Fail | Relationship filter recovery and explicit source-version index |
| #5 QSP/QSVT sources | Pass | Eight pinned primary URLs and version/date metadata rechecked |
| #6 Standalone skill | Pass | Released ZIP runs outside checkout, including with site packages disabled |
| #7 Release assets and CI | Pass | Four archive digests match; released wheel/skill produce the released demo; four CI jobs pass |

Passing packaging and the original 62 tests did not establish complete product
acceptance. Issues #2–#4 were reopened for their reproduced failures. The original
tag remains unchanged; the corrections are shipped as v0.1.1.

The corrected local suite collects **82 tests: 79 pass and 3 skip** in the Windows
sandbox. The three skips are hard-link creation restrictions; the corresponding
checks remain enabled on ordinary filesystems. Measured Python line coverage is
**97%**. This is not JavaScript interaction coverage or scientific certification.

The [patch PR CI](https://github.com/Chengkai-Zhu/research-lineage/actions/runs/38935542860)
then passed **all 82 tests on each of Windows/Linux and Python 3.11/3.14**, including
the three hard-link cases that the local sandbox could not create.

The [new-question feature test](test-reports/test-feature-20261017-nmt.md) records
the full NMT authoring and browser run, including 6/6 route steps, keyboard access,
actual 389 CSS px layout, multi-version links, and downloads after filtering to
2/6 results. All three downloaded formats retain data equal to the input. The
independent #2/#3 reviewers reran their original failing fixtures against the fix.

## Original v0.1.0 observations

The remaining record below describes the original release checks. It is retained
to make their limits visible; the stronger re-audit above supersedes the original
implication that those checks alone established complete acceptance.

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
