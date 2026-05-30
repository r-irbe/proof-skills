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
| Need a foundational lemma absent from Mathlib at the pin | Author it locally in a host-repository `Foundation/Helpers.lean` (mirroring the Mathlib namespace) and open a Lean/Mathlib PR via `@lean-pr` |
| Want to suppress an instance for one section | `attribute [-instance] foo in section` — preferable to deleting the instance entirely |

---

## See also

- [`../../references/lean4-math-foundations.md`](../../references/lean4-math-foundations.md) — Foundational Mathematics Encyclopaedia (full encyclopaedia, extracted from this skill)
- [`../../templates/Template_Foundation.md`](../../templates/Template_Foundation.md) — Template: Foundation modules (types, structures, decidable preds)
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Proof strategy & error priority
- [`../../references/mathlib4-conventions.md`](../../references/mathlib4-conventions.md) — Mathlib4 naming and file conventions
