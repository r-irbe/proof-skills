# Templates (`templates/core/`, `templates/workflow/`, and `templates/packs/`)

Reusable v3 Lean 4 module skeletons, `@[csimp]` Abstraction-Concrete Duality bridges, kernel WHNF patterns, workflow schemas, and opt-in domain packs.

## 1. Partition Layout

| Partition | Path | Count | Scope |
| :--- | :--- | ---: | :--- |
| **Root Standards & Handoff** | [`00-CONVENTIONS.md`](00-CONVENTIONS.md), [`handoff_protocol.json`](handoff_protocol.json) | 2 | v3 cross-template conventions (`INV-001`, `lean-lsp`, `@[csimp]`) & role handoff schema. |
| **Core Lean 4 Templates** | [`core/`](core/) + [`core/examples/`](core/examples/) | 14 + 6 | Canonical module, `@[csimp]` computable twin, kernel WHNF, proof-carrying codegen, tactic, bridge, MWE, bisect, and verification templates + kernel-checked `.lean` exemplars. |
| **Workflow & Governance** | [`workflow/`](workflow/) | 9 | Theorem specs (`Template_Spec`), PRs, Review Council, Blueprints, RETRO logs, Zettelkasten, and Pedagogical Walkthroughs. |
| **Domain Starters Pack** | [`packs/domain-starters/`](packs/domain-starters/) | 22 | Analysis, arithmetic, probability, measure, dynamics, Lyapunov, bigraph, BFT consensus, IFS fractals, info-geometry, and graph starters. |
| **Arithmetic Geometry & FLT Pack** | [`packs/arithmetic-geometry/`](packs/arithmetic-geometry/) | 143 | ModularJacobian, Euler system, Heegner point, Fontaine-Laffaille, Serre weight, Brauer-Nesbitt, and regulator templates. |
| **Fluid PDE Pack** | [`packs/fluid-pde/`](packs/fluid-pde/) | 10 | Vorticity confinement, Gevrey regularity, Reynolds cascade, Piola transform, and continuum flow templates. |

## 2. Core Templates (`templates/core/`)

- [`core/Template_AltProofTactics.md`](core/Template_AltProofTactics.md)
- [`core/Template_Bisect.md`](core/Template_Bisect.md)
- [`core/Template_Bridge.md`](core/Template_Bridge.md)
- [`core/Template_ComputableTwin_Csimp.md`](core/Template_ComputableTwin_Csimp.md)
- [`core/Template_DataModule.md`](core/Template_DataModule.md)
- [`core/Template_FinalCheck.md`](core/Template_FinalCheck.md)
- [`core/Template_KernelWHNF.md`](core/Template_KernelWHNF.md)
- [`core/Template_Lakefile.md`](core/Template_Lakefile.md)
- [`core/Template_MWE.md`](core/Template_MWE.md)
- [`core/Template_ProofCarryingCodegen.md`](core/Template_ProofCarryingCodegen.md)
- [`core/Template_Refactoring.md`](core/Template_Refactoring.md)
- [`core/Template_TacticHelper.md`](core/Template_TacticHelper.md)
- [`core/Template_Theorem.md`](core/Template_Theorem.md)
- [`core/Template_Verification.md`](core/Template_Verification.md)

### Compile-Tested `.lean` Exemplars (`templates/core/examples/`)

- [`core/examples/Template_AltProofTactics.lean`](core/examples/Template_AltProofTactics.lean)
- [`core/examples/Template_ComputableTwin_Csimp.lean`](core/examples/Template_ComputableTwin_Csimp.lean)
- [`core/examples/Template_KernelWHNF.lean`](core/examples/Template_KernelWHNF.lean)
- [`core/examples/Template_ProofCarryingCodegen.lean`](core/examples/Template_ProofCarryingCodegen.lean)
- [`core/examples/Template_KernelDecide.lean`](core/examples/Template_KernelDecide.lean)
- [`core/examples/Template_Theorem_Exemplar.lean`](core/examples/Template_Theorem_Exemplar.lean)

## 3. Workflow Templates (`templates/workflow/`)

- [`workflow/Template_Blueprint.md`](workflow/Template_Blueprint.md)
- [`workflow/Template_Council.md`](workflow/Template_Council.md)
- [`workflow/Template_FormalizationBreakdown.md`](workflow/Template_FormalizationBreakdown.md)
- [`workflow/Template_LeanBlueprintChapter.md`](workflow/Template_LeanBlueprintChapter.md)
- [`workflow/Template_PR.md`](workflow/Template_PR.md)
- [`workflow/Template_PedagogicalProofWalkthrough.md`](workflow/Template_PedagogicalProofWalkthrough.md)
- [`workflow/Template_RetroLog.md`](workflow/Template_RetroLog.md)
- [`workflow/Template_Spec.md`](workflow/Template_Spec.md)
- [`workflow/Template_Zettelkasten.md`](workflow/Template_Zettelkasten.md)
