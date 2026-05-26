# Research Queue Management

Single canonical reference for prioritising, parallelising, and
budgeting research tasks dispatched from
[`lean-research/SKILL.md`](../skills/lean-research/SKILL.md) Part 9.

---

## Priority Rules

```
P0  Research blocking a proof that blocks a P0 fix
P1  Research for a P1 finding or missing coverage
P2  Research for improvement or optimisation
P3  Exploration or curiosity-driven research
```

Within a priority band, FIFO unless the dispatch site explicitly
re-prioritises.

---

## Parallelisation Rules

| Combination | Parallel-safe? | Notes |
|---|---|---|
| Type M ∥ Type T | yes | Different goal classes; no shared mutable state |
| Type L | always | Pure read; can fan out across many sub-questions |
| Type S after Type M | sequenced | Need the proof artefact before checking soundness |
| Type D before implementation | sequenced | Design choices gate the proof-writing work |
| Type E at project checkpoints | sequenced | Snapshots the epistemic map; do not run mid-wave |
| Type X ∥ {M, T, L} | yes | Domain consultation is read-mostly |

When dispatching multiple Type-M / Type-T sub-questions in parallel,
budget per-question is unchanged but the wall-clock budget for the
overall task is the *max* of sub-question budgets, not the sum.

---

## Budget Tracking

Each research task carries a time budget set by the depth level
chosen in [`lean-research`](../skills/lean-research/SKILL.md) Part 4
(Quick / Standard / Deep / Exhaustive).

If the budget is exceeded:

1. Checkpoint findings (write the partial deliverable using the
   matching output template from
   [`research-output-templates.md`](research-output-templates.md)).
2. Return partial results to the dispatcher.
3. Suggest one of {extend budget, narrow scope, escalate to council}.

Budget overruns are a Trigger 1 (Confidence) signal — never silently
keep researching past the budget.  Escalate per the HITL contract.
