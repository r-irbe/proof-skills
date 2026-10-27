---
name: "lean-proof-review-handbook"
description: "Reference handbook for @lean-proof-review."
extracted_from: "skills/lean-proof-review/SKILL.md"
---

# Lean 4 Proof Review

Systematic review of Lean 4 proofs across four layers: formal soundness, statement correctness, non-triviality, and proof quality. Covers the standard Lean 4 + Mathlib automation stack and optional project tactic libraries.

## The Lean 4 Automation Stack

Commonly imported automation packages across Lean 4 projects:

| Import | Package | What it provides |
|---|---|---|
| `Mathlib.Tactic` | Mathlib | `omega`, `simp`, `norm_num`, `linarith`, `nlinarith`, `ring`, `positivity`, `decide`, `exact?`, `apply?`, `rw?`, `conv`, `ext`, `gcongr`, `polyrith`, `field_simp` |
| `Aesop` | Aesop (via Mathlib) | `aesop`, `aesop?`, `@[aesop]` rule attributes |
| `Duper` | Duper | `duper [lemmas]` superposition prover |
| `Auto.Tactic` | lean-auto | `auto [lemmas] u[unfolds]` monomorphization bridge to Duper |
| `Qq` | Qq | Type-safe quotations (`Q(...)`, `q(...)`) for metaprogramming custom tactics |
| `Canonical` | Canonical | `canonical [hints]` exhaustive DTT term search |
| `Cslib` | CSLib | Automata, complexity, algorithms foundations |

---

## Proof Search Priority

When a goal is not immediately obvious, try tactics in this order. **Prefer earlier entries** — they produce higher-quality, more readable proofs:

| Priority | Tactic | When to use | Quality |
|---|---|---|---|
| 1 | `grind` | Mixed LIA + equality + ring + case-splitting. Subsumes ~54% of omega, ~64% of linarith. Use for any goal mixing integer arithmetic with equalities. | Best first choice |
| 2 | `omega` | Pure Nat/Int linear arithmetic, gate thresholds, scaled integers | Excellent — transparent |
| 3 | `simp [lemmas]` | Definitional unfolding, SimplexVec, regime classification | Good if lemma list explicit |
| 4 | `norm_num` | Concrete numeric evaluation (100-scale, discriminants) | Excellent — numeric |
| 5 | `linarith` / `nlinarith` | Real-valued linear/nonlinear arithmetic (Lyapunov, convex) | Good — arithmetic |
| 6 | `ring` / `ring_nf` | Polynomial identities (cusp potential, outer products) | Excellent — algebraic |
| 7 | `positivity` | Non-negativity goals (`0 ≤ x^2`, `0 ≤ a * b`) | Good — structured |
| 8 | `decide` | Concrete finite evaluations (enum cases, bounded checks) — prefer over `native_decide` (which adds `Lean.ofReduceBool` / `Lean.trustCompiler`) | Opaque — evaluation |
| 16 | `auto [lemmas] u[unfolds]` | lean-auto bridge — monomorphizes then calls Duper | Opaque — first-order |
| 17 | `duper [lemmas]` | Direct superposition (trust simplex, envelope commutativity) | Opaque — superposition |
| 18 | `canonical [hints]` | Exhaustive DTT term search (small finite goals) | Semi-transparent |
| 19 | `aesop` | General-purpose heuristic search (last resort — slow on large goals) | Opaque — heuristic |

---

## Tool-by-Tool Usage Guide

### Mathlib Decision Procedures (Priority 1–6)

These are the most trustworthy tactics with well-understood algorithms:

```lean
-- omega: linear Nat/Int arithmetic (fully verified)
example (a b c : Nat) (h : a + b + c = 100) : a ≤ 100 := by omega

-- simp: equational simplification (prefer simp only [...] for stability)
example : List.length [1, 2, 3] = 3 := by simp

-- norm_num: concrete numeric computation
example : (2 : ℝ) ^ 10 = 1024 := by norm_num

-- linarith / nlinarith: ordered field arithmetic
example (x : ℝ) (hx : 0 ≤ x) (hx1 : x < 1) : x ^ 2 < 1 := by nlinarith [sq_nonneg (1 - x)]

-- ring / ring_nf: polynomial identity
example (a b : ℝ) : (a + b) ^ 2 = a ^ 2 + 2 * a * b + b ^ 2 := by ring

-- positivity: non-negativity of expressions
example (x : ℝ) : 0 ≤ x ^ 2 + 1 := by positivity
```

