# USER_GUIDE.md - proof-skills Practical Operator Guide

`proof-skills` is a project-agnostic toolkit of 38 active v0.5.0 core Agent Skills (+ 7 opt-in applied-strategy pack skills, 100% <4,000B with Layer-1 lookup cards and Layer-2 handbooks), v3 Lean 4 proof, kernel WHNF, proof-carrying codegen, and AltProof equality-saturation templates, 5 Pure Role-Actor Containers + 24 soul overlays, and an embedded 21-tool MCP server (`tools/lean-lsp-mcp`) for Lean 4 + Mathlib4 formal verification.

---

## 1. Customer Installation Tiers & Environment Setup

`proof-skills` is organized into three progressive installation tiers so customers only install what their workflow requires:

### Tier 1 -- Prompt / Skill Collection Only (`apm install r-irbe/proof-skills`)

```bash
apm install r-irbe/proof-skills                       # install all 38 core skills
apm install r-irbe/proof-skills --skill lean-proof    # install a single skill
apm install r-irbe/proof-skills#v0.5.0                # version-pinned
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
  - All stdlib scripts in `scripts/lean/*.py` (axiom audit, census, formalization breakdown, proof quality, blueprint sync, zettelkasten lint)
  - All **20 modules** in `scripts/lean/altproof/*.py` (AltProof tactic/route advisor & evaluator)
  - `graph/graph_query.py` (queries `vendor/itp-ontology/master-authority-index.json` and `kuzu/prover_knowledge.kz` archives via stdlib `json`, `csv`, and `zipfile`)

The shipped Kuzu archive contains only concepts and tactic concordances derived
from the two vendored Apache-2.0 ontology indexes. Its book and section tables
contain headers for compatibility. Regenerate it with
`python3 graph/export_kuzu.py --profile release --out-dir kuzu`.
The `prover` and `all` profiles build local graphs. Use a separate private output
directory for them. `--export-public` writes the same restricted release
projection even when used alongside a local build.

The project initializer sets `PROVER_KNOWLEDGE_KZ` for the embedded MCP.
Search the release index with `lean_search` and
`{"source":"graph","query":"induction"}`. For tactic mappings use
`{"source":"concordance","query":"induction","target_prover":"lean4"}`.
Section browsing requires a private archive that includes sections.
See the [MCP graph guide](tools/lean-lsp-mcp/USER_GUIDE.md#35-search-and-explore-the-knowledge-graph)
for configuration, result limits and examples.

  - `tools/lean-serve-broker/*` and `tools/visualizer/*`
  - `scripts/check-structure` and `scripts/lint/apm_validate.py` (include pure-stdlib YAML fallbacks)
- **Optional Python packages** (declared in [`pyproject.toml`](pyproject.toml) and [`requirements.txt`](requirements.txt)):
  ```bash
  pip install -r requirements.txt      # PyYAML>=6.0 for check_conformance.py, run_eval.py, per_rubric_elo.py
  pip install ".[kuzu]"                # kuzu>=0.7.0 for graph/kuzu_federation.py & graph/export_kuzu.py
  pip install ".[dev]"                 # pytest>=8.0 + PyYAML>=6.0
  pip install ".[all]"                 # PyYAML>=6.0 + kuzu>=0.7.0 + pytest>=8.0
  ```

### Tier 3 -- Full 21-Tool `lean-lsp` MCP Server + Rust/WASM `lean-analyzer`

The MCP server requires **stable Node.js >=22.6.0** (matching the bundled engine's
`engines.node` requirement), including when using precompiled `dist/index.js`.
The doctor checks canonical `node -v` output (`vMAJOR.MINOR.PATCH`) against this
minimum. Prerelease/nightly versions are not validated or supported by this
check; this does not imply they cannot work. Older Node versions are outside
the supported contract even if a launcher fallback can use precompiled output.
Plugin and Gemini manifests retain `--experimental-strip-types`; APM invokes
the same bin launcher without the outer flag. This version requirement is not
certification of every external agent host or MCP runtime combination.

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

## 2. Skill Routing Architecture (38 Core Skills + 7 Opt-In Pack Skills)

All skills follow the v2 dispatch triad (`USE FOR`, `DO NOT USE FOR`, `TRIGGERS`):

1. **Top-Level Orchestration**:
   - `@lean-gateway`: Routes multi-phase formalization tasks across specification, proving, refactoring, and enforcement.
   - `@lean-gateway`: Defines cross-skill handoffs and lifecycle gates.
2. **Core Lean 4 Proving & Build**:
   - `@lean-setup`: Toolchain pinning (`lean-toolchain`), `elan`, and C FFI sysroot setup.
   - `@lean-build`: Lake build diagnosis and `lake-serve-broker` singleton management.
   - `@lean-proof`: Step-by-step tactic proving (`grind -> omega -> norm_num -> simp only -> ring -> linarith`) using `lean-lsp` MCP (`lean_goal`, `lean_diagnostics`, `lean_counterexample_search`).
   - `@lean-proof-refactor`: Slimming long proofs into shared helper lemmas.
   - `@lean-mwe` & `@lean-bisect`: Minimizing reproducers and bisecting Lean nightlies.
3. **Domain Mathematics & AI Formalization**:
   - `@lean-math-foundations`, `@lean-math-analysis`, `@lean-math-discrete`, `@lean-math-dynamical`, `@lean-math-optimization`, `@lean-math-stochastic`.
   - `@lean-math-dynamical`, `@lean-math-discrete`, `@lean-knowledge-formalization`, `@lean-ai-formalization`.
4. **Quality, Audits, and Exposition**:
   - `@lean-verification-gate`, `@lean-corpus-audit`, `@lean-proof-review`, `@lean-review-council`, `@lean-tautology-triage`, `@lean-verification-gate`.
   - `@lean-blueprint`, `@lean-blueprint`, `@lean-pedagogical-exposition`, `@lean-blueprint`, `@lean-retro-methodology`.

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
