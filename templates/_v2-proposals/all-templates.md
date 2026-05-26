# Project Template Improvement Report — All Twelve Templates

> **Scope.** Consolidated proposal-only improvement report for the 12 generic Lean 4 templates in `skills/templates/`. Recommendations are grounded in the the project's Lean 4 corpus (125 modules, 3,846 declarations, 0 sorry/admit, 3 whitelisted axioms — per `docs/refactor/MASTER-PLAN-V6.md`), the `docs/refactor/playbooks/` (native-decide, consolidation, …), the `research/` notes (`proof-methodology.md`, `lean4-performance-guide.md`, `lean4-ecosystem-tools.md`), and `AGENT.md`. **No code changes** to the templates themselves are proposed here — only additive, cite-backed recommendations.
>
> **Conventions.**
> - Citations are formatted `Project/<path>.lean:<line>` or `Foundations/<path>.lean:<line>` (or `docs/...` / `research/...` for prose).
> - **Effort** is tagged **S** (≤ 30 min), **M** (½–1 day), **L** (multi-day, may need new exemplar code).
> - For each addition we specify **where** in the template it belongs (existing section or "append as new §X").
> - Snippets are minimal and copy-pasteable; full proofs live in the cited Project source.

---

## Table of contents

1. [Template_Foundation](#1-template_foundation)
2. [Template_Analysis](#2-template_analysis)
3. [Template_Arithmetic](#3-template_arithmetic)
4. [Template_Dynamics](#4-template_dynamics)
5. [Template_Application](#5-template_application)
6. [Template_Index](#6-template_index)
7. [Template_Lakefile](#7-template_lakefile)
8. [Template_ProofStrategy](#8-template_proofstrategy)
9. [Template_Verification](#9-template_verification)
10. [Template_Performance](#10-template_performance)
11. [Template_Refactoring](#11-template_refactoring)
12. [Template_Automation](#12-template_automation)
13. [Cross-template patterns](#cross-template-patterns)
14. [New templates to create](#new-templates-to-create)
15. [README.md improvements](#readmemd-improvements)
16. [Top-10 prioritized improvements](#top-10-prioritized-improvements)

---

## 1. Template_Foundation

**Current scope.** Starter for a Foundations/* module: typeclass-rich algebraic / order-theoretic / topological scaffolding, instances, and `@[simp]` discipline.

### Strengths

- Clear `namespace`-per-file convention.
- Lists `@[simp]`, `@[grind]`, `@[ext]` correctly.
- Notes the "instance vs lemma" choice up front.

### Gaps from Project

- **Measure-theoretic foundations** are absent. Project heavily uses `MeasurePreserving`, `Ergodic`, `PreErgodic`, `AEStronglyMeasurable`, `IsFiniteMeasure` (e.g., `Foundations/Dynamics/BirkhoffErgodic.lean`).
- **Fractal / IFS foundations** missing. See `LipschitzWith.of_dist_le_mul` + Hutchinson operator in `Foundations/FractalGeometry/CantorSet.lean`.
- **Information geometry** foundations missing. `Matrix.diagonal`-based Fisher matrix in `Foundations/InformationGeometry/Fisher.lean` is the canonical Project exemplar.
- **Whitelisted-axiom discipline** unmentioned. Project has exactly 3 whitelisted axioms (Luczak, Hutchinson OSC, Fisher); template should show how to introduce one safely (with `axiom` + `@[simp]`-free declaration + provenance comment).
- **Bridge / facade pattern** for re-exporting external libraries (`abbrev`-based) — see `Project/Bridges/CslibLTS.lean`. Should be a first-class Foundation idiom.
- **noncomputable audit.** `AGENT.md:132` notes 122 `noncomputable` instances; template never explains when `noncomputable` is mandatory (any ℝ-valued definition, `Classical.choice`, `Real.log`, etc.).

### Concrete additions

**(A) Append new §"Measure-theoretic skeleton"** *(Effort: M)*

```lean
import Mathlib.MeasureTheory.Measure.MeasureSpace
import Mathlib.Dynamics.Ergodic.Basic

open MeasureTheory

variable {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]

/-- A measure-preserving self-map gives a discrete dynamical system. -/
structure DiscreteSystem where
  T : Ω → Ω
  hT : MeasurePreserving T μ μ

/-- Prefer `PreErgodic` over `Ergodic` when you don't need
    `IsProbabilityMeasure` — see `Foundations/Dynamics/BirkhoffErgodic.lean`. -/
example (S : DiscreteSystem μ) : PreErgodic S.T μ ↔
    ∀ s, MeasurableSet s → S.T ⁻¹' s = s → μ s = 0 ∨ μ s = 1 := Iff.rfl
```

Citation: `Foundations/Dynamics/BirkhoffErgodic.lean` (whole file is the gold-standard exemplar).

**(B) Append new §"Whitelisted-axiom protocol"** *(Effort: S)*

Show the project 3-axiom convention:

```lean
/--
Project whitelisted axiom — Hutchinson Open Set Condition.
Justification: well-known classical result; mechanical proof postponed.
Provenance: `Foundations/FractalGeometry/CantorSet.lean`.
DO NOT add new whitelisted axioms without `MASTER-PLAN` approval. -/
axiom hutchinson_osc_holds : ∀ (𝓘 : IFS ℝ), 𝓘.satisfiesOSC → 𝓘.dim = 𝓘.similarityDim
```

Cite: `docs/refactor/MASTER-PLAN-V6.md` (axiom inventory).

**(C) Append new §"Facade / bridge pattern"** *(Effort: S)*

```lean
-- Project/Bridges/<External>.lean
import Cslib.Foundations.Semantics.Lts.Basic

/-- Re-export an external library's API under an Project namespace.
    `abbrev` keeps definitional equality (cheap rewrites, free instance transport). -/
abbrev Project.LTS (S A : Type*) := Cslib.LTS S A
```

Cite: `Project/Bridges/CslibLTS.lean` (whole file).

**(D) Inline note in "noncomputable" subsection** *(Effort: S)*

> **Rule of thumb.** Any definition that uses `Real.log`, `Real.exp`, `Classical.choice`, `Classical.dec`, or pattern-matches on a `Set`-defined value must be `noncomputable`. Project has 122 such (`AGENT.md:132`); aim to keep `noncomputable` at the *definition* site, never at the lemma site.

**(E) Append new §"Information-geometry seed"** *(Effort: M)*

```lean
import Mathlib.LinearAlgebra.Matrix.Diagonal

/-- Fisher information matrix as a `Matrix.diagonal` — the project canonical form.
    See `Foundations/InformationGeometry/Fisher.lean` for the worked example. -/
noncomputable def fisher (p : Fin n → ℝ) : Matrix (Fin n) (Fin n) ℝ :=
  Matrix.diagonal (fun i => 1 / p i)
```

---

## 2. Template_Analysis

**Current scope.** Starter for a real-analysis module: limits, derivatives, integrals, inequalities.

### Strengths

- Covers `ContinuousAt`, `Continuous`, `HasDerivAt`.
- Notes `Tendsto` API.

### Gaps from Project

- **`HasDerivAt` ↔ `deriv` identification** pattern not shown. Canonical: `CuspCatastrophe/Core.lean:184-193`.
- **Chain rule** via `HasDerivAt.comp` + `congr_deriv` is missing as a recipe (`CuspCatastrophe/Core.lean:544-551`).
- **Lyapunov / SDE noise** analysis (martingale-difference) not referenced; see `Project/Probability/MartingaleDiffNoise.lean`.
- **Quadratic-form Lyapunov** discharge with `nlinarith [sq_nonneg α]` / `nlinarith [sq_nonneg (1-α)]` is pervasive in the project (LyapunovStability, RL, CuspCatastrophe) and absent from the template.
- **`field_simp [hden]; ring`** denominator-clearing recipe (canonical in `Project/Spectral.lean`) missing.
- **`convert ... using N <;> push_cast <;> omega`** cast-placement pattern (Spectral.lean:1062) missing.

### Concrete additions

**(A) Append after "Derivatives" subsection: §"`HasDerivAt` / `deriv` identification"** *(Effort: S)*

```lean
/-- Identify `deriv f x` with its `HasDerivAt` witness. -/
example (f : ℝ → ℝ) (x v : ℝ) (h : HasDerivAt f v x) : deriv f x = v :=
  h.deriv

/-- Chain rule via `HasDerivAt.comp`, then transfer to `deriv`. -/
example (g f : ℝ → ℝ) (x : ℝ) (hf : HasDerivAt f (deriv f x) x)
    (hg : HasDerivAt g (deriv g (f x)) (f x)) :
    HasDerivAt (g ∘ f) (deriv g (f x) * deriv f x) x :=
  hg.comp x hf
```

Cite: `Project/CuspCatastrophe/Core.lean:184-193` and `:544-551`.

**(B) Append new §"Quadratic Lyapunov discharge"** *(Effort: S)*

```lean
example {α x : ℝ} (hα : 0 ≤ α) (hα1 : α ≤ 1) :
    α * x ^ 2 + (1 - α) * x ^ 2 = x ^ 2 := by
  nlinarith [sq_nonneg α, sq_nonneg (1 - α), sq_nonneg x]
```

> **Heuristic.** For any convex combination of squares, *first* try `nlinarith [sq_nonneg <weight>]`; only fall back to `polyrith` / manual ring manipulation if that fails.

Cite: `Project/LyapunovStability/*.lean`, `Project/RL/*.lean`, `Project/CuspCatastrophe/Core.lean`.

**(C) Append new §"Denominator clearing"** *(Effort: S)*

```lean
example (a b c : ℝ) (hb : b ≠ 0) (hc : c ≠ 0) :
    a / b + a / c = a * (b + c) / (b * c) := by
  field_simp
  ring
```

Cite: `Project/Spectral.lean` (multiple call sites).

**(D) Append new §"Cast placement with `convert`"** *(Effort: S)*

```lean
example (n : ℕ) (h : (n : ℝ) ≤ 5) : n ≤ 5 := by
  have : (n : ℝ) ≤ (5 : ℕ) := by exact_mod_cast h
  exact_mod_cast this

-- For deeply nested goal mismatches:
example (n : ℕ) (f : ℝ → ℝ) (h : f (n + 1 : ℕ) = 0) : f ((n : ℝ) + 1) = 0 := by
  convert h using 2
  push_cast
  ring
```

Cite: `Project/Spectral.lean:1062`.

**(E) Inline note in "Integrals" subsection** *(Effort: S)*

> Project uses `MeasureTheory.integral_eq_sum_of_finite` and `birkhoffSum` / `birkhoffAverage` (`Foundations/Dynamics/BirkhoffErgodic.lean`). For Lyapunov-energy integrals, prefer `MeasureTheory.integral_nonneg` + `nlinarith` over hand-rolled bounds.

---

## 3. Template_Arithmetic

**Current scope.** Discrete arithmetic and decidable goals: `Nat`, `Int`, `Fin n`, simplex constraints, `decide` tactics.

### Strengths

- Mentions `omega`, `decide`, `interval_cases`.
- Notes Nat → Int → Real ladder.

### Gaps from Project

- **`proj_decide` 3-rung ladder** is the central Project tactic for decidable goals (`Project/Tactics.lean:104-117`); not surfaced.
- **`register_simp_attr proj_decide_unfold`** (Tactics.lean:86-100) — templates only mention `register_grind_attr`.
- **Trust-base table** (`docs/refactor/playbooks/native-decide/00-OVERVIEW.md`) is essential: kernel-only policy means **no `native_decide`** anywhere; templates should make this a hard rule.
- **Nat-scaled simplex `a+b+c=100`** patterns: `simplex_component_le`, `simplex4_component_le` (Tactics.lean:164, :429) and other `@[grind .]` helpers.
- **`zify [bounds]; linarith`** + **`push_cast; ring`** Nat→Int bridging — canonical in `Project/StochasticCCV/Core/Contraction.lean:1130-1244, 1397`.
- **`Int.abs_eq_natAbs`** bridge for `natAbs` reasoning (Contraction.lean:1397).
- **`interval_cases r <;> assumption`** for `Fin N` regime exhaustion (Tactics.lean:194).

### Concrete additions

**(A) Append new §"Project decide ladder (kernel-only policy)"** *(Effort: M)*

```lean
/-! ### `proj_decide` — the 3-rung kernel-only ladder

  Project policy: never use `native_decide` (adds `Lean.ofReduceBool` +
  `Lean.trustCompiler` axioms). The audited baseline went from 42 → 0
  `native_decide` calls (see `docs/refactor/playbooks/native-decide/`).

  Trust-base table:
  | Tactic              | Adds axioms?              | When to use            |
  |---------------------|---------------------------|------------------------|
  | `decide`            | none (kernel whnf)        | ≤ ~100 cases           |
  | `decide +kernel`    | none (explicit kernel)    | Lean ≥ 4.13, larger    |
  | `native_decide`     | **forbidden in the project**    | never                  |
-/

register_simp_attr proj_decide_unfold
  "Whitelisted unfold set for the third rung of the `proj_decide` ladder."

syntax "proj_decide" : tactic
macro_rules
  | `(tactic| proj_decide) =>
    `(tactic|
      first
        | decide
        | decide +kernel
        | (simp only [proj_decide_unfold]; decide))
```

Cite: `Project/Tactics.lean:86-117`; `docs/refactor/playbooks/native-decide/00-OVERVIEW.md`.

**(B) Append new §"Nat-scaled simplex helpers"** *(Effort: S)*

```lean
/-- A Nat-scaled simplex component is bounded by the simplex total. -/
@[grind .]
lemma simplex_component_le {a b c : ℕ} (h : a + b + c = 100) : a ≤ 100 := by
  omega

@[grind .]
lemma simplex4_component_le {a b c d : ℕ} (h : a + b + c + d = 100) : a ≤ 100 := by
  omega
```

> **Annotation discipline.** Use `@[grind .]` (with the trailing dot) — not bare `@[grind]` — for *simplex-elimination* helpers so they participate in the `grind` saturation phase before any user lemma.

Cite: `Project/Tactics.lean:164, :429`.

**(C) Append new §"Nat → Int bridging cookbook"** *(Effort: S)*

```lean
-- Pattern 1: `push_cast; ring` — for additive / multiplicative identities
example (m n : ℕ) : ((m + n : ℕ) : ℤ) = m + n := by
  push_cast; ring

-- Pattern 2: `zify [bound]; linarith` — for inequalities that need a Nat→Int lift
example (m n : ℕ) (h : n ≤ m) : (m - n : ℕ) + n = m := by
  zify [h]; linarith

-- Pattern 3: `Int.abs_eq_natAbs` — for `Int.natAbs` reasoning
example (z : ℤ) (h : z.natAbs ≤ 5) : -5 ≤ z ∧ z ≤ 5 := by
  zify [Nat.le_of_lt_succ] at h
  rw [Int.abs_eq_natAbs] at *
  omega
```

Cite: `Project/StochasticCCV/Core/Contraction.lean:1130-1244, :1397`.

**(D) Append to existing "Fin / interval_cases" subsection** *(Effort: S)*

```lean
/-- Exhaust an enum / `Fin n` regime when every case is by `assumption`. -/
example {r : Fin 4} (h0 : r = 0 → P) (h1 : r = 1 → P) (h2 : r = 2 → P) (h3 : r = 3 → P) :
    P := by
  interval_cases r <;> assumption
```

Cite: `Project/Tactics.lean:194`.

**(E) Inline guardrail at top of template** *(Effort: S)*

> **Hard rule.** No `native_decide` in the project code. Audited baseline: 42 → 0. Any new `native_decide` introduction requires `MASTER-PLAN` review.

---

## 4. Template_Dynamics

**Current scope.** Dynamical-systems modules: discrete / continuous flows, fixed points, contraction.

### Strengths

- Notes `ContractingWith` and `Function.iterate`.
- Mentions Banach fixed point.

### Gaps from Project

- **`affine_contracting_with`** — the project bridge to Mathlib's `ContractingWith` for `f(x) = c·x + (1−c)·t` (Tactics.lean:480) is missing.
- **LaSalle invariance / `LaSalleCondition`** (Tactics.lean:537+) and **`forwardInvariant`** not surfaced.
- **`LearningLevel` / `ProjectHierarchy`** 4-level nested contraction (Tactics.lean:580+) — the canonical compositional pattern.
- **Iterate / fixed-point lifts** consolidation pattern (`docs/refactor/playbooks/consolidation/00-OVERVIEW.md`, pattern 3).
- **Birkhoff ergodic** / `MeasurePreserving` / `Ergodic` not referenced (`Foundations/Dynamics/BirkhoffErgodic.lean`).
- **Doeblin / spectral-gap / mixing-time** chain in `Project/StochasticCCV/Core/` is the gold standard for Markov-chain dynamics — absent.
- **Lyapunov-energy decay** + **`geometric_decay`** (polymorphic over `CommSemiring`, Tactics.lean:154).

### Concrete additions

**(A) Append new §"Affine contraction bridge to Mathlib"** *(Effort: S)*

```lean
open Mathlib in
/-- Affine contraction `f(x) = c·x + (1−c)·t` packaged as `ContractingWith`. -/
lemma affine_contracting_with {c : ℝ} (hc : 0 ≤ c) (hc1 : c < 1) (t : ℝ) :
    ContractingWith ⟨c, hc⟩ (fun x => c * x + (1 - c) * t) := by
  -- proof body: see `Project/Tactics.lean:480` for the full discharge
  sorry
```

Cite: `Project/Tactics.lean:475-495`.

**(B) Append new §"LaSalle invariance template"** *(Effort: M)*

```lean
/-- `S` is forward-invariant under `T`. -/
def forwardInvariant (T : α → α) (S : Set α) : Prop := ∀ x ∈ S, T x ∈ S

/-- LaSalle condition: `V` is non-increasing along `T` on `S`,
    and strictly decreasing off the zero set. -/
structure LaSalleCondition (T : α → α) (V : α → ℝ) (S : Set α) : Prop where
  invariant : forwardInvariant T S
  nonIncreasing : ∀ x ∈ S, V (T x) ≤ V x
  strictDecrease : ∀ x ∈ S, V x ≠ 0 → V (T x) < V x
```

Cite: `Project/Tactics.lean:537+`.

**(C) Append new §"Nested-hierarchy compositional contraction"** *(Effort: M)*

> the project's 4-level `LearningLevel` / `ProjectHierarchy` pattern composes contractions across layers. Template should sketch the nesting + show how `ContractingWith` propagates upward.

```lean
inductive LearningLevel | task | skill | meta | identity

structure HierarchicalContraction (L : LearningLevel) where
  c    : { x : ℝ // 0 ≤ x ∧ x < 1 }
  step : (state L) → (state L)
  contracts : ContractingWith ⟨c.val, c.2.1⟩ step
```

Cite: `Project/Tactics.lean:580+`.

**(D) Append new §"Birkhoff / ergodic averages"** *(Effort: M)*

```lean
import Mathlib.Dynamics.BirkhoffSum.Basic
open MeasureTheory

example (T : Ω → Ω) (f : Ω → ℝ) (n : ℕ) :
    birkhoffAverage ℝ T f n = (1 / n) • birkhoffSum T f n := by
  rfl
```

Cite: `Project/Foundations/Dynamics/BirkhoffErgodic.lean`.

**(E) Append new §"Markov chain mixing skeleton"** *(Effort: L)*

> Doeblin condition → spectral gap → geometric ergodicity. Template should provide the *signature* of each lemma so users wire in their kernel and get convergence-rate bounds. Exemplar: `Project/StochasticCCV/Core/Banach.lean` (the ℕ → ℚ → ℝ trust tower).

```lean
structure DoeblinCondition (P : Ω → Set Ω → ℝ) (ε : ℝ) (ν : Measure Ω) : Prop where
  pos    : 0 < ε
  bound  : ∀ x A, MeasurableSet A → ε * ν A ≤ P x A
```

Cite: `Project/StochasticCCV/Core/Banach.lean:1-60`.

**(F) Append to existing "Iteration" subsection** *(Effort: S)*

> **Mono-variant collapse, Pattern 3 (iterate/fixed-point lift).** If you have `iter_step_mono` and want `iter_n_mono`, write the fundamental lemma once and lift via `Function.iterate_succ` + `induction n`. See `docs/refactor/playbooks/consolidation/00-OVERVIEW.md` for the recipe.

---

## 5. Template_Application

**Current scope.** Domain-application modules (consensus, safety, RL, …): how to wire a Foundations layer into a problem-specific theorem.

### Strengths

- Calls out module-as-narrative discipline.
- Mentions `structure` + `theorem` + `instance` triplet.

### Gaps from Project

- **BFT consensus / quorum intersection / view-change** patterns from `Project/AgenticSafety/Consensus.lean` §17–§18 are absent.
- **Hamiltonian-cycle existence proofs** (`Project/ProvenanceChain/Extensions.lean:206-228`, `proj_is_hamiltonian_cycle`) are an underexploited application template.
- **DAG-layered modules** (`AGENT.md:204-214` layers 0–4) not surfaced — every Application module should declare which layer it sits on.
- **Cross-module bridge lemmas** (Tactics.lean §21: `lyapunov_contraction_bridge`, `severity_threshold_monotone`, `trust_ccv_combined_bound`) — the *style* of these bridges is reusable.
- **Doob / Submartingale / Robbins-Siegmund** framework (`Project/Probability/*`, `Project/RL/{RobbinsSiegmund, DoobLyapunov, MaximalDoob, Polyak*}.lean`) — applications often need these.

### Concrete additions

**(A) Inline at top of template: §"Declare your DAG layer"** *(Effort: S)*

```lean
/-!
# Module: Project.<Domain>.<File>

**DAG layer:** 3 (Application). See `AGENT.md:204-214`.
**Depends on:** Layer 0 (Foundations), Layer 1 (Core algebraic), Layer 2 (Analysis).
**Forbidden imports:** other Layer-3 Applications, unless via an explicit Bridge.
-/
```

Cite: `AGENT.md:204-214`.

**(B) Append new §"Cross-module bridge lemmas"** *(Effort: S)*

```lean
/-! ### Bridge lemmas

  Bridge lemmas transport hypotheses across module boundaries without
  introducing import cycles. They live in the *downstream* module.

  Convention: name as `<downstream>_<upstream>_bridge`, e.g.
  `lyapunov_contraction_bridge` (Tactics.lean §21). -/

lemma my_app_foo_bridge {x : Foundations.Foo} (h : x.P) : MyApp.Q x := …
```

Cite: `Project/Tactics.lean §21` (514+); list `lyapunov_contraction_bridge`, `severity_threshold_monotone`, `trust_ccv_combined_bound` as exemplars.

**(C) Append new §"BFT-consensus exemplar"** *(Effort: M)*

```lean
/-- Quorum intersection (Byzantine fault tolerance). -/
structure QuorumIntersect (N f : ℕ) : Prop where
  size_lt : 3 * f < N
  inter   : ∀ Q₁ Q₂ : Finset (Fin N), Q₁.card ≥ N - f → Q₂.card ≥ N - f →
            (Q₁ ∩ Q₂).card ≥ N - 2 * f
```

Cite: `Project/AgenticSafety/Consensus.lean §17-§18`.

**(D) Append new §"Hamiltonian-cycle existence proofs"** *(Effort: M)*

```lean
/-- A constructive Hamiltonian cycle witness on an explicit `Fin n` graph. -/
def myCycle : List (Fin 4) := [0, 1, 2, 3]

/-- Discharged by `decide` (kernel-only) on the closed `Fin n` finite type. -/
example : proj_is_hamiltonian_cycle myGraph myCycle := by decide
```

Cite: `Project/ProvenanceChain/Extensions.lean:206-228`.

**(E) Append new §"Stochastic-application skeleton (RL / SDE)"** *(Effort: M)*

```lean
import Project.Probability.MartingaleDiffNoise
open MeasureTheory ProbabilityTheory

/-- Skeleton: Polyak-Ruppert average under bounded martingale-difference noise. -/
example (h : IsBoundedMartingaleDiffNoise η)
    (hα : ∀ n, 0 ≤ α n) (hα_sum : Summable α) :
    Tendsto (fun n => partialSumαη α η n) atTop (𝓝 0) := …
```

Cite: `Project/Probability/MartingaleDiffNoise.lean`; `Project/RL/RobbinsSiegmund.lean`.

---

## 6. Template_Index

**Current scope.** The aggregator `Project.lean`-style root module: re-exports, `open`s, `attribute`s, top-level docstring.

### Strengths

- Mentions `import Project.Foo`, `export`, `open ... in`.
- Calls out the importance of a single `Project.lean` entry point.

### Gaps from Project

- **DAG layer ordering** of imports (AGENT.md:204-214) not surfaced; the Index file is the natural place to *demonstrate* it.
- **`register_simp_attr`** seeding (e.g., `proj_decide_unfold`) is a root-level concern that Project handles in the early imports.
- **Tactics.lean** as a single dedicated tactic-library file imported by `Project.lean` — a convention worth surfacing.
- **Bridges/** as a separate subtree imported before any Application module.
- **MASTER-PLAN-V6 snapshot** (corpus stats) belongs in a top-of-file docstring so the Index doubles as a living dashboard.

### Concrete additions

**(A) Replace existing imports section with a DAG-ordered template** *(Effort: S)*

```lean
/-!
# Project — root index

Corpus snapshot (see `docs/refactor/MASTER-PLAN-V6.md`):
  • 125 modules · 3,846 declarations
  • 0 sorry · 0 admit · 0 forbidden axioms
  • 3 whitelisted axioms: Luczak, Hutchinson OSC, Fisher

Import order MUST follow the DAG (AGENT.md:204-214):
  Layer 0 → 1 → 2 → 3 → 4
-/

-- Layer 0: Foundations
import Project.Foundations
import Project.Tactics              -- registers `proj_decide_unfold`

-- Layer 1: Core algebraic / arithmetic
import Project.Arithmetic
import Project.LyapunovStability

-- Layer 2: Analysis / dynamics
import Project.Spectral
import Project.StochasticCCV

-- Layer 2.5: External bridges
import Project.Bridges.CslibLTS

-- Layer 3: Applications
import Project.AgenticSafety.Consensus
import Project.RL.RobbinsSiegmund

-- Layer 4: Cross-cutting / extensions
import Project.ProvenanceChain.Extensions
```

Cite: `AGENT.md:204-214`; `docs/refactor/MASTER-PLAN-V6.md`.

**(B) Append new §"What the Index does NOT do"** *(Effort: S)*

> The Index re-exports — it does not prove. No `theorem`, no `instance`, no `def` should live in `Project.lean`. Tactic registration (`register_simp_attr`, `register_grind_attr`) is exempt and *must* live near the top.

**(C) Append new §"Doc snapshot harvest"** *(Effort: S)*

> Whenever you add a module, update the top-of-file count comment. This makes `wc -l Project/**/*.lean` agree with the Index claim, which is what `MASTER-PLAN-V6` audits against.

---

## 7. Template_Lakefile

**Current scope.** `lakefile.lean` / `lakefile.toml` patterns: package deps (Mathlib, Cslib), `LeanOptions`, build groups.

### Strengths

- Lists `Mathlib`, `Aesop`, `Batteries`.
- Mentions `lake build`, `lake test`.

### Gaps from Project

- **`LEAN_STACK_SIZE` / `LEAN_MAX_MEMORY`** env vars (research/lean4-performance-guide.md) not mentioned.
- **`lake -j N`** parallelism guidance missing.
- **Per-module `maxHeartbeats` / `set_option`** policy at lakefile-level (`leanOptions := #[⟨'maxHeartbeats, 400000⟩]`) is the leverage point for the *project default* — see the project's actual policy of 200K default / 400K acceptable / 800K red-flag.
- **`require Cslib from git ...`** pattern for the consensus / LTS bridge.
- **doc-gen4** integration (research/lean4-ecosystem-tools.md) absent.
- **Smoke-test target** that runs `lake build` + `lake exe smoke` (matches `docs/refactor/playbooks/smoke/`).

### Concrete additions

**(A) Append new §"Heartbeat & resource defaults"** *(Effort: S)*

```lean
package Project where
  leanOptions := #[
    ⟨`maxHeartbeats, 400000⟩,         -- default: 200K, acceptable up to 400K
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩
  ]
  moreLeanArgs := #["-Dlinter.unusedVariables=true"]
  moreServerArgs := #["-DmaxHeartbeats=400000"]
```

> Set env vars in CI: `LEAN_STACK_SIZE=8388608 LEAN_MAX_MEMORY=8192 lake build -j 4`.

Cite: `research/lean4-performance-guide.md:43-46`.

**(B) Append new §"External deps with provenance"** *(Effort: S)*

```lean
require mathlib from git "https://github.com/leanprover-community/mathlib4" @ "v4.X.0"
require Cslib   from git "https://github.com/<org>/cslib"           @ "main"

-- For doc generation:
require «doc-gen4» from git "https://github.com/leanprover/doc-gen4" @ "main"
```

Cite: `Project/Bridges/CslibLTS.lean`; `research/lean4-ecosystem-tools.md`.

**(C) Append new §"Smoke target"** *(Effort: S)*

```lean
@[default_target]
lean_lib Project

lean_exe smoke where
  root := `Tests.Smoke
  -- a single `example := by decide` per module, aggregated
```

Cite: `docs/refactor/playbooks/smoke/00-OVERVIEW.md`.

**(D) Append new §"CI command checklist"** *(Effort: S)*

| Step | Command | Gate |
|------|---------|------|
| Build | `lake build` | exit 0 |
| Smoke | `lake exe smoke` | exit 0 |
| Axiom audit | `lake exe axiom-audit` | only whitelist |
| Sorry audit | `! grep -rn 'sorry\|admit' Project/` | no match |
| `native_decide` audit | `! grep -rn 'native_decide' Project/` | no match |

Cite: `docs/refactor/playbooks/native-decide/00-OVERVIEW.md`.

---

## 8. Template_ProofStrategy

**Current scope.** How to plan a proof: problem posing, tactic selection, working-backward vs forward.

### Strengths

- Tactic taxonomy is good.
- `apply?` / `exact?` / `simp?` mentioned.

### Gaps from Project

- **`research/proof-methodology.md`** is the canonical companion to this template (760 lines) — link is missing.
- **`grind (splits := N)`** case-explosion control (`Project/CCVEContraction.lean:97`) not mentioned.
- **`suffices ∀ s, P s` motive-generalization** (research/proof-methodology.md §5.6) — the canonical fix for "motive is not type correct" errors.
- **Loogle / LeanSearch workflow** (research/lean4-ecosystem-tools.md): structural `|-` patterns, `?a` metavars.
- **Aesop / Duper / Canonical / lean-auto** as fallbacks before `sorry`.
- **`weighted_sum_le_max_real`** as a reusable Project inequality (Tactics.lean:288).

### Concrete additions

**(A) Append new §"Tactic-search ladder"** *(Effort: S)*

```
1. exact?           — direct hit from Mathlib
2. apply?           — when goal needs to be matched against a conclusion
3. simp?            — terminal `simp` (never non-terminal `simp` without `only`)
4. rw?              — show me what to rewrite
5. Loogle: |- ?_ ≤ ?_ * ?_      (web / VS Code)
6. LeanSearch: "natural-language description"
7. Aesop: aesop                  — saturation-style search
8. Duper: duper                  — superposition prover
9. grind                         — the project's preferred all-in-one (note: `@[grind .]`)
10. Canonical / lean-auto        — last-resort heavy automation
```

Cite: `research/lean4-ecosystem-tools.md` (full TOC).

**(B) Append new §"grind discipline"** *(Effort: S)*

```lean
-- Default
example : … := by grind

-- Case-explosion budget (default ≈ 8; raise judiciously)
example : … := by grind (splits := 64)

-- Annotation policy: `@[grind .]` (with the dot) ranks the lemma higher
-- in the saturation phase than `@[grind]`. Use `.` for foundational
-- helpers and bare `@[grind]` for derived lemmas.
@[grind .] lemma simplex_component_le … := …
```

Cite: `Project/CCVEContraction.lean:97`; `Project/Tactics.lean:164, :230, :429, :977, :1000`.

**(C) Append new §"`simp` discipline"** *(Effort: S)*

> **Rule.** A terminal `simp` is fine (the proof closes here). A *non-terminal* `simp` must be `simp only [lemma₁, lemma₂, ...]` — never let `simp` change the goal in the middle of a proof, because the simp set may shift under you. From `research/proof-methodology.md §6.3`.

**(D) Append new §"Motive-error fix"** *(Effort: S)*

```
Error: "motive is not type correct"

Fix recipe:
  - Replace `have h : P x := …; rw [hxy]`
    with
    `suffices h : ∀ s, P s by exact h y; …`
  - or `generalize hxy : x = z` before the rewrite.
```

Cite: `research/proof-methodology.md §5.6`.

**(E) Append new §"Working-backward example: weighted-sum ≤ max"** *(Effort: S)*

```lean
/-- For a convex combination, sum ≤ max — reusable Project inequality. -/
example {α β a b : ℝ} (h₀ : 0 ≤ α) (h₁ : 0 ≤ β) (hαβ : α + β = 1)
    (M : ℝ) (ha : a ≤ M) (hb : b ≤ M) :
    α * a + β * b ≤ M := by
  nlinarith [mul_nonneg h₀ (by linarith : (0:ℝ) ≤ M - a),
             mul_nonneg h₁ (by linarith : (0:ℝ) ≤ M - b)]
```

Cite: `Project/Tactics.lean:288` (`weighted_sum_le_max_real`).

---

## 9. Template_Verification

**Current scope.** Audit, validation, smoke tests, `#check`/`#eval`/`example` patterns.

### Strengths

- Lists `#check`, `#eval`, `#print axioms`.
- Calls out `example := by decide` as a smoke pattern.

### Gaps from Project

- **`#print axioms` audit policy** for the whitelisted 3 (Luczak, Hutchinson OSC, Fisher) not encoded.
- **Tests/ subdirectory** + per-module test file + `Main.lean` aggregator (matches `docs/refactor/playbooks/smoke/`) absent.
- **`example := by decide` smoke** can be made stronger via the `proj_decide` ladder (Tactics.lean:104-117).
- **CI-gate scripts** (no `sorry`, no `admit`, no `native_decide`, no new axioms) absent.
- **Bisection-floor `maxHeartbeats`** policy (CCVEContraction.lean:68-77) as a *verification artifact* — every heavy proof should document its minimum-passing budget.
- **`lake exe axiom-audit`** target (research/lean4-ecosystem-tools.md CI section) absent.

### Concrete additions

**(A) Append new §"Axiom audit"** *(Effort: S)*

```lean
-- At the bottom of every Tests/<Module>.lean
#print axioms my_theorem
-- Expected output: only `propext`, `Classical.choice`, `Quot.sound`,
-- and whitelisted: `luczak_random_matrix`, `hutchinson_osc_holds`,
-- `fisher_information_holds`. Anything else is a regression.
```

Cite: `docs/refactor/MASTER-PLAN-V6.md`.

**(B) Append new §"Tests/ subtree convention"** *(Effort: M)*

```
Project/
  Foo.lean
Tests/
  Foo.lean              -- one file per Project module
  Main.lean             -- aggregator: `import all of Tests/...`

-- Tests/Foo.lean
import Project.Foo

example : (3 : ℕ).succ = 4 := by proj_decide
example : MyType.foo_well_defined := by decide
#print axioms my_theorem
```

Cite: `docs/refactor/playbooks/smoke/00-OVERVIEW.md`.

**(C) Append new §"CI gates"** *(Effort: S)*

```bash
# scripts/ci.sh
set -euo pipefail
lake build
lake exe smoke
! grep -rn '\bsorry\b\|\badmit\b' Project/ Foundations/
! grep -rn '\bnative_decide\b' Project/ Foundations/
lake exe axiom-audit                     # custom: diff against whitelist
```

Cite: `docs/refactor/playbooks/native-decide/00-OVERVIEW.md`; `MASTER-PLAN-V6.md`.

**(D) Append new §"Heartbeat-floor documentation"** *(Effort: S)*

```lean
-- Every heavy `theorem` should document its bisection-floor:
set_option maxHeartbeats 800000 in
-- ^ Bisection-floor: 750K fails, 800K passes. Raise only after profiling.
-- See `Project/CCVEContraction.lean:68-77` for the methodology.
theorem heavy_proof : … := by
  …
```

Cite: `Project/CCVEContraction.lean:68-77`.

**(E) Append new §"Doc-gen verification"** *(Effort: S)*

> Run `lake build Project:docs` to ensure every public declaration has a `/-- ... -/` docstring. doc-gen4 fails on undocumented `public` declarations when configured strictly.

Cite: `research/lean4-ecosystem-tools.md` (doc-gen4 section).

---

## 10. Template_Performance

**Current scope.** Heartbeat budgets, `set_option`, `maxHeartbeats`, recompile minimization.

### Strengths

- Lists `set_option maxHeartbeats`.
- Notes `simp only` over `simp`.

### Gaps from Project

- **Bisection-floor `maxHeartbeats`** at the proven minimum — the *single most important* Project performance lesson (`Project/CCVEContraction.lean:68-77`).
- **File-level → per-theorem** scoping migration (CCVEContraction.lean dropped 4M → 800K + 1M by per-theorem scoping) is a refactor recipe in its own right.
- **`grind (splits := N)`** as a performance lever, not just a tactic choice.
- **Quantitative thresholds** from `research/lean4-performance-guide.md:43-46`: 200K default / 400K acceptable / 800K red-flag.
- **Heap / stack tuning** via `LEAN_STACK_SIZE` / `LEAN_MAX_MEMORY` env vars.
- **Lake parallelism** `lake -j N` and `lake clean` semantics.
- **`set_option pp.all true` / `set_option pp.numericTypes true`** for diagnosing slow `simp` calls.
- **Profile tooling** `set_option profiler true; set_option profiler.threshold 100`.

### Concrete additions

**(A) Append new §"Bisection floor for `maxHeartbeats`"** *(Effort: S)*

> **Methodology (Project gold standard).** For any proof that needs `> 200000`:
> 1. Find the proven *minimum* passing value by bisection.
> 2. Scope `set_option maxHeartbeats <floor> in` to the *theorem*, never the file.
> 3. Comment the floor and the bisection date.
>
> Case study: `Project/CCVEContraction.lean:68-77` dropped a file-level budget of 4M → per-theorem budgets of 800K + 1M after this exercise.

```lean
set_option maxHeartbeats 800000 in
theorem ccve_contraction_main : … := by
  -- Bisection-floor 2024-05-12: 750K fails, 800K passes.
  …
```

Cite: `Project/CCVEContraction.lean:68-77`.

**(B) Append new §"Heartbeat tiering"** *(Effort: S)*

| Tier | Budget | Action |
|------|--------|--------|
| Green | ≤ 200K | Default; no `set_option` needed |
| Yellow | 200K – 400K | Acceptable; document why |
| Orange | 400K – 800K | Refactor target; bisection-floor mandatory |
| Red | > 800K | **Stop**; split the proof or extract a lemma |

Cite: `research/lean4-performance-guide.md:43-46`.

**(C) Append new §"Environment & lake tuning"** *(Effort: S)*

```bash
# Recommended for large Project rebuilds
LEAN_STACK_SIZE=8388608 \
LEAN_MAX_MEMORY=8192 \
lake build -j $(nproc)

# For incremental work on a single file
lake build Project.<Module>
```

Cite: `research/lean4-performance-guide.md`.

**(D) Append new §"Profiling slow proofs"** *(Effort: S)*

```lean
set_option profiler true
set_option profiler.threshold 100   -- ms

theorem slow_proof : … := by
  -- Inspect the "elaboration" / "simp" / "tactic" timings printed below.
  …
```

**(E) Append new §"`grind (splits := N)` knob"** *(Effort: S)*

```lean
-- Default split budget ≈ 8. Bisect upward; do NOT default to a large value.
example : … := by grind (splits := 64)
```

Cite: `Project/CCVEContraction.lean:97`.

**(F) Inline "Anti-patterns" subsection** *(Effort: S)*

- ❌ File-level `set_option maxHeartbeats <huge>` to mask a single slow proof.
- ❌ Non-terminal `simp` without `only` (rebuild fragility).
- ❌ `native_decide` (forbidden in the project; adds axioms).
- ❌ `simp_all` in inner loops (re-traverses the whole context).
- ❌ `decide` on goals with `> ~1000` cases without bisecting → use `decide +kernel` or refactor.

---

## 11. Template_Refactoring

**Current scope.** When and how to refactor: rename, split, consolidate, migrate.

### Strengths

- Calls out `rename_decl` / `import` hygiene.
- Notes module-split criteria.

### Gaps from Project

- **Five mono-variant consolidation patterns** from `docs/refactor/playbooks/consolidation/00-OVERVIEW.md` (430 LOC reduction across 8 clusters): (1) monotone variants, (2) direction duality, (3) iterate/fixed-point lifts, (4) component-wise lifts, (5) bridge towers.
- **`native_decide` → `decide` migration** (`docs/refactor/playbooks/native-decide/`) as a worked refactor case (42 → 0).
- **Split-plan** playbook (`docs/refactor/playbooks/split-plan/`) — when one file > N LOC, split by *responsibility* not by line count.
- **Bridge towers** (`docs/refactor/playbooks/cslib-sub/`) — the systematic way to migrate from a local stand-in to the upstream lib.
- **Rename playbook** (`docs/refactor/playbooks/rename/`) — `lake exe rename` + Mathlib-style deprecation aliases.

### Concrete additions

**(A) Append new §"The five consolidation patterns"** *(Effort: M)*

> Source: `docs/refactor/playbooks/consolidation/00-OVERVIEW.md` — proven 430 LOC reduction across 8 clusters.

| # | Pattern | Smell | Recipe |
|---|---------|-------|--------|
| 1 | Monotone variants | `foo_le`, `foo_lt`, `foo_le_of_lt` separately proved | Prove *one* `foo_le`; derive others via `le_of_lt` + `lt_of_le_of_ne` |
| 2 | Direction duality | `foo_pos`, `foo_neg` separately | Prove `foo_sign`; specialize via `sign_pos` / `sign_neg` |
| 3 | Iterate / fixed-point lifts | `f_iter_n_mono` for each `n` | Prove `f_step_mono`; lift by induction on `n` |
| 4 | Component-wise lifts | `foo_fst`, `foo_snd`, `foo_pair` | Prove `foo_fst`; pair via `Prod.mk.injEq` |
| 5 | Bridge towers | local `MyMonoid`, upstream `Monoid` | Define `abbrev MyMonoid := Monoid` in a Bridge file; deprecate local |

Cite: `docs/refactor/playbooks/consolidation/00-OVERVIEW.md`.

**(B) Append new §"`native_decide` migration case study"** *(Effort: S)*

> Audited baseline: 42 call sites. Class A (mechanical): replace by `decide` or `decide +kernel`. Class B (small refactor): pre-compute via `register_simp_attr` + `proj_decide_unfold`. Class C (heavy): extract a helper lemma proved by `omega` / `nlinarith` and discharge by `rfl` / `simp`.

Cite: `docs/refactor/playbooks/native-decide/00-OVERVIEW.md`.

**(C) Append new §"Split-by-responsibility, not by size"** *(Effort: S)*

> When a module crosses ~600 LOC, do **not** split on a line-count threshold. Split on *responsibility*: each child file should have one provable narrative (one main `theorem` + its supporting lemmas). Indicators: multiple `noncomputable section`s, multiple `open` clauses for unrelated namespaces, > 3 `structure`s defined at the top level.

Cite: `docs/refactor/playbooks/split-plan/`.

**(D) Append new §"Bridge-tower migration"** *(Effort: M)*

```lean
-- Step 1: Introduce the bridge
abbrev Project.LTS S A := Cslib.LTS S A         -- in the project/Bridges/CslibLTS.lean

-- Step 2: Re-export the API in the bridge
export Cslib.LTS (Step Trace …)

-- Step 3: Deprecate the local stand-in
@[deprecated (since := "2024-MM-DD")] alias MyLts := Project.LTS
```

Cite: `Project/Bridges/CslibLTS.lean`; `docs/refactor/playbooks/cslib-sub/`.

**(E) Append new §"Rename hygiene"** *(Effort: S)*

> Use Mathlib-style `@[deprecated (since := "YYYY-MM-DD")] alias` for every renamed public symbol; never silently rename. Run `grep -rn '<old-name>'` after the change to find missed call sites.

Cite: `docs/refactor/playbooks/rename/`.

---

## 12. Template_Automation

**Current scope.** Custom tactics, elaborators, simp sets, `register_grind_attr`.

### Strengths

- Mentions `macro_rules`, `syntax`.
- Calls out `register_grind_attr`.

### Gaps from Project

- **`register_simp_attr`** is missing — Project uses it for `proj_decide_unfold` (Tactics.lean:86-100), which is structurally distinct from `register_grind_attr`.
- **The `proj_decide` ladder** as a *worked tactic macro* (Tactics.lean:104-117).
- **`@[grind .]` vs `@[grind]` distinction** (with vs without trailing dot) — only the latter is shown in the template; the former is heavily used in the project (Tactics.lean:164, :230, :429, :977, :1000).
- **`geometric_decay`** polymorphism over `CommSemiring` (Tactics.lean:154) — a reusable tactic-target shape.
- **Reusable Project tactic library** (`Project/Tactics.lean`, 2287 LOC) as the canonical "where do shared tactics live" exemplar.
- **`Qq` for safe meta-programming** (`research/lean4-ecosystem-tools.md`) — at least mention.
- **Loogle / LeanSearch** as an *automation* aid for tactic authors, not just provers.

### Concrete additions

**(A) Append new §"`register_simp_attr` vs `register_grind_attr`"** *(Effort: S)*

```lean
/-- `register_simp_attr` creates a *simp set* that `simp only [name]` can target. -/
register_simp_attr proj_decide_unfold
  "Whitelisted unfold set for the third rung of the `proj_decide` ladder."

/-- `register_grind_attr` creates a *grind hint set*. -/
register_grind_attr proj_grind_hints "project-specific grind hints."

-- Usage:
@[proj_decide_unfold] lemma my_unfold : myDef = … := rfl
@[proj_grind_hints]   lemma my_hint   : … := …
```

Cite: `Project/Tactics.lean:86-100`.

**(B) Append new §"The `proj_decide` macro (kernel-only)"** *(Effort: S)*

(see Arithmetic template §"Project decide ladder" — cross-reference)

Cite: `Project/Tactics.lean:104-117`.

**(C) Append new §"`@[grind .]` annotation discipline"** *(Effort: S)*

```lean
@[grind .]                              -- "with the dot" — high priority
lemma foundational_helper : … := …

@[grind]                                -- "without the dot" — standard
lemma derived_lemma : … := …
```

> **Rule.** Reserve `@[grind .]` for foundational / saturation-stage helpers (simplex elimination, monotonicity primitives). Use bare `@[grind]` for derived results. Templates currently show only the latter.

Cite: `Project/Tactics.lean:164, :230, :429, :977, :1000`.

**(D) Append new §"Polymorphic tactic targets — `geometric_decay`"** *(Effort: M)*

```lean
variable {R : Type*} [CommSemiring R] [PartialOrder R]

/-- Polymorphic geometric decay shape — `r^n` over any `CommSemiring`.
    Tactic authors: write your decay lemmas at this generality first,
    specialize to ℝ via `letI` only at the call site. -/
lemma geometric_decay {r : R} (hr : 0 ≤ r) (hr' : r < 1) (n : ℕ) :
    r ^ (n + 1) ≤ r ^ n := …
```

Cite: `Project/Tactics.lean:154`.

**(E) Append new §"Where shared tactics live"** *(Effort: S)*

> Project consolidates all shared tactics in a single `Project/Tactics.lean` (2287 LOC), imported early in `Project.lean`. Convention: any tactic / `register_simp_attr` / `register_grind_attr` used by more than one module *must* live in `Tactics.lean`. Per-module tactics stay local.

Cite: `Project/Tactics.lean` (whole file).

**(F) Append new §"Meta-programming with `Qq`"** *(Effort: S)*

> When you need to *build* terms (not just elaborate them) — e.g., to generate Fisher-matrix entries by `Matrix.diagonal` from a literal `Vector` — use `Qq` (`import Qq`) for type-safe expression construction. Avoid raw `Expr` manipulation. See `research/lean4-ecosystem-tools.md` (`Qq` section) for the API surface.

---

## Cross-template patterns

These themes recur across multiple templates and would benefit from a *shared* recipe page (perhaps `templates/SharedPatterns.md`):

1. **Kernel-only trust policy.** No `native_decide`. Three-rung `proj_decide` ladder (decide → `decide +kernel` → `simp only [proj_decide_unfold]; decide`). Affects: Arithmetic, ProofStrategy, Verification, Performance, Automation. Cite: `Project/Tactics.lean:104-117`, `docs/refactor/playbooks/native-decide/00-OVERVIEW.md`.

2. **Nat-scaled → ℝ tower.** Discrete domain in `ℕ` for `decide`-ability; lift to `ℤ` via `zify [bounds]; linarith` or `push_cast; ring`; lift to `ℝ` via `Real.toNNReal` / `(_ : ℝ)`. Affects: Arithmetic, Analysis, Dynamics. Cite: `Project/StochasticCCV/Core/Banach.lean:1-60`; `Contraction.lean:1130-1244, :1397`.

3. **`@[grind .]` discipline.** The trailing dot is a *priority* signal; reserve for foundational helpers. Templates show only `@[grind]`. Affects: Automation, Arithmetic, Dynamics. Cite: `Project/Tactics.lean:164, :230, :429, :977, :1000`.

4. **Bisection-floor `maxHeartbeats`.** Per-theorem scoping at the proven minimum. The single most leveraged performance discipline. Affects: Performance, Verification, Refactoring. Cite: `Project/CCVEContraction.lean:68-77`.

5. **Five-pattern consolidation playbook.** 430 LOC saved across 8 clusters via systematic mono-variant collapse. Affects: Refactoring (lead), Dynamics, Arithmetic. Cite: `docs/refactor/playbooks/consolidation/00-OVERVIEW.md`.

6. **DAG-layered imports.** Layers 0–4; downward-only imports; bridges between Application modules. Affects: Foundation, Index, Application, Lakefile. Cite: `AGENT.md:204-214`.

7. **Whitelisted-axiom audit.** Exactly 3 (Luczak, Hutchinson OSC, Fisher). `#print axioms` in every Tests/ file. Affects: Foundation, Verification, Refactoring. Cite: `docs/refactor/MASTER-PLAN-V6.md`.

8. **Facade `abbrev`-based bridges.** `Project.LTS := Cslib.LTS` style. Definitional equality preserves Mathlib instances for free. Affects: Foundation, Index, Refactoring. Cite: `Project/Bridges/CslibLTS.lean`.

9. **Quadratic-Lyapunov `nlinarith [sq_nonneg …]` cookbook.** Pervasive across LyapunovStability, RL, CuspCatastrophe. Affects: Analysis, Dynamics, Application. Cite: multiple — start with `Project/LyapunovStability/*.lean`.

10. **Cross-module bridge lemmas.** Named `<downstream>_<upstream>_bridge`. Live downstream. Examples: `lyapunov_contraction_bridge`, `severity_threshold_monotone`, `trust_ccv_combined_bound`. Affects: Application, Index. Cite: `Project/Tactics.lean §21`.

---

## New templates to create

Nine gaps in the current twelve-template set, ranked by frequency of need across the project corpus:

| # | Proposed template | Justification | Headline Project exemplar |
|---|-------------------|----------------|--------------------------|
| 1 | **Template_Probability** | Doob, Submartingale, Robbins-Siegmund, condExp recur in every RL / SDE module; no current template covers them. | `Project/Probability/MartingaleDiffNoise.lean`; `Project/RL/{RobbinsSiegmund,DoobLyapunov,MaximalDoob,PolyakRuppert}.lean` |
| 2 | **Template_Measure** | `MeasurePreserving`, `Ergodic`, `PreErgodic`, `AEStronglyMeasurable`, `IsFiniteMeasure`. | `Project/Foundations/Dynamics/BirkhoffErgodic.lean` |
| 3 | **Template_InfoGeom** | Fisher matrix, KL divergence, exponential family, Bregman divergence; one of the 3 whitelisted axioms lives here. | `Project/Foundations/InformationGeometry/Fisher.lean` |
| 4 | **Template_Bridge** | The facade `abbrev`-pattern is reused in every external integration (Cslib, Mathlib clusters). Deserves a dedicated recipe. | `Project/Bridges/CslibLTS.lean` |
| 5 | **Template_Fractal_IFS** | Hutchinson operator, similarity dimension, `LipschitzWith.of_dist_le_mul`; second of the 3 whitelisted axioms. | `Project/Foundations/FractalGeometry/CantorSet.lean` |
| 6 | **Template_Consensus_BFT** | Quorum intersection, view-change, liveness/safety. Underexploited application class. | `Project/AgenticSafety/Consensus.lean §17-§18` |
| 7 | **Template_Calculus** | `HasDerivAt` / `deriv`, chain rule via `.comp`, polynomial derivatives — current Analysis template under-covers calculus. | `Project/CuspCatastrophe/Core.lean:184-193, :544-551` |
| 8 | **Template_Tests** | Tests/ subtree convention; per-module test file; `Main.lean` aggregator; `proj_decide` smoke; `#print axioms` audit. | `docs/refactor/playbooks/smoke/00-OVERVIEW.md` |
| 9 | **Template_Graph** | Hamiltonian cycles, DAG layering, strongly-connected enumeration; recurring in ProvenanceChain. | `Project/ProvenanceChain/Extensions.lean:206-228` |

---

## README.md improvements

The current `skills/templates/README.md` (178 LOC) is a flat index. Recommended additions:

**(R1) Add quick-start §"Pick your template"** *(Effort: S)*

```
You need to … →                  Start from …
─────────────────────────────────────────────────────────────────
Define algebraic / order types  → Template_Foundation
Prove real-analysis lemmas      → Template_Analysis
Discharge decidable goals       → Template_Arithmetic
Prove contraction / Lyapunov    → Template_Dynamics
Wire foundations into a domain  → Template_Application
Aggregate / re-export modules   → Template_Index
Configure your package          → Template_Lakefile
Plan a proof                    → Template_ProofStrategy
Audit / smoke-test              → Template_Verification
Manage heartbeat budget         → Template_Performance
Reduce / migrate code           → Template_Refactoring
Build custom tactics            → Template_Automation
```

**(R2) Add §"Dependency DAG"** *(Effort: S)*

```
Layer 0  Foundations  (Foundation)
                ↓
Layer 1  Core         (Arithmetic, Analysis)
                ↓
Layer 2  Dynamics / Spectral / Stochastic
                ↓
Layer 2.5  Bridges    (Cslib, Mathlib facades)
                ↓
Layer 3  Applications (Consensus, RL, ProvenanceChain)
                ↓
Layer 4  Extensions   (Cross-cutting)
```

Cite: `AGENT.md:204-214`.

**(R3) Add §"Trust-base table at a glance"** *(Effort: S)*

| Tactic | Axioms added | Project policy |
|--------|--------------|---------------|
| `rfl`, `decide` | none | ✓ preferred |
| `decide +kernel` | none | ✓ for larger cases |
| `Classical.choice` | `Classical.choice` (transitive) | ✓ allowed |
| `native_decide` | `Lean.ofReduceBool`, `Lean.trustCompiler` | ✗ forbidden |
| `sorry` / `admit` | n/a (incomplete proof) | ✗ forbidden |

**(R4) Add §"Where to read next"** *(Effort: S)*

- `AGENT.md` — corpus-wide conventions
- `research/proof-methodology.md` — proof strategies
- `research/lean4-performance-guide.md` — heartbeats, memory
- `research/lean4-ecosystem-tools.md` — Loogle, Aesop, doc-gen4, …
- `docs/refactor/MASTER-PLAN-V6.md` — current corpus snapshot
- `docs/refactor/playbooks/` — consolidation, native-decide, smoke, split-plan, rename

**(R5) Add §"Corpus snapshot"** *(Effort: S)*

> Project corpus (per `MASTER-PLAN-V6`): 125 modules, 3,846 declarations, 0 sorry/admit, 3 whitelisted axioms (Luczak, Hutchinson OSC, Fisher), 0 `native_decide` calls.

**(R6) Add §"Effort tag legend"** *(Effort: S)*

Adopt the S / M / L convention used in this report so that all improvement proposals are comparable.

---

## Top-10 prioritized improvements

Ranked by (impact × ubiquity / effort).

| # | Improvement | Template(s) | Why it's #N | Effort | Citation |
|---|-------------|-------------|--------------|--------|----------|
| 1 | **`proj_decide` 3-rung ladder + kernel-only policy** | Arithmetic, Verification, ProofStrategy, Automation | Codifies the single most important Project trust invariant; eliminates `native_decide` regressions; copy-paste macro. | **S** | `Project/Tactics.lean:86-117`; `docs/refactor/playbooks/native-decide/00-OVERVIEW.md` |
| 2 | **Bisection-floor `maxHeartbeats` methodology** | Performance, Verification, Refactoring | Highest-leverage performance discipline; CCVEContraction case study shows 4M → 800K+1M. | **S** | `Project/CCVEContraction.lean:68-77` |
| 3 | **`@[grind .]` vs `@[grind]` annotation discipline** | Automation, Arithmetic | Templates show only `@[grind]`; Project uses `@[grind .]` for foundational helpers across 5+ files. | **S** | `Project/Tactics.lean:164, :230, :429, :977, :1000` |
| 4 | **Five-pattern consolidation playbook** | Refactoring | Proven 430 LOC reduction across 8 clusters; reusable recipe. | **M** | `docs/refactor/playbooks/consolidation/00-OVERVIEW.md` |
| 5 | **Nat → Int → ℝ bridging cookbook (`push_cast` / `zify [bounds]; linarith` / `Int.abs_eq_natAbs`)** | Arithmetic, Analysis | Pervasive across StochasticCCV; explicit recipes prevent ad-hoc reinvention. | **S** | `Project/StochasticCCV/Core/Contraction.lean:1130-1244, :1397` |
| 6 | **New Template_Probability + Template_Measure** | (new templates) | Doob / Submartingale / Robbins-Siegmund and `MeasurePreserving` / `Ergodic` recur in every stochastic module; no current template covers them. | **L** | `Project/Probability/MartingaleDiffNoise.lean`; `Foundations/Dynamics/BirkhoffErgodic.lean` |
| 7 | **DAG-layered imports** + corpus snapshot in Index | Index, Foundation, Application | Encodes the architectural invariant; auto-audits via Index docstring. | **S** | `AGENT.md:204-214`; `docs/refactor/MASTER-PLAN-V6.md` |
| 8 | **`HasDerivAt` ↔ `deriv` + chain-rule recipe** | Analysis (or new Template_Calculus) | Calculus is currently under-covered; CuspCatastrophe is the worked exemplar. | **S** | `Project/CuspCatastrophe/Core.lean:184-193, :544-551` |
| 9 | **Whitelisted-axiom protocol + `#print axioms` audit** | Foundation, Verification | Encodes the 3-axiom invariant; prevents silent axiom regressions in CI. | **S** | `docs/refactor/MASTER-PLAN-V6.md`; `Project/Foundations/FractalGeometry/CantorSet.lean` |
| 10 | **Facade `abbrev`-based Bridge pattern** | (new Template_Bridge), Foundation, Refactoring | Reused in every external library integration; enables zero-cost migration from local stand-ins. | **S** | `Project/Bridges/CslibLTS.lean` |

---

*End of report.*