**Review flags:**
- `simp` without lemma list (non-terminal) → brittle; flag as 🟡 Style
- `simp` and `omega` do NOT unfold custom definitions → use `unfold myDef` or `simp [myDef]` first
- `native_decide` adds `Lean.trustCompiler` to axioms → prefer `decide` unless infeasible

### lean-auto + Duper Bridge (Priority 15–16)

The `auto` tactic monomorphizes higher-order Lean goals into first-order logic, then calls Duper (superposition prover). The bridge monomorphizes goals and invokes `Auto.duperRaw`.

```lean
-- auto: monomorphization + Duper (best for propositional/FOL goals)
example (P Q : Prop) (h : P → Q) (hp : P) : Q := by auto
example (P Q : Prop) (h : P ∧ Q) : Q ∧ P := by auto

-- auto with lemma hints
example (a b : Nat) (h : a + b = 100) : b + a = 100 := by
  auto [Nat.add_comm a b, h]

-- duper: direct superposition (provide only relevant lemmas)
example (a b c : Nat) (h1 : a = b) (h2 : b = c) : a = c := by duper [h1, h2]

-- duper for propositional tautologies
example (P Q : Prop) (h : P ∧ Q) : Q ∧ P := by duper [h]

-- duper with compound lemma chains
example (a b c d : Nat) (h1 : a = b) (h2 : b = c) (h3 : c = d) : a = d := by
  duper [h1, h2, h3]
```

**When to use:**
- `auto` → propositional tautologies, FOL implications, universal quantification
- `duper [lemmas]` → equality chains, commutativity, transitivity, disjunctive syllogism

**Review flags:**
- `duper` without lemma list → inefficient; Duper lacks a relevance filter, provide only relevant lemmas
- `auto` fails silently if monomorphization cannot handle the type-theoretic features → fall back to manual case split then `duper`
- Check `#print axioms` after `duper` — proof reconstruction can fail
- Debug monomorphization: `set_option duper.monomorphization.debug true`
- Prefer `duper?`/`auto` suggested replacements when available

### Canonical Term Search (Priority 17)

Exhaustive DTT term search using iterative deepening with entropy-based ordering.

```lean
-- canonical: exhaustive search (always provides a suggested replacement)
example : True := by canonical

-- canonical with hints to narrow search space
canonical [hint_lemma1, hint_lemma2]

-- count := n generates n inhabitants (check uniqueness)
canonical (count := 5)
```

**When to use:**
- Small finite goals that stump other tactics
- When you want a human-readable proof term (Canonical always suggests a replacement)
- 84% success rate on Natural Number Game problems

**Review flags:**
- Bare `canonical` in final proof → replace with the suggested readable term
- `count := n` producing multiple inhabitants → statement may be underspecified
- Search space grows exponentially without hints → always provide `[hints]`

### Aesop Heuristic Search (Priority 18)

Best-first search with configurable rules. Available through Mathlib.

```lean
-- aesop: heuristic search (last resort)
example : P := by aesop

-- aesop?: generates proof script for cleanup (always prefer this)
example : P := by aesop?
-- Output: Try this: exact ⟨fun a => a.2, fun a => ⟨trivial, a⟩⟩
```

**Rule types:** `norm` (always applied), `safe` (eager, must progress), `unsafe N%` (heuristic).

```lean
-- Register custom aesop rules
@[aesop safe apply]    theorem my_safe : A → B := ...
@[aesop unsafe 50%]    theorem my_risky : A → B := ...
@[aesop norm simp]     theorem my_simp : f x = g x := ...
@[aesop norm unfold]   def myDef := ...
@[aesop safe constructors] structure MyStruct where ...
```

**Builders:** `apply`, `forward`, `destruct`, `constructors`, `cases`, `simp`, `unfold`, `tactic`.

**Tracing:** `set_option trace.aesop true` / `set_option trace.aesop.profile true`.

