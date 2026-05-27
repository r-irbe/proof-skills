#!/usr/bin/env python3
"""LLM-judge calibration harness (lab/design/01-eval-framework.md §4.2).

For each ``*.transcript.md`` under ``lab/evals/known-bad/<skill>/``, build
the canonical judge prompt and aggregate the captured judge replies
(stored under ``_replies/<task_id>/<judge-model>.json``). Compute the
**flag-rate** = (transcripts aggregated ≤ rubric floor) / (transcripts
with replies). Per ADR-0039 the calibration gate is ≥ 0.90.

The script is **pure replay** — it never calls an LLM API. The
orchestrator (Copilot CLI sub-agent or Anthropic SDK dispatcher) is
responsible for producing the reply JSON files. See
``scripts/eval/graders/DISPATCH.md``.

Subcommands
-----------

``build``
    Emit the judge prompt for one transcript (for handing to a
    dispatcher). Mirrors ``llm_judge.py build``.

``replay``
    Aggregate captured replies across all transcripts and write a
    calibration report to
    ``reports/_calibration/<rubric>/<judge-model>.json``.

``check``
    Run ``replay`` and exit non-zero if flag-rate < ``--min-flag-rate``.
    Suitable for CI.

Layout
------

    lab/evals/known-bad/lean-proof/
        leaves-sorry.transcript.md      (frontmatter + # Task + # Response)
        uses-admit.transcript.md
        ...
        _replies/
            leaves-sorry/
                claude-opus-4.7-high.json
                claude-sonnet-4.6.json
            uses-admit/
                ...

Each ``.json`` file is the raw judge reply (parseable by
``llm_judge.parse_judge_response``).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

# Local import — calibrate_judge.py lives next to graders/.
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from graders.llm_judge import (  # noqa: E402
    JudgeReply,
    GradeResult,
    _load_yaml,
    _rubric_definitions,
    build_prompt,
    grade,
    parse_judge_response,
)


# ---------------------------------------------------------------------------
# Transcript parsing
# ---------------------------------------------------------------------------

@dataclass
class Transcript:
    path: Path
    task_id: str
    expected_max_score: int
    failure_mode: str
    task: str
    response: str
    notes: str = ""


_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def parse_transcript(path: Path) -> Transcript:
    """Parse a ``.transcript.md`` file with YAML frontmatter and
    ``# Task`` / ``# Response`` sections.
    """
    text = path.read_text()
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fm_raw, body = m.group(1), m.group(2)
    fm = _parse_simple_yaml(fm_raw)

    sections = _split_sections(body)
    if "task" not in sections:
        raise ValueError(f"{path}: missing '# Task' section")
    if "response" not in sections:
        raise ValueError(f"{path}: missing '# Response' section")

    return Transcript(
        path=path,
        task_id=str(fm.get("task_id") or path.stem.removesuffix(".transcript")),
        expected_max_score=int(fm.get("expected_max_score", 2)),
        failure_mode=str(fm.get("failure_mode", "unspecified")),
        task=sections["task"].strip(),
        response=sections["response"].strip(),
        notes=str(fm.get("notes", "")).strip(),
    )


def _parse_simple_yaml(raw: str) -> dict:
    """Tiny YAML reader for transcript frontmatter.

    Supports:
      key: scalar
      key: |   (block scalar to next dedented key)
    """
    out: dict = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "|":
            buf: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                buf.append(lines[i][2:] if lines[i].startswith("  ") else lines[i])
                i += 1
            out[key] = "\n".join(buf).rstrip()
        else:
            out[key] = _coerce_scalar(rest)
            i += 1
    return out


def _coerce_scalar(raw: str):
    if raw.startswith(("'", '"')) and raw.endswith(raw[0]) and len(raw) >= 2:
        return raw[1:-1]
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    if raw.lower() in {"true", "false"}:
        return raw.lower() == "true"
    return raw


_HEADER_RE = re.compile(r"^#\s+(\w+)\s*$", re.IGNORECASE | re.MULTILINE)


def _split_sections(body: str) -> dict[str, str]:
    matches = list(_HEADER_RE.finditer(body))
    if not matches:
        return {}
    out: dict[str, str] = {}
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        out[m.group(1).lower()] = body[start:end]
    return out


# ---------------------------------------------------------------------------
# Reply loading
# ---------------------------------------------------------------------------

def load_replies(replies_dir: Path, task_id: str, scale: list[int]) -> list[JudgeReply]:
    """Load all judge replies for ``task_id`` and parse them."""
    task_dir = replies_dir / task_id
    if not task_dir.is_dir():
        return []
    replies: list[JudgeReply] = []
    for p in sorted(task_dir.glob("*.json")):
        # Allow either {raw judge reply} or {"score":..,"rationale":..} shape.
        raw_text = p.read_text()
        obj = parse_judge_response(raw_text, scale=scale)
        replies.append(JudgeReply(
            score=int(obj["score"]),
            rationale=str(obj.get("rationale", "")),
            rubric_evidence=list(obj.get("rubric_evidence", [])),
            judge_id=p.stem,
            raw_text=raw_text,
        ))
    return replies


# ---------------------------------------------------------------------------
# Calibration core
# ---------------------------------------------------------------------------

@dataclass
class TranscriptResult:
    task_id: str
    failure_mode: str
    expected_max_score: int
    expected_flag: bool                 # True iff transcript is a known-bad negative
    aggregated_score: int | None
    flagged: bool                       # True iff aggregated_score ≤ floor
    correct: bool                       # True iff flagged == expected_flag
    judges: list[dict] = field(default_factory=list)
    notes: str = ""


@dataclass
class CalibrationReport:
    rubric: str
    skill: str
    floor: int
    pass_floor: int
    min_flag_rate: float
    max_false_flag_rate: float
    total_transcripts: int
    judged_transcripts: int
    # Negative-class metrics (known-bad transcripts, expected_max_score ≤ floor).
    negatives_total: int
    negatives_judged: int
    negatives_flagged: int
    flag_rate: float                    # recall on negatives
    # Positive-class metrics (adversarial good transcripts, expected_max_score > floor).
    positives_total: int
    positives_judged: int
    positives_flagged: int
    false_flag_rate: float              # false-positive rate on positives
    # Back-compat: count of correctly-flagged negatives.
    flagged: int
    per_transcript: list[TranscriptResult] = field(default_factory=list)


def calibrate(
    *,
    transcripts: list[Transcript],
    replies_dir: Path,
    rubric: dict,
    min_flag_rate: float,
    max_false_flag_rate: float = 1.0,
) -> CalibrationReport:
    floor = int(rubric.get("aggregation", {}).get("floor", 2))
    pass_floor = int(rubric.get("aggregation", {}).get("pass_floor", 4))
    scale = list(rubric.get("scale", [1, 2, 3, 4, 5]))

    per: list[TranscriptResult] = []
    judged = 0
    neg_total = neg_judged = neg_flagged = 0
    pos_total = pos_judged = pos_flagged = 0
    for t in transcripts:
        expected_flag = t.expected_max_score <= floor
        if expected_flag:
            neg_total += 1
        else:
            pos_total += 1
        replies = load_replies(replies_dir, t.task_id, scale)
        if not replies:
            per.append(TranscriptResult(
                task_id=t.task_id,
                failure_mode=t.failure_mode,
                expected_max_score=t.expected_max_score,
                expected_flag=expected_flag,
                aggregated_score=None,
                flagged=False,
                correct=False,
                notes="no judge replies captured",
            ))
            continue
        result = grade(
            case={"id": t.task_id, "task": t.task},
            response=t.response,
            judge_replies=replies,
            rubric=rubric,
        )
        is_flagged = result.aggregated_score <= floor
        judged += 1
        if expected_flag:
            neg_judged += 1
            if is_flagged:
                neg_flagged += 1
        else:
            pos_judged += 1
            if is_flagged:
                pos_flagged += 1
        per.append(TranscriptResult(
            task_id=t.task_id,
            failure_mode=t.failure_mode,
            expected_max_score=t.expected_max_score,
            expected_flag=expected_flag,
            aggregated_score=result.aggregated_score,
            flagged=is_flagged,
            correct=(is_flagged == expected_flag),
            judges=[
                {"judge_id": r.judge_id, "score": r.score,
                 "rationale": r.rationale} for r in replies
            ],
            notes=result.notes,
        ))

    flag_rate = (neg_flagged / neg_judged) if neg_judged else 0.0
    false_flag_rate = (pos_flagged / pos_judged) if pos_judged else 0.0
    skill = transcripts[0].path.parent.name if transcripts else "unknown"
    return CalibrationReport(
        rubric=str(rubric.get("name", "unknown")),
        skill=skill,
        floor=floor,
        pass_floor=pass_floor,
        min_flag_rate=min_flag_rate,
        max_false_flag_rate=max_false_flag_rate,
        total_transcripts=len(transcripts),
        judged_transcripts=judged,
        negatives_total=neg_total,
        negatives_judged=neg_judged,
        negatives_flagged=neg_flagged,
        flag_rate=flag_rate,
        positives_total=pos_total,
        positives_judged=pos_judged,
        positives_flagged=pos_flagged,
        false_flag_rate=false_flag_rate,
        flagged=neg_flagged,
        per_transcript=per,
    )


def discover_transcripts(skill_dir: Path) -> list[Transcript]:
    files = sorted(skill_dir.glob("*.transcript.md"))
    return [parse_transcript(p) for p in files]


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def _cmd_build(args: argparse.Namespace) -> int:
    rubric = _load_yaml(Path(args.rubric))
    transcript = parse_transcript(Path(args.transcript))
    prompt = build_prompt(
        task=transcript.task,
        response=transcript.response,
        rubric_name=rubric["name"],
        rubric_scale=list(rubric["scale"]),
        rubric_definitions=_rubric_definitions(rubric),
        blind=not args.no_blind,
    )
    if args.out:
        Path(args.out).write_text(prompt)
    else:
        sys.stdout.write(prompt)
    return 0


def _cmd_replay(args: argparse.Namespace) -> int:
    rubric = _load_yaml(Path(args.rubric))
    skill_dir = Path(args.skill_dir)
    transcripts = discover_transcripts(skill_dir)
    if not transcripts:
        print(f"calibrate_judge: no transcripts found under {skill_dir}", file=sys.stderr)
        return 2
    replies_dir = skill_dir / "_replies"
    report = calibrate(
        transcripts=transcripts,
        replies_dir=replies_dir,
        rubric=rubric,
        min_flag_rate=float(args.min_flag_rate),
        max_false_flag_rate=float(args.max_false_flag_rate),
    )

    out_path: Path
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = (
            Path(args.report_root)
            / report.rubric
            / f"{args.label}.json"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(asdict(report), indent=2) + "\n")

    # Human-readable summary on stdout.
    print(f"calibrate_judge: rubric={report.rubric} skill={report.skill}")
    print(f"  judged={report.judged_transcripts}/{report.total_transcripts}")
    print(f"  negatives: flagged={report.negatives_flagged}/{report.negatives_judged}"
          f"  flag_rate={report.flag_rate:.2%}"
          f"  min_required={report.min_flag_rate:.2%}")
    print(f"  positives: flagged={report.positives_flagged}/{report.positives_judged}"
          f"  false_flag_rate={report.false_flag_rate:.2%}"
          f"  max_allowed={report.max_false_flag_rate:.2%}")
    for tr in report.per_transcript:
        agg = "—" if tr.aggregated_score is None else str(tr.aggregated_score)
        if tr.aggregated_score is None:
            mark = "∅"
        else:
            mark = "✓" if tr.correct else "✗"
        kind = "neg" if tr.expected_flag else "pos"
        print(f"    {mark} [{kind}] {tr.task_id:<40} ({tr.failure_mode:<22})"
              f" agg={agg}  expected ≤ {tr.expected_max_score}")
    print(f"  → wrote {out_path}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    rc = _cmd_replay(args)
    if rc != 0:
        return rc
    # Re-read what replay wrote (cheap, gives us the report).
    rubric = _load_yaml(Path(args.rubric))
    if args.out:
        report_path = Path(args.out)
    else:
        report_path = (
            Path(args.report_root)
            / str(rubric.get("name", "unknown"))
            / f"{args.label}.json"
        )
    report = json.loads(report_path.read_text())
    if report["judged_transcripts"] == 0:
        print("calibrate_judge: FAIL — no transcripts had judge replies", file=sys.stderr)
        return 1
    fail = False
    if report.get("negatives_judged", 0) > 0 and report["flag_rate"] < float(args.min_flag_rate):
        print(
            f"calibrate_judge: FAIL — flag_rate {report['flag_rate']:.2%} "
            f"< required {float(args.min_flag_rate):.2%}",
            file=sys.stderr,
        )
        fail = True
    if report.get("positives_judged", 0) > 0 and report["false_flag_rate"] > float(args.max_false_flag_rate):
        print(
            f"calibrate_judge: FAIL — false_flag_rate {report['false_flag_rate']:.2%} "
            f"> max allowed {float(args.max_false_flag_rate):.2%}",
            file=sys.stderr,
        )
        fail = True
    if fail:
        return 1
    print(f"calibrate_judge: PASS — flag_rate {report['flag_rate']:.2%} "
          f"≥ {float(args.min_flag_rate):.2%}; "
          f"false_flag_rate {report['false_flag_rate']:.2%} "
          f"≤ {float(args.max_false_flag_rate):.2%}")
    return 0


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def _add_replay_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--rubric", required=True,
                   help="path to rubric YAML (e.g. scripts/eval/graders/rubrics/lean-proof-quality.yaml)")
    p.add_argument("--skill-dir", required=True,
                   help="directory containing *.transcript.md (e.g. lab/evals/known-bad/lean-proof)")
    p.add_argument("--label", default="ensemble",
                   help="report filename label (default: ensemble)")
    p.add_argument("--report-root", default="reports/_calibration",
                   help="root for report output (default: reports/_calibration)")
    p.add_argument("--out", default=None, help="explicit output path (overrides --report-root)")
    p.add_argument("--min-flag-rate", type=float, default=0.90,
                   help="minimum acceptable flag-rate on negatives (default 0.90 per ADR-0039)")
    p.add_argument("--max-false-flag-rate", type=float, default=1.0,
                   help="maximum acceptable false-flag rate on adversarial positives (default 1.0 = no gate)")


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="LLM-judge calibration harness")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_build = sub.add_parser("build", help="emit the judge prompt for one transcript")
    sp_build.add_argument("--rubric", required=True)
    sp_build.add_argument("--transcript", required=True)
    sp_build.add_argument("--out", default=None)
    sp_build.add_argument("--no-blind", action="store_true",
                          help="skip model-identity stripping (debug only)")
    sp_build.set_defaults(func=_cmd_build)

    sp_replay = sub.add_parser("replay", help="aggregate captured replies, write report")
    _add_replay_args(sp_replay)
    sp_replay.set_defaults(func=_cmd_replay)

    sp_check = sub.add_parser("check", help="replay + hard-gate on min_flag_rate (CI)")
    _add_replay_args(sp_check)
    sp_check.set_defaults(func=_cmd_check)

    args = ap.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
