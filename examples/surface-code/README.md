# From one paper to a surface-code reading history

**Illustrative baseline:** this four-work authored path is retained for comparison.
It does not establish adequate field-history coverage or an independent execution
of the skill from one paper. Research-workflow acceptance was reopened in #12.

Input: [Quantum error correction below the surface code threshold, arXiv v1](https://arxiv.org/abs/2408.13687v1).
The single paper was supplied to `research-lineage start`; the helper produced an
empty draft and research brief. The host then read and annotated sources. This is
a worked authoring run, not an automatic extraction benchmark.

The map asks when increasing the code size begins to protect a quantum memory
better. It selects four works and four proposed relationships, with a four-step
reading route. It is separate from QSP/QSVT and uses error-correction conditions,
physical qubits and logical error per cycle rather than oracle-cost settings.

## Source checks on 2026-10-17

| Work | First available | Version used | What was checked |
| --- | --- | --- | --- |
| [Dennis et al., Topological quantum memory](https://arxiv.org/abs/quant-ph/0110143v1) | 2001-10-24 | arXiv v1 | Identity, dates, abstract and explicit recovery assumptions |
| [Fowler et al., A primer on surface codes](https://arxiv.org/abs/1208.0928v1) | 2012-08-04 | arXiv v1 | Identity, dates and abstract; keep the v1 title rather than replacing it with the later journal title |
| [Google Quantum AI, Suppressing quantum errors](https://www.nature.com/articles/s41586-022-05434-1) | 2022-07-13 | Nature record, 2023-02-22 | Abstract, logical-performance section and Fig. 3; record the earlier arXiv version separately |
| [Google Quantum AI and Collaborators, below-threshold memory](https://arxiv.org/pdf/2408.13687v1) | 2024-08-24 | arXiv v1 | PDF pp. 1–3, sections I–II, Fig. 1 and references 3, 13, 17 |

The seed's reference 17 and section II explicitly describe reuse of the 2023
memory methods. The threshold connection is grounded in its introduction. The
two primer connections are explicitly editorial, including the distinction
between the inspected v1 and the journal version cited by the seed. Collective
author names are taken from the actual paper headers.

The arXiv HTML conversion of the 2022 paper displayed a later generated date;
publication dates come from version history and the publisher record. Its PDF
retrieval failed in the research tool, so the accessible Nature full text was
used and recorded as the cited version. The 2024 seed PDF was accessible.

## Boundaries and effort

The reading path ends at the 2024 seed. A bounded follow-up search surfaced later
work, including a 2025 leakage-suppression experiment; those papers are outside
this selected history and are not claimed as covered. Shor/stabilizer origins,
alternative codes, other hardware and complete decoding developments are also
excluded. Two entries use abstracts. All results and relations remain proposed.

The host performed this source reading and annotation during the implementation
session. Active research minutes were not instrumented, so no estimate is reported
as a measurement. Timed validation/build and browser observations are recorded
in the [v0.2 workflow report](../../docs/test-reports/skill-first-workflow.md).
Independent human review effort and participant outcomes remain unavailable (#10).

## Reproduce

```sh
research-lineage start "https://arxiv.org/abs/2408.13687v1" --out output/paper-seed
research-lineage validate examples/surface-code/map.json
research-lineage build examples/surface-code/map.json --out output/surface-code
research-lineage compare examples/surface-code/map.json r-scaling r-below-threshold
```

Open `output/surface-code/map.html`. Start at the overview, follow the four-step
route, and open evidence only when needed. Comparing reported settings does not
establish a cross-device performance ranking.
