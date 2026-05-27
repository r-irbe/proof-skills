From the repo root, reset to a clean build state with `lake clean` (or delete `.lake/build` if needed).
If dependencies are not already prepared, run `lake exe cache get` to fetch prebuilt Mathlib artifacts.
Then build exactly one module by its Lean name, for example: `lake build Mathlib.Data.Nat.Basic`.
Use dotted module names, not file paths, so `Mathlib/Data/Nat/Basic.lean` becomes `Mathlib.Data.Nat.Basic`.
The compiled output will be placed under `.lake/build/lib/Mathlib/...`, and Lake will also build any required dependencies automatically.
To verify a specific source file maps correctly, strip `.lean` and replace `/` with `.` before passing it to `lake build`.
