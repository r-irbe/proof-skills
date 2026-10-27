#!/usr/bin/env python3
"""Unified CLI entrypoint for lean-altproof (`altproof <subcommand>`).

Supports:
  - altproof detect-v4 <file.lean> [--trace-root DIR] [--source-rel REL]
  - altproof dispatch [--goal GOAL] [--proof PROOF] [--self-test]
  - altproof rank [--lines N] [--shared-lemmas K] [--upstream] [--kernel-cost S]
  - altproof cluster <root_dir> [out_report.md]
  - altproof extract <file.lean> [--theorem NAME]
  - altproof report <sandbox_dir> <out_dir>
  - altproof routes [--json | --regen]

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


SUBCOMMANDS = (
    "detect-v4",
    "dispatch",
    "rank",
    "cluster",
    "extract",
    "report",
    "routes",
    "legibility",
    "axiom-profiles",
)


def _cmd_rank(argv: list[str]) -> int:
    from cost_ranker import Weights, cost, leanprogress_scorer

    parser = argparse.ArgumentParser(
        prog="altproof rank",
        description="Compute two-axis AltProof elegance & kernel cost score",
    )
    parser.add_argument("--lines", type=float, default=10.0, help="Proof line count")
    parser.add_argument("--shared-lemmas", type=int, default=0, help="Extracted shared lemmas")
    parser.add_argument("--upstream", action="store_true", help="Mathlib-absent upstreamable bonus")
    parser.add_argument("--kernel-cost", type=float, default=0.0, help="Kernel cost in seconds / 1000-hb units")
    parser.add_argument("--goal", default="", help="Optional goal state for LeanProgress progress estimate")
    args = parser.parse_args(argv)

    w = Weights()
    score = cost(
        lines=args.lines,
        shared_lemmas=args.shared_lemmas,
        upstream=args.upstream,
        w=w,
        kernel_cost=args.kernel_cost,
    )
    out: dict = {
        "lines": args.lines,
        "shared_lemmas": args.shared_lemmas,
        "upstream": args.upstream,
        "kernel_cost": args.kernel_cost,
        "cost": round(score, 4),
        "cost_x10": round(score * 10),
    }
    if args.goal:
        out["leanprogress_score"] = round(leanprogress_scorer(args.goal), 4)
    print(json.dumps(out, indent=2))
    return 0


def _cmd_extract(argv: list[str]) -> int:
    from extraction_detector import detect_v3, module_symbols

    parser = argparse.ArgumentParser(
        prog="altproof extract",
        description="Run v3 extraction detector on a Lean 4 file or proof block",
    )
    parser.add_argument("file", type=Path, help="Path to .lean file")
    parser.add_argument("--theorem", default="", help="Optional theorem name label")
    args = parser.parse_args(argv)

    source = args.file.read_text(encoding="utf-8")
    syms = module_symbols(source)
    cands = detect_v3(source, theorem=args.theorem or args.file.stem, file_symbols=syms)
    out = [
        {
            "theorem": c.theorem,
            "route": c.route,
            "kind": c.kind,
            "evidence": c.evidence,
            "occurrences": c.occurrences,
            "estimated_lines_saved": c.estimated_lines_saved,
        }
        for c in cands
    ]
    print(json.dumps({"count": len(out), "candidates": out}, indent=2))
    return 0


def _cmd_routes(argv: list[str]) -> int:
    import gen_route_table
    from route_definitions import ROUTES

    parser = argparse.ArgumentParser(
        prog="altproof routes",
        description="Inspect or regenerate the canonical AltProof 11-route table",
    )
    parser.add_argument("--regen", action="store_true", help="Regenerate route-table.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON route table payload")
    args = parser.parse_args(argv)

    if args.regen:
        return gen_route_table.main()
    if args.json:
        print(json.dumps(gen_route_table.generate(), indent=2, sort_keys=True))
        return 0
    print(json.dumps({"total": len(ROUTES), "routes": ROUTES}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help", "help"):
        print("usage: altproof <subcommand> [args]\n")
        print("subcommands:")
        print("  detect-v4       Run .ilean / TraceIndex S2+S3 extraction detector on a Lean file")
        print("  dispatch        Run AltProof tactic advisor and two-axis legibility scorer")
        print("  rank            Compute two-axis B1 extraction-outranks + SAIR kernel cost")
        print("  cluster         Run cross-theorem have-clustering (S5) over a Lean directory")
        print("  extract         Run v3 extraction detector on a Lean file")
        print("  report          Render whole-corpus elegance Markdown report suite")
        print("  routes          Inspect or regenerate the 11-route AltProof table")
        print("  legibility      Score proof block legibility and structural golf opportunities")
        print("  axiom-profiles  Audit declaration axiom profiles")
        return 0

    cmd = args[0]
    rest = args[1:]

    if cmd in ("detect-v4", "detect_v4"):
        import detect_v4
        return detect_v4.main(rest)
    if cmd in ("dispatch", "tactic-dispatcher", "tactic_dispatcher"):
        import tactic_dispatcher
        return tactic_dispatcher._cli_main(rest)
    if cmd in ("rank", "cost-ranker", "cost_ranker"):
        return _cmd_rank(rest)
    if cmd in ("cluster", "have-cluster", "have_cluster"):
        import have_cluster
        if not rest or rest[0] in ("-h", "--help"):
            print("usage: altproof cluster <root_dir> [out_report.md]")
            return 0
        return have_cluster.main(["have_cluster.py"] + rest)
    if cmd in ("extract", "extraction-detector", "extraction_detector"):
        return _cmd_extract(rest)
    if cmd in ("report", "corpus-report", "corpus_report"):
        if len(rest) < 2 or rest[0] in ("-h", "--help"):
            print("usage: altproof report <sandbox_dir> <out_dir>")
            return 0 if (rest and rest[0] in ("-h", "--help")) else 2
        return subprocess.call([sys.executable, str(HERE / "corpus_report.py")] + rest)
    if cmd in ("routes", "route-table", "route_table"):
        return _cmd_routes(rest)
    if cmd == "legibility":
        import legibility
        if not rest or rest[0] in ("-h", "--help"):
            print("usage: altproof legibility <file.lean>")
            return 0
        return legibility.main(["legibility.py"] + rest)
    if cmd in ("axiom-profiles", "axiom_profiles"):
        import axiom_profiles
        return axiom_profiles.main(rest)

    mod_path = HERE / (cmd.replace("-", "_") + ".py")
    if mod_path.exists():
        return subprocess.call([sys.executable, str(mod_path)] + rest)

    print(f"unknown altproof subcommand: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
