# LitDelta implementation evidence

Date: 2026-10-17. Scope: issue #20 plus the owner's author/team color request.
Integrated base: `5055c21` (merged #14/#12 work in PR 21). This report records
software and agent observations; it is not independent scholarly review.

## Observed software results

| Check | Observed result |
| --- | --- |
| `python -m pytest -q` | 176 passed locally on Python 3.13 |
| `python -m ruff check src tests scripts skills` | Passed |
| JavaScript syntax checks for viewer and identity view | Passed |
| `python scripts/verify_litdelta.py --out output/litdelta-acceptance` | Software PASS, 21/21 known-input checks; research integration PARTIAL |
| Validate `output/litdelta-acceptance/controls/missing-comparison.json` | Native exit 2; missing comparison reference and persistent improvement context rejected |
| Curated example passed as `--research-manifest` with `--require-integration` | Native exit 2; research integration FAIL despite 20/20 independent software controls |
| Wheel/source distribution and portable skill | Built; both archives contain the identity view asset. The extracted skill ran with `python -I -S` and generated four results and four comparisons without site packages |

The verifier builds the actual fresh-run map with the same generic runtime and
preserves its input data. Its canonical audit reports provenance, cutoff and
source trail PASS, and research completion PARTIAL. The recorded central access
gap is retained. Closing an issue does not change that outcome. Original
SHA-bound research artifacts were not rewritten.

The acceptance report keeps browser checks MANUAL, publication PARTIAL and
participant evidence unavailable. An exit-zero software run does not promote
these other evidence streams. `--require-integration` demands a fully passing
research audit and therefore rejects the current partial outcome.

## Actual browser observations

The ChatGPT in-app browser opened generated localhost pages. Its observed viewport
was approximately 582 × 784 pixels. The following actions were actually exercised:

- Open the comparison overview and the sequential-depth explanation; expand
  condition rows, source excerpts, pinned versions and original annotations.
- Switch the same ordered result pair from sequential depth to total work with
  keyboard Down/Return. The explanation changes and the question selector retains
  focus. A saved `#comparison=c-quality` link restores the incomparable case.
- Reverse the result order. It shows an unassessed pair instead of inverting an
  improvement. Equal reported setting text remains an unknown comparison.
- Dismiss the dialog with Escape and return to the reading overview.
- Open the legacy NMT map with the new runtime. Switch the graph to author
  colors and follow Yoshua Bengio. The Cho and Bahdanau result nodes both have
  the identical `rgb(230, 159, 0)` color mark; the other four remain present in gray.
  The all-author view shows multiple collaboration marks on the same result.
- Open a clearly labeled synthetic group control. Both work/version assignments
  cite their own fixture evidence; team mode shows `rgb(0, 114, 178)` on both nodes.
  Group labels are not inferred from common authors. Invalid bindings are covered
  by separate negative tests.
- Expand a source card whose excerpt is
  `<script>document.title='INJECTED'</script>`. It appears literally and the page
  title stays **Engineering comparison controls · LitDelta**.
- Download the HTML through the running viewer's export menu. The captured file
  was 88,337 bytes and retained all four results and four comparisons, equal to
  the canonical example at the time of that check. This preceded the later color
  view changes; export preference restoration still needs a final manual check.

Screenshots were captured as local evidence outside the committed source tree.
The browser-managed download operation took 1,317 seconds to return its file path;
this is tool wall-clock time, not an application-performance measurement.

Direct reopening of the downloaded `file://` URL was blocked by browser policy.
No alternate browser or indirect mechanism was used to bypass that restriction.
Offline reopening and final color-preference restoration remain manual acceptance
items. Unit/packaging checks establish data retention, not the blocked browser action.

## Source and effort record

The focused paper reading began at 01:58:49 UTC. Primary HTML/version history and
the locators in `examples/attention-comparisons/README.md` were inspected. The
annotation/implementation checkpoint was 02:11:47 UTC: a 778-second elapsed window
with coding and source checking interleaved. Pure reading/annotation duration was
not separately instrumented. Neither this interval nor the later browser-tool wait
is a measured authoring-speed benefit.

The one-paper comparison fixture is a deliberately scoped reading task, independent
of the full-corpus research run. It keeps the actual cutoff, source versions,
proposed review state, and source access limits. New 1.1 data and legacy inputs
use the same runtime. The actual #12 run and #10 independent/user validation remain
separate evidence streams.

## Remaining acceptance

- Publish the static preview through the explicit Pages workflow after merge and
  record the actual reachable URL and download behavior.
- Manually reopen the saved HTML and check the selected author/team mode and SVG
  legend in the target browser. These steps were not established by file existence.
- Preserve the actual research run's PARTIAL status until the source gap is
  resolved. No new completed field-history or participant-benefit claim is made.
