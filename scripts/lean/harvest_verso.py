#!/usr/bin/env python3
"""Verso-to-markdown harvest adapter (TASK-LIB-02 pass 1).

Converts Verso manual sources (lean files whose #doc blocks carry a
book's prose) into per-chapter markdown realizations the SALA resolver
can address, per source-materials-librarian-pipeline-plan.md sections
5.1/R4a (ingestion artifacts are built once per edition) and 3.2 (anchor
unit paths come from the book's own analytical TOC -- here, the #doc
chapter order and the in-file '# Section' headings).

Folding rules (behavior, not style):
  - the '#doc (Manual) "Title" =>' line names the chapter (markdown '#')
  - in-document '# Section' lines become markdown '## Section'
  - %%% metadata fences are dropped
  - the prelude (import/open lines before the #doc) is dropped
  - {lean}`x` folds to `x`; {tech}[x] and {tech (key := "k")}[x] fold to x

Usage:
  harvest_verso.py <verso-src-dir> <out-dir> [--book-id TPIL4]

Writes one markdown file per chapter plus a TOC manifest (toc.json:
chapter order, section order, titles) that build_anchor_table.py
consumes. Strict 7-bit ASCII only (INV-001) for the tool itself; the
harvested prose keeps its native Unicode.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict

DOC_TITLE = re.compile(r"#doc\s*\((?:Manual|Manual\.[A-Za-z]+)\)\s*\"([^\"]+)\"\s*=>")
SECTION_HEADING = re.compile(r"^#\s+(.+?)\s*$")
META_BLOCK = re.compile(r"^%%%\n.*?\n%%%\s*$", re.MULTILINE | re.DOTALL)
LEAN_SPAN = re.compile(r"\{lean\}`([^`]+)`")
TECH_SPAN = re.compile(r"\{tech(?:\s*\(.*?\))?\}\[([^\]]+)\]")
CODE_BLOCK = re.compile(r"```lean\n.*?\n```", re.DOTALL)


def doc_title(text: str) -> str:
    """The chapter title from the #doc line; ValueError if absent."""
    match = DOC_TITLE.search(text)
    if match is None:
        raise ValueError("no #doc title found")
    return match.group(1)


def _fold_markup(body: str) -> str:
    """Fold Verso inline markup to plain markdown."""
    body = LEAN_SPAN.sub(lambda m: f"`{m.group(1)}`", body)
    body = TECH_SPAN.sub(lambda m: m.group(1), body)
    return body


class Section(TypedDict):
    """One #doc section: heading, depth, and markdown body."""

    title: str
    level: int
    body: str


def extract_sections(text: str) -> list[Section]:
    """Split a #doc source into [(title, level, body)] markdown sections."""
    doc_at = DOC_TITLE.search(text)
    if doc_at is None:
        raise ValueError("no #doc title found")
    doc_body = text[doc_at.start() :]
    doc_body = doc_body[doc_body.index("\n") + 1 :]

    sections: list[Section] = [{"title": doc_at.group(1), "level": 1, "body": ""}]
    for line in doc_body.splitlines():
        heading = SECTION_HEADING.match(line)
        if heading is not None:
            sections.append({"title": heading.group(1), "level": 2, "body": ""})
            continue
        if sections[-1]["level"] == 1 and not sections[-1]["body"] and not line.strip():
            continue
        if line.strip() == "%%%" or (line.strip().startswith("%%") and line.strip().endswith("%%")):
            continue
        if re.match(r"^\s*%%%\s*$", line):
            continue
        sections[-1]["body"] += line + "\n"

    for section in sections:
        body = str(section["body"])
        # drop %%% fenced metadata blocks
        body = re.sub(r"%%%\n[^%]*?%%%\n?", "", body)
        body = _fold_markup(body)
        # drop lean import/open prelude that leaked inside the doc body
        body = "\n".join(
            ln
            for ln in body.splitlines()
            if not re.match(r"^\s*(import |open |%%%\s*$|tag :=)", ln)
        )
        section["body"] = body.strip()
    return sections


def harvest_file(path: Path) -> dict:
    """Harvest one Verso .lean chapter source to a markdown payload."""
    text = path.read_text(encoding="utf-8")
    title = doc_title(text)
    sections = extract_sections(text)
    lines: list[str] = [f"# {title}", ""]
    for section in sections:
        level = int(section["level"])
        if section["body"]:
            lines.append(str(section["body"]))
            lines.append("")
        if level >= 2:
            # the level-1 section IS the chapter: its heading is already
            # the file's H1; re-rendering it would duplicate the title.
            prefix = "#" * level
            lines.append(f"{prefix} {section['title']}")
            lines.append("")
    return {
        "title": title,
        "markdown": "\n".join(lines),
        "sections": len(sections),
    }


def harvest_tree(srcdir: Path, outdir: Path, root_module: Path | None = None) -> list[dict]:
    """Harvest #doc-carrying .lean files under srcdir into outdir.

    With a root module, the chapter set is the module's own import list
    (the author's TOC) -- support files that also carry #doc markers are
    excluded, and toc.json entries carry an `order` field.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    import_order: dict[str, int] = {}
    if root_module is not None:
        for position, line in enumerate(
            Path(root_module).read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = re.match(r"^\s*(?:public\s+)?import\s+\w+\.(\w+)\s*$", line)
            if match is not None:
                import_order[match.group(1)] = position
    for path in sorted(Path(srcdir).rglob("*.lean")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "import VersoManual" not in text or "#doc (Manual)" not in text:
            continue
        if import_order and path.stem not in import_order:
            continue
        payload = harvest_file(path)
        slug = re.sub(r"[^A-Za-z0-9]+", "-", payload["title"]).strip("-")
        out_path = outdir / f"{slug}.md"
        out_path.write_text(payload["markdown"], encoding="utf-8")
        manifest.append(
            {
                "title": payload["title"],
                "source": path.name,
                "path": out_path,
                "sections": payload["sections"],
                "order": import_order.get(path.stem, 0),
            }
        )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harvest_verso",
        description="Verso manual sources to per-chapter markdown (TASK-LIB-02).",
    )
    parser.add_argument("srcdir")
    parser.add_argument("outdir")
    parser.add_argument("--root", default=None, help="the book's root module (order source)")
    args = parser.parse_args(argv)
    manifest = harvest_tree(
        Path(args.srcdir),
        Path(args.outdir),
        Path(args.root) if args.root else None,
    )
    (Path(args.outdir) / "toc.json").write_text(
        json.dumps(
            [
                {
                    "title": m["title"],
                    "source": m["source"],
                    "file": Path(m["path"]).name,
                    "sections": m["sections"],
                }
                for m in manifest
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"chapters": len(manifest)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
