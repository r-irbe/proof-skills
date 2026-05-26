---
name: lean-research-types
description: Specialized research methodologies for different research needs in Lean 4 formalization. Extends lean-research (SK-11) with typed research protocols for mathematical, AI-safety, tactic, literature, and design research. Use when the research question belongs to a specific category requiring targeted methodology.
---

# SK-38: Typed Research Protocols

Extends lean-research (SK-11) with specialized research types. Each type has its own methodology, tools, success criteria, and output format.

---

## Part 1 — Research Type Classification

```
Research question arrives
  │
  ├── Mathematical: "How to prove X?"
  │     └── Type M: Mathematical Research
  │
  ├── Tactic: "Which tactic/lemma to use?"
  │     └── Type T: Tactic & API Research
  │
  ├── Literature: "What's known about X in formalization?"
  │     └── Type L: Literature Research
  │
  ├── Safety: "Is this formalization sound/safe?"
  │     └── Type S: Safety & Soundness Research
  │
  ├── Design: "How to structure this formalization?"
  │     └── Type D: Design & Architecture Research
  │
  ├── Domain: "What does this concept mean in domain X?"
  │     └── Type X: Cross-Domain Research
  │
  └── Epistemic: "What don't we know?"
        └── Type E: Epistemic Research (→ epistemic-mapping SK-23)
```

---

## Part 2 — Type M: Mathematical Research

**When:** Proving a theorem that requires non-trivial mathematical insight.

### 2.1 Protocol

```
1. FORMALIZE: Write the exact goal in Lean syntax
2. DECOMPOSE: Break into sub-goals (have/suffices)
3. SEARCH INTERNAL:
   a. Check Tactics.lean reusable lemmas
   b. Check same module for related results
   c. Check bridge theorems to other modules
4. SEARCH MATHLIB:
   a. Loogle with 3+ reformulations
   b. exact? / apply? on each sub-goal
   c. Browse namespace hierarchy around the topic
5. SEARCH LITERATURE:
   a. Check if the mathematical result has a name
   b. Find the original paper if applicable
   c. Check Coq/Isabelle/HOL for alternative proofs
6. SYNTHESIZE:
   a. Choose proof strategy (direct | contradiction | induction | calc)
   b. Identify all needed lemmas
   c. Write proof sketch in prose before Lean
7. IMPLEMENT: Code the proof
8. VERIFY: Build, check axioms, review
```

### 2.2 Output

```markdown
## Research: Type M — [topic]
- **Goal:** [Lean goal statement]
- **Strategy chosen:** [direct/contradiction/induction/calc]
- **Key lemmas used:** [list with sources]
- **Alternative strategies considered:** [why rejected]
- **Epistemic transition:** [KU→KK or UU→KU or ...]
- **ZK note created:** [ZK-ID if applicable]
```

### 2.3 Depth Levels

| Depth | Time Budget | When |
|---|---|---|
| Quick | First result from exact?/Loogle | Known technique, just need the API |
| Standard | Methodical Mathlib exploration | Standard mathematical result |
| Deep | Multi-source research + alternatives | Novel formalization, no precedent |
| Exhaustive | Full literature survey | Research-level mathematics |

---

## Part 3 — Type T: Tactic & API Research

**When:** Need to find the right tactic, lemma, or Mathlib API for a specific goal.

### 3.1 Protocol

```
1. CLASSIFY GOAL TYPE:
   - Arithmetic (ℕ, ℤ, ℚ, ℝ) → omega, norm_num, linarith, nlinarith, ring
   - Propositional → decide, tauto, aesop
   - Set/Collection → simp, ext, Finset lemmas
   - Order/Lattice → gcongr, mono, bound_tac
   - Topology → continuity, measurability
   - Category → aesop_cat
   
2. TRY AUTOMATED:
   - #check / #find for declaration and statement-shape exploration
   - exact? / apply? (precise match)
   - rw? (rewrite search)
   - simp? (simplification with lemma discovery)
   - auto + duper (first-order reasoning)
   
3. SEARCH MATHLIB API:
   - Loogle with constants, conclusion filters (`|-`), and comma intersections
   - LeanSearch when the concept is known only in natural language
   - Namespace browse (e.g., Nat.*, Finset.*, List.*)
   - Check _root_ alternatives
   
4. CHECK Project CUSTOM TACTICS:
   | Tactic | Good For |
   |---|---|
   | proj_decide **(DEPRECATED — 0 uses)** | Phase/gate decidability — use `decide` directly |
   | proj_omega **(DEPRECATED — 0 uses)** | ×100 Nat arithmetic — use `omega` directly |
   | proj_contraction **(DEPRECATED — 0 uses)** | Contraction map ε·d — use `nlinarith` directly |
   | proj_lyapunov **(DEPRECATED — 0 uses)** | Lyapunov decrease V' ≤ (1-α)·V |
   | proj_pipeline **(DEPRECATED — 0 uses)** | Pipeline composition |
   | proj_stochastic **(DEPRECATED — 0 uses)** | Row-stochastic simplex |
   | proj_nested **(DEPRECATED — 0 uses)** | Nested learning hierarchy |
   
5. REPORT: Which tactic(s) work, which lemma(s) needed
```

