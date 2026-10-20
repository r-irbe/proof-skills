#!/usr/bin/env python3
# executable-bit audit 2026-09-29: mode 0755 verified (stat + git index)
"""SALA anchor resolver (TASK-LIB-01).

Maps statute-style semantic anchors (SALA) to text at read time, per
docs/investigation-garden/source-materials-librarian-pipeline-plan.md:

  - Section 3.2: anchor grammar. Canonical form is pure ASCII (INV-001):
    BOOK-ID " s" unit ("." unit)* [ " p" para [ "s" sentence ] ].
  - Section 3.3: one anchors.v1.json per book under
    source-materials/books/<BOOK-ID>/, binding each anchor to its current
    physical realization (print page, source file, heading, leittext,
    char band).
  - Section 3.4: resolution and drift protocol. Locate the anchor's
    leittext (normalized whitespace, fuzzy threshold 0.92), materialize
    half-open to the next anchor boundary, verify the char band, and on
    any miss emit an anchor_drift finding. The fragment is never silently
    re-mapped: text drift repairs the table, not the callers.
  - Section 6: fragment intervals are half-open; a fragment never spans
    two sections, so an end anchor outside the start unit clamps the span
    at the unit boundary and records the clamp as a finding.

Exit codes: 0 resolved, 2 drift (fail-closed for pipelines), 1 usage/IO.

Strict 7-bit ASCII only (INV-001). Standard library only.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FUZZY_THRESHOLD = 0.92

SALA_PATTERN = re.compile(r"^([A-Z0-9_-]+) s([0-9]+(?:\.[0-9]+)*) p([0-9]+)(?:s([0-9]+))?$")

# Unicode punctuation folds to ASCII; legal-typography glyphs carry no
# semantics (plan section 3.2), so normalization erases them.
_ASCII_FOLD = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2212": "-",
    "\u00a0": " ",
    "\u00a7": "s",
    "\u00b6": "p",
}

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_DRIFT = 2


@dataclass(frozen=True)
class Anchor:
    """A parsed SALA address (plan section 3.2)."""

    book: str
    unit_path: tuple[int, ...]
    para: int | None
    sentence: int | None


@dataclass(frozen=True)
class AnchorRow:
    """One row of a book's anchor table (plan section 3.3)."""

    anchor: str
    print_page: int
    source_file: str
    heading_text: str
    leittext: str
    char_band: tuple[int, int]
    parsed: Anchor


def parse_anchor(text: str) -> Anchor:
    """Parse a schema-canonical SALA address; ValueError on malformation.

    The fragment schema's sala_anchor pattern requires the paragraph
    ordinal (p), so the resolver enforces it even though the plan's
    conceptual grammar marks it optional; every anchor-table row and
    fragment address carries a paragraph.
    """
    match = SALA_PATTERN.match(text.strip()) if isinstance(text, str) else None
    if match is None:
        raise ValueError(f"malformed SALA anchor: {text!r}")
    book, units, para, sentence = match.groups()
    unit_path = tuple(int(part) for part in units.split("."))
    return Anchor(
        book=book,
        unit_path=unit_path,
        para=int(para),
        sentence=int(sentence) if sentence is not None else None,
    )


def format_anchor(anchor: Anchor) -> str:
    """Render the canonical ASCII form of an address."""
    units = ".".join(str(u) for u in anchor.unit_path)
    text = f"{anchor.book} s{units}"
    if anchor.para is not None:
        text += f" p{anchor.para}"
        if anchor.sentence is not None:
            text += f"s{anchor.sentence}"
    return text


def normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Whitespace-collapsed, ASCII-folded text plus an original-index map.

    The map returns, for each normalized character, the index of the
    original character it came from, so located offsets convert back to
    byte-accurate positions in the raw source file.
    """
    out: list[str] = []
    idx: list[int] = []
    pending_space = False
    for i, ch in enumerate(text):
        folded = _ASCII_FOLD.get(ch, ch)
        if folded.isspace():
            if not pending_space:
                out.append(" ")
                idx.append(i)
            pending_space = True
            continue
        pending_space = False
        out.append(folded)
        idx.append(i)
    return "".join(out), idx


def _map_span(idx: list[int], start: int, end: int) -> tuple[int, int]:
    """Convert a normalized [start, end) span to original offsets."""
    if end <= start:
        return (idx[start], idx[start]) if 0 <= start < len(idx) else (0, 0)
    return (idx[start], idx[end - 1] + 1)


@dataclass(frozen=True)
class Located:
    """A leittext hit in one source file (original offsets)."""

    start: int
    end: int
    fuzzy: bool


def locate_leittext(
    source_text: str, leittext: str, threshold: float = FUZZY_THRESHOLD
) -> Located | None:
    """Locate a leittext in source text (plan section 3.4 step 1).

    First an exact match on whitespace-normalized, ASCII-folded text; on
    miss a deterministic token-window scan (difflib ratio >= threshold)
    relocates the moved passage without re-mapping the table.
    """
    norm_src, idx = normalize_with_map(source_text)
    norm_leit, _ = normalize_with_map(leittext)
    norm_leit = norm_leit.strip()
    if not norm_leit:
        return None
    hit = norm_src.find(norm_leit)
    if hit >= 0:
        start, end = _map_span(idx, hit, hit + len(norm_leit))
        return Located(start=start, end=end, fuzzy=False)
    return _fuzzy_locate(norm_src, idx, norm_leit, threshold)


def _fuzzy_locate(
    norm_src: str, idx: list[int], norm_leit: str, threshold: float
) -> Located | None:
    """Deterministic earliest-token-window fuzzy search.

    The window slides one source token at a time and always spans the
    same token count as the leittext; the first window scoring at or
    above the threshold wins, so relocation is reproducible.
    """
    leit_tokens = re.findall(r"\S+", norm_leit)
    src_token_starts = [m.start() for m in re.finditer(r"\S+", norm_src)]
    src_token_ends = [m.end() for m in re.finditer(r"\S+", norm_src)]
    n = len(leit_tokens)
    if n == 0 or len(src_token_starts) < n:
        return None
    leit_joined = " ".join(leit_tokens)
    for i in range(len(src_token_starts) - n + 1):
        start_char = src_token_starts[i]
        end_char = src_token_ends[i + n - 1]
        candidate = norm_src[start_char:end_char]
        ratio = difflib.SequenceMatcher(None, leit_joined, candidate).ratio()
        if ratio >= threshold:
            start, end = _map_span(idx, start_char, end_char)
            return Located(start=start, end=end, fuzzy=True)
    return None


def load_anchor_table(path: Path | str, expect_book: str | None = None) -> list[AnchorRow]:
    """Load and validate one book's anchors.v1.json (plan section 3.3)."""
    table_path = Path(path)
    payload = json.loads(table_path.read_text(encoding="utf-8"))
    rows: list[AnchorRow] = []
    for raw in payload.get("rows", []):
        parsed = parse_anchor(raw["anchor"])
        if expect_book is not None and parsed.book != expect_book:
            raise ValueError(f"anchor book mismatch: {raw['anchor']!r} is not {expect_book!r}")
        band = raw.get("char_band", {})
        rows.append(
            AnchorRow(
                anchor=raw["anchor"],
                print_page=int(raw.get("print_page", 0)),
                source_file=raw["source_file"],
                heading_text=raw.get("heading_text", ""),
                leittext=raw["leittext"],
                char_band=(int(band["min"]), int(band["max"])),
                parsed=parsed,
            )
        )
    return rows


def _finding(anchor: str, detail: str, **extra: Any) -> dict[str, Any]:
    """One anchor_drift finding row (plan section 3.4 step 4)."""
    entry: dict[str, Any] = {
        "kind": "anchor_drift",
        "anchor": anchor,
        "detail": detail,
    }
    entry.update(extra)
    return entry


def _locate_row(rows: list[AnchorRow], address: Anchor) -> AnchorRow | None:
    target = format_anchor(address)
    for row in rows:
        if row.anchor == target:
            return row
    return None


