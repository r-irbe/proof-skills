---
id: zk-002
title: Filab skill-template v2 frontmatter contract
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [template-contract, skills-architecture, dispatch]
refs:
  - zk-001
  - zk-009
  - zk-008
status: validated
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
127-129 (3 concrete failure modes). The fork-local audit
(`lab/skill-audit/audit.md` §0) confirms current corpus conformance is
**0/62** — every skill needs migration.

**Implication.** Any new or refactored skill in this fork must satisfy
the triad and the section order before merge; the consolidation rubric
[[zk-009]] uses the same fields (`applies-to`, scope) as its inputs.
The Lean-specific tactic policy in [[zk-008]] is the canonical example
of a `G-rule` block we still need to lift out of prose. Provenance of
this contract is recorded in the fork-rationale note [[zk-001]].

See also: [[zk-001]], [[zk-008]], [[zk-009]].
