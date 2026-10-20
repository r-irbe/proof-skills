# Lean 4 Language Server Protocol (LSP) Reference Guide

> Authoritative reference on maximizing the Lean 4 Language Server Protocol
> for AI agents, developer tooling, and interactive formalizers.
> Pair with `lean4-lsp-proof-protocol.md`, `lean4-proof-strategy.md`, and
> `lean4-module-dependency-guide.md`. Strict 7-bit ASCII.

---

## 1. Architecture & Daemon Topology

Lean 4 implements a two-tier language server architecture:

```
[Client / Agent / pi-lens]
       | JSON-RPC (stdio)
       v
  [Lake Serve]
       | Watchdog process
       +------------------------------------+
       |                                    |
       v                                    v
[FileWorker: Foo.lean]            [FileWorker: Bar.lean]
  (Elaboration, AST,                (Elaboration, AST,
   Live Proof State)                 Live Proof State)
```

1. **Watchdog (`lake serve`)**:
   - The primary daemon launched by the editor or tool.
   - Parses the project configuration (`lakefile.lean` or `lakefile.toml`), sets up the environment variables (`LEAN_PATH`, `LEAN_SRC_PATH`), and listens for JSON-RPC messages on stdio.
   - It routes document events to dedicated FileWorker child processes.
2. **FileWorkers**:
   - One isolated worker process per active `.lean` file.
   - Performs asynchronous, incremental elaboration and maintains the live proof state.
3. **Server Memory & Execution Safeguards**:
   - To prevent Linux kernel OOM killer (SIGKILL) and C call-stack exhaustion on deep recursive proofs, configure `moreServerArgs` in `lakefile.lean`:
     ```lean
     package my_project where
       moreServerArgs := #["-M", "4096", "-s", "32768", "-D", "maxHeartbeats=500000"]
     ```
   - `-M 4096`: Caps memory at 4 GB before graceful GC/restart.
   - `-s 32768`: Expands stack allocation to 32 MB to prevent recursion crashes during tactic execution.
4. **Sysroot & C Header Resolution**:
   - The Lean toolchain root can be queried instantly without starting a server:
     `lean --print-prefix`
   - Yields `${prefix}/include` and `${prefix}/include/clang` for C FFI bindings and `clangd` integration.

---

## 2. Interactive Proof State (`$/lean/plainGoal`)

The `$/lean/plainGoal` custom JSON-RPC method inspects the tactic proof state at any file position.

### 2.1 Cursor Placement Protocol
- **Active tactic lines**: Place the cursor inside the tactic block, directly after `by`, on an active tactic, or on the line of a `sorry` placeholder.
- **Header placement hazard**: Querying line 1, `theorem`, or declaration headers returns `no goals`. Tools must not interpret header queries as proof completion.
- **Completion detection**: When the query returns `no goals` within an open tactic block, the active goal is closed. Stop emitting tactics immediately.

### 2.2 Inaccessible Dagger Variables (`rename_i`)
When induction, case splits, or macros introduce variables without user-assigned names, Lean tags them with an inaccessible marker (dagger):
```lean
x+ : Nat
h+ : x+ > 0
|- x+ + 1 > 1
```
- **Hazard**: Writing `rw [h+]` or `exact h+` triggers `unknown identifier 'h+'`.
- **Rule**: Inaccessible variables cannot be referenced by name. Always use `rename_i x h` to bring them into scope, or use structured binders (`intro x h`, `rcases ... with <x, hx>`).

---

## 3. Hole-Driven Type Synthesis (`$/lean/plainTermGoal`)

When the structure of a term, constructor, or lemma argument is unknown:
1. Place an underscore placeholder `_` at the argument location.
2. Query `$/lean/plainTermGoal` at the position of `_`.
3. The server returns the exact expected type:
   `expected type: Decidable (a <= b)`
4. Use this expected type to query the library or select constructors deterministically.

---

## 4. Suggestion Harvesting (`textDocument/codeAction`)

