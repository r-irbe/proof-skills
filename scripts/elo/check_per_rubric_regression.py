#!/usr/bin/env python3
"""Per-rubric ELO regression gate.

Companion to ``check_regression.py`` (which gates on the global ELO).
Reads per-rubric ratings produced by `per_rubric_elo.py` (or any equivalent
Glicko-2 archive structured as
``<archive>/<rubric>/ratings.json``) and compares each per-rubric leaderboard
against the lockfile at ``scripts/elo/baseline_ratings_per_rubric.json``.

Exits non-zero if any (rubric, entrant) drops more than tolerance_points
rating points vs the baseline.

Usage:
    python3 scripts/elo/check_per_rubric_regression.py \
        --archive scripts/elo/example_runs/<date>-r25-per-rubric/

    python3 scripts/elo/check_per_rubric_regression.py \
        --archive scripts/elo/example_runs/<date>-r25-per-rubric/ \
        --refresh        # regenerate baseline from this archive
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).parent
BASELINE = ROOT / "baseline_ratings_per_rubric.json"


def load_archive(archive_dir: Path) -> dict[str, dict[str, float]]:
    """Discover per-rubric ratings.json under archive_dir/<rubric>/ratings.json."""
    out = {}
    if not archive_dir.is_dir():
        sys.exit(f"--archive {archive_dir} is not a directory")
    for rdir in sorted(archive_dir.iterdir()):
        if not rdir.is_dir():
            continue
        rf = rdir / "ratings.json"
        if not rf.exists():
            continue
        d = json.loads(rf.read_text())
        players = d.get("players")
        if players is None:
            continue
        out[rdir.name] = {k: round(float(v["rating"]), 2)
                          for k, v in players.items()}
    if not out:
        sys.exit(f"no per-rubric ratings.json found under {archive_dir}")
    return out


def load_baseline() -> tuple[dict[str, dict[str, float]], float]:
    obj = json.loads(BASELINE.read_text())
    return obj["rubrics"], float(obj["tolerance_points"])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True,
                   help="archive dir containing <rubric>/ratings.json")
    p.add_argument("--refresh", action="store_true",
                   help="regenerate baseline from --archive (intentional update)")
    p.add_argument("--tolerance", type=float, default=None,
                   help="override tolerance points (default from baseline lockfile)")
    args = p.parse_args()

    cur = load_archive(args.archive)

    if args.refresh:
        existing = json.loads(BASELINE.read_text())
        existing["rubrics"] = cur
        existing["_meta"]["source_archive"] = str(args.archive)
        BASELINE.write_text(json.dumps(existing, indent=2) + "\n")
        print(f"baseline refreshed from {args.archive} → {BASELINE.name}")
        for r, players in cur.items():
            print(f"  {r}: {len(players)} entrants")
        return 0

    baseline, tol = load_baseline()
    if args.tolerance is not None:
        tol = args.tolerance

    regressions = []
    for rubric in sorted(set(baseline) | set(cur)):
        print(f"\n=== {rubric} ===")
        base_r = baseline.get(rubric, {})
        cur_r = cur.get(rubric, {})
        if not base_r:
            print(f"  (new rubric in current run)")
            continue
        if not cur_r:
            print(f"  MISSING from current archive", file=sys.stderr)
            regressions.append((rubric, "<rubric>", None, None, "MISSING"))
            continue
        for player, b in sorted(base_r.items()):
            if player not in cur_r:
                print(f"  {player}: present in baseline ({b:.2f}) but missing")
                regressions.append((rubric, player, b, None, "MISSING"))
                continue
            c = cur_r[player]
            delta = c - b
            marker = "ok" if delta > -tol else "REGRESSION"
            print(f"  {player}: {b:.2f} → {c:.2f}  Δ={delta:+.2f}  [{marker}]")
            if delta <= -tol:
                regressions.append((rubric, player, b, c, "REGRESSION"))

    if regressions:
        print(f"\nFAIL: {len(regressions)} per-rubric regression(s) "
              f"> {tol} points:", file=sys.stderr)
        for rubric, player, b, c, kind in regressions:
            if kind == "MISSING":
                desc = f"present in baseline but missing"
                if b is not None:
                    desc = f"baseline {b:.2f}; {desc}"
                print(f"  [{rubric}] {player}: {desc}", file=sys.stderr)
            else:
                print(f"  [{rubric}] {player}: {b:.2f} → {c:.2f}  Δ={c-b:+.2f}",
                      file=sys.stderr)
        return 1

    total = sum(len(v) for v in baseline.values())
    print(f"\nOK: no per-rubric regressions > {tol} pts across "
          f"{len(baseline)} rubric(s) / {total} (rubric, entrant) pair(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
