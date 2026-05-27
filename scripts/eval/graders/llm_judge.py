#!/usr/bin/env python3
"""LLM-as-Judge grader (W8 Phase 2).

Per the design in ``lab/design/01-eval-framework.md §4.2``. The grader is
split into three pure functions plus an orchestration boundary:

* ``build_prompt(case, response, rubric)``   → str (the judge prompt)
* ``parse_judge_response(text, scale)``      → dict {score, rationale, …}
* ``aggregate(scores, rubric)``              → int (minority-veto / median)
* ``grade(case, response, judge_responses, rubric)`` → GradeResult

The orchestrator (``dispatch_judge.py`` or the human / Copilot CLI agent
running this session) is responsible for *executing* the prompt against
one or more judge models. This module never calls an API directly — that
boundary lets us swap dispatchers (Anthropic SDK, OpenAI SDK, local
Claude sub-agent, etc.) without touching the grader.

CLI usage (test the parser):

    python3 -m graders.llm_judge \\
        --rubric scripts/eval/graders/rubrics/lean-proof-quality.yaml \\
        --case scripts/eval/cases/lean-proof-omega.yaml \\
        --response scripts/eval/judge_runs/<case>/response.txt \\
        --judge-replies scripts/eval/judge_runs/<case>/judge-*.json \\
        --out scripts/eval/judge_runs/<case>/grade.json
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "judge.txt"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class JudgeReply:
    score: int
    rationale: str = ""
    rubric_evidence: list[str] = field(default_factory=list)
    judge_id: str = ""           # e.g. "claude-opus-4.7-high"
    raw_text: str = ""


@dataclass
class GradeResult:
    grader_kind: str = "llm-judge"
    passed: bool = False
    aggregated_score: int = 0
    pass_floor: int = 4
    judges: list[JudgeReply] = field(default_factory=list)
    aggregation_method: str = "minority_veto"
    notes: str = ""


# ---------------------------------------------------------------------------
# YAML loader (PyYAML if available, regex fallback for simple cases)
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    text = path.read_text()
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        return _yaml_fallback(text)


def _yaml_fallback(text: str) -> dict:
    """Minimal YAML loader for rubric/case files. Supports:
      scalar values (incl. quoted), block scalars (|), simple lists,
      one level of nesting via 2-space indentation.

    Limitations: no flow-style dicts, no anchors, no merge keys. Good
    enough for our rubric + case shape. PyYAML is preferred.
    """
    out: dict = {}
    lines = text.splitlines()
    i = 0

    def _parse_value(raw: str) -> Any:
        raw = raw.strip()
        if not raw:
            return None
        if raw.startswith('"') and raw.endswith('"'):
            return raw[1:-1]
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            if not inner:
                return []
            items = [s.strip().strip('"').strip("'") for s in inner.split(",")]
            out_items: list[Any] = []
            for it in items:
                try:
                    out_items.append(int(it))
                except ValueError:
                    out_items.append(it)
            return out_items
        try:
            return int(raw)
        except ValueError:
            pass
        try:
            return float(raw)
        except ValueError:
            pass
        if raw in ("true", "True"):
            return True
        if raw in ("false", "False"):
            return False
        return raw

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        # Top-level key
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            key, rest = m.group(1), m.group(2)
            if rest == "|":
                # Block scalar
                i += 1
                block = []
                while i < len(lines) and (
                    lines[i].startswith("  ") or lines[i].strip() == ""
                ):
                    block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                    i += 1
                out[key] = "\n".join(block).rstrip() + "\n"
                continue
            if rest:
                out[key] = _parse_value(rest)
                i += 1
                continue
            # Nested block or list
            i += 1
            sub_lines = []
            while i < len(lines) and (
                lines[i].startswith("  ") or lines[i].strip() == ""
            ):
                sub_lines.append(lines[i])
                i += 1
            if any(l.lstrip().startswith("- ") for l in sub_lines):
                out[key] = []
                for sl in sub_lines:
                    s = sl.strip()
                    if s.startswith("- "):
                        out[key].append(_parse_value(s[2:]))
            else:
                # Recurse on the dedented block
                sub_text = "\n".join(l[2:] if l.startswith("  ") else ""
                                     for l in sub_lines)
                out[key] = _yaml_fallback(sub_text)
            continue
        i += 1
    return out


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------

def _blind_response(text: str) -> str:
    """Strip model identity from a response. Heuristic, not security-grade."""
    patterns = [
        r"\b(claude[-\w.]*)\b",
        r"\b(gpt[-\w.]*)\b",
        r"\b(gemini[-\w.]*)\b",
        r"\b(llama[-\w.]*)\b",
        r"\bI am (an? )?(?:assistant|AI|language model)[^.]*\.",
    ]
    out = text
    for p in patterns:
        out = re.sub(p, "[MODEL]", out, flags=re.IGNORECASE)
    return out


def build_prompt(
    *,
    task: str,
    response: str,
    rubric_name: str,
    rubric_scale: list[int],
    rubric_definitions: dict[int, str],
    template_path: Path | None = None,
    blind: bool = True,
) -> str:
    """Build the judge prompt from the canonical template."""
    tpl = (template_path or PROMPT_TEMPLATE_PATH).read_text()
    defs_str = "\n".join(
        f"  Score {k}: {v.strip()}"
        for k, v in sorted(rubric_definitions.items())
    )
    payload = response.strip()
    if blind:
        payload = _blind_response(payload)
    # Use literal placeholder replacement (not str.format) because the
    # template contains literal `{"score": ...}` example JSON.
    out = tpl
    out = out.replace("{task}", task.strip())
    out = out.replace("{response_blinded}", payload)
    out = out.replace("{rubric_name}", rubric_name)
    out = out.replace("{scale}", str(list(rubric_scale)))
    out = out.replace("{rubric_definitions}", defs_str)
    return out


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_judge_response(text: str, *, scale: list[int]) -> dict:
    """Extract a JSON object from a (possibly noisy) judge reply.

    Returns the parsed dict. Raises ValueError on parse failure or if
    `score` is not in `scale`.
    """
    text = text.strip()
    if not text:
        raise ValueError("empty judge response")
    # 1. Try direct parse.
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # 2. Strip common markdown fences.
        stripped = re.sub(r"^```(?:json)?\s*", "", text)
        stripped = re.sub(r"\s*```$", "", stripped)
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            # 3. Greedy match for first {...} block.
            m = _JSON_OBJECT_RE.search(text)
            if not m:
                raise ValueError(f"no JSON object found in judge reply: {text[:200]!r}")
            obj = json.loads(m.group(0))
    if not isinstance(obj, dict):
        raise ValueError(f"judge reply is not a JSON object: {obj!r}")
    if "score" not in obj:
        raise ValueError(f"judge reply missing 'score': {obj!r}")
    score = obj["score"]
    if not isinstance(score, int) or score not in scale:
        raise ValueError(f"judge score {score!r} not in rubric scale {scale}")
    return obj


def minority_veto(scores: list[int], *, floor: int = 2, threshold: int = 4) -> int:
    """Per design §4.2: if any judge ≤floor while ≥1 other ≥threshold,
    return the minority low score. Else return median (rounded to int)."""
    if not scores:
        raise ValueError("no scores to aggregate")
    low = [s for s in scores if s <= floor]
    high = [s for s in scores if s >= threshold]
    if low and high:
        return min(low)
    return int(round(statistics.median(scores)))


def grade(
    *,
    case: dict,
    response: str,
    judge_replies: list[JudgeReply],
    rubric: dict,
) -> GradeResult:
    if not judge_replies:
        return GradeResult(passed=False, notes="no judge replies",
                           pass_floor=int(rubric.get("aggregation", {}).get("pass_floor", 4)))
    agg_spec = rubric.get("aggregation", {})
    floor = int(agg_spec.get("floor", 2))
    threshold = int(agg_spec.get("threshold", 4))
    pass_floor = int(agg_spec.get("pass_floor", 4))
    method = agg_spec.get("method", "minority_veto")

    scores = [r.score for r in judge_replies]
    if method == "minority_veto":
        agg = minority_veto(scores, floor=floor, threshold=threshold)
    elif method == "median":
        agg = int(round(statistics.median(scores)))
    elif method == "min":
        agg = min(scores)
    else:
        raise ValueError(f"unknown aggregation method: {method}")

    return GradeResult(
        grader_kind="llm-judge",
        passed=agg >= pass_floor,
        aggregated_score=agg,
        pass_floor=pass_floor,
        judges=judge_replies,
        aggregation_method=method,
        notes=f"{len(judge_replies)} judge(s); scores={scores}; "
              f"floor={floor} threshold={threshold} pass_floor={pass_floor}",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_case(path: Path) -> dict:
    return _load_yaml(path)


def _load_rubric(path: Path) -> dict:
    return _load_yaml(path)


def _rubric_definitions(rubric: dict) -> dict[int, str]:
    raw = rubric.get("definitions", {})
    out: dict[int, str] = {}
    for k, v in raw.items():
        try:
            out[int(k)] = str(v)
        except (TypeError, ValueError):
            continue
    return out


def _cmd_build(args: argparse.Namespace) -> int:
    case = _load_case(args.case)
    rubric = _load_rubric(args.rubric)
    response = args.response.read_text() if args.response else ""
    prompt = build_prompt(
        task=case["input"]["prompt"],
        response=response,
        rubric_name=rubric.get("name", args.rubric.stem),
        rubric_scale=list(rubric.get("scale", [1, 2, 3, 4, 5])),
        rubric_definitions=_rubric_definitions(rubric),
        blind=not args.no_blind,
    )
    if args.out:
        args.out.write_text(prompt)
        print(f"wrote prompt: {args.out}")
    else:
        sys.stdout.write(prompt)
    return 0


def _cmd_grade(args: argparse.Namespace) -> int:
    case = _load_case(args.case)
    rubric = _load_rubric(args.rubric)
    response = args.response.read_text() if args.response else ""
    scale = list(rubric.get("scale", [1, 2, 3, 4, 5]))

    replies: list[JudgeReply] = []
    for reply_path in args.judge_reply:
        raw = reply_path.read_text()
        parsed = parse_judge_response(raw, scale=scale)
        replies.append(JudgeReply(
            score=int(parsed["score"]),
            rationale=str(parsed.get("rationale", "")),
            rubric_evidence=list(parsed.get("rubric_evidence", [])),
            judge_id=reply_path.stem,
            raw_text=raw.strip(),
        ))

    result = grade(case=case, response=response,
                   judge_replies=replies, rubric=rubric)

    payload = {
        "case_id": case.get("id", args.case.stem),
        "grader": "llm-judge",
        "rubric": rubric.get("name", args.rubric.stem),
        "result": asdict(result),
    }
    if args.out:
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"wrote grade: {args.out}")
    else:
        print(json.dumps(payload, indent=2))
    print(f"[{'PASS' if result.passed else 'FAIL'}] "
          f"case={payload['case_id']} score={result.aggregated_score}/"
          f"{rubric.get('scale', [5])[-1]} pass_floor={result.pass_floor}")
    return 0 if result.passed else 1


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("build", help="emit a judge prompt to stdout / file")
    pb.add_argument("--case", required=True, type=Path)
    pb.add_argument("--rubric", required=True, type=Path)
    pb.add_argument("--response", type=Path,
                    help="file with the model response (default: case.input.expected_output_substring)")
    pb.add_argument("--out", type=Path)
    pb.add_argument("--no-blind", action="store_true",
                    help="skip identity stripping (debug only)")
    pb.set_defaults(func=_cmd_build)

    pg = sub.add_parser("grade", help="aggregate judge replies into a GradeResult")
    pg.add_argument("--case", required=True, type=Path)
    pg.add_argument("--rubric", required=True, type=Path)
    pg.add_argument("--response", type=Path)
    pg.add_argument("--judge-reply", action="append", type=Path, required=True,
                    help="file(s) with raw judge JSON (repeat per judge)")
    pg.add_argument("--out", type=Path)
    pg.set_defaults(func=_cmd_grade)

    args = p.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