Search tactics publish machine-applicable suggestions via standard LSP Code Actions:
- `exact?`: Mathlib search for closing terms.
- `apply?`: Head-symbol lemma search.
- `simp?`: Traces simp applications and produces minimal `simp only [...]` sets.
- `grind?` / `aesop?`: Automation scripts with deterministic replay.

### Harvesting Workflow:
1. Write the search tactic (e.g. `exact?`).
2. Query `textDocument/codeAction` for the line.
3. Match actions titled `Try this: <tactic>`.
4. Apply the edit (`apply: true`) to substitute the concrete proof term.
5. **Invariant**: Never commit bare search tactics to version control.

---

## 5. Sub-10ms Offline Navigation via `.ilean`

Lean 4 produces `.ilean` (Interactive Lean) files during compilation:
- Location: `.lake/build/lib/**/*.ilean` alongside `.olean` binaries.
- Format: Structured JSON storing declaration definitions, references, and symbol ranges.
- **Advantage**: Fast tools can parse `.ilean` directly in < 5 ms to resolve "go-to-definition" and references across millions of lines of Mathlib without starting the Lean server or waiting for FileWorker elaboration.

---

## 6. Cross-Language FFI & Generated C99 Navigation

Lean 4 is a compiled functional language that lowers to C99:
1. **FFI Declarations**:
   - `@[extern "lean_c_func"] opaque cFunc : Nat -> Nat`
   - Jumps from `cFunc` resolve to the native C implementation file in `native/`.
2. **Compiler-Generated C99 (`.lake/build/ir/`)**:
   - Every Lean module has an emitted C intermediate file in `.lake/build/ir/`.
   - Inspecting the generated C file (`operation: "implementation"`) reveals:
     - Unboxed integer/float representations.
     - Reference-counting primitives (`lean_inc`, `lean_dec`).
     - Initialization closures (`_init_` symbols) and boxed wrappers (`___boxed`).

---

## 7. Type Inspection, Implicits & Universe Levels (`textDocument/hover`)

Querying `textDocument/hover` on any symbol provides:
- Fully instantiated types including implicit arguments (`{alpha : Type u}`).
- Universe level parameters (`u_1`, `max u v`).
- Markdown docstrings with syntax annotations.
- Resolves abbreviations and reducible type synonyms without modifying code.

---

## 8. Dot-Notation Probing via Completion (`textDocument/completion`)

In Lean 4, if term `t` has type `Foo`, any function `Foo.bar (self : Foo) : ...` can be called as `t.bar`.
- Typing `t.` and requesting completions returns all functions, projections, and lemmas defined in the `Foo` namespace.
- This allows agents to discover applicable lemmas for a data structure dynamically without manual namespace searches.

---

## 9. Structural Overview: Document & Workspace Symbols

- `textDocument/documentSymbol`: Returns hierarchical outlines of all `inductive`, `structure`, `def`, `theorem`, and `namespace` blocks in the active file.
- `workspace/symbol`: Searches definitions across all compiled modules in the Lake dependency tree.

---

## 10. Module Hierarchy & Blast-Radius Management (`$/lean/moduleHierarchy`)

Lean 4 provides custom module hierarchy navigation:
1. `$/lean/prepareModuleHierarchy`: Prepares the module target.
2. `$/lean/moduleHierarchy/imports`: Forward dependency tree (what this module imports).
3. `$/lean/moduleHierarchy/importedBy`: Reverse dependency tree (what downstream modules import this module).
- **Blast-Radius Check**: Before renaming or changing a theorem signature, query `importedBy` to evaluate the impact across the formalization DAG.

---

## 11. FileWorker Lifecycle & Telemetry (`$/lean/fileProgress`)

The server emits `$/lean/fileProgress` notifications containing:
- `processing: [...]`: Array of file ranges currently being elaborated.
- `fatalError`: Indicates whether the worker crashed or encountered an unrecoverable toolchain error.
- **Pacing Discipline**: Agents must pace edits to wait for a quiet window (empty processing array) before sending subsequent changes. Flooding edits while the FileWorker is running heavy tactics (`omega`, `ring`, `simp`) leads to server cancellation and lag.

