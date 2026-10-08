# Template_FormalizationBreakdown.md -- Master Formalization Breakdown Plan

> **Status:** Production template for large Lean 4 formalization deconstructions.
> Modeled on the FLT 28-wave (`PLAN-FLT-INVESTIGATION-AND-LEARNINGS`) and
> Navier-Stokes & Euler 8-wave (`PLAN-NSE-INVESTIGATION-AND-LEARNINGS`) architectures.

---

## 1. When to Use

- Initiating a multi-wave investigation and architectural deconstruction of a large Lean 4 formalization (100 to 60,000+ modules).
- Creating an authoritative master plan with static census metrics, DAG topology, landmark matrices, and multi-wave action items.

---

## 2. Template Structure

````markdown
---
id: PLAN-<FORMALIZATION>-INVESTIGATION-AND-LEARNINGS
title: "<Formalization Title> Lean 4 Formalization: Architecture, Dual-Kernel Verification, Proof Route, Definitions Census, and Agentic Synthesis Learnings"
layer: 6
status: active
maturity: seedling
created: YYYY-MM-DD
sources:
  - "<path/to/formalization/lakefile.toml>"
  - "<path/to/formalization/README.md>"
indexed-by:
  - MOC-root-investigator
  - the project's Lean MOC index
related:
  - PLAN-FLT-INVESTIGATION-AND-LEARNINGS
  - PLAN-NSE-INVESTIGATION-AND-LEARNINGS
---

# <Formalization Title> in Lean 4: Deep Investigation and Learnings Plan

<!-- plan-lint:measured YYYY-MM-DD -->

> **Operator Directive (YYYY-MM-DD):** "<Original user request or directive>"
>
> *(Target path resolved per AOR-2: `<path/to/formalization>`,
> formalization repository containing <N> Lean 4 modules on Lean <version> / Mathlib <version>)*

---

## 1. Problem Statement and Scope

<Comprehensive summary of the mathematical result formalized in the target codebase,
its foundational significance, and the historical/formal proof context.>

Our automated static census (`scripts/lean/formalization_breakdown.py`) establishes the exact scope:
- **Total compiled Lean modules**: <N> files.
- **Total lines of code**: <total_lines> lines (<code_lines> code, <comment_lines> comment, <blank_lines> blank).
- **Total proved declarations**: <theorems> theorems, <lemmas> lemmas.
- **Total formal definitions**: <defs> defs, <structures> structures, <classes> classes.
- **Custom axioms**: <axioms> custom axioms. Checked against foundational axioms (`propext`, `Quot.sound`, `Classical.choice`).
- **Proof completeness**: <sorries> sorry occurrences in implementation modules.

---

## 2. Cluster Inventory and Census Metrics

| Cluster | Path | Files | Total Lines | Code Lines | Thms / Lemmas | Definitions | Structures | Sorries |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `<Cluster1>` | `<path1>` | ... | ... | ... | ... | ... | ... | 0 |
| `<Cluster2>` | `<path2>` | ... | ... | ... | ... | ... | ... | 0 |
| **Total** | Repository Root | ... | ... | ... | ... | ... | ... | 0 |

### Dependency Graph Topology

- **Internal Modules (Nodes)**: <N>.
- **Strict Directed Acyclic Graph (DAG)**: Verified (0 dependency cycles).
- **Longest Dependency Chain Depth**: <depth> layers.

---

## 3. Landmark Theorems and Critical Path

| Landmark ID | Lean Module Path | Formal Declaration | Mathematical Meaning | Topological Depth |
| :--- | :--- | :--- | :--- | :--- |
| **LM-001** | `<path/to/module.lean>` | `<Namespace.theorem_name>` | <Informal math statement> | <depth> |
| **LM-002** | `<path/to/module.lean>` | `<Namespace.theorem_name>` | <Informal math statement> | <depth> |

---

## 4. Multi-Wave Research and Synthesis Roadmap

| Wave | Lanes | Focus Area | Deliverables | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Wave 1** | Lanes 1-4 | Macro Census & DAG Topology | Static census, DAG depth, cluster matrix | COMPLETED |
| **Wave 2** | Lanes 5-8 | Verification & Axiom Audit | Dual-kernel check, zero sorry audit | COMPLETED |
| **Wave 3** | Lanes 9-12| Mathematical Engine (Stage 1)| Coordinate geometry & deformation | PLANNED |
| **Wave 4** | Lanes 13-16| Mathematical Engine (Stage 2)| Scaling, concentration & asymptotics | PLANNED |
| **Wave 5** | Lanes 17-20| Mathematical Engine (Stage 3)| BKM reduction / contradiction | PLANNED |
| **Wave 6** | Lanes 21-24| Substrate Transfer to Packages| Downstream module formalization | PLANNED |
| **Wave 7** | Lanes 25-28| AST Linter Rules & Templates | Static guards and proof templates | PLANNED |
| **Wave 8** | Lanes 29-32| Verification Gate & Closeout | Contract tests, CI ladder, zettels | PLANNED |

---

## 5. Downstream Substrate Mapping Matrix

| Substrate ID | Source Declaration | Target Package | Target Lean Module | Mathematical Concept |
| :--- | :--- | :--- | :--- | :--- |
| `SUB-01` | `<Source.decl>` | `<PackageName>` | `<Target/Module.lean>` | <Concept> |
| `SUB-02` | `<Source.decl>` | `<PackageName>` | `<Target/Module.lean>` | <Concept> |

---

## 6. Action Items Registry

| Action ID | Workstream | Target Deliverable | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **ACT-001** | Tooling | `scripts/census.py` | Automated static census | **COMPLETED** |
| **ACT-002** | Master Plan| `docs/.../plan.md` | Investigation master plan | **COMPLETED** |

---

## 7. Compliance and Verification Sign-Off

- **INV-001 Conformance**: Strictly 7-bit ASCII throughout document.
- **INV-014 Conformance**: All cited repository paths physically exist in the worktree.
- **Tufte and AGENTS.md Voice Invariant**: Restrained, objective authorial voice.
````
