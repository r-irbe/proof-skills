import Lake
open Lake DSL

package «myproj» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.20.0"

@[default_target]
lean_lib Myproj