---

## 12. 4-Tier Diagnostic Priority & Error Triage

When reviewing compiler and LSP diagnostics, resolve them in strict priority order:

| Tier | Diagnostic Class | Behavior & Handling |
|---|---|---|
| **1** | **Syntax Error** | FileWorker cannot build AST. All downstream diagnostics in the declaration are phantom noise. Fix immediately. |
| **2** | **Elaboration / Type Mismatch** | Tactic or argument fails type-checking. Fix before evaluating goal counts. |
| **3** | **Unsolved Goals (`done`)** | Proof is incomplete. Inspect via `$/lean/plainGoal` (`lean_goal`). |
| **4** | **Linter & Static Abstract Interpretation** | `NatSubTruncation` (`a - b` on `Nat` without `b <= a`), `NatDivModByZero`, unused variables, naming conventions. Inspect via `lean_diagnostics`. |

> **The Golden Rule of Proving**: Never attempt to fix an "unsolved goals" diagnostic at a `by` line when an elaboration error or tactic failure is active on a later line. Always fix the lowest error line first.

---

## 13. Mapping Raw LSP Methods to `lean-lsp` (`r-irbe/lean4-lsp-mcp`) Tools

Agents should invoke the `lean-lsp` MCP tools directly rather than constructing raw JSON-RPC frames:

| Raw LSP / Engine Capability | `lean-lsp` MCP Tool | Example JSON Arguments |
|---|---|---|
| `$/lean/plainGoal` | `lean_goal` | `{"filePath": "Foo.lean", "line": 42, "col": 3, "target": "filtered"}` |
| `$/lean/plainTermGoal` | `lean_goal` | `{"filePath": "Foo.lean", "line": 42, "col": 10, "target": "term"}` |
| AltProof Tactic & Route Advisor | `lean_goal` or `lean_metrics` | `{"filePath": "Foo.lean", "line": 42, "target": "altproof"}` |
| `textDocument/publishDiagnostics` + Abstract Interpretation | `lean_diagnostics` | `{"filePath": "Foo.lean", "maxWaitMs": 4000}` |
| Plausible Counterexample Harness (Galois-pruned) | `lean_counterexample_search` | `{"filePath": "Foo.lean", "theoremName": "my_thm", "strategy": "dense"}` |
| `.ilean` Go-to-Definition (< 5 ms) | `lean_lookup_symbol` | `{"symbol": "MyNamespace.my_thm"}` |
| `.ilean` Declaration References (< 5 ms) | `lean_decl_references` | `{"symbol": "MyNamespace.my_thm", "direction": "both"}` |
| `$/lean/moduleHierarchy` (`imports` / `importedBy`) | `lean_module_hierarchy` | `{"moduleName": "MyProject.QualityGates", "direction": "importedBy", "transitive": true}` |
| Multi-Source Search (Local, Loogle, Ontology, Reservoir, arXiv) | `lean_search` | `{"query": "Finset.sum_le_sum", "source": "code"}` |
| Textbook Index Lookup (65+ curated indexes) | `lean_book_index_lookup` | `{"term": "octagon domain", "book": "cousot"}` |
| Cross-ITP Prover Concordance | `lean_cross_itp_concordance` | `{"concept": "generalizing induction", "source_prover": "coq", "target_prover": "lean4"}` |
| Kernel Trust-Base Check (`#print axioms`) | `lean_axiom_closure` | `{"symbol": "MyNamespace.my_thm", "module": "MyModule"}` |
| Ephemeral `lake env lean --stdin` Probe | `lean_exec` | `{"code": "import Mathlib.Data.Nat.Basic\n#check Nat.sub_add_cancel"}` |
| Force Document Re-Sync | `lean_resync` | `{"filePath": "Foo.lean"}` |
| Broker & Worker Health Status | `lean_server_status` | `{}` |

