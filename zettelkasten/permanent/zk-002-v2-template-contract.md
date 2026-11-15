---
id: zk-002
title: Skill-template v2 frontmatter contract
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [template-contract, skills-architecture, dispatch]
refs:
  - zk-001
  - zk-009
  - zk-008
status: validated
confidence: high
---

# Skill-template v2 frontmatter contract

**Claim.** Under `specs/templates/skill-template-v2.md`, a conforming `SKILL.md` must carry a dispatch triad plus a small, ordered body so that a router can decide *whether* to load the skill before reading any prose. The triad is `USE FOR:` (3-5 verb-object paraphrases), `DO NOT USE FOR:` (must name an alternative `@skill` for handoff), and `TRIGGERS:` (2-4 bare nouns or phrases).

**Evidence.** Codified in `specs/templates/skill-template-v2.md` and enforced deterministically by `scripts/skill-audit/check_conformance.py`: dispatch triad presence, G-rule `MUST`/`SHOULD`/`MUST NOT` prefixes, capped rule count, `Discover -> Plan -> Execute -> Verify -> Persist` workflow order, explicit `STOP` gates, and concrete failure modes.

**Implication.** Any new or refactored skill in `proof-skills` must satisfy the triad and section order before merge; the consolidation rubric [[zk-009]] uses the same fields (`applies-to`, scope) as its inputs. The Lean-specific tactic policy in [[zk-008]] remains the canonical example of a `G-rule` block. Provenance of this contract is recorded in [[zk-001]].

See also: [[zk-001]], [[zk-008]], [[zk-009]].
