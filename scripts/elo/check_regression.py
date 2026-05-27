#!/usr/bin/env python3
"""ELO regression gate.

Compares the current `ratings.json` from the latest Glicko-2 archive to the
baseline lockfile at `scripts/elo/baseline_ratings.json`. Exits non-zero if
any entrant has dropped more than ``tolerance_points`` rating points.

Usage:
    python3 scripts/elo/check_regression.py \
        --current scripts/elo/example_runs/<date>/ratings.json
    python3 scripts/elo/check_regression.py --refresh      # regenerate baseline

CI invokes:
    python3 scripts/elo/check_regression.py \
        --current scripts/elo/example_runs/$(ls scripts/elo/example_runs/ | tail -1)/ratings.json
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).parent
BASELINE = ROOT / "baseline_ratings.json"


def load_ratings(p: Path) -> dict[str, float]:
    obj = json.loads(p.read_text())
    if "players" in obj:  # glicko-2 ratings.json format
        return {k: float(v["rating"]) for k, v in obj["players"].items()}
    if "ratings" in obj:  # baseline lockfile format
        return {k: float(v) for k, v in obj["ratings"].items()}
    raise SystemExit(f"unrecognized ratings file shape: {p}")


def load_tolerance() -> float:
    return float(json.loads(BASELINE.read_text())["tolerance_points"])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--current", type=Path,
                   help="path to current ratings.json from a glicko-2 archive")
    p.add_argument("--refresh", action="store_true",
                   help="regenerate the baseline from --current (intentional update)")
    p.add_argument("--tolerance", type=float, default=None,
                   help="override tolerance points (default from baseline lockfile)")
    args = p.parse_args()

    if args.refresh:
        if not args.current:
            sys.exit("--refresh requires --current")
        cur = load_ratings(args.current)
        existing = json.loads(BASELINE.read_text())
        existing["ratings"] = cur
        existing["_meta"]["source_archive"] = str(args.current.relative_to(ROOT.parent))
        BASELINE.write_text(json.dumps(existing, indent=2) + "\n")
        print(f"baseline refreshed from {args.current} → {BASELINE.name}")
        for k, v in sorted(cur.items()):
            print(f"  {k}: {v:.2f}")
        return 0

    if not args.current:
        sys.exit("--current is required (path to glicko-2 ratings.json)")

    cur = load_ratings(args.current)
    base = load_ratings(BASELINE)
    tol = args.tolerance if args.tolerance is not None else load_tolerance()

    regressions = []
    for player, base_r in sorted(base.items()):
        if player not in cur:
            regressions.append((player, base_r, None, "MISSING"))
            continue
        cur_r = cur[player]
        delta = cur_r - base_r
        marker = "ok" if delta > -tol else "REGRESSION"
        print(f"  {player}: {base_r:.2f} → {cur_r:.2f}  Δ={delta:+.2f}  [{marker}]")
        if delta <= -tol:
            regressions.append((player, base_r, cur_r, "REGRESSION"))

    new_players = sorted(set(cur) - set(base))
    for p in new_players:
        print(f"  (new) {p}: {cur[p]:.2f}")

    if regressions:
        print(f"\nFAIL: {len(regressions)} entrant(s) regressed by > {tol} points:",
              file=sys.stderr)
        for player, b, c, kind in regressions:
            if kind == "MISSING":
                print(f"  {player}: present in baseline ({b:.2f}) but missing from current",
                      file=sys.stderr)
            else:
                print(f"  {player}: {b:.2f} → {c:.2f}  Δ={c - b:+.2f}",
                      file=sys.stderr)
        return 1

    print(f"\nOK: no regressions > {tol} points across {len(base)} baseline entrant(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
