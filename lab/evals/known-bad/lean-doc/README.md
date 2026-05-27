# lean-doc cluster known-bad corpus

Calibration corpus for the `lean-doc-quality` rubric. Covers the
following layered skills:

- `lean-doc-improvement`
- `lean-doc-requirements`
- `lean-blueprint`
- `lean-report`
- `lean-specification`

Each transcript exemplifies one of the rubric's ≤2 (or =1) clauses.
Captured judge replies live in `_replies/<task-id>/<judge>.json` and
are replayed in CI via `judge-calibration` matrix row.

## Failure modes covered

| Transcript | Rubric clause | Expected aggregate |
|---|---|---|
| `hallucinated-mathlib-anchor` | §2 fabricated_api_anchor | 2 |
| `empty-doc` | §1 empty_response | 1 |
| `contradictory-blueprint` | §2 self_contradiction | 2 |
| `ad-hoc-structure` | §3 missing_template_structure | 3 (boundary case) |
| `sorry-in-spec-proof-obligation` | §1 contains_sorry | 1 |

## How to add a transcript

See `references/AUTHORING.md` → "Calibration — adding a judge corpus".
