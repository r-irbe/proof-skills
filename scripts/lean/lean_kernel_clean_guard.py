#!/usr/bin/env python3
"""scripts/lean/lean_kernel_clean_guard.py

Kernel-Clean Axiom Guard for Lean 4 Formal Proofs.
Adapted from algos/lean/verify.py.
Enforces strict allowlist: {propext, Classical.choice, Quot.sound}.
Strictly rejects sorryAx, Lean.ofReduceBool (native_decide), and untracked axioms.
Strict 7-bit ASCII only (INV-001).
"""

import argparse
import json
import re
import sys

KERNEL_CLEAN_ALLOWLIST: set[str] = {"propext", "Classical.choice", "Quot.sound"}

BANNED_AXIOMS: set[str] = {"sorryAx", "Lean.ofReduceBool", "Lean.reduceBool"}


def parse_axiom_lines(text: str) -> set[str]:
    """Extract the axiom identifiers from Lean 4 `#print axioms` output.

    The real output is one line per declaration:

        'name' depends on axioms: [propext, Classical.choice, Quot.sound]
        'name' does not depend on any axioms

    The previous parse split every line into tokens and kept whatever was not
    bracketed, which collected each declaration's *own name* as though it were an
    axiom: a clean module was reported as introducing `convexComb_between` and
    `phase_refines_cynefin` as non-allowlisted axioms. Its test passed because it fed
    the parser a format `#print axioms` never produces -- bare names on separate
    lines -- so the instrument was measuring its own fiction, and the seven Lean
    packages went un-gated partly because the gate did not work.

    Only what the brackets contain is read, across line breaks, because a long
    dependency list wraps.
    """
    axioms: set[str] = set()
    for match in re.finditer(r"\[([^\]]*)\]", text):
        for name in match.group(1).split(","):
            name = name.strip().strip("'\"`")
            if name:
                axioms.add(name)
    return axioms


def verify_module_axioms(
    module_name: str, axioms: set[str], allowlist: set[str] | None = None
) -> tuple[bool, list[str]]:
    """Verifies that axioms for a given module strictly conform to the allowlist."""
    effective_allowlist = allowlist if allowlist is not None else KERNEL_CLEAN_ALLOWLIST
    violations = []

    for ax in axioms:
        if ax in BANNED_AXIOMS:
            violations.append(f"Module '{module_name}' uses banned shortcut axiom '{ax}'")
        elif ax not in effective_allowlist:
            violations.append(f"Module '{module_name}' introduces non-allowlisted axiom '{ax}'")

    is_clean = len(violations) == 0
    return is_clean, violations


def audit_axiom_manifest(
    manifest: dict[str, list[str]], allowlist: set[str] | None = None
) -> tuple[bool, list[str]]:
    """Audits a dictionary of {module_name: [axioms]} against the kernel-clean policy."""
    all_clean = True
    all_violations = []

    for mod, ax_list in manifest.items():
        is_clean, violations = verify_module_axioms(mod, set(ax_list), allowlist)
        if not is_clean:
            all_clean = False
            all_violations.extend(violations)

    return all_clean, all_violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Lean 4 axiom prints against kernel-clean allowlist."
    )
    parser.add_argument(
        "--file", "-f", help="JSON manifest of module to axioms mapping, or raw text file."
    )
    parser.add_argument("--json", action="store_true", help="Treat input file as JSON manifest.")
    parser.add_argument(
        "--strict", action="store_true", help="Strict mode: reject any axioms outside minimal set."
    )
    args = parser.parse_args()

    if not args.file:
        raw = sys.stdin.read()
    else:
        with open(args.file, encoding="ascii", errors="replace") as f:
            raw = f.read()

    if args.json or (args.file and args.file.endswith(".json")):
        try:
            data = json.loads(raw)
        except Exception as e:
            print(f"ERROR: Failed to parse JSON input: {e}", file=sys.stderr)
            return 2

        # Format can be {module: [axioms]} or list of dicts
        manifest = {}
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list):
                    manifest[k] = v
                elif isinstance(v, dict) and "axioms" in v:
                    manifest[k] = v["axioms"]
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "module" in item and "axioms" in item:
                    manifest[item["module"]] = item["axioms"]

        clean, violations = audit_axiom_manifest(manifest)
    else:
        axioms = parse_axiom_lines(raw)
        clean, violations = verify_module_axioms("stdin_stream", axioms)

    if clean:
        print("PASS: Kernel-clean verification passed. All axioms conform to standard foundation.")
        return 0
    else:
        print("FAIL: Kernel-clean verification failed with violations:")
        for v in violations:
            print(f"  - {v}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
