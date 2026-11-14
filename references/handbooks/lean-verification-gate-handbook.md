---
name: lean-verification-gate-handbook
description: Unified reference handbook for @lean-verification-gate (CI enforcement,
  3-axiom closure lockdown, and cold kernel replay).
extracted_from: skills/lean-verification-gate/SKILL.md
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Exported theorem `theorem foo ...` before merge | `lean_axiom_closure` | Verify closure subset of `[propext, Classical.choice, Quot.sound]` |
| Module after `sorry` removal | `lake build <Module>` (cold replay) | Ensure `.olean` cache does not hide unchecked terms |
| File missing `set_option autoImplicit false` | Static enforcement lint | Add `set_option autoImplicit false` immediately after `import` |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Lock down transitive axioms across corpus | `lean_axiom_closure` + `#print axioms` | Fail CI on `sorryAx`, custom `axiom`, or unapproved `Lean.ofReduceBool` |
| Verify proofs survive fresh kernel check | Cold replay (`lake clean` / targeted rebuild) | Quote scanned module & declaration counts in gate verdict |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `depends on axiom sorryAx` | Unfinished subgoal or upstream `sorry` import | Locate culprit via `lean_axiom_closure` and route to `@lean-proof` |
| `depends on axiom Lean.ofReduceBool` | `native_decide` or `bv_decide` used in strict kernel lane | Replace with `sair_decide` (`rfl | decide +kernel | omega`) |

---

<!-- Merged from lean-enforcement-handbook.md -->

# SK-36: Lean 4 Enforcement Engine

Enforce quality, conventions, and completeness programmatically. Every check that can be automated MUST be automated -- human review time is spent on judgement, not mechanics.

---

## Part 1 -- Script Inventory

| Script | Language | Purpose | Blocks Review? |
|---|---|---|---|
| `council_precheck.sh` | Bash | Build + sorry + conventions + git | **Yes** |
| `review_coverage.py` | Python | Theorem → review record mapping | No |
| `axiom_audit.py` | Python | Axiom contamination scan | **Yes** (if sorryAx found) |
| `metric_sync.py` | Python | Paper metrics ↔ code metrics | No |
| `zettelkasten_lint.py` | Python | ZK structural health | No |
| `retro_recon.py` | Python | RETRO Phase R automated discovery | No |
| `bridge_validator.py` | Python | Cross-module import validation | No |
| `proof_quality.py` | Python | Vacuous truth, long proof, unused hyp | No (P1 = warning) |
| `ecosystem_health.py` | Python | Skill registry, structure, integrity | No |
| `enforce_all.sh` | Bash | Run all above in correct order | Pipeline gate |
| **`workflow_gate.py`** | **Python** | **Workflow gate enforcer -- validates mandatory gates before any workflow step** | **Yes (blocking gates)** |

---

## Part 2 -- Execution Model

### 2.1 When to Run

| Event | Scripts to Run | Who Triggers |
|---|---|---|
| Before council review | `council_precheck.sh` | Gateway or reviewer |
| After completing theorem | `review_coverage.py` | Implementer |
| After build succeeds | `axiom_audit.py --generate-script` | CI |
| Before paper submission | `metric_sync.py` | Documenter |
| Weekly maintenance | `zettelkasten_lint.py` | Synthesizer |
| Starting RETRO audit | `retro_recon.py` | Audit coordinator |
| After module refactoring | `bridge_validator.py` | Ω (Integration) |
| Before milestone review | `enforce_all.sh --strict` | Gateway |
| Skill ecosystem changes | `ecosystem_health.py` | Gateway |

### 2.2 Dependency Order

```
lake build
  ├── council_precheck.sh (includes build check)
  │     └── axiom_audit.py (needs build artifacts)
  ├── proof_quality.py (static analysis, no build needed)
  ├── retro_recon.py (static analysis)
  ├── bridge_validator.py (static analysis)
  ├── metric_sync.py (reads code + paper)
  ├── review_coverage.py (reads code + review records)
  ├── zettelkasten_lint.py (reads ZK directory)
  └── ecosystem_health.py (reads skills + scripts)

enforce_all.sh orchestrates all in this order.
```