**Review flags:**
- Bare `aesop` in final proof → replace with `aesop?` output
- `aesop` closing a "hard" goal instantly → re-check hypotheses
- `aesop` on arithmetic goals → should use `omega`/`linarith`/`nlinarith` instead
- `aesop` won't unfold custom project definitions → use `simp [myDef]` first

### Qq Metaprogramming (Custom Tactic Engine)

Custom project tactics are typically built with Qq (type-safe quotations) and the `Lean.Elab.Tactic.Meta` API. Qq provides `Q(...)` for type-level quotes and `q(...)` for term-level quotes.

**Review flags for custom tactics:**
- Custom tactic hiding a failing sub-step → check which inner tactic actually closes the goal

### CSLib (CS Foundations)

Provides automata theory, complexity classes, and algorithm foundations. Used for formalizing state machines, DAGs, and algorithmic bounds.

**Review flags:**
- CSLib extends list literal syntax → do NOT use `[` inside `/-- ... -/` doc comments on `unsafe def` blocks (use `--` comments instead)
- CSLib API may overlap with Mathlib for some structures → prefer Mathlib versions for consistency

---

## Project Helper & Custom Tactic Libraries

Before proving a new helper lemma or introducing a custom tactic macro, check the target repository's shared tactic/lemma modules:

1. **Custom tactic macros:** Prefer transparent Mathlib or core tactics (`omega`, `simp only`, `norm_num`, `linarith`, `ring`, `positivity`, `decide`) over opaque catch-all cascade macros.
2. **Shared helper lemmas:** Check existing domain helper modules before adding duplicate arithmetic, bound, or structural lemmas.
3. **Core-only profile:** In core-only Lean 4 projects without Mathlib (see `@lean-core-only`), restrict tactics to `omega`, `decide`, `simp`, `rfl`, `exact`, `apply`, `rw`, and structural induction.

---

## Four-Layer Verification Checklist

### Layer 1: Formal Soundness

1. **`#print axioms my_theorem`** — must show only `propext`, `Classical.choice`, `Quot.sound`.
   - `sorryAx` → proof is incomplete (🔴 fatal).
   - `Lean.ofReduceBool` / `Lean.trustCompiler` → `native_decide` used (🔴 block in standard-axiom-locked projects; replace with kernel-checked `decide`).
   - Any custom `axiom` → conditional validity; audit the axiom (🟠).
2. **`lean4checker --fresh MyModule`** — independent kernel re-verification from `.olean` files.
3. **No `sorry`, `admit`, `apply?`, `exact?`, `rw?`** left in the proof.
4. **`lake build` produces 0 errors, 0 warnings.**

Note: Blue checkmarks (✓✓) appear even when a *dependency* uses `sorry`. Always run `#print axioms`.

### Layer 2: Statement Correctness

1. **Informal translation test:** Write the statement in plain English. Does it match the intended claim?
2. **Boundary case test:** Empty, zero, degenerate inputs — do hypotheses exclude them?
3. **Missing hypothesis checklist:**
   - Non-emptiness: `[Nonempty α]` or `(h : s.Nonempty)`?
   - Distinctness: `(h : a ≠ b)`?
   - Positivity/non-zero: `(h : n > 0)` or `(h : x ≠ 0)`?
   - Finiteness: `[Fintype α]` or `(h : Set.Finite s)`?
   - Decidability: `[DecidableEq α]`?
4. **Instant closure red flag:** If `simp`, `trivial`, `rfl`, `omega`, `decide`, `aesop`, or `duper` closes a "hard" theorem instantly → suspect missing hypothesis or vacuous truth.

### Layer 3: Non-Triviality

1. **Theorem-search check** — use
   [`theorem-search`](../../references/theorem-search.md) to check
   Mathlib, project helpers, and local tactic suggestions before accepting a
   custom proof.
   - `#check` known names and namespace candidates.
   - `#find` statement patterns such as `_ + _ = _ + _`.
   - Loogle with constants, `|-` conclusion filters, and comma intersections.
   - `exact?`, `apply?`, `rw?`, and `simp?` in the local goal state.
   - Remove diagnostic search commands from the final proof.
2. **Triviality classification:** vacuously true → definitionally trivial → computationally trivial → already exists → non-trivially correct → genuinely novel
3. **Dead-end check:** Does this lemma get used downstream, or is it isolated?
4. **Duplicate check:** Search the repository's shared lemma modules before adding new helpers.