def resolve(
    bookdir: Path | str,
    start_anchor: str,
    end_anchor: str | None = None,
    emit_text: bool = False,
) -> dict[str, Any]:
    """Resolve one SALA address (optionally to an end anchor) to text.

    Half-open interval per plan section 3.4; end anchor omitted means
    to the end of the start anchor's unit. Any miss, band violation, or
    carving violation yields an anchor_drift finding and status "drift";
    the table is never silently re-mapped.
    """
    book_path = Path(bookdir)
    parsed_start = parse_anchor(start_anchor)
    findings: list[dict[str, Any]] = []
    try:
        rows = load_anchor_table(book_path / "anchors.v1.json", expect_book=parsed_start.book)
    except FileNotFoundError:
        return {
            "status": "drift",
            "book": parsed_start.book,
            "start_anchor": start_anchor,
            "end_anchor": end_anchor,
            "findings": [_finding(start_anchor, "anchor-table-missing")],
        }

    start_row = _locate_row(rows, parsed_start)
    if start_row is None:
        return {
            "status": "drift",
            "book": parsed_start.book,
            "start_anchor": start_anchor,
            "end_anchor": end_anchor,
            "findings": [_finding(start_anchor, "anchor-not-in-table")],
        }

    source_path = book_path / start_row.source_file
    source_text = source_path.read_text(encoding="utf-8", errors="strict")
    located = locate_leittext(source_text, start_row.leittext)
    if located is None:
        return _drift_result(
            parsed_start, end_anchor, start_row, findings=[_finding(start_anchor, "leittext-miss")]
        )

    start_pos = located.start

    parsed_end: Anchor | None = None
    if end_anchor is not None:
        parsed_end = parse_anchor(end_anchor)
        if parsed_end.unit_path != parsed_start.unit_path:
            # Carving discipline (plan section 6): a fragment never spans
            # two sections. Clamp half-open at the next unit boundary and
            # record the clamp visibly.
            findings.append(_finding(end_anchor, "end-anchor-out-of-unit"))

    end_pos = _end_boundary(rows, source_text, start_row, parsed_end, findings)
    materialized = source_text[start_pos:end_pos]

    band_min, band_max = start_row.char_band
    if not (band_min <= len(materialized) <= band_max):
        findings.append(
            _finding(
                start_anchor,
                "char-band-violation",
                expected={"min": band_min, "max": band_max},
                actual=len(materialized),
            )
        )

    result: dict[str, Any] = {
        "status": "drift" if findings else "resolved",
        "book": parsed_start.book,
        "start_anchor": start_anchor,
        "end_anchor": end_anchor,
        "source_file": str(source_path),
        "char_start": start_pos,
        "char_end": end_pos,
        "length": len(materialized),
        "located_fuzzy": located.fuzzy,
        "findings": findings,
        "text": materialized,
    }
    return result


def _drift_result(
    parsed_start: Anchor,
    end_anchor: str | None,
    start_row: AnchorRow | None,
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "status": "drift",
        "book": parsed_start.book,
        "start_anchor": format_anchor(parsed_start),
        "end_anchor": end_anchor,
        "source_file": start_row.source_file if start_row else None,
        "findings": findings,
    }


def _end_boundary(
    rows: list[AnchorRow],
    source_text: str,
    start_row: AnchorRow,
    parsed_end: Anchor | None,
    findings: list[dict[str, Any]],
) -> int:
    """Half-open end offset per plan sections 3.4 and 6.

    Explicit in-unit end anchor: that row's leittext start. Explicit
    out-of-unit end anchor (already flagged): clamp at the next unit
    boundary row. No end anchor: the next unit boundary row; none means
    end of file.
    """
    if parsed_end is not None:
        end_row = _locate_row(rows, parsed_end)
        if end_row is not None and end_row.parsed.unit_path == start_row.parsed.unit_path:
            located = locate_leittext(source_text, end_row.leittext)
            if located is not None:
                return located.start
            findings.append(_finding(end_row.anchor, "end-leittext-miss"))
            return len(source_text)
    boundary = _next_unit_boundary_row(rows, start_row)
    if boundary is None:
        return len(source_text)
    if boundary.source_file != start_row.source_file:
        # the next anchor lives in another realization file: the start
        # file's remainder is the span end (no cross-file locate miss)
        return len(source_text)
    located = locate_leittext(source_text, boundary.leittext)
    if located is None:
        findings.append(_finding(boundary.anchor, "boundary-leittext-miss"))
        return len(source_text)
    return located.start


def _next_unit_boundary_row(rows: list[AnchorRow], start_row: AnchorRow) -> AnchorRow | None:
    """First row after the start row whose unit path differs."""
    seen_start = False
    for row in rows:
        if row.anchor == start_row.anchor:
            seen_start = True
            continue
        if seen_start and row.parsed.unit_path != start_row.parsed.unit_path:
            return row
    return None


