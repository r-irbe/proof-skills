# 05 — Zettelkasten

**Status:** RECONSTRUCTED stub (R27 audit).

## 1. Where notes live

```
zettelkasten/
  _index.md                  -- the entry point (rendered as a graph map)
  permanent/zk-NNN-<slug>.md -- numbered durable notes
  fleeting/                  -- transient capture (if used)
```

Each `zk-NNN-<slug>.md` is **one idea, one note**, ID-stable, and may
cross-link to other `zk-NNN` notes via inline references like
`[zk-009](zk-009-skill-consolidation-rubric.md)`.

## 2. Conventions

- **ID stability.** Once a `zk-NNN` is published, its ID never changes.
  Renames update the slug only.
- **Link reciprocity.** When zk-A references zk-B, the next regen of the
  index should surface the back-link from zk-B → zk-A.
- **Concept density.** Each note is short (~1 page), self-contained, and
  cites primary sources (papers, Mathlib lemmas, design docs) by anchor.
- **No-bibliography preference.** Inline citations only — the graph
  itself is the bibliography.

## 3. Currently published notes (sample)

- `zk-007-elo-for-agents.md`
- `zk-009-skill-consolidation-rubric.md`
- `zk-010-multi-model-pareto.md`

These reference `lab/design/03-multi-model-runner.md` and were the
canary for the R27 audit finding ("lab/design/ missing").

## 4. Graph rendering

`_index.md` describes a small-enough graph that no external tool is
required; section "while the graph is small" in the index documents this
choice.
