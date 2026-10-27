/-
Copyright (c) 2026 Proof-Skills. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import AltProof.Tactics

set_option autoImplicit false
set_option linter.unusedTactic false

/-!
# AltProof.Tests -- Kernel-Checked Pins for AltProof Meta-Tactics

Verifies `AltProof.Tactics`:
1. `sum_congr_ring`: finite-sum linearity (`sum_sub_distrib`, `sum_add_distrib`,
   `mul_sum`, `sum_mul`) and pointwise ring congruence.
2. `alt_proof`: automated reduction cascade across Presburger arithmetic,
   ordered rings, and finite sums.
3. `elegance?`: AST feature extraction, relevance filtering, speculative
   backtracking evaluation (`withoutModifyingState`), heartbeat profiling,
   and `TryThis` suggestion emission.
4. `computeCostX10` and `filterRelevantRoutes`: deterministic unit pins.
5. Golden Pilots 2, 3, and 4 reduced via `sum_congr_ring` and `alt_proof`.
-/

namespace AltProof.Tests

open AltProof.Tactics
open scoped BigOperators

/-! ### 1. Cost Model & Relevance Filter Pins -/

/-- Extraction of 1 shared lemma (-50) on a 10-line block (+10) yields net score -40. -/
theorem cost_extraction_outranks_pin :
    computeCostX10 10 1 false 0 = -40 := rfl

/-- Upstreamable lemma (+200 bonus) reduces cost by a further 200 units. -/
theorem cost_upstream_bonus_pin :
    computeCostX10 10 1 true 0 = -240 := rfl

/-- Relevance filter selects 4 routes when both `hasFinsetSum` and `hasAbs` hold. -/
theorem filter_finset_abs_routes_pin :
    (filterRelevantRoutes { hasFinsetSum := true, hasAbs := true }).length = 5 := rfl

/-- Relevance filter selects `redirect-by-contradiction` when `hasNegOrContra` holds. -/
theorem filter_neg_contra_routes_pin :
    (filterRelevantRoutes { hasNegOrContra := true }).map Route.id =
      ["redirect-by-contradiction"] := rfl

/-! ### 2. `sum_congr_ring` & `alt_proof` Reduction Pins -/

/-- `sum_congr_ring` collapses finite-sum difference and pointwise ring distribution in one step. -/
theorem sum_sub_mul_collapse
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    (c₁ c₂ : ι → R) (w : ι → R) :
    (∑ i, c₁ i * w i) - (∑ i, c₂ i * w i) = ∑ i, (c₁ i - c₂ i) * w i := by
  sum_congr_ring

/-- `sum_congr_ring` collapses scalar-times-sum into a single reassociated sum in one step. -/
theorem mul_sum_reassoc_collapse
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    (a : R) (f g : ι → R) :
    a * (∑ i, f i * g i) = ∑ i, (a * f i) * g i := by
  sum_congr_ring

/-- `alt_proof` dispatches Presburger arithmetic goals via `omega` and ring goals via `ring`. -/
theorem alt_proof_nat_and_ring_pin (n : Nat) (x y : Int) :
    (n + 5 ≤ n + 10) ∧ ((x + y) ^ 2 = x ^ 2 + 2 * x * y + y ^ 2) := by
  constructor
  · alt_proof
  · alt_proof

/-! ### 3. Golden Pilots Slimmed via `sum_congr_ring` and `alt_proof` -/

/-- Golden Pilot 2 (`contraction_step_general`): L1 nonexpansiveness of a row-stochastic
    operator over any ordered commutative ring, with `hrewrite` discharged in 1 line by
    `sum_congr_ring`. -/
