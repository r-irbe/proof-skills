#!/usr/bin/env python3
"""Lean-docstring prose extractor (TASK-LIB-02 pass 1).

The metaprogramming book's chapters are lean files whose leading
`/- ... -/` block carries the chapter's markdown prose (the MIL-style
layout). This adapter extracts those blocks as per-chapter markdown and
orders units by the chapter filenames' numeric prefixes (01_intro before
02_overview) -- the author's own numbering, which serves as the SALA
unit order (plan section 3.2).

Extraction contract:
  - the prose is the FIRST `/- ... -/` block in the file
  - the markers themselves are dropped; the inner markdown is kept
    verbatim (dedented flush-left already)
  - anything after the block (imports, examples, code) is not prose

Usage:
  harvest_lean_prose.py <lean-src-dir> <out-dir>

Emits one markdown file per chapter plus toc.json (order fields for
build_anchor_table.py). Strict 7-bit ASCII only (INV-001) for the tool
itself; the prose keeps its native Unicode.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

OPEN, CLOSE = "/-", "-/"


def extract_prose(path: Path) -> str:
    """The markdown prose of a chapter file's first docstring block."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    start = text.find(OPEN)
    if start < 0:
        raise ValueError(f"no {OPEN} prose block in {path.name}")
    end = text.find(CLOSE, start + len(OPEN))
    if end < 0:
        raise ValueError(f"unterminated {OPEN} block in {path.name}")
    inner = text[start + len(OPEN) : end]
    # drop one leading newline; keep the markdown body flush-left
    if inner.startswith("\n"):
        inner = inner[1:]
    return inner.strip() + "\n"


def _count_sections(markdown: str) -> int:
    import re as _re

    return sum(1 for line in markdown.splitlines() if _re.match(r"^#{1,2}\s+\S", line))


def harvest_tree(srcdir: Path, outdir: Path, summary: Path | None = None) -> list[dict[str, Any]]:
    """Extract every chapter docstring.

    With a mdBook SUMMARY.md, the link order (stems matching the lean
    filenames) is the author's unit order and drives the selection --
    cover pages and solution stubs (absent from the summary) are
    excluded. Without a summary, filename-prefix order applies.
    """
    srcdir = Path(srcdir)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    chapters = sorted(
        p for p in srcdir.rglob("*.lean") if OPEN in p.read_text(encoding="utf-8", errors="replace")
    )
    if summary is not None and Path(summary).exists():
        # the SUMMARY links name .md realizations that do not exist in a
        # lean-prose book; their STEMS map to the chapter files. Parse the
        # raw links (existence-filtered order would drop every chapter).
        import re as _re

        link = _re.compile(r"^\s*-\s*\[([^\]]+)\]\(([^)]+)\)\s*$")
        rel_paths: list[str] = []
        for line in Path(summary).read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("<!--"):
                continue
            m = link.match(stripped)
            if m is None:
                continue
            rel = m.group(2).lstrip("./").replace(".md", ".lean")
            if rel not in rel_paths:
                rel_paths.append(rel)
        # the summary's relative paths map 1:1 into the lean tree; this
        # excludes cover pages and the solutions tree (same stems, wrong
        # directory)
        chapters = [
            srcdir / rel
            for rel in rel_paths
            if (srcdir / rel).exists()
            and OPEN in (srcdir / rel).read_text(encoding="utf-8", errors="replace")
        ]
        chapters.sort(key=lambda p: rel_paths.index(str(p.relative_to(srcdir))))
    for position, path in enumerate(chapters, start=1):
        prose = extract_prose(path)
        stem = path.stem
        out_path = outdir / f"{stem}.md"
        out_path.write_text(prose, encoding="utf-8")
        manifest.append(
            {
                "title": (prose.splitlines() or [""])[0].lstrip("# ").strip(),
                "source": str(path.relative_to(srcdir)),
                "file": out_path.name,
                "order": position,
                "sections": _count_sections(prose),
            }
        )
    (outdir / "toc.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harvest_lean_prose",
        description="Lean docstring prose to per-chapter markdown (TASK-LIB-02).",
    )
    parser.add_argument("srcdir")
    parser.add_argument("outdir")
    parser.add_argument("--summary", default=None, help="mdBook SUMMARY.md driving unit order")
    args = parser.parse_args(argv)
    manifest = harvest_tree(
        Path(args.srcdir),
        Path(args.outdir),
        Path(args.summary) if args.summary else None,
    )
    print(json.dumps({"chapters": len(manifest)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
