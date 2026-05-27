# research-synthesis cluster known-bad corpus

Calibration corpus for the `research-synthesis-quality` rubric.
Covers the following layered skills:

- `research-synthesis-engine`
- `research-council`
- `lean-research`
- `lean-retro-methodology`
- `epistemic-discovery-engine`

## Failure modes covered

| Transcript | Rubric clause | Expected aggregate |
|---|---|---|
| `fabricated-citation` | §1 fabricated_citation | 1 |
| `speculation-as-fact` | §2 speculation_as_fact | 2 |
| `single-perspective` | §3 shallow_single_perspective | 3 (boundary case) |
| `misattribution` | §2 misattributed_result | 2 |
| `empty-synthesis` | §1 empty_response | 1 |
