---
name: math-strategy-studio
description: Strategic mathematical thinking — brainstorming, problem decomposition, proof strategy design, creative hypothesis generation, and mathematical intuition development. Use when facing novel formalization challenges, when standard approaches fail, when exploring connections between domains, or when the theorem specification needs creative mathematical insight. The creative counterpart to the systematic research-council and review-council skills.
---

# Mathematical Strategy Studio

Creative mathematical thinking and proof strategy design for Lean 4 formalization.

---

## Part 1 — Strategy Design Framework

### 1.1 The Strategy Cycle

```
Frame → Explore → Generate → Evaluate → Select → Verify
  ↑                                                ↓
  └──────────── Feedback (didn't work) ────────────┘
```

### 1.2 Problem Framing

Before attempting any proof, frame the problem in multiple ways:

| Frame | Question | Output |
|---|---|---|
| **Direct** | What does the goal state literally say? | Syntactic analysis |
| **Semantic** | What does this mean mathematically? | English translation |
| **Structural** | What algebraic/topological structure is present? | Structure identification |
| **Analogical** | What is this similar to? | Known proof patterns |
| **Contrapositive** | What would it mean if this were false? | Counterexample intuition |
| **Constructive** | Can we build the witness explicitly? | Term-mode proof possibility |
| **Abstract** | Does this follow from a more general principle? | Generalization opportunity |
| **Computational** | Can we just compute this for all cases? | Decidability check |

### 1.3 The 5-Minute Rule

Before any creative strategy session:
1. **1 min:** Try `exact?`, `apply?`, `rw?` on the raw goal
2. **1 min:** Try `omega`, `simp`, `linarith`, `nlinarith`
3. **1 min:** Try `aesop`, `auto`, `duper`
4. **1 min:** Try `decide` (if goal might be decidable)
5. **1 min:** Unfold top-level definition and retry above

If none work → proceed to strategy design.

---

## Part 2 — Proof Strategy Patterns

### 2.1 Strategy Catalog

| Strategy | When to use | Pattern |
|---|---|---|
| **Induction** | Goal involves ℕ or recursive structure | `induction n with ...` then close base + step |
| **Case split** | Goal involves disjunction or finite cases | `rcases` or `match` then close each case |
| **Contradiction** | Direct proof seems hard, negation is structured | `by_contra h` then derive `False` |
| **Construction** | Existential goal | `use witness` then verify |
| **Calculation** | Equality/inequality chain | `calc` block with lemmas |
| **Approximation** | Exact result hard, bound suffices | Prove bound, then derive result |
| **Generalization** | Goal specific, general version easier | `suffices ∀ x, ...` then specialize |
| **Specialization** | General result available | Apply general lemma to specific case |
| **Symmetry** | Goal has symmetry structure | `wlog` or explicit symmetry argument |
| **Monotonicity** | Goal involves preserving an order | Show function is monotone, apply |
| **Continuity** | Goal involves limits or topology | `fun_prop` or manual continuous/tendsto |
| **Compactness** | Need to extract finite subcover | `IsCompact.exists_finite_subcover` |
| **Pigeonhole** | More items than slots | `Finset.exists_lt_card_fiber_of_nMul_lt_card` |
| **Diagonal** | Self-referential construction | Fixed-point or Cantor-style |

### 2.2 Multi-Tactic Compositions

| Composition | Effect | When to use |
|---|---|---|
| `unfold X; simp` | Expand definition then simplify | Goals involving Project custom defs |
| `push_neg; intro` | Negate then introduce | Proving ¬∀ or ¬∃ |
| `rw [h]; ring` | Rewrite then algebraic simplification | Polynomial identities |
| `have h := ...; linarith` | Establish key fact then linear arith | Inequality chains |
| `obtain ⟨x, hx⟩ := h; exact` | Destructure then use | Existential hypotheses |
| `constructor <;> simp` | Split and simplify both sides | Conjunction/iff goals |
| `ext; simp [*]` | Extensionality then simplify | Function/set equality |

---

## Part 3 — Creative Techniques

### 3.1 Analogy-Based Strategy

```
Source domain: [known proof that worked]
Target domain: [current problem]
Mapping:
  - Type A in source ↔ Type B in target
  - Lemma L1 in source ↔ Lemma L2 in target (to find)
  - Tactic T1 in source ↔ Tactic T2 in target
```

Project examples:
- Trust contraction ≈ Bellman contraction ≈ Lyapunov decay (same pattern!)
- Quality gates ≈ Lyapunov sublevel sets (both monotone barriers)
- Provenance chain ≈ proof tree (both DAGs with derivation structure)

### 3.2 Reversal Technique

When stuck on `A → B`:
1. Try proving `¬B → ¬A` (contrapositive)
2. Try proving `B → B'` for a weaker `B'` that implies `A → B'`
3. Try assuming `A ∧ ¬B` and deriving contradiction
4. Try proving `A ↔ B` (stronger, but sometimes easier)

### 3.3 Decomposition Patterns

**Horizontal decomposition:** split into independent sub-goals
```lean
-- Before: complicated goal G
-- After:
have h1 : G1 := by ...
have h2 : G2 := by ...
exact combine h1 h2
```

