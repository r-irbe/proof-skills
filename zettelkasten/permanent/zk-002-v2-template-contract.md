---
id: zk-002
title: Filab skill-template v2 frontmatter contract
created: 2026-05-27
updated: 2026-05-29
type: permanent
tags: [template-contract, skills-architecture, dispatch]
refs:
  - zk-001
  - zk-009
  - zk-008
status: superseded-by-current-corpus
confidence: high
---

# Filab skill-template v2 frontmatter contract

**Claim.** Under filab `specs/templates/skill-template-v2.md`, a
conforming SKILL.md must carry a dispatch triad plus a small, ordered
body so that a router can decide *whether* to load the skill before
reading any prose. The triad is `USE FOR:` (3–5 verb-object
paraphrases), `DO NOT USE FOR:` (must name an alternative `@skill` for
handoff), and `TRIGGERS:` (2–4 bare nouns, not phrases).

**Evidence.** Pulled from `lab/filab-survey/02-conventions.md` §2.1–2.3,
which cites template-v2 lines 64-65 (triad), 88 (USE FOR cardinality),
89 (handoff requirement), 90 (TRIGGERS grammar), 94-96 (G-rule
MUST/SHOULD/MUST NOT prefix), 98 (≤14 G-rules gated / ≤6 advisory),
103-110 (Discover→Plan→Execute→Verify→Persist), 112-118 (explicit STOP),
127-129 (3 concrete failure modes). This was a migration note: the live
corpus is now fully v2-conformant, and the current checker is
`scripts/skill-audit/check_conformance.py`.

**Implication.** Any new or refactored skill in this fork must satisfy
the triad and section order before merge; the consolidation rubric
[[zk-009]] uses the same fields (`applies-to`, scope) as its inputs.
The Lean-specific tactic policy in [[zk-008]] remains the canonical
example of a `G-rule` block. Provenance of this contract is recorded in
the fork-rationale note [[zk-001]].

See also: [[zk-001]], [[zk-008]], [[zk-009]].
