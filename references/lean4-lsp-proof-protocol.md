# Lean 4 Interactive LSP Proof Protocol (ILPL) & `lean-lsp` MCP Reference

> Practical guide for AI proving agents and formalizers interacting with Lean 4
> via the `lean-lsp` (`r-irbe/lean4-lsp-mcp`) MCP server, `pi-lens`, `vscode-lean4`,
> or `lean.nvim`. Pair with `lean4-lsp-guide.md`, `lean4-proof-strategy.md`, and
> `lean4-tactic-hierarchy.md`. Strict 7-bit ASCII.

---

## 1. Core Principles

Traditional batch theorem proving relies on editing source files with exploratory
tactics (`trace_state`, `done`), saving to disk, running `lake build`, and parsing
compiler output. This batch loop introduces disk churn, git noise, and high latency.

The Interactive LSP Proof Protocol replaces file-polluting exploratory probes with
real-time Language Server Protocol and `.ilean` index queries via `lean-lsp`:

1. **Zero-Disk-Churn Inspection**: Never write `trace_state` to disk. Query the
   live goal state directly via `lean_goal` (or `pilens_lsp_navigation(operation: "goal")`).
2. **Counterexample-First Falsification**: Before spending tactic iterations on a
   new or modified lemma, run `lean_counterexample_search` to check whether a
   concrete assignment refutes the statement.
3. **AltProof & Static Abstract Interpretation**: Query `lean_goal(target: "altproof")`
   or `lean_diagnostics` to inspect ranked tactic recommendations, route hints, and
   static abstract-interpretation certificates (`NatSubTruncation` on `a - b` without
   `b <= a`, `NatDivModByZero` on `/ d` without `0 < d`).
4. **Hole-Directed Synthesis**: Use `_` (AST holes) with expected-type queries
   (`lean_goal(target: "term")`) to deduce constructor arguments and lemma requirements.
5. **Hygienic Name Discipline**: Respect Lean 4 macro hygiene. Never reference
   inaccessible variables (`x+`) directly; bind them explicitly via `rename_i` or `rcases`.

---

## 2. Complete `lean-lsp` MCP Tool Matrix (21 Tools)

In Antigravity, invoke these tools via `call_mcp_tool` with `ServerName: "lean-lsp"`.
In Claude Code / Cursor / Copilot, invoke `mcp__lean-lsp__<ToolName>` directly.

### 2.1 Primary Interactive Proving & Verification Tools

| Tool Name | Required Args | Key Optional Args | Purpose & Speed |
| :--- | :--- | :--- | :--- |
| `lean_goal` | `filePath`, `line` | `col` (1-indexed), `target` (`"tactic" \| "term" \| "filtered" \| "altproof"`), `hideTypeclasses`, `hideInaccessible`, `onlyTarget`, `goal`, `proof` | Live tactic goal state, expected term type at `_`, or AltProof tactic/route advisor (~50-200 ms) |
| `lean_diagnostics` | `filePath` | `maxWaitMs` (default `4000`) | Live compiler errors, warnings, unsolved goals, and static `NatSubTruncation` / `NatDivModByZero` certificates (~100-500 ms) |
| `lean_counterexample_search` | `filePath`, `theoremName` | `strategy` (`"slice" \| "dense"`), `samples` (default `100`), `budgetMs` (default `60000`), `imports` | Synthesizes & runs a Plausible test in an isolated scratch dir using Galois-pruned domains (~2-15 s) |
| `lean_exec` | `code` | `timeoutMs` (default `15000`) | Ephemeral `lake env lean --stdin` execution (`#check`, `#eval`, `#synth`) without file edits (~1-3 s) |
| `lean_resync` | `filePath` | *(none)* | Forces disk re-read and `textDocument/didChange` version bump when live goals look stale (~50 ms) |
| `lean_server_status` | *(none)* | *(none)* | Reports `lake serve` broker attachment, project root, open files, and worker RSS (< 10 ms) |

### 2.2 Sub-5ms Offline `.ilean` Navigation & Dependency DAG Tools (No `lake serve` Needed)

| Tool Name | Required Args | Key Optional Args | Purpose & Speed |
| :--- | :--- | :--- | :--- |
| `lean_lookup_symbol` | `symbol` | *(accepts alias `name` / `query`)* | Offline `.ilean` jump-to-definition: exact file path, line/col range, and module (< 5 ms) |
| `lean_decl_references` | `symbol` | `direction` (`"uses" \| "usedBy" \| "both"`), `limit` (default `50`) | Offline declaration-level reference graph from `.ilean` (< 5 ms) |
| `lean_module_hierarchy` | `moduleName` | `direction` (`"imports" \| "importedBy" \| "both"`), `transitive` (bool), `maxDepth` | Forward `imports` and reverse `importedBy` DAG traversal with cycle detection (< 5 ms) |
| `lean_dependency_subgraph` | `moduleName` | `maxDepth` (default `5`), `format` (`"mermaid" \| "dot" \| "json"`) | Renders local import subgraph around a module (< 10 ms) |

### 2.3 Unified Search, Book Indexes & Cross-ITP Concordance Tools