**Vertical decomposition:** chain through intermediate results
```lean
-- Before: A = D
-- After:
calc A = B := by ... -- step 1
  _ = C := by ...    -- step 2
  _ = D := by ...    -- step 3
```

**Parametric decomposition:** prove for arbitrary parameter, then instantiate
```lean
-- Before: f(3) ≤ f(5)
-- After:
theorem general (h : a ≤ b) : f a ≤ f b := by ... -- monotonicity
example : f 3 ≤ f 5 := general (by omega)
```

### 3.4 The "Zoom" Technique

When a proof is overwhelming:
1. **Zoom out:** What is the high-level structure? (Induction? Cases? Chain?)
2. **Zoom in:** What is the hardest single step? (Focus there, sorry the rest)
3. **Zoom sideways:** What adjacent theorems use similar proofs? (Copy pattern)

---

## Part 4 — Brainstorming Protocols

### 4.1 Divergent Phase: Hypothesis Generation

For generating proof strategy candidates:

1. **Mind map:** Start with the goal, branch to every tactic that could contribute
2. **Random walk:** Pick a random Mathlib namespace, see if anything applies
3. **Reversal:** "What if the conclusion were a hypothesis instead?"
4. **Combination:** "What if we combine the approaches of two similar proofs?"
5. **Simplification:** "What is the simplest version of this that is still non-trivial?"
6. **Escalation:** "What is the most powerful tool we could bring to this?" (duper/auto/decide)

### 4.2 Convergent Phase: Strategy Selection

Rank candidates by:

| Criterion | Weight | Assessment |
|---|---|---|
| Likelihood of success | 35% | Based on similar goals in project |
| Proof length estimate | 20% | Shorter is better |
| Readability | 15% | Can a reviewer understand it? |
| Tactic stability | 15% | Will it survive Lean updates? |
| Automation potential | 15% | Can this be automated for similar goals? |

### 4.3 Time-Boxed Exploration

| Time box | Activity | Exit condition |
|---|---|---|
| 5 min | Try obvious tactics (5-Minute Rule) | Success or proceed |
| 15 min | Analogy search + 2 strategies | Found promising approach or proceed |
| 30 min | Deep dive into best strategy | Proof works or escalate |
| 1 hour | Full brainstorming + all strategies | Proof works or declare "research-level" |
| 2+ hours | Research Council deep exploration | Strategy document or "table with rationale" |

---

## Part 5 — Problem Decomposition for Complex Theorems

### 5.1 The Decomposition Ladder

```
Level 0: State the full theorem → sorry
Level 1: Identify the main proof structure (induction/cases/chain)
Level 2: Create sorry lemmas for each component
Level 3: Prove the main theorem assuming sorry lemmas
Level 4: Prove each sorry lemma (recursively apply this ladder)
Level 5: Clean up and compose
```

### 5.2 Dependency-Minimizing Decomposition

**Goal:** Each sorry lemma should be independently provable (no circular dependencies).

```lean
-- Level 0:
theorem main_hard : P := by sorry

-- Level 2-3:
lemma step1 : A := by sorry
lemma step2 (h : A) : B := by sorry
lemma step3 (h : B) : P := by sorry
theorem main_hard : P := step3 (step2 step1)

-- Level 4: prove step1, step2, step3 independently
```

### 5.3 Complexity Budget

For each decomposed lemma, estimate effort:

| Effort class | Description | Budget |
|---|---|---|
| Trivial | `decide` / `omega` / `simp` | 1 min |
| Routine | Known pattern, < 10 tactic lines | 15 min |
| Moderate | Requires thought, 10-30 lines | 1 hour |
| Hard | Non-obvious, 30-100 lines | 4 hours |
| Research-level | No clear approach | Research Council session |

---

## Part 6 — Mathematical Intuition Development

### 6.1 Building Intuition Checklist

For each new domain, before formalizing:
- [ ] Can you state the main results in plain English?
- [ ] Can you draw a picture / diagram / example?
- [ ] Can you state the key definitions without looking them up?
- [ ] Can you name the main proof techniques used?
- [ ] Can you identify the "hard part" of each major theorem?
- [ ] Can you construct a counterexample if a hypothesis is dropped?

### 6.2 Example-First Methodology

Before proving a general theorem, try specific cases:

```lean
-- General: ∀ n : ℕ, ∀ q ∈ [0, 100], gate_monotone q n
-- First try:
example : gate_monotone 50 3 := by decide  -- specific case
example : gate_monotone 0 0 := by decide   -- edge case
example : gate_monotone 100 10 := by decide -- boundary case
-- If these work, the general proof is likely correct + achievable
-- If any fail, the statement needs revision BEFORE general proof
```

---

## Part 7 — Research Council Integration

| Strategy Topic | Research Council Member |
|---|---|
| Problem framing | All (each from their perspective) |
| Analogy identification | Γ (Methods Scholar) |
| Tactic selection | Γ (Methods Scholar) |
| Bound estimation | Δ (Bounds Analyst) |
| Structure identification | Β (Structure Strategist) |
| Domain relevance check | Ε (Applications Bridge) |
| Foundational approach | Α (Foundations Architect) |
| Brainstorming facilitation | Ε (Applications Bridge) — chairs the session |
