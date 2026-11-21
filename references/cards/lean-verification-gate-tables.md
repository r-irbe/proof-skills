---
name: "lean-verification-gate-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-verification-gate-handbook.md."
generated_from: "references/handbooks/lean-verification-gate-handbook.md"
skill_ref: "skills/lean-verification-gate/SKILL.md"
---

# `lean-verification-gate` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-verification-gate-handbook.md`](../handbooks/lean-verification-gate-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Exported theorem `theorem foo ...` before merge | `lean_axiom_closure` | Verify closure subset of `[propext, Classical.choice, Quot.sound]` |
| Module after `sorry` removal | `lake build <Module>` (cold replay) | Ensure `.olean` cache does not hide unchecked terms |
| File missing `set_option autoImplicit false` | Static enforcement lint | Add `set_option autoImplicit false` immediately after `import` |
| Standalone paper supplement `.tar.gz` | `scripts/lean/cold_kernel_replay.lean` | Replay 100% of slice `.olean` constants via `Lean.Kernel.Environment.replay` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Lock down transitive axioms across corpus | `lean_axiom_closure` + `#print axioms` | Fail CI on `sorryAx`, custom `axiom`, or unapproved `Lean.ofReduceBool` |
| Verify proofs survive fresh kernel check | `scripts/lean/replay_verify.sh` (`R1`--`R3`) | Cold `lake build` + `axiom_audit.py` + `Lean.Kernel.Environment.replay` |
| Gate joint LaTeX paper + Lean supplement | `scripts/lean/paper_supplement_audit.py --strict` | Verify 0 `@[deprecated]` shims, 0 misnomers, `.bib` parity, and `INV-001` Unicode |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `depends on axiom sorryAx` | Unfinished subgoal or upstream `sorry` import | Locate culprit via `lean_axiom_closure` and route to `@lean-proof` |
| `depends on axiom Lean.ofReduceBool` | `native_decide` or `bv_decide` used in strict kernel lane | Replace with `kernel_decide` (`rfl | decide +kernel | omega`) |
| Green axiom gate missed renamed or newly added theorems | Stale generated `#print axioms` probe script (`GT-21`) | Run `python3 scripts/lean/axiom_audit.py --generate-script` and quote scanned counts |
| Verdict cites external checker (`nanoda_lib`) that never ran | Unexecuted boilerplate or wrong-OS binary | Cite only tools physically executed (`Lean.Kernel.Environment.replay`) and quote coverage gaps |
