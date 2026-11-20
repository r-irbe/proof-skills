# Handoff: Continuous Improvement of `AltProof` (`elegance?`, `Closers`) & Scoped `INV-001`

- **Date**: 2026-11-16
- **From**: `downstream-corpus` (`agy-trust2027-7362288c`)
- **Scope**: `packages/altproof/`, `tools/lean-lsp-mcp/`, `scripts/lean/altproof/tree_shake.py`

## 1. Standing Operator Directive: Continuous Tooling Improvement

The operator established a standing cross-workspace requirement:
- **`elegance?`, `bfs_elegance?`, `AltProof.Closers`, and `lean-tree-shake` must be improved continuously on every proving and audit wave.**
- Whenever a domain formalization repeats a tactic pattern or algebraic/analytic bridge 3+ times, extract the general Mathlib-level closer or lemma into `proof-skills/packages/altproof` (with regression pins in `AltProof/Tests.lean` and candidate probes in `elegance?`) rather than leaving project-local copies scattered across corpora.
- Deliver `AltProof` through `proof-skills/packages/altproof` (`require altproof from ".../packages/altproof"`) until an independent Reservoir/GitHub Lean package release is warranted.

## 2. Landed Architecture (`AltProof` v0.6.1 in `downstream-corpus/lean/skills`)

Sync from `<downstream-corpus>/lean/skills/packages/altproof/` and `tools/lean-lsp-mcp/`:

1. **Three-Module Split (`packages/altproof/`)**:
   - `AltProof/Core.lean`: Route table, `GoalFeatures` classifier, `elegance?` / `bfs_elegance?` interactive tactics, `kernel_decide` (primary 3-rung kernel decision closer), and `eval_nat%`.
   - `AltProof/Closers.lean`: Standalone `lean_lib AltProofClosers` containing lightweight Mathlib domain closers with zero `Lean.Elab.Tactic` search-table overhead:
     * Existing macros: `sum_congr_ring`, `finset_nonneg`, `sq_nonneg_ring`, `simplex_row_sum`
     * Newly harvested closers & lemmas (2026-11-16):
       - `sup'_const_mul_of_nonneg` & `sup_norm_scale` (finite `Finset.sup'` scaling & weighted sup-norm contraction)
       - `deriv_quot_ring` (`HasDerivAt` quotient-rule ring closer for replicator/ratio ODEs)
       - `fin_card_filter_Ico` (`Finset.card` interval filter calculator on `Fin M`)
       - `natAbs_le_div_of_cast_abs_le` (`Int.natAbs` floor-bound transfer from real `|·|` inequalities)
       - `zero_sum_vecMul_l1_le_of_entry_floor` (Dobrushin zero-sum vector-matrix $\ell^1$ contraction under uniform column floor $\delta \ge 0$)
   - `AltProof/Tactics.lean`: `alt_proof` combining `Core` + `Closers`, with `elegance?` probing `sup_norm_scale` and `deriv_quot_ring`.
2. **Surface-Syntax-Token Tree-Shaking (`tools/lean-lsp-mcp/src/tree_shake.ts` + `src/autoslim.ts`)**:
   - Prunes uninvoked `syntax` / `macro` / `macro_rules` / `elab` / `register_simp_attr` blocks by surface keyword reachability and inlines local `"type": "path"` Lake dependencies when emitting standalone supplements (`AltProof.Core` and `AltProof.Tactics` drop to 0 lines automatically when `elegance?` is absent from final proof terms).

## 3. Priority Backlog for Next `AltProof` Iteration

1. **`martingale_l2_ae_tendsto` (`AltProof/Closers.lean` or `AltProof/Stochastic.lean`)**:
   - Package the pairwise-orthogonal martingale-difference $L^2 \to L^1 \to$ Doob almost-sure convergence chain (`Summable (fun t => (sigma t) ^ 2)` + a.s. bounded increments -> `Submartingale.exists_ae_tendsto_of_bdd`).
2. **`fin_border_simp` (`AltProof/Closers.lean`)**:
   - Automate `Fin.sum_univ_castSucc` / `Fin.sum_univ_succ` + `ite` splitting on bordered block matrices `Fin (n + 1)` (`Fin.last n` renewal state vs transient sub-block `Fin n`).
3. **Cold-Kernel Replay Scoring in `elegance?`**:
   - Rank candidate tactic closures not only by syntax-line brevity, but also by elaborated `Expr` size / kernel reduction cost.

## 4. Updated `INV-001` Compliance Reminder

`INV-001` uses three-tier scoped Unicode + prompt-injection scanning:
- `ascii` mode: strict 7-bit ASCII ONLY for `package.json`, `package-lock.json`, `lake-manifest.json`, and `**/*.sh`.
- `typographic-free` mode (default for `.lean`, `.md`, `.json`, `.ts`, `.py`): math operators (`∀, ∃, ≤, ≥, →, ∑`), Greek, scripts, and emoji are permitted; curly quotes, en/em-dashes (`–`, `—`), horizontal ellipses (`…`), non-breaking/thin spaces, and all invisible/zero-width/bidi/tag characters are strictly banned.