### 2.3 Exit Codes

All scripts follow this convention:
- `0` -- pass (or info-only findings)
- `1` -- warnings or issues found (non-blocking)
- `2` -- critical failure (blocks everything)

---

## Part 3 -- Integration with Skills

### 3.1 Gateway Integration

The gateway (SK-07) calls enforcement scripts at these points:

```
TASK ARRIVES → route_task()
  IF task_type == "review":
    RUN council_precheck.sh
    IF exit_code == 2: REJECT task, report build failure
    IF exit_code == 1: WARN, proceed with caution flag
    IF exit_code == 0: PROCEED normally

  IF task_type == "retroactive_audit":
    RUN retro_recon.py → produce recon_report.md
    PARSE report → extract wave schedule
    PROCEED with RETRO protocol (SK-35)

  IF task_type == "milestone":
    RUN enforce_all.sh --strict
    IF exit_code != 0: BLOCK milestone, remediate
```

### 3.2 Council Integration

Council pre-check is mandatory:

```
BEFORE any council session:
  1. council_precheck.sh → must exit 0
  2. axiom_audit.py → no sorryAx
  3. If FAIL: session BLOCKED until fixes applied
```

### 3.3 Retroactive Audit Integration

The RETRO protocol (SK-35) uses enforcement scripts at each phase:

| RETRO Phase | Scripts Used |
|---|---|
| R (Reconnaissance) | `retro_recon.py`, `bridge_validator.py` |
| E (Establish) | `council_precheck.sh`, `axiom_audit.py` |
| T (Triage) | `proof_quality.py` (finds issues to prioritize) |
| R (Review) | `review_coverage.py` (tracks progress) |
| O (Onboard) | `enforce_all.sh --strict` (graduation gate) |

---

## Part 4 -- Creating New Enforcement Scripts

When adding a new check:

### 4.1 Template

```python
#!/usr/bin/env python3
"""
[CheckName] Enforcement
[One-line purpose]
Referenced by [skill names and section numbers].

Usage:
    python3 scripts/[check_name].py [--lean-dir Project] [args...]
"""

import argparse
import sys
from pathlib import Path


def check(lean_dir: Path) -> list[dict]:
    """Run the check. Returns list of findings."""
    findings = []
    # ... implementation ...
    return findings


def main():
    parser = argparse.ArgumentParser(description='[check description]')
    parser.add_argument('--lean-dir', type=Path, default=Path('Project'))
    args = parser.parse_args()
    
    findings = check(args.lean_dir)
    
    errors = [f for f in findings if f['severity'] == 'error']
    print(f"{'✓' if not errors else '✗'} [CheckName]: {len(findings)} finding(s)")
    
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
```

### 4.2 Conventions

1. Always use `argparse` with `--lean-dir` defaulting to `Path('Project')`
2. Always include a `"""docstring"""` with usage
3. Always use `sys.exit(0)` for pass, `sys.exit(1)` for issues
4. Return structured findings as `list[dict]` with at least `severity` and `message`
5. Reference the skill(s) that use this script in the docstring
6. Add the script to `enforce_all.sh`
7. Add the script to the `ecosystem_health.py` expected scripts list
8. Add to the Script Inventory table above

---

## Part 5 -- Enforcement Anti-Patterns

| Anti-Pattern | Why It's Bad | Correction |
|---|---|---|
| Skipping council_precheck | Review on broken build wastes time | Make it the FIRST check |
| Running enforce_all.sh every commit | Too slow; blocks development flow | Run on milestones only; use individual scripts for targeted checks |
| Ignoring exit code 1 | Warnings accumulate and become errors | Address warnings within 2 sessions |
| Not updating enforce_all.sh | New scripts not integrated | Always add new scripts to the pipeline |
| Manual checks for things scripts can do | Inconsistent, error-prone | Automate everything automatable |
| Scripts that modify code | Enforcement = observe, not mutate | Scripts ONLY report; agents fix |
| Overlapping checks | Wasted time | Each script has a unique concern |
| No --strict mode | Can't distinguish advisory from blocking | Always support strict/non-strict |

