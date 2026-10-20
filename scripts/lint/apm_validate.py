#!/usr/bin/env python3
"""apm-validate — local-only validator for the APM manifest + skill collection.

Checks that this repository is a well-formed APM "skill collection"
package per https://microsoft.github.io/apm/reference/package-types/ :

  1. apm.yml exists at the repo root.
  2. apm.yml has the required keys: name, version, description.
  3. Every skills/<name>/SKILL.md has frontmatter with `name` and
     `description` (the agentskills.io minimum).
  4. The skills/<name>/ directory name matches `name:` in its
     SKILL.md frontmatter.
  5. No skill name is duplicated.

This script does NOT require the `apm` CLI to be installed — it is a
hermetic pre-publish check that runs in CI and locally.

Usage:
    python3 scripts/lint/apm_validate.py                # exit 0/1
    python3 scripts/lint/apm_validate.py --report       # human report
    python3 scripts/lint/apm_validate.py --json         # CI-friendly
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
    _HAVE_YAML = True
except ImportError:  # pragma: no cover - stdlib fallback when PyYAML is absent
    yaml = None  # type: ignore
    _HAVE_YAML = False

REPO_ROOT = Path(__file__).resolve().parents[2]
APM_YML = REPO_ROOT / "apm.yml"
SKILLS_DIR = REPO_ROOT / "skills"

REQUIRED_APM_KEYS = ("name", "version", "description")
REQUIRED_SKILL_KEYS = ("name", "description")


def _stdlib_yaml_load(text: str) -> dict:
    """Minimal stdlib YAML loader for apm.yml and SKILL.md frontmatter."""
    raw_lines = text.splitlines()
    out: dict = {}
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent > 0 or ":" not in line:
            i += 1
            continue
        key_part, val_part = line.split(":", 1)
        key = key_part.strip()
        val = val_part.strip()
        if val in ("|", "|-", "|+", ">", ">-", ">+"):
            block_lines: list[str] = []
            block_indent: int | None = None
            j = i + 1
            while j < len(raw_lines):
                bl = raw_lines[j]
                s_bl = bl.lstrip(" ")
                this_indent = len(bl) - len(s_bl)
                if s_bl == "":
                    block_lines.append("")
                    j += 1
                    continue
                if this_indent <= indent:
                    break
                if block_indent is None:
                    block_indent = this_indent
                block_lines.append(
                    bl[block_indent:] if this_indent >= block_indent else s_bl
                )
                j += 1
            while block_lines and block_lines[-1] == "":
                block_lines.pop()
            sep = " " if val.startswith(">") else "\n"
            out[key] = sep.join(block_lines) + ("\n" if not val.endswith("-") else "")
            i = j
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        out[key] = val
        i += 1
    return out


def _safe_load_yaml(text: str) -> dict | None:
    if _HAVE_YAML and yaml is not None:
        try:
            res = yaml.safe_load(text)
            return res if isinstance(res, dict) else {}
        except yaml.YAMLError:
            return None
    return _stdlib_yaml_load(text)


def load_yaml_frontmatter(path: Path) -> dict | None:
    """Extract the YAML frontmatter block from a SKILL.md."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    return _safe_load_yaml(match.group(1))


def validate() -> tuple[list[str], dict]:
    """Return (errors, summary). Empty errors => package is valid."""
    errors: list[str] = []
    summary: dict = {
        "apm_yml": False,
        "skill_count": 0,
        "valid_skills": 0,
        "duplicate_names": [],
    }

    # 1. apm.yml present
    if not APM_YML.exists():
        errors.append("MISSING apm.yml at repo root")
        return errors, summary

    manifest = _safe_load_yaml(APM_YML.read_text(encoding="utf-8"))
    if manifest is None:
        errors.append("apm.yml is not valid YAML")
        return errors, summary

    summary["apm_yml"] = True

    # 2. Required keys
    for key in REQUIRED_APM_KEYS:
        if key not in manifest:
            errors.append(f"apm.yml MISSING required key: {key}")

    # 3 + 4 + 5. SKILL.md sweep
    if not SKILLS_DIR.is_dir():
        errors.append(f"MISSING skills/ directory at {SKILLS_DIR}")
        return errors, summary

    seen_names: dict[str, Path] = {}
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        # Skip _overrides — those are dispatch-time, not first-party.
        if "_overrides" in skill_md.parts:
            continue
        summary["skill_count"] += 1
        rel = skill_md.relative_to(REPO_ROOT)
        fm = load_yaml_frontmatter(skill_md)
        if fm is None:
            errors.append(f"{rel}: missing or invalid YAML frontmatter")
            continue
        missing = [k for k in REQUIRED_SKILL_KEYS if k not in fm]
        if missing:
            errors.append(f"{rel}: missing frontmatter keys: {missing}")
            continue
        # Directory name == frontmatter name
        dir_name = skill_md.parent.name
        fm_name = str(fm["name"]).strip()
        if fm_name != dir_name:
            errors.append(
                f"{rel}: frontmatter name={fm_name!r} != dir {dir_name!r}"
            )
            continue
        # Duplicate name detection
        if fm_name in seen_names:
            errors.append(
                f"{rel}: duplicate skill name {fm_name!r} "
                f"(also at {seen_names[fm_name]})"
            )
            summary["duplicate_names"].append(fm_name)
            continue
        seen_names[fm_name] = rel
        summary["valid_skills"] += 1

    return errors, summary


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--report", action="store_true",
                   help="Print human-readable report (always exits 0 unless --strict)")
    p.add_argument("--json", action="store_true",
                   help="Emit JSON summary (exit 0/1 by validity)")
    p.add_argument("--strict", action="store_true",
                   help="Fail with exit code 1 if any validation errors are found")
    args = p.parse_args()

    errors, summary = validate()

    if args.json:
        print(json.dumps({"errors": errors, "summary": summary}, indent=2))
        return 0 if not errors else 1

    if args.report or args.strict:
        print(f"apm.yml present .......... {summary['apm_yml']}")
        print(f"skills discovered ........ {summary['skill_count']}")
        print(f"skills validated ......... {summary['valid_skills']}")
        if errors:
            print(f"\nERRORS ({len(errors)}):")
            for e in errors:
                print(f"  - {e}")
            if args.strict:
                return 1
        else:
            print("\nOK -- package is a valid APM skill collection.")
        return 0

    # Default: silent on success, errors to stderr, exit 0/1.
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
