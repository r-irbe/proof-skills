---
name: "lean-math-foundations-handbook"
description: "Unified reference handbook for @lean-math-foundations (Lean 4 formalization + domain mathematical theory)."
extracted_from: "skills/lean-math-foundations/SKILL.md"
---

# Foundational Mathematics Encyclopaedia (Lean 4)

> **Layering note.** This file holds the deep encyclopaedia content
> previously embedded in [`skills/lean-math-foundations/SKILL.md`](../skills/lean-math-foundations/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow / Recovery /
> Handoffs) and the high-frequency pitfalls / recipes; this file holds the
> full reference content. Zero fidelity loss vs the pre-layering revision.

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

---

## Inline Pitfalls & Recovery Recipes (from `skills/lean-math-foundations/SKILL.md`)

# Lean 4 Mathematical Foundations

Guide to formalizing foundational mathematics in Lean 4, covering the structures and patterns that underpin all domain-specific formalization work.

## Routing

- **USE FOR:** foundational mathematics in Lean 4 — Lean's type system (Prop / Type / universes), classical vs constructive choices, Mathlib's algebraic
  typeclass hierarchy (Group / Ring / Order / Lattice / Module / Algebra), category theory basics, and any proof that needs foundational reasoning about
  types, propositions, or universes.
- **DO NOT USE FOR:** applied lattice instances such as severity / quality-gate lattices (delegate to `@lean-math-discrete`); analysis-flavoured algebra
  such as normed-space structure (delegate to `@lean-math-analysis`); writing a specific proof (delegate to `@lean-proof`); reviewing a finished proof
  (delegate to `@lean-proof-review`).
- **TRIGGERS:** type universe, Prop vs Type, classical reasoning, `Classical.choice`, algebraic typeclass, Mathlib hierarchy, category theory, `propext`,
  `funext`.

## Workflow

1. Identify whether the question is about Lean's logical foundation (Part 1), Mathlib's typeclass hierarchy (Parts 2–5), or a category-theoretic
   construction (later parts).
2. Locate the relevant Part below and read the project-relevance callouts before applying any pattern.
3. If the answer is a specific proof, handoff to `@lean-proof`; if it is a soundness-affecting choice (e.g., adding a new `Classical` import), handoff to
   `@lean-proof-review` and `@lean-enforcement`.

## Recovery & STOP

- STOP if a foundational choice silently introduces a new axiom — `#print axioms` must show only `propext`, `Classical.choice`, `Quot.sound` (and `funext`
  is a theorem, not an axiom). Escalate to `@lean-review-council` if uncertain.
- STOP and handoff to `@lean-research` if the question is about a result not present in Mathlib at the current pin (e.g., a new universe-polymorphism API).

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-proof` (mid-proof typeclass synthesis failure), `skill:lean-research` (when a survey turns up a
  foundational construct).
- **Successors:** `skill:lean-proof` (apply the foundational pattern in a concrete proof), `skill:lean-proof-review` (verify axiom impact),
  `skill:lean-enforcement` (run native-decide / `#print axioms` checks after the change).

## Detailed reference

Full encyclopaedia content (Parts 1 through 6) lives in
[`references/lean4-math-foundations.md`](../../references/lean4-math-foundations.md). Load that file
when authoring; the SKILL.md only carries the dispatch contract and
the high-frequency pitfalls / recipes (kept inline below).

| Part | Topic | Covers |
|---|---|---|
| Part 1 | Lean's Logical Foundations | type universes, classical vs constructive, Prop vs Decidable, equality variants |
| Part 2 | Set Theory in Mathlib | Set vs Finset, set operations, well-founded recursion, choice principles |
| Part 3 | Algebraic Hierarchies | Monoid → Group → Ring → Field, Order typeclasses, instance discovery |
| Part 4 | Order Theory | Preorder, PartialOrder, LinearOrder, Lattice, Galois connections |
| Part 5 | Logic and Proof Techniques | classical reasoning, decidability, choice, propositional extensionality |
| Part 6 | Category Theory Basics | Mathlib's CategoryTheory namespace; when to use it (rarely) |

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

- **Do not** redeclare a `Group` / `Ring` instance that already exists in Mathlib — it triggers diamond / overlap issues. Search
  `Mathlib.Algebra.Group.Defs` first.
