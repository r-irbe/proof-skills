#!/usr/bin/env python3
"""Unified `lean-skills` CLI: dispatches to scripts/lean and altproof tools. ASCII only."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALIASES = {
    "audit": "proof_quality",
    "sentinel": "variable_scope_sentinel",
    "axioms": "axiom_audit",
    "axiom-diff": "axiom_diff",
    "axiom-trend": "axiom_trend",
    "simp": "simp_baseline",
    "simp-diff": "simp_diff",
    "lake-diff": "lake_timer_diff",
    "microbench-diff": "lake_microbench_diff",
    "blueprint": "expand_blueprint",
    "blueprint-probe": "blueprint_probe",
    "blueprint-guard": "blueprint_tex_guard",
    "sync": "workspace_sync",
    "drift": "workspace_drift",
    "receipts": "gen_receipts",
    "config": "project_config",
    "census": "census",
    "concat": "concat_corpus",
    "profile": "profile_build",
    "tautology": "tautology_scan",
    "council": "council_stv",
    "repair-proof": "apollo_repair",
    "sorry2lemma": "apollo_repair",
    "verify-statement": "verify_statement",
    "validate-patch": "verify_statement",
    "run-persist": "run_persist",
    "disprove-artifact-txn": "run_persist",
    "evolve-lemma": "lemma_evolver",
    "conjecture": "lemma_evolver",
    "check-citations": "check_citations",
    "check-validation": "check_canary_validation",
    "check-canary": "check_canary_validation",
    "detect-v4": "altproof/detect_v4",
}

FORWARD_SUBCOMMAND_TOOLS = frozenset(
    {
        "repair-proof",
        "sorry2lemma",
        "verify-statement",
        "validate-patch",
        "run-persist",
        "disprove-artifact-txn",
        "evolve-lemma",
        "conjecture",
    }
)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help", "list"):
        print("usage: lean-skills <tool> [args]\ntools:")
        for k in sorted(ALIASES):
            print("  %-22s -> %s" % (k, ALIASES[k]))
        print("  %-22s -> %s" % ("altproof <mod>", "altproof/<mod>.py"))
        return 0
    if argv[1] == "altproof":
        if len(argv) < 3:
            print("usage: lean-skills altproof <module> [args]", file=sys.stderr)
            return 2
        mod = HERE / "altproof" / (argv[2].replace("-", "_") + ".py")
        if mod.exists():
            return subprocess.call([sys.executable, str(mod)] + argv[3:])
        print("unknown altproof module: " + argv[2], file=sys.stderr)
        return 2
    subcmd = argv[1]
    name = ALIASES.get(subcmd, subcmd.replace("-", "_"))
    forwarded_args = argv[1:] if subcmd in FORWARD_SUBCOMMAND_TOOLS else argv[2:]
    for ext, cmd in ((".py", [sys.executable]), (".sh", ["bash"])):
        p = HERE / (name + ext)
        if p.exists():
            return subprocess.call(cmd + [str(p)] + forwarded_args)
    p_alt = HERE / "altproof" / (name + ".py")
    if p_alt.exists():
        return subprocess.call([sys.executable, str(p_alt)] + forwarded_args)
    print("unknown tool: " + argv[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
