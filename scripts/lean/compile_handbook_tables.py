#!/usr/bin/env python3
"""Compile structured tables from proof-skills handbooks and dialect manifests.

Extracts the 3 canonical tables (Goal-Shape Templates, Intent-to-Tactic Phrasebook,
and Error-to-Fix Table) from ``references/*-handbook.md`` plus cross-prover
mechanisms from ``references/dialects/*.json`` into a single offline index at
``vendor/itp-ontology/handbook-tables.v1.json``.

Strict 7-bit ASCII output only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_REFS_DIR = REPO_ROOT / "references"
DEFAULT_DIALECTS_DIR = DEFAULT_REFS_DIR / "dialects"
DEFAULT_OUT_PATH = REPO_ROOT / "vendor" / "itp-ontology" / "handbook-tables.v1.json"

SCHEMA_VERSION = "1.0.0"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")


def _ascii_clean(text: str) -> str:
    """Convert any non-ASCII code points to deterministic 7-bit ASCII."""
    replacements = {
        "\u2014": "--",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
        "\u202f": " ",
        "\u2192": "->",
        "\u2190": "<-",
        "\u2194": "<->",
        "\u21d2": "=>",
        "\u21d4": "<=>",
        "\u2200": "forall ",
        "\u2203": "exists ",
        "\u2264": "<=",
        "\u2265": ">=",
        "\u2260": "!=",
        "\u2208": "in",
        "\u2209": "notin",
        "\u2286": "subset",
        "\u2211": "sum",
        "\u222b": "int",
        "\u2297": "otimes",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("ascii", errors="ignore").decode("ascii").strip()


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


def _split_md_row(line: str) -> list[str]:
    """Split a Markdown table row while respecting escaped pipes ``\\|``."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    placeholder = "\x00PIPE\x00"
    safe = stripped.replace(r"\|", placeholder)
    cells = [c.replace(placeholder, "|").strip() for c in safe.split("|")]
    return [_ascii_clean(c) for c in cells]


def _is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(bool(re.match(r"^:?-{2,}:?$", c.strip())) for c in cells if c.strip())


def _classify_section(heading_text: str) -> str | None:
    lower = heading_text.lower()
    if "goal-shape" in lower or "(templates)" in lower or "table 1:" in lower:
        return "goal_shape_templates"
    if (
        "intent-to-tactic" in lower
        or "(phrasebook)" in lower
        or "intent-first" in lower
        or "table 2:" in lower
    ):
        return "intent_phrasebook"
    if (
        "error-to-fix" in lower
        or "(errors)" in lower
        or "error / kernel bottleneck" in lower
        or "table 3:" in lower
    ):
        return "error_to_fix"
    return None


def _normalize_row(table_kind: str, headers: list[str], cells: list[str], handbook_id: str) -> dict[str, Any]:
    raw_map: dict[str, str] = {}
    for idx, header in enumerate(headers):
        val = cells[idx] if idx < len(cells) else ""
        raw_map[header] = val

    c0 = cells[0] if len(cells) > 0 else ""
    c1 = cells[1] if len(cells) > 1 else ""
    c2 = cells[2] if len(cells) > 2 else ""

    if table_kind == "goal_shape_templates":
        return {
            "handbook": handbook_id,
            "goal_shape": c0,
            "route_or_concordance": c1,
            "template": c2,
            "columns": raw_map,
        }
    if table_kind == "intent_phrasebook":
        return {
            "handbook": handbook_id,
            "intent": c0,
            "tactic_or_idiom": c1,
            "notes": c2,
            "columns": raw_map,
        }
    return {
        "handbook": handbook_id,
        "error_pattern": c0,
        "cause": c1,
        "fix": c2,
        "columns": raw_map,
    }