---

## Part 6 -- Workflow Gate Enforcement

### 6.1 The Problem: Gate Bypass Risk

Gates documented in SKILL.md files are only as strong as the agent's willingness to follow them. Two critical gaps existed:

| Gap | Risk | Severity |
|---|---|---|
| **G5:** `council_precheck.sh` not programmatically enforced | Agent skips precheck, reviews on broken build | **High** |
| **G7:** Gateway dispatch rules exist only as pseudocode | No executable code enforces workflow ordering | **High** |

### 6.2 The Solution: `workflow_gate.py`

`workflow_gate.py` is the single, executable enforcement layer that:
1. **Defines all workflows** as structured data (not prose)
2. **Enforces step ordering** -- step B cannot run until step A has passed
3. **Runs required scripts** -- and blocks on failure
4. **Tracks state** -- persisted in `docs/tracking/workflow_state/*.json`
5. **Detects staleness** -- script results expire after 30 minutes

### 6.3 Invocation Protocol

**Rule:** Every workflow step invocation MUST be preceded by a `workflow_gate.py` call.

```bash
# Before council review:
python3 scripts/workflow_gate.py --workflow council_review --step pre_check
# Exit 0 → proceed. Exit 1 → BLOCKED.

# Before dispatching members:
python3 scripts/workflow_gate.py --workflow council_review --step dispatch_members
# Automatically checks that pre_check has passed.

# Check what's available:
python3 scripts/workflow_gate.py --list-workflows
python3 scripts/workflow_gate.py --status
```

### 6.4 Available Workflows

| Workflow | Steps | Primary Gate Script(s) |
|---|---|---|
| `council_review` | pre_check → dispatch → votes → sdr → close | `council_precheck.sh` |
| `retro_audit` | recon → establish → triage → review → onboard | All scripts in RETRO order |
| `milestone` | pre_milestone → council_all → metric_sync → release | `enforce_all.sh --strict` |
| `spec_lifecycle` | requirements → design → docs → approval | Council vote |
| `forward_sync` | extract → specify → research → implement → review → index | `council_precheck.sh`, `review_coverage.py` |
| `backward_sync` | detect → generate → apply → verify | `metric_sync.py` |

### 6.5 State Tracking

All gate checks are persisted:

```
docs/tracking/workflow_state/
  council_review_20260328.json
  retro_audit_20260328.json
  milestone_20260328.json
```

Each file records: workflow name, session ID, step statuses (passed/blocked), script results (passed/failed + timestamp + output tail), and failure reasons.

### 6.6 Enforcement Hierarchy

```
Level 1: Compile-time    @[linter] in Lean 4          Catches sorry, bare aesop, native_decide
Level 2: Pre-workflow     workflow_gate.py             Blocks workflow steps with failed gates
Level 3: Script-level     Individual scripts           Build, axioms, quality, coverage, etc.
Level 4: Pipeline-level   enforce_all.sh               All scripts in dependency order
Level 5: Workflow-level   workflow_gate.py + state      Step ordering, prerequisite chains, staleness
Level 6: Council-level    5-member vote                 Human-equivalent judgement
Level 7: Meta-level       Meta-council + calibration    Cross-council coherence, member reliability
```

Each level catches what the level below cannot. No single level is sufficient alone. The combination provides defense-in-depth for 99.99% reliability.

---

## See also

- [`../../templates/Template_Verification.md`](../../templates/Template_Verification.md) -- Template: What to enforce and how
- [`../../scripts/lean/`](../../scripts/lean/) -- Runnable enforcement scripts (project-agnostic)

