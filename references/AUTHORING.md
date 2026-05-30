# Authoring a new skill

This guide is for contributors adding a new skill (or refactoring an
existing one) to match the v2 dispatch contract + layering pattern that
the corpus settled on across waves 13–17.

If you're just *consuming* skills, you don't need this. Read
`AGENT.md` and the relevant `skills/<name>/SKILL.md` files instead.

---

## TL;DR — Decision tree

```
Is this skill < ~150 LOC of actual guidance?
├── YES → Single SKILL.md (v2 dispatch contract inline).
│
└── NO  → Layered: thin SKILL.md (dispatch contract only) +
          references/<name>-handbook.md (the deep content).
```

Either way, your SKILL.md MUST satisfy the v2 contract (next section)
or `scripts/skill-audit/check_conformance.py` will fail the build.

---

## The v2 dispatch contract

Every non-REDIRECT SKILL.md MUST have the following:

### YAML frontmatter

```yaml
---
name: example-skill
description: |
  ...one-line elevator pitch...

  USE FOR: <comma-separated trigger list>; <secondary list>.

  DO NOT USE FOR: <comma-separated anti-trigger list>.

  TRIGGERS: <keyword/regex list that should route here>.
tier: hot | warm | cold
runtime_targets:
  - skill:<predecessor-skill>
  - skill:<peer-skill>
dispatch_targets:
  - skill:<successor-skill>
handoffs:
  predecessors:
    - skill:<upstream-skill>  # what routes INTO me
  successors:
    - skill:<downstream-skill>  # what I route TO
metadata:
  cluster: <cluster-name>
  pass: <wave-id>
  layered: true | false
---
```

The audit script checks for: `tier:`, `handoffs:`, and the
USE FOR/DO NOT USE FOR/TRIGGERS markers in the description. Skills
without these are flagged as non-v2 and fail CI.

### Body sections

```markdown
# <Skill Name>

## Routing
...when this skill is selected, what's the dispatch decision...

## Workflow
1. Step 1 — domain-specific (NOT a canonical 4-step template;
   tailor to what this skill actually does)
2. Step 2
3. Step 3
4. Step 4 — STOP signal: what concrete output indicates done

## Recovery
- STOP 1: <when to abort and dispatch elsewhere>
- STOP 2: <when to escalate or HITL>
- STOP 3: <when to call a recovery sibling>

## Handoffs
- **Receives from:** `skill:<upstream>` (what context they pass)
- **Sends to:** `skill:<downstream>` (what context I pass)
- **Sibling:** `skill:<peer>` (escalation / collaboration)
```

The Workflow/Recovery/Handoffs sections are required at the heading
level. Body content under each is your design judgment.

---

## When to layer (the rule of thumb)

| Skill LOC | Recommendation |
|---:|---|
| ≤ 150 | Keep inline — no handbook needed. |
| 150 – 240 | Inline if every section is dispatch-critical; layer if some sections are "load on demand" deep-dive. |
| ≥ 240 | Layer — split into thin dispatch SKILL + `references/<name>-handbook.md`. |

The 240 threshold reflects pass-16's empirical breakpoint: above it,
dispatch context cost dominates; below it, the cognitive cost of
two-file lookup exceeds the context savings.

---

## How to layer (the mechanical recipe)

Given a heavy `skills/<name>/SKILL.md` you want to layer:

1. **Keep in `SKILL.md`** (the "operational core"):
   - YAML frontmatter (unchanged, but set `metadata.layered: true`).
   - `## Routing` / `## Workflow` / `## Recovery` / `## Handoffs`.
   - Any top-level architecture diagram or dispatch matrix that the
     agent uses on EVERY invocation.
   - A "Parts index" pointing into the handbook.

2. **Move to `references/<name>-handbook.md`** (the "encyclopaedia"):
   - All multi-page methodology sections.
   - All template / example bodies.
   - All theoretical background.
   - All cross-skill protocol details.

3. **Handbook YAML preamble** (required for audit):
   ```yaml
   ---
   status: reference
   extracted_from: <name>
   extracted_on: YYYY-MM-DD
   scope: |
     ...one-paragraph description of what this handbook covers...
   loader_hint: |
     This file is loaded on-demand from skills/<name>/SKILL.md.
     Do not load by default; route through the SKILL.md first.
   ---
   ```

   The `extracted_from:` field MUST match the source skill name —
   the audit verifies the back-reference both ways.

4. **Add a "See handbook" link** in the SKILL.md body, e.g.:
   ```markdown
   For the full methodology, see
   [`references/<name>-handbook.md`](../../references/<name>-handbook.md).
   ```

5. **Run the audit:**
   ```bash
   cd skills/
   python3 scripts/skill-audit/check_conformance.py
   ```
   Confirms (a) handbook exists, (b) handbook back-references the
   source SKILL, (c) v2 contract still satisfied, (d) no broken
   handoff refs, (e) inline `@skill` refs point at active skills, and
   (f) relative Markdown links resolve.

6. **Verify content preservation:**
   ```bash
   # Confirm every Part / Identity / Appendix header from the
   # pre-layered SKILL still appears in the SKILL + handbook union:
   diff <(grep -E '^#+\s' skills/<name>/SKILL.md.old) \
        <(cat skills/<name>/SKILL.md \
              references/<name>-handbook.md | grep -E '^#+\s')
   ```

---

## Handoffs — designing the routing graph

The audit detects 4 graph health properties:

1. **Broken refs** — `handoffs.successors: skill:foo` where no
   `skills/foo/` or `skills/_overrides/foo/` exists. **Hard fail.**
2. **Mutual peer pairs** — X has Y in successors, Y has X in
   successors. Reported but allowed (collaboration pattern).
