#!/usr/bin/env python3
"""mdBook harvest adapter (TASK-LIB-02 pass 1).

mdBook's SUMMARY.md is a book's own analytical table of contents: the
link order defines the SALA anchor unit order (plan section 3.2). This
adapter parses that order, copies the chapter markdown into the book's
realization directory, and emits a toc.json whose entries carry an
`order` field -- which build_anchor_table.py honors directly (no root
module needed for mdBook sources).

Parsing rules:
  - `- [Title](path)` links are chapters, in file order
  - `<!-- - [Draft]() -->` commented entries are skipped
  - mdBook part headings (`# Main`, `# Extra`) are not units
  - paths resolve relative to the SUMMARY.md directory

Strict 7-bit ASCII only (INV-001) for the tool itself; the prose keeps
its native Unicode.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

SUMMARY_LINK = re.compile(r"^-\s*\[([^\]]+)\]\(([^)]+)\)\s*$")


def summary_order(summary_path: Path) -> list[dict[str, str]]:
    """The chapters in the author's link order.

    Commented-out entries are skipped; part headings are not units.
    Paths are resolved against the SUMMARY's directory but returned as
    the bare filenames' relative paths for the toc manifest.
    """
    base = summary_path.parent
    order: list[dict[str, str]] = []
    for line in summary_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("<!--"):
            continue
        match = SUMMARY_LINK.match(stripped)
        if match is None:
            continue
        title, link = match.group(1), match.group(2)
        relative = link.lstrip("./")
        if not (base / relative).exists():
            continue  # a dead link is not a chapter
        order.append({"title": title, "file": Path(relative).name})
    return order


def harvest_tree(srcdir: Path, outdir: Path) -> list[dict[str, Any]]:
    """Copy the chapters in SUMMARY order and emit toc.json."""
    srcdir = Path(srcdir)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    order = summary_order(srcdir / "SUMMARY.md")
    manifest: list[dict[str, Any]] = []
    for position, entry in enumerate(order, start=1):
        candidates = list(srcdir.rglob(entry["file"]))
        if not candidates:
            continue
        source = candidates[0]
        destination = outdir / entry["file"]
        shutil.copyfile(source, destination)
        manifest.append(
            {
                "title": entry["title"],
                "file": entry["file"],
                "order": position,
                "sections": _count_sections(source),
            }
        )
    (outdir / "toc.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _count_sections(path: Path) -> int:
    """'## ' headings plus the chapter H1 (the anchor builder's regions)."""
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^#{1,2}\s+\S", line):
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harvest_mdbook",
        description="mdBook SUMMARY order to toc.json + copied chapters (TASK-LIB-02).",
    )
    parser.add_argument("srcdir", help="mdBook md/ directory (with SUMMARY.md)")
    parser.add_argument("outdir")
    args = parser.parse_args(argv)
    manifest = harvest_tree(Path(args.srcdir), Path(args.outdir))
    print(json.dumps({"chapters": len(manifest)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
