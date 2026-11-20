---
id: zk-014
title: Two-tier WASM static analyzer and 5-role 21-tool MCP architecture
created: 2026-11-15
updated: 2026-11-15
type: permanent
tags: [mcp, wasm, static-analysis, architecture]
refs:
  - zk-002
  - zk-008
  - zk-013
  - zk-015
status: validated
confidence: high
---

# Two-tier WASM static analyzer and 5-role 21-tool MCP architecture

**Claim.** Static Lean 4 quality enforcement scales cleanly across diverse repositories only when split into a universal **Tier-1 `core` profile** (sub-millisecond `lean_analyzer.wasm` abstract interpretation + universal `lean-rules` YAML checks) and opt-in **Tier-2 domain profiles** (`--profile=kernel|fluid-pde|p2m|all` or `[rules] profile = "kernel"` in `lean-project.toml`, with `paths:` globs), surfaced alongside **21 MCP tools** partitioned across **5 specialist agent roles** (`specifier`, `prover`, `auditor`, `editor`, `gardener`).

**Evidence.** Shipped in `tools/lean-lsp-mcp` (`bin/lean-rules.js`, `wasm/lean_analyzer.wasm` `<= 128 KiB`, `src/sota_engines.ts`) and `ROLES.md`. `lean_analyzer.wasm` catches `Nat` subtraction truncation (`SOUND-04`), division/modulo by zero, `Classical.choice` leakage, and `WellFounded` fuel traps before invoking `lake build`.

**Implication.** Downstream CI (`scripts/lean/enforce_all.sh`) gets zero false-positive domain leakage on general Mathlib repos while retaining strict contest, PDE, and codegen (`N01..N12` in [[zk-013]]) gates when requested. Role-scoped tool surfaces respect the L0 context contract in [[zk-002]], enforce the tactic hierarchy in [[zk-008]], and expose offline concordance search for [[zk-015]].

See also: [[zk-002]], [[zk-008]], [[zk-013]], [[zk-015]].
