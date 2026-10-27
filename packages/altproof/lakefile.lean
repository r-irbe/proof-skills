import Lake
open Lake DSL

package altproof where
  version := v!"0.4.0"
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.34.1"

@[default_target]
lean_lib AltProof where
  srcDir := "."
