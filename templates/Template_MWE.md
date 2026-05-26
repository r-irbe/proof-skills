# Template_MWE.md — Minimal Working Example artefact

> **Status:** v2 production template (extracted from
> `_v2-proposals/workflow-templates-v2.md §1`).  An MWE is a
> minimum-viable reproducer for an upstream or local bug.  Each
> instantiation is a Markdown file with YAML frontmatter under
> e.g. `docs/mwe/MWE-YYYYMMDD-NNN.md`.

---

## 1. When to use

* You hit a bug in `lean4`, `mathlib4`, `cslib`, `Batteries`, or
  another upstream and need to file an issue with a clean reproducer.
* You want to bisect a regression — every bisect needs an MWE.
* You discovered an internal regression in your project and want a
  stable, isolated test that survives refactors.

**Output contract.** The reproducer in §2 must compile to a verbatim
diagnostic under the pinned toolchain, in ≤ 20 LOC of body and ≤ 2
import lines.  See §6 acceptance criteria.

---

## 2. Template (copy into a new `MWE-YYYYMMDD-NNN.md`)

````markdown
---
kind: mwe
id: MWE-YYYYMMDD-NNN
title: "<one-line summary of the bug>"
status: draft         # draft | active | landed | superseded | rejected
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id or human>"
upstream: "lean4 | mathlib4 | cslib | lspec | leanblueprint | other"
upstream_issue: ""    # filled when filed; e.g. leanprover/lean4#1234
captured_from:
  module: "<Project>/<Path>/<…>.lean"
  line: 0
  commit: "<short-sha>"
toolchain:
  lean: "leanprover/lean4:vX.Y.Z-rcN"
  mathlib_pin: "<short-sha>"
  cslib_pin: "<short-sha>"
  lspec_pin: "<short-sha>"
minimizer:
  tool: "lake exe minimize"
  passes: ["delete", "import-inlining"]   # default both
  resumed: false
  rounds: 0
guard: "guard_msgs | guard_panic | exit_code"
skill: "skills/skills/lean-mwe/SKILL.md@vX.Y.Z"
refs:
  - "<related ZK note or wave doc>"
---

# MWE-YYYYMMDD-NNN — <title>

## §1 Symptom

One paragraph describing what goes wrong and why it surprised the
author.  Quote the exact error or panic message verbatim.

## §2 Reproduction (final minimised file)

```lean
import <only-imports-that-survived-minimization>

/--
error: <exact verbatim diagnostic, including line numbers>
-/
#guard_msgs in
example : <goal> := by <tactic>
```

- **Imports remaining after minimisation:** N (target: 0, ≤2
  acceptable for Mathlib-rooted bugs)
- **LOC remaining after minimisation:** N (target: ≤20)

## §3 Reproducibility checklist

- [ ] `lake env lean MWE.lean` returns exit code 0 (guard passed)
- [ ] `lake --version` matches `toolchain.lean` in frontmatter
- [ ] `lean-toolchain` file in workspace pins exactly that release
- [ ] No `Mathlib` imports remain (or count ≤2 with explicit
      justification in §4)
- [ ] No `sorry` / `admit` anywhere in the file
- [ ] `#print axioms` on the minimal example shows only
      `{propext, Classical.choice, Quot.sound}` — extra axioms must be
      listed in §4

## §4 Provenance

Original site that triggered the bug:

- File:        `<Project/…/Module.lean:L>`
- Original commit: `<short-sha>`
- Original tactic: `<the tactic line that failed>`
- Suspected upstream component: `<elaborator | linter | simp set | …>`

Notes on imports / axioms that could not be removed and why.

## §5 Bisect handoff (optional but recommended)

If this MWE should feed `script/lean-bisect`:

- Self-contained?    yes / no
- Bisect range:      `<good-nightly>..<bad-nightly>` (or empty)
- Pass/fail mode:    exit-code | guard_msgs | ignore-messages
- Expected good sha: `<short-sha>` (verified locally)
- Expected bad sha:  `<short-sha>` (verified locally)

→ When this MWE is fed to `lean-bisect`, file the resulting
`Bisect-YYYYMMDD-NNN.md` and cross-link it in `refs:`.

## §6 Acceptance criteria

This MWE is "good" when **all** of the following hold:

1. The reproduction file in §2 compiles to the verbatim diagnostic
   under the pinned toolchain.
2. Frontmatter `toolchain.*` keys are all populated (no `?`, no `n/a`).
3. The file would be acceptable to file upstream as-is (no project
   imports, no project-private namespaces, no `sorry`).
4. Reproduction is bounded: ≤ 20 LOC of body, ≤ 2 import lines.
5. `#print axioms` is captured in §4 if anything beyond the
   `{propext, Classical.choice, Quot.sound}` triple appears.
6. A `lean-bisect` handoff section exists (even if "n/a").

## §7 Skill citation

Produced by `skills/skills/lean-mwe/SKILL.md@vX.Y.Z`.  See also
`skills/templates/Template_DataModule.md` for the starter module
shape from which §2 reproductions were factored.
````

---

## 3. What v2 adds over v1

* YAML frontmatter (`kind`, `id`, `toolchain` triple, `minimizer.*`,
  `skill`).
* §3 reproducibility checklist (6 gates) replacing 4 free-form bullets.
* §5 explicit bisect handoff block (was prose-only).
* §6 acceptance criteria (none in v1).
* §7 skill back-pointer (none in v1).

---

## 4. See also

* [`Template_PR.md`](./Template_PR.md) — file the bug upstream
* [`Template_Bisect.md`](./Template_Bisect.md) — isolate a regression with this MWE
* [`Template_Zettelkasten.md`](./Template_Zettelkasten.md) — capture an insight from the MWE
* [`00-CONVENTIONS.md`](./00-CONVENTIONS.md) — frontmatter spine + comment-tag conventions
* `_v2-proposals/workflow-templates-v2.md §1` — full gap analysis & evidence
