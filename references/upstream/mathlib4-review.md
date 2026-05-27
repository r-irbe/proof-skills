# Mathlib PR Review Standards (reference)

> Pure reference. Originally hosted as
> `skills/_overrides/mathlib-review/SKILL.md`; moved here in W4 Wave 1
> (move A2 of `lab/design/07-cluster-workflow.md`) because the content
> is a Mathlib-style checklist with no workflow, triggers, or callers —
> i.e., it never matched the SKILL contract. The slug `mathlib-review`
> survives as a REDIRECT stub for Ctrl-F discoverability per the
> zero-deletions Chesterton protocol. The generic review surface lives
> in [`lean-proof-review`](../../skills/lean-proof-review/SKILL.md);
> Mathlib-specific deltas are below.

## Attributes and API

- New definitions should come with associated lemmas and appropriate
  attributes (`@[simp]`, `@[ext]`, etc.).
- Watch for instance diamonds.
- Prefer bundled morphisms, `FunLike` API for morphism classes,
  `SetLike` API for subobject classes.

## Style points specific to Mathlib

- **Simp squeezing:** terminal `simp` calls should NOT be squeezed
  (replaced with `simp only [...]`) unless there's a measured
  performance problem. Unsqueezed `simp` is more maintainable and
  doesn't break when lemmas are renamed.
- **Normal forms:** prefer `s.Nonempty` over alternatives. Use
  `hne : x ≠ ⊥` in hypotheses (easier to check), `hlt : ⊥ < x` in
  conclusions (more powerful).
- **Transparency:** needing `erw`, or `rfl` after `simp`/`rw`, usually
  means the API is missing lemmas.
- **File size:** consider splitting files that exceed ~1000 lines or
  cover multiple topics.

## Reference guides

The full review guide and style references:

- **Review guide:** <https://leanprover-community.github.io/contribute/pr-review.html>
- **Naming conventions:** <https://leanprover-community.github.io/contribute/naming.html>
- **Code style:** <https://leanprover-community.github.io/contribute/style.html>
- **Documentation style:** <https://leanprover-community.github.io/contribute/doc.html>

## See also

- [`../../skills/lean-proof-review/SKILL.md`](../../skills/lean-proof-review/SKILL.md) — Generic Lean proof review surface
- [`./lean-nightly-infrastructure.md`](./lean-nightly-infrastructure.md) — Nightly testing infrastructure (added in W4 Wave 1 / A4)
- [`./lean-bug-report-pipeline.md`](./lean-bug-report-pipeline.md) — Shared bug-report pipeline
