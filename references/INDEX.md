# Reference Index -- 4-Layer Progressive Disclosure Architecture

Authoritative catalog of the `proof-skills` reference hierarchy.
Scoped Unicode policy (`INV-001`; UTF-8 mathematical symbols valid in Lean 4, typographic punctuation banned).

---

## 1. Progressive Disclosure Layers

| Layer | Path | Typical Size | When Agents Read It |
| :--- | :--- | :--- | :--- |
| **L0: Dispatch Contract** | `../skills/<slug>/SKILL.md` | `2.5--3.8 KB` | Trigger routing, 4-step workflow, and stop conditions. |
| **L1: Fast Lookup Card** | `cards/<slug>-tables.md` (`43` cards) | `2.0--6.5 KB` | **Default first read** during proving: Goal-Shape, Intent Phrasebook, and Error->Fix tables. |
| **L2: Deep Handbook** | `handbooks/<slug>-handbook.md` (`43` manuals) | `5--60 KB` | Deep derivations, multi-step patterns, case studies, and domain annexes. |
| **L3: Machine Index** | `../vendor/itp-ontology/handbook-tables.v1.json` + `dialects/*.json` | `490` compiled rows | Sub-5ms offline queries via `lean-lsp` MCP (`lean_search`, `lean_goal(target: "altproof")`). |

---

## 2. Layer-1 Fast Lookup Cards & Layer-2 Domain Handbooks (`43` Canonical Pairs)