For high-risk non-triviality questions, route to
[`lean-tautology-triage`](../lean-tautology-triage/SKILL.md). Use it when a
statement looks like a placeholder (`: True`), smoke theorem, reflexive `rfl`
self-projection, bare `decide` closure, or automation-only proof whose name
suggests a stronger mathematical claim.

### Layer 4: Proof Quality

1. **Readability:** Uses `calc`, `have`, `show` for multi-step arguments?
2. **Modularity:** Sub-arguments > 3 steps extracted as named lemmas?
3. **Tactic choice:** Uses the highest-priority tactic that works (see table above)?
4. **Anti-patterns to flag:**
   - Giant `simp` sets (> 10 lemmas without structure)
   - `decide` taking more than a few seconds
   - Long `omega`/`linarith` with irrelevant hypotheses
   - Repeated `rw` chains without `calc` (> 4 rewrites)
   - `native_decide` in standard-axiom-locked modules (adds `Lean.ofReduceBool` / `Lean.trustCompiler`; replace with `decide`)
   - Monolithic proofs > 20 tactic steps without named sub-lemmas
   - `duper` without lemma hints
   - any `proj_*` tactic use (all DEPRECATED — 0 uses; replace with specific Mathlib tactic)
   - Bare `aesop` / `canonical` without extracting the suggested proof script
   - `: True` theorem/lemma conclusions unless explicitly marked as smoke tests
   - Single-line `by decide` or `by rfl` proofs on names that claim semantic
     correspondence, equivalence, convergence, safety, or optimality
5. **Docstring:** Theorem has a docstring describing the mathematical content?

---

## Common Lean Pitfalls (Review Flags)

### Critical Pitfalls

- **`autoImplicit` enabled:** Variables silently introduced as implicit. Prefer `set_option autoImplicit false` in every module.
- **`sorry` in dependencies:** Blue checkmarks appear even when a dependency uses `sorry`. Always run `#print axioms`.
- **`have` vs `let` for data:** `have` erases the value (proof irrelevance); use `let` when the computed value is needed later.
- **Prop vs Bool confusion:** `Prop` is erased; `Bool` is computable. Mixing them causes subtle issues with `decide` and `if`.
- **Not checking distinctness:** Forgetting `a ≠ b` makes injectivity lemmas trivially true.

### Arithmetic Pitfalls

- **Natural number subtraction:** `Nat.sub` is truncating — `3 - 5 = 0`. Prefer rewriting to addition.
- **Division by zero:** `n / 0 = 0` and `n % 0 = n` in Lean. Ensure denominators non-zero by hypothesis.
- **Integer division truncation:** `Nat.div` truncates. Proofs about `(a * b) / c` need `have : c ∣ (a * b)`.
- **`Fin` wrapping:** `Fin n` arithmetic wraps mod `n`. `(5 : Fin 3) = (2 : Fin 3)`.

### Tactic Pitfalls

- **Non-terminal `simp`:** Brittle mid-proof. Use `simp only [...]` or `simp_all`.
- **Tactics don't unfold custom defs:** `simp`/`omega` don't unfold custom definitions. Use `unfold myDef` or `simp [myDef]`.
- **Rewriting under binders:** `rw` cannot rewrite inside `fun x =>` or `∀ x,`. Use `simp only [lemma]`, `conv`, or `ext`.
- **`native_decide` trust surface:** Adds `Lean.ofReduceBool` / `Lean.trustCompiler` to the axiom closure. Prefer kernel-checked `decide` unless explicitly carved out.
- **`b > a` vs `a < b`:** Not definitionally equal. Use `show a < b` or `change a < b`.
- **CSLib doc comment pitfall:** Do NOT use `[` inside `/-- ... -/` on `unsafe def` blocks (CSLib extends list literals).

### Style Pitfalls

- **Not accounting for `0`:** Many Mathlib lemmas require `0 < n` or `n ≠ 0`.
- **Partial functions:** `List.head!`, `Array.get!` use `panic!`. Prefer total versions with proof arguments.
- **Ignoring warnings:** Unused variables, deprecated syntax — fix them.
- **Ambiguous unicode:** `∈` for set vs list membership — different types, same symbol.

---

## Project-Level Review Checks

