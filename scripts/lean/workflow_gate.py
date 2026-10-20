#!/usr/bin/env python3
"""
Workflow Gate Enforcer
Validates that mandatory gates are satisfied before a workflow step can proceed.
Closes enforcement gaps G5 (precheck not programmatically enforced) and G7
(gateway dispatch rules exist only as pseudocode, not executable enforcement).

Every workflow invocation MUST pass through this script. It reads gate
definitions, checks that prerequisite scripts have been run and passed,
validates the workflow state file, and either PERMITS or BLOCKS the step.

Usage:
    python3 scripts/workflow_gate.py --workflow WORKFLOW --step STEP [--lean-dir EASCI]
    python3 scripts/workflow_gate.py --list-workflows
    python3 scripts/workflow_gate.py --status [--workflow WORKFLOW]

Workflows:
    council_review   — 5-member review council session
    retro_audit      — RETRO 5-phase retroactive audit
    milestone        — Project milestone release gate
    spec_lifecycle   — Specification lifecycle (requirements → design → docs)
    forward_sync     — Document → Lean forward pipeline
    backward_sync    — Lean → Document backward pipeline

Exit codes:
    0  — gate passed, step may proceed
    1  — gate failed, step is BLOCKED (with reason)
    2  — invalid workflow/step specification
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from axiom_audit import scan_raw_axioms, strip_comments_preserving_newlines

STATE_DIR = Path("docs/tracking/workflow_state")

# ═══════════════════════════════════════════════════════════════
# Condition Checkers (Wave 9 HITL C241, 2026-04-29)
# ═══════════════════════════════════════════════════════════════
# Each gate carries a `required_conditions` list of named conditions that
# must hold for the step to pass.  Previously the metadata was declared but
# never evaluated.  Conditions are now resolved by the registry below.
#
# A checker has the signature:
#     check(state: dict, lean_dir: Path, asserted: set[str]) -> (bool, str)
# returning (passed, reason).  The third argument lists conditions that the
# operator has explicitly asserted on the command line via `--assert NAME`,
# which is required for conditions whose truth cannot be verified
# automatically (manual artefact existence, council votes, etc.).
# ═══════════════════════════════════════════════════════════════


def _count_keyword_occurrences(lean_dir: Path, pattern: re.Pattern[str]) -> int:
    """Count real keyword occurrences in Lean code after stripping comments."""
    if not lean_dir.exists():
        return -1
    total = 0
    try:
        for lean_file in sorted(lean_dir.rglob("*.lean")):
            source = strip_comments_preserving_newlines(lean_file.read_text(encoding="utf-8"))
            total += len(pattern.findall(source))
        return total
    except OSError:
        return -1


def _grep_sorry_count(lean_dir: Path) -> int:
    """Count real `sorry` tokens in Lean source (comments/docstrings stripped)."""
    return _count_keyword_occurrences(lean_dir, re.compile(r"\bsorry\b"))


def _grep_admit_count(lean_dir: Path) -> int:
    """Count real `admit` tokens in Lean source (comments/docstrings stripped)."""
    return _count_keyword_occurrences(lean_dir, re.compile(r"\badmit\b"))


def _grep_axiom_count(lean_dir: Path) -> int:
    try:
        return sum(len(items) for items in scan_raw_axioms(lean_dir).values())
    except OSError:
        return -1


def _check_lake_build(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
    """Run `lake build -q` and return whether it succeeded."""
    if "build_passes" in asserted:
        return True, "asserted"
    try:
        result = subprocess.run(
            ["lake", "build", "-q"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(lean_dir.resolve().parent if lean_dir.is_dir() else Path.cwd()),
        )
        if result.returncode == 0:
            return True, "lake build returned 0"
        return False, f"lake build returned {result.returncode}: {result.stderr[-200:]}"
    except FileNotFoundError:
        return False, "lake binary not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "lake build timed out after 600s"


def _check_no_sorry(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
    if "no_sorry" in asserted or "zero_sorry" in asserted:
        return True, "asserted"
    sorry_count = _grep_sorry_count(lean_dir)
    admit_count = _grep_admit_count(lean_dir)
    if sorry_count < 0 or admit_count < 0:
        return False, f"grep failed under {lean_dir}"
    ok = sorry_count == 0 and admit_count == 0
    return (ok, f"real sorry count = {sorry_count}, admit count = {admit_count}")


def _check_zero_sorry(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
    return _check_no_sorry(state, lean_dir, asserted)


def _check_zero_axiom(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
    if "axiom_audit_clean" in asserted:
        return True, "asserted"
    count = _grep_axiom_count(lean_dir)
    if count < 0:
        return False, f"grep failed under {lean_dir}"
    return (count == 0, f"axiom count = {count}")


def _check_auto_implicit_false(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
    if "autoImplicit_false" in asserted:
        return True, "asserted"

    missing: list[str] = []
    try:
        for lean_file in sorted(lean_dir.rglob("*.lean")):
            text = lean_file.read_text(encoding="utf-8")
            if "set_option autoImplicit false" not in text:
                missing.append(lean_file.relative_to(lean_dir).as_posix())
    except OSError as exc:  # pragma: no cover — defensive
        return False, f"could not read Lean sources: {exc}"

    if not missing:
        file_count = len(list(lean_dir.rglob("*.lean")))
        return True, f"all {file_count} Lean files set autoImplicit false"

    preview = ", ".join(missing[:5])
    if len(missing) > 5:
        preview += f", ... (+{len(missing) - 5} more)"
    return False, f"{len(missing)} file(s) missing set_option autoImplicit false: {preview}"


def _check_step_passed(step_name: str):
    """Build a checker that verifies a prior step has reached `passed` state."""

    def _checker(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
        if f"{step_name}_passed" in asserted:
            return True, "asserted"
        step_state = state.get("steps", {}).get(step_name, {})
        status = step_state.get("status")
        if status == "passed":
            return True, f"{step_name} status=passed"
        return False, f"{step_name} status={status or 'not_run'}"

    return _checker


def _check_cached_script(script_name: str, must_pass: bool = True):
    """Build a checker that requires a prior cached script run to have passed."""

    def _checker(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
        cached = state.get("script_results", {}).get(script_name)
        if not cached:
            return False, f"script {script_name} has no cached result"
        if must_pass and not cached.get("passed"):
            return False, f"script {script_name} most recent run did not pass"
        return True, f"script {script_name} cached pass at {cached.get('timestamp', '?')}"

    return _checker


def _check_all_gates_green(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
    if "all_gates_green" in asserted:
        return True, "asserted"
    steps = state.get("steps", {})
    if not steps:
        return False, "no steps recorded yet"
    failed = [name for name, data in steps.items() if data.get("status") != "passed"]
    if failed:
        return False, f"non-passed steps: {', '.join(failed)}"
    return True, f"{len(steps)} step(s) passed"


def _operator_asserted(condition_label: str):
    """Build a checker that only passes if the operator explicitly asserts it."""

    def _checker(state: dict, lean_dir: Path, asserted: set[str]) -> tuple[bool, str]:
        if condition_label in asserted:
            return True, "operator-asserted"
        return False, f"manual condition '{condition_label}' not asserted (use --assert)"

    return _checker


CONDITION_CHECKERS: dict[str, "callable[[dict, Path, set[str]], tuple[bool, str]]"] = {
    # Auto-verifiable from the live source tree.
    "build_passes": _check_lake_build,
    "no_sorry": _check_no_sorry,
    "zero_sorry": _check_zero_sorry,
    "axiom_audit_clean": _check_zero_axiom,
    "autoImplicit_false": _check_auto_implicit_false,
    "proofs_compile": _check_lake_build,
    # Derivable from previously-recorded workflow state.
    "pre_check_passed": _check_step_passed("pre_check"),
    "all_gates_green": _check_all_gates_green,
    "metrics_in_sync": _check_cached_script("metric_sync.py"),
    "enforce_all_strict_passes": _check_cached_script("enforce_all.sh"),
    # Operator-asserted (require an explicit `--assert NAME`).
    "all_members_voted": _operator_asserted("all_members_voted"),
    "split_vote_detected": _operator_asserted("split_vote_detected"),
    "decision_recorded": _operator_asserted("decision_recorded"),
    "session_report_written": _operator_asserted("session_report_written"),
    "recon_report_generated": _operator_asserted("recon_report_generated"),
    "wave_schedule_defined": _operator_asserted("wave_schedule_defined"),
    "priorities_assigned": _operator_asserted("priorities_assigned"),
    "all_waves_reviewed": _operator_asserted("all_waves_reviewed"),
    "coverage_above_80": _operator_asserted("coverage_above_80"),
    "100_percent_review_coverage": _operator_asserted("100_percent_review_coverage"),
    "paper_section_identified": _operator_asserted("paper_section_identified"),
    "requirements_documented": _operator_asserted("requirements_documented"),
    "lean_signature_defined": _operator_asserted("lean_signature_defined"),
    "proof_strategy_chosen": _operator_asserted("proof_strategy_chosen"),
    "docstring_written": _operator_asserted("docstring_written"),
    "module_placement_decided": _operator_asserted("module_placement_decided"),
    "council_vote_passed": _operator_asserted("council_vote_passed"),
    "paper_section_read": _operator_asserted("paper_section_read"),
    "claims_documented": _operator_asserted("claims_documented"),
    "lean_signatures_defined": _operator_asserted("lean_signatures_defined"),
    "research_complete": _operator_asserted("research_complete"),
    "council_approved": _operator_asserted("council_approved"),
    "coverage_updated": _operator_asserted("coverage_updated"),
    "changes_cataloged": _operator_asserted("changes_cataloged"),
    "patches_generated": _operator_asserted("patches_generated"),
    "patches_reviewed": _operator_asserted("patches_reviewed"),
}


def evaluate_conditions(
    conditions: list[str],
    state: dict,
    lean_dir: Path,
    asserted: set[str],
) -> tuple[list[str], list[str]]:
    """Evaluate a gate's `required_conditions` and return (passes, failures)."""
    passes: list[str] = []
    failures: list[str] = []
    for condition in conditions:
        checker = CONDITION_CHECKERS.get(condition)
        if checker is None:
            failures.append(f"unknown condition '{condition}' (no checker registered)")
            continue
        try:
            ok, reason = checker(state, lean_dir, asserted)
        except Exception as exc:  # pragma: no cover — defensive
            failures.append(f"condition '{condition}' raised: {exc}")
            continue
        msg = f"{condition}: {reason}"
        if ok:
            passes.append(msg)
        else:
            failures.append(f"condition not satisfied — {msg}")
    return passes, failures