- **Do not** `open Classical` at file scope — it pollutes every `decide` downstream. Open it only inside the proof that needs it.
- **Do not** reach for `Mathlib.CategoryTheory.*` if the same statement can be phrased in `Mathlib.Order.*` or `Mathlib.Algebra.Order.*`; the
  category-theoretic phrasing is correct but harder to automate against.

---

## Part 9 — Recovery Recipes

| Situation | First-line recipe |
|---|---|
| Typeclass synthesis stuck on an instance you believe exists | `set_option synthInstance.maxHeartbeats 40000` temporarily, then `exact?` to confirm the instance Mathlib expects |
| `simp` loops on an algebraic rewrite | `simp only [list]`; replace `add_comm` with `Nat.add_comm` etc. (qualified names cut through diamond confusion) |
| `decide` can't see a `Decidable` instance | `classical decide` (uses `Classical.dec`); or rewrite the predicate to one with a `Decidable` instance you can locate via `#check` |
| Universe issue blocks elaboration | Annotate universes explicitly (`@F.{u, v}`) at the call site |
| Need a foundational lemma absent from Mathlib at the pin | Author it locally in a host-repository `Foundation/Helpers.lean` (mirroring the Mathlib namespace) and open a Lean/Mathlib PR via `@lean-pr` |
| Want to suppress an instance for one section | `attribute [-instance] foo in section` — preferable to deleting the instance entirely |

---

## See also

- [`../../references/lean4-math-foundations.md`](../../references/lean4-math-foundations.md) — Foundational Mathematics Encyclopaedia (full encyclopaedia,
  extracted from this skill)
- [`../../templates/Template_Foundation.md`](../../templates/Template_Foundation.md) — Template: Foundation modules (types, structures, decidable preds)
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy & error priority
- [`../../references/mathlib4-conventions.md`](../../references/mathlib4-conventions.md) — Mathlib4 naming and file conventions

---

## Merged Domain Companion: `lean-math-foundations` (Unified into `@lean-math-foundations`)

# Abstract Algebra & Category Theory

Algebraic and categorical foundations for type hierarchies, compositional structures, lattice-based orderings, and the deep connection between algebra and
dependent type theory that makes Lean formalization possible.

---

## Routing

- **USE FOR:** Abstract algebra, category theory, lattice theory, universal algebra, and algebraic structures relevant to Lean formalization. Use for
  reasoning about groups, rings, fields, modules, categories, functors, natural transformations, monads, adjunctions, lattices, and algebraic hierarchies.
  Covers both pure algebraic theory and categorical perspectives essential for type-theoretic formalization.
- **DO NOT USE FOR:** measure-theoretic reasoning (use @lean-math-stochastic); topology/analysis (use @lean-math-analysis); Lean proof (use
  @lean-math-foundations).
- **TRIGGERS:** abstract algebra, category theory, lattice theory, universal algebra, algebraic structure.

## Workflow