1. **`set_option autoImplicit false`** — present in modules where project conventions require explicit binders?
2. **Representation consistency** — no unbridged mixing of numeric representations (`Nat` / `Int` / `Rat` / `Real`)?
3. **Structural invariants** — domain invariants carried explicitly through theorem hypotheses or structure fields?
4. **Minimal imports** — module imports match the project profile (e.g. Mathlib vs `@lean-core-only`)?
5. **Specification traceability** — theorem links to its specification, blueprint node, or paper claim when applicable?
6. **Naming conventions** — structures `PascalCase`, definitions `camelCase`, theorems `snake_case`?
7. **Reusable lemma duplication** — is the helper already in Mathlib or the project's shared lemma modules?
8. **Automation transparency** — opaque `duper`/`auto`/`canonical`/`aesop` proofs replaced with suggested readable scripts?

## Review Workflow

### Solo Review (Single Agent)

1. **Read the theorem statement** first. Translate to English. Check hypotheses.
2. **Run `#print axioms`** on the theorem.
3. **Check for duplicates** — does a Mathlib or project helper lemma already cover this?
4. **Assess tactic choice** — is the highest-priority tactic used? (See priority table.)
5. **Scan for pitfalls** from the checklist above.
6. **Check project conventions** — naming, imports, specification references.
7. **Run `lake build`** — 0 errors, 0 warnings.
8. **Report findings** with severity: 🔴 Fatal, 🟠 Warning, 🟡 Style, ✅ Clean.

### Council Review (5-Member RALPH Protocol)

For high-assurance reviews, this skill is executed by the **Review Council** (`lean-review-council` skill). Each council member runs the checks for their layer in a RALPH loop:

| Member | Symbol | Executes | Focus |
|---|---|---|---|
| Kernel Guardian | Σ | Layer 1 | `#print axioms`, sorry/admit, build |
| Statement Oracle | Φ | Layer 2 | English translation, missing hypotheses, vacuous truth |
| Novelty Scout | Ν | Layer 3 | `exact?`, Loogle, helper duplicates, triviality |
| Quality Architect | Λ | Layer 4 | Tactic priority, step count, modularity, docstrings |
| Integration Sentinel | Ω | Cross-cutting | autoImplicit, conventions, build, paper cross-refs |

Each member votes (✅ 🟡 🟠 🔴) after their RALPH Review+Analyze. A single 🔴 blocks. See `lean-review-council` skill for full voting protocol, disagreement resolution, topologies, and document templates.

### Ring Audit Protocol (High-Assurance)

When using Ring topology (see [`references/lean-review-council-handbook.md` Part 4, Topology 6](../../references/lean-review-council-handbook.md)), each member audits one adjacent member's findings after the primary review:

| Reviewer | Audits findings of | Audit focus |
|---|---|---|
| Σ | Ω | Do integration findings affect axiom cleanliness? |
| Φ | Σ | Does soundness pass confirm the statement is right (not just provable)? |
| Ν | Φ | Are statement corrections actually novel or re-discovered Mathlib results? |
| Λ | Ν | Are "novel" results written with adequate quality? |
| Ω | Λ | Do quality refactorings maintain cross-module conventions? |

**Audit actions:** For each finding, the auditor marks CONFIRM / UPGRADE / DOWNGRADE with a one-line justification. Disagreements enter SDR scoped to that single finding.

### Pre-Review Enforcement Gate

Before any council session begins, the following automated checks **must pass**:

```bash
# Mandatory pre-review gate
./scripts/council_precheck.sh [module_path]
```

This script runs:
1. `lake build` — must produce 0 errors
2. `axiom_audit.py` — flags `sorryAx` / `trustCompiler`
3. Convention checks — `autoImplicit`, naming, section numbering
4. Git status — no uncommitted changes in target module

If the gate fails, the council does not convene — the Implementer must fix gate failures first.

### Post-Review Calibration

After a council session closes:
1. All findings are logged with member ID and severity
2. Overruled findings are tagged as `false_positive`
3. Post-merge defects are retroactively tagged as `false_negative` against the responsible member
4. `calibration_tracker.py` updates member calibration scores
5. Members in `Degraded` tier (< 0.70) trigger mandatory re-read of this skill and Zettelkasten review

### RALPH Loop Integration