# ═══════════════════════════════════════════════════════════════
# Gate Definitions — the single source of truth
# ═══════════════════════════════════════════════════════════════

WORKFLOWS = {
    "council_review": {
        "description": "5-member review council session (Star/Pipeline/Ring/Swarm/Hub-Spoke topology)",
        "steps": ["pre_check", "dispatch_members", "collect_votes", "sdr", "close_session"],
        "gates": {
            "pre_check": {
                "description": "Mandatory pre-review enforcement gate",
                "required_scripts": ["council_precheck.sh"],
                "required_conditions": ["build_passes", "no_sorry", "autoImplicit_false"],
                "blocks": True,
                "max_stale_minutes": 30,
            },
            "dispatch_members": {
                "description": "Dispatch 5 council members",
                "requires_steps": ["pre_check"],
                "required_conditions": ["pre_check_passed"],
                "blocks": True,
            },
            "collect_votes": {
                "description": "Collect and tally votes from all members",
                "requires_steps": ["dispatch_members"],
                "required_conditions": ["all_members_voted"],
                "blocks": True,
            },
            "sdr": {
                "description": "Structured Disagreement Resolution (only if split vote)",
                "requires_steps": ["collect_votes"],
                "required_conditions": ["split_vote_detected"],
                "blocks": False,
                "conditional": True,
            },
            "close_session": {
                "description": "Finalize session report and update tracking",
                "requires_steps": ["collect_votes"],
                "required_conditions": ["decision_recorded", "session_report_written"],
                "blocks": True,
            },
        },
    },
    "retro_audit": {
        "description": "RETRO 5-phase retroactive audit (SK-35)",
        "steps": ["recon", "establish", "triage", "review", "onboard"],
        "gates": {
            "recon": {
                "description": "Phase R: Reconnaissance — automated census and dependency graph",
                "required_scripts": ["retro_recon.py"],
                "required_conditions": ["recon_report_generated"],
                "blocks": True,
            },
            "establish": {
                "description": "Phase E: Establish baselines per wave",
                "requires_steps": ["recon"],
                "required_scripts": ["council_precheck.sh", "axiom_audit.py"],
                "required_conditions": ["wave_schedule_defined"],
                "blocks": True,
            },
            "triage": {
                "description": "Phase T: Priority assignment for findings",
                "requires_steps": ["establish"],
                "required_scripts": ["proof_quality.py"],
                "required_conditions": ["priorities_assigned"],
                "blocks": True,
            },
            "review": {
                "description": "Phase R: Per-wave council reviews and fixes",
                "requires_steps": ["triage"],
                "required_scripts": ["review_coverage.py"],
                "required_conditions": ["all_waves_reviewed"],
                "blocks": True,
            },
            "onboard": {
                "description": "Phase O: Graduation gate — enforce_all.sh --strict",
                "requires_steps": ["review"],
                "required_scripts": ["enforce_all.sh --strict"],
                "required_conditions": ["enforce_all_strict_passes"],
                "blocks": True,
            },
        },
    },
    "milestone": {
        "description": "Project milestone release gate",
        "steps": ["pre_milestone", "council_review_all", "metric_sync", "release"],
        "gates": {
            "pre_milestone": {
                "description": "Run full enforcement pipeline in strict mode",
                "required_scripts": ["enforce_all.sh --strict"],
                "required_conditions": ["zero_sorry", "axiom_audit_clean", "coverage_above_80"],
                "blocks": True,
            },
            "council_review_all": {
                "description": "All modules reviewed by council",
                "requires_steps": ["pre_milestone"],
                "required_scripts": ["review_coverage.py"],
                "required_conditions": ["100_percent_review_coverage"],
                "blocks": True,
            },
            "metric_sync": {
                "description": "Paper metrics match code metrics",
                "requires_steps": ["council_review_all"],
                "required_scripts": ["metric_sync.py"],
                "required_conditions": ["metrics_in_sync"],
                "blocks": True,
            },
            "release": {
                "description": "Final release sign-off",
                "requires_steps": ["pre_milestone", "council_review_all", "metric_sync"],
                "required_conditions": ["all_gates_green"],
                "blocks": True,
            },
        },
    },
    "spec_lifecycle": {
        "description": "Specification lifecycle: requirements → design → documentation",
        "steps": ["requirements", "design", "documentation", "approval"],
        "gates": {
            "requirements": {
                "description": "Extract and document requirements from paper",
                "required_conditions": ["paper_section_identified", "requirements_documented"],
                "blocks": True,
            },
            "design": {
                "description": "Design Lean signature and proof strategy",
                "requires_steps": ["requirements"],
                "required_conditions": ["lean_signature_defined", "proof_strategy_chosen"],
                "blocks": True,
            },
            "documentation": {
                "description": "Document theorem purpose, placement, and ZK links",
                "requires_steps": ["design"],
                "required_conditions": ["docstring_written", "module_placement_decided"],
                "blocks": False,
            },
            "approval": {
                "description": "Council approves specification",
                "requires_steps": ["requirements", "design"],
                "required_conditions": ["council_vote_passed"],
                "blocks": True,
            },
        },
    },
    "forward_sync": {
        "description": "Document → Lean forward pipeline",
        "steps": ["extract_claims", "specify", "research", "implement", "review", "index"],
        "gates": {
            "extract_claims": {
                "description": "Extract claims from paper into REQ documents",
                "required_conditions": ["paper_section_read", "claims_documented"],
                "blocks": True,
            },
            "specify": {
                "description": "Write Lean theorem specifications",
                "requires_steps": ["extract_claims"],
                "required_conditions": ["lean_signatures_defined"],
                "blocks": True,
            },
            "research": {
                "description": "Research proof strategies and Mathlib coverage",
                "requires_steps": ["specify"],
                "required_conditions": ["research_complete"],
                "blocks": False,
            },
            "implement": {
                "description": "Write Lean proofs",
                "requires_steps": ["specify"],
                "required_scripts": ["council_precheck.sh"],
                "required_conditions": ["proofs_compile"],
                "blocks": True,
            },
            "review": {
                "description": "Council reviews proofs",
                "requires_steps": ["implement"],
                "required_scripts": ["council_precheck.sh"],
                "required_conditions": ["council_approved"],
                "blocks": True,
            },
            "index": {
                "description": "Update coverage matrix and ZK index",
                "requires_steps": ["review"],
                "required_scripts": ["review_coverage.py"],
                "required_conditions": ["coverage_updated"],
                "blocks": False,
            },
        },
    },
    "backward_sync": {
        "description": "Lean → Document backward pipeline",
        "steps": ["detect_changes", "generate_patches", "apply_patches", "verify_sync"],
        "gates": {
            "detect_changes": {
                "description": "Detect Lean changes that affect paper claims",
                "required_scripts": ["metric_sync.py"],
                "required_conditions": ["changes_cataloged"],
                "blocks": True,
            },
            "generate_patches": {
                "description": "Generate paper update suggestions",
                "requires_steps": ["detect_changes"],
                "required_conditions": ["patches_generated"],
                "blocks": True,
            },
            "apply_patches": {
                "description": "Apply patches to paper (human review required)",
                "requires_steps": ["generate_patches"],
                "required_conditions": ["patches_reviewed"],
                "blocks": True,
            },
            "verify_sync": {
                "description": "Verify paper and code are back in sync",
                "requires_steps": ["apply_patches"],
                "required_scripts": ["metric_sync.py"],
                "required_conditions": ["metrics_in_sync"],
                "blocks": True,
            },
        },
    },
}

