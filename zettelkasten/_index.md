---
id: zk-index
title: Proof-skills zettelkasten — seed index
created: 2026-05-27
updated: 2026-05-29
type: literature
tags: [moc, index, seed]
refs:
  - zk-002
  - zk-003
  - zk-004
  - zk-005
  - zk-006
  - zk-007
  - zk-008
  - zk-009
  - zk-010
status: provisional
confidence: high
---

# Proof-skills zettelkasten — seed index

This is the entry-point Map-of-Content for the first ten seed notes.
The notes capture early findings from the proof-skills work
(survey material, skill-audit, eval framework, multi-model runner, and
the ranking prototype that later became the Glicko-2 live corpus) and
follow a simplified Luhmann 3-tier model:
**fleeting** → **literature** → **permanent**. All ten seeds are
`permanent` (with two at `confidence: medium` while we collect more
runs).

The seed IDs are short (`zk-001` … `zk-010`) for legibility while the
graph is small. When the design in `lab/design/05-zettelkasten.md`
lands, these will be re-IDed to the timestamp scheme
`ZK-YYYYMMDDHHMM` and the `refs:` fields rewritten in lock-step —
filenames-as-IDs make this a mechanical migration.

## Seed catalogue

| ID | Title | Tier-1 tag | Confidence |
|---|---|---|---|
| [[zk-002]] | Filab skill-template v2 frontmatter contract | template-contract | high |
| [[zk-003]] | AgentRx 9-category failure taxonomy | concept | high |
| [[zk-004]] | BACM — Burst-And-Compact-Memory context pattern | pattern | medium |
| [[zk-005]] | TDAD — Test-Driven Agent Definition (4-role loop) | methodology | high |
| [[zk-006]] | Four eval targets per ADR-0039 | concept | high |
| [[zk-007]] | ELO for non-deterministic agents | pattern | medium |
| [[zk-008]] | Lean 4 tactic priority hierarchy | pattern | high |
| [[zk-009]] | Skill consolidation rubric — merge, split, keep | decision | high |
| [[zk-010]] | Multi-model cost–quality Pareto | synthesis | medium |

## Link graph (ASCII)

Edges below are outgoing `refs:` from each note. Arrows read
"depends on / cites".

```

   ┌──────────────────────────┐            ┌──────────────────────────┐
   │       zk-002             │◀───┘──────▶│        zk-009            │
   │  template-v2 contract    │◀───────────│  consolidation rubric    │
   └─────────┬────────────────┘            └──┬────────────────┬──────┘
             │                                │                │
             ▼                                ▼                ▼
   ┌──────────────────────────┐    ┌──────────────────────────┐
   │       zk-008             │    │        zk-003            │◀─────┐
   │  Lean tactic hierarchy   │    │  AgentRx 9-category tax. │      │
   └──────────────────────────┘    └──┬────────────────┬──────┘      │
                                      │                │             │
                                      ▼                ▼             │
                          ┌─────────────────────────┐  │             │
                          │       zk-006            │◀─┘             │
                          │  4 eval targets         │                │
                          └──┬──────────────────┬───┘                │
                             │                  │                    │
                             ▼                  ▼                    │
              ┌──────────────────────┐  ┌──────────────────────┐     │
              │      zk-005          │  │      zk-007          │─────┘
              │  TDAD 4-role loop    │  │  ELO for agents      │
              └──────────┬───────────┘  └──────────┬───────────┘
                         │                         │
                         ▼                         ▼
              ┌──────────────────────┐  ┌──────────────────────┐
              │      zk-004          │  │      zk-010          │
              │  BACM context burst  │  │  multi-model Pareto  │
              └──────────────────────┘  └──────────────────────┘
```

## Reading paths

- **Newcomer to the fork** — start at [[zk-002]] → [[zk-009]].
- **Building eval cases** — [[zk-006]] → [[zk-005]] → [[zk-003]] →
  [[zk-007]].
- **Lean-proof-review migration** — [[zk-008]] → [[zk-002]] →
  [[zk-009]].
- **Cost-aware model selection** — [[zk-010]] → [[zk-007]] →
  [[zk-006]].

## Invariants the index promises

1. Every seed note has a YAML frontmatter block with the schema
   declared in this index.
2. Every seed note has ≥ 2 outgoing `refs:` to other seed notes.
3. Every seed note is ≤ 300 words.
4. Every outgoing `refs:` entry is matched by an inline `[[zk-NNN]]`
   wikilink in the body, and vice versa.
5. Historical source paths may appear in seed-note evidence, but current
   active tooling paths must be cited in any new or refreshed note.
