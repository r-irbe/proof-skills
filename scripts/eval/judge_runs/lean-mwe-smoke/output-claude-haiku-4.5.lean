This is a TypeScript/Vue project (tacit-mui), not a Lean project. You need a Lean environment to create a `#guard_msgs` minimal repro. Here's a standard example for a Lean elaborator error:

```lean
#guard_msgs in
theorem test : ∀ x : Nat, x = x + 1 := by
  intro x
  rfl
```

This triggers an elaborator error because `rfl` cannot prove `x = x + 1`. The `#guard_msgs` command verifies the expected error message matches. To create a minimal repro in a Lean project, initialize a Lean 4 file with `#guard_msgs in` before the problematic code block, then run `lean` to verify the error message is captured correctly.