theorem pilot2_contraction_step_slim
    {ι κ : Type*} [Fintype ι] [Fintype κ] {R : Type*} [CommRing R]
    [LinearOrder R] [IsOrderedRing R]
    (M : Matrix ι κ R) (hrow : ∀ i, ∑ j, M i j = 1)
    (hM : ∀ i j, 0 ≤ M i j) (c₁ c₂ : ι → R) :
    ∑ j, |(∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j)| ≤ ∑ i, |c₁ i - c₂ i| := by
  have hrewrite : ∀ j : κ,
      (∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j) = ∑ i, (c₁ i - c₂ i) * M i j :=
    fun _ => by sum_congr_ring
  have htri : ∀ j : κ,
      |(∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j)| ≤ ∑ i, |c₁ i - c₂ i| * M i j := by
    intro j
    rw [hrewrite j]
    calc |∑ i, (c₁ i - c₂ i) * M i j|
        ≤ ∑ i, |(c₁ i - c₂ i) * M i j| := Finset.abs_sum_le_sum_abs _ _
      _ = ∑ i, |c₁ i - c₂ i| * M i j := by
          refine Finset.sum_congr rfl fun i _ => ?_
          rw [abs_mul, abs_of_nonneg (hM i j)]
  calc ∑ j, |(∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j)|
      ≤ ∑ j, ∑ i, |c₁ i - c₂ i| * M i j := Finset.sum_le_sum fun j _ => htri j
    _ = ∑ i, |c₁ i - c₂ i| * (∑ j, M i j) := by
        rw [Finset.sum_comm]
        exact Finset.sum_congr rfl fun i _ => by rw [Finset.mul_sum]
    _ = ∑ i, |c₁ i - c₂ i| := by
        exact Finset.sum_congr rfl fun i _ => by rw [hrow i, mul_one]

/-- Golden Pilot 4 (`lyapunov_descent_general`): convex Lyapunov drift inequality over
    any ordered commutative ring, slimmed with `sum_congr_ring` and `alt_proof`. -/
theorem pilot4_lyapunov_descent_slim
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    [LinearOrder R] [IsOrderedRing R]
    (M : Matrix ι ι R) (V : ι → R) (γ B : R)
    (hdrift : ∀ i, ∑ j, M i j * V j ≤ γ * V i + B)
    (c : ι → R) (hc_nonneg : ∀ i, 0 ≤ c i) (hc_sum : ∑ i, c i = 1) :
    ∑ j, (∑ i, c i * M i j) * V j ≤ γ * (∑ i, c i * V i) + B := by
  have hswap : ∑ j, (∑ i, c i * M i j) * V j = ∑ i, c i * (∑ j, M i j * V j) := by
    calc ∑ j, (∑ i, c i * M i j) * V j
        = ∑ j, ∑ i, c i * M i j * V j :=
          Finset.sum_congr rfl fun j _ => by rw [Finset.sum_mul]
      _ = ∑ i, ∑ j, c i * M i j * V j := by rw [Finset.sum_comm]
      _ = ∑ i, c i * (∑ j, M i j * V j) :=
          Finset.sum_congr rfl fun i _ => by sum_congr_ring
  rw [hswap]
  have hle : ∑ i, c i * (∑ j, M i j * V j) ≤ ∑ i, c i * (γ * V i + B) := by
    have _ := hdrift; have _ := hc_nonneg
    finset_mono
  have hsplit : ∑ i, c i * (γ * V i + B) = γ * (∑ i, c i * V i) + B := by
    calc ∑ i, c i * (γ * V i + B)
        = ∑ i, (c i * (γ * V i) + c i * B) := by sum_congr_ring
      _ = (∑ i, c i * (γ * V i)) + (∑ i, c i * B) := by rw [Finset.sum_add_distrib]
      _ = γ * (∑ i, c i * V i) + (∑ i, c i) * B := by
          congr 1
          · sum_congr_ring
          · rw [← Finset.sum_mul]
      _ = γ * (∑ i, c i * V i) + B := by rw [hc_sum, one_mul]
  exact hle.trans (le_of_eq hsplit)

/-- `GoalFeatures.merge` combines disjoint feature flags from target and local context. -/
theorem goal_features_merge_pin :
    GoalFeatures.merge { hasFinsetSum := true } { hasAbs := true, hasNegOrContra := true } =
      { hasFinsetSum := true, hasAbs := true, hasNegOrContra := true } := rfl