3. **Cycles** — A→B→C→A chains of length ≥ 3. Reported but allowed
   when they are editorial feedback loops with explicit STOP
   contracts at every node.
4. **Orphans / dead-ends** — skills with no predecessors or no
   successors. Reported but allowed for entry-points (`lean-setup`)
   and terminal operational tools (`lean-bisect`, `lean-mwe`).

When you add handoffs:
- **Use the namespace** `skill:<name>` — the audit parses this token.
- **`_overrides/<X>/`** is part of the routing namespace. A
  `skill:lean-build` ref resolves to `skills/_overrides/lean-build/`.
- **Match the slug** — case-sensitive, hyphens (not underscores).

---

## Eval coverage — adding a smoke test

Every new skill should have at least one deterministic smoke case at
`scripts/eval/cases/<name>-smoke.yaml`:

```yaml
case_id: <name>-smoke
title: <one-line scenario>
skill: <name>
difficulty: trivial | easy | medium | hard
prompt: |
  ...the user-facing prompt that would route to this skill...
expected_substring: ...the canonical answer fragment to grep for...
contains:
  - <regex pattern 1>
  - <regex pattern 2>
not_contains:
  - <regex of forbidden output>
tags:
  - <cluster>
  - <task-type>
```

After adding the YAML:

```bash
cd skills/
# 1. Run the runner to generate per-case output JSONs:
python3 scripts/eval/run_eval.py \
  --cases 'scripts/eval/cases/<name>-smoke.yaml' \
  --out /tmp/eval-out

# 2. Refresh the baseline (this includes your new case):
python3 scripts/eval/baseline.py \
  --run-dir /tmp/eval-out \
  --baseline scripts/eval/baselines/smoke/baseline.json \
  --mode write
```

CI will then hard-gate against the refreshed baseline.

**YAML escape gotcha:** in double-quoted YAML strings, `\(` is an
invalid escape. Use single-quoted strings for regexes, or
double-escape (`\\(`).

---

## Calibration — adding a judge corpus (optional)

For skills where LLM-judge quality matters (proof-quality, blueprint,
spec writing, etc.), you can add a calibration corpus per ADR-0039:

1. **Create `lab/evals/known-bad/<skill>/<task-id>.transcript.md`**
   with YAML preamble:
   ```yaml
   ---
   task_id: <unique-task-id>
   expected_max_score: 2  # or 1 if rubric-clearly-bad
   failure_mode: <one of the rubric's "≤2" clauses>
   notes: <why this is a known-bad example>
   ---
   # Task
   <the user-facing prompt>

   # Response
   <the bad response that should be flagged>
   ```

2. **Capture judge replies** via the sub-agent fleet
   (see `scripts/eval/graders/DISPATCH.md`):
   ```bash
   python3 scripts/eval/calibrate_judge.py build \
     --rubric scripts/eval/graders/rubrics/<rubric>.yaml \
     --transcript lab/evals/known-bad/<skill>/<task-id>.transcript.md \
     > /tmp/judge-prompt.txt
   # Dispatch /tmp/judge-prompt.txt to N judges, capture JSON replies,
   # save to lab/evals/known-bad/<skill>/_replies/<task-id>/<judge>.json
   ```

3. **Validate the corpus passes:**
   ```bash
   python3 scripts/eval/calibrate_judge.py check \
     --rubric scripts/eval/graders/rubrics/<rubric>.yaml \
     --skill-dir lab/evals/known-bad/<skill> \
     --label ensemble-2026-XX-XX \
     --min-flag-rate 0.90
   ```

4. **Add a CI matrix row** in
   `.github/workflows/eval-smoke.yml :: judge-calibration` so the
   gate runs on every push.

---

## Identifier conventions

| Asset | Convention | Example |
|---|---|---|
| Skill slug (folder + name) | `kebab-case` | `lean-proof` |
| YAML `name:` | matches slug | `name: lean-proof` |
| `SK-ID` in gateway registry | sequential `SK-NN` | `SK-07 lean-gateway` |
| Handbook file | `<slug>-handbook.md` | `lean-review-council-handbook.md` |
| Reference (non-handbook) file | descriptive kebab | `lean4-tactic-hierarchy.md` |
| Smoke case file | `<slug>-smoke.yaml` | `lean-proof-omega-smoke.yaml` |
| Calibration transcript | `<task-id>.transcript.md` | `leaves-sorry.transcript.md` |

---

## Checklist before opening a PR

- [ ] SKILL.md satisfies the v2 dispatch contract (run `check_conformance.py`).
- [ ] If layered: handbook back-references the SKILL via `extracted_from:`.
- [ ] All `handoffs.successors` / `handoffs.predecessors` refs resolve.
- [ ] At least one `scripts/eval/cases/<name>-smoke.yaml` smoke case
      added (or justification documented in PR description).
- [ ] Baseline refreshed: `scripts/eval/baselines/smoke/baseline.json`
      reflects the new case at score 1.00.
- [ ] CI green:
      `skill-conformance`, `smoke`, `glicko2`, `llm-judge-grader`,
      `judge-calibration` — all 5 jobs pass.
- [ ] If touching a tier classification or moving handoff edges:
      update `lab/skill-audit/audit-2026-05-27-snapshot.md` headline
      counts.

---

## Provenance

This authoring guide consolidates the conventions established across:
- **Pass 2-6**: hot-tier v2 schema + templates v2.
- **Pass 13-15**: layering pattern + math-cluster v2 upgrade +
  breadth-pass tail.
- **Pass 16-17**: per-skill polish, handoff DAG audit, override v2
  migration, audit-script promotion.

See `lab/MASTER-PLAN.md` and the session checkpoints under
`docs/easci/lean/lab/` for the historical design rationale.
