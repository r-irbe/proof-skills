---
name: lean-zettelkasten
description: Manage Zettelkasten knowledge notes for Lean 4 proof review. Use when creating, linking, synthesizing, or searching review knowledge. Covers note types (fleeting, literature, permanent), linking conventions, synthesis workflows, disconnected-note detection, and index maintenance.
---

# Lean 4 Zettelkasten Knowledge Management

Persistent knowledge system for accumulating, connecting, and synthesizing insights across Lean 4 proof reviews. All notes stored in `docs/project/lean/docs/zettelkasten/`.

## Directory Structure

```
docs/project/lean/docs/zettelkasten/
  _index.md              — Master index (auto-maintained)
  _tags.md               — Tag index
  fleeting/              — Session-scoped raw observations
  literature/            — Reference facts from external sources
  permanent/             — Synthesized, proven insights
    tactics/             — Tactic patterns and anti-patterns
    pitfalls/            — Recurring pitfall patterns
    conventions/         — Convention insights
    cross-module/        — Cross-module relationship insights
    proofs/              — Proof strategy patterns
```

## Note Types

| Type | Lifetime | Created by | Promoted to |
|---|---|---|---|
| **Fleeting** | Single review session | Any council member during RALPH Review | Literature or Permanent |
| **Literature** | Permanent | Any agent citing external source (lean-pitfalls, Mathlib docs, papers) | Permanent (after synthesis) |
| **Permanent** | Permanent | Synthesizer agent after pattern accumulation | — (terminal) |

## Note Format

Every note follows this template:

```markdown
# [ZK-YYYYMMDD-NNN]: [Title]
## Type: [fleeting / literature / permanent]
## Created: [ISO-8601]
## Updated: [ISO-8601]
## Author: [Σ / Φ / Ν / Λ / Ω / SYN / member-name]
## Source: [theorem / module / review session / external URL]

### Content
[The insight, pattern, or fact. Keep concise — one idea per note.]

### Evidence
[Lean diagnostic output, axiom trace, code snippet, or citation]

### Links
- Related: [[ZK-ID-1]], [[ZK-ID-2]]
- Contradicts: [[ZK-ID-3]]
- Supports: [[ZK-ID-4]]
- Supersedes: [[ZK-ID-5]]

### Tags
[lean, tactic, pitfall, pattern, convention, omega, simplex, ...]

### Status
[active / superseded / disputed / archived]
```

## ID Convention

`ZK-YYYYMMDD-NNN` where:
- `YYYYMMDD` = creation date
- `NNN` = sequential number within that date (001, 002, ...)

## Creating Notes

### Fleeting Notes (during review)

When a council member observes something during RALPH Review/Analyze:

1. Create `fleeting/ZK-YYYYMMDD-NNN.md` with the observation
2. Tag minimally (the key concept + `fleeting`)
3. Link to the theorem/module being reviewed
4. Do NOT spend time perfecting — capture the raw insight

### Literature Notes (from external sources)

When citing lean-pitfalls, Mathlib docs, or papers:

1. Create `literature/ZK-YYYYMMDD-NNN.md`
2. Include the exact citation with URL or section reference
3. Paraphrase the key insight in your own words
4. Link to any related fleeting or permanent notes
5. Tag with source category + concept

### Permanent Notes (synthesized insights)

When the Synthesizer agent detects a pattern across 3+ notes:

1. Create `permanent/<category>/ZK-YYYYMMDD-NNN.md`
2. Synthesize the pattern into a clear, actionable statement
3. Link back to all source notes (fleeting + literature)
4. Mark source fleeting notes as `superseded`
5. Assess if the insight warrants a skill update (lean-proof-review improvement)

## Synthesis Protocol

The Synthesizer agent (`SYN_*`) runs after each council session:

1. **Scan** all new fleeting notes from the session
2. **Cluster** by tag similarity and link proximity
3. **Check** if any cluster has 3+ notes → candidate for permanent note
4. **Draft** permanent note with synthesized insight
5. **Link** to all sources, establish bidirectional references
6. **Detect contradictions** — if two notes disagree, flag for SDR
7. **Update** `_index.md` and `_tags.md`
8. **Propose** skill updates if the insight affects review methodology

## Connection Discovery

Periodically (every project-level RALPH iteration):

1. **Orphan scan:** Notes with 0 outgoing links → attempt connection or archive
2. **Island scan:** Clusters of notes disconnected from the main graph → investigate
3. **Contradiction scan:** Notes with `contradicts` links → verify both are still valid
4. **Staleness scan:** Notes not updated in 5+ sessions → verify still relevant
5. **Coverage scan:** Map Zettelkasten coverage against Lean module structure → find gaps

## Searching Notes

### By tag
```bash
grep -rl "Tags:.*simplex" docs/project/lean/docs/zettelkasten/
```

### By link
```bash
grep -rl "ZK-20260327-005" docs/project/lean/docs/zettelkasten/
```

### By content
```bash
grep -rl "omega fails" docs/project/lean/docs/zettelkasten/
```

## Integration with Review Council

| Council event | Zettelkasten action |
|---|---|
| RALPH Review phase | Create fleeting notes for observations |
| RALPH Analyze phase | Link new notes to existing knowledge |
| RALPH Learn phase | Synthesizer promotes patterns to permanent notes |
| Council vote | Record decision rationale as fleeting note |
| SDR (disagreement) | Record all positions as linked literature/fleeting notes |
| Skill update | Create permanent note documenting what changed and why |
| AGENT.md update | Create permanent note documenting the change |

## Index Maintenance

### `_index.md` format:
```markdown
# Zettelkasten Index
## Last updated: [ISO-8601]
## Total notes: [N] (fleeting: [N], literature: [N], permanent: [N])

### Recent
- [[ZK-YYYYMMDD-NNN]]: [Title] ([type])

### By Module
- Project/Tactics: [[ZK-...]], [[ZK-...]]
- Project/LyapunovStability: [[ZK-...]]

### By Category
- Tactics: [[ZK-...]], [[ZK-...]]
- Pitfalls: [[ZK-...]]
```

### `_tags.md` format:
```markdown
# Tag Index
- `omega`: [[ZK-...]], [[ZK-...]]
- `simplex`: [[ZK-...]]
- `contraction`: [[ZK-...]]
```
