---
name: "lean-math-foundations"
description: |
  USE FOR: foundational mathematics in Lean 4 — Lean's type system (Prop / Type / universes), classical vs constructive choices, Mathlib's algebraic typeclass hierarchy (Group / Ring / Order / Lattice / Module / Algebra), category theory basics, and any proof that needs foundational reasoning about types, propositions, or universes.
  DO NOT USE FOR: applied lattice instances such as severity / quality-gate lattices (use @lean-math-discrete); analysis-flavoured algebra such as normed-space structure (use @lean-math-analysis); writing a specific proof (use @lean-proof); reviewing a finished proof (use @lean-proof-review).
  TRIGGERS: type universe, Prop vs Type, classical reasoning, Classical.choice, algebraic typeclass, Mathlib hierarchy, category theory, propext, funext.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["agent:gateway", "skill:lean-proof", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-enforcement"]
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-math-foundations/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Mathematical Foundations

Guide to formalizing foundational mathematics in Lean 4, covering the structures and patterns that underpin all domain-specific formalization work.

## Routing

- **USE FOR:** foundational mathematics in Lean 4 — Lean's type system (Prop / Type / universes), classical vs constructive choices, Mathlib's algebraic typeclass hierarchy (Group / Ring / Order / Lattice / Module / Algebra), category theory basics, and any proof that needs foundational reasoning about types, propositions, or universes.
- **DO NOT USE FOR:** applied lattice instances such as severity / quality-gate lattices (delegate to `@lean-math-discrete`); analysis-flavoured algebra such as normed-space structure (delegate to `@lean-math-analysis`); writing a specific proof (delegate to `@lean-proof`); reviewing a finished proof (delegate to `@lean-proof-review`).
- **TRIGGERS:** type universe, Prop vs Type, classical reasoning, `Classical.choice`, algebraic typeclass, Mathlib hierarchy, category theory, `propext`, `funext`.

## Workflow

1. Identify whether the question is about Lean's logical foundation (Part 1), Mathlib's typeclass hierarchy (Parts 2–5), or a category-theoretic construction (later parts).
2. Locate the relevant Part below and read the project-relevance callouts before applying any pattern.
3. If the answer is a specific proof, handoff to `@lean-proof`; if it is a soundness-affecting choice (e.g., adding a new `Classical` import), handoff to `@lean-proof-review` and `@lean-enforcement`.

## Recovery & STOP

- STOP if a foundational choice silently introduces a new axiom — `#print axioms` must show only `propext`, `Classical.choice`, `Quot.sound` (and `funext` is a theorem, not an axiom). Escalate to `@lean-review-council` if uncertain.
- STOP and handoff to `@lean-research` if the question is about a result not present in Mathlib at the current pin (e.g., a new universe-polymorphism API).

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof typeclass synthesis failure), `skill:lean-research` (when a survey turns up a foundational construct).
- **Successors:** `skill:lean-proof` (apply the foundational pattern in a concrete proof), `skill:lean-proof-review` (verify axiom impact), `skill:lean-enforcement` (run native-decide / `#print axioms` checks after the change).

---

## Part 1 — Lean's Logical Foundations

### 1.1 Type Universe Hierarchy

```
Sort 0 = Prop          -- propositions (proof-irrelevant)
Sort 1 = Type 0 = Type -- computational types
Sort 2 = Type 1        -- types of types
Sort (n+1) = Type n    -- cumulative hierarchy
```

**Project relevance:** All Project theorem statements live in `Prop`. Definitions of structures (e.g., `PhaseState`, `SafetyEnvelope`) live in `Type`. Metaprogramming (Qq quotations) may require universe-polymorphism awareness.

### 1.2 Classical vs Constructive

Lean + Mathlib is **classical by default** (via `Classical.choice`, `propext`, `Quot.sound`).

| Axiom | What it gives | Project usage |
|---|---|---|
| `propext` | Propositions with same truth value are equal | Set extensionality |
| `Quot.sound` | Quotient types respect equivalence | Quotient structures |
| `Classical.choice` | Every nonempty type has an element | Proof by contradiction, `Decidable` instances |
| `funext` | Pointwise equal functions are equal | Function extensionality (theorem, not axiom) |