| Skill (`@slug`) | Layer-1 Fast Card (`cards/`) | Layer-2 Deep Handbook (`handbooks/`) |
| :--- | :--- | :--- |
| [`counterexample-first-proving`](../skills/counterexample-first-proving/SKILL.md) | [`cards/counterexample-first-proving-tables.md`](cards/counterexample-first-proving-tables.md) | [`handbooks/counterexample-first-proving-handbook.md`](handbooks/counterexample-first-proving-handbook.md) |
| [`hol-metamath-adapter`](../skills/hol-metamath-adapter/SKILL.md) | [`cards/hol-metamath-adapter-tables.md`](cards/hol-metamath-adapter-tables.md) | [`handbooks/hol-metamath-adapter-handbook.md`](handbooks/hol-metamath-adapter-handbook.md) |
| [`isabelle-isar-adapter`](../skills/isabelle-isar-adapter/SKILL.md) | [`cards/isabelle-isar-adapter-tables.md`](cards/isabelle-isar-adapter-tables.md) | [`handbooks/isabelle-isar-adapter-handbook.md`](handbooks/isabelle-isar-adapter-handbook.md) |
| [`itp-cross-porting`](../skills/itp-cross-porting/SKILL.md) | [`cards/itp-cross-porting-tables.md`](cards/itp-cross-porting-tables.md) | [`handbooks/itp-cross-porting-handbook.md`](handbooks/itp-cross-porting-handbook.md) |
| [`lean-ai-formalization`](../skills/lean-ai-formalization/SKILL.md) | [`cards/lean-ai-formalization-tables.md`](cards/lean-ai-formalization-tables.md) | [`handbooks/lean-ai-formalization-handbook.md`](handbooks/lean-ai-formalization-handbook.md) |
| [`lean-asymptotic-algorithms`](../skills/lean-asymptotic-algorithms/SKILL.md) | [`cards/lean-asymptotic-algorithms-tables.md`](cards/lean-asymptotic-algorithms-tables.md) | [`handbooks/lean-asymptotic-algorithms-handbook.md`](handbooks/lean-asymptotic-algorithms-handbook.md) |
| [`lean-bisect`](../skills/lean-bisect/SKILL.md) | [`cards/lean-bisect-tables.md`](cards/lean-bisect-tables.md) | [`handbooks/lean-bisect-handbook.md`](handbooks/lean-bisect-handbook.md) |
| [`lean-blueprint`](../skills/lean-blueprint/SKILL.md) | [`cards/lean-blueprint-tables.md`](cards/lean-blueprint-tables.md) | [`handbooks/lean-blueprint-handbook.md`](handbooks/lean-blueprint-handbook.md) |
| [`lean-build`](../skills/lean-build/SKILL.md) | [`cards/lean-build-tables.md`](cards/lean-build-tables.md) | [`handbooks/lean-build-handbook.md`](handbooks/lean-build-handbook.md) |
| [`lean-computational-reflection`](../skills/lean-computational-reflection/SKILL.md) | [`cards/lean-computational-reflection-tables.md`](cards/lean-computational-reflection-tables.md) | [`handbooks/lean-computational-reflection-handbook.md`](handbooks/lean-computational-reflection-handbook.md) |
| [`lean-core-only`](../skills/lean-core-only/SKILL.md) | [`cards/lean-core-only-tables.md`](cards/lean-core-only-tables.md) | [`handbooks/lean-core-only-handbook.md`](handbooks/lean-core-only-handbook.md) |
| [`lean-corpus-audit`](../skills/lean-corpus-audit/SKILL.md) | [`cards/lean-corpus-audit-tables.md`](cards/lean-corpus-audit-tables.md) | [`handbooks/lean-corpus-audit-handbook.md`](handbooks/lean-corpus-audit-handbook.md) |
| [`lean-dependency-management`](../skills/lean-dependency-management/SKILL.md) | [`cards/lean-dependency-management-tables.md`](cards/lean-dependency-management-tables.md) | [`handbooks/lean-dependency-management-handbook.md`](handbooks/lean-dependency-management-handbook.md) |
| [`lean-doc-sync`](../skills/lean-doc-sync/SKILL.md) | [`cards/lean-doc-sync-tables.md`](cards/lean-doc-sync-tables.md) | [`handbooks/lean-doc-sync-handbook.md`](handbooks/lean-doc-sync-handbook.md) |
| [`lean-egraph-cpsat-superopt`](../skills/lean-egraph-cpsat-superopt/SKILL.md) | [`cards/lean-egraph-cpsat-superopt-tables.md`](cards/lean-egraph-cpsat-superopt-tables.md) | [`handbooks/lean-egraph-cpsat-superopt-handbook.md`](handbooks/lean-egraph-cpsat-superopt-handbook.md) |
| [`lean-gateway`](../skills/lean-gateway/SKILL.md) | [`cards/lean-gateway-tables.md`](cards/lean-gateway-tables.md) | [`handbooks/lean-gateway-handbook.md`](handbooks/lean-gateway-handbook.md) |
| [`lean-kernel-optimization`](../skills/lean-kernel-optimization/SKILL.md) | [`cards/lean-kernel-optimization-tables.md`](cards/lean-kernel-optimization-tables.md) | [`handbooks/lean-kernel-optimization-handbook.md`](handbooks/lean-kernel-optimization-handbook.md) |
| [`lean-knowledge-formalization`](../skills/lean-knowledge-formalization/SKILL.md) | [`cards/lean-knowledge-formalization-tables.md`](cards/lean-knowledge-formalization-tables.md) | [`handbooks/lean-knowledge-formalization-handbook.md`](handbooks/lean-knowledge-formalization-handbook.md) |
| [`lean-math-analysis`](../skills/lean-math-analysis/SKILL.md) | [`cards/lean-math-analysis-tables.md`](cards/lean-math-analysis-tables.md) | [`handbooks/lean-math-analysis-handbook.md`](handbooks/lean-math-analysis-handbook.md) |
| [`lean-math-discrete`](../skills/lean-math-discrete/SKILL.md) | [`cards/lean-math-discrete-tables.md`](cards/lean-math-discrete-tables.md) | [`handbooks/lean-math-discrete-handbook.md`](handbooks/lean-math-discrete-handbook.md) |
| [`lean-math-dynamical`](../skills/lean-math-dynamical/SKILL.md) | [`cards/lean-math-dynamical-tables.md`](cards/lean-math-dynamical-tables.md) | [`handbooks/lean-math-dynamical-handbook.md`](handbooks/lean-math-dynamical-handbook.md) |
| [`lean-math-foundations`](../skills/lean-math-foundations/SKILL.md) | [`cards/lean-math-foundations-tables.md`](cards/lean-math-foundations-tables.md) | [`handbooks/lean-math-foundations-handbook.md`](handbooks/lean-math-foundations-handbook.md) |
| [`lean-math-optimization`](../skills/lean-math-optimization/SKILL.md) | [`cards/lean-math-optimization-tables.md`](cards/lean-math-optimization-tables.md) | [`handbooks/lean-math-optimization-handbook.md`](handbooks/lean-math-optimization-handbook.md) |
| [`lean-math-stochastic`](../skills/lean-math-stochastic/SKILL.md) | [`cards/lean-math-stochastic-tables.md`](cards/lean-math-stochastic-tables.md) | [`handbooks/lean-math-stochastic-handbook.md`](handbooks/lean-math-stochastic-handbook.md) |
| [`lean-mwe`](../skills/lean-mwe/SKILL.md) | [`cards/lean-mwe-tables.md`](cards/lean-mwe-tables.md) | [`handbooks/lean-mwe-handbook.md`](handbooks/lean-mwe-handbook.md) |
| [`lean-pedagogical-exposition`](../skills/lean-pedagogical-exposition/SKILL.md) | [`cards/lean-pedagogical-exposition-tables.md`](cards/lean-pedagogical-exposition-tables.md) | [`handbooks/lean-pedagogical-exposition-handbook.md`](handbooks/lean-pedagogical-exposition-handbook.md) |
| [`lean-proof`](../skills/lean-proof/SKILL.md) | [`cards/lean-proof-tables.md`](cards/lean-proof-tables.md) | [`handbooks/lean-proof-handbook.md`](handbooks/lean-proof-handbook.md) |
| [`lean-proof-refactor`](../skills/lean-proof-refactor/SKILL.md) | [`cards/lean-proof-refactor-tables.md`](cards/lean-proof-refactor-tables.md) | [`handbooks/lean-proof-refactor-handbook.md`](handbooks/lean-proof-refactor-handbook.md) |
| [`lean-proof-repair`](../skills/lean-proof-repair/SKILL.md) | [`cards/lean-proof-repair-tables.md`](cards/lean-proof-repair-tables.md) | [`handbooks/lean-proof-repair-handbook.md`](handbooks/lean-proof-repair-handbook.md) |
| [`lean-proof-review`](../skills/lean-proof-review/SKILL.md) | [`cards/lean-proof-review-tables.md`](cards/lean-proof-review-tables.md) | [`handbooks/lean-proof-review-handbook.md`](handbooks/lean-proof-review-handbook.md) |
| [`lean-research`](../skills/lean-research/SKILL.md) | [`cards/lean-research-tables.md`](cards/lean-research-tables.md) | [`handbooks/lean-research-handbook.md`](handbooks/lean-research-handbook.md) |
| [`lean-retro-methodology`](../skills/lean-retro-methodology/SKILL.md) | [`cards/lean-retro-methodology-tables.md`](cards/lean-retro-methodology-tables.md) | [`handbooks/lean-retro-methodology-handbook.md`](handbooks/lean-retro-methodology-handbook.md) |
| [`lean-review-council`](../skills/lean-review-council/SKILL.md) | [`cards/lean-review-council-tables.md`](cards/lean-review-council-tables.md) | [`handbooks/lean-review-council-handbook.md`](handbooks/lean-review-council-handbook.md) |
| [`lean-kernel-optimization`](../skills/lean-kernel-optimization/SKILL.md) | [`cards/lean-kernel-optimization-tables.md`](cards/lean-kernel-optimization-tables.md) | [`handbooks/lean-kernel-optimization-handbook.md`](handbooks/lean-kernel-optimization-handbook.md) |
| [`lean-security-formalization`](../skills/lean-security-formalization/SKILL.md) | [`cards/lean-security-formalization-tables.md`](cards/lean-security-formalization-tables.md) | [`handbooks/lean-security-formalization-handbook.md`](handbooks/lean-security-formalization-handbook.md) |
| [`lean-setup`](../skills/lean-setup/SKILL.md) | [`cards/lean-setup-tables.md`](cards/lean-setup-tables.md) | [`handbooks/lean-setup-handbook.md`](handbooks/lean-setup-handbook.md) |
| [`lean-specification`](../skills/lean-specification/SKILL.md) | [`cards/lean-specification-tables.md`](cards/lean-specification-tables.md) | [`handbooks/lean-specification-handbook.md`](handbooks/lean-specification-handbook.md) |
| [`lean-tautology-triage`](../skills/lean-tautology-triage/SKILL.md) | [`cards/lean-tautology-triage-tables.md`](cards/lean-tautology-triage-tables.md) | [`handbooks/lean-tautology-triage-handbook.md`](handbooks/lean-tautology-triage-handbook.md) |
| [`lean-unboxed-limbs-swar`](../skills/lean-unboxed-limbs-swar/SKILL.md) | [`cards/lean-unboxed-limbs-swar-tables.md`](cards/lean-unboxed-limbs-swar-tables.md) | [`handbooks/lean-unboxed-limbs-swar-handbook.md`](handbooks/lean-unboxed-limbs-swar-handbook.md) |
| [`lean-upstream-pr`](../skills/lean-upstream-pr/SKILL.md) | [`cards/lean-upstream-pr-tables.md`](cards/lean-upstream-pr-tables.md) | [`handbooks/lean-upstream-pr-handbook.md`](handbooks/lean-upstream-pr-handbook.md) |
| [`lean-verification-gate`](../skills/lean-verification-gate/SKILL.md) | [`cards/lean-verification-gate-tables.md`](cards/lean-verification-gate-tables.md) | [`handbooks/lean-verification-gate-handbook.md`](handbooks/lean-verification-gate-handbook.md) |
| [`lean-worker-wrapper-cps`](../skills/lean-worker-wrapper-cps/SKILL.md) | [`cards/lean-worker-wrapper-cps-tables.md`](cards/lean-worker-wrapper-cps-tables.md) | [`handbooks/lean-worker-wrapper-cps-handbook.md`](handbooks/lean-worker-wrapper-cps-handbook.md) |
| [`research-council`](../skills/research-council/SKILL.md) | [`cards/research-council-tables.md`](cards/research-council-tables.md) | [`handbooks/research-council-handbook.md`](handbooks/research-council-handbook.md) |
| [`rocq-proof-adapter`](../skills/rocq-proof-adapter/SKILL.md) | [`cards/rocq-proof-adapter-tables.md`](cards/rocq-proof-adapter-tables.md) | [`handbooks/rocq-proof-adapter-handbook.md`](handbooks/rocq-proof-adapter-handbook.md) |

