# Lean Bug-Report Pipeline (reference)

> Pure reference. Cross-skill pipeline diagram shared between
> [`lean-mwe`](../../skills/_overrides/lean-mwe/SKILL.md) and
> [`lean-bisect`](../../skills/_overrides/lean-bisect/SKILL.md).
> Added in W4 Wave 1 (move E1 of `lab/design/07-cluster-workflow.md`).

## Why this reference exists

`lean-mwe` and `lean-bisect` are deliberately kept as separate skills
(different artifacts — minimised test file vs. commit-range git
operation), but they almost always appear together in real bug-report
work. This reference is the joint story: which skill to reach for
first, when to chain them, and what hand-off they expect.

## Five-stage pipeline

```
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  1. Repro   │ →  │  2. Guard   │ →  │ 3. Minimise │ →  │  4. Bisect  │ →  │  5. File    │
  │  (manual)   │    │ (lean-mwe)  │    │ (lean-mwe)  │    │(lean-bisect)│    │  (lean-pr)  │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │                   │
   reproduce          one-line          shrink to           narrow to          attach MWE +
   the failure        guard that        ≤30-line MWE        single commit      offending
   locally            triggers it       (or theorem)        / toolchain        commit hash
                                                            bump
```

Stages 2–4 are tool-driven; stages 1 and 5 are human-driven.

## "Do I need MWE first?" decision table

| Symptom | Need MWE? | Need bisect? | Order |
|---|---|---|---|
| `lake build` fails on one file, fresh checkout | **Yes** | Maybe — only if it used to pass | MWE first; bisect optional |
| Single `theorem` errors with cryptic message | **Yes** | No | MWE only |
| `theorem` passes locally, fails in CI | **Yes** | No | MWE first to reproduce CI shape |
| Slowdown vs. previous toolchain | Optional | **Yes** | Bisect first to find culprit, MWE to confirm |
| `lake update` regressed a downstream proof | Optional | **Yes** | Bisect first |
| Spurious `sorry` after `import Mathlib` shuffle | **Yes** | **Yes** | MWE first (so bisect has a stable test file) |
| `lean4` itself crashes / `panic` | **Yes** | Probably yes | MWE first (compiler MWE), then bisect Lean toolchain |
| Heartbeat exhaustion on a stable proof | **Yes** | Maybe | MWE first (with `set_option maxHeartbeats 0` removed) |

## Hand-off contract

The MWE artifact emitted by `lean-mwe` (single `.lean` file, no
extra-package imports beyond Mathlib/Cslib, exits non-zero on the
failure) is exactly the test file `lean-bisect` requires (it scripts
`lake build <file>` and checks the exit code). The two skills are
deliberately designed to chain at this boundary — keep the MWE
self-contained so bisect doesn't need patching to swap toolchains.

## File-it-upstream checklist

- [ ] MWE under `Lean.MWE.<Issue>` or `Mathlib.MWE.<Issue>` namespace
- [ ] Fail-mode comment at top: expected error message, line, exit code
- [ ] If bisect was used: include the `lean-bisect` summary
      (`<bad commit hash>` + one-line description of the regression)
- [ ] Toolchain version (`lean --version` + `lake --version`)
- [ ] Mathlib + Cslib commits (`git -C .lake/packages/<pkg> rev-parse HEAD`)
- [ ] Link to upstream tracking issue if one exists
- [ ] Cross-link in `lean-pr` body so the reviewer sees the artifact

## See also

- [`../../skills/_overrides/lean-mwe/SKILL.md`](../../skills/_overrides/lean-mwe/SKILL.md) — Minimal working example construction
- [`../../skills/_overrides/lean-bisect/SKILL.md`](../../skills/_overrides/lean-bisect/SKILL.md) — Git bisect for regressions
- [`../../skills/_overrides/lean-pr/SKILL.md`](../../skills/_overrides/lean-pr/SKILL.md) — PR submission workflow
- [`./lean-nightly-infrastructure.md`](./lean-nightly-infrastructure.md) — Nightly testing infrastructure (added in W4 Wave 1 / A4)