**Guideline:** Use classical reasoning freely — Project is not a constructive project. But `#print axioms` must never show `sorryAx`.

### 1.3 Prop vs Decidable

```lean
-- Prop: a proposition (truth value, no computational content)
-- Decidable: a proposition with a decision procedure
-- In Project: finite, bounded Nat comparisons are always Decidable
-- Use `decide` for any goal that's computationally checkable

-- Pattern: when Lean says "failed to synthesize Decidable instance"
-- Either provide the instance or use Classical.dec
instance : Decidable (someComplexProp) := by
  unfold someComplexProp
  infer_instance  -- or: exact Classical.dec _
```

---

## Part 2 — Set Theory in Mathlib

### 2.1 Key Namespaces

| Namespace | Content | Project usage |
|---|---|---|
| `Set` | Sets as `α → Prop` | Quality gate domains, phase regions |
| `Set.Icc`, `Set.Ico`, etc. | Intervals `[a,b]`, `[a,b)`, etc. | Bounded score ranges, simplex constraints |
| `Finset` | Finite sets with decidable membership | Finite enumerations, gate conditions |
| `Multiset` | Unordered collections with multiplicity | (Rare in the project) |

### 2.2 Common Patterns

```lean
-- Membership in an interval
example (h : x ∈ Set.Icc (0:ℝ) 1) : 0 ≤ x := h.1
example (h : x ∈ Set.Icc (0:ℝ) 1) : x ≤ 1 := h.2

-- Set operations
example : Set.Icc 0 1 ∩ Set.Icc 0.5 1.5 = Set.Icc 0.5 1 := by ext; simp; constructor <;> intro ⟨h1, h2⟩ <;> omega

-- Finite set decidability
example : (3 : ℕ) ∈ ({1, 2, 3, 4} : Finset ℕ) := by decide
```

### 2.3 Simplex as Set

the project's trust simplex and CCV components live on simplices:

```lean
-- The standard simplex in the project (Nat-scaled)
def SimplexNat100 := { v : Fin 3 → ℕ | v 0 + v 1 + v 2 = 100 }

-- Real simplex for analysis
def SimplexReal := { v : Fin 3 → ℝ | (∀ i, 0 ≤ v i) ∧ ∑ i, v i = 1 }
```

---

## Part 3 — Algebraic Hierarchies (Mathlib Typeclasses)

### 3.1 The Algebra Tower

```
Mul → Semigroup → Monoid → Group
Add → AddSemigroup → AddMonoid → AddGroup
                          ↓
                    CommMonoid → CommGroup
                          ↓
              Semiring → Ring → CommRing → Field
                          ↓
              OrderedSemiring → OrderedRing → LinearOrderedField
                                                    ↓
                                                    ℝ
```

**Project relevance:** `ℕ` is an `OrderedSemiring`. `ℝ` is a `LinearOrderedField`. Proofs that work for `ℝ` often need `OrderedField` or `LinearOrder` hypotheses.

### 3.2 Common Typeclass Patterns

```lean
-- Working with ordered structures
example [OrderedSemiring α] (a b c : α) (hab : a ≤ b) (hc : 0 ≤ c) :
    a * c ≤ b * c := mul_le_mul_of_nonneg_right hab hc

-- Lattice operations (for Project severity lattice)
example [Lattice α] (a b : α) : a ⊔ b = b ⊔ a := sup_comm a b

-- Linear order (for threshold comparisons)
example [LinearOrder α] (a b : α) : a ≤ b ∨ b ≤ a := le_total a b
```

### 3.3 Project-specific Algebraic Structures

| Project concept | Algebraic structure | Mathlib typeclass |
|---|---|---|
| Quality scores (Nat ×100) | Bounded ordered monoid | `OrderedAddCommMonoid` |
| Phase severity | Total order with 4 elements | `LinearOrder` + `Fintype` |
| Trust vector | Simplex (convex subset of ℝ³) | `Convex ℝ` |
| Pipeline composition | Monoid of transformations | `Monoid` |
| Stochastic matrix | Row-stochastic `Matrix` | `StochMatrix` (custom) |

---

## Part 4 — Order Theory

### 4.1 Key Structures

