#!/usr/bin/env python3
"""Unified `lean-skills` CLI: dispatches to scripts/lean tools. ASCII only."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALIASES = {"sentinel": "variable_scope_sentinel", "axiom-diff": "axiom_diff",
           "simp-diff": "simp_diff", "lake-diff": "lake_timer_diff",
           "sync": "workspace_sync", "drift": "workspace_drift",
           "receipts": "gen_receipts", "config": "project_config"}


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help", "list"):
        print("usage: lean-skills <tool> [args]\ntools:")
        for k in sorted(ALIASES):
            print("  %-10s -> %s" % (k, ALIASES[k]))
        return 0
    name = ALIASES.get(argv[1], argv[1])
    for ext, cmd in ((".py", [sys.executable]), (".sh", ["bash"])):
        p = HERE / (name + ext)
        if p.exists():
            return subprocess.call(cmd + [str(p)] + argv[2:])
    print("unknown tool: " + argv[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
