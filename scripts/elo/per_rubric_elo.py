#!/usr/bin/env python3
"""Per-rubric Glicko-2 ELO computation.

Splits a live-matches CSV into buckets by each case's rubric metadata, then
runs Glicko-2 on each bucket independently. Smoke cases use
`ensemble_rubric:`; adversarial cases may instead use `grader:` values such as
`lean-proof-quality`.

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
        --cases   lab/evals/adversarial-cases \
        --out     scripts/elo/example_runs/2026-05-27-x-per-rubric/
"""
from __future__ import annotations
import argparse, csv, glob, json, subprocess, sys
from pathlib import Path
from collections import defaultdict

try:
    import yaml
except ImportError:
    sys.exit("per_rubric_elo.py requires PyYAML")

HERE = Path(__file__).resolve().parent


def _case_files(case_inputs: list[Path]) -> list[Path]:
    """Expand case inputs that may be directories, files, or glob patterns."""
    files: list[Path] = []
    seen: set[Path] = set()
    for raw in case_inputs:
        raw_s = str(raw)
        if any(ch in raw_s for ch in "*?["):
            candidates = [Path(p) for p in glob.glob(raw_s, recursive=True)]
            if not candidates:
                print(f"warning: --cases glob matched no files: {raw}", file=sys.stderr)
        elif raw.is_dir():
            candidates = sorted(raw.rglob("*.yaml"))
        elif raw.is_file():
            candidates = [raw]
        else:
            print(f"warning: --cases path does not exist: {raw}", file=sys.stderr)
            candidates = []

        for p in candidates:
            rp = p.resolve()
            if rp not in seen:
                files.append(p)
                seen.add(rp)
    return files


def rubric_from_case(case_id: str, d: dict) -> str:
    """Resolve a case's per-rubric rating bucket from explicit metadata first."""
    rubric = d.get("ensemble_rubric")
    if rubric:
        return str(rubric)

    grader = d.get("grader")
    if isinstance(grader, str) and grader.endswith("-quality"):
        return grader

    skill = d.get("skill") or ""
    if skill == "mathlib-lookup":
        return "mathlib-lookup-quality"
    if skill.startswith("lean-setup"):
        return "lean-setup-import-quality"
    if skill.startswith("lean-tactic") or "tactic-discipline" in case_id:
        return "lean-tactic-discipline-quality"
    if skill.startswith("lean-") and "doc" in skill:
        return "lean-doc-quality"
    if skill.startswith("lean-"):
        return "lean-proof-quality"
    if skill.startswith(("ai-", "applied-", "math-")):
        return "applied-domain-quality"
    return rubric_for(case_id, {})


def load_rubricmap(case_inputs: list[Path]) -> dict[str, str]:
    """Read case YAML inputs and build {case_id -> rubric}."""
    rmap: dict[str, str] = {}
    for cy in _case_files(case_inputs):
        try:
            docs = list(yaml.safe_load_all(cy.read_text()))
        except Exception as exc:
            print(f"warning: failed to parse {cy}: {exc}", file=sys.stderr)
            continue
        if not docs:
            continue
        d = docs[0]
        if not isinstance(d, dict):
            print(f"warning: skipped non-mapping YAML document: {cy}", file=sys.stderr)
            continue
        case = d.get("id")
        if not case:
            print(f"warning: skipped case YAML without id: {cy}", file=sys.stderr)
            continue
        rmap[case] = rubric_from_case(str(case), d)
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
    p.add_argument("--cases", type=Path, action="append", required=True,
                   help=("case YAML source for rubric discovery; may be repeated "
                         "and may be a directory, file, or quoted glob pattern"))
    p.add_argument("--out", type=Path, required=True,
                   help="output directory; one subdir per rubric will be written")
    args = p.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    rmap = load_rubricmap(args.cases)

    buckets: dict[str, list[dict]] = defaultdict(list)
    unknown_adv_cases: set[str] = set()
    with args.matches.open(newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            case_id = row["case_id"]
            if case_id not in rmap and case_id.startswith("adv-"):
                unknown_adv_cases.add(case_id)
            buckets[rubric_for(case_id, rmap)].append(row)

    for case_id in sorted(unknown_adv_cases):
        print(
            f"warning: adversarial case {case_id!r} not found in --cases metadata; "
            "using fallback rubric",
            file=sys.stderr,
        )

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