Each review step above maps to the RALPH cycle:
- **Review** = steps 1–7 (execute checks)
- **Analyze** = step 8 (classify and report)
- **Learn** = update Zettelkasten with patterns found
- **Plan** = create todo items for fixes
- **Handle** = implement fixes, then re-enter Review

### Topology Selection Quick Reference

| Scope | Recommended | See |
|---|---|---|
| Single theorem, standard | Star | `lean-review-council` Topology 1 |
| Single theorem, high-assurance | Ring | `lean-review-council` Topology 6 |
| File (2-30 theorems) | Pipeline | `lean-review-council` Topology 2 |
| File (30+ theorems) | Swarm | `lean-review-council` Topology 5 |
| File (quick triage) | Hub-Spoke | `lean-review-council` Topology 7 |
| Multi-file (dependencies) | Mesh | `lean-review-council` Topology 3 |
| Full project | Hierarchical | `lean-review-council` Topology 4 |

---

## See also

- [`../../templates/Template_ProofStrategy.md`](../../templates/Template_ProofStrategy.md) — Template: Proof methodology cheat sheet
- [`../../templates/Template_Verification.md`](../../templates/Template_Verification.md) — Template: Verification completeness checklist
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Generic proof-cleanup and dependent-rewrite patterns

---

## Operational Details (from `skills/lean-proof-review/SKILL.md`)

# lean-proof-review

> ⚠️ **MANDATORY** (hot-tier): layers L1 (soundness) and L2 (statement) are
> hard gates — a failure at either MUST block sign-off, regardless of L3/L4.
> Skipping Persist = incomplete.

## Routing

- **USE FOR:** auditing a single Lean 4 proof or file across the 4-layer checklist (L1 soundness, L2 statement, L3 non-triviality, L4 quality);
  cross-checking that imported tactics from the project automation stack are used correctly; spotting common pitfalls (vacuous truth, unused hypothesis,
  broken simp set, scope drift).
- **DO NOT USE FOR:** authoring the proof (delegate to `@lean-proof`); convening a multi-agent review (delegate to `@lean-review-council`); running the CI
  scripts (delegate to `@lean-enforcement`).
- **TRIGGERS:** proof review, audit proof, verify Lean, 4-layer checklist, lean-pitfalls, proof quality.

## Behavioural rules (G-*)

- **G-1** (MUST): The reviewer MUST run the four layers in order (L1 → L2 → L3 → L4); a failure at L1 or L2 MUST halt the review. [Trace: AC-01]
- **G-2** (MUST): The reviewer MUST verify the theorem statement matches the source spec / paper / requirement before judging the proof. [Trace: AC-02]
- **G-3** (MUST NOT): The reviewer MUST NOT silently rewrite the proof; suggested rewrites MUST be flagged as suggestions for the author. [Trace: AC-03]
- **G-4** (SHOULD): The reviewer SHOULD recommend the higher-quality tactic when a lower-priority one was used unnecessarily (see
  [`REFERENCE.md`](./REFERENCE.md) "Proof Search Priority"). [Trace: AC-04]
- **G-5** (MUST): A non-trivial theorem with a one-tactic `decide` / `aesop` / `grind` close MUST be flagged for L3 (non-triviality) review. [Trace: AC-05]
- **G-6** (SHOULD NOT): The reviewer SHOULD NOT mark a proof "approved" without confirming `lake build` is green on the containing file. [Trace: AC-06]
- **G-7** (MUST): Every flagged finding MUST cite the layer, the line(s), and the rule from `REFERENCE.md` or `GUARDRAILS.md`. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — read the target file, locate the theorem(s), find the source spec and any prior review record.
2. **L1 soundness** [validate] — confirm no `sorry`, no `admit`, no `sorryAx`, and no unauthorized `Lean.ofReduceBool` via `lean_axiom_closure`
   (`{"symbol": "...", "module": "..."}`) and `lean_diagnostics` (`{"filePath": "..."}`); defer to `@lean-enforcement` for full-module axiom audit if
   needed.
