---
name: "lean-core-only-handbook"
description: "Reference handbook for @lean-core-only."
extracted_from: "skills/lean-core-only/SKILL.md"
---

# lean-core-only

> **MANDATORY** (hot-tier): G-1 (prove the invocation), G-2 (no Mathlib-only
> tactic names), and G-4 (recursion failures are ELABORATION limits, never
> "the theorem is unprovable") are hard gates. A core-only lane that reports a
> build as clean, or a statement as unprovable, without having satisfied G-1 is
> reporting an environment artefact as a mathematical result.

Core-only means: the final artifact's transitive imports are the Lean toolchain
alone. It is the normal shape for judge/contest artifacts and for any package
whose `lakefile.toml` declares no dependencies, and it changes which tactics
exist, which errors are environmental, and how a stuck proof must be inspected.

---

## Routing

- **USE FOR:** a core-only lane's tactic choices (core `omega` yes, `linarith` no);
  `import Spec` failing with `unknown module prefix`; `unknown tactic` from a
  Mathlib name; `maximum recursion depth` / `maximum heartbeats` on an otherwise
  correct-looking proof; project-root and `lakefile.toml` invocation questions;
  goal-state introspection without editing the artifact.
- **DO NOT USE FOR:** anything where Mathlib is allowed (use `@lean-proof` with
  the `@lean-math-analysis` family); the axiom-closure audit itself (use `@lean-axiom-closure`);
  toolchain brokenness (use `@lean-setup`).
- **TRIGGERS:** core Lean, no Mathlib, core-only, judge artifact, unknown module
  prefix, unknown tactic, maximum recursion depth, maxRecDepth, maxHeartbeats,
  lakefile.toml, bare lean.

## Behavioural rules (G-*)

- **G-1** (MUST): Every compile/query command MUST be run through the project
  environment -- `lake env lean <file>` from the project root (which may be a
  `lakefile.toml` root, not a `lakefile.lean` one). A bare `lean <file>` is not a
  result: it has no `LEAN_PATH`, so `unknown module prefix 'Spec'` is the expected
  output even when the build is green.
- **G-2** (MUST): Before using a tactic, the skill MUST classify it as core or
  Mathlib-only, against the MEASURED table in the handbook (probe the pinned
  toolchain when it moves). Core: `omega`, `simp`, `simp_all`, `simpa`,
  `simp_arith`, `decide`, `native_decide`, `norm_cast`, `push_cast`, `rfl`,
  `ac_rfl`, `calc`, `rw`, `exact`, `apply`, `refine`, `intro`, `cases`,
  `induction`, `by_cases`, `split`, `injection`, `contradiction`, `exfalso`,
  `subst`, `funext`, `generalize`, `rcases`, `rintro`, `obtain`, `have`,
  `show`, `trivial`, `cc`, `bv_omega`, `grind`, `exact?`, `apply?`, `simp?`.
  Mathlib-only: `linarith`, `nlinarith`, `ring`, `ring_nf`, `ring_exp`,
  `norm_num`, `positivity`, `gcongr`, `field_simp`, `polyrith`, `aesop`,
  `tauto`, `interval_cases`, `fin_cases`, `convert`, `use`, `decide!`. None of
  the Mathlib-only names may be introduced into a core-only artifact.
- **G-3** (MUST): `unknown tactic` in a core-only lane MUST be read as an import
  question, not a naming question. The fix is to rewrite the step with core
  primitives (`omega`, `simp only [...]`, `rw`, `cases`), never to add an import
  the artifact is not allowed to have.
- **G-4** (MUST): `maximum recursion depth has been reached` and
  `maximum heartbeats exceeded` are ELABORATION limits. The skill MUST report them
  as such and MUST NOT conclude that the statement is false or unprovable. Raising
  `maxRecDepth` / `maxHeartbeats` locally is a diagnostic step; a judge artifact
  must still build at DEFAULT limits, so the fix is a proof-structure change
  (register earlier, avoid `rfl`-closed opaque computation, split the definition).
