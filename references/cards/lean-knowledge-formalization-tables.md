---
name: "lean-knowledge-formalization-tables"
description: "Layer-1 fast 3-table lookup card auto-extracted from references/handbooks/lean-knowledge-formalization-handbook.md."
generated_from: "references/handbooks/lean-knowledge-formalization-handbook.md"
skill_ref: "skills/lean-knowledge-formalization/SKILL.md"
---

# `lean-knowledge-formalization` -- Fast 3-Table Lookup Card (Layer 1)

> Auto-generated from [`../handbooks/lean-knowledge-formalization-handbook.md`](../handbooks/lean-knowledge-formalization-handbook.md) by `scripts/lean/compile_handbook_tables.py`.
> Read this compact card first during interactive proving; open the Layer-2 handbook only when deep derivations or annexes are needed.

## 1. Goal-Shape -> Tactic / Template

| Goal / Term Shape | Primary Tactic / Law | Template / Notes |
| :--- | :--- | :--- |
| Concept lattice subsumption `C  D` | `PartialOrder` / `Lattice` | `exact le_trans hCD hDE` |
| Frame / interval temporal relation `Allen.Before i j` | Interval endpoint inequalities `i.hi < j.lo` | `rcases hi with ...; omega` |
| Epistemic knowledge `K_a  -> ` (T-axiom / truthfulness) | Reflexive Kripke accessibility `R a w w` | `intro hK; exact hK w (h_refl a w)` |
| DAG acyclicity ` Reachable G u u` | Topological rank `rank u < rank v` | `intro h; have := rank_lt_of_reachable h; omega` |
| Interventional distribution `do(X := x)` | Truncated factorization / edge surgery | `unfold intervene; split_ifs <;> simp only [...]` |
| Deontic obligation `Obliged P -> Permitted P` | Standard Deontic Logic (`KD` axiom) | `intro h_ob; exact kd_serial h_ob` |
| ACH diagnosticity matrix score | Weighted sum over evidence rows | `unfold achScore; simp only [...]; omega` |
| Bayesian likelihood update (scaled integer) | Prior * likelihood normalization | `unfold updatePost; omega` |
| Game/wargame dominant strategy `payoff s* b >= payoff s b` | Finite case exhaustion + `omega` | `cases b <;> simp only [payoff] <;> omega` |

## 2. Intent -> Recipe Phrasebook

| Intent | Recommended Pattern / Tool | Recipe |
| :--- | :--- | :--- |
| Prove ontology taxonomy is cycle-free | Assign integer stratum/depth and close with `omega` | Fast kernel check |
| Verify Allen interval algebra composition table | Unfold endpoint bounds `(lo, hi)` with `lo < hi` and run `omega` | Reduces all 13 Allen relations to linear arithmetic |
| Prove Kripke S5 epistemic property | Unfold `Knows` over equivalence relation `Equivalence (R a)` | Use `.refl`, `.symm`, `.trans` |
| Prove finite causal graph is a DAG without path cycles | Witness a strict topological ranking `rank : V -> Nat` | Reduces graph acyclicity to `omega` on `rank u < rank v` |
| Evaluate Pearl Level-3 counterfactual in finite Structural Causal Model | `unfold counterfactual abduce intervene; decide` | Decidable on finite exogenous domains |
| Discharge provenance-chain transitivity | `Relation.TransGen.trans` | Standard transitive closure composition |
| Prove Analysis of Competing Hypotheses (ACH) rank order | `decide` or `omega` on scaled diagnosticity weights | Keep weights in `Nat` or `Int` |
| Verify evidentiary chain-of-custody monotonicity | Lattice meet `min tier1 tier2` via `omega` | Weakest-link provenance bound |
| Prove minimax / saddle-point bound on finite strategy matrix | `decide` (concrete matrix) or `omega` (parametric) | Fast decidable verification |

## 3. Error / Bottleneck -> Fix

| Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Degenerate empty interval breaks Allen transitivity | Missing `i.lo < i.hi` well-formedness invariant | Bundle `lo < hi` inside `structure Interval` |
| Belief (`KD45`) vs Knowledge (`S5`) conflation | Used reflexive `R` for fallible belief | Use serial, transitive, Euclidean (`KD45`) frame for belief |
| Cycle induction hangs on `Reachable` | Missing acyclicity witness | Add `forall  u v, Edge u v -> rank u < rank v` and induct on `rank` |
| Chiseling / contrary-to-duty paradox in deontic model | Naive `Obliged` predicate without world/state transition | Index deontic modalities by pre/post state `(s, s')` |
| Division by zero in normalized posterior | Total evidence weight `sum w = 0` not excluded | Add hypothesis `0 < totalWeight` or cross-multiply before comparing |
| Conflicting hypotheses sum to `> 100` | Unnormalized probability vector | Enforce simplex invariant `sum p_i = 100` in state structure |
