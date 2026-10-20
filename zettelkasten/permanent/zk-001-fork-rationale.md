---
id: zk-001
title: Fork rationale and project-agnostic override architecture
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [provenance, governance, fork]
refs:
  - zk-002
  - zk-008
  - zk-009
status: validated
confidence: high
---

# Fork rationale and project-agnostic override architecture

**Claim.** A reusable proof-skills library must separate universal Lean 4 / Mathlib4 workflows from downstream project conventions via a thin override layer (`<Project>` placeholders + delta overrides) rather than duplicating or hardcoding project paths inside the shared skill corpus.

**Evidence.** Captured during the initial extraction of `proof-skills` from upstream `leanprover/skills` and formalization campaigns. Skills in `skills/` and templates in `templates/` enforce the template-v2 frontmatter contract in [[zk-002]] and the tactic priority hierarchy in [[zk-008]], while the consolidation rubric in [[zk-009]] governs when specialized skills merge or split.

**Implication.** Downstream repositories consume `proof-skills` as a read-only package or submodule and place local domain deltas in an override directory that links back to the canonical skill.

See also: [[zk-002]], [[zk-008]], [[zk-009]].
