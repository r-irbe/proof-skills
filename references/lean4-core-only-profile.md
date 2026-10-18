# Core-only Lean 4 profile (no Mathlib)

Handbook for [`skills/lean-core-only`](../skills/lean-core-only/SKILL.md).
Everything below is about a lane whose artifact may import the Lean toolchain
only: a judge/contest submission, a vendored artifact, or a `lakefile.toml`
package with no dependencies.

Two facts drive the whole profile:

1. A core-only project has **no `LEAN_PATH` for project modules unless Lake
   supplies it**, so the invocation is part of the proof.
2. The **tactic namespace is smaller than Mathlib's**, and a missing tactic is
   reported as `unknown tactic` -- an import question that a core-only lane is
   not allowed to answer by importing.

---

## 1. Invocation: `lake env lean`, never bare `lean`

| Situation | Command |
|---|---|
| Root has `lakefile.lean` **or** `lakefile.toml` | `lake env lean <File>.lean` from the root |
| Root has only `lean-toolchain` (no lakefile) | `lean <File>.lean` (no project modules exist) |
| Need one module compiled as the build sees it | `lake build <Module>` |
| Whole-lane gate (judge shape) | `lake build` (default targets, default limits) |

`lakefile.toml` is a first-class Lake root. Detection code that only looks for
`lakefile.lean` will miss every lane built by `lake new --toml` or by a
problem-workspace copy, and the failure surfaces far away from the cause:

```
$ lean Foo.lean                       # WRONG (no LEAN_PATH)
Foo.lean:1:0: error: unknown module prefix 'Spec'

$ lake env lean Foo.lean              # RIGHT
(no output)
```

Rules:

- `unknown module prefix 'X'` is **always** an invocation/root problem, never a
  statement problem. Check the root and re-run under `lake env lean` first.
- Anything that shells out to Lean on the project's behalf (an MCP server, a
  script, a CI step) must run **inside the project root** with `lake env lean`.
  A helper launched from a different cwd silently answers about a different
  project.
- Setting `LEAN_PATH` by hand is a diagnostic, not a fix: it bypasses the pinned
  toolchain and the project's `leanOptions`.

## 2. Tactic availability (measured, not remembered)

Measured on **Lean 4.33.1, zero imports**, by elaborating one tactic per goal:

```bash
cd <empty lake project>
for t in omega simp decide rfl linarith ring norm_num aesop grind; do
  printf 'example (n : Nat) (h : n >= 3) : n + 1 >= 4 := by %s\n' "$t" \
    | lake env lean --stdin 2>&1 | head -1 | grep -q 'unknown tactic' \
    && echo "$t ABSENT" || echo "$t present"
done
```

**Present in core:** `omega`, `simp`, `simp_all`, `simp_arith`, `simpa`,
`decide`, `native_decide`, `norm_cast`, `push_cast`, `rfl`, `ac_rfl`, `calc`,
`rw`, `exact`, `apply`, `refine`, `intro`, `intros`, `cases`, `induction`,
`by_cases`, `split`, `injection`, `contradiction`, `exfalso`, `subst`,
`funext`, `generalize`, `rcases`, `rintro`, `obtain`, `have`, `haveI`, `show`,
`trivial`, `cc`, `bv_omega`, `grind`, `exact?`, `apply?`, `simp?`.

**Absent (Mathlib-only):** `linarith`, `nlinarith`, `ring`, `ring_nf`,
`ring_exp`, `norm_num`, `positivity`, `gcongr`, `field_simp`, `polyrith`,
`aesop`, `tauto`, `interval_cases`, `fin_cases`, `convert`, `use`, `decide!`.

Notes that matter in practice:

- `grind` **is** core in current toolchains -- do not assume every
  "search tactic" is Mathlib. Re-run the probe above when the toolchain pin
  moves; this table ages.
- `norm_num` absent means concrete arithmetic must go through `decide`,
  `omega`, or `simp` with explicit lemmas.
- `convert` absent changes the "generalise then instantiate" recipe: in core use
  `suffices`/`have` + `exact` instead.
- `native_decide` being *available* does not make it *allowed*: a judge class
  that bans it (trust surface) still bans it.

## 3. Recursion and heartbeat triage

| Message | What it is | First move |
|---|---|---|
| `maximum recursion depth has been reached` | Elaborator/kernel depth bound (`maxRecDepth`, default 1000) | Raise it **locally** (`set_option maxRecDepth 10000 in`) to see whether the proof is otherwise correct |
| `maximum heartbeats exceeded` | Elaboration budget (`maxHeartbeats`) | Same: raise locally to localise, then fix the structure |
| `deep recursion was detected` during `decide`/`rfl` on a closed term | Kernel evaluation of a big term | Do not fight it: prove a lemma that avoids the closed-term reduction |
| Build fine, `rfl`-proof dies at one declaration | Opaque computation in a definitional-equality step | Replace `rfl` with a structural lemma (`Nat.rec` induction) |

Rules:

- A limit failure is a **limit** failure. It says nothing about truth. Report it
  as "elaboration limit tripped on <declaration>", never "statement is false".
- Raising limits is a **diagnostic**, not a fix: the judge builds at defaults.
  Leaving `set_option maxHeartbeats 0` in a shipped artifact moves the failure to
  the judge's run.
- The structural fixes, in the order that usually works:
  1. Register/prove the recurrence earlier so the kernel never unfolds the big
     term (`have` + `rw` instead of `rfl`).
  2. Split one huge definition into a chain of smaller ones.
  3. Replace `decide` on a large domain with an induction + `omega` per step.
  4. Rewrite the closed-form computation as a lemma with an explicit proof term.

## 4. Inspecting a stuck goal without touching the artifact

A core-only artifact is usually gated on zero `sorry` and zero residue, so
editing `trace_state`, `#check`, or `sorry` probes into it is a contract
violation even temporarily (and a stray probe has shipped more than once).

Preferred loop:

1. Query the goal **out of band** at the exact tactic position
   (`$/lean/plainGoal`, or `lean-lsp-mcp`'s `lean_goal {filePath, line, col}`).
2. Query the expected type at a term position (`target: "term"`).
3. Ask for diagnostics ("unknown tactic", "unsolved goals") from the same
   session, with an explicit wait budget.
4. Only when no out-of-band queryer exists: copy the file into a scratch
   directory (never edit the artifact) and use `trace_state` there.

Two verification traps to check in whatever tool you use:

- **"No diagnostics" is not "clean".** Lean publishes an empty diagnostics set
  when analysis *starts*; a client that latches the first publication reports a
  file with errors as clean. Demand a completed-analysis signal
  (`$/lean/fileProgress` with an empty `processing` list) before believing it.
- **A suspended interactive worker is not a build failure.** Some clients pause
  queries while a build is running; a "suspended" answer must be retried, not
  read as a result.

## 5. Lane checklist (core-only)

- [ ] Root identified, and it is a `lakefile.lean`/`lakefile.toml` root.
- [ ] Every command run as `lake env lean` / `lake build` from that root.
- [ ] No Mathlib-shaped tactic name left in the artifact (`linarith`, `ring`,
      `norm_num`, `positivity`, `gcongr`, `field_simp`, `aesop`, `tauto`).
- [ ] `lake build` green at DEFAULT limits, no `set_option maxHeartbeats 0`.
- [ ] `#print axioms <main theorem>` within `[propext, Classical.choice,
      Quot.sound]`; no `native_decide` if the class bans it.
- [ ] Zero `sorry` / `admit` / residue probes; no scratch files in the artifact
      tree.
- [ ] Recursion/heartbeat findings recorded with the declaration name and the
      option tripped.
