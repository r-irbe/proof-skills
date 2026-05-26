# Template_PR.md — Pull Request artefact

> **Status:** v2 production template (extracted from
> `_v2-proposals/workflow-templates-v2.md §2`).
> Use as a side-car artefact attached to a PR (e.g. under
> `docs/pr/PR-YYYYMMDD-NNN.md`) when contributing upstream to
> `leanprover/lean4`, `leanprover-community/mathlib4`, `cslib`, etc.,
> or for project-internal PRs that warrant a paper trail.

---

## 1. When to use

* You are filing a PR upstream and want a reproducible record that
  links the PR to its motivating MWE, bisect, spec, or council review.
* You are filing a PR project-internal and want machine-linkable
  authority (per the §7 authority chain) so a future reviewer can
  trace the decision lineage.
* You want a stable record that survives merges, force-pushes, and PR
  closures.

---

## 2. Template

````markdown
---
kind: pr
id: PR-YYYYMMDD-NNN          # local id; replace with upstream # when filed
title: "<type>: <imperative subject>"  # e.g. "feat: add fisherMatrix posDef variant"
status: draft                # draft | filed | review | merged | closed
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id or human>"
target_repo: "leanprover/lean4 | leanprover-community/mathlib4 | cslib | <Project>-internal"
target_branch: "master"
base_sha: "<short-sha>"
head_sha: "<short-sha>"
upstream_number: ""          # filled when filed; e.g. 1234
changelog_label: "changelog-{language|tactics|library|…|no}"
type: "feat | fix | doc | style | refactor | test | chore | perf"
toolchain:
  lean: "leanprover/lean4:vX.Y.Z"
  mathlib_pin: "<short-sha>"   # n/a if PR is to mathlib itself
  cslib_pin: "<short-sha>"
authority:
  - "<spec id or design doc path>"
  - "<MWE-id or bisect-id if applicable>"
skill: "skills/skills/lean-pr/SKILL.md@vX.Y.Z"  # or skills/skills/mathlib-pr/SKILL.md
---

# PR-YYYYMMDD-NNN — <title>

## §1 Description (PR body, ≤ 2 short paragraphs)

> Per `lean-pr/SKILL.md:79–87`: start with "This PR …".  No `## Summary`
> header.  No "Test plan" section.  No "Implementation details" section.

This PR <imperative, present-tense one-liner>.  <One sentence of why,
linking to the upstream issue or the project artefact that motivated it.>

<Optional second paragraph: any caveat, follow-up, or limitation.>

## §2 Change inventory

| File                       | LOC ± | Reason            |
|----------------------------|------:|-------------------|
| `<path/to/file.lean>`      | +N / -M | <one-line reason> |
| `<path/to/another.lean>`   | +N / -M | …                 |
| **Total**                  | **+N / -M** |               |

- New theorems / defs: N
- Modified theorems / defs: N
- Removed theorems / defs: N (must be 0 in `mathlib4` unless deprecation
  protocol followed)

## §3 Reproducibility checklist

- [ ] Branch checks out at `head_sha` cleanly
- [ ] `lake build` (or `lake build <Project>`) passes at `head_sha`; tail
      pasted below
- [ ] `#print axioms <new_theorem>` for every new public theorem shows
      only the standard triple `{propext, Classical.choice, Quot.sound}`
      (paste under §5)
- [ ] No new `sorry`, `admit`, or unwhitelisted `axiom`
- [ ] If `type: feat | fix`, a `changelog-*` label is set (see
      `lean-pr/SKILL.md:32–46`)
- [ ] If touching `src/Lean/`, `src/Std/`, `src/lake/Lake/`: `module` +
      `prelude` declarations present (see `lean-pr/SKILL.md:48–63`)
- [ ] Copyright header on every new file in `src/`
      (`lean-pr/SKILL.md:65–77`)

## §4 Build tail (paste verbatim)

```
✔ [N/N] Built <target> (Xs)
Build completed successfully (N jobs).
```

## §5 Axiom audit (paste verbatim)

```
'<new_theorem_1>' depends on axioms: [propext, Classical.choice, Quot.sound]
'<new_theorem_2>' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Any deviation from the standard triple must be justified in §6.

## §6 Justification of any deviations

- New axioms introduced: <list, with one-line rationale each; usually empty>
- Unwhitelisted axioms touched in call graph: <list; must be empty for
  upstream PRs>
- API breaking changes: <list; must be empty for `fix`/`doc`>

## §7 Authority chain

This PR is justified by:

1. `<spec id or design doc>` — <one-line role: design / spec / critique>
2. `<MWE-id>` — <one-line role: motivating bug report> (optional)
3. `<bisect-id>` — <one-line role: regression isolation> (optional)
4. `<ZK-id>` — <one-line role: extracted convention> (optional)

## §8 Acceptance criteria

This PR is "good" when **all** of the following hold:

1. §1 description follows `lean-pr` conventions (starts with "This PR…",
   no banned section headers, imperative present-tense title).
2. §2 change inventory totals match `git diff --stat` at `head_sha`.
3. §3 checklist is all ticked or has an explicit waiver inline.
4. §4 build tail and §5 axiom audit are verbatim, not paraphrased.
5. §6 deviations list is empty OR every deviation has an authority
   reference in §7.
6. `target_repo`, `target_branch`, `base_sha`, `head_sha`,
   `changelog_label`, and `type` in frontmatter are all populated
   before status moves from `draft` to `filed`.

## §9 Skill citation

Produced by `skills/skills/lean-pr/SKILL.md@vX.Y.Z` (or
`skills/skills/mathlib-pr/SKILL.md@vX.Y.Z` for mathlib4 contributions).
````

---

## 3. What v2 adds over v1

* Full YAML frontmatter (v1 was conventions-only).
* §2 change inventory table.
* §3 reproducibility checklist (7 gates).
* §4 / §5 verbatim build + axiom blocks.
* §7 authority chain (links MWE / Bisect / Spec / Council artefacts).
* §8 acceptance criteria.

---

## 4. See also

* [`Template_MWE.md`](./Template_MWE.md) — the bug reproducer the PR fixes
* [`Template_Bisect.md`](./Template_Bisect.md) — regression-isolation evidence
* [`Template_Spec.md`](./Template_Spec.md) — theorem specification underlying the PR
* [`Template_Council.md`](./Template_Council.md) — design critique authority
* [`00-CONVENTIONS.md`](./00-CONVENTIONS.md) — frontmatter spine
* `_v2-proposals/workflow-templates-v2.md §2` — full gap analysis & evidence