---

## Operational Details (from `skills/lean-enforcement/SKILL.md`)

# lean-enforcement

> ⚠️ **MANDATORY** (hot-tier): blocking scripts (`council_precheck.sh`,
> `axiom_audit.py` on `sorryAx`, `workflow_gate.py` on mandatory gates) are
> hard gates -- a failure HALTS the calling workflow. Skipping Persist =
> incomplete.

## Routing

- **USE FOR:** running an individual enforcement script or the full `enforce_all.sh` pipeline; checking a build is clean before review; auditing axioms
  after a refactor; validating cross-module bridges; gating a workflow step.
- **DO NOT USE FOR:** deciding whether a proof is *correct* (delegate to `@lean-proof-review`); scoring repository quality (delegate to
  `@lean-quality-engine`); routing across skills (delegate to `@lean-gateway`).
- **TRIGGERS:** enforcement, CI gate, axiom audit, council_precheck, workflow_gate, ecosystem_health, sorry check.

## Behavioural rules (G-*)

- **G-1** (MUST): Every check that CAN be automated MUST be automated -- human review time is for judgement, not mechanics. [Trace: AC-01]
- **G-2** (MUST): `axiom_audit.py` detecting `sorryAx` MUST block the calling workflow with exit code ≠ 0. [Trace: AC-02]
- **G-3** (MUST): `council_precheck.sh` failure MUST block council convening; the workflow MUST NOT proceed to review. [Trace: AC-03]
- **G-4** (MUST): `workflow_gate.py` MUST verify all mandatory gates for a given step before that step starts. [Trace: AC-04]
- **G-5** (SHOULD NOT): The skill SHOULD NOT silently retry a failed blocking script; escalate per §Recovery & STOP instead. [Trace: AC-05]
- **G-6** (MUST): Every script invocation MUST emit a structured result (exit code, summary, artefact path) to the repository's enforcement log. [Trace: AC-06]
- **G-7** (SHOULD): When multiple scripts can answer the same question, the skill SHOULD prefer the most specific (e.g. `axiom_audit.py` over
  `enforce_all.sh` for an axiom-only question). [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] -- identify the target gate (single script, group, `enforce_all.sh`, `lean_diagnostics` static abstract interpretation
   certificates [`NatSubTruncation`, `NatDivModByZero`, Zone DBM `decreasing_by` synthesis, Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop
   widening, trace partitioning], `lean_counterexample_search` with Galois-guided hypothesis domain pruning [`analyzeHeaderHypothesisDomains` /
   `pruneHeaderNatDomain`], `lean-rules` via `node tools/lean-lsp-mcp/bin/lean-rules.js`, `pi-lens` [`pilens_ast_grep_search`, `pilens_diagnostics`] as
   sub-second structural pre-checks before `lake build`, or `pi-harness-bridge` policy/unicode gates); read the repository's `lakefile.lean` + recent
   commit log.
2. **Run** [execute] -- execute the script(s) in the order documented in [`REFERENCE.md`](./REFERENCE.md) Part 2; capture stdout, stderr, exit code,
   artefact paths.
3. **Validate** [validate] -- interpret exit codes against the blocking-vs-advisory table; for blocking failures, HALT and route to recovery.
4. **Aggregate** [validate] -- compose a per-script status line + overall pass/fail; surface advisories without blocking.
5. **Persist** [persist] *(MANDATORY)* -- append the structured result to the enforcement log, update the CI annotation, tick the relevant gate. Skipping
   Persist = incomplete.

## Recovery & STOP

