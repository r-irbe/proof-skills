---
name: lean-enforcement
description: Programmatic enforcement of quality, conventions, and completeness using Python and shell scripts. Use when running CI checks, pre-review gates, post-review validation, ecosystem health monitoring, or retroactive audit tooling. Covers all enforcement scripts and their integration with the skill ecosystem.
---

# SK-36: Lean 4 Enforcement Engine

Enforce quality, conventions, and completeness programmatically. Every check that can be automated MUST be automated — human review time is spent on judgement, not mechanics.

---

## Part 1 — Script Inventory

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
| **`workflow_gate.py`** | **Python** | **Workflow gate enforcer — validates mandatory gates before any workflow step** | **Yes (blocking gates)** |

---

## Part 2 — Execution Model

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
- `0` — pass (or info-only findings)
- `1` — warnings or issues found (non-blocking)
- `2` — critical failure (blocks everything)

---

## Part 3 — Integration with Skills

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

## Part 4 — Creating New Enforcement Scripts

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

## Part 5 — Enforcement Anti-Patterns

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

## Part 6 — Workflow Gate Enforcement

### 6.1 The Problem: Gate Bypass Risk

Gates documented in SKILL.md files are only as strong as the agent's willingness to follow them. Two critical gaps existed:

| Gap | Risk | Severity |
|---|---|---|
| **G5:** `council_precheck.sh` not programmatically enforced | Agent skips precheck, reviews on broken build | **High** |
| **G7:** Gateway dispatch rules exist only as pseudocode | No executable code enforces workflow ordering | **High** |

### 6.2 The Solution: `workflow_gate.py`

`workflow_gate.py` is the single, executable enforcement layer that:
1. **Defines all workflows** as structured data (not prose)
2. **Enforces step ordering** — step B cannot run until step A has passed
3. **Runs required scripts** — and blocks on failure
4. **Tracks state** — persisted in `docs/tracking/workflow_state/*.json`
5. **Detects staleness** — script results expire after 30 minutes

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

- [`../../templates/Template_Verification.md`](../../templates/Template_Verification.md) — Template: What to enforce and how
- [`../../scripts/lean/`](../../scripts/lean/) — Runnable enforcement scripts (project-agnostic)
