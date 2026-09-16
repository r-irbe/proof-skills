# Stanford ACE Prover Swarm -- Multi-Agent Lifecycle Roles

Operational contract for autonomous AI coding agents operating across formal
theorem-proving campaigns in Lean 4.

Strict 7-bit ASCII only.

---

## 1. Overview: The 4-Role Formalization Swarm

To prevent context collapse, persona drift, and proof degradation in long-running
Lean 4 sessions, the formalization lifecycle is divided into four distinct roles:

```text
+-----------------------------------------------------------------------------+
|                     STANFORD ACE PROVER SWARM PIPELINE                      |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [ SPECIFIER ]  ---->  [ PROVER ]  ---->  [ AUDITOR ]  ---->  [ GARDENER ]   |
|   Informal-to-          Interactive         Golfing,           Lemma        |
|   Formal,               LSP Tactics,        Linting,           Indexing,    |
|   Blueprint,            Goal Search,        Sorry-Check,       Zettelkasten |
|   MWE Extraction        Try this            PR Hygiene         Curation     |
|                                                                             |
+-----------------------------------------------------------------------------+
```

Each role operates under strict context boundaries, loaded skills, and verification
gates. Agents transition sequentially and never mix generative proving with long-term
memory curation within the same turn.

---

## 2. Role Specifications

### 2.1 Role 1: Specifier (Architect & Boundary Definer)
- **Mission**: Convert informal mathematical statements or software requirements into
  syntactically valid Lean 4 declarations with formal type signatures, docstrings,
  and dependency graphs.
- **Assigned Skills**:
  - `lean-specification`: Define clean theorem headers and explicit hypotheses.
  - `lean-blueprint`: Construct module dependency DAGs and statement graphs.
  - `lean-mwe`: Extract minimal isolated reproductions for stuck sub-goals.
  - `lean-doc-requirements`: Trace formal statements back to domain specifications.
- **Outputs**: Well-typed `.lean` declarations with `sorry` placeholders, validated
  by `lake build` syntax elaboration.
- **Stop Condition**: Declaration elaborates cleanly without type errors. Hands off
  to **Prover**.

### 2.2 Role 2: Prover (Tactician & Search Engine)
- **Mission**: Discharge goals interactively using the Lean 4 Language Server Protocol,
  following the canonical tactic hierarchy.
- **Assigned Skills**:
  - `lean-proof`: Core interactive proving loop using `plainGoal` and `plainTermGoal`.
  - `lean-setup`: Ensure compiler environment and elan toolchain consistency.
  - `lean-build`: Lake build execution and olean compilation.
  - `lean-gateway`: Route domain-specific lemmas to math facets.
- **Operational Rules**:
  - Never emit `trace_state` or diagnostic comments into project source files.
  - Harvest `Try this` code actions from `exact?`, `simp?`, and `grind?`.
  - Respect the tactic dispatch hierarchy: `rfl` -> `omega` / `linarith` -> `simp only` -> `aesop` -> `exact?`.
- **Stop Condition**: All goals closed (`0 sorry`). Hands off to **Auditor**.

### 2.3 Role 3: Auditor (Reviewer, Golfer & Enforcer)
- **Mission**: Inspect closed proofs for style violations, redundant steps, brittle
  tactics, and project invariants.
- **Assigned Skills**:
  - `lean-proof-review`: Proof golfing, non-terminal `simp` elimination, term-mode translation.
  - `lean-enforcement`: Zero-sorry, zero-warning CI policy gating.
  - `lean-tautology-triage`: Detect vacuous hypotheses and circular proofs.
  - `lean-bisect`: Isolate broken proofs across upstream toolchain bumps.
  - `lean-pr`: Ensure clean worktree, valid git commits, and upstream PR readiness.
- **Outputs**: Refactored, minimized proofs with bounded heartbeats and zero compiler warnings.
- **Stop Condition**: All linters pass and `lake build` is completely green. Hands off
  to **Gardener**.

### 2.4 Role 4: Gardener (Memory Curator & Synthesizer)
- **Mission**: Index newly verified lemmas into cross-session knowledge bases and
  prune failing tactic patterns.
- **Assigned Skills**:
  - `lean-zettelkasten`: Record reusable lemma idioms into the permanent knowledge garden.
  - `lean-retro-methodology`: Extract failure taxonomies and anti-patterns.
  - `lean-retroactive-audit`: Track lemma deprecation and blast radius across modules.
  - `lean-review-council`: Multi-agent consensus review for high-assurance modules.
- **Integration**: Feeds verified patterns into TacitFlow's `curation_engine.py`
  and MAGMA 4-orthogonal graph.
- **Stop Condition**: New patterns indexed; fleeting session scratch memory purged.

---

## 3. Handoff Protocol

Transitions between swarm roles use structured handoff receipts:

```json
{
  "handoff_version": "1.0",
  "from_role": "prover",
  "to_role": "auditor",
  "artifact": "docs/easci/lean/EASCI/Simplex.lean",
  "theorem": "Simplex.interior_nonempty",
  "proof_status": "closed",
  "sorry_count": 0,
  "heartbeats_consumed": 14200,
  "tactics_used": ["intro", "simp only", "omega"],
  "notes": "Proof closed with non-terminal simp; requires golf to simp only."
}
```
