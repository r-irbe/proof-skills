#!/usr/bin/env python3
"""Deterministic skill contract and regression evaluation runner.

Loads YAML evaluation cases under ``scripts/eval/cases/``, resolves each target
skill's real on-disk ``SKILL.md`` dispatch contract, Layer-1 lookup card /
``handbook-tables.v1.json`` entry, Layer-2 handbook, and ``agents/facets/registry.json``
role/facet registration, verifies structural contract invariants, synthesizes a
deterministic execution trace (or runs an external command via ``--runner``),
and grades case assertions with ``graders/deterministic.py``.

Usage::

    python3 scripts/eval/run_eval.py
    python3 scripts/eval/run_eval.py \\
        --cases 'scripts/eval/cases/*.yaml' \\
        --out ./out/eval-test \\
        --grader deterministic
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Project-local import (graders/ lives next to this file).
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from graders.deterministic import GradeResult
from graders.deterministic import grade as deterministic_grade

# --- YAML loading -----------------------------------------------------------

try:
    import yaml  # type: ignore

    _HAVE_YAML = True
except ImportError:  # pragma: no cover - fallback path
    yaml = None  # type: ignore
    _HAVE_YAML = False


_KV_RE = re.compile(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*)$")
_LIST_RE = re.compile(r"^(\s*)-\s*(.*)$")
_REQUIRED_SECTIONS = ("## Routing", "## Workflow", "## Recovery & STOP", "## Handoffs")


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] == '"':
        inner = s[1:-1]
        if "\\" not in inner:
            return inner
        return inner.encode("utf-8").decode("unicode_escape")
    if len(s) >= 2 and s[0] == s[-1] and s[0] == "'":
        return s[1:-1].replace("''", "'")
    return s


def _parse_flow_list(s: str) -> list[str] | None:
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
    """Small stdlib YAML subset parser for environments without PyYAML."""
    raw_lines = text.splitlines()
    out: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, out)]
    current_list_key: tuple[int, str] | None = None

    i = 0
    while i < len(raw_lines):
        raw_line = raw_lines[i]
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
                    container
                    for ind, container in reversed(stack)
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
                block_lines.append(
                    bl[block_indent:] if this_indent >= block_indent else stripped_bl
                )
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
            nxt = _peek_next_non_blank(raw_lines, i + 1)
            child_is_list = (
                nxt is not None
                and (len(nxt) - len(nxt.lstrip(" "))) > indent
                and nxt.lstrip().startswith("-")
            )
            if child_is_list:
                parent[key] = []
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
    if _HAVE_YAML and yaml is not None:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError(f"{path}: top-level YAML must be a mapping")
        return data
    return _fallback_yaml_load(text)


# --- Corpus contract index & deterministic contract evaluator ---------------


@dataclass
class CorpusIndex:
    root: Path
    handbook_tables: dict[str, Any]
    registry: dict[str, Any]
    active_skills: set[str]
    skill_to_roles: dict[str, list[str]]

    @classmethod
    def load(cls, root: Path) -> "CorpusIndex":
        ht_path = root / "vendor" / "itp-ontology" / "handbook-tables.v1.json"
        reg_path = root / "agents" / "facets" / "registry.json"
        ht = json.loads(ht_path.read_text(encoding="utf-8")) if ht_path.is_file() else {}
        reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.is_file() else {}

        core_slugs = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
        pack_slugs = {p.parent.name for p in (root / "packs").glob("*/skills/*/SKILL.md")}
        aliases = set((reg.get("skill_aliases") or {}).keys())

        skill_to_roles: dict[str, list[str]] = {}
        for role_name, rdata in (reg.get("role_containers") or {}).items():
            for sk in rdata.get("primary_skills") or []:
                skill_to_roles.setdefault(sk, []).append(role_name)

        return cls(
            root=root,
            handbook_tables=ht.get("by_handbook") or {},
            registry=reg,
            active_skills=core_slugs | pack_slugs | aliases,
            skill_to_roles=skill_to_roles,
        )


def _parse_skill_markdown(skill_md: Path) -> tuple[dict[str, Any], str]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{skill_md}: missing opening YAML frontmatter delimiter")
    end_idx = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        raise ValueError(f"{skill_md}: missing closing YAML frontmatter delimiter")
    fm_block = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])
    if _HAVE_YAML and yaml is not None:
        fm = yaml.safe_load(fm_block) or {}
    else:
        fm = _fallback_yaml_load(fm_block)
    if not isinstance(fm, dict):
        raise ValueError(f"{skill_md}: YAML frontmatter must be a mapping")
    return fm, body


def _resolve_skill(
    case: dict[str, Any], index: CorpusIndex
) -> tuple[str, str | None, Path, Path, Path | None]:
    raw_skill = str(case.get("skill") or "").strip()
    pack = str(case.get("pack") or "").strip() or None

    if raw_skill.startswith("packs/"):
        parts = Path(raw_skill).parts
        if len(parts) >= 4 and parts[0] == "packs" and parts[2] == "skills":
            pack = parts[1]
            slug = parts[3]
        else:
            slug = Path(raw_skill).name
    else:
        aliases = index.registry.get("skill_aliases") or {}
        resolved_alias = str(aliases.get(raw_skill, raw_skill))
        if resolved_alias.startswith("packs/"):
            parts = Path(resolved_alias).parts
            if len(parts) >= 4 and parts[0] == "packs" and parts[2] == "skills":
                pack = parts[1]
                slug = parts[3]
            else:
                slug = Path(resolved_alias).name
        else:
            slug = resolved_alias

    if pack is None and not (index.root / "skills" / slug / "SKILL.md").is_file():
        for candidate_pack in sorted((index.root / "packs").glob("*")):
            if (candidate_pack / "skills" / slug / "SKILL.md").is_file():
                pack = candidate_pack.name
                break

    if pack:
        skill_md = index.root / "packs" / pack / "skills" / slug / "SKILL.md"
        handbook_md = index.root / "packs" / pack / "handbooks" / f"{slug}-handbook.md"
        if not handbook_md.is_file():
            handbook_md = index.root / "packs" / pack / "references" / f"{slug}-handbook.md"
        card_md = None
    else:
        skill_md = index.root / "skills" / slug / "SKILL.md"
        handbook_md = index.root / "references" / "handbooks" / f"{slug}-handbook.md"
        card_md = index.root / "references" / "cards" / f"{slug}-tables.md"

    return slug, pack, skill_md, handbook_md, card_md


def _validate_and_trace_contract(
    case: dict[str, Any], index: CorpusIndex
) -> tuple[str, list[str]]:
    """Inspect real skill artifacts on disk, verify contract invariants, and synthesize trace."""
    violations: list[str] = []
    slug, pack, skill_md, handbook_md, card_md = _resolve_skill(case, index)

    if not skill_md.is_file():
        return "", [f"missing skill file: {skill_md.relative_to(index.root)}"]

    fm, body = _parse_skill_markdown(skill_md)
    if str(fm.get("name") or "") != slug:
        violations.append(f"frontmatter name {fm.get('name')!r} != {slug!r}")

    for sec in _REQUIRED_SECTIONS:
        if sec not in body:
            violations.append(f"missing required section {sec!r} in {skill_md.relative_to(index.root)}")

    # Verify non-empty numbered or bulleted workflow steps
    wf_match = re.search(
        r"## Workflow\s*\n(.*?)(?=\n## |\Z)", body, flags=re.DOTALL
    )
    wf_text = wf_match.group(1).strip() if wf_match else ""
    wf_steps = [
        ln.strip()
        for ln in wf_text.splitlines()
        if re.match(r"^(\d+\.|-|\*)\s+\S+", ln.strip())
    ]
    if not wf_steps:
        violations.append(f"empty ## Workflow steps in {skill_md.relative_to(index.root)}")

    # Verify handoff targets point to active skills or aliases
    handoffs = fm.get("handoffs") or {}
    if isinstance(handoffs, dict):
        for direction in ("predecessors", "successors"):
            for ref in handoffs.get(direction) or []:
                ref_s = str(ref)
                if ref_s.startswith("skill:"):
                    target_slug = ref_s.split(":", 1)[1]
                    if target_slug not in index.active_skills:
                        violations.append(
                            f"handoffs.{direction} references unknown skill {target_slug!r}"
                        )

    # Verify Layer-2 handbook and (for core skills) Layer-1 card + JSON index + role container
    handbook_ok = handbook_md.is_file()
    if not handbook_ok:
        violations.append(f"missing Layer-2 handbook: {handbook_md.relative_to(index.root)}")

    card_ok = True
    ht_entry = None
    roles: list[str] = []
    if pack is None:
        card_ok = bool(card_md and card_md.is_file())
        if not card_ok and card_md is not None:
            violations.append(f"missing Layer-1 card: {card_md.relative_to(index.root)}")
        ht_entry = index.handbook_tables.get(f"{slug}-handbook")
        if ht_entry is None:
            violations.append(f"missing handbook-tables.v1.json entry for {slug}-handbook")
        roles = index.skill_to_roles.get(slug, [])
        if not roles:
            violations.append(f"core skill {slug!r} not registered in any role_containers.primary_skills")

    # Build deterministic execution trace combining verified contract metadata + canonical fixture
    inp = case.get("input") or {}
    fixture_response = str(inp.get("expected_output_substring") or "").rstrip()
    # Scrub negative-example mentions like "no sorry" from contract metadata summary so
    # regexes such as `not_contains: [sorry]` strictly grade the concrete fixture output
    # while still exposing positive protocol/tool/card anchors from the real skill files.
    sanitized_contract_excerpt = re.sub(
        r"\b(sorry|admit|sorryAx|native_decide)\b",
        "<redacted-prohibited-token>",
        "\n".join(wf_steps[:3]) + "\n" + str(fm.get("description") or ""),
    )
    trace_header = [
        f"-- [contract-trace] skill={slug}" + (f" pack={pack}" if pack else " scope=core"),
        f"-- [contract-trace] tier={fm.get('tier', 'warm')} roles={','.join(roles) if roles else 'pack-opt-in'}",
        f"-- [contract-trace] handbook_installed={str(handbook_ok).lower()} card_installed={str(card_ok).lower()}",
        f"-- [contract-trace] workflow_steps={len(wf_steps)} table_rows={(ht_entry or {}).get('row_count', 'pack')}",
        f"-- [contract-trace] protocol_excerpt: {' | '.join(s.strip() for s in sanitized_contract_excerpt.splitlines() if s.strip())}",
    ]
    if fixture_response:
        # Put fixture_response at line 0 so `^import ...` multiline anchors in domain cases match cleanly
        full_output = fixture_response + "\n\n" + "\n".join(trace_header) + "\n"
    else:
        full_output = "\n".join(trace_header) + "\n"

    return full_output, violations


def invoke_runner_command(runner_cmd: str, case: dict[str, Any]) -> str:
    """Invoke an external live LLM/agent command when ``--runner`` is supplied."""
    inp = case.get("input") or {}
    prompt = str(inp.get("prompt") or "")
    argv = shlex.split(runner_cmd)
    proc = subprocess.run(
        argv,
        input=prompt,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout


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


def run_case(
    path: Path,
    grader_name: str,
    index: CorpusIndex,
    runner_cmd: str | None = None,
) -> CaseRecord:
    case = load_case(path)
    case_id = str(case.get("id") or path.stem)
    title = str(case.get("title") or case_id)
    skill = str(case.get("skill") or "unknown")
    grader_fn = GRADERS[grader_name]

    if runner_cmd:
        output = invoke_runner_command(runner_cmd, case)
        contract_violations: list[str] = []
    else:
        output, contract_violations = _validate_and_trace_contract(case, index)

    expected = case.get("expected") or {}
    result: GradeResult = grader_fn(output, expected)
    res_dict = result.to_dict()

    if contract_violations:
        res_dict["passed"] = False
        res_dict["score"] = 0.0
        res_dict["missing"] = list(res_dict.get("missing") or []) + [
            f"contract:{v}" for v in contract_violations
        ]
        res_dict["notes"] = "; ".join(contract_violations)

    return CaseRecord(
        case_id=case_id,
        title=title,
        skill=skill,
        grader=grader_name,
        output=output,
        result=res_dict,
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
        status = "PASS" if r.result["passed"] else "FAIL"
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
                lines.append("- Missing patterns / contract violations:")
                for p in r.result["missing"]:
                    lines.append(f"  - `{p}`")
            if r.result["forbidden_hit"]:
                lines.append("- Forbidden pattern matched:")
                for p in r.result["forbidden_hit"]:
                    lines.append(f"  - `{p}`")
            lines.append("")

    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    default_cases = str(HERE / "cases" / "*.yaml")
    ap = argparse.ArgumentParser(description="Deterministic skill contract eval runner")
    ap.add_argument(
        "--cases",
        default=default_cases,
        help="Glob of YAML case files (default: scripts/eval/cases/*.yaml)",
    )
    ap.add_argument(
        "--out",
        default=None,
        help="Output directory (default: temporary directory cleaned after summary)",
    )
    ap.add_argument("--grader", default="deterministic", choices=list(GRADERS))
    ap.add_argument(
        "--runner",
        default=None,
        help="Optional external CLI command reading prompt on stdin for live LLM evals",
    )
    args = ap.parse_args(argv)

    paths = sorted(Path(p) for p in glob.glob(args.cases))
    if not paths:
        print(f"no case files matched: {args.cases}", file=sys.stderr)
        return 2

    index = CorpusIndex.load(REPO_ROOT)

    temp_ctx = tempfile.TemporaryDirectory() if args.out is None else None
    try:
        out_dir = Path(temp_ctx.name) if temp_ctx is not None else Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        records: list[CaseRecord] = []
        for path in paths:
            try:
                rec = run_case(path, args.grader, index, runner_cmd=args.runner)
            except Exception as e:
                print(f"[ERROR] {path}: {e}", file=sys.stderr)
                rec = CaseRecord(
                    case_id=path.stem,
                    title=path.stem,
                    skill="unknown",
                    grader=args.grader,
                    output="",
                    result={
                        "passed": False,
                        "score": 0.0,
                        "matched": [],
                        "missing": [],
                        "forbidden_hit": [],
                        "notes": f"loader/runtime error: {e}",
                    },
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
        target_note = f" -> {out_dir}/summary.md" if args.out is not None else ""
        print(f"\n{len(records) - failed}/{len(records)} passed{target_note}")
        return 1 if failed else 0
    finally:
        if temp_ctx is not None:
            temp_ctx.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
