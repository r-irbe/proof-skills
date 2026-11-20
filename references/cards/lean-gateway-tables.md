---
name: "lean-gateway-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-gateway-handbook.md."
generated_from: "references/handbooks/lean-gateway-handbook.md"
skill_ref: "skills/lean-gateway/SKILL.md"
---

# `lean-gateway` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-gateway-handbook.md`](../handbooks/lean-gateway-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| New informal conjecture or paper section | `specifier` -> `@lean-specification` | Screen with `@counterexample-first-proving` before `@lean-proof` |
| `sorry` goal in existing `.lean` module | `prover` -> `@lean-proof` | Use `lean_goal` + Layer-1 lookup card |
| Slow `rfl` / `decide` or C++/SIMD extraction | `prover`/`editor` -> `@lean-kernel-optimization` | Bridge clean spec via `@[csimp]` twin (`KERNEL-LAW-07`) |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Route a multi-phase formalization campaign | 5-Role Swarm (`Specifier -> Prover -> Auditor -> Editor -> Gardener`) | Pass `templates/handoff_protocol.json` across role boundaries |
| Resolve legacy skill name after v0.4.0 consolidation | `agents/facets/registry.json` (`skill_aliases`) | Map retired slug to its canonical active skill |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Context bloat from loading 50 KB handbooks | Skipped Layer-1 lookup card | Read `references/cards/<slug>-tables.md` (`2-6 KB`) first |
| Generative prover edits its own soundness audit | Role-container boundary violation | Keep `auditor` strictly read-only in a separate subagent turn |
