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
}


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help", "list"):
        print("usage: lean-skills <tool> [args]\ntools:")
        for k in sorted(ALIASES):
            print("  %-16s -> %s" % (k, ALIASES[k]))
        print("  %-16s -> %s" % ("altproof <mod>", "altproof/<mod>.py"))
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
    name = ALIASES.get(argv[1], argv[1].replace("-", "_"))
    for ext, cmd in ((".py", [sys.executable]), (".sh", ["bash"])):
        p = HERE / (name + ext)
        if p.exists():
            return subprocess.call(cmd + [str(p)] + argv[2:])
    p_alt = HERE / "altproof" / (name + ".py")
    if p_alt.exists():
        return subprocess.call([sys.executable, str(p_alt)] + argv[2:])
    print("unknown tool: " + argv[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