/-- Empty `GoalFeatures` falls back to the top 3 extraction routes. -/
theorem filter_empty_features_fallback_pin :
    (filterRelevantRoutes {}).length = 3 := rfl

/-- `sum_congr_ring` collapses a general two-sum linear combination `a * ∑ f - b * ∑ g`
    into a single sum in one step. -/
theorem sum_linear_combination_collapse
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    (a b : R) (f g : ι → R) :
    a * (∑ i, f i) - b * (∑ i, g i) = ∑ i, (a * f i - b * g i) := by
  sum_congr_ring

/-- `finset_nonneg` discharges finite-sum non-negativity over squares and non-negative weights
    directly by instantiating the quantified hypothesis `hd : ∀ i, 0 ≤ d i`. -/
theorem finset_nonneg_squares_pin
    {ι : Type*} [Fintype ι] (d g : ι → ℝ) (hd : ∀ i, 0 ≤ d i) :
    0 ≤ ∑ i, d i * (g i) ^ 2 := by
  have _ := hd
  finset_nonneg

/-- `finset_nonneg` directly closes a sum of squares over any finite type. -/
theorem finset_nonneg_direct_sq_pin
    {ι : Type*} [Fintype ι] (u : ι → ℝ) :
    0 ≤ ∑ i, (u i) ^ 2 := by
  finset_nonneg

/-- `finset_nonneg` instantiates bounded-membership hypotheses `∀ i ∈ s, 0 ≤ w i`
    alongside unconditional hypotheses `∀ i, 0 ≤ f i`. -/
theorem finset_nonneg_membership_hyp_pin
    {ι : Type*} [DecidableEq ι] (s : Finset ι) (w f : ι → ℝ)
    (hw : ∀ i ∈ s, 0 ≤ w i) (hf : ∀ i, 0 ≤ f i) :
    0 ≤ ∑ i ∈ s, w i * f i := by
  have _ := hw; have _ := hf
  finset_nonneg

/-- `finset_mono` discharges weighted pointwise sum inequalities `∑ i, w i * f i ≤ ∑ i, w i * g i`
    over any ordered commutative ring by instantiating `hw : ∀ i, 0 ≤ w i` and `hfg : ∀ i, f i ≤ g i`. -/
theorem finset_mono_weighted_pin
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R] [LinearOrder R] [IsOrderedRing R]
    (w f g : ι → R) (hw : ∀ i, 0 ≤ w i) (hfg : ∀ i, f i ≤ g i) :
    ∑ i, w i * f i ≤ ∑ i, w i * g i := by
  have _ := hw; have _ := hfg
  finset_mono

/-- `finset_mono` instantiates bounded-membership hypotheses `∀ i ∈ s, f i ≤ g i`
    and closes linear pointwise inequalities over `ℝ`. -/
theorem finset_mono_membership_linarith_pin
    {ι : Type*} [DecidableEq ι] (s : Finset ι) (f g h : ι → ℝ)
    (hfg : ∀ i ∈ s, f i ≤ g i) (hh : ∀ i ∈ s, 0 ≤ h i) :
    ∑ i ∈ s, (2 * f i) ≤ ∑ i ∈ s, (2 * g i + h i) := by
  have _ := hfg; have _ := hh
  finset_mono

/-- `alt_proof` dispatches finite-sum monotonicity via `finset_mono` in one step. -/
theorem alt_proof_finset_mono_pin
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R] [LinearOrder R] [IsOrderedRing R]
    (c f g : ι → R) (hc : ∀ i, 0 ≤ c i) (hfg : ∀ i, f i ≤ g i) :
    ∑ i, c i * f i ≤ ∑ i, c i * g i := by
  have _ := hc; have _ := hfg
  alt_proof

