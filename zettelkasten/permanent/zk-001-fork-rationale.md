---
id: zk-001
title: Why we forked leanprover/skills into r-irbe/proof-skills
created: 2026-05-27
updated: 2026-05-27
type: permanent
tags: [provenance, governance, fork]
refs:
  - zk-002
  - zk-009
status: validated
confidence: high
---

# Why we forked leanprover/skills into r-irbe/proof-skills

**Claim.** `r-irbe/proof-skills` exists as a downstream fork of
`leanprover/skills` so that skill-engineering experiments (template
migration, eval harness, multi-model runner, zettelkasten) can iterate
without being gated on the upstream release cadence, while the
lean-proof-review pipeline still tracks upstream verbatim.

**Evidence.** The README still points installation at
`https://github.com/leanprover/skills.git` (README.md:45-68) and the
upstream test infrastructure at `leanprover/skills-testing`
(README.md:80). The new surface area lives strictly under `lab/`
(eval framework, ELO prototype, filab-survey, skill-audit) and never
edits upstream skill bodies in-place; the audit confirms 62/62 skill
files still carry only the upstream `name + description` frontmatter
(`lab/skill-audit/audit.md` §0). The divergence is therefore
*additive* — no behavioural breakage on the upstream path.

**Implication.** Two rules follow. (1) Anything we change inside
`skills/<name>/SKILL.md` is a candidate upstream contribution and must
respect the filab template contract distilled in [[zk-002]]. (2) The
consolidation rubric in [[zk-009]] is *fork-local policy*: it may
merge/split skills more aggressively than upstream tolerates, so
merges must be staged behind a rebase plan before any PR back to
`leanprover/skills`.

See also: [[zk-002]], [[zk-009]].