| Structure | Definition | Typical project usage |
|---|---|---|
| `Preorder` | Reflexive + transitive | (Rarely needed directly) |
| `PartialOrder` | + antisymmetric | General ≤ infrastructure |
| `LinearOrder` | Total order | Threshold comparisons |
| `Lattice` | Sup + inf | See `lean-math-discrete` §3 for applied lattices |
| `CompleteLattice` | Arbitrary sup/inf | (Lyapunov sublevel sets) |
| `BoundedOrder` | Has ⊤ and ⊥ | Bounded score types |
| `WellFoundedRelation` | No infinite descending chains | Induction on DAGs, provenance depth |

Applied / project lattice instances (severity lattices, gate
composition, quality-gate lattice, trust-vector componentwise order,
information-flow security levels) are owned by
[`lean-math-discrete §3 Lattice Theory`](../lean-math-discrete/SKILL.md).
This file keeps only the typeclass tower.

### 4.2 Monotonicity

Project monotonicity theorems use:

```lean
-- Monotone: preserves ≤
theorem gate_monotone : Monotone gateFunction := by
  intro a b hab
  unfold gateFunction
  omega  -- or linarith for ℝ

-- StrictMono: preserves <
-- Antitone: reverses ≤
-- StrictAnti: reverses <
```

### 4.3 Fixed Points

Knaster-Tarski (lattice fixed points) and Banach (metric / contraction
fixed points) are consolidated into:

- Lattice side: `Mathlib.Order.FixedPoints` —
  `CompleteLattice.fixedPoint_lfp`, `CompleteLattice.fixedPoint_gfp`.
- Metric / contraction side: see
  [`references/lean4-contraction-catalog.md`](../../references/lean4-contraction-catalog.md)
  for the full `ContractingWith` API, geometric-decay lemma, and
  project contraction-theorem index.

---

## Part 5 — Logic and Proof Techniques

### 5.1 Proof Methods Cheat Sheet

| Goal shape | Primary tactic | Alternatives |
|---|---|---|
| `P ∧ Q` | `constructor` then prove each | `exact ⟨hp, hq⟩` |
| `P ∨ Q` | `left` / `right` | `exact Or.inl hp` |
| `P → Q` | `intro h` | `fun h => ...` |
| `¬P` | `intro h; exact absurd ...` | `by_contra` |
| `∀ x, P x` | `intro x` | |
| `∃ x, P x` | `exact ⟨witness, proof⟩` | `use witness` |
| `P ↔ Q` | `constructor <;> intro h` | `Iff.intro ...` |
| `a = b` | `rfl` / `ext` / `ring` / `omega` | `calc ...` |
| `a ≤ b` | `omega` / `linarith` / `nlinarith` | `gcongr` |
| `a < b` | `omega` / `linarith` | `lt_of_le_of_lt` |
| Decidable | `decide` (**`native_decide` BANNED** — adds `Lean.trustCompiler`; zero uses in the project) | |
| By contradiction | `by_contra h` | `absurd` |
| Case split | `rcases` / `obtain` / `match` | `cases` |

### 5.2 Induction Patterns

```lean
-- Simple natural number induction
theorem pow_pos (n : ℕ) (h : 0 < base) : 0 < base ^ n := by
  induction n with
  | zero => simp
  | succ k ih => exact mul_pos ih h

-- Strong induction
theorem strong_example (n : ℕ) : P n := by
  induction n using Nat.strong_rec_on with
  | _ n ih => ...

-- Well-founded induction (on DAGs, trees)
theorem wf_example (h : WellFounded r) : ... := by
  exact WellFounded.fix h (fun x ih => ...)

-- Structural induction on inductive types
theorem phase_exhaustive (p : PhaseType) : P p := by
  cases p <;> simp [...]
```

### 5.3 Project Proof Architecture Patterns

| Pattern | When to use | Example |
|---|---|---|
| `have` chain | Build intermediate facts | Simplex arithmetic (`have hk : tK = 100 - tR - tS`) |
| `calc` block | Step-by-step equality/inequality | Lyapunov decay chain |
| `suffices` | Prove a stronger statement first | Generalize before instantiate |
| `convert` | Goal is "almost" matched by a lemma | Type coercion bridges |
| `push_neg` | Negate quantifiers | Counterexample construction |

---