---

## 3. Cross-Cutting Engineering Protocols (`protocols/` & `upstream/`)

| Protocol / Guide | Path |
| :--- | :--- |
| `discovery-ladder-evals` | [`protocols/discovery-ladder-evals.md`](protocols/discovery-ladder-evals.md) |
| `discovery-ladder` | [`protocols/discovery-ladder.md`](protocols/discovery-ladder.md) |
| `double-blind-paper-and-supplement-release` | [`protocols/double-blind-paper-and-supplement-release.md`](protocols/double-blind-paper-and-supplement-release.md) |
| `ecosystem-refactor` | [`protocols/ecosystem-refactor.md`](protocols/ecosystem-refactor.md) |
| `formalization_breakdown_guide` | [`protocols/formalization_breakdown_guide.md`](protocols/formalization_breakdown_guide.md) |
| `lean4-core-only-profile` | [`protocols/lean4-core-only-profile.md`](protocols/lean4-core-only-profile.md) |
| `lean4-lsp-guide` | [`protocols/lean4-lsp-guide.md`](protocols/lean4-lsp-guide.md) |
| `lean4-lsp-proof-protocol` | [`protocols/lean4-lsp-proof-protocol.md`](protocols/lean4-lsp-proof-protocol.md) |
| `lean4-module-dependency-guide` | [`protocols/lean4-module-dependency-guide.md`](protocols/lean4-module-dependency-guide.md) |
| `lean4-proof-strategy` | [`protocols/lean4-proof-strategy.md`](protocols/lean4-proof-strategy.md) |
| `lean4-tactic-hierarchy` | [`protocols/lean4-tactic-hierarchy.md`](protocols/lean4-tactic-hierarchy.md) |
| `lean_to_math_exposition_patterns` | [`protocols/lean_to_math_exposition_patterns.md`](protocols/lean_to_math_exposition_patterns.md) |
| `mathlib-module-system-notes` | [`protocols/mathlib-module-system-notes.md`](protocols/mathlib-module-system-notes.md) |
| `mathlib4-conventions` | [`protocols/mathlib4-conventions.md`](protocols/mathlib4-conventions.md) |
| `research-council-skill-map` | [`protocols/research-council-skill-map.md`](protocols/research-council-skill-map.md) |
| `research-output-templates` | [`protocols/research-output-templates.md`](protocols/research-output-templates.md) |
| `research-queue` | [`protocols/research-queue.md`](protocols/research-queue.md) |
| `theorem-search` | [`protocols/theorem-search.md`](protocols/theorem-search.md) |
| `upstream/lean-bug-report-pipeline` | [`upstream/lean-bug-report-pipeline.md`](upstream/lean-bug-report-pipeline.md) |
| `upstream/lean-nightly-infrastructure` | [`upstream/lean-nightly-infrastructure.md`](upstream/lean-nightly-infrastructure.md) |
| `upstream/lean4-pr` | [`upstream/lean4-pr.md`](upstream/lean4-pr.md) |
| `upstream/mathlib4-pr` | [`upstream/mathlib4-pr.md`](upstream/mathlib4-pr.md) |
| `upstream/mathlib4-review` | [`upstream/mathlib4-review.md`](upstream/mathlib4-review.md) |

