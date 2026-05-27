# Lean skills ecosystem refactor map

This map records the current consolidation direction for the 62-skill bundle.
It is a planning reference, not a dispatch surface and not a deprecation list.
Do not suppress or avoid a skill because it appears here as a future merge,
split, or extraction candidate. Skills should stay small and operational; large
persona, domain, and template content should move here or to adjacent reference
folders over time.

## Artifact boundaries

| Artifact | Owns | Does not own |
|---|---|---|
| Skill | A reusable workflow and when to use it | Persona monologues, large domain textbooks |
| Agent | Routing, role, and bounded execution responsibility | Reusable domain reference |
| Soul | Voice, review stance, uncertainty behaviour | Commands, validation logic |
| Reference | Background knowledge, examples, matrices, provenance | Triggering or workflow control |
| Script | Deterministic checks and file operations | Judgement or review semantics |
| Tactic/macro | Kernel-checked proof automation | Project management prose |

## Keep as focused skills

| Skill | Reason |
|---|---|
| `lean-proof` | Single-proof implementation workflow |
| `lean-proof-review` | Review workflow and checklist |
| `lean-specification` | Theorem/design specification |
| `lean-research` | Search and research workflow |
| `lean-mwe` | Reproducer minimization workflow |
| `lean-setup` | Lean repository setup workflow |
| `lean-build` | Lake/build validation workflow (formerly `mathlib-build`; renamed in W4 Wave 2 / move A3) |
| `lean-doc-requirements` | Document-to-formal-claim extraction |
| `lean-doc-improvement` | Formal-results-to-document update |
| `lean-blueprint` | Blueprint pipeline orchestration |
| `lean-report` | Blueprint-to-report pipeline |

## Refactor into agents or souls

| Source | Target | Reason |
|---|---|---|
| `lean-review-council` Σ/Φ/Ν/Λ/Ω blocks | `souls/` or `agents/` | Persona and role content overwhelms the skill body |
| `research-council` member descriptions | `souls/` or `agents/` | Long-lived scholarly personas should be reusable |
| `lean-gateway` fan-out/fan-in operators | `agents/lean-orchestrator.agent.md` | Orchestration is role behaviour, not domain reference |
| `lean-integration-protocol` role table | `agents/` | Dispatch ownership belongs with agent definitions |

## Refactor into references

| Source cluster | Reference target | Reason |
|---|---|---|
| `lean-math-*` and `math-*` overlap | `references/math/` | General theory and Lean implementation should be separated |
| `ai-*`, `applied-*` | `references/domain/` | Most content is taxonomic/domain grounding |
| `lean-retro-*` templates | `references/retro/` | Templates are reusable context, not trigger text |
| `lean-blueprint` / `lean-report` templates | `references/documentation/` | Pipeline examples are cold context |
| `epistemic-mapping` quadrants | `references/epistemic/` | Methodology definitions are reference material |

## Merge candidates

| Candidate | Recommendation |
|---|---|
| `lean-doc-feedback` | Merge into `lean-doc-requirements` + `lean-doc-improvement`; keep a reference for the bidirectional loop |
| `lean-research-types` Type T | Fold theorem/API/tactic search into `lean-research` or keep as a thin typed-protocol extension |
| `lean-math-dynamical` + `math-nonlinear-dynamics` | Keep both only if one is strictly Lean/Mathlib implementation and one is conceptual |
| `lean-math-stochastic` + `math-measure-probability` + `math-time-series` | Split by Lean proof workflow vs probability reference vs temporal-method reference |

## First safe migration sequence

1. Add shared references (`theorem-search`, this refactor map).
2. Wire references into core skills without deleting old content.
3. Add offline structural validators.
4. Add tests for modified skills.
5. Extract council personas to `souls/` in a later PR.
6. Trim oversized skill bodies after references and aliases exist.
