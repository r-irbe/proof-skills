```lean
import Lake
open Lake DSL

package «my_project» where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.21.0"

@[default_target]
lean_lib «MyProject» where
```
