# 07 — Cluster workflow (upstream-contribution skills)

**Status:** RECONSTRUCTED stub (R27 audit). Used to coordinate Wave / Move
labels in the upstream-contribution skills under `references/upstream/`.

## 1. The Wave / Move system

Skills for upstream contribution work were promoted through *waves*, each
of which contained one or more *moves* identified by a letter+number
(e.g., `A1`, `A2`, `E1`).

| Wave | Move letter | Theme |
|---|---|---|
| W2 | A1 | mathlib4-pr |
| W2 | A2 | mathlib4-review |
| W4 | A1 | lean4-pr |
| W4 | A4 | lean-nightly-infrastructure |
| W4 | E1 | lean-bug-report-pipeline |

References from the upstream skills in `references/upstream/*.md`
identify themselves by their (Wave, Move) coordinate so that historical
provenance is unambiguous.

## 2. Why a separate cluster

Upstream-contribution work is bursty (one PR at a time, hours-days latency
between iterations) and high-context (must understand mathlib4 conventions,
PR etiquette, reviewer expectations). Bundling these skills under a shared
*cluster workflow* (i.e., a cascade of cluster prompts) lets a single
SKILL.md fan out into multiple co-located reference files without
multiplying SKILL files.

## 3. Pointers

- `references/upstream/lean4-pr.md`
- `references/upstream/mathlib4-pr.md`
- `references/upstream/mathlib4-review.md`
- `references/upstream/lean-bug-report-pipeline.md`
- `references/upstream/lean-nightly-infrastructure.md`
