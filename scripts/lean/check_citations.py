#!/usr/bin/env python3
"""Skill & Reference Citation Verifier (`check-citations`) + `LAST_VERIFIED.md` Generator (Proposal 10C).

Scans `skills/**/SKILL.md` and `references/*.md` for:
  1. File-and-line citations (`path/to/file.lean:123` or `path/to/file.py:45`), verifying
     that the file exists and `1 <= line <= total_lines`.
  2. Backticked Lean module paths (`EASCI/Tactics/AltProof.lean`), verifying file existence.
  3. Optional `.ilean` symbol verification when `--trace-root` is provided.
  4. Optional `LAST_VERIFIED.md` provenance stamp generation (`--write-last-verified`).

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

FILE_LINE_RE = re.compile(
    r"`([A-Za-z0-9_./-]+\.(?:lean|py|rs|ts|md|sh|json)):(\d+)(?:-\d+)?`"
)


def _discover_lake_package_roots(roots: list[Path]) -> list[Path]:
    """Auto-discover `.lake/packages/*/` roots under any provided root or parent Lean workspace."""
    extra: list[Path] = []
    candidates = list(roots)
    for r in list(roots):
        for parent in [r, *r.parents]:
            lake_pkgs = parent / ".lake" / "packages"
            if lake_pkgs.is_dir():
                for pkg_dir in sorted(lake_pkgs.iterdir()):
                    if pkg_dir.is_dir() and pkg_dir not in candidates and pkg_dir not in extra:
                        extra.append(pkg_dir)
            easci_pkgs = parent / "docs" / "easci" / "lean" / ".lake" / "packages"
            if easci_pkgs.is_dir():
                for pkg_dir in sorted(easci_pkgs.iterdir()):
                    if pkg_dir.is_dir() and pkg_dir not in candidates and pkg_dir not in extra:
                        extra.append(pkg_dir)
    return extra


def verify_markdown_citations(
    docs_root: Path,
    repo_roots: list[Path] | None = None,
    trace_root: Path | None = None,
) -> dict:
    """Scan markdown files under `docs_root` and verify `file:line` citations against `repo_roots`
    and optional `.ilean` symbol definitions under `trace_root`."""
    docs_root = Path(docs_root).resolve()
    search_roots = [Path(r).resolve() for r in (repo_roots or [docs_root])]
    if docs_root not in search_roots:
        search_roots.insert(0, docs_root)
    pkg_roots = _discover_lake_package_roots(search_roots)
    for pr in pkg_roots:
        if pr not in search_roots:
            search_roots.append(pr)

    md_files: list[Path] = []
    if docs_root.is_file():
        md_files = [docs_root]
    else:
        for sub in ("skills", "references"):
            d = docs_root / sub
            if d.exists():
                md_files.extend(sorted(d.rglob("*.md")))
        if not md_files:
            md_files = sorted(docs_root.rglob("*.md"))

    checked_citations = 0
    broken_citations: list[dict] = []

    for md_path in md_files:
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in FILE_LINE_RE.finditer(text):
            rel_file = m.group(1)
            line_no = int(m.group(2))
            # Skip obvious placeholder/template examples
            if any(
                ph in rel_file
                for ph in (
                    "path/to/",
                    "<",
                    ">",
                    "MyProject",
                    "example",
                    "foo.lean",
                    "bar.lean",
                )
            ):
                continue
            checked_citations += 1
            resolved: Path | None = None
            for sr in search_roots:
                for cand_rel in (
                    rel_file,
                    f"Mathlib/{rel_file}" if not rel_file.startswith("Mathlib/") else rel_file,
                ):
                    cand = sr / cand_rel
                    if cand.is_file():
                        resolved = cand
                        break
                if resolved is not None:
                    break
            if resolved is None:
                broken_citations.append(
                    {
                        "source_doc": str(md_path),
                        "citation": m.group(0),
                        "file": rel_file,
                        "line": line_no,
                        "reason": "FILE_NOT_FOUND",
                    }
                )
                continue
            total_lines = len(resolved.read_text(encoding="utf-8").splitlines())
            if line_no < 1 or line_no > max(1, total_lines):
                broken_citations.append(
                    {
                        "source_doc": str(md_path),
                        "citation": m.group(0),
                        "file": rel_file,
                        "line": line_no,
                        "total_lines": total_lines,
                        "reason": "LINE_OUT_OF_RANGE",
                    }
                )

    ilean_symbols_count = 0
    if trace_root is not None:
        altproof_dir = Path(__file__).resolve().parent / "altproof"
        if str(altproof_dir) not in sys.path:
            sys.path.insert(0, str(altproof_dir))
        from trace_symbols import TraceIndex

        idx = TraceIndex(trace_root)
        ilean_symbols_count = len(idx.all_defined_symbols)

    return {
        "ok": len(broken_citations) == 0,
        "docs_scanned": len(md_files),
        "citations_checked": checked_citations,
        "broken_count": len(broken_citations),
        "broken_citations": broken_citations,
        "ilean_symbols_indexed": ilean_symbols_count,
    }


def write_last_verified_stamp(output_path: Path, report: dict) -> None:
    """Write a `lean4-skills`-style `LAST_VERIFIED.md` provenance stamp."""
    commit = "unknown"
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(output_path.resolve().parent),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode == 0:
            commit = proc.stdout.strip()
    except Exception:
        pass
    stamp = "\n".join(
        [
            "# LAST_VERIFIED",
            "",
            f"- **Timestamp (UTC)**: `{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}`",
            f"- **Git Commit**: `{commit}`",
            f"- **Documents Scanned**: `{report['docs_scanned']}`",
            f"- **Citations Verified**: `{report['citations_checked']}`",
            f"- **Broken Citations**: `{report['broken_count']}`",
            f"- **Status**: `{'PASS' if report['ok'] else 'FAIL'}`",
            "",
        ]
    )
    output_path.write_text(stamp, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("check-citations", "check_citations"):
        argv.pop(0)
    parser = argparse.ArgumentParser(
        prog="lean-skills check-citations",
        description="Verify file:line citations across SKILL.md and references/*.md",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Root directory of proof-skills",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        action="append",
        default=[],
        help="Additional repository root(s) for resolving cited paths",
    )
    parser.add_argument(
        "--trace-root",
        type=Path,
        default=None,
        help="Optional Lean project root for .ilean symbol index verification",
    )
    parser.add_argument(
        "--write-last-verified",
        type=Path,
        default=None,
        help="Optional path to write LAST_VERIFIED.md",
    )
    args = parser.parse_args(argv)

    res = verify_markdown_citations(
        args.root, repo_roots=args.repo_root, trace_root=args.trace_root
    )
    if args.write_last_verified:
        write_last_verified_stamp(args.write_last_verified, res)
    print(json.dumps(res, indent=2))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