### 3.2 Output

```markdown
## Research: Type T — [goal description]
- **Goal type:** [arithmetic/propositional/set/order/...]
- **Automated result:** exact? found [lemma] / no result
- **Recommended tactic:** [tactic] with [lemma arguments]
- **Alternatives:** [other approaches that work]
- **New to add to Tactics.lean?** [yes/no — if a helper would be reusable]
```

### 3.3 Theorem-search loop

When the task is "find the theorem/API/tactic", use the bundle-level
[`theorem-search`](../../references/theorem-search.md) reference and report:

1. the goal shape queried,
2. at least one Loogle or Mathlib-search query,
3. any `#check` / `#find` / `exact?` / `apply?` / `rw?` / `simp?` result,
4. the verified candidate tried in Lean,
5. the final proof fragment or reason no candidate worked.

---

## Part 4 — Type L: Literature Research

**When:** Need to understand what's known about a topic in formal verification literature.

### 4.1 Protocol

```
1. DEFINE SCOPE: What specific question needs answering?
2. SEARCH INTERNAL:
   a. Zettelkasten (existing notes on this topic)
   b. Project docs (tech reports, analysis plans)
3. SEARCH MATHLIB:
   a. Mathlib4 documentation
   b. Mathlib4 GitHub discussions
   c. Lean Zulip chat threads
4. SEARCH EXTERNAL:
   a. arXiv (formal verification, mathematics)
   b. Coq/Isabelle libraries (analogous formalizations)
   c. Conference proceedings (ITP, CPP, IJCAR)
5. SYNTHESIS:
   a. What exists? What's missing?
   b. Can we reuse anything?
   c. What approach works best for our domain?
6. ZK OUTPUT:
   a. Literature note for each significant finding
   b. Permanent note if synthesis reveals a pattern
```

### 4.2 Output

```markdown
## Research: Type L — [topic]
- **Sources consulted:** [list with citations]
- **Key findings:**
  1. [finding + source]
  2. [finding + source]
- **Applicable to Project:** [yes/no/partially]
- **Reusable code/proofs:** [list with locations]
- **ZK notes created:** [ZK-IDs]
```

---

## Part 5 — Type S: Safety & Soundness Research

**When:** Verifying that a formalization is sound, axiom-clean, or safety-relevant.

### 5.1 Protocol

```
1. AXIOM CHECK:
   a. #print axioms for all relevant theorems
   b. Verify only propext, Quot.sound, Classical.choice
   c. Flag any sorryAx immediately (P0)
   
2. VACUITY CHECK:
   a. For each theorem: can the hypotheses be satisfied?
   b. Construct witness values for all existential hypotheses
   c. Check that conclusion is non-trivial given hypotheses
   
3. FAITHFULNESS CHECK (delegate to Φ):
   a. Does the Lean formalization match the paper claim?
   b. Are hypotheses correctly translated?
   c. Is the conclusion logically equivalent?
   
4. BOUNDARY CHECK:
   a. What happens at boundary values (0, 1, ∞)?
   b. Does the result degrade gracefully?
   c. Are there edge cases the paper ignores?
   
5. CROSS-MODULE CHECK:
   a. Do bridge theorems preserve soundness?
   b. Are there type coercions that hide assumptions?
   c. Do namespace qualifications match?
```

### 5.2 Output

```markdown
## Research: Type S — [theorem/module]
- **Axiom status:** [clean / contaminated]
- **Vacuity status:** [non-vacuous / potentially vacuous / vacuous]
- **Faithfulness:** [matches paper / diverges — how]
- **Boundary cases:** [tested / issues found]
- **Cross-module soundness:** [clean / issues]
```

---

## Part 6 — Type D: Design & Architecture Research

**When:** Deciding how to structure definitions, modules, or proof architectures.

### 6.1 Protocol

