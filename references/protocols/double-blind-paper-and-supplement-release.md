# Double-Blind Paper & Shaken Lean 4 Supplement Release Protocol

<!-- Scoped Unicode policy (INV-001; typographic-free by default).
     Status: Authoritative Cross-Cutting Protocol
     Target Skills: lean-doc-sync, lean-verification-gate, lean-proof-review, lean-proof-refactor, lean-dependency-management -->

## 1. Objective & Scope

Publishing a formalized mathematics or computer-science paper alongside an anonymized, standalone Lean 4 supplementary archive fails silently when:
1. Paper prose or Lean identifiers splice, misattribute, or invent mathematical terminology;
2. Theorem statements in `.tex` overclaim or drift from the compiled `.lean` signatures;
3. Proof provenance blurs upstream libraries (`Mathlib`, `Cslib`), adapted classical ports, newly proved classical theorems, and novel domain contributions;
4. Retired misnomers remain as `@[deprecated]` shims polluting `.lean` files; or
5. Tree-shaken supplements retain orphan section husks, dangling docstring cross-references to pruned symbols, unused `lakefile` dependencies, or double-blind leaks.

This protocol defines the deterministic 7-stage pipeline that drives joint paper + supplement audits to `FINDINGS_COUNT: 0`.

---

## 2. Stage 1 -- Three-Tier Proof Provenance Classification

Never claim blanket novelty over classical mathematics, and never under-report genuine formalization or modeling contributions. Every verification section must partition results across three explicit tiers:

| Tier | Category | Attribution & Licensing Requirement |
| :--- | :--- | :--- |
| **Tier 1** | **Upstream Community Foundations** (`Mathlib`, `Cslib`, `Batteries`) | Cite pinned toolchain version and exact package commit SHAs; name the upstream theories used directly. |
| **Tier 2** | **Adapted & Newly Formalized Classical Theory** | Split cleanly into: (a) **Adapted third-party Lean ports** (preserve upstream `Apache-2.0`/`MIT` copyright blocks, `Adapted from` provenance notes, and root `LICENSE` notices); (b) **Partial Mathlib bridges** (state what Mathlib provides vs. what bridge/specialization was proved); and (c) **Original Lean proofs of settled mathematics** (credit the primary mathematical originator while noting the Lean formalization is new). |
| **Tier 3** | **Novel Domain Models, Sharpness Witnesses & Synthesis** | Identify new domain transition/equilibrium bounds, necessity counterexamples, discretization tubes, and end-to-end compositional reflection theorems (`Bool = true <-> Prop`). |

---

## 3. Stage 2 -- Skeptical Primary-Literature Terminology & `.bib` Verification

Before freezing prose or Lean identifiers, audit every eponymous or compound technical term against publisher metadata and primary papers:

1. **Zero Spliced or Promotional Misnomers**:
   - Do not label Aumann partition measurability ($K_i(B) = B$) as `"awareness"` (reserve awareness for Fagin-Halpern, Dekel-Lipman-Rustichini, or Heifetz-Meier-Schipper operators).
   - Do not label Robbins-Monro step-size schedules ($\sum \alpha_t = \infty$, $\sum \alpha_t^2 < \infty$) as `"Polyak step-size"` or `"Polyak-Doob"`.
   - Do not label bounded integer percentage grids $\{0,\dots,100\}^n$ as `"Presburger lattices"` when theorems involve quadratic forms or multiplication.
   - Do not label closed Markov renewal cycle-rate identities ($\pi_k^* r = 1/Z$) as queueing `"Little's law"` ($L = \lambda W$).
   - State exact mathematical inequalities (for example, sub-majority quota $Q_{\mathrm{Droop}} < \lfloor N/2 \rfloor + 1$) rather than political slogans (`"minority protection"`).
2. **Publisher-Verified Bibliography Parity**:
   - Verify volume, issue/number, article number, page range, author spelling, and DOI against primary publisher records (preventing chimera `.bib` entries that splice two papers from the same year or attach an unrelated DOI).
   - Keep any embedded `\begin{filecontents*}{...bib}` block byte-for-byte identical to the standalone `.bib` file, with `0` BibTeX warnings and `100%` of `.bib` entries cited.

---

## 4. Stage 3 -- Bidirectional Paper-vs-Lean Concordance (Combined Option 1 + Option 2)

Maintain a single entry module (`Concordance.lean`) containing `#check` and `#print axioms` anchors for every numbered proposition, theorem, corollary, table row, and numerical walkthrough calculation in the paper:

1. **Combined Option 1 (Strengthen Corpus) + Option 2 (Calibrate Prose)**:
   - When Lean proves a weaker special case than the paper states (for example, uniform action sets instead of heterogeneous `Fin (k i)`, scalar coordinate bounds instead of `Finset.sup'` $\|\cdot\|_\infty$, or taking an equilibrium fixed point as an input hypothesis instead of composing existence + uniqueness), **strengthen the upstream Lean theorem first** so the corpus itself improves.
   - When a full generalization lies outside scope (for example, summable-drift Bellman convergence vs. persistent-variance stochastic approximation, or top-level detour reduction vs. full strong normalization), **calibrate the paper statement and proof sketch to match the exact Lean hypotheses**.
