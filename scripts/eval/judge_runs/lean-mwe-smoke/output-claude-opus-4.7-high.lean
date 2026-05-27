```lean
import Lean

/--
error: unknown identifier 'foo'
-/
#guard_msgs in
example : Nat := foo
```