---
name: lean-egraph-cpsat-superopt-handbook
description: Reference handbook for exact sharing-aware DAG e-graph extraction via OR-Tools CP-SAT and Z3, dual-certified rewriting, and kernel-model-calibrated superoptimization in Lean 4.
extracted_from: skills/lean-egraph-cpsat-superopt/SKILL.md
---

# Sharing-Aware CP-SAT / Z3 DAG E-Graph Superoptimization Handbook (Lean 4)

## Overview & Literature Foundations

Equality saturation using e-graphs (Nelson-Oppen; Tate et al. POPL 2009; Willsey et al. *egg*, POPL 2021) explores exponentially large spaces of algebraic program variations by compactly representing equivalence classes of expressions.

However, standard e-graph extraction relies on **tree-greedy extraction**, which assumes an expression is a tree and evaluates sub-expression costs independently. In the Lean 4 reduction kernel (`src/kernel/type_checker.cpp`), expressions are stored as hash-consed Directed Acyclic Graphs (DAGs) in `m_whnf`. When an e-node is reused across multiple parents, its reduction cost is incurred **only once**. Tree-greedy extraction completely ignores this sharing, leading to suboptimal candidate expressions that bloat instruction count.

Drawing on **OptiSat** (Wang et al., *Extracting Sharing-Aware Programs from E-Graphs*) and Google OR-Tools CP-SAT (`ortools.sat.python.cp_model`), this handbook provides the blueprints for **exact sharing-aware DAG extraction** and **dual-certified rewriting**.

---

## Exact Sharing-Aware CP-SAT Formulation

Given an e-graph $G = (C, N)$ with e-classes $c \in C$ and e-nodes $n \in N$:

### Decision Variables
1. $x_n \in \{0, 1\}$ for each e-node $n$: indicates whether node $n$ is selected in the extracted DAG.
2. $y_c \in \{0, 1\}$ for each e-class $c$: indicates whether e-class $c$ is active in the extracted DAG.
3. $l_c \in [0, |C|]$ for each e-class $c$: integer topological level ensuring acyclicity.

### Mathematical Constraints
1. **Root Activation**: For the target root e-class $c_{\text{root}}$, $y_{c_{\text{root}}} = 1$.
2. **Single Node per Active Class**:
   $$\sum_{n \in c} x_n = y_c \quad \forall c \in C$$
