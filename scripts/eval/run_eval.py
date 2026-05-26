#!/usr/bin/env python3
"""Prototype eval runner.

Loads YAML test cases, runs a placeholder "model invocation" (literal
echo of ``input.expected_output_substring``), grades with a deterministic
regex grader, and emits per-case JSON + a Markdown summary.

Usage::

    python3 run_eval.py \\
        --cases 'cases/*.yaml' \\
        --out ./out/eval-test \\
        --grader deterministic

Exit code is non-zero iff at least one case fails — so this can be
dropped into CI as a regression check once it's wired up.

This is a **prototype**. The real runner (see ``lab/design/03-multi-model-runner.md``)
will dispatch to background agents, capture token usage, and write
pairwise outcomes for ELO. None of that is here.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Project-local import (graders/ lives next to this file).
sys.path.insert(0, str(Path(__file__).parent))
from graders.deterministic import GradeResult, grade as deterministic_grade

# --- YAML loading -----------------------------------------------------------

try:
    import yaml  # type: ignore
    _HAVE_YAML = True
except ImportError:  # pragma: no cover - fallback path
    _HAVE_YAML = False


_KV_RE = re.compile(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*)$")
_LIST_RE = re.compile(r"^(\s*)-\s*(.*)$")


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] == '"':
        inner = s[1:-1]
        # Only run escape processing if there's a backslash; otherwise
        # `unicode_escape` mangles multibyte UTF-8 (e.g. "≤" -> mojibake).
        if "\\" not in inner:
            return inner
        return inner.encode("utf-8").decode("unicode_escape")
    if len(s) >= 2 and s[0] == s[-1] and s[0] == "'":
        return s[1:-1].replace("''", "'")
    return s


def _parse_flow_list(s: str) -> list[str] | None:
    """Parse a YAML flow list like ``[a, b, c]``. Returns None if not one."""
    s = s.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return None
    body = s[1:-1].strip()
    if not body:
        return []
    return [_strip_quotes(p.strip()) for p in body.split(",")]


def _peek_next_non_blank(lines: list[str], start: int) -> str | None:
    for j in range(start, len(lines)):
        if lines[j].strip() and not lines[j].lstrip().startswith("#"):
            return lines[j]
    return None


def _fallback_yaml_load(text: str) -> dict[str, Any]:
    """A *very* small YAML subset parser.

    Handles the case schema we care about: nested mappings, lists of
    strings (block or ``[a, b]`` flow style), ``|`` block scalars, and
    double-quoted strings with ``\\`` escapes. It does NOT handle
    anchors, ``>``-folded scalars, ints/bools, nested lists of maps,
    etc. It is here so the runner can still be smoke-tested on a
    machine without PyYAML.
    """
    raw_lines = text.splitlines()
    out: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, out)]
    current_list_key: tuple[int, str] | None = None

    i = 0
    while i < len(raw_lines):
        raw_line = raw_lines[i]
        # Strip comments outside of list-item lines (which may contain `#`
        # inside quoted strings — we don't try to handle that edge case).
        if raw_line.lstrip().startswith("-"):
            line = raw_line.rstrip()
        else:
            line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            i += 1
            continue

        m_list = _LIST_RE.match(line)
        if m_list and current_list_key is not None:
            indent = len(m_list.group(1))
            if indent > current_list_key[0]:
                _parent_indent, key = current_list_key
                owner = next(
                    container for ind, container in reversed(stack)
                    if ind < indent and isinstance(container, dict)
                )
                lst = owner.setdefault(key, [])
                if not isinstance(lst, list):
                    lst = []
                    owner[key] = lst
                lst.append(_strip_quotes(m_list.group(2)))
                i += 1
                continue

        m_kv = _KV_RE.match(line)
        if not m_kv:
            i += 1
            continue
        indent = len(m_kv.group(1))
        key = m_kv.group(2)
        value = m_kv.group(3).strip()

        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if not isinstance(parent, dict):
            i += 1
            continue

        if value == "|":
            # Block scalar: consume subsequent lines indented past `indent`.
            block_lines: list[str] = []
            j = i + 1
            block_indent: int | None = None
            while j < len(raw_lines):
                bl = raw_lines[j]
                stripped_bl = bl.lstrip(" ")
                this_indent = len(bl) - len(stripped_bl)
                if stripped_bl == "":
                    block_lines.append("")
                    j += 1
                    continue
                if this_indent <= indent:
                    break
                if block_indent is None:
                    block_indent = this_indent
                block_lines.append(bl[block_indent:] if this_indent >= block_indent else stripped_bl)
                j += 1
            while block_lines and block_lines[-1] == "":
                block_lines.pop()
            parent[key] = "\n".join(block_lines) + "\n"
            current_list_key = None
            i = j
            continue

        flow = _parse_flow_list(value) if value else None
        if flow is not None:
            parent[key] = flow
            current_list_key = None
            i += 1
            continue

        if value == "":
            # Look ahead: if the next non-blank line is a list item indented
            # past this key, this key is a LIST, not a sub-map. Defer the
            # container choice until we see the first child line.
            nxt = _peek_next_non_blank(raw_lines, i + 1)
            child_is_list = (
                nxt is not None
                and (len(nxt) - len(nxt.lstrip(" "))) > indent
                and nxt.lstrip().startswith("-")
            )
            if child_is_list:
                parent[key] = []                  # list-typed
                current_list_key = (indent, key)
            else:
                new_map: dict[str, Any] = {}
                parent[key] = new_map
                stack.append((indent, new_map))
                current_list_key = (indent, key)
        else:
            parent[key] = _strip_quotes(value)
            current_list_key = None
        i += 1
    return out


def load_case(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if _HAVE_YAML:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError(f"{path}: top-level YAML must be a mapping")
        return data
    return _fallback_yaml_load(text)


# --- Model invocation (placeholder) -----------------------------------------

def invoke_model(case: dict[str, Any]) -> str:
    """Stand-in for a real model call.

    The eventual runner will dispatch this to a background agent and
    capture the structured response. For now we just echo back the
    ``input.expected_output_substring`` field so the deterministic
    grader has something realistic to match against.
    """
    inp = case.get("input") or {}
    return str(inp.get("expected_output_substring", ""))


# --- Runner core -----------------------------------------------------------

@dataclass
class CaseRecord:
    case_id: str
    title: str
    skill: str
    grader: str
    output: str
    result: dict[str, Any]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


GRADERS = {
    "deterministic": deterministic_grade,
}


def run_case(path: Path, grader_name: str) -> CaseRecord:
    case = load_case(path)
    case_id = str(case.get("id") or path.stem)
    title = str(case.get("title") or case_id)
    skill = str(case.get("skill") or "unknown")
    grader_fn = GRADERS[grader_name]

    output = invoke_model(case)
    expected = case.get("expected") or {}
    result: GradeResult = grader_fn(output, expected)

    return CaseRecord(
        case_id=case_id,
        title=title,
        skill=skill,
        grader=grader_name,
        output=output,
        result=result.to_dict(),
        source=str(path),
    )


def write_summary(records: list[CaseRecord], out_dir: Path) -> None:
    passed = sum(1 for r in records if r.result["passed"])
    total = len(records)
    lines = [
        "# Eval run summary",
        "",
        f"- **Cases run:** {total}",
        f"- **Passed:** {passed}",
        f"- **Failed:** {total - passed}",
        f"- **Pass rate:** {(passed / total * 100):.1f}%" if total else "- _no cases_",
        "",
        "| Case | Skill | Grader | Score | Result |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in records:
        status = "✅ PASS" if r.result["passed"] else "❌ FAIL"
        lines.append(
            f"| `{r.case_id}` | {r.skill} | {r.grader} | "
            f"{r.result['score']:.2f} | {status} |"
        )

    lines.append("")
    failing = [r for r in records if not r.result["passed"]]
    if failing:
        lines.append("## Failures")
        lines.append("")
        for r in failing:
            lines.append(f"### `{r.case_id}`")
            if r.result["missing"]:
                lines.append("- Missing patterns:")
                for p in r.result["missing"]:
                    lines.append(f"  - `{p}`")
            if r.result["forbidden_hit"]:
                lines.append("- Forbidden pattern matched:")
                for p in r.result["forbidden_hit"]:
                    lines.append(f"  - `{p}`")
            lines.append("")

    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Prototype eval runner")
    ap.add_argument("--cases", required=True,
                    help="Glob of YAML case files (quote it!)")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--grader", default="deterministic", choices=list(GRADERS))
    args = ap.parse_args(argv)

    paths = sorted(Path(p) for p in glob.glob(args.cases))
    if not paths:
        print(f"no case files matched: {args.cases}", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    records: list[CaseRecord] = []
    for path in paths:
        try:
            rec = run_case(path, args.grader)
        except Exception as e:
            print(f"[ERROR] {path}: {e}", file=sys.stderr)
            rec = CaseRecord(
                case_id=path.stem, title=path.stem, skill="unknown",
                grader=args.grader, output="",
                result={"passed": False, "score": 0.0, "matched": [],
                        "missing": [], "forbidden_hit": [],
                        "notes": f"loader/runtime error: {e}"},
                source=str(path),
            )
        records.append(rec)
        (out_dir / f"{rec.case_id}.json").write_text(
            json.dumps(rec.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
        status = "PASS" if rec.result["passed"] else "FAIL"
        print(f"[{status}] {rec.case_id}  score={rec.result['score']:.2f}")

    write_summary(records, out_dir)

    failed = sum(1 for r in records if not r.result["passed"])
    print(f"\n{len(records) - failed}/{len(records)} passed → {out_dir}/summary.md")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
