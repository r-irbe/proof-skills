import Lake

package myproject

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.3.0"

@[default_target]
def myLib : Lake.LeanLib where
  name := "MyProject"