- `axiom_audit.py` finds `sorryAx` → immediate STOP; escalate to proof author; do NOT mark the workflow green.
- `council_precheck.sh` fails → STOP; fix build / sorry / convention / git state before retrying.
- `workflow_gate.py` blocks a mandatory gate → STOP; complete the prerequisite gate, then retry.
- Any blocking script crashes ×3 → STOP; file a bug against this skill.
- Confidence < 90 % about which script to invoke → STOP, ask.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/enforcement/requirements.md` -- every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the full script inventory, integration matrix, anti-patterns, and the workflow-gate enforcement
  model (original v1 content, preserved verbatim).

## Common failure modes

> AI agents commonly: silently retry a blocking failure; downgrade a hard gate
> to a soft one to "unblock progress"; run `enforce_all.sh` when a single
> script would have answered the question; skip the structured-result emit
> step; trust a green gate whose generated probe/scan manifest is stale --
> after registering new modules or targets, REGENERATE generated probe
> scripts and rerun before quoting the result, and treat per-item coverage
> gaps inside the gate's own report as findings rather than noise (a summary
> can be clean while whole namespaces went unscanned). When a report shows
> unexplained gaps, close the loop with a targeted spot-check (e.g. a
> single-declaration `#print axioms` probe) before declaring the gate clean.
> Full registry: GUARDRAILS.md §Agent failure taxonomy.


---

<!-- Merged from lean-axiom-closure-handbook.md -->

# Axiom-Closure Audit (the FinalCheck discipline)

## Why

`#print axioms foo` checks ONE declaration. A project that claims
"only the standard axioms" needs the claim over EVERY declaration,
re-checked automatically on every build, with a failure that blocks
the build. Spot checks rot; a compile-time lockdown does not.

## The instrument

`AxiomClosure.lean.tmpl` (this directory) is a small, dependency-free
Lean module defining `Audit.axiomClosureAudit (root : Name)
(allow : Array Name) : CommandElabM Unit`: it walks every constant in
the environment whose root namespace is `root`, computes each
declaration's transitive axiom closure (`Lean.collectAxioms`, the same
machinery as `#print axioms`), and throws an error naming the
declaration for every axiom outside `allow`. Internal
implementation-detail names are excluded. Full-corpus cost measured on
a Mathlib-dependent corpus of ~9k named declarations: **seconds**.

## Workflow (the FinalCheck setup discipline)

1. Vendor `AxiomClosure.lean.tmpl` into the project (e.g. `<root>/Audit/AxiomClosure.lean`),
   adjusting only the module path of the example.
2. Create the consumer file (`FinalCheckAll.lean.tmpl`): import the
   audit module + the project root, then
   `#guard_msgs (drop info) in #eval Audit.axiomClosureAudit <root> #[...allowlist]`.
3. Keep the consumer file INSIDE the library's source globs so the
   project's normal build runs it. `#guard_msgs (drop info)` drops the
   summary info line; any violation error - and only a violation
   error - fails the build.
4. The allowlist is the project's DECLARED trust base. Default:
   `#[`propext, `Quot.sound, `Classical.choice]`. Tighten it to exactly
   the axioms the project is willing to assume; every extra entry must
   have a recorded reason.

## What violations mean

- `sorryAx` - a `sorry` (or `admit`) in the closure: the proof is not
  complete. This is how incomplete proofs hide behind wrappers,
  aliases, and re-exports that per-theorem checks miss.
- `Lean.ofReduceBool` - a `native_decide` somewhere in the closure:
  compiled evaluation is trusted, not kernel-checked. Replace with
  `decide`/`native_decide`-free proofs or record an explicit,
  reviewed exception (a widened allowlist entry with a reason).
- A custom axiom name - an `axiom` declaration is in the closure:
  either remove it and prove the statement, or document it in the
  allowlist with justification.

## Behavioural rules (G-*)

- **G-1** (MUST): the audit module runs inside the project's normal
  build (source globs), not as an optional side script.
- **G-2** (MUST): the allowlist is explicit and versioned; an empty or
  implicit allowlist makes the audit meaningless.
- **G-3** (MUST): a new allowlist entry requires a recorded reason and
  a named owner decision - tightening is free, widening is a decision.
- **G-4** (SHOULD): pair with `@lean-replay-verification` R2: the
  closure audit is the per-build instrument; the replay ladder is the
  cadence.
- **G-5** (MUST -- Check 7 Barrel Completeness): verify 100% barrel
  completeness before trusting `Audit.axiomClosureAudit` -- every `.lean`
  file in the package directory MUST be transitively imported by the
  root barrel module imported by `FinalCheckAll.lean`, otherwise
  unimported orphan modules silently bypass `Lean.collectAxioms`.
- **G-6** (SHOULD -- Check 7 Constructive Gate): for first-order
  decidable `Nat`/`Int`/`Bool`/`BitVec` modules, audit with a tightened
  constructive allowlist `#[`propext, `Quot.sound]` (excluding
  `Classical.choice`) and eliminate accidental `Classical.choice`
  leakage via `Bool.and_eq_true`, `decide_eq_true_eq`, `omega`, or
  `bv_decide` (`constructive-decidable-reduction`).

