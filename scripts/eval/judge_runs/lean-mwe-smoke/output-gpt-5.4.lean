Use a tiny file that isolates the failing term and asserts the exact diagnostic with `#guard_msgs in`.
```lean
import Lean

#guard_msgs in
example : Nat := by
  fail_if_success exact "x"
```
That reproduces an elaborator type-mismatch error because `"x"` elaborates as `String` while the goal is `Nat`.
If you want to lock the exact message, use:
```lean
/--
error: type mismatch
  "x"
has type
  String
but is expected to have type
  Nat
-/
#guard_msgs in
example : Nat := by
  exact "x"
```
Keep the repro minimal by removing unrelated imports, using `example` instead of theorem names, and choosing the smallest term that still triggers the elaborator failure.