```
1. UNDERSTAND REQUIREMENTS:
   a. What theorems need this structure?
   b. What properties must be preserved?
   c. What's the intended API?
   
2. SURVEY PATTERNS:
   a. How does Mathlib structure similar concepts?
   b. How do other Project modules handle this?
   c. What Lean 4 idioms apply (typeclasses, structures, abbrev)?
   
3. EVALUATE OPTIONS:
   a. Structure vs class vs inductive
   b. Bundled vs unbundled approach
   c. Namespace organization
   d. Notation choices
   
4. PROTOTYPE:
   a. Write minimal version of each option
   b. Test with one downstream theorem
   c. Compare ergonomics
   
5. RECOMMEND:
   a. Chosen design with rationale
   b. Migration plan if changing existing structure
```

### 6.2 Output

```markdown
## Research: Type D — [design question]
- **Options evaluated:** [list]
- **Recommended:** [option with rationale]
- **Trade-offs:** [what we give up]
- **Migration needed:** [yes/no — scope if yes]
```

---

## Part 7 — Type X: Cross-Domain Research

**When:** Connecting Lean formalization to domain knowledge (AI safety, RL, stochastic systems, etc.)

### 7.1 Protocol

```
1. IDENTIFY DOMAIN: Which domain skill (SK-12..21, SK-32, SK-33) applies?
2. CONSULT DOMAIN SKILL: Read the SKILL.md for domain-specific guidance
3. BRIDGE ANALYSIS:
   a. How does the domain concept map to Lean types?
   b. What domain-specific assumptions are needed?
   c. Are there domain standards to follow?
4. CROSS-REFERENCE:
   a. Do other domains formalize this concept?
   b. Are there analogies across domains?
   c. Can we generalize?
5. DOMAIN EXPERT INPUT:
   a. If Research Council is active: dispatch to relevant member (Α/Β/Γ/Δ/Ε)
   b. If solo: reference domain skill + literature
```

### 7.2 Output

```markdown
## Research: Type X — [domain + topic]
- **Domain:** [AI safety / RL / stochastic / ...]
- **Domain skill consulted:** SK-[N]
- **Concept mapping:** [domain concept → Lean type]
- **Domain assumptions:** [list]
- **Cross-domain connections:** [other domains with similar concepts]
```

---

## Part 8 — Type E: Epistemic Research

**When:** Probing for unknown unknowns or mapping knowledge coverage.

Delegates to epistemic-mapping (SK-23) and research-council (SK-22).

### 8.1 Protocol

```
1. RUN EPISTEMIC AUDIT for target module/theorem
2. For each KU (Known Unknown):
   - Dispatch targeted Type M/T/L research
3. For each UU (Unknown Unknown) PROBE:
   - Cross-domain analogy sweep
   - Boundary testing
   - Hypothesis negation
   - Counterexample hunting
4. UPDATE EPISTEMIC MAP with all transitions
```

See epistemic-mapping SKILL.md for full Rumsfeld matrix methodology.

---

## Part 9 — Research Dispatch Matrix

| Research Type | Primary Skill | Council Member | Domain Skills |
|---|---|---|---|
| Type M (Mathematical) | lean-research (SK-11) | Γ (Methods) | SK-12..17 |
| Type T (Tactic/API) | lean-proof-review (SK-02) | Ν (Novelty) | — |
| Type L (Literature) | lean-research (SK-11) | Ε (Applications) | SK-12..21 |
| Type S (Safety) | lean-enforcement (SK-36) | Σ (Soundness) | SK-18, SK-20 |
| Type D (Design) | lean-specification (SK-05) | Λ (Quality) | — |
| Type X (Cross-domain) | domain skills | Β (Structure) | SK-12..21, 32, 33 |
| Type E (Epistemic) | epistemic-mapping (SK-23) | Α (Foundations) | all |

---

## Part 10 — Research Queue Management

When multiple research tasks are pending:

### 10.1 Priority Rules

```
1. P0: Research blocking a proof that blocks a P0 fix
2. P1: Research for a P1 finding or missing coverage
3. P2: Research for improvement or optimization
4. P3: Exploration or curiosity-driven research
```

### 10.2 Parallelization

Type M and Type T are often independent → can run in parallel.
Type L is always parallelizable (pure read).
Type S should run after Type M (need the proof first).
Type D should run before implementation.
Type E should run at project checkpoints.

### 10.3 Budget Tracking

Each research task has a time budget (from depth levels in SK-11).
If budget exceeded: checkpoint findings, return partial results, suggest continuation.
