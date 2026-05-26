# Template_Council.md — Council review / design critique artefact

> **Status:** v2 production template (extracted from
> `_v2-proposals/workflow-templates-v2.md §7`).
> Records a design critique (single-critic or full-council mode) of a
> wave plan, spec, PR, or other artefact.  Each instantiation is a
> Markdown file under e.g. `docs/reviews/COUNCIL-YYYYMMDD-NNN.md`.

---

## 1. When to use

* Before landing a non-trivial design (new wave plan, big refactor, new
  cluster), invoke a critique pass and record it.
* A reviewer (single agent or the five-member council Σ / Φ / Ν / Λ /
  Ω) audits one or more input docs, surfaces concerns, proposes
  amendments, and renders a verdict.
* The verdict + amendments authorise (or block) the downstream
  implementation work.

**Two modes.**
* `single-critic`: one agent reviews; severity = Blocking /
  Non-Blocking / Suggestion.
* `full-council`: five members vote; verdict aggregates the votes.

---

## 2. Template

````markdown
---
kind: council-review
id: COUNCIL-YYYYMMDD-NNN     # or W<NN>-B<N>-a<N>-design-critique
title: "<one-line scope>"
status: draft                # draft | landed | superseded
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
agent: "<agent-id>"           # primary critic
council_role: "a5-critique"   # or Σ | Φ | Ν | Λ | Ω if single-member
mode: "single-critic | full-council"
session: "<session-id>"
wave: 0
batch: 0
shard: ""
pin_head: "<short-sha>"
mathlib_pin: "<short-sha>"
cslib_pin: "<short-sha>"
lspec_pin: "<short-sha>"
lean_toolchain: "leanprover/lean4:vX.Y.Z"
inputs_audited:
  - "<path/to/doc.md>"
  - "<path/to/another.md>"
sibling_artifacts_inferred_only: []   # docs referenced but not yet read
verdict: "GO | GO-WITH-AMENDMENTS | NO-GO | PASS-WITH-FIXES"
counts:
  blocking: 0
  major: 0
  minor: 0
  nit: 0
skill: "skills/skills/lean-review-council/SKILL.md@vX.Y.Z"
---

# COUNCIL-YYYYMMDD-NNN — <title>

## §0 Executive verdict

**<verdict>**.  <One paragraph summary: what was reviewed, what the
critique concluded, what the next action is.>

Severity scale (single-critic mode): **Blocking / Non-Blocking /
Suggestion**.
Five-member voting (full-council mode): see §3.

## §1 Pressure-test summary (single-critic mode)

Bullet list of risks discovered, each ≤ 2 sentences, each tagged with
a proposed amendment id (`M-N`).

- **<topic>**: <observation>.  → M-1
- **<topic>**: <observation>.  → M-2
- …

## §2 Amendments table

| M-id    | Concern              | Severity     | Proposed amendment | Adoption recommendation |
|---------|----------------------|--------------|--------------------|-------------------------|
| **M-1** | <one-line concern>   | Blocking     | <concrete fix>     | **ADOPT**               |
| **M-2** | <one-line concern>   | Non-Blocking | <concrete fix>     | **ADOPT-EQUIVALENT**    |
| **M-N** | …                    | Suggestion   | <concrete fix>     | **DEFER**               |

> **Adoption recommendation vocabulary:**
> **ADOPT** (apply verbatim) ·
> **ADOPT-EQUIVALENT** (apply a functionally-equivalent change) ·
> **DEFER** (carry to the next wave) ·
> **REJECT** (with rationale).

## §3 Review findings table (full-council mode only)

| Member | Finding               | Severity     | Evidence              | Line   |
|--------|-----------------------|--------------|-----------------------|--------|
| Σ      | <kernel finding>      | Blocking     | `#print axioms` out   | L42    |
| Φ      | <statement finding>   | Non-Blocking | English translation   | L10    |
| Ν      | <novelty finding>     | Suggestion   | `exact?` result       | L10    |
| Λ      | <quality finding>     | Non-Blocking | step count = N        | L42-80 |
| Ω      | <integration finding> | Non-Blocking | grep result           | all    |

### Votes

| Σ | Φ | Ν | Λ | Ω | Decision                  |
|---|---|---|---|---|---------------------------|
| ✅ | 🟡 | ✅ | 🟠 | ✅ | Approved with amendments  |

## §4 Specific notes by review dimension

(Free-form; one short subsection per axis: scope, staging, gates,
dependencies, conventions, anti-collapse safeguards.)

## §5 Reproducibility checklist

- [ ] All docs in `inputs_audited` resolve at `pin_head`
- [ ] `lake build <Project>` (or relevant target) GREEN at `pin_head`
- [ ] Every M-id in §2 cross-references a file:line in an input doc
- [ ] If `mode: full-council`, every council member has a row in §3
- [ ] If `mode: single-critic`, the `agent` field identifies the
      reviewing agent and `council_role: a5-critique` (or equivalent)
- [ ] `verdict` matches the §0 paragraph wording

## §6 Acceptance criteria

This critique is "good" when **all** of the following hold:

1. `inputs_audited` enumerates ≥ 1 doc and is not "TBD".
2. §0 verdict matches `verdict` in frontmatter.
3. §2 amendments table is non-empty if `verdict ∈ {GO-WITH-AMENDMENTS,
   NO-GO, PASS-WITH-FIXES}`; may be empty only if `verdict: GO`.
4. Severity counts in frontmatter (`counts.{blocking, major, minor,
   nit}`) sum to the §2 amendment count.
5. Every BLOCKER amendment carries an **ADOPT** recommendation OR a
   `verdict: NO-GO` justification.
6. The next-action (which downstream artefact must apply the
   amendments — a `b1-integration.md`, a follow-up spec, a PR) is
   named in §0.

## §7 Skill citation

Produced by `skills/skills/lean-review-council/SKILL.md@vX.Y.Z`.  The
five-member roster (Σ / Φ / Ν / Λ / Ω) is at
`lean-review-council/SKILL.md "Part 1 — The Five Council Members"`.
Topology selection follows
`lean-review-council/SKILL.md "Part 4 — Council Topologies"`.
````

---

## 3. What v2 adds over v1

* Frontmatter reconciles wave-doc shape with the SKILL template (adds
  `wave/batch/shard/pin_head/mathlib_pin/cslib_pin/lspec_pin/
  lean_toolchain/inputs_audited/verdict/counts`).
* §2 amendments table canonicalised (column set fixed).
* Bimodal template (`single-critic` vs `full-council`) — real wave
  critiques are nearly always single-critic.
* §5 reproducibility checklist; §6 acceptance criteria.
* Verdict vocabulary unified
  (`GO | GO-WITH-AMENDMENTS | NO-GO | PASS-WITH-FIXES`).
* Severity-count cross-check between frontmatter and table body.

---

## 4. See also

* [`Template_Spec.md`](./Template_Spec.md) — specs are common inputs to a council review
* [`Template_PR.md`](./Template_PR.md) — PRs cite the council in `authority:`
* [`Template_RetroLog.md`](./Template_RetroLog.md) — wave closeouts cite all council reviews of the wave
* [`00-CONVENTIONS.md`](./00-CONVENTIONS.md) — frontmatter spine
* `_v2-proposals/workflow-templates-v2.md §7` — full gap analysis & evidence