def parse_handbook_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = _parse_frontmatter(text)
    handbook_id = _ascii_clean(meta.get("name") or path.stem)
    skill_ref = _ascii_clean(meta.get("extracted_from") or f"skills/{handbook_id.removesuffix('-handbook')}/SKILL.md")

    result: dict[str, Any] = {
        "handbook_id": handbook_id,
        "file": f"references/{path.name}",
        "skill_ref": skill_ref,
        "goal_shape_templates": [],
        "intent_phrasebook": [],
        "error_to_fix": [],
    }

    lines = text.splitlines()
    current_kind: str | None = None
    current_level: int = 0
    in_code_block = False
    table_headers: list[str] | None = None
    seen_separator = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        h_match = _HEADING_RE.match(line)
        if h_match:
            level = len(h_match.group(1))
            heading_title = h_match.group(2)
            classified = _classify_section(heading_title)
            if classified is not None:
                current_kind = classified
                current_level = level
                table_headers = None
                seen_separator = False
            elif current_kind is not None and level <= current_level:
                current_kind = None
                table_headers = None
                seen_separator = False
            continue

        if current_kind is None:
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = _split_md_row(stripped)
            if not any(cells):
                continue
            if table_headers is None:
                table_headers = cells
                seen_separator = False
            elif not seen_separator and _is_separator_row(cells):
                seen_separator = True
            elif seen_separator:
                row_obj = _normalize_row(current_kind, table_headers, cells, handbook_id)
                result[current_kind].append(row_obj)
        else:
            if seen_separator and not stripped:
                table_headers = None
                seen_separator = False

    return result


