# `proof-skills` Taxonomy -- 4-Layer Progressive Disclosure, 38 Core Lean Skills & 6-Prover Concordance

Classification of all **38 active Lean 4 skills** (`+ 7` opt-in `pack-applied-strategy` skills), **5 Role-Actor Containers** (`agents/*.md`), **24 Soul Overlays** (`agents/souls/*.md`), **4-Layer Reference Hierarchy** (`references/{cards,handbooks,protocols,dialects}/`), **v3 Partitioned Templates** (`templates/{core,workflow,packs}/`), and **20 Cross-ITP Concordance Mechanisms (`CONC-01..20`)**.

---

## 1. Progressive Disclosure & Five-Tier Functional Stack

1. **L0 (`skills/<slug>/SKILL.md`, `< 3.8 KB`)**: Trigger routing, 4-step workflow, and stop conditions.
2. **L1 (`references/cards/<slug>-tables.md`, `2--6.5 KB`)**: Auto-compiled 3-table fast lookup cards (`templates`, `phrasebook`, `errors`).
3. **L2 (`references/handbooks/<slug>-handbook.md`, `5--60 KB`)**: Deep domain handbooks, derivations, and consolidated annexes.
4. **L3 (`vendor/itp-ontology/handbook-tables.v1.json` + `lean-lsp` MCP)**: Sub-5ms machine-queryable index (`390` compiled rows).

---

## 2. Core & Multi-Prover Kernel Skills (`16` Skills)

| Skill | Role Container | Profile | Primary Function |
| :--- | :--- | :--- | :--- |
| [`lean-gateway`](skills/lean-gateway/SKILL.md) | Specifier / Prover | `core` | Top-level dispatch router & cross-skill integration protocol. |
| [`lean-specification`](skills/lean-specification/SKILL.md) | Specifier | `core` | Three-part theorem specification & abstract `Prop` interface design. |
| [`lean-blueprint`](skills/lean-blueprint/SKILL.md) | Specifier | `core` | `@[blueprint]` scaffolding, formalization breakdowns, censuses & DAG visualizers. |
| [`counterexample-first-proving`](skills/counterexample-first-proving/SKILL.md) | Prover / Specifier | `core` | Plausible property testing & Galois-pruned boundary falsification. |
| [`lean-proof`](skills/lean-proof/SKILL.md) | Prover | `core` | Interactive tactic synthesis via `lean_goal` & Layer-1 lookup cards. |
| [`lean-proof-repair`](skills/lean-proof-repair/SKILL.md) | Prover | `core` | Proof repair across Lean toolchain and Mathlib bumps. |
| [`lean-core-only`](skills/lean-core-only/SKILL.md) | Prover | `core` | Stdlib/Core-only proving without Mathlib (`omega`, `grind`, `sair_decide`). |
| [`lean-sair-kernel-optimization`](skills/lean-sair-kernel-optimization/SKILL.md) | Prover | `core` | SAIR kernel WHNF, `@[csimp]` twins, ZDDs, and SWAR word packing (`SAIR-LAW-01..25B`). |
| [`lean-setup`](skills/lean-setup/SKILL.md) | Prover | `core` | Toolchain pins, `elan`, and singleton `lean-serve-broker` setup. |
| [`lean-build`](skills/lean-build/SKILL.md) | Prover | `core` | Lake builds and `.olean` cache hygiene. |
| [`lean-mwe`](skills/lean-mwe/SKILL.md) | Prover | `core` | Minimal Working Examples and `#guard_msgs` reproducers. |
| [`lean-bisect`](skills/lean-bisect/SKILL.md) | Prover | `core` | Toolchain and commit bisection for regressions. |
| [`itp-cross-porting`](skills/itp-cross-porting/SKILL.md) | Prover | `multi-prover` | Cross-ITP router across 6 prover families (`CONC-01..20`). |
| [`rocq-proof-adapter`](skills/rocq-proof-adapter/SKILL.md) | Prover | `multi-prover` | Coq / Rocq / SSReflect / MathComp -> Lean 4 adapter. |
| [`isabelle-isar-adapter`](skills/isabelle-isar-adapter/SKILL.md) | Prover | `multi-prover` | Isabelle/HOL / Isar / `locale` -> Lean 4 adapter. |
| [`hol-metamath-adapter`](skills/hol-metamath-adapter/SKILL.md) | Prover | `multi-prover` | HOL Light & Metamath (`set.mm`) -> Lean 4 adapter. |

---

## 3. Unified Mathematical & AI Formalization Skills (`9` Skills)

- **Mathematics (`6`)**: [`lean-math-foundations`](skills/lean-math-foundations/SKILL.md), [`lean-math-discrete`](skills/lean-math-discrete/SKILL.md) *(includes bigraphs & competition math)*, [`lean-math-stochastic`](skills/lean-math-stochastic/SKILL.md) *(includes ergodic & time series)*, [`lean-math-dynamical`](skills/lean-math-dynamical/SKILL.md) *(includes continuous & discrete convergence)*, [`lean-math-optimization`](skills/lean-math-optimization/SKILL.md), [`lean-math-analysis`](skills/lean-math-analysis/SKILL.md) *(includes IVT & contraction catalogs)*.
- **AI, Knowledge & Security (`3`)**: [`lean-ai-formalization`](skills/lean-ai-formalization/SKILL.md) *(includes nested learning)*, [`lean-knowledge-formalization`](skills/lean-knowledge-formalization/SKILL.md) *(includes causal DAGs, counterfactuals, and applied/deontic reasoning)*, [`lean-security-formalization`](skills/lean-security-formalization/SKILL.md).

---

## 4. Governance, Audit, Refactoring & Synthesis Skills (`13` Skills)

- [`lean-verification-gate`](skills/lean-verification-gate/SKILL.md), [`lean-proof-review`](skills/lean-proof-review/SKILL.md), [`lean-tautology-triage`](skills/lean-tautology-triage/SKILL.md), [`lean-corpus-audit`](skills/lean-corpus-audit/SKILL.md), [`lean-review-council`](skills/lean-review-council/SKILL.md), [`lean-proof-refactor`](skills/lean-proof-refactor/SKILL.md), [`lean-pedagogical-exposition`](skills/lean-pedagogical-exposition/SKILL.md), [`lean-doc-sync`](skills/lean-doc-sync/SKILL.md), [`lean-research`](skills/lean-research/SKILL.md), [`research-council`](skills/research-council/SKILL.md), [`lean-retro-methodology`](skills/lean-retro-methodology/SKILL.md), [`lean-dependency-management`](skills/lean-dependency-management/SKILL.md), [`lean-upstream-pr`](skills/lean-upstream-pr/SKILL.md).