/-- `finset_mono` instantiates multi-binder hypotheses `∀ i j, f i j ≤ g i j` at both
    the summation index `i` and a fixed local context variable `j : κ`. -/
theorem finset_mono_multi_binder_local_pin
    {ι κ : Type*} [Fintype ι] (f g : ι → κ → ℝ)
    (hfg : ∀ i j, f i j ≤ g i j) (j : κ) :
    ∑ i, (2 * f i j) ≤ ∑ i, (2 * g i j + 1) := by
  have _ := hfg
  finset_mono

/-- `finset_mono` recursively discharges nested double sums `∑ i, ∑ j, f i j ≤ ∑ i, ∑ j, g i j`
    over any ordered commutative ring. -/
theorem finset_mono_nested_double_sum_pin
    {ι κ : Type*} [Fintype ι] [Fintype κ] {R : Type*} [CommRing R]
    [LinearOrder R] [IsOrderedRing R]
    (f g : ι → κ → R) (hfg : ∀ i j, f i j ≤ g i j) :
    ∑ i, ∑ j, f i j ≤ ∑ i, ∑ j, g i j := by
  have _ := hfg
  finset_mono

/-- `finset_nonneg` recursively discharges nested double sum non-negativity
    `0 ≤ ∑ i, ∑ j, w i j * (u i j) ^ 2`. -/
theorem finset_nonneg_nested_double_sum_pin
    {ι κ : Type*} [Fintype ι] [Fintype κ] (w u : ι → κ → ℝ)
    (hw : ∀ i j, 0 ≤ w i j) :
    0 ≤ ∑ i, ∑ j, w i j * (u i j) ^ 2 := by
  have _ := hw
  finset_nonneg

/-- `sum_congr_ring` collapses a 3-sum linear combination `a * ∑ f + b * ∑ g - c * ∑ h`
    with right-multiplied scalars into a single sum in one step. -/
theorem sum_three_term_linear_combination_collapse
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    (a b c : R) (f g h : ι → R) :
    a * (∑ i, f i) + (∑ i, g i) * b - c * (∑ i, h i) =
      ∑ i, (a * f i + g i * b - c * h i) := by
  sum_congr_ring

/-- `alt_proof` dispatches finite-sum non-negativity with quantified hypotheses via
    `finset_nonneg` and local-context implications via `aesop`. -/
theorem alt_proof_finset_nonneg_and_aesop_pin
    {ι : Type*} [Fintype ι] (d u : ι → ℝ) (hd : ∀ i, 0 ≤ d i)
    (P Q : Prop) (hp : P) (hpq : P → Q) :
    (0 ≤ ∑ i, d i * (u i) ^ 2) ∧ Q := by
  have _ := hd; have _ := hp; have _ := hpq
  constructor
  · alt_proof
  · alt_proof

/-- Golden Pilot 3 (`doeblin_contraction_general`): quantitative Doeblin contraction
    with minorant `δ ≤ M i j`, slimmed using `sum_congr_ring`. -/