## Pitfalls

- The audit checks declarations under ONE root namespace; imported
  dependencies (Mathlib, core) are trusted at their own guarantee.
  State the boundary.
- `#eval` runs at elaboration: the consumer file re-runs the audit on
  every rebuild of itself - that is the point, but keep the consumer
  small so rebuilds stay fast (the audit itself is seconds).
- Compile-time `decide`-heavy environments may see slower elaboration
  of the consumer file; that cost is the audit running.
- Name-literal allowlist entries (`propext`, not "propext" strings):
  the parameter is `Array Name`.

## Verification

- The consumer file builds as part of `lake build` and is silent.
- Deliberately introducing a `sorry` makes the build FAIL with
  `<name> : axiom closure contains sorryAx` - verify the failure path
  once during setup.
- The summary line (dropped by the guard in CI) is printable by
  running the same `#eval` without the guard; quote checked/violation
  counts as the audit evidence.

## Recovery

- If `Audit.axiomClosureAudit` reports `sorryAx`, trace the offending declaration via `#print axioms` and hand off to `@lean-proof` to close the open subgoal.
- If `Lean.ofReduceBool` appears, replace `native_decide` with kernel-checked `decide` / `omega` or obtain explicit owner sign-off before widening the
  allowlist.

## Handoffs

- **Predecessors:** `@lean-replay-verification` (R2 cadence), `@lean-deep-audit` (P1 trust-base lockdown).
- **Successors:** `@lean-proof-review` (single-module audit), `@lean-enforcement` (CI gate execution).


---

<!-- Merged from lean-replay-verification-handbook.md -->

# Replay Verification After Sorry Removal

## Why

An incremental `lake build` re-elaborates only changed modules. That is
enough to kernel-check the edited proof, but it is NOT evidence that the
tree's acceptance is real: stale `.olean` artifacts, a partially applied
edit, or a single kernel release's bug can all make a tree "finish
successfully" without the completed proof being re-checked from a cold
state. Trust in a finished proof should rest on a replay ladder, not on
one incremental green build.

## The replay ladder (R1 -> R4, increasing independence)

