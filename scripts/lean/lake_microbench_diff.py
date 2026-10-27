#!/usr/bin/env python3
"""Diff two W14-B2 lake microbenchmark snapshots.

Usage:
  python3 scripts/w14b2_lake_microbench_diff.py BASELINE_JSON CANDIDATE_JSON

Flags modules whose wall-clock time grows by more than max(25% of baseline, 5s).
Outputs a markdown table sorted by percentage growth (largest first). Exit status is
2 when any regression is flagged, otherwise 0.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diff two W14-B2 lake microbenchmark JSON snapshots.",
    )
    parser.add_argument("baseline_json", type=Path)
    parser.add_argument("candidate_json", type=Path)
    parser.add_argument(
        "--percent-threshold",
        type=float,
        default=25.0,
        help="Percentage component of the regression threshold (default: 25).",
    )
    parser.add_argument(
        "--absolute-threshold",
        type=float,
        default=5.0,
        help="Absolute-seconds component of the regression threshold (default: 5).",
    )
    return parser.parse_args()


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as err:
        raise SystemExit(f"missing microbench JSON: {path}") from err
    except json.JSONDecodeError as err:
        raise SystemExit(f"invalid microbench JSON at {path}: {err}") from err


def extract_timings(raw: object, path: Path) -> dict[str, float]:
    if not isinstance(raw, dict):
        raise SystemExit(f"microbench JSON must be an object: {path}")

    if "modules" in raw:
        modules = raw["modules"]
        if not isinstance(modules, dict):
            raise SystemExit(f"microbench JSON modules field must be an object: {path}")
        timings: dict[str, float] = {}
        for module, result in modules.items():
            if not isinstance(module, str):
                raise SystemExit(f"microbench JSON module names must be strings: {path}")
            if not isinstance(result, dict):
                raise SystemExit(
                    f"microbench JSON module payload must be an object: {path} -> {module!r}"
                )
            seconds = result.get("wall_clock_seconds")
            if not isinstance(seconds, (int, float)):
                raise SystemExit(
                    f"microbench JSON module wall_clock_seconds must be numeric: {path} -> {module!r}"
                )
            timings[module] = float(seconds)
        return timings

    timings: dict[str, float] = {}
    for module, value in raw.items():
        if not isinstance(module, str):
            raise SystemExit(f"microbench JSON keys must be strings: {path}")
        if not isinstance(value, (int, float)):
            raise SystemExit(f"microbench JSON values must be numeric: {path} -> {module!r}")
        timings[module] = float(value)
    return timings


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "new"
    return f"+{value:.1f}%"


def fmt_delta(value: float) -> str:
    return f"+{value:.3f}"


def main() -> int:
    args = parse_args()
    baseline = extract_timings(load_json(args.baseline_json), args.baseline_json)
    candidate = extract_timings(load_json(args.candidate_json), args.candidate_json)

    rows: list[tuple[float, float, str, float, float, float, float | None]] = []
    for module in sorted(set(baseline) | set(candidate)):
        before = baseline.get(module, 0.0)
        after = candidate.get(module, 0.0)
        delta = after - before
        if delta <= 0:
            continue
        percent_component = before * (args.percent_threshold / 100.0)
        threshold_seconds = max(args.absolute_threshold, percent_component)
        if delta <= threshold_seconds:
            continue
        pct_growth = None if before == 0 else (delta / before) * 100.0
        sort_pct = math.inf if pct_growth is None else pct_growth
        rows.append((sort_pct, delta, module, before, after, threshold_seconds, pct_growth))

    print("# W14-B2 lake microbench diff")
    print()
    print(f"- Baseline: `{args.baseline_json}`")
    print(f"- Candidate: `{args.candidate_json}`")
    print(
        "- Regression rule: `delta > max("
        f"{args.percent_threshold:.1f}% of baseline, {args.absolute_threshold:.1f}s)`"
    )
    print()
    print("| Module | Baseline (s) | Candidate (s) | Δ (s) | Growth | Threshold (s) |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")

    if not rows:
        print("| _None_ | - | - | - | - | - |")
        return 0

    for _, delta, module, before, after, threshold_seconds, pct_growth in sorted(
        rows,
        key=lambda row: (-row[0], -row[1], row[2]),
    ):
        print(
            f"| `{module}` | {before:.3f} | {after:.3f} | {fmt_delta(delta)} | "
            f"{fmt_pct(pct_growth)} | {threshold_seconds:.3f} |"
        )
    return 2


if __name__ == "__main__":
    sys.exit(main())
