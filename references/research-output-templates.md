# Research Output Templates (M / T / L / S / D / X / E)

Per-type output templates for the 7 typed research protocols dispatched
from [`lean-research/SKILL.md`](../skills/lean-research/SKILL.md) Part 9.
Use these as the post-research deliverable so downstream skills
(`lean-proof`, `lean-proof-review`, `lean-enforcement`, `epistemic-mapping`,
`research-council`) can consume the findings deterministically.

Cross-reference for protocols, depth budgets, and dispatch routing:
see `lean-research` Part 9.

---

## Type M — Mathematical Research

```markdown
## Research: Type M — [topic]
- **Goal:** [Lean goal statement]
- **Strategy chosen:** [direct / contradiction / induction / calc]
- **Key lemmas used:** [list with sources]
- **Alternative strategies considered:** [why rejected]
- **Epistemic transition:** [KU→KK or UU→KU or ...]
- **ZK note created:** [ZK-ID if applicable]
```

---

## Type T — Tactic & API Research

```markdown
## Research: Type T — [goal description]
- **Goal type:** [arithmetic / propositional / set / order / topology / category]
- **Automated result:** `exact?` found [lemma] / no result
- **Recommended tactic:** [tactic] with [lemma arguments]
- **Alternatives:** [other approaches that work]
- **New to add to `Tactics.lean`?** [yes / no — if a helper would be reusable]
```

When the task is *"find the theorem / API / tactic"*, also follow the
bundle-level [`theorem-search`](theorem-search.md) loop and report:

1. the goal shape queried,
2. at least one Loogle or Mathlib-search query,
3. any `#check` / `#find` / `exact?` / `apply?` / `rw?` / `simp?` result,
4. the verified candidate tried in Lean,
5. the final proof fragment or reason no candidate worked.

---

## Type L — Literature Research

```markdown
## Research: Type L — [topic]
- **Sources consulted:** [list with citations]
- **Key findings:**
  1. [finding + source]
  2. [finding + source]
- **Applicable to <Project>:** [yes / no / partially]
- **Reusable code / proofs:** [list with locations]
- **ZK notes created:** [ZK-IDs]
```

---

## Type S — Safety & Soundness Research

```markdown
## Research: Type S — [theorem / module]
- **Axiom status:** [clean / contaminated]
- **Vacuity status:** [non-vacuous / potentially vacuous / vacuous]
- **Faithfulness:** [matches paper / diverges — how]
- **Boundary cases:** [tested / issues found]
- **Cross-module soundness:** [clean / issues]
```

---

## Type D — Design & Architecture Research

```markdown
## Research: Type D — [design question]
- **Options evaluated:** [list]
- **Recommended:** [option with rationale]
- **Trade-offs:** [what we give up]
- **Migration needed:** [yes / no — scope if yes]
```

---

## Type X — Cross-Domain Research

```markdown
## Research: Type X — [domain + topic]
- **Domain:** [AI safety / RL / stochastic / ...]
- **Domain skill consulted:** SK-[N]
- **Concept mapping:** [domain concept → Lean type]
- **Domain assumptions:** [list]
- **Cross-domain connections:** [other domains with similar concepts]
```

---

## Type E — Epistemic Research

Delegates to [`epistemic-mapping`](../skills/epistemic-mapping/SKILL.md)
and [`research-council`](../skills/research-council/SKILL.md).  The
output of Type E is the updated epistemic map plus a list of follow-up
M/T/L/S/D/X research tasks for each newly-promoted Known-Unknown.

```markdown
## Research: Type E — [target module/theorem]
- **Audit scope:** [module / theorem / wave]
- **KK → KU transitions:** [list]
- **KU → KK transitions:** [list]
- **UU → KU discoveries:** [list — these are the high-value findings]
- **Follow-up research tasks dispatched:** [list with type tags]
- **Epistemic map delta:** [link to the updated map artefact]
```
