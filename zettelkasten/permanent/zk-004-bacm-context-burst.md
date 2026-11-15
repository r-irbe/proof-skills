---
id: zk-004
title: BACM -- Burst-And-Compact-Memory context pattern
created: 2026-05-27
updated: 2026-11-15
type: permanent
tags: [context-engineering, pattern]
refs:
  - zk-005
  - zk-002
status: validated
confidence: high
---

# BACM -- Burst-And-Compact-Memory context pattern

**Claim.** BACM is a two-phase context-discipline pattern. The agent intentionally *bursts* context early (targeted searches, L1 lookup cards, `lean_lookup_symbol`) to maximize information gain, then immediately *compacts* into a structured summary before reasoning loops consume the context window. Without compaction, context burst crowds out active proof obligations.

**Evidence.** Anchored in `GUARDRAILS.md` and the L0/L1/L2 progressive disclosure architecture (`SKILL.md` <= 4 KB, `vendor/itp-ontology/handbook-tables.v1.json` L1 cards, `references/*-handbook.md` L2 handbooks). Compaction routinely achieves a 4-8x reduction in working-set tokens before proof synthesis begins.

**Implication.** Two follow-ups. (1) Skills must never instruct an agent to pre-load 8+ handbooks upfront; cap co-loaded skills at <= 3, encoded in the template contract [[zk-002]]. (2) BACM forms the opening phase of the TDAD loop in [[zk-005]]: TestSmith bursts context across existing fixtures, then compacts to a minimal eval-case skeleton before PromptSmith iterates.

See also: [[zk-002]], [[zk-005]].
