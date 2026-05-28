#!/usr/bin/env python3
"""Per-rubric Glicko-2 ELO computation.

Splits a live-matches CSV into buckets by `ensemble_rubric` (read from
each case's YAML in --cases), then runs Glicko-2 on each bucket
independently. Writes one sub-directory per rubric:

    <out>/
      <rubric>-matches.csv
      <rubric>/
        ratings.json
        leaderboard.md
      per-rubric-summary.md

Used by:
- R25 item 4 (per-rubric ELO split)
- CI `eval-smoke.yml :: glicko2 :: Per-rubric ELO regression gate`
  (paired with `check_per_rubric_regression.py`).

Usage:
    python3 scripts/elo/per_rubric_elo.py \
        --matches scripts/elo/matches/2026-05-27-live.csv \
        --cases   scripts/eval/cases \
        --out     scripts/elo/example_runs/2026-05-27-x-per-rubric/
"""
from __future__ import annotations
import argparse, csv, json, subprocess, sys
from pathlib import Path
from collections import defaultdict

try:
    import yaml
except ImportError:
    sys.exit("per_rubric_elo.py requires PyYAML")

HERE = Path(__file__).resolve().parent


def load_rubricmap(cases_dir: Path) -> dict[str, str]:
    """Read every case YAML in cases_dir and build {case_id -> rubric}."""
    rmap: dict[str, str] = {}
    for cy in sorted(cases_dir.glob("*.yaml")):
        try:
            docs = list(yaml.safe_load_all(cy.read_text()))
        except Exception:
            continue
        if not docs:
            continue
        d = docs[0]
        case = d.get("id")
        if not case:
            continue
        rubric = d.get("ensemble_rubric")
        if not rubric:
            skill = d.get("skill") or ""
            if skill.startswith("lean-") and "doc" in skill:
                rubric = "lean-doc-quality"
            elif skill.startswith(("ai-", "applied-", "math-")):
                rubric = "applied-domain-quality"
            else:
                rubric = "lean-proof-quality"
        rmap[case] = rubric
    return rmap


def rubric_for(case_id: str, rmap: dict[str, str]) -> str:
    if case_id in rmap:
        return rmap[case_id]
    if case_id.startswith("lean-doc"):
        return "lean-doc-quality"
    if case_id.startswith("lean-tactic-discipline"):
        return "lean-tactic-discipline-quality"
    if case_id.startswith("lean-"):
        return "lean-proof-quality"
    return "applied-domain-quality"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--matches", type=Path, required=True,
                   help="path to live matches CSV")
    p.add_argument("--cases", type=Path, required=True,
                   help="directory of case YAMLs (for rubric discovery)")
    p.add_argument("--out", type=Path, required=True,
                   help="output directory; one subdir per rubric will be written")
    args = p.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    rmap = load_rubricmap(args.cases)

    buckets: dict[str, list[dict]] = defaultdict(list)
    with args.matches.open(newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            buckets[rubric_for(row["case_id"], rmap)].append(row)

    summary_lines = [
        "# Per-rubric Glicko-2 leaderboards",
        "",
        f"Source: {args.matches} "
        f"({sum(len(v) for v in buckets.values())} rows total)",
        f"Buckets: {len(buckets)} rubric(s)",
        "",
    ]
    glicko = HERE / "glicko2.py"

    for rubric in sorted(buckets):
        rows = buckets[rubric]
        rubric_csv = args.out / f"{rubric}-matches.csv"
        with rubric_csv.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        out_dir = args.out / rubric
        out_dir.mkdir(exist_ok=True)
        subprocess.run([
            sys.executable, str(glicko),
            "--matches", str(rubric_csv),
            "--out", str(out_dir),
        ], check=True, capture_output=True)
        ratings = json.loads((out_dir / "ratings.json").read_text())["players"]
        summary_lines.append(f"## {rubric} ({len(rows)} rows)")
        summary_lines.append("")
        summary_lines.append("| Rank | Player | Rating | RD | Games |")
        summary_lines.append("|---|---|---:|---:|---:|")
        for i, (pid, r) in enumerate(
            sorted(ratings.items(), key=lambda kv: -kv[1]["rating"]), 1
        ):
            summary_lines.append(
                f"| {i} | `{pid}` | {r['rating']:.1f} | {r['rd']:.1f} | {r['games']} |"
            )
        summary_lines.append("")

    (args.out / "per-rubric-summary.md").write_text("\n".join(summary_lines))
    print(f"wrote {args.out / 'per-rubric-summary.md'}")
    print(f"buckets: { {k: len(v) for k, v in buckets.items()} }")
    return 0


if __name__ == "__main__":
    sys.exit(main())
