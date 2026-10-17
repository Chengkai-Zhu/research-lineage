# Independent review and reading-task protocol

Status: **awaiting actual participants and independent labels** (#10).
No participant data or measured user benefit is claimed by the engineering run.

## Scholarly labels

Recruit domain researchers who did not author the map. Obtain permission to record
and publish anonymized observations. Record expertise, conflicts, review method,
source/version references and disagreements. Use separate positive, negative and
incomparable cases; preserve disagreements rather than forcing a consensus label.
Review actual claims and locators, not titles or model confidence. Store consent
and identifying materials separately from public anonymized datasets.

The `evaluate` input has `provenance` and `cases`; each case contains a complete
candidate and an `expected` decision. Use `kind: independent_human` only for real
labels with `consent: true`, `method` and `review_reference`. Engineering fixtures
use `kind: engineering_fixture`. Precision, coverage and abstention are reported
per candidate type; zero proposed cases have unavailable precision.

## Paired reading tasks

Use fixed tasks with an answer key checked against pinned sources:

1. Locate the primary source and exact version behind a claimed development.
2. Identify an assumption that prevents comparing two reported costs.
3. Explain whether a connection is author-explicit or editorial inference.

Compare a bibliography-and-source baseline against the map. Counterbalance order
and equivalent task variants to reduce practice effects. Record failures, actual
elapsed seconds and source-check correctness. Retain recruitment/selection limits
and sample size. Descriptive differences are not automatically causal effects.

`study` consumes `observations` with non-identifying `participant` and `task` IDs,
`condition` (`baseline` or `map`), positive measured `seconds`, boolean
`source_check_correct`, and explicit `consent: true`. Every participant/task must
have both conditions, with no duplicates. An empty template reports zero
participants and unavailable accuracy/time. Never manufacture rows to complete
the report. Synthetic test rows remain test fixtures, not study observations.