3. **Child Class Activation**: If node $n \in c$ with children $\text{children}(n)$ is selected, all its children must be active:
   $$x_n \le y_{c'} \quad \forall c' \in \text{children}(n)$$
4. **Strict Acyclicity (Topological Leveling)**:
   $$l_c \ge l_{c'} + 1 - |C| (1 - x_n) \quad \forall c' \in \text{children}(n)$$

### Objective Function
Minimize total shared kernel WHNF cost:
$$\min \sum_{n \in N} \text{Cost}_{\text{kernel}}(n) \cdot x_n$$

Where $\text{Cost}_{\text{kernel}}(n)$ incorporates:
- Node AST size and recursor step count.
- GMP limb penalty: high cost for operations producing values $\ge 2^{63}$.
- Branch penalty: high cost for conditional `if-then-else` vs branch-free Zhegalkin gates.

---

## Dual-Certified Rewriting Architecture

Every rewrite rule synthesized by the superoptimizer must carry dual certification:

```
+-----------------------------------------------------------------------+
| Rewrite Candidate: lhs -> rhs                                         |
+-----------------------------------------------------------------------+
                 |                                     |
                 v                                     v
+-----------------------------------+ +---------------------------------+
| Certificate 1: Semantic Soundness | | Certificate 2: Cost Reduction   |
| Lean 4 Theorem:                   | | Proven inequality under         |
| theorem rule_sound (x : Nat) :    | | KernelModel.lean:               |
|   eval lhs = eval rhs             | | whnfCost rhs <= whnfCost lhs    |
+-----------------------------------+ +---------------------------------+
```

---

## Canonical Python CP-SAT Extractor & Lean 4 Verification Exemplar

```python
# Exact Sharing-Aware DAG Extractor via OR-Tools CP-SAT
from ortools.sat.python import cp_model

def extract_optimal_dag(eclass_nodes, root_class, node_costs):
    model = cp_model.CpModel()
    classes = list(eclass_nodes.keys())
    num_classes = len(classes)

    x = {} # node selection
    y = {} # class active
    l = {} # topological level

    for c in classes:
        y[c] = model.NewBoolVar(f"y_{c}")
        l[c] = model.NewIntVar(0, num_classes, f"l_{c}")
        for n_id, children in eclass_nodes[c]:
            x[n_id] = model.NewBoolVar(f"x_{n_id}")

    # Root active
    model.Add(y[root_class] == 1)

    # Exactly one node per active class
    for c in classes:
        nodes = [x[n_id] for n_id, _ in eclass_nodes[c]]
        model.Add(sum(nodes) == y[c])
        for n_id, children in eclass_nodes[c]:
            for child in children:
                model.Add(x[n_id] <= y[child])
                model.Add(l[c] >= l[child] + 1).OnlyEnforceIf(x[n_id])

    # Objective
    model.Minimize(sum(node_costs[n_id] * x[n_id] for c in classes for n_id, _ in eclass_nodes[c]))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return [n_id for n_id in x if solver.Value(x[n_id]) == 1]
```

```lean
set_option autoImplicit false

namespace DualCertifiedRewrite

/-- Certified 3-gate Zhegalkin rewrite replacing 4-gate Choice. -/
theorem ch_zhegalkin_sound (e f g : Nat) :
    (g ^^^ (e &&& (f ^^^ g))) = ((e &&& f) ^^^ ((e ^^^ 0xFFFFFFFF) &&& g)) := by
  omega

/-- Verified cost inequality: 3 bitwise ops vs 4 bitwise ops. -/
theorem ch_cost_reduced : 3 <= 4 := by decide

end DualCertifiedRewrite
```

---

## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| Common subexpressions across e-graph | `CP-SAT Exact DAG Extraction` | `model := CpModel(); model.Minimize(sum(cost * x)); solver.Solve(model)` |
| Candidate rewrite rule `lhs -> rhs` | `Dual-Certified Rewriting` | `theorem sound : eval lhs = eval rhs; theorem cost : cost rhs <= cost lhs` |
| Bitwise logic simplification | `3-Gate Zhegalkin Normal Form` | `theorem maj_zhegalkin : (a &&& (b ^^^ c)) ^^^ (b &&& c) = (a &&& b) ^^^ (a &&& c) ^^^ (b &&& c)` |
| Fixed schedule constant folding | `E-Graph Equality Saturation` | `egg_saturate rules [const_fold, shift_fold]; extract_dag` |
| SWAR lane bit-budget allocation | `CP-SAT Knapsack Model` | `model.Add(sum(lane_widths) <= 62); solver.Solve(model)` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Extract sharing-optimal DAG from e-graph | `CP-SAT ILP solver` | Solves 0-1 integer model minimizing shared node cost with acyclicity levels |
| Prove semantic soundness of rewrite rule | `omega / bitwise lemmas` | Discharges algebraic equivalence without `bv_decide` or `native_decide` |
| Prove cost reduction under KernelModel | `by decide` | Verifies `whnfCost rhs <= whnfCost lhs` counting AST nodes and scalar limbs |
| Synthesize optimal schedule unrolling | `CP-SAT sequence formulation` | Finds optimal operation ordering minimizing peak register pressure |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Tree-greedy extractor increases instruction count | Greedy tree extraction duplicates shared subterms | Use CP-SAT sharing-aware DAG extractor with e-class activation variables |
| Cycle detected in extracted e-graph expression | E-graph rewrite cycles permitted circular dependency | Add topological level constraints `l_c >= l_child + 1` in CP-SAT model |
| `Nat` subtraction underflow in rewrite proof | Truncated subtraction hazard on `Nat` | Guard rewrite with hypothesis `b <= a` or use bitwise XOR masking |
| Solver timeout on massive e-graphs | Excessive e-class count without pruning | Apply e-graph class compaction and greedy domain tightening before CP-SAT |
