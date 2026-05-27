The "unknown identifier 'foo'" error means Lean can't resolve `foo` in the current scope. Common causes and fixes:

1. Missing import: if `foo` is defined in another module, add `import Path.To.Module` at the top of the file.
2. Missing `open`: the identifier may live in a namespace. Either use the fully qualified name (`Namespace.foo`) or add `open Namespace`.
3. Typo or wrong case: Lean is case-sensitive; check the exact spelling against the definition.
4. Out-of-scope local: if `foo` was a `let`/`have`/binder, ensure you're using it inside the block where it's bound.
5. Defined after use: in the same file, `foo` must be declared before it's referenced (or use mutual blocks).
6. Wrong Lean version / library: if `foo` comes from Mathlib or std, confirm the dependency is in your `lakefile.lean` and run `lake update` / `lake build`.

To diagnose, share the surrounding code and where `foo` is supposed to be defined, and I can pinpoint the fix.
