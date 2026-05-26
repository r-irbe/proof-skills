# AGENT.md — proof-skills repo contract

Authoritative entry-point for any AI agent doing work inside this repo.
Read this *before* you touch any file. The rules below are repo-wide and
override session-only preferences.

> **Audience.** This file is for agents (Claude, Copilot, Gemini, Codex
> CLI sessions). Humans should read [`README.md`](README.md) for install
> and quickstart.

---

# AGENT.md — proof-skills repo contract

Authoritative entry-point for any AI agent doing work inside this repo.
Read this *before* you touch any file. The rules below are repo-wide and
override session-only preferences.

> **Audience.** This file is for agents (Claude, Copilot, Gemini, Codex
> CLI sessions). Humans should read [`README.md`](README.md) for install
> and quickstart.

---

## 0. What this repo is

A toolkit of [Agent Skills](https://agentskills.io) for working with
[Lean 4](https://github.com/leanprover/lean4) and
[Mathlib4](https://github.com/leanprover-community/mathlib4). This is a
**standalone** repository — not a fork — and references upstream
`leanprover/skills` as a vendor git submodule for transparent
re-dispatch (see §3).

Top-level surfaces:

| Path | Purpose | Lifecycle |
|---|---|---|
| `skills/` | One folder per skill; each has a `SKILL.md` agent-loadable contract. | Migrating to v2 template (see `scripts/lint/check_skill.py`). |
| `skills/_overrides/` | Local overrides for upstream skill slugs (audit-modified copies of `leanprover/skills` entries). | Stable; dispatched per §3. |
| `templates/` | Copy-pasteable Lean module / proof / refactor templates. | Stable; v2 in progress. |
| `references/` | Background knowledge an agent can `view` when a skill `## See also`s it. | Append-only. |
| `scripts/lean/` | Generic Lean-4 helper scripts (axiom audit, DAG checks, bridge validators, etc.) callable from any project. | Project-agnostic; no host-project paths. |
| `vendor/leanprover-skills/` | Upstream `leanprover/skills` referenced as a git submodule (read-only; do not edit in place). | Pinned commit; bump deliberately. |
| `zettelkasten/` | Reserved for the canonical Luhmann-tier ZK. Currently empty pending W7 of the master plan. | Bootstrapping. |

This repo is **standalone** and has **no runtime dependency** on any
host formalization project. Examples and references may be inspired by
real Lean projects, but no project-specific names appear in the public
content.

---

## 1. HITL gating (MANDATORY)

**Rule.** Before any non-trivial decision, estimate your **belief** that
the decision is correct. If `belief < 0.90`, **stop and ask the user**
via the runtime's elicitation channel (`ask_user` for Copilot CLI, MCP
`elicitation/create` for MCP-aware hosts, the chat surface otherwise).
Do **not** silently choose.

### 1.1 Why this number (and not 0.80)

Empirical HITL studies of structured belief-gated agents (3 250+ traced
gates over 12 weeks, plus published agent-SDK common practice) show
structured channels drop silent-continuation rate from ~15 % to <1 %.
The 0.80 floor is the published common-practice number (see the
"escalate if confidence < 80 %" pattern in mainstream agent-SDK
literature and the *architectural decision confidence gate* family of
ADRs). The **0.90** floor in this repo is intentionally stricter
because:

1. The artifacts here (templates, skills, references) are read by *many*
   downstream agents — a single wrong design choice fans out.
2. Lean formalisation is unforgiving: an incorrect tactic recommendation
   in a `SKILL.md` propagates into failed proofs across the ecosystem.
3. The cost of asking is one round-trip; the cost of being wrong is a
   churn cycle and lost trust.

### 1.2 The 5 trigger categories

Adapted from the AgentRx-2025 minimal cover (`{Confidence, Irreversible,
Conflict, Novelty, Governance}`); 5 categories empirically dominate
8-category alternatives at <1 % structured-error rate.

| # | Category | Fires when… | Gate type |
|---|---|---|---|
| 1 | **Confidence** | Your belief < 0.90 on routing, design, taxonomy, naming, scope. | Soft — `ask_user`. |
| 2 | **Irreversible** | You are about to do anything in the reversibility table below at class ≥ `irreversible_*`. | **Hard — always ask**, regardless of confidence. |
| 3 | **Conflict** | Two readings of the same source give materially different answers (spec vs. ADR, template vs. SKILL.md, two skills mutually contradicting). | Soft — `ask_user`, cite both. |
| 4 | **Novelty** | The user's request mentions a pattern, tool, ADR slot, or skill name that is not present in the repo and not in the runtime knowledge cutoff. | Soft — `ask_user` for intent. |
| 5 | **Governance** | The change touches `AGENT.md`, top-level layout, license, the public README, or this contract. | **Hard — always ask**. |

### 1.3 Reversibility table

Order matters: if a single command crosses two classes, treat as the
*higher* class.

| Class | Examples | HITL gate |
|---|---|---|
| `reversible` | Read-only inspection, temp-file write, local build, `lake exe`, `git status`, `view`, `grep`. | None — auto. |
| `mostly_reversible` | New file under a draft path, branch creation, local commit on a personal branch, `git add`, `lake update` on lockfile-bearing project. | None — auto, but log the action in the response. |
| `irreversible_data` | `rm -rf`, `git push --force`, `git filter-repo`, `git reset --hard`, `git rebase` on shared branch, history rewrite. | **Hard HITL gate**. |
| `irreversible_trust` | PR merge, branch push to default, release tag, public docs change, edit to this `AGENT.md`. | **Hard HITL gate**. |
| `irreversible_economic` | Paid API call, model invocation expected to cost ≥ $1, third-party webhook, billing-bearing action. | **Hard HITL gate**. |

### 1.4 When the user is unavailable (autopilot fallback)

If the runtime tells you the user is unavailable (Copilot CLI returns
*"The user is not available to respond and will review your work
later"*), apply this decision rule **in this exact order**:

1. **Trigger 2 or 5 fired (hard gate)** → do **not** execute the action.
   Stop, write the proposed action + rationale + alternatives to the
   response, and end the turn (`task_complete` with explanation).
2. **Trigger 1 / 3 / 4 fired (soft gate)** → pick the most defensible
   option per the rule of *least irreversibility, smallest scope, most
   literal reading of the user's last request*, **document the choice
   in the commit message and in the response**, and proceed.
3. **No trigger fired** → proceed normally.

This is the *fail-closed* discipline (cf. OWASP LINDDUN-GO `T-NC`
silent-grant pattern): never auto-approve an irreversible op on a
timeout.

### 1.5 What "ask" looks like

| Runtime | Channel |
|---|---|
| Copilot CLI | `ask_user` with a JSON-schema form (single field for simple yes/no; multi-field with `default` set when there is a recommended answer). |
| MCP-aware host (Claude Code, Cursor, etc.) | `elicitation/create` with the same shape. |
| Plain chat | A numbered question list ending with *"Pick A/B/C, or describe alternative"*. |

The form **must** include: (a) the decision under contention, (b) 2–4
named options, (c) which option is recommended and why, (d) what blocks
on the answer.

### 1.6 Logging

Every HITL gate fire (whether asked or auto-resolved under §1.4) must
appear in the agent's response so the user can audit. If the runtime
provides a structured trace (`events.jsonl`, OTel `gen_ai.hitl.*`
spans), use it; otherwise inline prose is sufficient.

---

## 2. Confidentiality (MANDATORY)

This repo is **public** and intentionally project-agnostic. Do **not**
introduce, restore, or paraphrase any reference to specific private
host-project names, internal modules, internal ADR identifiers,
internal directory structures, or internal personnel. Example
identifiers in body text should be obviously synthetic (`MyProject`,
`Foo`, `ExampleGroup`, etc.) — never a real downstream project name.

If you discover a slip-through (a private name in body text, a
real project's path in a sample command, etc.), treat the rewrite as
a `governance` HITL trigger (§1.2 #5) and ask before pushing.

---

## 3. Layout invariants

### 3.1 Skill dispatch precedence

When an agent asks for a skill by slug `<X>`, resolve in this order
(first hit wins):

1. **`skills/<X>/`** — first-party skills authored in this repo.
2. **`skills/_overrides/<X>/`** — local overrides of upstream slugs
   (e.g., audit-modified copies of upstream `lean-bisect`,
   `mathlib-pr`, etc.). Use these when behaviour must diverge from
   upstream but the slug must remain stable.
3. **`vendor/leanprover-skills/skills/<X>/`** — upstream `leanprover/skills`
   read-only fallback.

This rule applies to runtime dispatchers (the plugin loader, eval
harness, ELO runner) and to humans reading the repo. Do not edit
under `vendor/`; update the submodule pin instead.

### 3.2 Other invariants

- `scripts/lean/` is for **generic** Lean-4 tooling. Project-coupling
  is not allowed. Project-specific globs (e.g. `MyProject/*.lean`)
  must be parameterised via CLI flags or environment variables.
- `templates/` and `references/` may show **example** identifiers, but
  example identifiers must be obviously synthetic (e.g.
  `ExampleProject`, `MyGroup`, `foo`, `bar`) — not a real project name.
- One folder per skill in `skills/<slug>/`; mandatory file is
  `SKILL.md`. Optional files live alongside but must be referenced
  from `SKILL.md`'s `## See also` footer.
- `zettelkasten/` is reserved. Do not populate ad-hoc — the W7 rollout
  has a specific Luhmann-tier layout.

---

## 4. Workflow defaults

- Branch naming: `work/<topic>-<YYYYMMDD>`.
- Commit messages: prefix with `feat:` / `fix:` / `docs:` / `chore:`;
  no internal slot IDs in subjects.
- All structural changes (skill consolidation, template rewrites,
  layout moves) follow the **master plan** under
  `lab/MASTER-PLAN.md` *if accessible*; the lab lives outside this
  repo. If you are working without the lab, defer the change and ask.
- Linter (`scripts/lint/check_skill.py` once promoted) is **advisory**
  in CI; do not silently regress the pass-rate of v2-compliant
  skills.

---

## 5. Quick links

- Public README: [`README.md`](README.md)
- License: [`LICENSE`](LICENSE) — Apache-2.0
- Upstream attribution: [`NOTICE`](NOTICE)
- Skill dispatch precedence: §3.1 above
- Generic Lean scripts: [`scripts/lean/`](scripts/lean/)
- Tooling scripts (eval / linter / ELO — populated by W1):
  [`scripts/`](scripts/)
- Upstream submodule: [`vendor/leanprover-skills/`](vendor/leanprover-skills)
- Master plan (private superrepo only): `lab/MASTER-PLAN.md`

---

## Provenance

This contract is informed by published agent-HITL practice
(constitutional AI, FrugalGPT cascades, OWASP LINDDUN-GO `T-NC`,
A2A v1.0 `TaskState`, AgentRx-2025 5-category cover) and empirical
HITL research summarised in the public *belief-gated escalation*
literature. The patterns themselves are public research and are
paraphrased above so this repo stands alone, with no dependency on any
external ADR vocabulary.