1. Classify the structure: group / ring / field / module / lattice / category / functor / monoidal.
2. Pick the matching section of the body for the structure + its standard constructions.
3. Produce the mathematical answer or the Mathlib pointer; surface any Mathlib namespacing convention.
4. Hand off: to `@lean-math-foundations` for the Lean encoding, to `@lean-research` if pin-verification is needed, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is measure-theoretic — delegate to `@lean-math-stochastic`.
- STOP if topology/analysis dominates — delegate to `@lean-math-analysis`.
- STOP if the answer requires a pin-verified Mathlib lemma — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-math-foundations`, `skill:lean-research`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-math-foundations` lives in
[`references/lean-math-foundations-handbook.md`](../../references/lean-math-foundations-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Algebraic Structures Hierarchy |
| Part 2 | Lattice Theory |
| Part 3 | Category Theory Foundations |
| Part 4 | Monads and Computational Effects |
| Part 5 | Topos Theory and Logic |
| Part 6 | Type Theory as Algebra |
| Part 7 | Homological Methods |
| Part 8 | Galois Theory Perspective |
| Part 9 | Formalization Connections |

---

## See also

- [`../../references/lean-math-foundations-handbook.md`](../../references/lean-math-foundations-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-math-foundations/SKILL.md`](../lean-math-foundations/SKILL.md) — Successor
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

# Math Algebra Category Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-math-foundations/SKILL.md`](../skills/lean-math-foundations/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Algebraic Structures Hierarchy

### 1.1 The Algebra Tower

```
Set → Magma → Semigroup → Monoid → Group → Abelian Group → Ring → Field
                 ↓            ↓         ↓
             Semilattice   Module    Vector Space
```

### 1.2 Structures in the project

| Structure | Definition | Project usage |
|---|---|---|
| Monoid (M, ·, e) | Associative binary op + identity | Provenance chain composition |
| Group (G, ·, e, ⁻¹) | Monoid + inverses | Reversible transformations |
| Lattice (L, ∧, ∨) | Partial order with meet/join | Knowledge ordering, quality levels |
| Boolean algebra | Complemented distributive lattice | Logical gates, compliance predicates |
| Semiring (S, +, ×) | Ring without additive inverses | Path algebra on provenance DAGs |
| Module (M, R) | Abelian group acted on by ring | Quality vector spaces |
| Algebra over field | Vector space with multiplication | Trust score arithmetic |

### 1.3 Key Algebraic Theorems

| Theorem | Statement | Relevance |
|---|---|---|
| Lagrange | |H| divides |G| for H ≤ G | Symmetry constraints on states |
| First Isomorphism | G/ker(φ) ≅ im(φ) | Quotient structures in the project |
| Chinese Remainder | CRT for modular decomposition | Multi-stage independence |
| Structure theorem (f.g. abelian) | ℤⁿ ⊕ ℤ/d₁ ⊕ ... ⊕ ℤ/dₖ | Classification of discrete states |
| Zorn's Lemma | Every chain-complete poset has maximal | Existence of maximal consistent sets |
| Knaster-Tarski | Monotone function on complete lattice has fixpoint | Quality fixed-point convergence |

---

## Part 2 — Lattice Theory

### 2.1 Lattice Fundamentals

```
Partial order (P, ≤): reflexive, antisymmetric, transitive
Lattice: partial order where every pair has meet (∧) and join (∨)
Complete lattice: every subset has infimum and supremum
Distributive lattice: a∧(b∨c) = (a∧b)∨(a∧c)
Heyting algebra: lattice with implication operator (→)
Boolean algebra: complemented Heyting algebra
```

### 2.2 Project Quality Lattice

```
Knowledge quality forms a lattice:
  q₁ ≤ q₂ iff quality(q₁) ≤ quality(q₂) in all dimensions

Meet: q₁ ∧ q₂ = worst-case across dimensions
Join: q₁ ∨ q₂ = best-case across dimensions

Galois connection between:
  - Knowledge artifacts (ordered by derivation)
  - Quality scores (ordered by value)
  
Quality gate = lattice filter: {q ∈ L : q ≥ threshold}
```

### 2.3 Fixed-Point Theorems on Lattices

```
Knaster-Tarski: f: L → L monotone on complete lattice L
  → fix(f) = {x : f(x) = x} is a non-empty complete lattice
  → lfp(f) = ⊓{x : f(x) ≤ x}  (least fixed point)
  → gfp(f) = ⊔{x : x ≤ f(x)}  (greatest fixed point)

Kleene: f continuous on ω-complete poset
  → lfp(f) = ⊔{fⁿ(⊥) : n ∈ ℕ}  (iterative computation)

Project: Quality iteration q_{n+1} = QualityGate(improve(q_n))
  Monotone → converges to fixed point by Knaster-Tarski
  Continuous → computable as iterative limit by Kleene
```

---

## Part 3 — Category Theory Foundations

### 3.1 Basic Definitions

```
Category C = (Ob(C), Hom(C), ∘, id) where:
  Ob(C) = collection of objects
  Hom(A,B) = morphisms from A to B
  ∘ = composition (associative)
  id_A ∈ Hom(A,A) = identity (unit for ∘)

Important categories:
  Set:   objects = sets, morphisms = functions
  Type:  objects = types, morphisms = functions (Lean!)
  Cat:   objects = categories, morphisms = functors
  Meas:  objects = measurable spaces, morphisms = measurable functions
  Top:   objects = topological spaces, morphisms = continuous maps
  Poset: objects = elements, morphisms = order relations
```

### 3.2 Functors

```
Functor F: C → D preserves:
  Objects: A ↦ F(A)
  Morphisms: (f: A → B) ↦ (F(f): F(A) → F(B))
  Identity: F(id_A) = id_{F(A)}
  Composition: F(g ∘ f) = F(g) ∘ F(f)

Covariant: preserves arrow direction
Contravariant: reverses arrow direction

Project functors:
  Formalize: MathConcept → LeanType  (formalization functor)
  Verify: LeanType → ProofStatus     (verification functor)
  Compose: Formalize ; Verify = end-to-end pipeline
```

### 3.3 Natural Transformations

```
η: F ⟹ G (natural transformation between functors F, G: C → D)
For every A ∈ Ob(C): η_A: F(A) → G(A) in D
Naturality square commutes:
  G(f) ∘ η_A = η_B ∘ F(f)  for all f: A → B

Project: natural transformation between different quality metrics
  ensures consistent comparison across knowledge artifacts
```

### 3.4 Universal Properties

```
Initial object: unique morphism to every object (∅ in Set, ⊥ type)
Terminal object: unique morphism from every object (singleton, ⊤ type)
Product A × B: with projections π₁, π₂ (Cartesian product)
Coproduct A + B: with injections ι₁, ι₂ (disjoint union)
Equalizer: universal solution to f(x) = g(x)
Pullback: fiber product (constrainted product)
Pushout: amalgamated sum (gluing)

Limits & colimits generalize all of the above.
```

---

## Part 4 — Monads and Computational Effects

### 4.1 Monad Definition

```
Monad (T, η, μ) on category C:
  T: C → C  (endofunctor)
  η: Id ⟹ T  (unit / return)
  μ: T² ⟹ T  (multiplication / join)

Laws:
  μ ∘ Tμ = μ ∘ μT  (associativity)
  μ ∘ Tη = μ ∘ ηT = id  (unit laws)

Kleisli category: objects = C objects, morphisms A → TB
  composition: g ∘_K f = μ_C ∘ T(g) ∘ f
```

### 4.2 Monads in the project

| Monad | Type | Project usage |
|---|---|---|
| Maybe/Option | T(A) = A + 1 | Partial computation (might fail) |
| List | T(A) = [A] | Non-deterministic search |
| Reader | T(A) = Env → A | Configuration context passing |
| State | T(A) = S → (A × S) | Stateful quality tracking |
| Probability | T(A) = Dist(A) | Probabilistic computation |
| IO | T(A) = World → (A × World) | External interaction |

```
Project pipeline as monadic composition:
  experience >>= articulate >>= structure >>= consolidate >>= innovate
  where each stage may fail, has state, uses context
```

### 4.3 Adjunctions

```
Adjunction F ⊣ G (F: C → D, G: D → C):
  Hom_D(FA, B) ≅ Hom_C(A, GB)  naturally in A, B

Unit: η: Id_C → GF
Counit: ε: FG → Id_D

Every adjunction gives a monad: T = GF, η = η, μ = GεF

Key adjunctions:
  Free ⊣ Forget (free algebraic structures)
  Σ ⊣ Δ ⊣ Π (dependent types in Lean)
  ∃ ⊣ * ⊣ ∀ (quantifiers via adjoints)
```

---

## Part 5 — Topos Theory and Logic

### 5.1 Topos as Generalized Space

```
Elementary topos: category with:
  - Finite limits (products, equalizers)
  - Exponential objects (function spaces)
  - Subobject classifier Ω (generalized truth values)

Internal logic of a topos = intuitionistic higher-order logic
  → Lean's dependent type theory lives here!

Boolean topos: Ω ≅ 1 + 1 (classical logic)
  → Lean with Classical axiom
```

### 5.2 Subobject Classifier

```
Ω classifies subobjects: for each mono m: S ↪ A,
  there exists unique χ: A → Ω such that S = χ⁻¹(true)

In Set: Ω = {true, false}
In a presheaf topos: Ω = sieves (generalized open sets)

Project: quality predicates as morphisms to Ω
  "artifact is above threshold" = characteristic function to Ω
```

---

## Part 6 — Type Theory as Algebra

### 6.1 Curry-Howard-Lambek Correspondence

| Logic | Type Theory | Category Theory |
|---|---|---|
| Proposition | Type | Object |
| Proof | Term | Morphism |
| Implication A→B | Function type A→B | Exponential B^A |
| Conjunction A∧B | Product A×B | Product A×B |
| Disjunction A∨B | Sum A+B | Coproduct A+B |
| True | Unit type | Terminal object |
| False | Empty type | Initial object |
| ∀x:A, P(x) | Π(x:A), P(x) | Right adjoint to pullback |
| ∃x:A, P(x) | Σ(x:A), P(x) | Left adjoint to pullback |

### 6.2 Lean's Type Universe as Category

```
Lean's type hierarchy:
  Prop : Type 0 : Type 1 : Type 2 : ...

Each universe level is a category:
  Objects = types at that level
  Morphisms = functions between types

Universes form a tower of categories connected by lifting.
Type families form fibrations.
Dependent types form display maps.
```

---

## Part 7 — Homological Methods

### 7.1 Chain Complexes

```
... → C_{n+1} → C_n → C_{n-1} → ...
where ∂_{n} ∘ ∂_{n+1} = 0 (boundary of boundary = 0)

Homology: H_n = ker(∂_n) / im(∂_{n+1})
  Measures "holes" in the complex — things that look like boundaries
  but aren't actual boundaries of anything.

Project: provenance chains form a chain complex
  Homology detects "gaps" in the knowledge derivation
```

### 7.2 Exact Sequences

```
Short exact sequence: 0 → A → B → C → 0
  A injects into B, B surjects onto C, kernel = image

Long exact sequence:
  ... → H_n(A) → H_n(B) → H_n(C) → H_{n-1}(A) → ...

Project: exact sequences relate quality metrics across stages
  Quality can't "leak" — it's conserved modulo boundary effects
```

---

## Part 8 — Galois Theory Perspective

### 8.1 Symmetry and Automorphisms

```
Aut(K/F) = field automorphisms of K fixing F

Fundamental Theorem of Galois Theory:
  Subfields of K/F ↔ Subgroups of Gal(K/F)
  (inclusion-reversing correspondence)

Project analogy: symmetries of knowledge structures correspond
  to invariant properties under transformations
  
  Gal(KnowledgeState/BaselineState) = group of permissible 
  transformations that preserve baseline quality guarantees
```

---

## Part 9 — Formalization Connections

### 9.1 Lean Mathlib Algebraic Hierarchy

```
Mathlib structure tower (used in the project):
  MulOneClass → Monoid → Group → CommGroup
  AddZeroClass → AddMonoid → AddGroup → AddCommGroup
  Semiring → Ring → CommRing → Field
  PartialOrder → SemilatticeSup → Lattice → CompleteLattice
  Category → Functor → NatTrans → Adjunction

Project modules use these directly:
  - PhaseGates: lattice ordering for quality
  - ProvenanceChain: monoid for chain composition
  - TrustSimplex: convex combination (module over [0,1])
```

### 9.2 Formalization Priorities

- Lattice-theoretic quality gate proofs (Knaster-Tarski convergence)
- Monadic pipeline composition correctness
- Functorial preservation of knowledge properties
- Galois connection between knowledge and quality orders
- Homological detection of provenance gaps

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| `(a : α) = b` in `Subtype P` | `Subtype.ext` | `ext; simp only [...]` |
| `Quotient.mk s a = Quotient.mk s b` | `Quotient.sound` / `Quotient.eq` | `apply Quotient.sound; ...` |
| `(f : α → β) = g` | `funext` | `funext x; ...` |
| `l (a : α) ≤ b ↔ a ≤ u b` | `GaloisConnection l u` | `exact gc.le_iff_le` |
| Algebraic identity in `[CommRing R]` | `ring` | `by ring` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Prove two functions or sets equal | `ext x` | Chains `funext`, `Set.ext`, `Subtype.ext` |
| Lift function to quotient `Quotient s` | `Quotient.lift f (fun a b hab => ...)` | Requires congruence proof |
| Induct over quotient elements | `induction q using Quotient.inductionOn` | Reduces goal to representatives |
| Synthesize algebraic typeclass instance | `infer_instance` | Avoids manual constructor spelling |
| Use classical decidability locally | `classical` (tactic) | Scopes `Classical.propDecidable` to current goal |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| `failed to synthesize Decidable` | Predicate in `Prop` lacks computational decision procedure | Run `classical` tactic inside proof or add `[DecidablePred P]` |
| Typeclass diamond (`type mismatch` on instances) | Two non-defeq paths to same base carrier class | Use `extends` flat hierarchy or `convert h using 1` |
| `funext_iff` fails to rewrite | Function is dependent `(x : α) → β x` | Use `Department.funext` (`funext x`) instead of `funext_iff` |
