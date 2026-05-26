---
id: zk-005
title: TDAD — Test-Driven Agent Definition (4-role loop)
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [methodology, evals, agent-fleet]
refs:
  - zk-004
  - zk-006
  - zk-003
status: validated
confidence: high
---

# TDAD — Test-Driven Agent Definition (4-role loop)

**Claim.** Test-Driven Agent Definition (TDAD, ADR-0039) treats a
SKILL.md as a *compiled artefact*, not hand-edited prose. Four roles
co-operate in a TDD-style red/green loop: **TestSmith** generates eval
fixtures from each skill's G-rules; **PromptSmith** iterates SKILL.md
until fixtures go green; **MutationSmith** weakens rules (drop a
G-rule, soften a `MUST` to `SHOULD`) to verify fixture strength; the
**Built Agent** is the runtime consumer scored against the fixtures.

**Evidence.** Distilled from `lab/filab-survey/01-adrs.md` §5.3. The
ADR sets explicit per-skill targets: **HPR ≥ 97%** (human pass rate),
**MS 86–100%** (mutation score), **SURS 97%** (skill-under-rule
score). These are the bars each Lean-skill family eval should aim at
when porting to the harness under `lab/evals/`.

**Implication.** TDAD resolves the chicken-and-egg of "how do you
eval an agent before you have one" by requiring fixtures **before**
the skill body is written. The first TestSmith phase uses the BACM
pattern from [[zk-004]] to gather corpus signal cheaply. The eval
oracle is one of the four targets named in [[zk-006]], and the failure
labels used by MutationSmith are the nine AgentRx categories in
[[zk-003]]. Without MutationSmith specifically, fixture strength is
unfalsifiable — a green eval may just mean weak tests.

See also: [[zk-003]], [[zk-004]], [[zk-006]].