- **R1 - fresh kernel replay (same kernel, cold state).** A full build
  from a clean build directory (`lake clean` + `lake build`, or a fresh
  worktree's first build). Kills every stale-artifact and partial-state
  false-accept class. REQUIRED on the commit that removes a `sorry`.
- **R2 - axiom-closure audit.** `#print axioms` over the touched
  declarations (or a project-wide axiom audit against an explicit
  expected-axioms allowlist). `sorryAx` and any non-standard axiom in
  the closure = FAIL. This bounds the trust base to the named axioms
  and catches sorries hiding behind wrappers or aliases.
  EXECUTOR: the `lean-axiom-closure` skill supplies a compile-time
  metaprogram that checks every declaration's closure inside the
  project's normal build (the FinalCheck discipline) - prefer it over
  per-theorem spot checks wherever the project can vendor one module.
- **R3 - cross-version replay.** Rebuild the same proofs at the next
  toolchain pin when one is available. A different kernel RELEASE is
  the practical second opinion; institutionalize via the project's
  upgrade/migration campaign rather than ad-hoc. A deferral (no newer
  pin yet) MUST be recorded, not skipped silently.
- **R4 - independent-kernel recheck (load-bearing results).** Export
  the proofs and check them with an independent implementation.
  Known checkers: trepplein (Scala; genuinely independent lineage;
  checks Lean's exported proof terms) and lean4lean (complete Lean 4
  typechecker written in Lean; fast enough for Mathlib-scale corpora,
  but derived from the C++ kernel, so it shares some implementation
  bug classes - weaker independence, still useful). Record WHICH
  checker and version, and the caveat.

## Behavioural rules (G-*)

- **G-1** (MUST): the commit that removes a `sorry` MUST record R1
  replay evidence: toolchain (exact pin/SHA), job/module count,
  exit status. "It builds" from an incremental build is not replay
  evidence. [R1]
- **G-2** (MUST): the R2 axiom-closure audit MUST pass against an
  explicit allowlist of expected axioms; empty or missing allowlist
  makes the audit meaningless. [R2]
- **G-3** (MUST NOT): an incremental build MUST NOT be presented as
  replay evidence in a review, ledger, or commit message. [R1]
- **G-4** (MUST): when a newer toolchain pin exists, R3 MUST either
  run or carry a recorded deferral with the reason. [R3]
- **G-5** (SHOULD): load-bearing result batches SHOULD get R4 with a
  named independent checker; record checker name, version, and the
  lineage caveat when the checker shares kernel lineage. [R4]
- **G-6** (MUST NOT): a cold replay MUST NOT destroy shared in-flight
  state on a multi-writer tree without coordination - clean in an
  agreed window or an isolated worktree, never under active lanes.

## Workflow

1. Identify the proof-completion event (sorry removed / new theorem
   accepted as load-bearing).
2. Run R1 (cold full build); capture pin, job count, rc into the
   commit message or ledger.
3. Run R2 against the expected-axioms allowlist; quote the verdict.
4. Check R3 status: is a newer pin available? Run it via the
   project's migration flow or record the deferral.
5. For load-bearing batches, run R4 with trepplein or lean4lean and
   record checker + version + lineage caveat.
6. Link the replay evidence from the review record (commit, ledger,
   or review file) so a later reader can re-derive it.

## Pitfalls

- Incremental green build presented as replay (G-3) - the most common
  laundering of weak evidence.
- After `lake clean`, dependency caches (e.g. Mathlib's) must be
  re-fetched; budget for it, do not silently skip it.
- `#print axioms` on a wrapper can look clean while the INNER lemma
  is sorry-ed - audit the full closure, not one name.
- lean4lean shares code lineage with the C++ kernel; trepplein covers
  exported proof terms but check its format-version coverage against
  the toolchain's export format.
- A replay re-runs everything: on multi-writer trees coordinate the
  clean (G-6) or other lanes' tooling will fight the missing artifacts.

## Verification

- R1 evidence present (pin, job count, rc) for the sorry-removal commit.
- R2 verdict quoted against the named allowlist: no `sorryAx`, no
  non-standard axioms.
- R3 run or deferred-with-reason, recorded.
- R4 (when applicable): checker name + version + caveat recorded.

## Recovery

- If R1 (`lake clean` + `lake build`) fails on a tree that passed incrementally, treat the proof as unverified and hand back to `@lean-proof` or
  `@lean-build` to fix the hidden stale-artifact dependency.
- If R2 surfaces `sorryAx` or an unexpected axiom in the closure, block acceptance and route to `@lean-axiom-closure` / `@lean-proof`.

## Handoffs

- **Predecessors:** `@lean-proof` (sorry removed), `@lean-proof-review` (single-proof review).
- **Successors:** `@lean-axiom-closure` (R2 compile-time lockdown), `@lean-quality-engine` (milestone QA gate).

