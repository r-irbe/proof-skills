# Templates (`templates/` & `templates/packs/`)

Reusable Lean 4 code, specification, governance, and domain formalization templates partitioned into **59 Core & Domain Templates** (`templates/`) and **2 Domain Packs** (`templates/packs/`).

## 1. Partition Layout (`200 = 59 + 131 + 10`)

| Partition | Path | Count | APM Pack Profile | Scope |
| :--- | :--- | ---: | :--- | :--- |
| **Core & Domain Templates** | `templates/` | 59 | `core`, `math`, `ai`, `governance` | Project lakefiles, proof strategy, AltProof tactics, Lyapunov/Markov/PDE/bigraph/causal/deontic/game/ergodic starters, review council JSON/Markdown schemas, and `handoff_protocol.json`. |
| **Arithmetic Geometry & FLT Pack** | `templates/packs/arithmetic-geometry/` | 131 | `pack-arithmetic-geometry` | 111 `Template_ModularJacobian*.md` templates + 20 Euler system, Heegner point, Fontaine-Laffaille, Eichler-Shimura, Mazur control, and Ribet level-lowering templates. |
| **Fluid PDE & Continuum Dynamics Pack** | `templates/packs/fluid-pde/` | 10 | `pack-fluid-pde` | Axisymmetric swirl, bilinear duality, Gevrey regularity, logarithmic gradient, Piola transform, potential lifting, Reynolds cascade, scaling limits, Thom-Mather flows, and vorticity confinement. |

## 2. Core & Domain Templates (`templates/`)

- **Lean 4 Starters (`.lean` & `.md`)**: `Template_Foundation`, `Template_Arithmetic`, `Template_Analysis`, `Template_Algebra`, `Template_Probability`, `Template_Measure`, `Template_Dynamics`, `Template_Lyapunov`, `Template_Cusp`, `Template_GameTheory`, `Template_Ergodic`, `Template_PDE`, `Template_TimeSeries`, `Template_Bigraph`, `Template_Causal`, `Template_Deontic`, `Template_StatMech`, `Template_Graph`, `Template_Safety`, `Template_Security`, `Template_Lakefile`, `Template_ProofStrategy`, `Template_AltProofTactics`, `Template_Verification`, `Template_Performance`.
- **Governance & Handoff Schemas**: `handoff_protocol.json` (v2.0 Role-Actor Container + Soul Overlay + Facet Registry envelope), `Template_CouncilCharter.md`, `Template_QualityGate.md`, `Template_RetroReport.md`, `Template_ZettelNote.md`, `Template_FormalizationBreakdown.md`, `Template_BlueprintTex.md`, `Template_PaperUpdate.md`, `Template_RequirementSpec.md`, `Template_ReviewChecklists.json`.
