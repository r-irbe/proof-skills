#!/usr/bin/env python3
"""Diff two W14-B2 lake timing JSON snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_timings(path: Path) -> dict[str, float]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing timing JSON: {path}")
    except json.JSONDecodeError as err:
        raise SystemExit(f"invalid timing JSON at {path}: {err}")

    if not isinstance(raw, dict):
        raise SystemExit(f"timing JSON must be an object: {path}")

    timings: dict[str, float] = {}
    for target, value in raw.items():
        if not isinstance(target, str):
            raise SystemExit(f"timing JSON keys must be strings: {path}")
        if not isinstance(value, (int, float)):
            raise SystemExit(f"timing JSON values must be numbers: {path} -> {target!r}")
        timings[target] = float(value)
    return timings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report targets whose lake build time regressed between two timing JSON snapshots.",
    )
    parser.add_argument("baseline_json", type=Path)
    parser.add_argument("candidate_json", type=Path)
    parser.add_argument(
        "--percent-threshold",
        type=float,
        default=25.0,
        help="Report targets whose runtime grows by more than this percentage (default: 25).",
    )
    parser.add_argument(
        "--absolute-threshold",
        type=float,
        default=60.0,
        help="Report targets whose runtime grows by more than this many seconds (default: 60).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    before = load_timings(args.baseline_json)
    after = load_timings(args.candidate_json)

    rows = []
    for target in sorted(set(before) | set(after)):
        before_sec = before.get(target, 0.0)
        after_sec = after.get(target, 0.0)
        delta_sec = after_sec - before_sec
        if delta_sec <= 0:
            continue
        pct_growth = None if before_sec == 0 else (delta_sec / before_sec) * 100.0
        pct_hit = pct_growth is not None and pct_growth > args.percent_threshold
        abs_hit = delta_sec > args.absolute_threshold
        if pct_hit or abs_hit:
            rows.append((target, before_sec, after_sec, delta_sec, pct_growth, pct_hit, abs_hit))

    print(f"baseline={args.baseline_json}")
    print(f"candidate={args.candidate_json}")
    print(
        f"thresholds=percent>{args.percent_threshold:.1f}% absolute>{args.absolute_threshold:.1f}s"
    )

    if not rows:
        print("status=ok")
        print("regressions=0")
        return 0

    print("status=regression")
    print(f"regressions={len(rows)}")
    for target, before_sec, after_sec, delta_sec, pct_growth, pct_hit, abs_hit in sorted(
        rows,
        key=lambda row: (-row[3], row[0]),
    ):
        pct_text = "new-target" if pct_growth is None else f"{pct_growth:.1f}%"
        triggers = []
        if pct_hit:
            triggers.append("percent")
        if abs_hit:
            triggers.append("absolute")
        print(
            f"regression {target}: before={before_sec:.3f}s after={after_sec:.3f}s "
            f"delta={delta_sec:.3f}s growth={pct_text} trigger={'+'.join(triggers)}"
        )
    return 2


if __name__ == "__main__":
    sys.exit(main())
