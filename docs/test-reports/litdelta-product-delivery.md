# LitDelta product delivery

Date: 2026-10-17. Issue: #20. PR: #22.
Public runtime revision: `958fcc5ba9c1f200d82f657870e1ef99a955b601`.
Later commits containing this report do not change that runtime.

## Delivered entry points

- [Product](https://chengkaizhu.site/research-lineage/)
- [Complete offline collection](https://chengkaizhu.site/research-lineage/offline.zip)
- [Current standalone skill](https://chengkaizhu.site/research-lineage/downloads/research-lineage-skill-0.2.0.zip)
- [Published manifest](https://chengkaizhu.site/research-lineage/manifest.json)

The homepage offers a one-paper comparison reader, a six-paper author-linked
history, and the actual 52-work surface-code research run. Each reader uses the
canonical runtime. The full collection includes the three map sets, review
reports, source notes, recorded audit, offline landing page and current skill.
The preview skill is distinct from a tagged release.

## Observed verification

| Evidence stream | Actual outcome |
| --- | --- |
| Local Python tests | 177 passed |
| Local Node preference/production-handler tests | 6 passed |
| Ruff, JavaScript syntax, Git whitespace checks | Passed |
| Known-input comparison acceptance | Software PASS, 21/21; actual research remains PARTIAL |
| Fresh-context code/policy review | GATE PASS; three Important state defects repaired; no unresolved Critical/Important |
| Simulated downstream user | Portable isolated execution and complete map/archive checks passed; not human-participant evidence |
| Windows/Linux × Python 3.11/3.14 | All four jobs passed |
| Explicit preview build and deployment | Both passed |
| Published files and offline ZIP | 21/21 availability/integrity rows passed; source revision matches reviewed runtime; clean source |

Actual publication run:
[39000869968](https://github.com/Chengkai-Zhu/research-lineage/actions/runs/39000869968).
The earlier run 39000684340 was cancelled before final publication so the fixed
source, rather than an earlier reading-state implementation, was delivered.

The public check actually executed:

```sh
python scripts/verify_preview.py --url https://chengkaizhu.site/research-lineage/ --out output/litdelta-public-958fcc5.json
```

Observed: `Preview: PASS`. The [retained JSON](litdelta-public-preview.json)
records the checked URL, UTC timestamp, each file result, clean source revision,
and the separately preserved research status. It verifies file integrity against
the manifest, not document authenticity or scientific correctness.

The [simulated-user report](how-to-test-feature-20261017-115450.md) records actual
isolated skill commands and complete archive checks at d0f225d. The final source
adds the independently reviewed inspector-close repair and its actual production
handler regression; final publication checks cover that corrected source.

## Browser observations and limits

Actual local HTTP browser actions exercised the product landing page, entry into
the supported sequential-depth question, selection of the total-work tradeoff,
expanded conditions/source excerpts, and the author deep link selecting Yoshua
Bengio consistently on both relevant works. An HTTP developer fixture containing
a known saved comparison preference, with no URL fragment, restored the correct
incomparable question; switching Overview then Explore ended at `#explore`.
This fixture was generated from canonical source and test data, not from a
downloaded page.

The reviewer reproduced a pre-fix contradictory saved view in a real browser and
read the downloaded HTML as text. It was not reopened or re-served to bypass
file-navigation restrictions. The actual inspector close handler was also
executed in a Node VM, including a history-write exception, to verify that it
closes the panel and clears its saved result selection.

After publication, browser inventory reported the public URL and the title
**LitDelta — See how research moves forward.** Interactive automation rebinding
timed out, so a full walkthrough on that public URL is not claimed. Direct
`file://` reopening also remains blocked by the browser tool's policy. These are
explicit manual verification limits; byte checks and Node tests do not establish
those browser actions.

## Research and release boundaries

The actual fresh run retains provenance/cutoff/source-trail PASS and research
completion PARTIAL. A central full-text access gap remains recorded. Source
versions, proposed review state, exclusions and full corpus remain available;
the reading route does not become a corpus quota.

No independent scholarly review, authenticated reviewer, exhaustive research
coverage, measured reader benefit or host-agent installation is claimed by
this delivery. The code is delivered through PR #22 and the public preview;
no merge or release tag was performed. Remaining manual browser acceptance and
the actual research outcome stay visible to reviewers.