2. **Eliminate Facade Stubs**:
   - Delete arithmetic tautologies masquerading as domain theorems (for example, proving `N = 4 * (N / 4) + 1` under a voting-theory theorem name).
3. **Exact Kernel Axiom Footprints**:
   - Populate axiom tables strictly from `Lean.collectAxioms` / `#print axioms` (`\varnothing`, `\{propext\}`, `\{propext, Quot.sound\}`, `\{propext, Classical.choice, Quot.sound\}`). Never guess `(0 axioms)` on `omega` or `decide` proofs without checking, as both frequently depend on `propext` or `Quot.sound`.

---

## 5. Stage 4 -- Zero `@[deprecated]` Corpus Refactoring & External Rename Ledger

1. **Never Pollute `.lean` Files with `@[deprecated]` Shims**:
   - Leaving `@[deprecated]` aliases in `.lean` modules preserves mathematical misnomers in `.olean` constants, autocomplete, and shaken supplements.
   - Delete retired identifiers and misnamed modules cleanly across the corpus and all downstream package mirrors.
2. **External Markdown Rename Ledger**:
   - Record all `Module | Retired Identifier | Canonical Replacement | Mathematical Rationale` rows in a standalone tracking document (`docs/tracking/terminology-rename-ledger.md`).
3. **Regenerate Probe Manifests (`GT-21`)**:
   - Immediately regenerate `#print axioms` check scripts (`python3 scripts/lean/axiom_audit.py --generate-script`) after any module or declaration rename so gates never scan stale manifests.

---

## 6. Stage 5 -- Declaration-Level Tree-Shaking & Scar-Free Anonymization

Generate the standalone double-blind supplement from `Concordance.lean` via `altproof tree-shake` (`lean_tree_shake`):

```bash
lake build MyProject.Synthesis.Concordance
python3 scripts/lean/altproof/tree_shake.py MyProject.Synthesis.Concordance \
  --project-root . \
  --output-dir /tmp/lean4-supplement \
  --archive /tmp/anonymous_lean4_supplement.tar.gz \
  --package-name SupplementSlice \
  --anonymize \
  --forbid "authorname,internal-repo,private-monograph" \
  --verify-build \
  --markdown
```

Required post-conditions enforced by `tree_shake` + `paper_supplement_audit.py`:
- **Fail-Closed `.ilean` Check**: Aborts if any imported module lacks a fresh `.ilean` from `lake build` (preventing mid-build concurrent-writer races).
- **Dead-Code & Dependency Pruning**: Strips unreachable declarations, `@[deprecated]` shims, unreferenced `@[simp]`/instances on pruned local types, unused surface-syntax macros, secondary `/-! ... -/` section husks, dangling `(; see \`PrunedDecl\`)` docstring clauses, and unused git `require` entries in `lakefile.lean` / `lake-manifest.json`.
- **Import & License Hygiene**: Rewrites deprecated imports (`Mathlib.Data.Real.Basic` -> `Mathlib.Basic.Real.Basic`), suppresses bare `import Mathlib`, emits a root `LICENSE` file, prepends neutral Apache-2.0 headers where absent, and preserves third-party `MIT`/`Apache-2.0` copyright notices.
- **Deterministic Metadata-Scrubbed Archive**: Emits tarballs with `--mtime='UTC 2026-01-01' --owner=0 --group=0 --numeric-owner` and zero `.git/` or `.lake/` entries.

---

## 7. Stage 6 -- Clean-Room Cold `Lean.Kernel.Environment.replay` & Executed-Tool Honesty

1. Unpack the `.tar.gz` archive into a clean directory, run `lake build` verifying **`0` compiler warnings and `0` errors**, and execute cold in-process kernel replay across 100% of compiled slice constants:
   ```bash
   COLD_REPLAY_LIB_DIR=.lake/build/lib/lean lake env lean scripts/lean/cold_kernel_replay.lean
   ```
2. **Executed-Scanner Honesty**: Cite only verification tools actually executed on the final artifact in the current environment (`Lean.Kernel.Environment.replay`, `Lean.collectAxioms`, `lake build`). Never cite external checkers (`nanoda_lib`, `lean4checker`) in paper prose unless they were physically run on the final slice.

---

## 8. Stage 7 -- Automated Gate + Independent Multi-Round Convergence (`FINDINGS_COUNT: 0`)

1. Run the deterministic joint audit gate:
   ```bash
   python3 scripts/lean/paper_supplement_audit.py \
     --tex path/to/paper.tex \
     --bib path/to/paper.bib \
     --lean-dir /tmp/lean4-supplement \
     --supplement-mode \
     --max-content-pages 9 \
     --forbid-first-person \
     --strict
   ```
2. Dispatch an independent read-only `auditor` verification pass jointly over the compiled `.tex`/`.pdf`/`.log`/`.blg` and the unpacked `lean4-supplement/` across all 6 dimensions (semantic alignment, skeptical terminology, Lean code quality, double-blind anonymity, LaTeX/BibTeX integrity, and scoped `INV-001` Unicode) and iterate until the auditor reports **`FINDINGS_COUNT: 0`**.
