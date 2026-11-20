# `proof-skills` `v0.5.0` Architecture

`proof-skills` (`v0.5.0`, pinned to Lean `v4.34.1`) is organized into five strictly decoupled layers:

1. **Skill & Progressive Disclosure Layer (`skills/`, `packs/`, `references/`)**:
   - **38 Core Lean 4 Skills** (`skills/*/SKILL.md`, each `< 4,000 B` with `<= 320`-char dispatch descriptions) + **7 Opt-In Applied-Strategy Pack Skills** (`packs/applied-strategy/skills/*/SKILL.md`).
   - **4-Layer Progressive Reference Stack**: L0 `SKILL.md` -> L1 fast lookup cards (`references/cards/*-tables.md`) -> L2 encyclopedic handbooks (`references/handbooks/*-handbook.md`) -> L3 machine-queryable `vendor/itp-ontology/handbook-tables.v1.json` (`394` compiled rows) + canonical Kuzu graph [`kuzu/prover_knowledge.kz`](kuzu/prover_knowledge.kz) (`15,481` zettels) and [`graph/procedural-graph.v1.json`](graph/procedural-graph.v1.json).

2. **Multi-Agent Role-Actor & Soul Layer (`agents/`, `ROLES.md`, `FACETS.md`)**:
   - **5 Pure Role-Actor Containers** ([`agents/specifier.md`](agents/specifier.md), [`agents/prover.md`](agents/prover.md), [`agents/auditor.md`](agents/auditor.md), [`agents/editor.md`](agents/editor.md), [`agents/gardener.md`](agents/gardener.md)) with role-scoped allowlists spanning all **21 `lean-lsp` MCP tools**.
   - **24 Specialist Soul Overlays** (`agents/souls/*.md`) and **5 Domain Facets** (`core`, `math`, `ai`, `governance`, `multi-prover`) bound in [`agents/facets/registry.json`](agents/facets/registry.json).

3. **AltProof `v0.5.0` Tactics & Kernel WHNF Superoptimization (`packages/altproof/`, `templates/core/`)**:
   - **Pure-Lean `AltProof.Core`** (`import Lean` only): 20-route `routeTable`, bounded equality saturation (`eqsat_rw` / `egg_rw`), Core `MetaM` backward chaining (`backchain`), `grind_close`, `contra_direct`, `kernel_decide`, and compile-time term superoptimizers (`eval_nat%`, `preunfold%`, `swar_unroll%`).
   - **Mathlib `AltProof.Tactics`**: `sum_congr_ring`, `calc_ring_sum`, `finset_nonneg`, `finset_mono`, `gcongr_pos`, `alt_proof`, `elegance?`, `bfs_elegance?`.
   - **42 Kernel WHNF Laws (`KERNEL-LAW-01..28`)**, Abstraction-Concrete Duality (`WAVE-13 G1`), and proof-carrying C++/SIMD/CUDA codegen (`Template_ProofCarryingCodegen.{md,lean}`, `Template_KernelWHNF.{md,lean}`).

4. **Embedded `lean-lsp` MCP (`v0.8.0`) & Two-Tier WASM `lean-rules` (`tools/lean-lsp-mcp/`)**:
   - **21 MCP Tools** backed by the `102,368 B` Rust/WASM `lean-analyzer` abstract interpreter (intervals, congruences, bitmasks, zones, octagons, WTO widening, 8-category proof fidelity audit).
   - **Two-Tier `lean-rules` Engine**: `16` universal `core`/`default` rules + `7` opt-in profile rules (`--profile={kernel,fluid-pde,p2m,all}` (or `[rules] profile = "kernel"` in `lean-project.toml`)), wired into [`scripts/lean/enforce_all.sh`](scripts/lean/enforce_all.sh).

5. **Deterministic CI & Confidentiality Gates (`scripts/`, `tests/`, `.github/workflows/`)**:
   - Offline contract evaluator ([`scripts/eval/run_eval.py`](scripts/eval/run_eval.py)) across **45** skill smoke cases + **15** domain cases, [`scripts/lint/privacy_audit.py`](scripts/lint/privacy_audit.py), [`scripts/check-structure`](scripts/check-structure), [`scripts/skill-audit/check_conformance.py`](scripts/skill-audit/check_conformance.py), and `PROOF_SKILLS_REQUIRE_LEAN=1 pytest`.
