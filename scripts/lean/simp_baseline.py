#!/usr/bin/env python3
"""W14-B2 pre-Phase-D @[simp] surface baseline capture.

Scans the reinforcement-learning Core/Bellman surface, captures every
simp-tagged declaration, writes an immutable JSON baseline, and emits a
human-readable routing summary for Phase D.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import os as _os
REPO = Path(_os.environ.get("LEAN_PROJECT_ROOT", Path.cwd())).resolve()
CORE_REL = _os.environ.get("SIMP_BASELINE_CORE_REL", "EASCI/ReinforcementLearning/Core.lean")
BELLMAN_REL = _os.environ.get("SIMP_BASELINE_BELLMAN_REL", "EASCI/ReinforcementLearning/Core/Bellman.lean")
TARGET_RELS = (
    tuple(
        t.strip()
        for t in _os.environ["SIMP_BASELINE_TARGETS"].split(",")
        if t.strip()
    )
    if _os.environ.get("SIMP_BASELINE_TARGETS")
    else (CORE_REL, BELLMAN_REL)
)
TARGET_PATHS = tuple(REPO / rel for rel in TARGET_RELS)
ROUTING_PATH = Path(
    _os.environ.get(
        "SIMP_BASELINE_ROUTING_PATH",
        str(REPO / "docs" / "refactor" / "wave-14" / "b2-phase2-script-routing-v2.json"),
    )
)
DEFAULT_JSON_OUT = REPO / "docs" / "refactor" / "findings" / "wave-14-b2-simp-baseline.json"
DEFAULT_SUMMARY_OUT = REPO / "docs" / "refactor" / "findings" / "wave-14-b2-simp-baseline.md"

DECL_HEAD_RE = re.compile(
    r"^(?:(?:protected|private|noncomputable|unsafe|partial|local|scoped)\s+)*"
    r"(theorem|lemma|def|instance)\b(.*)$"
)
NAME_TOKEN_RE = re.compile(r"[A-Za-z_][\w\']*(?:\.[A-Za-z_][\w\']*)*")
ATTRIBUTE_DIRECTIVE_RE = re.compile(r"^attribute\s+\[([^\]]+)\]\s+(.*)$")
NAMESPACE_RE = re.compile(r"^namespace\s+([A-Za-z_][\w\']*(?:\.[A-Za-z_][\w\']*)*)\s*$")
SECTION_RE = re.compile(r"^section\b")
END_RE = re.compile(r"^end\b(?:\s+([A-Za-z_][\w\']*(?:\.[A-Za-z_][\w\']*)*))?\s*$")


@dataclass
class DeclRecord:
    file: str
    line: int
    decl_kind: str
    decl_name: str
    qualified_name: str
    signature: str
    lhs_pattern: str | None

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "decl_kind": self.decl_kind,
            "decl_name": self.decl_name,
            "qualified_name": self.qualified_name,
            "signature": self.signature,
            "lhs_pattern": self.lhs_pattern,
        }


@dataclass
class DeclInfo:
    record: DeclRecord
    simp_sources: list[tuple[str, int]]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_ws(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def line_code_without_comments(line: str, block_depth: int) -> tuple[str, int]:
    """Remove Lean line/block comments for line-based declaration detection."""
    out: list[str] = []
    i = 0
    while i < len(line):
        pair = line[i : i + 2]
        if block_depth > 0:
            if pair == "/-":
                block_depth += 1
                i += 2
            elif pair == "-/":
                block_depth -= 1
                i += 2
            else:
                i += 1
            continue
        if pair == "--":
            break
        if pair == "/-":
            block_depth += 1
            i += 2
            continue
        out.append(line[i])
        i += 1
    return "".join(out), block_depth


class TopLevelScanState:
    __slots__ = ("block_depth", "brace", "bracket", "paren")

    def __init__(self) -> None:
        self.paren = 0
        self.bracket = 0
        self.brace = 0
        self.block_depth = 0

    def at_top_level(self) -> bool:
        return self.paren == 0 and self.bracket == 0 and self.brace == 0 and self.block_depth == 0


class TopLevelStringState:
    __slots__ = ("brace", "bracket", "paren")

    def __init__(self) -> None:
        self.paren = 0
        self.bracket = 0
        self.brace = 0

    def at_top_level(self) -> bool:
        return self.paren == 0 and self.bracket == 0 and self.brace == 0


def peel_attr_blocks(text: str) -> tuple[list[str], str]:
    payloads: list[str] = []
    rest = text.lstrip()
    while rest.startswith("@["):
        close = rest.find("]")
        if close < 0:
            break
        payloads.append(rest[2:close])
        rest = rest[close + 1 :].lstrip()
    return payloads, rest


def attr_payload_has_simp(payload: str) -> bool:
    tokens = [tok for tok in re.split(r"[\s,]+", payload.strip()) if tok]
    return "simp" in tokens


def parse_decl_head(text: str, line_number: int) -> tuple[str, str, str] | None:
    match = DECL_HEAD_RE.match(text)
    if not match:
        return None
    kind = match.group(1)
    rest = match.group(2).lstrip()
    name_match = NAME_TOKEN_RE.match(rest)
    if kind == "instance" and not name_match:
        name = f"<anonymous_instance@{line_number}>"
    elif not name_match:
        return None
    else:
        name = name_match.group(0)
    qualified_name = name
    return kind, name, qualified_name


def qualify_name(namespace_parts: list[str], name: str) -> str:
    if name.startswith("<anonymous_instance@"):
        return name
    if "." in name:
        return name
    if namespace_parts:
        return ".".join(namespace_parts + [name])
    return name


def scan_line_for_signature_delim(line: str, state: TopLevelScanState) -> int | None:
    i = 0
    while i < len(line):
        pair = line[i : i + 2]
        if state.block_depth > 0:
            if pair == "/-":
                state.block_depth += 1
                i += 2
            elif pair == "-/":
                state.block_depth -= 1
                i += 2
            else:
                i += 1
            continue
        if pair == "--":
            break
        if pair == "/-":
            state.block_depth += 1
            i += 2
            continue
        ch = line[i]
        if ch == "(":
            state.paren += 1
        elif ch == ")":
            state.paren = max(0, state.paren - 1)
        elif ch == "[":
            state.bracket += 1
        elif ch == "]":
            state.bracket = max(0, state.bracket - 1)
        elif ch == "{":
            state.brace += 1
        elif ch == "}":
            state.brace = max(0, state.brace - 1)
        elif state.at_top_level() and pair == ":=":
            return i + 2
        elif state.at_top_level() and line.startswith("where", i):
            before_ok = i == 0 or not (line[i - 1].isalnum() or line[i - 1] == "_")
            after_idx = i + 5
            after_ok = after_idx >= len(line) or not (
                line[after_idx].isalnum() or line[after_idx] == "_"
            )
            if before_ok and after_ok:
                return after_idx
        i += 1
    return None


def capture_signature(lines: list[str], start_line: int) -> str:
    state = TopLevelScanState()
    parts: list[str] = []
    for idx in range(start_line - 1, len(lines)):
        line = lines[idx]
        cut = scan_line_for_signature_delim(line, state)
        if cut is not None:
            parts.append(line[:cut])
            break
        parts.append(line)
    return "\n".join(parts).rstrip()


def trim_decl_prefix(signature: str) -> str:
    _, remainder = peel_attr_blocks(signature.lstrip())
    return remainder or signature.lstrip()


def last_top_level_colon(text: str) -> int | None:
    state = TopLevelStringState()
    colon_index: int | None = None
    i = 0
    while i < len(text):
        pair = text[i : i + 2]
        ch = text[i]
        if ch == "(":
            state.paren += 1
        elif ch == ")":
            state.paren = max(0, state.paren - 1)
        elif ch == "[":
            state.bracket += 1
        elif ch == "]":
            state.bracket = max(0, state.bracket - 1)
        elif ch == "{":
            state.brace += 1
        elif ch == "}":
            state.brace = max(0, state.brace - 1)
        elif state.at_top_level() and ch == ":" and pair != ":=":
            colon_index = i
        i += 1
    return colon_index


def first_top_level_relation(text: str) -> int | None:
    state = TopLevelStringState()
    i = 0
    while i < len(text):
        pair = text[i : i + 2]
        ch = text[i]
        if ch == "(":
            state.paren += 1
        elif ch == ")":
            state.paren = max(0, state.paren - 1)
        elif ch == "[":
            state.bracket += 1
        elif ch == "]":
            state.bracket = max(0, state.bracket - 1)
        elif ch == "{":
            state.brace += 1
        elif ch == "}":
            state.brace = max(0, state.brace - 1)
        elif state.at_top_level() and pair == ":=":
            return None
        elif state.at_top_level() and ch == "↔":
            return i
        elif state.at_top_level() and ch == "=":
            prev = text[i - 1] if i > 0 else ""
            if prev != ":":
                return i
        i += 1
    return None


def extract_lhs_pattern(signature: str) -> str | None:
    trimmed = trim_decl_prefix(signature)
    colon = last_top_level_colon(trimmed)
    if colon is None:
        return None
    proposition = trimmed[colon + 1 :]
    relation = first_top_level_relation(proposition)
    if relation is None:
        return None
    lhs = proposition[:relation]
    lhs_text = compact_ws(lhs)
    return lhs_text or None


def parse_attribute_targets(text: str) -> list[str]:
    return NAME_TOKEN_RE.findall(text)


def resolve_attribute_target(
    token: str,
    namespace_parts: tuple[str, ...],
    decls_by_qualified: dict[str, list[DeclInfo]],
    decls_by_simple: dict[str, list[DeclInfo]],
    attribute_line: int,
) -> DeclInfo | None:
    candidates: list[DeclInfo] = []
    if "." in token:
        candidates.extend(decls_by_qualified.get(token, []))
    else:
        if namespace_parts:
            qualified = ".".join((*namespace_parts, token))
            candidates.extend(decls_by_qualified.get(qualified, []))
        candidates.extend(decls_by_simple.get(token, []))
    unique: list[DeclInfo] = []
    seen: set[tuple[str, int]] = set()
    for cand in candidates:
        key = (cand.record.file, cand.record.line)
        if key not in seen:
            seen.add(key)
            unique.append(cand)
    earlier = [cand for cand in unique if cand.record.line <= attribute_line]
    pool = earlier or unique
    if not pool:
        return None
    if len(pool) == 1:
        return pool[0]
    pool.sort(key=lambda cand: (attribute_line - cand.record.line, cand.record.line))
    return pool[0]


def parse_file(path: Path) -> list[DeclInfo]:
    rel_path = path.relative_to(REPO).as_posix()
    lines = path.read_text(encoding="utf-8").splitlines()
    scope_stack: list[tuple[str, list[str] | None]] = []
    namespace_parts: list[str] = []
    block_depth = 0
    pending_simp_lines: list[int] = []
    decls: list[DeclInfo] = []
    decls_by_qualified: dict[str, list[DeclInfo]] = {}
    decls_by_simple: dict[str, list[DeclInfo]] = {}
    deferred_attrs: list[tuple[int, tuple[str, ...], list[str]]] = []

    for line_number, original_line in enumerate(lines, start=1):
        code, block_depth = line_code_without_comments(original_line, block_depth)
        stripped = code.strip()
        if not stripped:
            continue

        attr_payloads, remainder = peel_attr_blocks(stripped)
        inline_simp = any(attr_payload_has_simp(payload) for payload in attr_payloads)

        if attr_payloads and not remainder:
            if inline_simp:
                pending_simp_lines.append(line_number)
            continue

        directive_match = ATTRIBUTE_DIRECTIVE_RE.match(stripped)
        if directive_match:
            if attr_payload_has_simp(directive_match.group(1)):
                deferred_attrs.append(
                    (
                        line_number,
                        tuple(namespace_parts),
                        parse_attribute_targets(directive_match.group(2)),
                    )
                )
            pending_simp_lines.clear()
            continue

        namespace_match = NAMESPACE_RE.match(stripped)
        if namespace_match:
            parts = namespace_match.group(1).split(".")
            scope_stack.append(("namespace", parts))
            namespace_parts.extend(parts)
            pending_simp_lines.clear()
            continue

        if SECTION_RE.match(stripped):
            scope_stack.append(("section", None))
            pending_simp_lines.clear()
            continue

        if END_RE.match(stripped):
            if scope_stack:
                kind, payload = scope_stack.pop()
                if kind == "namespace" and payload:
                    del namespace_parts[-len(payload) :]
            pending_simp_lines.clear()
            continue

        decl_text = remainder if attr_payloads else stripped
        decl_head = parse_decl_head(decl_text, line_number)
        if decl_head is not None:
            kind, name, raw_qualified_name = decl_head
            qualified_name = qualify_name(namespace_parts, raw_qualified_name)
            signature = capture_signature(lines, line_number)
            record = DeclRecord(
                file=rel_path,
                line=line_number,
                decl_kind=kind,
                decl_name=name,
                qualified_name=qualified_name,
                signature=signature,
                lhs_pattern=extract_lhs_pattern(signature),
            )
            info = DeclInfo(record=record, simp_sources=[])
            if inline_simp:
                info.simp_sources.append(("inline", line_number))
            for attr_line in pending_simp_lines:
                info.simp_sources.append(("attribute-block", attr_line))
            pending_simp_lines.clear()
            decls.append(info)
            decls_by_qualified.setdefault(qualified_name, []).append(info)
            decls_by_simple.setdefault(name, []).append(info)
            continue

        pending_simp_lines.clear()

    for attr_line, namespace_at_attr, targets in deferred_attrs:
        for token in targets:
            info = resolve_attribute_target(
                token,
                namespace_at_attr,
                decls_by_qualified,
                decls_by_simple,
                attr_line,
            )
            if info is None:
                continue
            source = ("attribute-directive", attr_line)
            if source not in info.simp_sources:
                info.simp_sources.append(source)

    return [info for info in decls if info.simp_sources]


def capture_simp_entries(paths: Iterable[Path] = TARGET_PATHS) -> list[dict]:
    entries: list[dict] = []
    for path in paths:
        entries.extend(info.record.to_dict() for info in parse_file(path))
    entries.sort(key=lambda entry: (entry["file"], entry["line"], entry["qualified_name"]))
    return entries


def build_baseline_payload(entries: list[dict]) -> dict:
    counts_by_file: dict[str, int] = {}
    for entry in entries:
        counts_by_file[entry["file"]] = counts_by_file.get(entry["file"], 0) + 1
    return {
        "schema_version": 1,
        "generated_at_utc": utc_now(),
        "source_files": list(TARGET_RELS),
        "entry_count": len(entries),
        "counts_by_file": counts_by_file,
        "entries": entries,
    }


def load_routing() -> dict[tuple[int, str], dict]:
    raw = json.loads(ROUTING_PATH.read_text(encoding="utf-8"))
    routing: dict[tuple[int, str], dict] = {}
    for item in raw:
        routing[(int(item["line"]), item["name"])] = item
    return routing


def render_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    widths = [len(head) for head in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    fmt = "| " + " | ".join(f"{{:{width}}}" for width in widths) + " |"
    rule = "| " + " | ".join("-" * width for width in widths) + " |"
    lines = [fmt.format(*headers), rule]
    lines.extend(fmt.format(*row) for row in rows)
    return lines


def write_summary(entries: list[dict], path: Path) -> None:
    routing = load_routing()
    core_entries = [entry for entry in entries if entry["file"] == CORE_REL]
    bellman_entries = [entry for entry in entries if entry["file"] == BELLMAN_REL]
    migrated: list[dict] = []
    remain: list[dict] = []
    for entry in core_entries:
        route = routing.get((entry["line"], entry["decl_name"]))
        if route and str(route.get("verdict", "")).startswith("MIGRATE"):
            migrated.append({"entry": entry, "route": route})
        else:
            remain.append({"entry": entry, "route": route})

    lines: list[str] = []
    lines.append("# W14-B2 simp surface baseline")
    lines.append("")
    lines.append("Immutable pre-Phase-D snapshot generated by `scripts/w14b2_simp_baseline.py`.")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append(f"- `Core.lean`: {len(core_entries)}")
    lines.append(f"- `Core/Bellman.lean`: {len(bellman_entries)}")
    lines.append(f"- Total `@[simp]` declarations captured: {len(entries)}")
    lines.append("")
    lines.append("## Routed `@[simp]` decls migrating out of `Core.lean` (routing v2)")
    lines.append("")
    if migrated:
        rows = []
        for item in migrated:
            entry = item["entry"]
            route = item["route"]
            rows.append(
                [
                    entry["qualified_name"],
                    str(entry["line"]),
                    entry["decl_kind"],
                    str(route["slice_id"]),
                    str(route["verdict"]),
                ]
            )
        lines.extend(render_table(["Decl", "Line", "Kind", "Slice", "Verdict"], rows))
    else:
        lines.append("_None._")
    lines.append("")
    lines.append("## `@[simp]` decls remaining in `Core.lean` after Phase D")
    lines.append("")
    if remain:
        rows = []
        for item in remain:
            entry = item["entry"]
            route = item["route"]
            rows.append(
                [
                    entry["qualified_name"],
                    str(entry["line"]),
                    entry["decl_kind"],
                    str(route["slice_id"]) if route else "-",
                    str(route["verdict"]) if route else "UNROUTED",
                ]
            )
        lines.extend(render_table(["Decl", "Line", "Kind", "Slice", "Verdict"], rows))
    else:
        lines.append(
            "_None. Routing v2 marks every current `Core.lean` `@[simp]` declaration as `MIGRATE`._"
        )
    lines.append("")
    lines.append("## Pre-existing `Core/Bellman.lean` `@[simp]` decls")
    lines.append("")
    if bellman_entries:
        rows = []
        for entry in bellman_entries:
            rows.append(
                [
                    entry["qualified_name"],
                    str(entry["line"]),
                    entry["decl_kind"],
                ]
            )
        lines.extend(render_table(["Decl", "Line", "Kind"], rows))
    else:
        lines.append("_None._")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_baseline_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture the W14-B2 pre-Phase-D @[simp] baseline.")
    parser.add_argument(
        "--json-out",
        type=Path,
        default=DEFAULT_JSON_OUT,
        help=f"Path to write the baseline JSON (default: {DEFAULT_JSON_OUT.relative_to(REPO)})",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        default=DEFAULT_SUMMARY_OUT,
        help=f"Path to write the summary markdown (default: {DEFAULT_SUMMARY_OUT.relative_to(REPO)})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entries = capture_simp_entries()
    payload = build_baseline_payload(entries)
    write_baseline_json(payload, args.json_out)
    write_summary(entries, args.summary_out)
    core_count = payload["counts_by_file"].get(CORE_REL, 0)
    bellman_count = payload["counts_by_file"].get(BELLMAN_REL, 0)
    print(
        f"Wrote {len(entries)} simp baseline entries ({core_count} Core, {bellman_count} Bellman)."
    )
    print(f"JSON: {args.json_out.relative_to(REPO)}")
    print(f"Summary: {args.summary_out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
