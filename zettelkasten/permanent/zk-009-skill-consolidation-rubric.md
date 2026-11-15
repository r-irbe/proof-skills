---
id: zk-009
title: Skill consolidation rubric -- merge, split, keep
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [skills-architecture, governance, decision]
refs:
  - zk-002
  - zk-003
  - zk-008
status: validated
confidence: high
---

# Skill consolidation rubric -- merge, split, keep

**Claim.** Corpus governance decides merge / split / keep against four quantitative signals: (1) **scope overlap** (`applies-to` Jaccard > 0.6 -> merge candidate); (2) **co-invocation rate** (> 70% shared sessions -> merge); (3) **L0 byte budget** (`SKILL.md` > 4,000 B -> compact into L2 handbook + L1 card); and (4) **failure-mode orthogonality** (two skills targeting the same AgentRx category from [[zk-003]] merge unless separated by lifecycle phase).

**Evidence.** Enforced via `scripts/skill-audit/check_conformance.py`, `scripts/compile_handbook_tables.py`, and `agents/facets/registry.json` `skill_aliases`, consolidating the toolkit from 75 sprawling skills down to **38 core Lean/ITP skills** + **7 opt-in pack skills** with zero capability loss.

**Implication.** Every consolidation records a `skill_aliases` entry in `agents/facets/registry.json` so legacy slugs resolve deterministically. Bounds follow the template-v2 contract in [[zk-002]], and redundant single-use tactic wrappers flagged by [[zk-008]] are deleted rather than re-documented.

See also: [[zk-002]], [[zk-003]], [[zk-008]].
