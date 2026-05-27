```lean
import Lean
open Lean Elab Command

/-- error: unknown identifier 'foo' -/
#guard_msgs in
example : Nat := foo
```
Save as `Mwe.lean` and run `lake env lean Mwe.lean`; the `#guard_msgs` command captures the elaborator's "unknown identifier 'foo'" diagnostic and compares it against the docstring, succeeding silently when they match and failing loudly otherwise, giving a minimal reproducible test for the elaborator error.
