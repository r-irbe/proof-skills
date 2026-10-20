# USER_GUIDE.md - proof-skills Practical Operator Guide

`proof-skills` is a project-agnostic toolkit of 75 first-party Agent Skills (+ 4 legacy redirect stubs), 196 Lean 4 proof and workflow templates, 5 specialized sub-agent personas, and an embedded 21-tool MCP server (`tools/lean-lsp-mcp`) for Lean 4 + Mathlib4 formal verification.

---

## 1. Installation & Harness Setup

### Option A: Microsoft APM (Agent Package Manager)

```bash
apm install r-irbe/proof-skills                       # install all 75 skills
apm install r-irbe/proof-skills --skill lean-proof    # install a single skill
```

### Option B: Git Clone / Submodule

```bash
git clone --recurse-submodules https://github.com/r-irbe/proof-skills.git
```

### Option C: Gemini CLI / Claude Code / Copilot CLI

- **Gemini CLI**: `gemini-extension.json` registers `./skills`, the `lean-lsp` MCP server (`tools/lean-lsp-mcp/bin/lean-lsp-mcp.js`), and the Kuzu knowledge graph (`kuzu/lean-knowledge.kz`).
- **Claude Code / Cursor**: Add `lean4-lsp-mcp` to `.mcp.json` and point your skill loader to `skills/`.

---

## 2. Skill Routing Architecture (75 Skills)

All skills follow the v2 dispatch triad (`USE FOR`, `DO NOT USE FOR`, `TRIGGERS`):

1. **Top-Level Orchestration**:
   - `@lean-gateway`: Routes multi-phase formalization tasks across specification, proving, refactoring, and enforcement.
   - `@lean-integration-protocol`: Defines cross-skill handoffs and lifecycle gates.
2. **Core Lean 4 Proving & Build**:
   - `@lean-setup`: Toolchain pinning (`lean-toolchain`), `elan`, and C FFI sysroot setup.
   - `@lean-build`: Lake build diagnosis and `lake-serve-broker` singleton management.
   - `@lean-proof`: Step-by-step tactic proving (`grind -> omega -> norm_num -> simp only -> ring -> linarith`) using `lean-lsp` MCP (`lean_goal`, `lean_diagnostics`, `lean_counterexample_search`).
   - `@lean-proof-refactor`: Slimming long proofs into shared helper lemmas.
   - `@lean-mwe` & `@lean-bisect`: Minimizing reproducers and bisecting Lean nightlies.
3. **Domain Mathematics & AI Formalization**:
   - `@lean-math-foundations`, `@lean-math-analysis`, `@lean-math-discrete`, `@lean-math-dynamical`, `@lean-math-optimization`, `@lean-math-stochastic`.
   - `@lean-convergence-verification`, `@lean-bigraph-modeling`, `@lean-causal-reasoning`, `@lean-nested-learning`.
4. **Quality, Audits, and Exposition**:
   - `@lean-enforcement`, `@lean-quality-engine`, `@lean-proof-review`, `@lean-review-council`, `@lean-tautology-triage`, `@lean-axiom-closure`.
   - `@lean-formalization-breakdown`, `@lean-dag-visualizer`, `@lean-pedagogical-exposition`, `@lean-blueprint`, `@lean-zettelkasten`.

See [`TAXONOMY.md`](TAXONOMY.md), [`ROLES.md`](ROLES.md), and [`FACETS.md`](FACETS.md) for the complete catalog.

---

## 3. Using Templates & Project Overrides

Templates under [`templates/`](templates/) use `<Project>` / `<proj>` placeholders so they stay portable across repositories.

1. Browse [`templates/README.md`](templates/README.md) and [`templates/00-CONVENTIONS.md`](templates/00-CONVENTIONS.md).
2. Copy a `.lean` or `.md` template into your target project and replace `<Project>` with your top-level Lake module namespace.
3. If your project has domain-specific conventions (e.g., fixed-point scaling or custom linters), create a lightweight `skills-overrides/` directory in your host repository that links back to the canonical `proof-skills` skill and records only the local deltas.

---

## 4. Verification & Linting Commands

Run the built-in quality gates from the repository root:

```bash
# 1. Validate APM manifest and skill collection structure
python3 scripts/lint/apm_validate.py

# 2. Check v2 skill conformance, handoff DAG, and relative links
python3 scripts/skill-audit/check_conformance.py

# 3. Lint the Zettelkasten knowledge graph
python3 scripts/lean/zettelkasten_lint.py --zk-dir zettelkasten --strict

# 4. Run static proof-quality heuristics on a Lean directory
python3 scripts/lean/proof_quality.py --lean-dir <path/to/lean> --output proof_quality.md

# 5. Extract a formalization breakdown or launch the interactive DAG visualizer
python3 scripts/lean/formalization_breakdown.py <path/to/lean> --format summary
python3 tools/visualizer/serve.py --corpus flt --no-browser
```
