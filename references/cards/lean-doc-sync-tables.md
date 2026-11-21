---
name: "lean-doc-sync-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-doc-sync-handbook.md."
generated_from: "references/handbooks/lean-doc-sync-handbook.md"
skill_ref: "skills/lean-doc-sync/SKILL.md"
---

# `lean-doc-sync` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-doc-sync-handbook.md`](../handbooks/lean-doc-sync-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Informal paper theorem `\begin{theorem}` | `requirements` mode -> 3-part spec | Extract Preconditions, Postconditions, and Witness for `@lean-specification` |
| Completed `@[blueprint]` graph | `scripts/lean/blueprint_to_report.py` | Compile dependency-ordered LaTeX report sections |
| Paper appendix theorem/module table | `scripts/lean/metric_sync.py` | Re-derive exact counts from compiled `.olean` census |
| Conference paper + Lean 4 concordance | `Concordance.lean` + `paper_supplement_audit.py` | Pair every numbered claim & walkthrough arithmetic check with `#check` + `#print axioms` |
| Double-blind CMT/HotCRP Lean supplement | `altproof tree-shake --anonymize --verify-build` | Emit declaration-shaken slice + metadata-scrubbed `.tar.gz` + root `LICENSE` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Verify every Lean name cited in LaTeX exists | `scripts/lean/check_citations.py` | Check `file:line` and identifier parity against compiled tree |
| Review documentation draft for undefined terms | `feedback` mode readability pass | Flag forward references, missing assumptions, and scope overclaims |
| Audit `.bib`, terminology, `INV-001` & supplement | `scripts/lean/paper_supplement_audit.py --strict` | Verify `filecontents*` `.bib` parity, 0 BibTeX/Overfull warnings, 0 misnomers, and 0 `@[deprecated]` shims |
| Document honest proof provenance & novelty | Three-Tier Provenance Section | Partition credit into Tier 1 (`Mathlib`/`Cslib`), Tier 2 (adapted/newly proved classical), and Tier 3 (novel domain results) |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Broken `foo.lean:123` citation in docs | Line numbers shifted after refactoring | Prefer declaration-anchored references and re-run `check_citations.py` |
| Prose claims theorem proved while `sorry` or facade stub remains | Premature paper sync before `@lean-verification-gate` | Strengthen upstream Lean theorem or calibrate paper statement to exact proved hypotheses |
| Coined/spliced mathematical misnomer (`Polyak-Doob`, `Presburger` on squares) | Unverified eponymous naming | Cross-check primary literature, delete `@[deprecated]` shims (`GT-66`), and run `paper_supplement_audit.py` |
| Embedded `filecontents*` `.bib` drifts from standalone `.bib` | Manual edit applied to only one file | Synchronize byte-for-byte and gate with `paper_supplement_audit.py --tex ... --bib ...` |
| Paper cites external checker (`nanoda_lib`) never run on final slice | Unverified boilerplate copied from prior prose | Cite only tools physically executed (`Lean.Kernel.Environment.replay` via `cold_kernel_replay.lean`, `GT-67`) |