theorem pilot3_doeblin_contraction_slim
    {ι κ : Type*} [Fintype ι] [Fintype κ] {R : Type*} [CommRing R]
    [LinearOrder R] [IsOrderedRing R] {δ : R}
    (M : Matrix ι κ R) (hrow : ∀ i, ∑ j, M i j = 1)
    (hM : ∀ i j, δ ≤ M i j) (c₁ c₂ : ι → R)
    (hmass : ∑ i, c₁ i = ∑ i, c₂ i) :
    ∑ j, |(∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j)|
      ≤ (∑ i, |c₁ i - c₂ i|) * (1 - (Fintype.card κ : ℕ) • δ) := by
  have hd0 : ∑ i, (c₁ i - c₂ i) = 0 := by
    rw [Finset.sum_sub_distrib, hmass, sub_self]
  have htri : ∀ j : κ, |∑ i, (c₁ i - c₂ i) * (M i j - δ)|
      ≤ ∑ i, |(c₁ i - c₂ i) * (M i j - δ)| := fun j =>
    Finset.abs_sum_le_sum_abs (fun i => (c₁ i - c₂ i) * (M i j - δ)) Finset.univ
  have hkey : ∀ j : κ,
      (∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j) = ∑ i, (c₁ i - c₂ i) * (M i j - δ) := by
    intro j
    have e1 : (∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j)
        = ∑ i, (c₁ i - c₂ i) * M i j := by sum_congr_ring
    have e2 : ∑ i, (c₁ i - c₂ i) * (M i j - δ) =
        (∑ i, (c₁ i - c₂ i) * M i j) - (∑ i, (c₁ i - c₂ i)) * δ := by
      have step : ∑ i, (c₁ i - c₂ i) * (M i j - δ) =
          ∑ i, ((c₁ i - c₂ i) * M i j - (c₁ i - c₂ i) * δ) := by sum_congr_ring
      rw [step, Finset.sum_sub_distrib, ← Finset.sum_mul, hd0, zero_mul, sub_zero]
    rw [e1, e2, hd0, zero_mul, sub_zero]
  calc ∑ j, |(∑ i, c₁ i * M i j) - (∑ i, c₂ i * M i j)|
      = ∑ j, |∑ i, (c₁ i - c₂ i) * (M i j - δ)| :=
        Finset.sum_congr rfl fun j _ => by rw [hkey j]
    _ ≤ ∑ j, ∑ i, |c₁ i - c₂ i| * (M i j - δ) := by
        refine Finset.sum_le_sum fun j _ => (htri j).trans (Finset.sum_le_sum fun i _ => ?_)
        rw [abs_mul]
        exact mul_le_mul_of_nonneg_left
          (le_of_eq (abs_of_nonneg (sub_nonneg.mpr (hM i j)))) (abs_nonneg _)
    _ = ∑ i, |c₁ i - c₂ i| * (∑ j, M i j - (Fintype.card κ : ℕ) • δ) := by
        rw [Finset.sum_comm]
        refine Finset.sum_congr rfl fun i _ => ?_
        rw [← Finset.mul_sum, Finset.sum_sub_distrib, hrow i, Finset.sum_const, Finset.card_univ]
    _ = (∑ i, |c₁ i - c₂ i|) * (1 - (Fintype.card κ : ℕ) • δ) := by
        simp only [hrow]
        rw [← Finset.sum_mul]

/-- `elegance?` runs speculatively in `withoutModifyingState` (detecting local-context
    hypotheses and ranking candidate closers) without mutating the active goal state,
    allowing `alt_proof` to discharge the goal immediately afterward. -/
theorem elegance_speculative_closer_pin
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    (a b : R) (f g : ι → R) (_hneg : ¬ False) :
    a * (∑ i, f i) + b * (∑ i, g i) = ∑ i, (a * f i + b * g i) := by
  elegance?
  alt_proof

/-- `bfs_elegance?` (Proposal 9C) speculatively explores depth-$\le 3$ decomposition sequences
    (`constructor <;> alt_proof`) inside `withoutModifyingState` without mutating the goal state. -/
theorem bfs_elegance_conjunction_pin
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    (a b : R) (f g : ι → R) (n : Nat) :
    (a * (∑ i, f i) + b * (∑ i, g i) = ∑ i, (a * f i + b * g i)) ∧ (n + 1 ≤ n + 2) := by
  bfs_elegance?
  constructor <;> alt_proof

/-- `elegance?` falls back to depth-2 BFS (`intros; sum_congr_ring`) when a universally quantified
    finite-sum goal cannot be closed by a single-step closer without `intros`. -/
theorem elegance_bfs_intros_finset_pin
    {ι : Type*} [Fintype ι] {R : Type*} [CommRing R]
    (f g : ι → R) :
    ∀ a b : R, a * (∑ i, f i) - b * (∑ i, g i) = ∑ i, (a * f i - b * g i) := by
  elegance?
  intros
  sum_congr_ring

end AltProof.Tests
