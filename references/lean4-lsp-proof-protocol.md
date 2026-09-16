# Lean 4 Interactive LSP Proof Protocol (ILPL)

> Practical guide for AI proving agents and formalizers interacting with Lean 4
> via Language Server Protocol (LSP) tools (such as pi-lens, vscode-lean4, or
> lean.nvim). Pair with `lean4-proof-strategy.md` and `lean4-tactic-hierarchy.md`.

---

## 1. Core Principles

Traditional batch theorem proving relies on editing source files with exploratory
tactics (`trace_state`, `done`), saving to disk, running `lake build`, and parsing
compiler output. This batch loop introduces disk churn, git noise, and high latency.

The Interactive LSP Proof Protocol replaces file-polluting exploratory probes with
real-time Language Server Protocol queries:

1. **Zero-Disk-Churn Inspection**: Never write `trace_state` to disk. Query the
   live goal state directly via LSP.
2. **Automated Suggestion Harvesting**: Use search tactics (`exact?`, `simp?`,
   `grind?`, `aesop?`) in combination with LSP Code Actions to automatically
   substitute verified proof terms with zero manual copy-pasting.
3. **Hole-Directed Synthesis**: Use `_` (AST holes) with expected-type queries
   (`termGoal`) to deduce constructor arguments and lemma requirements.
4. **Hygienic Name Discipline**: Respect Lean 4 macro hygiene. Never reference
   inaccessible variables directly; bind them explicitly.

---

## 2. The 5-Phase Interactive Proving Loop

```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Orient                                        │
│ Query lsp_navigation(operation: "goal")                │
│ Inspect hypotheses and target proposition              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: Explore & Synthesize                          │
│ Insert hole '_' and query termGoal                     │
│ Retrieve precise expected type constraints             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: Harvest Suggestions                           │
│ Try exact?, apply?, or simp?                           │
│ Apply "Try this:" suggestions via codeAction           │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 4: Isolate & Structure                           │
│ Focus multiple branches with '.' (dot) or 'case <tag> =>'    │
│ Resolve hygienic daggers with rename_i                 │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 5: Blast Radius Check                            │
│ Query moduleImportedBy before signature edits          │
│ Confirm clean lake build with zero errors/warnings     │
└────────────────────────────────────────────────────────┘
```

---

## 3. Phase 1: Live Goal Inspection

### 3.1 Cursor Placement
The Lean 4 language server computes goals relative to the active tactic sequence:
- **Correct placement**: Place the cursor immediately after `by`, on an active tactic
  line, or on the line containing `sorry`.
- **Header placement**: Querying line 1 or declaration headers returns `no goals`.
  Do not misinterpret `no goals` on a header line as a completed proof.

### 3.2 Reading the Proof State
A standard Lean 4 proof state contains:
```lean
1 goal
case zero
n : Nat
h : n = 0
⊢ n + 0 = n
```
- **Local Context**: Lines above `⊢` are hypotheses currently in scope (`n : Nat`, `h : n = 0`).
- **Target**: The proposition below `⊢` is the goal that must be proved to close this branch.
- **Completion**: When the query returns `no goals`, the proof branch at this position
  is complete. Stop emitting tactics.

### 3.3 Hygienic Inaccessible Variables (The Dagger Symbol)
When tactics (`intro`, `cases`, `rcases`, `induction`) or macros introduce variables
without user-assigned names, Lean tags them with a dagger:
```lean
x✝ : Nat
h✝ : x✝ > 0
⊢ x✝ + 1 > 1
```
- **Hazard**: Emitting `rw [h✝]` or `exact h✝` fails with `unknown identifier 'h✝'`.
- **Rule**: Inaccessible dagger variables cannot be referenced by name. You must either:
  1. Bring them into scope with `rename_i x h`, or
  2. Use structured binders that name variables explicitly: `intro x h` or
     `rcases h with ⟨x, hx⟩`.

---

## 4. Phase 2: Hole-Driven Term Synthesis (`termGoal`)

When constructing complex terms or finding the right lemma arguments:
1. Place an underscore placeholder `_` where the term is required.
2. Query `lsp_navigation(operation: "termGoal", path: "...", line: L, character: C)`
   at the position of the underscore.
3. Lean returns the exact expected type constraint (e.g. `expected type: Decidable (a ≤ b)`).
4. Use this type constraint to query Loogle, `#check`, or local hypotheses rather
   than guessing constructor structures.

---

## 5. Phase 3: Suggestion Harvesting via Code Actions

Lean 4 provides search tactics that compute candidate lemmas:
- `exact?`: Searches Mathlib and local context for an exact proof term.
- `apply?`: Finds lemmas whose conclusion matches the goal head.
- `simp?`: Traces simp applications and produces minimal `simp only [...]` sets.
- `grind?` / `aesop?`: Produces deterministic replay scripts.

### Harvesting Protocol:
1. Insert the search tactic (e.g. `exact?`) at the open goal position.
2. Query LSP code actions:
   `lsp_navigation(operation: "codeAction", path: "...", line: L, character: C)`
3. The server returns a code action with the title `Try this: exact ...`.
4. Run the code action with `apply: true` to automatically replace `exact?` with the
   concrete proof term, or extract the replacement string directly.
5. **Enforcement**: Bare search tactics (`exact?`, `apply?`, `simp?`) MUST NOT remain
   in committed code. They are exploratory tools and must be replaced by the concrete
   terms they suggest.

---

## 6. Phase 4: Multi-Goal Structuring & Case Focus

When an induction, case-split, or constructor splits a theorem into multiple branches:
```lean
2 goals
case zero
⊢ 0 + 0 = 0

case succ
n : Nat
ih : n + 0 = n
⊢ (n + 1) + 0 = n + 1
```

- **Default Focus Rule**: In Lean 4, tactics apply to the **first goal only**. Emitting
  tactics against an unfocused multi-goal state risks applying steps to the wrong branch.
- **Structuring Requirement**: Always isolate goals using focus blocks (`.` or bullet) or explicit
  case tags:
  ```lean
  induction n with
  | zero =>
    rfl
  | succ n ih =>
    rw [Nat.add_succ, ih]
  ```

---

## 7. Phase 5: Dependency Impact Analysis

Before refactoring, renaming, or modifying a theorem statement:
1. Query reverse module dependents:
   `lsp_navigation(operation: "moduleImportedBy", path: "Module.lean")`
2. The server returns every downstream file in the formalization DAG that imports
   the target module.
3. Inspect these downstream files to evaluate the blast radius of proposed signature changes.

---

## 8. Summary Checklist for AI Provers

- [ ] Am I using `goal` via LSP instead of inserting `trace_state` into the file?
- [ ] Did I place the cursor inside the tactic block rather than on the theorem header?
- [ ] Are there inaccessible `✝` variables in the context that need `rename_i`?
- [ ] If multiple goals exist, did I isolate branches with '.' or 'case'?
- [ ] Have I replaced all exploratory search tactics (`exact?`, `simp?`) with their
      suggested scripts?
- [ ] Does `lake build` compile completely clean with 0 errors, 0 warnings, and 0 `sorry`?