## Part 6 — Category Theory Basics

### 6.1 When Category Theory Appears in the project

- **Functorial structure** of pipeline composition (transformations between stages)
- **Monoidal categories** underlying the trust simplex operations
- **Diagrams** in provenance chains (DAG as a category)

### 6.2 Mathlib Category Theory

```lean
import Mathlib.CategoryTheory.Category.Basic
import Mathlib.CategoryTheory.Functor.Basic

-- Most Project work does NOT need explicit category theory.
-- The algebraic hierarchy (monoids, lattices) suffices.
-- Category theory is needed only if:
--   1. Formalizing functorial properties of pipeline transformations
--   2. Proving naturality of phase transitions
--   3. Working with enriched categories (e.g., metric spaces as enriched)
```

**Guideline:** Do not reach for category theory unless the theorem genuinely requires it. Prefer concrete algebraic structures.

---

## Part 7 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "Foundations" section).  When dispatching a question to a
council member, cite that table rather than restating the rows here.

---

## Part 8 — Common Pitfalls & Anti-Patterns

| Pitfall | Symptom | Recovery |
|---|---|---|
| Decidable-instance synthesis loop | `failed to synthesize Decidable` + stack-depth warning | Replace `infer_instance` with `Classical.dec _`; mark the surrounding def `noncomputable` if needed |
| Universe-polymorphism mismatch | `type mismatch` involving `.{u}` arguments in elaboration | Annotate universes explicitly (`@F.{u, v}`); prefer `Type _` over `Type 0` in generic positions |
| `simp` set explosion via algebraic typeclasses | Trivial goal hangs `simp` | Switch to `simp only [...]` with a hand-picked list; drop `Algebra.*` lemmas when working over `Nat` |
| Unintended `Classical.choice` leak | `#print axioms` shows `Classical.choice` on a supposedly constructive proof | Search for `Classical.byContradiction` / `decide`-via-`Decidable.decide` coercions; localise the `open Classical` |
| `Prop` ↔ `Bool` confusion | `simp` won't reduce a `decide`-based goal | `Decidable.decide_eq_true_iff` bridges them; or rewrite via `Bool.decide` lemmas |
| `funext` on dependent functions | `funext_iff` doesn't fire | `funext_iff` is non-dependent only; for `Π x, ...` unfold and apply `funext` directly |

### Anti-patterns

- **Do not** redeclare a `Group` / `Ring` instance that already exists in Mathlib — it triggers diamond / overlap issues. Search `Mathlib.Algebra.Group.Defs` first.
- **Do not** `open Classical` at file scope — it pollutes every `decide` downstream. Open it only inside the proof that needs it.
- **Do not** reach for `Mathlib.CategoryTheory.*` if the same statement can be phrased in `Mathlib.Order.*` or `Mathlib.Algebra.Order.*`; the category-theoretic phrasing is correct but harder to automate against.

---

## Part 9 — Recovery Recipes

| Situation | First-line recipe |
|---|---|
| Typeclass synthesis stuck on an instance you believe exists | `set_option synthInstance.maxHeartbeats 40000` temporarily, then `exact?` to confirm the instance Mathlib expects |
| `simp` loops on an algebraic rewrite | `simp only [list]`; replace `add_comm` with `Nat.add_comm` etc. (qualified names cut through diamond confusion) |
| `decide` can't see a `Decidable` instance | `classical decide` (uses `Classical.dec`); or rewrite the predicate to one with a `Decidable` instance you can locate via `#check` |
| Universe issue blocks elaboration | Annotate universes explicitly (`@F.{u, v}`) at the call site |
| Need a foundational lemma absent from Mathlib at the pin | Author it locally in a project-side `Foundation/Helpers.lean` (mirroring the Mathlib namespace) and open a Mathlib PR via `@mathlib-pr` |
| Want to suppress an instance for one section | `attribute [-instance] foo in section` — preferable to deleting the instance entirely |

---

## See also

- [`../../templates/Template_Foundation.md`](../../templates/Template_Foundation.md) — Template: Foundation modules (types, structures, decidable preds)
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy & error priority
- [`../../references/mathlib4-conventions.md`](../../references/mathlib4-conventions.md) — Mathlib4 naming and file conventions
