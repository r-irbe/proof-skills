---
name: lean-mwe
description: Create minimal working examples (MWEs) from Lean errors for bug reports. Use when minimizing a Lean error, preserving an exact diagnostic with `#guard_msgs`, isolating a panic with `#guard_panic`, or preparing a Lean 4/Mathlib report. Always validates repros with `lake env lean`.
---

# Minimizing Lean Errors

## Workflow

1. **Set up the guard** (`#guard_msgs` or `#guard_panic`)
2. **Run `lake exe minimize`**
3. **Review and polish** the output

## Repository Setup

For Mathlib-related bugs:
```bash
cd /tmp
git clone https://github.com/kim-em/mathlib-minimizer.git
cd mathlib-minimizer
lake exe cache get
```

For pure Lean 4 bugs:
```bash
cd /tmp
git clone https://github.com/kim-em/lean-minimizer.git
cd lean-minimizer
```

## Step 1: Create the Test File

### For Regular Errors

Use `#guard_msgs` to capture the exact error:

```lean
import Mathlib.SomeModule

/--
error: the exact error message
goes here verbatim
-/
#guard_msgs in
example : ... := by some_tactic
```

### For Panics

```lean
import Mathlib.SomeModule

#guard_msgs in
#guard_panic in
some_command_that_panics
```

## Step 2: Verify the Guard Works

```bash
lake env lean YourFile.lean
```

No output = success (guard passed). Error output = guard failed, and you need to redesign the test case.

Use `lake env lean`, not bare `lean`, so the reproduction uses the same
toolchain and package path as the project that exposed the bug.

## Step 3: Run the Minimizer

```bash
lake exe minimize YourFile.lean
```

Output is written to `YourFile.out.lean`.

### Useful Options

- `--resume`: Continue from the output file if interrupted
- `--quiet`: Suppress progress output
- `--only-delete`: Only run the deletion pass
- `--only-import-inlining`: Only inline imports

**Never use `--no-import-inlining`**. The entire point is to produce a self-contained file.

### For Long-Running Minimizations

Use `--resume` to continue from where you left off:

```bash
# Initial run (Ctrl-C if needed)
lake exe minimize YourFile.lean

# Resume later
lake exe minimize YourFile.lean --resume
```

After manually editing the `.out.lean` file, always use `--resume` to continue from the edited state.

## Step 4: Review the Output

```bash
lake env lean YourFile.out.lean
```

### Checklist Before Filing

- [ ] The `.out.lean` file compiles with the expected error/panic
- [ ] No Mathlib imports remain (ideal) or minimal imports remain
- [ ] The error message in `#guard_msgs` matches exactly
- [ ] project-specific: the project codebase has zero `sorry`; strip any sorry introduced during debugging before filing. Prefer `grind` over `omega`/`linarith` in reproductions when the original proof used `grind`.

---

## See also

- [`../../templates/Template_Foundation.md`](../../templates/Template_Foundation.md) — Template: Minimal foundation module to start from
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) — Workflow: error priority, one-step-at-a-time
