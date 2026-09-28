#!/usr/bin/env python3
"""
Unified Launcher for Lean 4 Formalization DAG Visualizer.

Supports arbitrary Lean projects, subpackages (packages/*), EASCI, and presets.
Automatically generates dependency graph JSON and launches the standalone web application.

Strict 7-bit ASCII only (INV-001). Standard library only.

Usage:
    python3 launch_visualizer.py packages/stochastic-ccv
    python3 launch_visualizer.py docs/easci/lean/EASCI
    python3 launch_visualizer.py --preset flt
    python3 launch_visualizer.py --preset nse --no-browser
    python3 launch_visualizer.py packages/agentic-safety --json-only
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = SCRIPT_DIR.parent.parent
SERVE_SCRIPT = SKILLS_DIR / "tools" / "visualizer" / "serve.py"
BREAKDOWN_SCRIPT = SCRIPT_DIR / "formalization_breakdown.py"

PRESETS = {
    "easci": "docs/easci/lean/EASCI",
    "flt": "docs/easci/lean/fermats-last-theorem",
    "nse": "docs/easci/lean/NavierStokesAndEuler",
}


def find_repo_root() -> Path:
    """Find the root repository directory."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs" / "easci" / "lean").is_dir() and (parent / "packages").is_dir():
            return parent
    return SKILLS_DIR.parent.parent.parent  # Fallback


def resolve_target(target_str: str, repo_root: Path) -> Path:
    """Resolve target path or preset to physical Path."""
    key = target_str.lower().strip("@/ ")
    if key in PRESETS:
        candidate = repo_root / PRESETS[key]
        if candidate.is_dir():
            return candidate

    # Try relative to cwd
    p1 = Path(target_str).resolve()
    if p1.is_dir():
        return p1

    # Try relative to repo root
    p2 = (repo_root / target_str).resolve()
    if p2.is_dir():
        return p2

    # Try inside packages/
    p3 = (repo_root / "packages" / target_str).resolve()
    if p3.is_dir():
        return p3

    print(f"Error: Target directory not found: {target_str}", file=sys.stderr)
    sys.exit(1)


def generate_or_get_graph(
    target_path: Path,
    repo_root: Path,
    refresh: bool = False,
    custom_out: str = None,
) -> Path:
    """Extract or return cached visualizer graph JSON."""
    slug = target_path.name.lower().replace(" ", "-")
    cache_dir = repo_root / ".cache" / "graphs"
    cache_dir.mkdir(parents=True, exist_ok=True)

    out_file = Path(custom_out).resolve() if custom_out else (cache_dir / f"{slug}_dag.json")

    # Check if cache is fresh
    needs_rebuild = refresh or (not out_file.is_file())
    if not needs_rebuild:
        cache_mtime = out_file.stat().st_mtime
        for f in target_path.rglob("*.lean"):
            if f.stat().st_mtime > cache_mtime:
                needs_rebuild = True
                break

    if needs_rebuild:
        print(f"[*] Extracting formalization DAG from: {target_path}")
        cmd = [
            sys.executable,
            str(BREAKDOWN_SCRIPT),
            str(target_path),
            "--json-graph",
            str(out_file),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error executing breakdown analyzer:\n{res.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"[OK] Generated graph: {out_file} ({out_file.stat().st_size} bytes)")
    else:
        print(f"[*] Using cached formalization DAG: {out_file}")

    return out_file


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launch standalone Lean 4 Formalization DAG Visualizer for any project or package"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="docs/easci/lean/EASCI",
        help="Target Lean formalization directory or package path (default: docs/easci/lean/EASCI)",
    )
    parser.add_argument(
        "--preset",
        choices=["easci", "flt", "nse"],
        help="Target named benchmark preset",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8088,
        help="Port to bind HTTP server (default: 8088, auto-increments if in use)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open web browser automatically (useful for AI sessions and SSH)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-extraction of dependency graph even if cache exists",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only extract graph JSON and print path without starting server",
    )
    parser.add_argument(
        "--output-graph",
        type=str,
        help="Custom output file path for generated graph JSON",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    repo_root = find_repo_root()

    target_str = args.preset if args.preset else args.target
    target_path = resolve_target(target_str, repo_root)

    graph_file = generate_or_get_graph(
        target_path=target_path,
        repo_root=repo_root,
        refresh=args.refresh,
        custom_out=args.output_graph,
    )

    if args.json_only:
        print(f"Graph JSON available at: {graph_file}")
        return 0

    if not SERVE_SCRIPT.is_file():
        print(f"Error: Visualizer server script not found: {SERVE_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    cmd = [
        sys.executable,
        str(SERVE_SCRIPT),
        "--graph",
        str(graph_file),
        "--port",
        str(args.port),
        "--host",
        args.host,
    ]
    if args.no_browser:
        cmd.append("--no-browser")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[OK] Visualizer session terminated.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
