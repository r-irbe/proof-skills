#!/usr/bin/env python3
"""Convert a directory of (output, judge-grade) pairs into ELO match rows.

Per the design in ``lab/design/02-elo-system.md §2`` ("pairwise comparison
protocol"), this script:

1. Reads ``output-<player_id>.lean`` + ``judge-<player_id>.json`` pairs
   from one or more *case directories* under ``judge_runs/<case>/``.
2. For each case, builds the ``score_player`` map by normalising the
   judge's integer score to ``[0, 1]`` (``score / max_scale``).
3. For each unordered pair (A, B) emits a row to ``--out`` CSV:
   - ``|s_A − s_B| ≥ 0.15``  → ``winner = a`` (or ``b``).
   - else                    → ``winner = draw``.
4. The output CSV is the exact shape consumed by ``elo.py`` and
   ``glicko2.py``: ``case_id,model_a,model_b,winner,reasoning_effort_a,reasoning_effort_b``.

Naming convention for ``player_id``:

- Files named ``output-<model_id>.lean`` (no @effort) → player is just ``<model_id>``,
  effort columns are empty.
- Files named ``output-<model_id>@<effort>.lean`` → split on ``@``; model in
  ``model_<a|b>``, effort in ``reasoning_effort_<a|b>``.

W8 Phase 2 dispatches the LLM judge via the orchestration loop in
``dispatch_judge.md`` (the procedural recipe — actual API/sub-agent
dispatch happens upstream of this script).

CLI:

    python3 scripts/eval/multi_model.py \\
        --runs-dir scripts/eval/judge_runs \\
        --case lean-add-comm-multi \\
        --rubric scripts/eval/graders/rubrics/lean-proof-quality.yaml \\
        --out scripts/elo/matches/run-<date>.csv \\
        --draw-threshold 0.15
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Allow `from graders.llm_judge import _load_yaml` without sys.path tricks.
sys.path.insert(0, str(Path(__file__).parent))
from graders.llm_judge import _load_yaml  # noqa: E402


@dataclass
class PlayerResult:
    player_id: str
    model: str
    effort: str
    score_raw: float          # judge score in rubric scale
    score_norm: float         # score / max_scale


_OUTPUT_RE = re.compile(r"^output-(.+)\.lean$")
_JUDGE_RE = re.compile(r"^judge-(.+)\.json$")


def _split_player(pid: str) -> tuple[str, str]:
    if "@" in pid:
        m, e = pid.split("@", 1)
        return m, e
    return pid, ""


def _collect_case(
    case_dir: Path, *, max_scale: int
) -> dict[str, PlayerResult]:
    """Find all output/judge pairs in a case directory."""
    outputs: dict[str, Path] = {}
    judges: dict[str, Path] = {}
    for f in sorted(case_dir.iterdir()):
        if not f.is_file():
            continue
        if m := _OUTPUT_RE.match(f.name):
            outputs[m.group(1)] = f
        elif m := _JUDGE_RE.match(f.name):
            judges[m.group(1)] = f
    results: dict[str, PlayerResult] = {}
    for pid, opath in outputs.items():
        jpath = judges.get(pid)
        if jpath is None:
            print(f"WARN: {opath.name} has no matching judge-{pid}.json — skipping",
                  file=sys.stderr)
            continue
        try:
            jobj = json.loads(jpath.read_text())
        except json.JSONDecodeError as e:
            print(f"WARN: {jpath} parse error: {e}", file=sys.stderr)
            continue
        score = float(jobj.get("score", 0))
        if score <= 0:
            print(f"WARN: {jpath} score {score!r} not positive — skipping",
                  file=sys.stderr)
            continue
        model, effort = _split_player(pid)
        results[pid] = PlayerResult(
            player_id=pid,
            model=model,
            effort=effort,
            score_raw=score,
            score_norm=score / float(max_scale),
        )
    return results


def _emit_pairs(
    case_id: str,
    results: dict[str, PlayerResult],
    *,
    draw_threshold: float,
) -> list[dict]:
    rows: list[dict] = []
    for a_id, b_id in itertools.combinations(sorted(results), 2):
        a = results[a_id]
        b = results[b_id]
        delta = a.score_norm - b.score_norm
        if abs(delta) < draw_threshold:
            winner = "draw"
        elif delta > 0:
            winner = "a"
        else:
            winner = "b"
        rows.append({
            "case_id": case_id,
            "model_a": a.model,
            "model_b": b.model,
            "winner": winner,
            "reasoning_effort_a": a.effort,
            "reasoning_effort_b": b.effort,
        })
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--runs-dir", type=Path, required=True,
                   help="Parent dir containing one subdir per case")
    p.add_argument("--case", action="append", default=None,
                   help="Restrict to these case subdirs (repeatable). "
                        "Default: every subdir of --runs-dir.")
    p.add_argument("--rubric", type=Path, required=True,
                   help="Rubric YAML — used only to read the max scale value")
    p.add_argument("--out", type=Path, required=True,
                   help="Output CSV (created or appended via --append)")
    p.add_argument("--append", action="store_true",
                   help="Append rows to --out instead of overwriting")
    p.add_argument("--draw-threshold", type=float, default=0.15,
                   help="Per design §2.3: |s_A - s_B| < threshold → draw. "
                        "Default 0.15 in normalized [0,1] space.")
    args = p.parse_args()

    if not args.runs_dir.is_dir():
        print(f"ERROR: --runs-dir {args.runs_dir} is not a directory", file=sys.stderr)
        return 2

    rubric = _load_yaml(args.rubric)
    scale = rubric.get("scale", [1, 2, 3, 4, 5])
    max_scale = max(int(s) for s in scale)

    if args.case:
        case_dirs = [args.runs_dir / c for c in args.case]
    else:
        case_dirs = [d for d in sorted(args.runs_dir.iterdir()) if d.is_dir()]

    all_rows: list[dict] = []
    summary_lines: list[str] = []
    for cd in case_dirs:
        if not cd.is_dir():
            print(f"WARN: {cd} is not a directory — skipping", file=sys.stderr)
            continue
        results = _collect_case(cd, max_scale=max_scale)
        if len(results) < 2:
            print(f"WARN: case {cd.name} has {len(results)} entrant(s) (<2) — skipping",
                  file=sys.stderr)
            continue
        rows = _emit_pairs(cd.name, results, draw_threshold=args.draw_threshold)
        all_rows.extend(rows)
        summary_lines.append(
            f"  {cd.name}: {len(results)} entrants → {len(rows)} pairs"
        )

    if not all_rows:
        print(f"ERROR: no match rows produced", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.append and args.out.exists() else "w"
    write_header = mode == "w" or not args.out.exists()
    with args.out.open(mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "case_id", "model_a", "model_b", "winner",
            "reasoning_effort_a", "reasoning_effort_b",
        ])
        if write_header:
            w.writeheader()
        w.writerows(all_rows)

    print(f"wrote {len(all_rows)} match rows → {args.out}")
    print(f"draw threshold (normalized [0,1] judge scores): {args.draw_threshold}")
    for line in summary_lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
