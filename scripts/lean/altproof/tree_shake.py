#!/usr/bin/env python3
"""Declaration-level & module-level Lean 4 tree-shaker wrapper (`altproof tree-shake`).

Bridges to `lean4-lsp-mcp` (`bin/lean-tree-shake.js`) for `.ilean` reference-closure
slicing, transitive import promotion, optional double-blind anonymization, and
metadata-scrubbed `.tar.gz` artifact generation.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def resolve_lean_tree_shake_bin(skills_root: Path | None = None) -> tuple[list[str], Path]:
    """Locate `bin/lean-tree-shake.js` or `lean-tree-shake` executable."""
    node_bin = shutil.which("node") or "node"
    env_override = os.environ.get("LEAN_TREE_SHAKE_BIN", "").strip()
    if env_override:
        cand = Path(env_override).expanduser().resolve()
        if cand.is_file():
            if cand.suffix in (".js", ".mjs", ".cjs"):
                return ([node_bin, str(cand)], cand)
            return ([str(cand)], cand)

    here = Path(__file__).resolve()
    root = skills_root or here.parents[3]
    search_candidates: list[Path] = [
        root / "tools" / "lean-lsp-mcp" / "bin" / "lean-tree-shake.js",
        root / "packages" / "lean-analysis" / "bin" / "lean-tree-shake.js",
    ]
    for anc in root.parents:
        search_candidates.append(anc / "packages" / "lean-analysis" / "bin" / "lean-tree-shake.js")
        search_candidates.append(anc / "tools" / "lean-lsp-mcp" / "bin" / "lean-tree-shake.js")

    for cand in search_candidates:
        if cand.is_file():
            return ([node_bin, str(cand)], cand)

    which_bin = shutil.which("lean-tree-shake")
    if which_bin:
        resolved = Path(which_bin).resolve()
        return ([which_bin], resolved)

    raise FileNotFoundError(
        "Could not locate bin/lean-tree-shake.js (set LEAN_TREE_SHAKE_BIN or install lean4-lsp-mcp)."
    )


def run_tree_shake(
    entry_modules: list[str],
    *,
    project_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    archive_path: str | Path | None = None,
    granularity: str = "declaration",
    anonymize: bool = False,
    package_name: str | None = None,
    forbidden_patterns: list[str] | None = None,
    verify_build: bool = False,
    timeout_ms: int = 600000,
) -> dict[str, Any]:
    """Execute `lean-tree-shake` and return the parsed JSON report."""
    if not entry_modules:
        raise ValueError("entry_modules must be non-empty")

    cmd_prefix, _ = resolve_lean_tree_shake_bin()
    cmd: list[str] = list(cmd_prefix) + list(entry_modules) + [
        "--json",
        "--granularity",
        granularity,
        "--timeout-ms",
        str(timeout_ms),
    ]
    if project_root is not None:
        cmd.extend(["--project-root", str(Path(project_root).expanduser().resolve())])
    if output_dir is not None:
        cmd.extend(["--output-dir", str(Path(output_dir).expanduser().resolve())])
    if archive_path is not None:
        cmd.extend(["--archive", str(Path(archive_path).expanduser().resolve())])
    if anonymize:
        cmd.append("--anonymize")
    if package_name:
        cmd.extend(["--package-name", package_name])
    for pat in forbidden_patterns or []:
        if pat:
            cmd.extend(["--forbid", pat])
    if verify_build:
        cmd.append("--verify-build")

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    stdout = proc.stdout.strip()
    if not stdout:
        stderr_msg = proc.stderr.strip() or f"exit code {proc.returncode}"
        raise RuntimeError(f"lean-tree-shake produced empty output ({stderr_msg})")

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Failed to parse lean-tree-shake JSON output (exit={proc.returncode}): {exc}\n{stdout[:400]}"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError("lean-tree-shake JSON payload must be an object")
    return payload


def format_tree_shake_markdown(report: dict[str, Any]) -> str:
    """Render concise Markdown summary of a `TreeShakeReport` dict."""
    lines = [
        f"## Lean 4 Tree-Shake Report (`{', '.join(report.get('entryModules') or [])}`)",
        f"- **Granularity:** `{report.get('granularity', 'declaration')}` "
        f"(`anonymized={report.get('anonymized', False)}`, `dryRun={report.get('dryRun', True)}`)",
        f"- **Modules:** `{report.get('keptModulesCount', 0)}/{report.get('totalCorpusModules', 0)}` kept "
        f"(file-import closure: `{report.get('fileImportClosureModules', 0)}`)",
        f"- **Declarations:** `{report.get('reachableDeclarationsCount', 0)}` reachable, "
        f"`{report.get('prunedDeclarationsCount', 0)}` pruned",
        f"- **LOC Reduction:** `{report.get('totalLinesBefore', 0)} -> {report.get('totalLinesAfter', 0)}` lines "
        f"(`-{report.get('lineReductionPct', 0)}%`), `-{report.get('byteReductionPct', 0)}%` bytes",
        f"- **Identity Leak Hits:** `{len(report.get('anonymityLeakHits') or [])}`",
    ]
    if report.get("archivePath"):
        lines.append(f"- **Archive:** `{report['archivePath']}`")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="altproof tree-shake",
        description="Declaration/module-level Lean 4 tree-shaker via .ilean reference graph",
    )
    parser.add_argument("entries", nargs="+", help="Entry module names or .lean paths")
    parser.add_argument("--project-root", type=Path, default=None, help="Lake project root (default: cwd)")
    parser.add_argument("--output-dir", type=Path, default=None, help="Emit standalone Lake slice directory")
    parser.add_argument("--archive", type=Path, default=None, help="Emit metadata-scrubbed .tar.gz archive")
    parser.add_argument(
        "--granularity",
        choices=("declaration", "module"),
        default="declaration",
        help="Pruning granularity (default: declaration)",
    )
    parser.add_argument("--anonymize", action="store_true", help="Scrub author headers & URLs for double-blind review")
    parser.add_argument("--package-name", default=None, help="Override package name in emitted Lake config")
    parser.add_argument(
        "--forbid",
        action="append",
        dest="forbidden_patterns",
        default=[],
        help="Case-insensitive leak pattern to forbid (repeatable)",
    )
    parser.add_argument("--verify-build", action="store_true", help="Run standalone `lake build` on emitted slice")
    parser.add_argument("--timeout-ms", type=int, default=600000, help="Build verification timeout in ms")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown summary instead of JSON")
    args = parser.parse_args(argv)

    try:
        report = run_tree_shake(
            args.entries,
            project_root=args.project_root,
            output_dir=args.output_dir,
            archive_path=args.archive,
            granularity=args.granularity,
            anonymize=args.anonymize,
            package_name=args.package_name,
            forbidden_patterns=args.forbidden_patterns,
            verify_build=args.verify_build,
            timeout_ms=args.timeout_ms,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.markdown:
        print(format_tree_shake_markdown(report))
    else:
        print(json.dumps(report, indent=2))

    if args.verify_build and not report.get("buildVerified", False):
        return 1
    if report.get("anonymityLeakHits"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
