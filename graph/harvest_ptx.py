#!/usr/bin/env python3
"""PreTeXt (.ptx) text extractor (TASK-LIB-02 pass 1).

Reduces a book's PreTeXt XML source (e.g. the Levin discrete-book's
source/*.ptx tree) to a linear text realization the PDF-flavor anchor
builder can address, per source-materials-librarian-pipeline-plan.md
sections 5.1/R4a and 3.2.

Extraction contract:
  - <title> elements (chapter and section level) become their own lines
  - <p> prose blocks are kept as text lines (tags stripped)
  - XML processing instructions and non-prose elements are dropped
  - chapter files concatenate with form-feed separators

Strict 7-bit ASCII only (INV-001) for the tool itself; the prose keeps
its native Unicode.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def extract_ptx(path: Path) -> str:
    """One .ptx file's text: the titles and the prose lines."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    lines: list[str] = []
    # the titles: the <title>...</title> blocks (chapter and subsection)
    for m in re.finditer(r"<title>(.*?)</title>", text, re.DOTALL):
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if title:
            lines.append(title)
    # the prose: the <p>...</p> blocks, tags stripped
    for m in re.finditer(r"<p>(.*?)</p>", text, re.DOTALL):
        para = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        para = re.sub(r"\s+", " ", para)
        if para:
            lines.append(para)
    return "\n".join(lines) + "\n"


def harvest_book(
    srcdir: Path, outdir: Path, output_name: str = "discrete_mathematics.txt"
) -> list[dict[str, Any]]:
    """Extract the .ptx files in filename order into one realization."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    chunks: list[str] = []
    for path in sorted(Path(srcdir).glob("*.ptx")):
        text = extract_ptx(path)
        chunks.append(text)
        files.append({"file": path.name, "chars": len(text)})
    (outdir / output_name).write_text("\f\n".join(chunks), encoding="utf-8")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harvest_ptx",
        description="PreTeXt .ptx to a linear text realization (TASK-LIB-02).",
    )
    parser.add_argument("srcdir")
    parser.add_argument("outdir")
    parser.add_argument("--output-name", default="discrete_mathematics.txt")
    args = parser.parse_args(argv)
    files = harvest_book(Path(args.srcdir), Path(args.outdir), args.output_name)
    print(json.dumps({"chapters": len(files)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
