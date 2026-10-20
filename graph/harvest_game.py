#!/usr/bin/env python3
"""Lean-4-Game-Engine prose extractor (TASK-LIB-02 pass 1).

The game-engine books (e.g. Marasingha's Modern Mathematics in Lean 4)
carry their prose in World/Level/Title/Introduction "..." command
blocks inside lean files. This adapter extracts the per-level prose,
ordered by the worlds' and the levels' own numbering (the author's
progression, plan section 3.2).

Extraction contract:
  - the World, Level, and Title commands name the unit
  - the Introduction "..." string is the prose (kept verbatim)
  - the file's other content (imports, examples, theorems) is not prose

Usage:
  harvest_game.py <game-src-dir> <out-dir>

Emits one markdown file per level (World-L{level}.md) plus toc.json.
Strict 7-bit ASCII only (INV-001) for the tool itself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

WORLD = re.compile(r'^\s*World\s+"([^"]+)"')
LEVEL = re.compile(r"^\s*Level\s+(\d+)")
TITLE = re.compile(r'^\s*Title\s+"([^"]+)"')
INTRO = re.compile(r'^\s*Introduction\s+"$', re.MULTILINE)


def extract_level(path: Path) -> dict[str, Any]:
    """One level's unit metadata and prose."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    world = None
    level = None
    title = None
    for line in text.splitlines():
        if world is None:
            m = WORLD.match(line)
            if m:
                world = m.group(1)
        if level is None:
            m = LEVEL.match(line)
            if m:
                level = int(m.group(1))
        if title is None:
            m = TITLE.match(line)
            if m:
                title = m.group(1)
    if world is None or level is None:
        raise ValueError(f"no World/Level commands in {path.name}")
    # the Introduction "..." block: everything between the opening quote
    # and the closing quote on its own line
    intro = ""
    # the closing quote sits alone on a line before further content (the
    # level's lean code); the end-of-string anchor cannot be used
    match = re.search(r'Introduction\s*"\n(.*?)\n"', text, re.DOTALL)
    if match is not None:
        intro = match.group(1).strip()
    return {"world": world, "level": level, "title": title or "", "introduction": intro}


def harvest_tree(srcdir: Path, outdir: Path) -> list[dict[str, Any]]:
    """Extract every level, ordered by (world, level) as encountered."""
    srcdir = Path(srcdir)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for path in sorted(srcdir.rglob("*.lean")):
        try:
            payload = extract_level(path)
        except ValueError:
            continue
        slug = f"{payload['world']}-L{payload['level']}"
        out_path = outdir / f"{slug}.md"
        prose = (
            f"# {payload['world']} - Level {payload['level']}: "
            f"{payload['title']}\n\n{payload['introduction']}\n"
        )
        out_path.write_text(prose, encoding="utf-8")
        manifest.append(
            {
                "world": payload["world"],
                "level": payload["level"],
                "title": payload["title"],
                "file": out_path.name,
                "order": len(manifest) + 1,
                "sections": 1,
            }
        )
    manifest.sort(key=lambda m: (m["world"], m["level"]))
    (outdir / "toc.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harvest_game",
        description="Lean-4-Game prose to per-level markdown (TASK-LIB-02).",
    )
    parser.add_argument("srcdir")
    parser.add_argument("outdir")
    args = parser.parse_args(argv)
    manifest = harvest_tree(Path(args.srcdir), Path(args.outdir))
    print(json.dumps({"levels": len(manifest)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
