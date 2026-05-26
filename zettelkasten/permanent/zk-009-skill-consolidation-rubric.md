---
id: zk-009
title: Skill consolidation rubric — merge, split, keep
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [skills-architecture, governance, decision]
refs:
  - zk-002
  - zk-003
  - zk-008
status: validated
confidence: high
---

# Skill consolidation rubric — merge, split, keep

**Claim.** The skill-audit decides merge / split / keep against four
quantitative signals: (1) **scope overlap** — Jaccard on `applies-to`
globs > 0.6 ⇒ merge candidate; (2) **co-invocation rate** — skills
appearing together in > 70% of each other's sessions ⇒ merge;
(3) **size** — SKILL.md > 500 lines ⇒ split; (4) **failure-mode
orthogonality** — two skills addressing the same AgentRx category
from [[zk-003]] ⇒ merge unless they target different lifecycle
phases.

**Evidence.** The fork-local audit at `lab/skill-audit/audit.md` §0
grades the corpus **F** for v2 conformance (62/62 files non-compliant)
and flags every SKILL.md over the 500-line threshold for split. The
size cap traces to `specs/templates/skill-template-v2.md` (cited via
`lab/filab-survey/02-conventions.md` §2.2). Co-invocation data is
sourced from the multi-model runner traces described in
`lab/design/03-multi-model-runner.md`.

**Implication.** The rubric runs as a decision gate, not a one-off.
Every merge produces a `MERGE` row in the changelog and a redirect
stub at the old path. Bounds and inputs come from the template
contract in [[zk-002]] (the size cap, the `applies-to` field). The
deprecated Project tactic macros listed in [[zk-008]] (rows 8–14, zero
cross-module uses) are the cleanest live test case for the rubric:
they fail all four signals and should be deleted, not refactored.

See also: [[zk-002]], [[zk-003]], [[zk-008]].
