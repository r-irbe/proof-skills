# USER_GUIDE.md - proof-skills Practical Operator Guide

`proof-skills` is a project-agnostic toolkit of 65 active v2 Agent Skills (100% <4,000B with paired handbooks), 200 Lean 4 proof and workflow templates (59 core + 131 arithmetic-geometry + 10 fluid-pde), 5 Pure Role-Actor Containers + 23 soul overlays, and an embedded 20-tool MCP server (`tools/lean-lsp-mcp`) for Lean 4 + Mathlib4 formal verification.

---

## 1. Customer Installation Tiers & Environment Setup

`proof-skills` is organized into three progressive installation tiers so customers only install what their workflow requires:

### Tier 1 -- Prompt / Skill Collection Only (`apm install r-irbe/proof-skills`)

```bash
apm install r-irbe/proof-skills                       # install all 65 skills
apm install r-irbe/proof-skills --skill lean-proof    # install a single skill
apm install r-irbe/proof-skills#v0.1.0                # version-pinned
```

- **What APM does**: Hoists `skills/*/SKILL.md` contracts into your agent harness (Copilot, Claude Code, Cursor, Gemini, OpenCode, Codex, Windsurf).
- **What APM 0.x does NOT do**: APM does not run `pip install`, `npm ci`, or `git submodule update --init`.
- **Dependencies required for Tier 1**: **Zero** Python or Node.js packages. The markdown skill contracts and `templates/` work immediately.

### Tier 2 -- Offline Python Scripts, Blueprints, AltProof & Audits

```bash
git clone --recurse-submodules https://github.com/r-irbe/proof-skills.git
cd proof-skills
```

- **Zero-`pip` Core (`Python >= 3.10` standard library only)**:
  - All **44 scripts** in `scripts/lean/*.py` (axiom audit, census, formalization breakdown, proof quality, blueprint sync, zettelkasten lint)
  - All **20 modules** in `scripts/lean/altproof/*.py` (AltProof tactic/route advisor & evaluator)
  - `graph/graph_query.py` (queries `vendor/itp-ontology/master-authority-index.json` and `kuzu/prover_knowledge.kz` archives via stdlib `json`, `csv`, and `zipfile`)
  - `tools/lean-serve-broker/*` and `tools/visualizer/*`
  - `scripts/check-structure` and `scripts/lint/apm_validate.py` (include pure-stdlib YAML fallbacks)
- **Optional Python packages** (declared in [`pyproject.toml`](pyproject.toml) and [`requirements.txt`](requirements.txt)):
  ```bash
  pip install -r requirements.txt      # PyYAML>=6.0 for check_conformance.py, run_eval.py, per_rubric_elo.py
  pip install ".[kuzu]"                # kuzu>=0.7.0 for graph/kuzu_federation.py & graph/export_kuzu.py
  pip install ".[dev]"                 # pytest>=8.0 + PyYAML>=6.0
  pip install ".[all]"                 # PyYAML>=6.0 + kuzu>=0.7.0 + pytest>=8.0
  ```

### Tier 3 -- Full 20-Tool `lean-lsp` MCP Server + Rust/WASM `lean-analyzer`

Run the one-command customer bootstrap and non-mutating environment doctor:

```bash
bash scripts/setup-env.sh              # or: apm run setup (pass --venv to create .venv)
bash scripts/setup-env.sh --doctor     # or: apm run doctor (verifies Python, Node, Lean, MCP, Ontology)
```

- **What `scripts/setup-env.sh` does**:
  1. Deduplicates any global `~/.gemini/config/plugins/proof-skills` mount and initializes `tools/lean-lsp-mcp` git submodule if uninitialized.
  2. Installs/verifies `PyYAML` (into `.venv` when `--venv` is passed, active `$VIRTUAL_ENV`, or `--user`).
  3. Runs `npm ci || npm install` and `npm run build` in `tools/lean-lsp-mcp` (`@modelcontextprotocol/sdk`, `js-yaml`).
  4. Runs the `--doctor` health check and outputs ready-to-paste MCP configuration snippets for Claude Code, Cursor, Gemini CLI, Antigravity, and Copilot.
- **Auto-Bootstrap on First MCP Launch**:
  - `tools/lean-lsp-mcp/bin/lean-lsp-mcp.js` checks for `node_modules/@modelcontextprotocol/sdk` before starting the server. If missing, it automatically runs `npm ci --omit=dev` with all installer output redirected to `stderr` (preserving clean JSON-RPC `stdout`). Any MCP harness launching `bin/lean-lsp-mcp.js` works with zero manual `npm install`.

---

## 2. Skill Routing Architecture (65 Skills)

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

## 4. Verification, Doctor & Linting Commands

Run the built-in health and quality gates from the repository root:

```bash
# 0. Non-mutating environment health check (Python, Node, Lean, MCP, Ontology)
bash scripts/setup-env.sh --doctor    # or: apm run doctor

# 1. Validate APM manifest and skill collection structure
python3 scripts/lint/apm_validate.py --strict
python3 scripts/check-structure --strict --self-test

# 2. Check v2 skill conformance, handoff DAG, and relative links
python3 scripts/skill-audit/check_conformance.py --fail-on any

# 3. Lint the Zettelkasten knowledge graph
python3 scripts/lean/zettelkasten_lint.py --zk-dir zettelkasten --strict

# 4. Run static proof-quality heuristics on a Lean directory
python3 scripts/lean/proof_quality.py --lean-dir <path/to/lean> --output proof_quality.md

# 5. Extract a formalization breakdown or launch the interactive DAG visualizer
python3 scripts/lean/formalization_breakdown.py <path/to/lean> --format summary
python3 tools/visualizer/serve.py --corpus flt --no-browser
```