- **G-5** (MUST): Goal state MUST be read with an out-of-band queryer (an LSP
  `plainGoal` verb, `lean-lsp-mcp`'s `lean_goal`) when one is available. Writing
  `trace_state`, `#check`, or `sorry` probes into a core-only artifact MUST be
  avoided: an artifact under judge rules is gated on zero `sorry` and no residue.
- **G-6** (MUST): "Clean" MUST be a completed-analysis claim. A diagnostics query
  that cannot distinguish "no findings" from "analysis did not finish" MUST NOT be
  reported as a green build; fall back to `lake build` at default limits.
- **G-7** (MUST): Import budget is part of the contract. Before adding any
  `import`, the skill MUST confirm the lane permits it; a core-only artifact that
  gains a Mathlib import has changed its trust surface and its judge class.

## Workflow

1. **Discover** [discover] -- establish the root and the invocation: which
   directory holds `lakefile.lean` / `lakefile.toml`, which toolchain is pinned,
   whether the package declares dependencies. Confirm `lake env lean <file>`
   resolves the artifact's own imports before touching any proof.
2. **Plan** [discover] -- pick the tactic set from the core list (G-2); for each
   numeric step prefer `omega`, for definitional steps `rw`/`simp only` with an
   explicit lemma list, for case analysis `cases`/`induction` + `omega` per branch.
3. **Execute** [execute] -- one tactic at a time, checking the goal out of band
   (G-5) instead of editing probes into the artifact.
4. **Validate** [validate] -- `lake build` at DEFAULT limits (no local
   `maxHeartbeats 0` in the artifact), `#print axioms` inside
   `[propext, Classical.choice, Quot.sound]`, zero `sorry`/`admit`/`native_decide`.
   A diagnostics query counts only when it reports a completed analysis (G-6).
5. **Persist** [persist] -- record the invocation used, the limits observed, and
   any recursion-limit finding in the lane NOTES; hand the axiom audit to
   `@lean-axiom-closure`.

## Recovery & STOP

- **Environment** -- `unknown module prefix` while the build is green: STOP,
  re-run through `lake env lean` from the project root (G-1) before diagnosing
  anything else.
- **Tactic availability** -- a needed step has no core-only equivalent: STOP and
  escalate. Do not smuggle in an import (G-3, G-7).
- **Recursion limits** -- the proof needs `maxRecDepth`/`maxHeartbeats` above
  defaults to elaborate: STOP and hand the declaration to `@lean-proof` for a
  structural fix; report the option that was tripped and the declaration name.
- **Untrustworthy verification** -- a tool reports "clean" but `lake build`
  disagrees: trust the build, and record the tool discrepancy (G-6).
- Same proof strategy fails 3 times: STOP; isolate with `@lean-mwe`.

## Handoffs

- **Predecessors:** `@lean-setup` (toolchain), `@lean-specification` (statement).
- **Successors:** `@lean-proof` (structural fixes), `@lean-build` (build/CI
  mechanics), `@lean-axiom-closure` (trust base), `@lean-mwe` (isolation).
- **Handbook:** [`../../references/lean4-core-only-profile.md`](../../references/lean4-core-only-profile.md)
  -- the core/Mathlib tactic boundary, the recursion-limit triage table, and the
  goal-introspection loop.

## Common failure modes

> AI agents commonly: run bare `lean file.lean` and report
> `unknown module prefix` as a code error; type `linarith` in a core-only lane and
> "fix" `unknown tactic` by adding an import the judge forbids; treat
> `maximum recursion depth` as a failed proof instead of an elaboration limit;
> edit `trace_state`/`sorry` probes into an artifact that is gated on zero residue;
> leave `set_option maxHeartbeats 0` in the shipped file so the judge's default
> limits fail; accept a diagnostics tool's first "clean" answer as a green build.

## See also

- [`../lean-build/SKILL.md`](../lean-build/SKILL.md) -- `lake env lean`, targeted
  builds, stale-artifact recovery.
- [`../lean-proof/SKILL.md`](../lean-proof/SKILL.md) -- one-tactic-at-a-time
  proving and error priority.
- [`../lean-competitive-math/SKILL.md`](../lean-competitive-math/SKILL.md) -- the
  answer-check ladder; note its L3 carve-out for `native_decide` does NOT apply to
  a judge class that bans it.
- [`../../references/lean4-lsp-proof-protocol.md`](../../references/lean4-lsp-proof-protocol.md)
  -- zero-disk-churn goal inspection.
