#!/usr/bin/env python3
"""Synchronize downstream package Lean modules upstream into the monolith corpus.

Reads `[workspace]` and `[workspace.mirrors]` from `lean-project.toml` (via
`project_config.py`) instead of hardcoding repository roots or package maps.
Respects module boundaries, rewrites imports to use `<Project>.*` namespace,
and updates umbrella re-export files.
Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from project_config import load_project_config  # noqa: E402


def build_mappings(start_dir: Path | None = None) -> tuple[Path, Path, str, list[tuple[Path, Path, str]]]:
    cfg = load_project_config(start_dir)
    if not cfg.workspace_mirrors and start_dir is not None:
        nested = Path(start_dir).resolve() / "docs" / "easci" / "lean"
        if nested.is_dir():
            cfg = load_project_config(nested)
    ws_root = cfg.workspace_root
    project_prefix = cfg.name
    corpus_dir_rel = cfg.raw.get("workspace", {}).get("corpus_dir")
    corpus_root = (ws_root / corpus_dir_rel) if corpus_dir_rel else cfg.corpus_dir
    mappings: list[tuple[Path, Path, str]] = []
    for pkg_rel, corp_rel in cfg.workspace_mirrors.items():
        pkg_base = ws_root / pkg_rel
        corp_target = ws_root / corp_rel
        domain_name = corp_target.name
        if (pkg_base / domain_name).is_dir():
            pkg_src = pkg_base / domain_name
        else:
            pkg_src = pkg_base
        mappings.append((pkg_src, corp_target, domain_name))
    return ws_root, corpus_root, project_prefix, mappings


def transform_imports(content: str, project_prefix: str, domain_names: list[str]) -> str:
    lines = content.splitlines(keepends=True)
    out = []
    for line in lines:
        if line.startswith("import "):
            line = re.sub(
                r"^import\s+ReinforcementLearning\.Probability\.",
                f"import {project_prefix}.Probability.",
                line,
            )
            for dom in domain_names:
                line = re.sub(
                    rf"^import\s+{re.escape(dom)}\.",
                    f"import {project_prefix}.{dom}.",
                    line,
                )
            line = re.sub(r"^import\s+Tactics$", f"import {project_prefix}.Tactics", line)
        out.append(line)
    return "".join(out)


def sync_missing_files(start_dir: Path | None = None, dry_run: bool = False) -> int:
    _, _, project_prefix, mappings = build_mappings(start_dir)
    domain_names = [m[2] for m in mappings]
    copied = 0
    for pkg_dir, corp_dir, _ in mappings:
        if not pkg_dir.is_dir():
            continue
        for root, _, files in os.walk(pkg_dir):
            if ".lake" in Path(root).parts:
                continue
            for f in files:
                if not f.endswith(".lean"):
                    continue
                rel = os.path.relpath(os.path.join(root, f), pkg_dir)
                target = corp_dir / rel
                if not target.exists():
                    if not dry_run:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        content = Path(root, f).read_text(encoding="utf-8")
                        transformed = transform_imports(content, project_prefix, domain_names)
                        target.write_text(transformed, encoding="utf-8")
                    copied += 1
    print(f"{'Would copy' if dry_run else 'Copied'} {copied} missing modules into {project_prefix}.")
    return copied


def update_umbrella_files(start_dir: Path | None = None, dry_run: bool = False) -> int:
    _, corpus_root, project_prefix, mappings = build_mappings(start_dir)
    updated_total = 0
    for pkg_src, _, dom in mappings:
        pkg_umbrella = pkg_src.parent / f"{dom}.lean"
        corp_umbrella = corpus_root / f"{dom}.lean"
        if not pkg_umbrella.is_file() or not corp_umbrella.is_file():
            continue
        pkg_imports = set()
        for line in pkg_umbrella.read_text(encoding="utf-8").splitlines():
            prefix = f"import {dom}."
            if line.startswith(prefix):
                pkg_imports.add(line[len(prefix):].strip())
        corp_lines = corp_umbrella.read_text(encoding="utf-8").splitlines(keepends=True)
        existing_mods = set()
        insert_idx = -1
        corp_prefix = f"import {project_prefix}.{dom}."
        for i, line in enumerate(corp_lines):
            if line.startswith(corp_prefix):
                existing_mods.add(line[len(corp_prefix):].strip())
                insert_idx = i
        added = [f"import {project_prefix}.{dom}.{m}\n" for m in sorted(pkg_imports) if m not in existing_mods]
        if insert_idx >= 0 and added:
            if not dry_run:
                new_lines = corp_lines[: insert_idx + 1] + added + corp_lines[insert_idx + 1 :]
                corp_umbrella.write_text("".join(new_lines), encoding="utf-8")
            print(f"Updated {dom}.lean with {len(added)} new imports.")
            updated_total += len(added)
    return updated_total


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None, help="Workspace or project root")
    ap.add_argument("--dry-run", action="store_true", help="Report missing modules without writing")
    args = ap.parse_args(argv)
    sync_missing_files(args.root, dry_run=args.dry_run)
    update_umbrella_files(args.root, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
