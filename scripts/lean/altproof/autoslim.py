#!/usr/bin/env python3
"""Kernel-verified proof auto-slimmer wrapper for AltProof (`altproof autoslim`).

Bridges `lean-analyzer` exact `by ...` proof-span quickfixes to `lean4-lsp-mcp`
(`bin/lean-autoslim.js`) for live LSP or `lake env lean` kernel verification.

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


def resolve_lean_autoslim_bin(skills_root: Path | None = None) -> tuple[list[str], Path]:
    """Locate `bin/lean-autoslim.js` or `lean-autoslim` executable.

    Returns `(command_prefix, script_path)`.
    """
    node_bin = shutil.which("node") or "node"
    env_override = os.environ.get("LEAN_AUTOSLIM_BIN", "").strip()
    if env_override:
        cand = Path(env_override).expanduser().resolve()
        if cand.is_file():
            if cand.suffix in (".js", ".mjs", ".cjs"):
                return ([node_bin, str(cand)], cand)
            return ([str(cand)], cand)

    here = Path(__file__).resolve()
    root = skills_root or here.parents[3]
    # Prefer the maintained host integration over an optional nested tooling clone.
    search_candidates: list[Path] = [root / "packages" / "lean-analysis" / "bin" / "lean-autoslim.js"]
    for anc in root.parents:
        search_candidates.append(anc / "packages" / "lean-analysis" / "bin" / "lean-autoslim.js")
    search_candidates.append(root / "tools" / "lean-lsp-mcp" / "bin" / "lean-autoslim.js")
    for anc in root.parents:
        search_candidates.append(anc / "tools" / "lean-lsp-mcp" / "bin" / "lean-autoslim.js")

    for cand in search_candidates:
        if cand.is_file():
            return ([node_bin, str(cand)], cand)

    which_bin = shutil.which("lean-autoslim")
    if which_bin:
        resolved = Path(which_bin).resolve()
        return ([which_bin], resolved)

    raise FileNotFoundError(
        "Could not locate bin/lean-autoslim.js (set LEAN_AUTOSLIM_BIN or install lean4-lsp-mcp)."
    )


def run_autoslim(
    file_path: str | Path | list[str | Path],
    *,
    apply: bool = False,
    mode: str = "auto",
    allow_altproof_import: bool = False,
    routes: list[str] | None = None,
    max_candidates: int = 50,
    timeout_ms: int = 25000,
) -> dict[str, Any]:
    """Execute kernel-verified auto-slimmer on `file_path` and return parsed JSON report."""
    targets = [Path(p).expanduser().resolve() for p in (file_path if isinstance(file_path, list) else [file_path])]
    if not targets:
        raise ValueError("At least one Lean file is required")
    for target in targets if not isinstance(file_path, list) else []:
        if not target.is_file():
            raise FileNotFoundError(f"Lean file not found: {target}")

    cmd_prefix, _ = resolve_lean_autoslim_bin()
    cmd: list[str] = list(cmd_prefix) + [str(target) for target in targets] + [
        "--json",
        "--mode",
        mode,
        "--max-candidates",
        str(max_candidates),
        "--timeout-ms",
        str(timeout_ms),
    ]
    if apply:
        cmd.append("--apply")
    if allow_altproof_import:
        cmd.append("--allow-altproof-import")
    for r in routes or []:
        if r:
            cmd.extend(["--route", r])

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
        raise RuntimeError(f"lean-autoslim produced empty output ({stderr_msg})")

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Failed to parse lean-autoslim JSON output (exit={proc.returncode}): {exc}\n{stdout[:400]}"
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError("lean-autoslim JSON payload must be an object")
    if proc.returncode != 0 and not (payload.get("kind") == "batch"
            and payload.get("completed") is False and isinstance(payload.get("reports"), list)
            and isinstance(payload.get("failures"), list)):
        raise RuntimeError(f"lean-autoslim failed (exit={proc.returncode}): {proc.stderr.strip() or stdout[:400]}")
    return payload


def format_autoslim_markdown(report: dict[str, Any]) -> str:
    """Render concise Markdown summary of an `AutoSlimReport` dict."""
    if report.get("kind") == "batch":
        return "\n\n".join([
            f"## Batch fixes: {len(report.get('reports', []))}/{report.get('filesRequested', 0)} files processed",
            *(format_autoslim_markdown(r) for r in report.get("reports", [])),
            *(f"Failed: {r.get('filePath', '')}: {r.get('error', '')}" for r in report.get("failures", [])),
        ])
    verified = int(report.get("verifiedCount", report.get("candidatesAccepted", 0)))
    discovered = int(report.get("candidatesDiscovered", report.get("candidatesFound", 0)))
    rejected_cnt = int(report.get("rejectedCount", report.get("candidatesRejected", 0)))
    lines_saved = int(report.get("netLinesSaved", report.get("totalLinesSaved", 0)))
    bytes_saved = int(report.get("netBytesSaved", report.get("totalBytesSaved", 0)))
    backend = str(report.get("backendUsed", report.get("modeUsed", "unknown")))
    lines = [
        f"## Auto-Slimmer (`{report.get('filePath', '')}`)",
        f"- **Backend:** `{backend}` (`applied={report.get('applied', False)}`)",
        f"- **Candidates:** `{verified}/{discovered}` verified (`{rejected_cnt}` rejected)",
        f"- **Delta:** `{report.get('linesBefore', 0)} -> {report.get('linesAfter', 0)}` lines "
        f"(`-{lines_saved}`), `-{bytes_saved}` bytes",
    ]
    if report.get("importInserted") or report.get("addedAltProofImport"):
        lines.append("- **Import:** auto-inserted project AltProof / Tactics import (kernel-verified)")

    edits = report.get("edits") or []
    if edits:
        lines.append("")
        lines.append("| Theorem | Route | Winning Tactic | Saved |")
        lines.append("| :--- | :--- | :--- | ---: |")
        for e in edits:
            thm = e.get("theoremName", "")
            route = e.get("route", "")
            winner = e.get("newText", "")
            saved = f"-{e.get('linesSaved', 0)}L (-{e.get('bytesSaved', 0)}B)"
            lines.append(f"| `{thm}` | `{route}` | `{winner}` | {saved} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="altproof autoslim",
        description="Kernel-verified Lean 4 proof auto-slimmer (lean-analyzer + lean-lsp)",
    )
    parser.add_argument("files", type=Path, nargs="+", help="Target .lean files")
    parser.add_argument("--apply", action="store_true", help="Write verified slimmed file atomically")
    parser.add_argument(
        "--mode",
        choices=("auto", "lsp", "batch"),
        default="auto",
        help="Verification backend: live LSP when warm & unlocked, or batch lake env lean",
    )
    parser.add_argument(
        "--allow-altproof-import",
        action="store_true",
        help="Permit trying custom AltProof tactics (adding project AltProof/Tactics import if present)",
    )
    parser.add_argument(
        "--route",
        action="append",
        dest="routes",
        default=[],
        help="Restrict to specific AltProof route ID(s) (repeatable)",
    )
    parser.add_argument("--max-candidates", type=int, default=50, help="Maximum candidates to evaluate")
    parser.add_argument("--timeout-ms", type=int, default=25000, help="Per-attempt timeout in milliseconds")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown summary instead of JSON")
    args = parser.parse_args(argv)

    try:
        report = run_autoslim(
            args.files if len(args.files) > 1 else args.files[0],
            apply=args.apply,
            mode=args.mode,
            allow_altproof_import=args.allow_altproof_import,
            routes=args.routes,
            max_candidates=args.max_candidates,
            timeout_ms=args.timeout_ms,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.markdown:
        print(format_autoslim_markdown(report))
    else:
        print(json.dumps(report, indent=2))
    return 1 if report.get("kind") == "batch" and report.get("completed") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
