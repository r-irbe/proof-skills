#!/usr/bin/env python3
"""Canary YAML Benchmark Validation Harness (`check-validation` / `check-canary`) (Proposal 10C).

Validates `leanprover/skills`-style `tests/*.yaml` canary benchmark definitions across skills,
verifying schema completeness (`prompt`, `expected_patterns`, `forbidden_patterns`, `skill`)
and optionally evaluating candidate responses against the canary assertions.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_CANARY_KEYS: tuple[str, ...] = ("skill", "prompt", "expected_patterns")


def _parse_simple_yaml(text: str) -> dict:
    """Minimal dependency-free YAML subset parser for canary `.yaml` files (falls back to PyYAML if installed)."""
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    result: dict = {}
    current_list_key: str | None = None
    for raw_ln in text.splitlines():
        ln = raw_ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if ln.startswith("- ") and current_list_key:
            val = ln[2:].strip().strip("'\"")
            result.setdefault(current_list_key, []).append(val)
            continue
        if ":" in ln:
            k, v = ln.split(":", 1)
            key = k.strip()
            val = v.strip().strip("'\"")
            if val == "":
                current_list_key = key
                result.setdefault(key, [])
            else:
                current_list_key = None
                result[key] = val
    return result


def validate_canary_spec(data: dict, source: str = "") -> dict:
    """Validate that a canary YAML spec has all required keys and valid regex patterns."""
    skill_name = data.get("skill", "")
    if not skill_name and source:
        parts = Path(source).parts
        if "skills" in parts:
            idx = parts.index("skills")
            if idx + 1 < len(parts):
                skill_name = parts[idx + 1]

    is_upstream_repo_canary = (
        bool(data.get("repo"))
        and bool(data.get("sha"))
        and bool(data.get("prompt"))
        and bool(data.get("description"))
    )
    if is_upstream_repo_canary and "expected_patterns" not in data:
        missing: list[str] = []
    else:
        missing = [k for k in REQUIRED_CANARY_KEYS if k not in data or not data[k]]

    invalid_regexes: list[str] = []
    for key in ("expected_patterns", "forbidden_patterns"):
        pats = data.get(key) or []
        if isinstance(pats, str):
            pats = [pats]
        for pat in pats:
            try:
                re.compile(str(pat))
            except re.error as exc:
                invalid_regexes.append(f"{key}:{pat} ({exc})")

    ok = len(missing) == 0 and len(invalid_regexes) == 0
    return {
        "ok": ok,
        "source": source,
        "skill": skill_name,
        "missing_keys": missing,
        "invalid_regexes": invalid_regexes,
    }


def evaluate_canary_response(spec: dict, response_text: str) -> dict:
    """Evaluate `response_text` against `expected_patterns` and `forbidden_patterns`."""
    expected = spec.get("expected_patterns") or []
    forbidden = spec.get("forbidden_patterns") or []
    if isinstance(expected, str):
        expected = [expected]
    if isinstance(forbidden, str):
        forbidden = [forbidden]

    missing_expected = [
        pat for pat in expected if not re.search(str(pat), response_text)
    ]
    matched_forbidden = [
        pat for pat in forbidden if re.search(str(pat), response_text)
    ]
    passed = len(missing_expected) == 0 and len(matched_forbidden) == 0
    return {
        "passed": passed,
        "missing_expected": missing_expected,
        "matched_forbidden": matched_forbidden,
    }


def scan_canary_directory(root_dir: Path) -> dict:
    root_path = Path(root_dir)
    skills_sub = root_path / "skills"
    search_base = skills_sub if skills_sub.is_dir() else root_path
    yaml_files = sorted(search_base.glob("**/tests/*.yaml")) + sorted(
        search_base.glob("**/tests/*.yml")
    )
    if not yaml_files and search_base == root_path:
        yaml_files = sorted(root_path.glob("*.yaml")) + sorted(root_path.glob("*.yml"))
    results: list[dict] = []
    for yf in yaml_files:
        data = _parse_simple_yaml(yf.read_text(encoding="utf-8"))
        results.append(validate_canary_spec(data, source=str(yf)))
    invalid = [r for r in results if not r["ok"]]
    return {
        "ok": len(invalid) == 0,
        "files_scanned": len(results),
        "invalid_count": len(invalid),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("check-validation", "check-canary", "check_canary_validation"):
        argv.pop(0)
    parser = argparse.ArgumentParser(
        prog="lean-skills check-validation",
        description="Validate leanprover/skills-style canary YAML benchmark specifications",
    )
    parser.add_argument(
        "target",
        nargs="?",
        type=Path,
        default=None,
        help="Directory or YAML file to validate",
    )
    parser.add_argument(
        "--root",
        dest="root_opt",
        type=Path,
        default=None,
        help="Repository or skills root directory to validate",
    )
    args = parser.parse_args(argv)
    target = args.root_opt or args.target or (Path(__file__).resolve().parents[2] / "skills")
    if target.is_file():
        data = _parse_simple_yaml(target.read_text(encoding="utf-8"))
        res = validate_canary_spec(data, source=str(target))
    else:
        res = scan_canary_directory(target)
    print(json.dumps(res, indent=2))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