# ═══════════════════════════════════════════════════════════════
# State Management
# ═══════════════════════════════════════════════════════════════


def get_state_file(workflow: str, session_id: str) -> Path:
    return STATE_DIR / f"{workflow}_{session_id}.json"


def load_state(workflow: str, session_id: str) -> dict:
    path = get_state_file(workflow, session_id)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {
        "workflow": workflow,
        "session_id": session_id,
        "created": datetime.now(UTC).isoformat(),
        "steps": {},
        "script_results": {},
    }


def save_state(state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = get_state_file(state["workflow"], state["session_id"])
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


# ═══════════════════════════════════════════════════════════════
# Gate Checking
# ═══════════════════════════════════════════════════════════════


def run_required_script(script_spec: str, lean_dir: Path) -> tuple[bool, str]:
    """Run a required script and return (passed, output)."""
    parts = script_spec.split()
    script_name = parts[0]
    extra_args = parts[1:]

    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        return False, f"Script not found: {script_path}"

    cmd = []
    if script_name.endswith(".sh"):
        cmd = ["bash", str(script_path), str(lean_dir), *extra_args]
    elif script_name.endswith(".py"):
        cmd = [sys.executable, str(script_path), "--lean-dir", str(lean_dir), *extra_args]
    else:
        return False, f"Unknown script type: {script_name}"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(lean_dir.resolve().parent if lean_dir.is_dir() else Path.cwd()),
        )
        passed = result.returncode == 0
        output = result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
        if result.stderr:
            output += "\n" + (result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        return passed, output
    except subprocess.TimeoutExpired:
        return False, f"Script timed out after 300s: {script_spec}"
    except Exception as e:
        return False, f"Script execution error: {e}"


def check_prerequisite_steps(workflow_def: dict, step: str, state: dict) -> list[str]:
    """Check that all prerequisite steps have been completed."""
    gate = workflow_def["gates"][step]
    failures = []

    for prereq in gate.get("requires_steps", []):
        step_state = state["steps"].get(prereq, {})
        if step_state.get("status") != "passed":
            failures.append(
                f"Prerequisite step '{prereq}' not completed (status: {step_state.get('status', 'not_run')})"
            )

    return failures


def check_script_staleness(state: dict, script_name: str, max_stale_minutes: int) -> bool:
    """Check if a script result is still fresh enough."""
    result = state.get("script_results", {}).get(script_name, {})
    if not result:
        return False  # never run = stale

    run_time = result.get("timestamp")
    if not run_time:
        return False

    try:
        run_dt = datetime.fromisoformat(run_time)
        now = datetime.now(UTC)
        age_minutes = (now - run_dt).total_seconds() / 60
        return age_minutes <= max_stale_minutes
    except (ValueError, TypeError):
        return False


def check_gate(
    workflow: str,
    step: str,
    lean_dir: Path,
    session_id: str,
    dry_run: bool = False,
    asserted: set[str] | None = None,
) -> tuple[bool, list[str], list[str]]:
    """
    Check if a workflow gate permits proceeding.
    Returns (passed, failures, warnings).
    """
    if workflow not in WORKFLOWS:
        return False, [f"Unknown workflow: {workflow}"], []

    wf = WORKFLOWS[workflow]

    if step not in wf["gates"]:
        return False, [f"Unknown step '{step}' in workflow '{workflow}'"], []

    gate = wf["gates"][step]
    state = load_state(workflow, session_id)
    asserted = asserted or set()
    failures = []
    warnings = []

    # 1. Check prerequisite steps
    prereq_failures = check_prerequisite_steps(wf, step, state)
    failures.extend(prereq_failures)

    # 2. Run required scripts (unless dry_run)
    for script_spec in gate.get("required_scripts", []):
        script_name = script_spec.split()[0]
        max_stale = gate.get("max_stale_minutes", 30)

        # Check if we have a fresh result
        if check_script_staleness(state, script_name, max_stale):
            cached = state["script_results"][script_name]
            if not cached.get("passed"):
                failures.append(f"Script '{script_spec}' failed (cached result)")
            continue

        if dry_run:
            warnings.append(f"Script '{script_spec}' would be run (dry-run mode)")
            continue

        passed, output = run_required_script(script_spec, lean_dir)

        # Record result
        state.setdefault("script_results", {})[script_name] = {
            "passed": passed,
            "timestamp": datetime.now(UTC).isoformat(),
            "output_tail": output[-500:] if output else "",
        }
        save_state(state)

        if not passed:
            failures.append(f"Script '{script_spec}' failed:\n  {output[:200]}")

    # 2b. Evaluate `required_conditions` (Wave 9 HITL C241, 2026-04-29).
    # Previously this metadata was declared but never executed.  We now resolve
    # each named condition through CONDITION_CHECKERS and treat unsatisfied
    # conditions as gate failures.
    condition_passes: list[str] = []
    if dry_run:
        for cond in gate.get("required_conditions", []):
            warnings.append(f"Condition '{cond}' would be evaluated (dry-run mode)")
    else:
        condition_passes, condition_failures = evaluate_conditions(
            gate.get("required_conditions", []),
            state,
            lean_dir,
            asserted,
        )
        failures.extend(condition_failures)

    # 3. Record step attempt
    if not dry_run:
        step_passed = len(failures) == 0
        state["steps"][step] = {
            "status": "passed" if step_passed else "blocked",
            "timestamp": datetime.now(UTC).isoformat(),
            "failures": failures,
            "warnings": warnings,
            "condition_passes": condition_passes,
            "asserted_conditions": sorted(asserted),
        }
        save_state(state)

    return len(failures) == 0, failures, warnings


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════


def list_workflows():
    print("Available workflows:\n")
    for name, wf in WORKFLOWS.items():
        print(f"  {name}")
        print(f"    {wf['description']}")
        print(f"    Steps: {' → '.join(wf['steps'])}")
        blocking = [s for s, g in wf["gates"].items() if g.get("blocks")]
        print(f"    Blocking gates: {', '.join(blocking)}")
        print()


def show_status(workflow: str | None):
    if not STATE_DIR.exists():
        print("No workflow state found.")
        return

    for state_file in sorted(STATE_DIR.glob("*.json")):
        with open(state_file) as f:
            state = json.load(f)

        if workflow and state.get("workflow") != workflow:
            continue

        print(f"Workflow: {state['workflow']} | Session: {state['session_id']}")
        print(f"  Created: {state.get('created', 'unknown')}")

        for step_name, step_data in state.get("steps", {}).items():
            status = step_data.get("status", "unknown")
            symbol = "✓" if status == "passed" else "✗" if status == "blocked" else "?"
            print(f"  {symbol} {step_name}: {status}")
            if step_data.get("failures"):
                for f in step_data["failures"][:3]:
                    print(f"      ✗ {f[:80]}")

        for script_name, result in state.get("script_results", {}).items():
            symbol = "✓" if result.get("passed") else "✗"
            print(
                f"  Script {symbol} {script_name}: {'passed' if result.get('passed') else 'failed'} @ {result.get('timestamp', '?')}"
            )
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Workflow Gate Enforcer — validates mandatory gates before workflow steps proceed"
    )
    parser.add_argument("--workflow", type=str, help="Workflow name")
    parser.add_argument("--step", type=str, help="Step to check gate for")
    parser.add_argument(
        "--session-id",
        type=str,
        default=datetime.now(UTC).strftime("%Y%m%d"),
        help="Session identifier (default: today's date)",
    )
    parser.add_argument(
        "--lean-dir", type=Path, default=Path("EASCI"), help="Path to Lean source directory"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Check gates without running scripts"
    )
    parser.add_argument(
        "--assert",
        dest="assert_conditions",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Operator-asserted condition name (repeatable).  Used for "
            "manual conditions such as 'all_members_voted' that the gate "
            "evaluator cannot verify automatically."
        ),
    )
    parser.add_argument(
        "--list-workflows", action="store_true", help="List all available workflows"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show status of active workflow sessions"
    )

    args = parser.parse_args()

    if args.list_workflows:
        list_workflows()
        sys.exit(0)

    if args.status:
        show_status(args.workflow)
        sys.exit(0)

    if not args.workflow or not args.step:
        parser.error("--workflow and --step are required (or use --list-workflows / --status)")

    passed, failures, warnings = check_gate(
        args.workflow,
        args.step,
        args.lean_dir,
        args.session_id,
        dry_run=args.dry_run,
        asserted=set(args.assert_conditions),
    )

    # Output
    wf = WORKFLOWS.get(args.workflow, {})
    gate = wf.get("gates", {}).get(args.step, {})

    if passed:
        print(f"✓ GATE PASSED: {args.workflow}/{args.step}")
        if warnings:
            for w in warnings:
                print(f"  ⚠ {w}")
        sys.exit(0)
    else:
        is_blocking = gate.get("blocks", True)
        if is_blocking:
            print(f"✗ GATE BLOCKED: {args.workflow}/{args.step}")
        else:
            print(f"⚠ GATE WARNING: {args.workflow}/{args.step} (non-blocking)")

        for f in failures:
            print(f"  ✗ {f}")
        for w in warnings:
            print(f"  ⚠ {w}")

        sys.exit(1 if is_blocking else 0)


if __name__ == "__main__":
    main()
