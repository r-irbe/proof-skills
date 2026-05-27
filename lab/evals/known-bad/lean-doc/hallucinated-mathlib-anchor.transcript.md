---
task_id: hallucinated-mathlib-anchor
expected_max_score: 2
failure_mode: fabricated_api_anchor
notes: |
  Rubric §2 fires: hallucinates a Mathlib name in a spec/blueprint anchor
  without flagging that the name does not exist at the current pin.
---

# Task

Write a Lean 4 specification document (per the `lean-specification` skill
template) for a small theorem stating that the harmonic series diverges.
Include: goals, non-goals, invariants, acceptance criteria, and at
least one verified Mathlib anchor.

# Response

## Goals
- Formalize `∑ n, 1/(n+1) = ∞` in Lean 4 / Mathlib.

## Non-goals
- Convergence rate analysis.

## Invariants
- Use `Mathlib.Analysis.SpecialFunctions.Harmonic` as the home file.

## Acceptance criteria
- Theorem `Real.harmonic_series_diverges` with signature
  `theorem harmonic_series_diverges : ¬ Summable (fun n => 1/(n+1) : ℕ → ℝ)`
  builds against current mathlib pin.

## Mathlib anchors
- `Mathlib.Analysis.Sum.HarmonicDivergent.diverges_harmonic` — the
  canonical proof of harmonic divergence.
- `Mathlib.NumberTheory.Harmonic.tendsto_atTop` — companion lemma.

## Implementation hint
Use `apply Real.HarmonicDivergent.diverges_harmonic` to discharge.