3. **L2 statement** [validate] — diff the theorem statement against the spec / paper; enforce **Check 5** (Necessity & Sufficiency `↔` Pairing for executable `Bool` checkers — no `ONE_WAY_BOOL_CHECKER`), **Check 6** (Precondition Tightness & Boundary Counterexample Witness — no `NAT_SUB_UNGUARDED` or `MISALIGNED_DOCSTRING`), and **Check 7** (100% Barrel Completeness & `Classical.choice`-Free Constructive Gate); check `lean-analyzer` static diagnostics (`NatSubTruncation`, `NatDivModByZero`, `HypothesisEcho`, `ReflexiveTautology`, `NatNonnegTriviality`, `UnusedUnderscoreBinder`, `OneWayBoolChecker`, Zone DBM `decreasing_by` synthesis, Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop widening, trace partitioning) for silent statement distortions; halt if it has drifted.
4. **L3 non-triviality** [validate] — confirm the hypothesis is non-vacuous; run automated vacuity and specification-fidelity detectors (`python3 scripts/lean/proof_quality.py`, `python3 scripts/lean/tautology_scan.py`, and `lean_metrics` with `action: "proof_fidelity"` in `lean-lsp-mcp`) to catch `HYPOTHESIS_ECHO`, `REFLEXIVE_TAUTOLOGY`, `NAT_NONNEG_TRIVIALITY`, `NAT_SUB_UNGUARDED`, `MISALIGNED_DOCSTRING`, `UNUSED_VALUE_OR_UNDERSCORE_BINDER`, and `ONE_WAY_BOOL_CHECKER`; use `lean_counterexample_search` (`{"filePath": "...", "theoremName": "...", "strategy": "dense"}`, backed by Galois-guided hypothesis domain pruning via `analyzeHeaderHypothesisDomains` / `pruneHeaderNatDomain`) when a statement or helper lemma looks suspect, and hand off to `@lean-tautology-triage` on P1/P2 flags.
5. **L4 quality** [validate] — run `lean-rules` (`node tools/lean-lsp-mcp/bin/lean-rules.js`) and `pi-lens` (`pilens_ast_grep_search`, `pilens_diagnostics`) as sub-second structural pre-checks before `lake build`, plus `lean_goal` (`target: "altproof"`) to evaluate proof-search priority (`bv_decide` for `BitVec`/SWAR goals, `constructive-decidable-reduction` to eliminate `Classical.choice` leakage, `SWAR_BIT_PACKING_SUBSTITUTION`) and two-axis elegance/heartbeat cost; flag tactic mis-selection, bare `simp`, dagger-variable references, unused hypothesis, and fragile rewrite chains; suggest improvements but do NOT apply them.
6. **Persist** [persist] *(MANDATORY)* — write the review record (per-layer status, findings, suggestions) to the repository's review log, link it from the
   theorem, update sign-off state. Skipping Persist = incomplete.

## Recovery & STOP

- L1 fails (`sorry` / `admit` / `sorryAx`) → STOP, do NOT proceed to L2-L4; escalate to author.
- L2 fails (statement drift) → STOP, escalate to spec owner before any proof judgement.
- `lake build` red on containing file → STOP, ask author to fix build first.
- Confidence < 90 % on a tactic suggestion → mark as advisory, do NOT block.
- Scope drift (edits to non-proof files) → immediate STOP, re-anchor.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/proof-review/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the full project automation stack, proof-search priority table, reusable `Tactics` lemma library,
  common Lean pitfalls, and the 4-layer verification checklist (original v1 content, preserved verbatim).
- **Mathlib-specific review:** see [`../../references/upstream/mathlib4-review.md`](../../references/upstream/mathlib4-review.md) for the Mathlib PR review
  delta (attributes/API, simp squeezing, normal forms, transparency, file size, canonical naming/style URLs). The former `lean-proof-review` SKILL has been
  demoted to a REDIRECT stub pointing at this reference (W4 Wave 1 / move A2).

## Common failure modes

> AI agents commonly: rewrite the proof inline instead of suggesting changes;
> approve at L4 without confirming L1/L2 passed; miss vacuous-truth L3
> failures behind a clean `aesop` close; cite a pitfall without quoting line
> numbers or the source rule; accept an "independent routes" claim without
> checking it — when a project claims two or more independent proofs of one
> theorem, verify the routes actually share no machinery (imports, helper
> lemmas, substrate definitions) before repeating the independence claim in
> a review verdict. Full registry: GUARDRAILS.md §Agent failure taxonomy.
