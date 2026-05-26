# Template_Bisect.md — Regression-bisect artefact

> **Status:** v2 production template (extracted from
> `_v2-proposals/workflow-templates-v2.md §6`).
> Use to record the result of a `script/lean-bisect` run that
> localises a regression to a specific upstream commit.  Each
> instantiation is a Markdown file under
> e.g. `docs/bisect/BISECT-YYYYMMDD-NNN.md`.

---

## 1. When to use

* A behaviour changed between two `lean4` / `mathlib4` / `cslib` /
  `Batteries` (etc.) versions, and you have an MWE that exhibits the
  delta.
* You want a stable record of the bisect command, the result commit,
  and the root-cause hypothesis so a future reader can re-run from a
  clean checkout.

**Prerequisite.** Every bisect needs an MWE.  Create the MWE first
(see [`Template_MWE.md`](./Template_MWE.md)) and reference it via
`mwe_ref:` in frontmatter.

---

## 2. Template

````markdown
---
kind: bisect
id: BISECT-YYYYMMDD-NNN
title: "<regression one-liner>"
status: draft                # draft | running | landed | superseded
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id>"
upstream: "lean4 | mathlib4 | cslib | <Project>-internal"
mwe_ref: "MWE-YYYYMMDD-NNN"  # required if Mathlib-rooted; required
                              # also for project regressions if a minimal
                              # test was authored
range:
  good: "<short-sha or nightly-YYYY-MM-DD>"
  bad:  "<short-sha or nightly-YYYY-MM-DD>"
options:
  timeout_s: 60
  ignore_messages: false
  nightly_only: false
  selftest_passed: true
result:
  commit: "<short-sha>"            # the bisect-identified commit
  author: "<commit-author>"
  message_subject: "<commit subject line>"
  files_touched: 0
  loc_changed: "+N / -M"
skill: "skills/skills/lean-bisect/SKILL.md@vX.Y.Z"
refs:
  - "<related ZK or wave doc>"
---

# BISECT-YYYYMMDD-NNN — <title>

## §1 Symptom

What changed between `range.good` and `range.bad`.  Paste the
diagnostic delta verbatim:

```
# at <range.good>
<output>

# at <range.bad>
<output>
```

## §2 MWE feeding this bisect

- File: `<path/to/MWE.lean>`
- Frontmatter id: `<MWE-id>` (full artefact at `…/MWE-….md`)
- Self-contained? yes (no Mathlib imports) / no (justification:
  <reason — bisect will fail outside Mathlib-pinned ranges>)
- LOC: N
- Guard: `guard_msgs | guard_panic | exit_code`

## §3 Bisect command (verbatim)

```bash
script/lean-bisect <path/to/MWE.lean> \
    <range.good>..<range.bad> \
    --timeout <options.timeout_s> \
    [--ignore-messages] [--nightly-only]
```

- Endpoint verification: `script/lean-bisect ... --selftest` →
  `options.selftest_passed`.
- Bisect steps performed: N
- Wall-clock duration: HH:MM:SS

## §4 Identified commit

- SHA: `<result.commit>`
- Author: `<result.author>`
- Subject: `<result.message_subject>`
- Files touched: <result.files_touched>
- LOC: `<result.loc_changed>`
- Permalink: `https://github.com/<upstream>/commit/<result.commit>`

### Diff summary (paste `git show --stat <result.commit>`)

```
<paste>
```

### Root-cause hypothesis (one paragraph)

<Your best guess at why this commit changes the diagnostic captured in
§1.  Cite specific changed files / lines.>

## §5 Reproducibility checklist

- [ ] MWE at `mwe_ref` compiles to the §1 "bad" diagnostic at
      `range.bad` and the "good" diagnostic at `range.good`
- [ ] `range.good` and `range.bad` are both reachable via
      `elan install <release>`
- [ ] The `script/lean-bisect` command in §3 can be re-run on a fresh
      checkout and yields the same `result.commit`
- [ ] `options.selftest_passed: true` was recorded before the run
- [ ] If the MWE was reduced from a project file, the original tactic
      was `grind` (or another project default) and the MWE preserves
      that tactic (per `lean-bisect/SKILL.md:79`)
- [ ] If `ignore_messages: true`, the rationale is in §1 (e.g.
      "diagnostic wording changed; only exit code matters")

## §6 Acceptance criteria

This bisect is "good" when **all** of the following hold:

1. `mwe_ref` resolves and the linked MWE has `status: active | landed`.
2. `range.good` and `range.bad` are both valid release identifiers (a
   tag, a nightly-YYYY-MM-DD, or a commit reachable from the upstream
   branch).
3. `result.commit` was reproducible on a re-run from a clean checkout
   (§5 box ticked).
4. §3 records the exact command (no `<…>` placeholders left).
5. §4 includes the `git show --stat` paste AND a one-paragraph
   root-cause hypothesis.
6. If `upstream != <Project>-internal`, a downstream issue/PR link is
   recorded in `refs:` once the bisect is filed.
7. The artefact ends with §7 skill citation.

## §7 Skill citation

Produced by `skills/skills/lean-bisect/SKILL.md@vX.Y.Z`.  The MWE that
feeds this bisect is produced by `skills/skills/lean-mwe/SKILL.md`
(see `Template_MWE.md`).  Upstream filing follows
`skills/skills/lean-pr/SKILL.md` (see `Template_PR.md`).
````

---

## 3. What v2 adds over v1

* Bisect-artefact concept (v1 had only stdout).
* `mwe_ref` field linking MWE ↔ bisect by id.
* Verbatim command block (with `--selftest` precondition).
* `git show --stat` paste of the identified commit.
* Root-cause hypothesis paragraph.
* §5 enforces `grind`-first MWE rule as a checklist gate.
* §6 acceptance criteria; in particular re-run reproducibility.

---

## 4. See also

* [`Template_MWE.md`](./Template_MWE.md) — the reproducer feeding this bisect
* [`Template_PR.md`](./Template_PR.md) — upstream filing using this bisect
* [`Template_Zettelkasten.md`](./Template_Zettelkasten.md) — capture the root-cause insight
* [`00-CONVENTIONS.md`](./00-CONVENTIONS.md) — frontmatter spine
* `_v2-proposals/workflow-templates-v2.md §6` — full gap analysis & evidence
