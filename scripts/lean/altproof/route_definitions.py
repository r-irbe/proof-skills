"""Route definitions for the alt-proof route table (design note 5b/10).

The single source of truth: gen_route_table.py generates
route-table.json from THIS module; hand-edited JSON is a defect by
construction. Each route records the campaign phase that realized
it (provenance per the pi-lens fork's rule-catalog discipline).
"""

ROUTES = [
    # --- extraction family (16 golden fixtures) ---
    {
        "id": "extract-shared-block",
        "family": "extraction",
        "match": "a >=3-line proof block reused verbatim or modulo renaming",
        "rewrite": "name the block as a lemma; call it at each site",
        "cost_hint": "high-yield: counts once, serves N sites",
        "provenance": "long-proof campaign fixtures 1-15, 17 (36 shared lemmas)",
    },
    {
        "id": "extract-mathlib-absent",
        "family": "extraction",
        "match": "a generic block with no Mathlib equivalent (verified absent before naming)",
        "rewrite": "name it in the owning module; flag as an upstreaming candidate",
        "cost_hint": "highest yield: reusable beyond the corpus",
        "provenance": "fixtures 10-11 (cesaro_tendsto_of_geometric_bound -> PR #44591; sum_mul_le_sum_mul_sum)",
    },
    {
        "id": "extract-horizon-package",
        "family": "extraction",
        "match": "three or more inline steps serving one standing theorem family",
        "rewrite": "package the steps as a named lemma trio in the theorem's module",
        "cost_hint": "high-yield: the Doeblin package pattern",
        "provenance": "fixture 12 (doeblin_card_mul_le_one, realStep_iterate_mul, stationary_ge_of_doeblin)",
    },
    {
        "id": "extract-cauchy-toolkit",
        "family": "extraction",
        "match": "a Cauchy/convergence argument assembled from pointwise and sum-level lemmas",
        "rewrite": "extract the four standard sub-steps as reusable convergence lemmas",
        "cost_hint": "high-yield: the GAP-7 pattern (154 -> ~40)",
        "provenance": "fixture 17 (iterate_sum_cauchy, pointwise_cauchy_of_sum_cauchy, sum_dist_tendsto_of_pointwise, step_fixedpoint_of_sum_dist_tendsto)",
    },
    # --- reflection family (1 golden fixture) ---
    {
        "id": "uniform-simp-collapse",
        "family": "reflection",
        "match": "branched case analysis where one uniform simp set closes every branch",
        "rewrite": "replace the branches with one uniform simp call (the boolean-reflection pattern)",
        "cost_hint": "high-yield: 76 lines/6 branches -> cleared (fixture 16)",
        "provenance": "fixture 16 (gate_row_diff_bound)",
    },
    # --- redirect family (no fixture yet; JAR16 generalization) ---
    {
        "id": "redirect-by-contradiction",
        "family": "redirect",
        "match": "by_contra-heavy proofs with a constructible direct witness",
        "rewrite": "restate as a direct construction (the JAR 2016 redirect class)",
        "cost_hint": "reserved: no corpus fixture yet - the tool's first hit becomes it",
        "provenance": "JAR16 redirect procedure; ballot B3",
    },
    # --- algorithmic substitution family (SAIR calibration cases S1, S1b, S6) ---
    {
        "id": "algorithm-class-substitution",
        "family": "algorithm-class-substitution",
        "match": "exponential or unhoisted recursion with an equivalent closed-form or DP reduction",
        "rewrite": "substitute algorithm class (e.g. in-place DP or structural sieve) and prove equivalence to spec",
        "cost_hint": "highest kernel yield: 20-30x reduction in kernel steps / rfl time",
        "provenance": "SAIR Lean Kernel Challenge lanes (partition in-place DP S1/S1b, primecount sieve S6)",
    },
    # --- kernel-friendly term design family (SAIR calibration case S5 + constructive decidable reduction) ---
    {
        "id": "kernel-friendly-term-design",
        "family": "kernel-friendly-term-design",
        "match": "structural recursion or helper calls with heavy defeq unfolding overhead",
        "rewrite": "refactor to kernel-friendly primitives (structural Nat.rec, unrolled trial division, import-minimal path)",
        "cost_hint": "high kernel yield: reduces defeq heartbeats and avoids WellFounded.fix traps",
        "provenance": "SAIR Lean Kernel Challenge lanes (primecount L1 structural trial division S5)",
    },
    {
        "id": "constructive-decidable-reduction",
        "family": "kernel-friendly-term-design",
        "match": "Classical.choice leakage in first-order Nat/Int/Bool/BitVec theorems caused by split on &&/And or classical by_cases",
        "rewrite": "replace split/by_cases with Bool.and_eq_true, decide_eq_true_eq, omega, or bv_decide to keep axiom closure Classical.choice-free",
        "cost_hint": "high kernel & trust yield: eliminates Classical.choice from decidable first-order theorems",
        "provenance": "lean_rules constructive-gate audit & AltProof bidirectional cross-pollination",
    },
]