| Tool Name | Required Args | Key Optional Args | Purpose & Speed |
| :--- | :--- | :--- | :--- |
| `lean_search` | `query` | `source` (`"code" \| "loogle" \| "ontology" \| "arxiv" \| "datasets" \| "reservoir" \| "book" \| "concordance" \| "symbol" \| "graph"`), `limit`, `prover`, `book` | Unified search across local code, Loogle, LeanSearch, Reservoir, arXiv, Kuzu graph, and ITP ontology |
| `lean_book_index_lookup` | `term` | `book` (corpus substring, e.g. `"cousot"`), `prover` (`"lean4" \| "coq" \| "isabelle" \| "hol_light"`) | Searches 65+ author-curated back-of-the-book indexes (`*.index.json`) (< 10 ms) |
| `lean_cross_itp_concordance` | `concept` | `source_prover`, `target_prover` | Translates proof concepts & tactics across Lean 4, Coq/Rocq, Isabelle, HOL Light, Agda (< 10 ms) |

### 2.4 Metrics, Audits, Blueprints & FFI Tools

| Tool Name | Required Args | Key Optional Args | Purpose & Speed |
| :--- | :--- | :--- | :--- |
| `lean_metrics` | `target` | `action` (`"census" \| "hierarchy" \| "subgraph" \| "bigraph" \| "axiom_audit" \| "altproof"`), `format`, `goal`, `proof` | Consolidated census, Milner Place-Link bigraph projection, static axiom/sorry audit, and AltProof analysis |
| `lean_module_census` | `targetPath` | `format` (`"markdown" \| "json" \| "summary"`) | Fast declaration & line census over a file or directory |
| `lean_axiom_closure` | `symbol` | `module` (declaring module to import first) | Kernel trust-base check via `#print axioms <symbol>` |
| `lean_blueprint` | *(none)* | `action` (`"status" \| "scaffold" \| "zettel" \| "skeleton" \| "walkthrough" \| "graph_neighborhood"`), `symbol`, `filePath`, `formalizationDir`, `blueprintDir` | Audits `\leanok` / `\uses` coverage or generates LaTeX scaffolds, proof skeletons, walkthroughs, and Zettels |
| `lean_blueprint_scaffold` | `symbol` | `filePath`, `line` | Generates LaTeX `\begin{theorem}...\leanok` scaffold for a declaration |
| `lean_proof_skeleton` | `filePath` or `symbol` | *(none)* | Extracts statement + `have`/`obtain`/`calc`/`induction` milestone outline |
| `lean_ffi` | *(none)* | `action` (`"inspect_env" \| "resolve_symbol" \| "verify_headers" \| "sysroot"`), `externName`, `cHeaderPath` | Inspects Lean 4 `@[extern]` C FFI bindings and `lean --print-prefix` sysroot headers |

---

## 3. The 6-Phase Interactive Proving Loop

```text
+------------------------------------------------------------------+
| Phase 0: Falsify & Audit Domain Guardrails                       |
| - Run lean_counterexample_search(filePath, theoremName, "dense") |
| - Run lean_diagnostics(filePath) to catch NatSubTruncation       |
+---------------------------------+--------------------------------+
                                  |
                                  v
+------------------------------------------------------------------+
| Phase 1: Orient                                                  |
| - Query lean_goal(filePath, line, col, target: "filtered")       |
| - Query lean_goal(filePath, line, target: "altproof") for advice |
+---------------------------------+--------------------------------+
                                  |
                                  v
+------------------------------------------------------------------+
| Phase 2: Explore & Synthesize                                    |
| - Insert hole '_' and query lean_goal(filePath, line, col,       |
|   target: "term") for exact expected type                        |
| - Search missing lemmas via lean_search(query, source: "code")   |
+---------------------------------+--------------------------------+
                                  |
                                  v
+------------------------------------------------------------------+
| Phase 3: Harvest Suggestions                                     |
| - Probe candidate lemmas with lean_exec(code: "#check ...")      |
| - Or run exact? / simp? and harvest via LSP codeAction           |
+---------------------------------+--------------------------------+
                                  |
                                  v
+------------------------------------------------------------------+
| Phase 4: Isolate & Structure                                     |
| - Focus multiple branches with '.' (dot) or 'case TAG =>'        |
| - Resolve hygienic daggers with rename_i                         |
+---------------------------------+--------------------------------+
                                  |
                                  v
+------------------------------------------------------------------+
| Phase 5: Blast Radius & Trust Closure                            |
| - Query lean_module_hierarchy(moduleName, direction:"importedBy")|
| - Verify lean_axiom_closure(symbol, module) & clean diagnostics  |
+------------------------------------------------------------------+
```

---

## 4. Phase 1: Live Goal Inspection (`lean_goal`)

### 4.1 Cursor Placement (1-Indexed!)
The Lean 4 language server computes goals relative to the active tactic sequence:
- **Correct placement**: Place `line` (1-indexed) immediately after `by`, on an active
  tactic line, or on the line containing `sorry`.
- **Header placement hazard**: Querying line 1 or the `theorem` header line returns
  `no goals`. Do not misinterpret `no goals` on a header line as a completed proof.
