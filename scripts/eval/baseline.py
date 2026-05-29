#!/usr/bin/env python3
"""Baseline tracker for the deterministic eval suite.

A minimal subset of the design in
``lab/design/01-eval-framework.md §5`` covering only the fields that
the deterministic + lean-build graders produce locally (no cost,
latency, or judge score — those require LLM dispatch which is not in
scope for W8 Phase 1 / smoke CI).

Two modes:

* ``--mode write``  Reads a directory of per-case ``<case_id>.json``
  files (produced by ``run_eval.py``) and writes / overwrites the
  requested baseline file.
* ``--mode diff``   Reads the same per-case JSON files plus the
  existing ``baseline.json`` and reports regressions. Exits 1 if
  any regression is found (so this is a drop-in CI gate).

Regression definition (subset of §5.2):

1. baseline.passed == True AND run.passed == False
   → hard regression (block).
2. baseline.passed == True AND run.score < baseline.score
   → score regression (block).
3. baseline.passed == False AND run.passed == True
   → positive regression (report, but don't block) — the baseline
     can be refreshed via ``--mode write``.

Cost / latency / judge gates are deferred until the LLM-judge grader
lands (out of session scope; W8 Phase 2).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = "1"


@dataclass
class CaseRun:
    case_id: str
    passed: bool
    score: float
    grader: str = "deterministic"


@dataclass
class Diff:
    hard_regressions: list[str] = field(default_factory=list)
    score_regressions: list[tuple[str, float, float]] = field(default_factory=list)
    positive_regressions: list[str] = field(default_factory=list)
    new_cases: list[str] = field(default_factory=list)
    dropped_cases: list[str] = field(default_factory=list)


def _read_run(run_dir: Path) -> dict[str, CaseRun]:
    runs: dict[str, CaseRun] = {}
    for jf in sorted(run_dir.glob("*.json")):
        if jf.name == "baseline.json":
            continue
        try:
            data = json.loads(jf.read_text())
        except json.JSONDecodeError as e:
            print(f"WARN: skipping {jf}: {e}", file=sys.stderr)
            continue
        cid = data.get("case_id") or jf.stem
        # run_eval.py emits both `result.passed` and a top-level `pass`/score.
        # Be permissive: check both shapes.
        result = data.get("result", data)
        passed = bool(result.get("passed", False))
        score = float(result.get("score", 0.0))
        grader = data.get("grader", "deterministic")
        runs[cid] = CaseRun(case_id=cid, passed=passed, score=score, grader=grader)
    return runs


def _write_baseline(out: Path, runs: dict[str, CaseRun]) -> Path:
    baseline = {
        "schema_version": SCHEMA_VERSION,
        "cases": {
            cid: {"passed": r.passed, "score": round(r.score, 4), "grader": r.grader}
            for cid, r in sorted(runs.items())
        },
    }
    out.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    return out


def _read_baseline(path: Path) -> dict[str, CaseRun]:
    data = json.loads(path.read_text())
    cases = data.get("cases", {})
    return {
        cid: CaseRun(
            case_id=cid,
            passed=bool(c.get("passed", False)),
            score=float(c.get("score", 0.0)),
            grader=c.get("grader", "deterministic"),
        )
        for cid, c in cases.items()
    }


def _diff(baseline: dict[str, CaseRun], run: dict[str, CaseRun]) -> Diff:
    d = Diff()
    for cid in sorted(set(baseline) | set(run)):
        b = baseline.get(cid)
        r = run.get(cid)
        if b is None and r is not None:
            d.new_cases.append(cid)
            continue
        if r is None:
            d.dropped_cases.append(cid)
            continue
        if b.passed and not r.passed:
            d.hard_regressions.append(cid)
        elif b.passed and r.score < b.score:
            d.score_regressions.append((cid, b.score, r.score))
        elif not b.passed and r.passed:
            d.positive_regressions.append(cid)
    return d


def _print_diff(d: Diff, *, baseline_path: Path) -> int:
    print(f"baseline: {baseline_path}")
    print(f"hard regressions     : {len(d.hard_regressions)}")
    print(f"score regressions    : {len(d.score_regressions)}")
    print(f"positive regressions : {len(d.positive_regressions)}")
    print(f"new cases            : {len(d.new_cases)}")
    print(f"dropped cases        : {len(d.dropped_cases)}")
    if d.hard_regressions:
        print()
        print("HARD REGRESSIONS (block):")
        for cid in d.hard_regressions:
            print(f"  ❌ {cid}")
    if d.score_regressions:
        print()
        print("SCORE REGRESSIONS (block):")
        for cid, was, now in d.score_regressions:
            print(f"  ⚠ {cid}  {was:.2f} → {now:.2f}")
    if d.positive_regressions:
        print()
        print("POSITIVE regressions (refresh baseline with --mode write):")
        for cid in d.positive_regressions:
            print(f"  ✅ {cid}")
    if d.new_cases:
        print()
        print("NEW CASES (refresh baseline with --mode write):")
        for cid in d.new_cases:
            print(f"  + {cid}")
    if d.dropped_cases:
        print()
        print("DROPPED CASES (refresh baseline with --mode write):")
        for cid in d.dropped_cases:
            print(f"  - {cid}")
    if d.hard_regressions or d.score_regressions:
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--run-dir", required=True, type=Path,
                   help="Directory containing <case>.json from run_eval.py")
    p.add_argument("--baseline", type=Path, default=None,
                   help="Path to baseline.json (default: <run-dir>/baseline.json)")
    p.add_argument("--mode", choices=["write", "diff"], required=True,
                   help="write: persist current run as baseline; diff: compare")
    args = p.parse_args()

    run_dir: Path = args.run_dir
    if not run_dir.is_dir():
        print(f"ERROR: --run-dir {run_dir} is not a directory", file=sys.stderr)
        return 2
    baseline_path: Path = args.baseline or (run_dir / "baseline.json")

    runs = _read_run(run_dir)
    if not runs:
        print(f"ERROR: no per-case JSON files found in {run_dir}", file=sys.stderr)
        return 2

    if args.mode == "write":
        out = _write_baseline(baseline_path, runs)
        print(f"wrote baseline: {out}  ({len(runs)} cases)")
        return 0

    if not baseline_path.exists():
        print(f"ERROR: baseline {baseline_path} does not exist. "
              f"Run --mode write first.", file=sys.stderr)
        return 2
    baseline = _read_baseline(baseline_path)
    d = _diff(baseline, runs)
    return _print_diff(d, baseline_path=baseline_path)


if __name__ == "__main__":
    sys.exit(main())