def verify_fragment(bookdir: Path | str, fragment: dict[str, Any] | Path | str) -> dict[str, Any]:
    """Verify a stored fragment (plan section 6) against its anchors.

    Resolves the interval via the anchor table, checks the fragment's
    expected_char_band, and confirms the fragment leittext still appears
    inside the materialized span.
    """
    frag: dict[str, Any]
    if isinstance(fragment, (str, Path)):
        frag = json.loads(Path(fragment).read_text(encoding="utf-8"))
    else:
        frag = fragment
    interval = frag.get("interval", {})
    start_anchor = interval.get("start_anchor")
    end_anchor = interval.get("end_anchor")
    if end_anchor is None:
        end_anchor = None
    book_path = Path(bookdir)
    result = resolve(book_path, start_anchor, end_anchor, emit_text=True)
    result["fragment_id"] = frag.get("fragment_id")

    if result["status"] != "resolved":
        return result

    findings = result["findings"]
    materialized = result.get("text", "")
    norm_materialized, _ = normalize_with_map(materialized)
    norm_frag_leit, _ = normalize_with_map(frag.get("leittext", ""))
    if norm_frag_leit.strip() and norm_frag_leit.strip() not in norm_materialized:
        findings.append(_finding(start_anchor, "fragment-leittext-miss"))
    band = frag.get("expected_char_band")
    if band is not None:
        band_min, band_max = int(band["min"]), int(band["max"])
        if not (band_min <= len(materialized) <= band_max):
            findings.append(
                _finding(
                    start_anchor,
                    "char-band-violation",
                    expected={"min": band_min, "max": band_max},
                    actual=len(materialized),
                )
            )
    result["findings"] = findings
    result["status"] = "drift" if findings else "resolved"
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anchor_resolver",
        description="Resolve SALA anchors to text (TASK-LIB-01).",
    )
    sub = parser.add_subparsers(dest="command")

    p_resolve = sub.add_parser("resolve", help="Resolve one anchor interval.")
    p_resolve.add_argument("--book", required=True)
    p_resolve.add_argument("--anchor")
    p_resolve.add_argument("--end-anchor")
    p_resolve.add_argument("--source-materials-root", default=None)
    p_resolve.add_argument("--emit-text", action="store_true")
    p_resolve.add_argument("--write-out", default=None)

    p_verify = sub.add_parser("verify", help="Verify a stored fragment.")
    p_verify.add_argument("--fragment", required=True)
    p_verify.add_argument("--source-materials-root", default=None)
    p_verify.add_argument("--emit-text", action="store_true")
    p_verify.add_argument("--write-out", default=None)
    return parser


def _books_root(args: argparse.Namespace) -> Path:
    import os as _os
    root = Path(args.source_materials_root or _os.environ.get("ANCHOR_SOURCE_MATERIALS_ROOT", "source-materials"))
    return root / "books"


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command not in ("resolve", "verify"):
        print(
            json.dumps(
                {
                    "status": "error",
                    "findings": [{"kind": "usage", "detail": "unknown command"}],
                }
            )
        )
        return EXIT_ERROR

    books_root = (
        Path(args.source_materials_root or __import__("os").environ.get("ANCHOR_SOURCE_MATERIALS_ROOT", "source-materials")) / "books"
    )

    if args.command == "resolve":
        if not args.anchor:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "findings": [
                            {
                                "kind": "usage",
                                "detail": "resolve requires --anchor",
                            }
                        ],
                    }
                )
            )
            return EXIT_ERROR
        bookdir = books_root / args.book
        result = resolve(bookdir, args.anchor, args.end_anchor, args.emit_text)
    else:
        frag_path = Path(args.fragment)
        book_id = None
        try:
            payload = json.loads(frag_path.read_text(encoding="utf-8"))
            book_id = parse_anchor(payload["interval"]["start_anchor"]).book
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            print(
                json.dumps(
                    {
                        "status": "error",
                        "findings": [
                            {
                                "kind": "usage",
                                "detail": "unreadable fragment",
                            }
                        ],
                    }
                )
            )
            return EXIT_ERROR
        bookdir = books_root / book_id
        result = verify_fragment(bookdir, payload)
        if args.emit_text and "text" not in result:
            result.setdefault("text", result.get("text"))

    if args.write_out and "text" in result:
        Path(args.write_out).write_text(result["text"], encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] == "drift":
        return EXIT_DRIFT
    if result["status"] == "error":
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
