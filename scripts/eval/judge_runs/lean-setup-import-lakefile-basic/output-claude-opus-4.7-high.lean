import Lake
open Lake DSL

package «myproj» where
  -- add package configuration here

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.11.0"

@[default_target]
lean_lib «MyProj» where
  -- add library configuration here
