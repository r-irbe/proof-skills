lean-toolchain:
leanprover/lean4:v4.30.0-rc2

Reason (one line): Mathlib is pinned to (and built against) a specific Lean version, and mismatching the toolchain typically breaks compilation and/or Lake caches.
