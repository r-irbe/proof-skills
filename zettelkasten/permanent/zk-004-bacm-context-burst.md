---
id: zk-004
title: BACM — Burst-And-Compact-Memory context pattern
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [context-engineering, pattern]
refs:
  - zk-005
  - zk-002
status: provisional
confidence: medium
---

# BACM — Burst-And-Compact-Memory context pattern

**Claim.** BACM is a two-phase context-discipline pattern. The agent
intentionally *bursts* context early (parallel reads, broad grep,
multi-file `view`) to maximise information gain, then immediately
*compacts* into a structured summary artefact before any reasoning
loop consumes the window. Without the compact step, the burst becomes
the failure mode "context burst" — too many irrelevant docs crowding
out the task.

**Evidence.** Anchored in filab `docs/conventions/context-management.md`
(token budgets Identity 5-10% / Task 30-40% / Knowledge 20-30% /
History 15-20% / Headroom 25-35%) and `GUARDRAILS.md:190-198` (context
burst as a named collapse mode), as summarised in
`lab/filab-survey/02-conventions.md` §2 and §3. In our internal runs
the compact step typically achieves a 4–8× reduction in working-set
tokens before the reasoning phase begins.

**Implication.** Two follow-ups. (1) Any skill that says "load the
following 8 skills before starting" is a guardrail violation — cap
at ≤3, per the survey. The template contract in [[zk-002]] should
encode this as a SHOULD-NOT. (2) BACM is the prescribed first phase of
the TDAD loop in [[zk-005]]: TestSmith bursts context across existing
fixtures, then compacts to a single eval-case skeleton before
PromptSmith starts iterating.

See also: [[zk-002]], [[zk-005]].