- **Filtered mode**: Pass `target: "filtered"` (or `hideTypeclasses: true`,
  `hideInaccessible: true`) to strip ambient typeclass clutter on heavy algebraic goals.

### 4.2 Reading the Proof State
A standard Lean 4 proof state contains:
```lean
1 goal
case zero
n : Nat
h : n = 0
|- n + 0 = n
```
- **Local Context**: Lines above `|-` are hypotheses currently in scope (`n : Nat`, `h : n = 0`).
- **Target**: The proposition below `|-` is the goal that must be proved to close this branch.
- **Completion**: When the query returns `no goals` inside a tactic block, the proof
  branch at this position is complete. Stop emitting tactics.

### 4.3 Hygienic Inaccessible Variables (The Dagger Symbol)
When tactics (`intro`, `cases`, `rcases`, `induction`) or macros introduce variables
without user-assigned names, Lean tags them with a dagger (`x+`, `h+`):
- **Hazard**: Emitting `rw [h+]` or `exact h+` fails with `unknown identifier`.
- **Rule**: Inaccessible dagger variables cannot be referenced by name. You must either:
  1. Bring them into scope with `rename_i x h`, or
  2. Use structured binders that name variables explicitly: `intro x h` or
     `rcases h with <x, hx>`.

---

## 5. Phase 2: Hole-Driven Term Synthesis & AltProof Advisor

### 5.1 Expected Term Type (`target: "term"`)
When constructing complex terms or finding the right lemma arguments:
1. Place an underscore placeholder `_` where the term is required.
2. Query `lean_goal` with `{"filePath": "...", "line": L, "col": C, "target": "term"}`
   at the position of the underscore.
3. Lean returns the exact expected type constraint (e.g. `expected type: Decidable (a <= b)`).

### 5.2 AltProof Hybrid Tactic & Route Advisor (`target: "altproof"`)
When stuck on a proof obligation or looking for a cleaner proof route:
1. Query `lean_goal` with `{"filePath": "...", "line": L, "target": "altproof"}`
   (or offline via `lean_metrics` with `{"target": "...", "action": "altproof", "goal": "...", "proof": "..."}`).
2. AltProof returns:
   - Ranked tactic recommendations (`omega`, `ring`, `positivity`, `linarith`, `simp_all`, `Finset.sum_le_sum`) with estimated heartbeat costs.
   - Structural transformation routes (simplex x100 normalization, BigOp Fubini swaps, PDG channel folding).
   - Static abstract-interpretation certificates (`NatSubTruncation`, `NatDivModByZero`) and Zone-domain termination hints.

---

## 6. Phase 3: Fast Ephemeral Probing (`lean_exec`) & Suggestion Harvesting

Instead of editing a large `.lean` file just to test `#check` or a small lemma shape:
1. Call `lean_exec` with `{"code": "import Mathlib.Data.Nat.Basic\n#check Nat.sub_add_cancel"}`.
2. When using search tactics (`exact?`, `apply?`, `simp?`, `grind?`, `aesop?`) inside a file:
   - Harvest the `Try this:` suggestion from `lean_diagnostics` (or `pilens_lsp_navigation(operation: "codeAction")` when using `pi-lens`).
   - **Enforcement**: Bare search tactics (`exact?`, `apply?`, `simp?`) MUST NOT remain in committed code.

---

## 7. Phase 4: Multi-Goal Structuring & Case Focus

When an induction, case-split, or constructor splits a theorem into multiple branches:
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

## 8. Phase 5: Dependency Impact & Trust-Base Verification

Before refactoring, renaming, or modifying a theorem statement:
1. Query reverse module dependents in < 5 ms via `.ilean`:
   `lean_module_hierarchy` with `{"moduleName": "MyProject.QualityGates", "direction": "importedBy", "transitive": true}`
2. Query declaration-level callers:
   `lean_decl_references` with `{"symbol": "MyProject.QualityGates.gatePass", "direction": "usedBy"}`
3. After closing the proof, verify the kernel axiom closure:
   `lean_axiom_closure` with `{"symbol": "MyProject.QualityGates.gate_monotone", "module": "MyProject.QualityGates"}`

---

## 9. Summary Checklist for AI Provers

- [ ] Did I use `lean_goal` and `lean_diagnostics` instead of inserting `trace_state` or running blind `lake build` loops?
- [ ] On a questionable statement, did I run `lean_counterexample_search` (`strategy: "dense"`) before spending proof budget?
- [ ] Did I place the `lean_goal` cursor (`line`, 1-indexed) inside the `by` tactic block rather than on the theorem header?
- [ ] Did I check `lean_diagnostics` for `NatSubTruncation` (`a - b` on `Nat` without `b <= a`) and `NatDivModByZero`?
- [ ] Are there inaccessible dagger variables in the context that need `rename_i`?
- [ ] Have I replaced all exploratory search tactics (`exact?`, `simp?`) with their concrete suggested scripts?
- [ ] Does `lean_axiom_closure` confirm only standard axioms (`propext`, `Classical.choice`, `Quot.sound`)?

