The error "unknown identifier 'foo'" in Lean means the name `foo` is not in scope at the point of use. Common causes and fixes:

1. Typo — check spelling and case (Lean is case-sensitive).
2. Not declared yet — `def`, `theorem`, or `let` for `foo` must appear before its use.
3. Wrong namespace — use the fully qualified name, e.g., `MyNamespace.foo`, or add `open MyNamespace` before the usage site.
4. Missing import — if `foo` lives in another file, add `import MyFile` at the top.
5. `foo` is a local variable that has gone out of scope — restructure so it's in scope where needed.
6. In tactic mode, a hypothesis named `foo` must be introduced first (e.g., via `intro foo` or `obtain ⟨foo, _⟩ := ...`).
7. If you defined `foo` inside a `section` or `namespace`, it may not be visible outside without qualification.

Share the surrounding code for a more precise diagnosis.
