import Lake
open Lake DSL

package «my-project» where
  name := "my-project"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4"
  @ "v4.14.0"

lean_lib «MyProject» where
  roots := #[`MyProject]
