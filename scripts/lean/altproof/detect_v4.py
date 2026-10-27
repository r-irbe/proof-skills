#!/usr/bin/env python3
"""detect_v4: trace-backed named-term demotion + S2 theorem-span attribution (Proposal 9A, S2 & S3).

Combines `extraction_detector.py`'s textual `module_symbols(source)` with `TraceIndex`
(`.ilean` and `.ast.json` cross-module symbol tables) via UNION demotion:

    demote_symbols = module_symbols(source) | index.symbols_for(source_rel)

Also exposes `detect_v4_corpus_file(lean_file, index, source_rel)` which uses S2
`attribute_theorem_spans` to attribute each candidate to its enclosing theorem.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from extraction_detector import Candidate, detect_v3, module_symbols
from trace_symbols import TraceIndex, attribute_theorem_spans


def detect_v4(
    proof_text: str,
    theorem: str,
    index: TraceIndex | None,
    source_rel: str,
    source: str | None = None,
) -> list[Candidate]:
    """Run `detect_v3` with union demotion (`module_symbols(source) | index.symbols_for(source_rel)`)."""
    syms = module_symbols(source if source is not None else proof_text)
    if index is not None:
        syms = syms | index.symbols_for(source_rel)
    return detect_v3(proof_text, theorem=theorem, file_symbols=syms)


def detect_v4_file(
    lean_path: Path,
    index: TraceIndex | None = None,
    source_rel: str = "",
) -> list[Candidate]:
    """Run S2 theorem-span attribution + S3 `detect_v4` across every theorem in `lean_path`."""
    text = lean_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    rel = source_rel or lean_path.name
    spans = attribute_theorem_spans(text, index=index, source_rel=rel)
    all_candidates: list[Candidate] = []
    for sp in spans:
        block_text = "\n".join(lines[sp.start_line - 1 : sp.end_line])
        cands = detect_v4(
            block_text,
            theorem=sp.name,
            index=index,
            source_rel=rel,
            source=text,
        )
        all_candidates.extend(cands)
    return all_candidates


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("detect-v4", "detect_v4"):
        argv.pop(0)
    parser = argparse.ArgumentParser(
        prog="lean-skills detect-v4",
        description="Run .ilean / TraceIndex S2+S3 extraction detector on a Lean file",
    )
    parser.add_argument("file", type=Path, help="Input .lean file")
    parser.add_argument(
        "--trace-root",
        type=Path,
        default=None,
        help="Project or .lake/build/lib root containing .ilean or .ast.json files",
    )
    parser.add_argument(
        "--source-rel",
        default="",
        help="Relative module path (e.g. EASCI/Core.lean)",
    )
    args = parser.parse_args(argv)

    idx = TraceIndex(args.trace_root) if args.trace_root else None
    cands = detect_v4_file(args.file, index=idx, source_rel=args.source_rel)
    out = [
        {
            "theorem": c.theorem,
            "route": c.route,
            "kind": c.kind,
            "evidence": c.evidence,
            "occurrences": c.occurrences,
            "estimated_lines_saved": c.estimated_lines_saved,
        }
        for c in cands
    ]
    print(json.dumps({"count": len(out), "candidates": out}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
