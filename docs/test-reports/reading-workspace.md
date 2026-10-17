# Personal reading workflow: implementation evidence

Issue: [#25](https://github.com/Chengkai-Zhu/litdelta/issues/25). Date: 2026-10-17.
Scope: ordered personal reading collection, source-linked Markdown note and
evidence check request. No release or public deployment.

## Expected and observed

| Reader task | Actual observation |
| --- | --- |
| Begin with an empty collection | **My reading 0** explains adding results or the suggested route; no note/check export controls appear |
| Keep a comparison | **Add both to My reading** adds its results; an existing selection is retained without duplicates |
| Change the order and remove work | Actual browser move-up and remove controls changed the list; keyboard focus followed the moved result |
| Reuse findings | Actual native Markdown download retained source v7, Table 2 locator, unknown cost, proposed review and the incomparable quality question |
| Hand checks to the agent | Actual native `.txt` download contained the exact note as a JSON string, version/context checks and a task-by-task response request |
| Keep complete data | Actual downloaded HTML, JSON and SVG metadata matched the full original map, not only the selection |
| Save, reopen and save again | Actual browser reopened the exported HTML; the reordered comparison selection was retained. Reopened surface HTML retained its selected result; removing it and downloading again saved an empty selection while retaining all 52 works / 54 results |
| Surface a real access limit | On the existing surface-code map, selecting `all-microwave-result` produced five follow-ups: one unextracted cost, one abstract-only full-text check and three original whole-map limits. The source remained DOI `10.1103/rqkg-dw31`, locator `Abstract`; it was not promoted to full-text evidence |
| Use a narrow viewport | At 390×844, actual add, move, remove, export and back controls worked. Testing found an inherited rule hiding all `.text-button` controls; limiting it to `#scope-button` repaired the affected controls |

The personal collection is explicitly separate from the complete searchable
**List view**. There is no paper cap. Automated tests also selected all 54
surface-code results and verified that every selected ID and evidence locator
traveled into the note without modifying the map.

## Reproducible software checks

```sh
python -m pytest
python -m ruff check src tests scripts skills
node --test tests/js/reader-state.test.cjs tests/js/reading-workspace.test.cjs
python scripts/verify_litdelta.py --out output/reading-acceptance
python scripts/build_preview.py --out output/reading-preview
python scripts/verify_preview.py --directory output/reading-preview --out output/reading-preview-check.json
```

Observed locally: 180 Python tests; 19 Node tests; Ruff PASS; 21/21 software
acceptance controls; complete preview and archive verification PASS. A local
acceptance run initially failed the `litdelta` alias because the environment
still had old 0.1.0 installation metadata. Reinstalling the current checkout
with `python -m pip install --no-deps -e .` supplied its existing console alias;
the rerun passed. This was a local development install, not a published release.

The Node suite executes production collection, export, checklist and control
handlers. Negative controls include invalid/stale IDs, duplicates, malformed
preferences, empty selections, hostile Markdown/JSON-script strings, missing
conditions, limited source access, unresolved excerpt matches and clipboard
failure. Copy success is reported only after the clipboard promise resolves;
failure selects the exact note for manual copying. Actual clipboard bytes were
not independently established in this browser pass; native downloads were.

An independent fresh-context review found no Critical/Important/Minor issues.
Its Git harm-signals gate passed. Generated previews, screenshots and native
downloads were kept outside the repository, not added to the source tree.

## Actual downloaded artifacts

The local handoff folder is
`D:\research_lineage\product-review-20261017\reading-artifacts`.
`verification.json` records 18 PASS checks and full hashes for ten native
downloads. These fingerprints identify observed files; they do not authenticate
research claims.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `comparison-reading-notes.md` | 4,242 | `0093182f37d909c845ec28a31ec2725aba469d8e69c548220c1b0fe51d2b0965` |
| `evidence-check-request.txt` | 4,959 | `bab71e19049e7e3c8c1717b1348399a334982f2f4267724f1cf2dad11a1e0a2a` |
| `surface-reading-notes.md` | 4,762 | `203c80028bd226572d7f49d55feb3dad0bd7a751be6f5c5dd99ff9ec26453fc6` |
| `surface-saved.html` | 358,197 | `629643f0014291b3f3aefbebbb9456cbb934fef9e86705984eb7b260b7ae9e87` |
| `surface-saved-again.html` | 358,175 | `bef8f2cdf0ea9a6331468403f7020d2c49b0ceafef88f7c1eb2db811b6c3d672` |

The comparison downloads exercised the first/revised candidates; the surface
downloads exercised the final implementation including the mobile repair. The
local final preview manifest honestly records the base revision and dirty tree
used to build it. CI artifacts identify the submitted commit independently.

## Limits

These are software and agent-operated browser observations, not a participant
study. Research productivity, adoption and GitHub stars are unmeasured. Real
external review in #10 remains open. The existing surface research run is still
PARTIAL; this reader work neither fills its full-text gap nor substitutes for a
new clean-agent paper-seed run. Issue #12 remains open, including the separate
host-side `start` rejection diagnosis. No scientific review status was changed.
