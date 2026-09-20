# AGENT.md — proof-skills repo contract

Authoritative entry-point for any AI agent doing work inside this repo.
Read this *before* you touch any file. The rules below are repo-wide and
override session-only preferences.


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
| 1 | **Confidence** | Your belief < 0.90 on routing, design, taxonomy, naming, scope. | Soft — `ask_user`. |
| 2 | **Irreversible** | You are about to do anything in the reversibility table below at class ≥ `irreversible_*`. | **Hard — always ask**, regardless of confidence. |
| 3 | **Conflict** | Two readings of the same source give materially different answers (spec vs. ADR, template vs. SKILL.md, two skills mutually contradicting). | Soft — `ask_user`, cite both. |
| 4 | **Novelty** | The user's request mentions a pattern, tool, ADR slot, or skill name that is not present in the repo and not in the runtime knowledge cutoff. | Soft — `ask_user` for intent. |
| 5 | **Governance** | The change touches `AGENT.md`, top-level layout, license, the public README, or this contract. | **Hard — always ask**. |

### 1.2.1 Trigger registry for skill authors

When writing or editing a `SKILL.md`, encode the same five categories in the
skill's `## Recovery & STOP` section. This keeps local skill behavior aligned
with the repo-wide contract and avoids hidden "continue anyway" paths.

- **Confidence**: STOP if below repo belief floor; ask. (e.g. naming, strategy, owner).
- **Irreversible**: STOP before irreversible data, trust, economic actions. (e.g. push, paid call).
- **Conflict**: STOP when authoritative sources disagree; ask.
- **Novelty**: STOP when tool/pattern is absent from repo.
- **Governance**: STOP before changing contracts, layout, rules.

Prefer a short explicit STOP rule over a vague reminder. A skill should tell the
agent what decision is risky, why the human must choose, and what work is
blocked until the answer is available.

### 1.3 Reversibility table

Order matters: if a single command crosses two classes, treat as the
*higher* class.

- `reversible`: Read-only, temp-file, local build, `lake exe`, `git status`, `view`, `grep`. -> **No gate**.
- `mostly_reversible`: New file in draft, branch creation, local commit on personal branch, `lake update` on lockfile. -> **No gate**, but log action.
- `irreversible_data`: `rm -rf`, `git push --force`, history rewrite. -> **Hard HITL gate**.
- `irreversible_trust`: PR merge, branch push to default, tag, docs change, edit AGENT.md. -> **Hard HITL gate**.
- `irreversible_economic`: Paid API call >= $1, billing action. -> **Hard HITL gate**.

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

> **Note on wall-clock time.**  The session time budget is **unlimited**
> by default — slow local builds, long lake-timer probes, repeated test
> reruns, and large eval loops are all fine.  Time-irreversibility is
> *not* on the reversibility table in §1.3 and is **not** a HITL trigger
> on its own.  Use *content* irreversibility (history rewrites, push to
> default, paid API calls, AGENT.md edits) to decide whether to stop —
> never wall-clock cost.  If the human operator explicitly imposes a
> wall-clock cap for a specific request, treat it as a §1.2#4 (Novelty)
> constraint and confirm before exceeding it; otherwise, slowness alone
> is never a reason to defer or skip work.

### 1.5 What "ask" looks like

- **Copilot CLI**: `ask_user` with a JSON-schema form.
- **MCP-aware host**: `elicitation/create` with the same shape.
- **Plain chat**: A numbered question list.

The form **must** include: (a) the decision under contention, (b) 2–4
named options, (c) which option is recommended and why, (d) what blocks
on the answer.

### 1.5.1 Sub-agent fleet patterns
- `claude-haiku-4.5` -> inline prompts, use `write_agent` for `/tmp` write restrictions
- `read_agent since_turn=N` -> exclusive
- `mac bash` -> no associative arrays; use Python
- ensembles (N>=3) -> prefer `statistics.median` over `min(low_band)`
- per_judge_json -> save local, move to `_archive`
- dispatch -> <32 concurrent, batch waves
- eval -> pure replay > rerun

### 1.6 Logging

Every HITL gate fire (whether asked or auto-resolved under §1.4) must
appear in the agent's response so the user can audit. If the runtime
provides a structured trace (`events.jsonl`, OTel `gen_ai.hitl.*`
spans), use it; otherwise inline prose is sufficient.

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

## 4. Workflow defaults

- Branch naming: `work/<topic>-<YYYYMMDD>`.
- Commit messages: prefix with `feat:` / `fix:` / `docs:` / `chore:`;
  no internal slot IDs in subjects.
- All structural changes (skill consolidation, template rewrites,
  layout moves) follow the current public design reports and release notes.
- Skill conformance is hard-gated by
  `scripts/skill-audit/check_conformance.py`; APM packaging is
  hard-gated by `scripts/lint/apm_validate.py`.