def compile_handbook_tables(
    refs_dir: Path = DEFAULT_REFS_DIR,
    dialects_dir: Path = DEFAULT_DIALECTS_DIR,
) -> dict[str, Any]:
    goal_shape_templates: list[dict[str, Any]] = []
    intent_phrasebook: list[dict[str, Any]] = []
    error_to_fix: list[dict[str, Any]] = []
    by_handbook: dict[str, dict[str, Any]] = {}

    handbook_files = sorted(refs_dir.glob("*-handbook.md")) if refs_dir.exists() else []
    for hb_path in handbook_files:
        parsed = parse_handbook_file(hb_path)
        total_rows = (
            len(parsed["goal_shape_templates"])
            + len(parsed["intent_phrasebook"])
            + len(parsed["error_to_fix"])
        )
        if total_rows == 0:
            continue
        hb_id = parsed["handbook_id"]
        by_handbook[hb_id] = {
            "file": parsed["file"],
            "skill_ref": parsed["skill_ref"],
            "goal_shape_count": len(parsed["goal_shape_templates"]),
            "intent_count": len(parsed["intent_phrasebook"]),
            "error_count": len(parsed["error_to_fix"]),
            "goal_shape_templates": parsed["goal_shape_templates"],
            "intent_phrasebook": parsed["intent_phrasebook"],
            "error_to_fix": parsed["error_to_fix"],
        }
        goal_shape_templates.extend(parsed["goal_shape_templates"])
        intent_phrasebook.extend(parsed["intent_phrasebook"])
        error_to_fix.extend(parsed["error_to_fix"])

    dialects: dict[str, dict[str, Any]] = {}
    dialect_files = sorted(dialects_dir.glob("*.json")) if dialects_dir.exists() else []
    for d_path in dialect_files:
        try:
            raw = json.loads(d_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        dialect_id = _ascii_clean(str(raw.get("dialect_id") or d_path.stem))
        mechanisms = []
        for m in raw.get("mechanisms", []):
            mechanisms.append(
                {
                    "id": _ascii_clean(str(m.get("id", ""))),
                    "canonical_name": _ascii_clean(str(m.get("canonical_name", ""))),
                    "category": _ascii_clean(str(m.get("category", ""))),
                    "dialect_tactics": [_ascii_clean(str(t)) for t in m.get("dialect_tactics", [])],
                    "dialect_syntax_pattern": _ascii_clean(str(m.get("dialect_syntax_pattern", ""))),
                    "dialect_idiom": _ascii_clean(str(m.get("dialect_idiom", ""))),
                    "dialect_pitfalls": [_ascii_clean(str(p)) for p in m.get("dialect_pitfalls", [])],
                    "lean4_target_tactics": [_ascii_clean(str(t)) for t in m.get("lean4_target_tactics", [])],
                    "lean4_target_syntax": _ascii_clean(str(m.get("lean4_target_syntax", ""))),
                }
            )
        dialects[dialect_id] = {
            "dialect_id": dialect_id,
            "prover_key": _ascii_clean(str(raw.get("prover_key", dialect_id))),
            "display_name": _ascii_clean(str(raw.get("display_name", dialect_id))),
            "foundation": _ascii_clean(str(raw.get("foundation", ""))),
            "file_extension": _ascii_clean(str(raw.get("file_extension", ""))),
            "adapter_skill": _ascii_clean(str(raw.get("adapter_skill", ""))),
            "mechanisms_count": len(mechanisms),
            "mechanisms": mechanisms,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "version": SCHEMA_VERSION,
        "description": "Compiled Goal-Shape Templates, Intent-to-Tactic Phrasebook, Error-to-Fix tables, and Cross-ITP Dialect Mechanisms.",
        "handbooks_count": len(by_handbook),
        "dialects_count": len(dialects),
        "counts": {
            "goal_shape_templates": len(goal_shape_templates),
            "intent_phrasebook": len(intent_phrasebook),
            "error_to_fix": len(error_to_fix),
            "total_rows": len(goal_shape_templates) + len(intent_phrasebook) + len(error_to_fix),
        },
        "goal_shape_templates": goal_shape_templates,
        "intent_phrasebook": intent_phrasebook,
        "error_to_fix": error_to_fix,
        "by_handbook": by_handbook,
        "dialects": dialects,
    }


def self_test() -> int:
    payload = compile_handbook_tables()
    assert payload["schema_version"] == SCHEMA_VERSION, "schema_version mismatch"
    assert payload["handbooks_count"] >= 15, f"expected >= 15 handbooks, got {payload['handbooks_count']}"
    assert payload["dialects_count"] >= 6, f"expected >= 6 dialects, got {payload['dialects_count']}"
    assert len(payload["goal_shape_templates"]) >= 50, "too few goal_shape_templates"
    assert len(payload["intent_phrasebook"]) >= 50, "too few intent_phrasebook rows"
    assert len(payload["error_to_fix"]) >= 50, "too few error_to_fix rows"
    encoded = json.dumps(payload, indent=2, ensure_ascii=True)
    assert all(ord(ch) < 128 for ch in encoded), "non-ASCII characters leaked into output"
    print(
        json.dumps(
            {
                "status": "PASS",
                "handbooks_count": payload["handbooks_count"],
                "dialects_count": payload["dialects_count"],
                "counts": payload["counts"],
            }
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile handbook tables and dialect mechanisms into handbook-tables.v1.json."
    )
    parser.add_argument(
        "--refs-dir",
        type=Path,
        default=DEFAULT_REFS_DIR,
        help="Path to references directory containing *-handbook.md files.",
    )
    parser.add_argument(
        "--dialects-dir",
        type=Path,
        default=DEFAULT_DIALECTS_DIR,
        help="Path to references/dialects directory containing *.json files.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_PATH,
        help="Output JSON path (default: vendor/itp-ontology/handbook-tables.v1.json).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that the existing output file is up-to-date.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in self-test suite.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    payload = compile_handbook_tables(args.refs_dir, args.dialects_dir)
    serialized = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"

    if args.check:
        if not args.out.exists():
            print(f"FAIL: {args.out} does not exist", file=sys.stderr)
            return 1
        current = args.out.read_text(encoding="utf-8")
        if current != serialized:
            print(f"FAIL: {args.out} is out of date with handbooks", file=sys.stderr)
            return 1
        print(f"OK: {args.out} is up-to-date ({payload['counts']['total_rows']} rows)")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(serialized, encoding="ascii")
    print(
        json.dumps(
            {
                "status": "OK",
                "output": str(args.out),
                "handbooks_count": payload["handbooks_count"],
                "dialects_count": payload["dialects_count"],
                "counts": payload["counts"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
