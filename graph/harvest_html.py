#!/usr/bin/env python3
"""jupyter-book HTML text extractor (TASK-LIB-02 pass 1).

Reduces a book's built HTML (jupyter-book flavor, e.g. the Mechanics of
Proof's html/ tree) to a linear text realization the PDF-flavor anchor
builder can address, per source-materials-librarian-pipeline-plan.md
sections 5.1/R4a and 3.2.

Extraction contract:
  - h1/h2/h3 headings become their own lines (kept verbatim, tags
    stripped)
  - paragraphs and pre/code blocks are kept as text lines
  - script, style, and footer/nav/boilerplate content is dropped
  - chapter files concatenate with form-feed separators, preserving
    page-ish boundaries for the band arithmetic

Strict 7-bit ASCII only (INV-001) for the tool itself; the prose keeps
its native Unicode.
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

_DROP_TAGS = {"script", "style", "footer", "nav", "head", "noscript"}
_KEEP_TAGS = {"h1", "h2", "h3", "p", "pre", "code", "li", "blockquote"}


class _PageText(HTMLParser):
    """A streaming h1/h2/h3/p/pre text collector."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self._keep_depth = 0
        self._drop_depth = 0
        self._current_tag: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _DROP_TAGS:
            self._drop_depth += 1
        elif tag in _KEEP_TAGS:
            if self._keep_depth == 0:
                self._current_tag = tag
                self._buf = []
            self._keep_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _DROP_TAGS and self._drop_depth:
            self._drop_depth -= 1
        elif tag in _KEEP_TAGS and self._keep_depth:
            self._keep_depth -= 1
            if self._keep_depth == 0 and self._current_tag is not None:
                text = " ".join("".join(self._buf).split())
                if text:
                    if self._current_tag in ("h1", "h2", "h3"):
                        self.lines.append(text)
                    else:
                        self.lines.append(text)
                self._current_tag = None
                self._buf = []

    def handle_data(self, data: str) -> None:
        if self._drop_depth == 0 and self._keep_depth:
            self._buf.append(html_mod.unescape(data))


def extract_page_text(path: Path) -> str:
    """One built chapter's text: headings and content lines."""
    parser = _PageText()
    parser.feed(Path(path).read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parser.lines) + "\n"


def harvest_book(
    htmldir: Path, outdir: Path, output_name: str = "realization.txt"
) -> list[dict[str, Any]]:
    """Extract every built chapter in filename order into one realization."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    chunks: list[str] = []
    for path in sorted(Path(htmldir).glob("*.html")):
        text = extract_page_text(path)
        chunks.append(text)
        files.append({"file": path.name, "chars": len(text)})
    (outdir / output_name).write_text("\f\n".join(chunks), encoding="utf-8")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harvest_html",
        description="jupyter-book HTML to a linear text realization (TASK-LIB-02).",
    )
    parser.add_argument("htmldir")
    parser.add_argument("outdir")
    parser.add_argument("--output-name", default="realization.txt")
    args = parser.parse_args(argv)
    files = harvest_book(Path(args.htmldir), Path(args.outdir), args.output_name)
    print(json.dumps({"chapters": len(files)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
