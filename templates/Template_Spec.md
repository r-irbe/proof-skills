# Template_Spec.md — Theorem specification artefact

> **Status:** v2 production template (extracted from
> `_v2-proposals/workflow-templates-v2.md §5`).
> A specification records the **what + why + how** of a planned
> theorem before it is implemented.  Each instantiation is a Markdown
> file under e.g. `docs/specs/SPEC-YYYYMMDD-NNN.md`.

---

## 1. When to use

* You want to formalise a paper claim and need to record the precise
  Lean statement before writing any proof.
* You are decomposing a hard theorem into sub-lemmas, each of which
  becomes its own `SPEC-id` (with `predecessors:` / `successors:`
  links).
* You want machine-linkable authority for a future PR
  (the PR's `authority:` chain cites this SPEC-id).

**Lifecycle.** `proposed → approved → implemented → reviewed → merged`.
Each transition adds acceptance criteria (see §5).

---

## 2. Template

````markdown
---
kind: spec
id: SPEC-YYYYMMDD-NNN
title: "<theorem one-liner, ≤80 chars>"
status: proposed             # proposed | approved | implemented | reviewed | merged | rejected
priority: P2                 # P0-blocker | P1-critical | P2-important | P3-enhancement
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id>"
paper_claim:
  source: "<paper-file>.tex §N"   # or ADR / RFC / issue
  ref: "<equation / proposition / corollary id>"
  quote: "<exact text from paper>"
domain:
  module: "<Project>/<Path>/<…>.lean"
  section: "§N"
toolchain:
  lean: "leanprover/lean4:vX.Y.Z"
  mathlib_pin: "<short-sha>"
predecessors: []             # ["SPEC-…", …] upstream theorems
successors: []               # ["SPEC-…", …] downstream theorems
skill: "skills/skills/lean-specification/SKILL.md@vX.Y.Z"
---

# SPEC-YYYYMMDD-NNN — <title>

## §1 Requirement (what + why)

### 1.1 Paper claim

- Source: §<section> of `<paper-file>.tex`
- Equation / Proposition: <ref>
- Quote: "<exact text from paper>"

### 1.2 English statement

"<Plain-English translation.  One sentence.>"

### 1.3 Preconditions

- <hypothesis 1>
- <hypothesis 2>
- <type constraints, bounds, simplex membership>

### 1.4 Domain placement

- Module: `<Project>/<…>.lean` §<N>
- DAG layer: <0 | 1 | 2 | 3 | 4> (per project AGENT.md "DAG Build Layers")
- Related existing theorems: <names>

## §2 Design (how)

### 2.1 Lean signature (final form; NO `sorry`)

```lean
theorem <name> {params : Types}
    (h₁ : <condition₁>) (h₂ : <condition₂>) :
    <conclusion> :=
  by /- proof sketch goes in §2.2; final signature must NOT carry a
        placeholder body.  Until ready, leave the body blank and mark
        status: proposed (not implemented). -/
```

> **v2 rule:** a spec at `status: proposed` may omit the proof body
> entirely.  A spec at `status: implemented` MUST carry a proof body
> with **no `sorry` and no `admit`**.

### 2.2 Proof strategy

1. <high-level step>
2. <high-level step>
3. <high-level step>

### 2.3 Tactic candidates

> Per project proof discipline.  Deprecated project tactics MUST NOT
> appear in this table — list only the current, supported set.

| Step | Primary           | Fallback                | Notes                |
|------|-------------------|-------------------------|----------------------|
|  0   | `grind`           | `grind`                 | always first         |
|  1   | `omega`           | `linarith`              | Nat / Int            |
|  2   | `nlinarith`       | `ring` + `positivity`   | Real with products   |
|  3   | `simp [<lemma>]`  | `unfold` + `omega`      | unfold + close       |

### 2.4 Dependencies

- Upstream lemmas (mathlib or project): <list>
- Upstream definitions: <list>
- Upstream modules to `import`: <list>

### 2.5 Difficulty + fallback

- Estimated: trivial | moderate | hard | research
- Rationale: <one sentence>
- Fallback if primary strategy fails:
  1. <alternative>
  2. <decomposition into sub-lemmas, each its own SPEC-id>

## §3 Documentation

### 3.1 Docstring (≤ 5 lines)

```lean
/-- One sentence summary.  References paper §N equation E.
    Used by: <downstream theorem names>. -/
```

### 3.2 Paper appendix update

- [ ] Per-module theorem count in `<paper-file>.tex` `\description`
- [ ] Total metrics in contribution inventory + Lean appendix sidenote
- [ ] If validating a new paper claim: add to enumerated properties
      list + verification mapping table

## §4 Reproducibility checklist

- [ ] `lake build <Project>.<Module>` GREEN at `toolchain.mathlib_pin`
- [ ] `lake build` (full) GREEN — 0 errors, 0 new warnings
- [ ] `#print axioms <name>` shows only
      `{propext, Classical.choice, Quot.sound}`
- [ ] No `sorry`, no `admit`, no unwhitelisted `axiom`
- [ ] `grep -n "theorem <name>" <Project>/*.lean` returns exactly 1 hit
      (no duplicate)
- [ ] Project AGENT.md "When Adding New Theorems" procedure executed
      in full

## §5 Acceptance criteria

By status:

**`proposed`** is good when:
1. §1 Requirement is complete (paper claim quoted, English stated,
   preconditions enumerated, domain placement set).
2. §2.1 signature type-checks (statement-only; no body required).
3. §2.4 dependencies are real (file:line references resolve).
4. `predecessors` in frontmatter list every transitively-required SPEC.

**`implemented`** adds:
5. Proof body is present and contains no `sorry`, no `admit`.
6. §4 reproducibility checklist is fully ticked.
7. `successors` in frontmatter is updated to include any new specs
   that depend on this one.

**`merged`** adds:
8. The theorem is referenced in the project paper / spec per §3.2.
9. A `PR-id` link is added to `refs:` and resolves to a merged PR.

## §6 Skill citation

Produced by `skills/skills/lean-specification/SKILL.md@vX.Y.Z`.  The
authority on tactic choice is the project AGENT.md "Proof Search
Strategy" section and `skills/references/lean4-proof-strategy.md`.
Hard constraints on sorry/axioms come from the project AGENT.md
"Hard Constraints" section.
````

---

## 3. What v2 adds over v1

* Collapses three v1 files (`REQ-` + `DES-` + `DOC-`) into one
  `SPEC-id` file with three sections.
* Full YAML frontmatter (`status`, `priority`, `paper_claim`,
  `predecessors`, `successors`).
* Removes `sorry -- placeholder` from the template signature; replaces
  with explicit "proposed = no body, implemented = no sorry" rule.
* §4 reproducibility checklist.
* §5 per-status acceptance criteria (`proposed → implemented →
  merged` lifecycle gates).

---

## 4. See also

* [`Template_PR.md`](./Template_PR.md) — the PR that lands this spec cites it in `authority:`
* [`Template_Council.md`](./Template_Council.md) — design critique of the spec
* [`Template_Theorem.md`](./Template_Theorem.md) — Lean module shape implementing the spec
* [`00-CONVENTIONS.md`](./00-CONVENTIONS.md) — frontmatter spine
* `_v2-proposals/workflow-templates-v2.md §5` — full gap analysis & evidence