---

## 4. Cross-ITP Dialect Specifications (`dialects/`)

| Prover Dialect | Specification JSON |
| :--- | :--- |
| `agda` | [`dialects/agda.json`](dialects/agda.json) |
| `hol_light` | [`dialects/hol_light.json`](dialects/hol_light.json) |
| `isabelle` | [`dialects/isabelle.json`](dialects/isabelle.json) |
| `lean4` | [`dialects/lean4.json`](dialects/lean4.json) |
| `metamath` | [`dialects/metamath.json`](dialects/metamath.json) |
| `rocq` | [`dialects/rocq.json`](dialects/rocq.json) |

---

## 5. Repository Architecture & Governance Docs (`references/` Root)

- [`AUTHORING.md`](AUTHORING.md) -- v2/v3 skill & handbook authoring specification
- [`architecture.md`](architecture.md) -- Hybrid Role-Container + Facet architecture
- [`swarm_methodology.md`](swarm_methodology.md) -- 5-Role Container + 24 Soul Overlay swarm protocol
- [`project_structure.md`](project_structure.md) -- Directory layout map
- [`contributing.md`](contributing.md) -- Contribution & confidentiality rules
- [`bibliography.md`](bibliography.md) -- Foundational ITP & verification literature
- [`eval_history.md`](eval_history.md) -- Benchmark & calibration history
