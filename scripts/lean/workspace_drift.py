#!/usr/bin/env python3
"""Workspace mirror drift checker for multi-package Lean 4 corpora.

Reads `[workspace]` and `[workspace.mirrors]` from `lean-project.toml` (via
`project_config.py`) to classify every matched pair between downstream
packages and the upstream monolith corpus, enumerate single-home files on
both sides, and report substantive divergences.

Classification per matched pair (import lines stripped, whitespace preserved):
  - import-only : content identical after stripping `import` lines.
  - tiny        : <= 6 differing lines outside imports (lint-level drift).
  - substantive : more lines differ; the newer side is estimated by line
                  counts (`PKG` / `CORPUS` / `BOTH-DIVERGED`).

Exit status: 0 when there is no substantive divergence, 1 otherwise.
Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from project_config import load_project_config  # noqa: E402

EXCLUDE = (".lake", "vendor", ".git", "node_modules")
TINY_THRESHOLD = 6


def keep(path: Path) -> bool:
    return not any(part in EXCLUDE for part in path.parts)


def is_corpus_pin(rel: str) -> bool:
    """Corpus surface-pin files (Tests/**) are assertion stubs, not forks."""
    return "Tests" in Path(rel).parts


def strip_imports(lines: list[str]) -> list[str]:
    return [line for line in lines if not line.lstrip().startswith("import")]


def classify(
    pkg_lines: list[str], corpus_lines: list[str]
) -> tuple[str, int, int]:
    a, b = strip_imports(pkg_lines), strip_imports(corpus_lines)
    if a == b:
        return "import-only", 0, 0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    pkg_only = corpus_only = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("delete", "replace"):
            pkg_only += i2 - i1
        if tag in ("insert", "replace"):
            corpus_only += j2 - j1
    if pkg_only + corpus_only <= TINY_THRESHOLD:
        return "tiny", pkg_only, corpus_only
    return "substantive", pkg_only, corpus_only


def newer_side(pkg_only: int, corpus_only: int) -> str:
    if pkg_only > 2 * corpus_only:
        return "PKG"
    if corpus_only > 2 * pkg_only:
        return "CORPUS"
    return "BOTH-DIVERGED"


def lean_files(root: Path) -> dict[str, Path]:
    """Map: path relative to `root` -> Path, for *.lean files, EXCLUDE-pruned."""
    if not root.exists():
        return {}
    return {
        str(p.relative_to(root)): p
        for p in sorted(root.rglob("*.lean"))
        if keep(p)
    }


def pair_files(
    pkg_files: dict[str, Path], corpus_files: dict[str, Path]
) -> tuple[list[tuple[Path, Path]], list[Path], list[Path], list[str]]:
    corpus_live = {k: v for k, v in corpus_files.items() if not is_corpus_pin(k)}
    corpus_pins = {k: v for k, v in corpus_files.items() if is_corpus_pin(k)}
    matched: list[tuple[Path, Path]] = []
    pkg_only: list[Path] = []
    used_corpus: set[str] = set()
    corpus_by_name = {Path(k).name: (k, v) for k, v in corpus_live.items()}
    for key, pkg_path in pkg_files.items():
        if key in corpus_live:
            matched.append((pkg_path, corpus_live[key]))
            used_corpus.add(key)
            continue
        rel = Path(key)
        if len(rel.parts) == 1 and rel.name in corpus_by_name:
            ckey, cpath = corpus_by_name[rel.name]
            matched.append((pkg_path, cpath))
            used_corpus.add(ckey)
            continue
        pkg_only.append(pkg_path)
    corpus_only = [
        corpus_live[k] for k in sorted(set(corpus_live) - used_corpus)
    ]
    return matched, pkg_only, corpus_only, sorted(corpus_pins)


def package_lib_roots(
    pkg_root: Path, corpus_root: Path, root: Path
) -> list[tuple[Path, Path]]:
    if (pkg_root / corpus_root.name).is_dir():
        primary = pkg_root / corpus_root.name
    else:
        content_children = [
            child
            for child in sorted(pkg_root.iterdir())
            if child.is_dir() and any(child.rglob("*.lean"))
        ]
        primary = content_children[0] if len(content_children) == 1 else pkg_root

    pairs = [(primary, corpus_root)]
    corpus_parent = corpus_root.parent
    for child in sorted(pkg_root.iterdir()):
        if not child.is_dir() or child == primary:
            continue
        twin = corpus_parent / child.name
        if not twin.is_dir():
            continue
        if is_corpus_pin(str(twin.relative_to(root))):
            continue
        if not any(lean_files(twin).values()):
            continue
        pairs.append((child, twin))
    return pairs


def load_mirrors(start_dir: Path | None = None) -> tuple[Path, dict[str, str], str]:
    cfg = load_project_config(start_dir)
    if not cfg.workspace_mirrors and start_dir is not None:
        nested = Path(start_dir).resolve() / "docs" / "easci" / "lean"
        if nested.is_dir():
            cfg = load_project_config(nested)
    ws_root = cfg.workspace_root
    mirrors = cfg.workspace_mirrors
    packages_dir = str(cfg.raw.get("workspace", {}).get("packages_dir", "packages"))
    return ws_root, mirrors, packages_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=None, help="repository or project root (default: auto-discover)"
    )
    parser.add_argument("--quiet", action="store_true", help="print only the summary line")
    parser.add_argument(
        "--list", action="store_true", help="also print every single-home file"
    )
    parser.add_argument("--json", action="store_true", help="output JSON report")
    args = parser.parse_args(argv)

    root, mirrors, packages_dir_rel = load_mirrors(args.root)
    if args.root is not None and not mirrors:
        root = args.root.resolve()

    buckets = {"import-only": 0, "tiny": 0, "substantive": 0}
    substantive: list[tuple[str, int, int, str]] = []
    pkg_only_files: list[str] = []
    corpus_only_files: list[str] = []
    pin_files = 0
    unmapped_packages: list[str] = []

    packages_dir = root / packages_dir_rel
    if packages_dir.exists():
        for child in sorted(packages_dir.iterdir()):
            if (child / "lakefile.lean").exists():
                key = str(child.relative_to(root))
                if key not in mirrors:
                    unmapped_packages.append(key)

    for pkg, corpus in mirrors.items():
        pkg_root = root / pkg
        corpus_root = root / corpus
        if not pkg_root.exists():
            continue
        for lib_root, corpus_lib in package_lib_roots(pkg_root, corpus_root, root):
            pkg_files = lean_files(lib_root)
            corpus_files = lean_files(corpus_lib)
            if pkg.endswith("reinforcement-learning") and corpus_lib == corpus_root:
                prob_root = corpus_root.parent / "Probability"
                if prob_root.is_dir():
                    for k, v in lean_files(prob_root).items():
                        corpus_files[f"Probability/{k}"] = v
            matched, pkg_only, corpus_only, pins = pair_files(pkg_files, corpus_files)
            pin_files += len(pins)
            pkg_only_files += [str(p.relative_to(root)) for p in pkg_only]
            corpus_only_files += [str(p.relative_to(root)) for p in corpus_only]
            for pkg_path, corpus_path in matched:
                kind, pkg_del, corpus_del = classify(
                    pkg_path.read_text(encoding="utf-8", errors="replace").splitlines(),
                    corpus_path.read_text(encoding="utf-8", errors="replace").splitlines(),
                )
                buckets[kind] += 1
                if kind == "substantive":
                    substantive.append(
                        (str(pkg_path.relative_to(root)), pkg_del, corpus_del, newer_side(pkg_del, corpus_del))
                    )

    if args.json:
        print(
            json.dumps(
                {
                    "buckets": buckets,
                    "pkg_only_count": len(pkg_only_files),
                    "corpus_only_count": len(corpus_only_files),
                    "pin_files": pin_files,
                    "unmapped_packages": unmapped_packages,
                    "substantive": [
                        {"file": f, "pkg_lines": p, "corpus_lines": c, "newer_side": s}
                        for f, p, c, s in substantive
                    ],
                },
                indent=2,
            )
        )
        return 1 if substantive else 0

    print(
        f"fork-state: {buckets['import-only']} import-only, "
        f"{buckets['tiny']} tiny, {buckets['substantive']} substantive "
        f"(pkg-only files: {len(pkg_only_files)}, "
        f"corpus-only files: {len(corpus_only_files)}, "
        f"corpus pins: {pin_files})"
    )
    if unmapped_packages and not args.quiet:
        for key in unmapped_packages:
            print(f"note: package without a MAP entry: {key}")

    if args.list and not args.quiet:
        if pkg_only_files:
            print("\npackage-only files:")
            for p in pkg_only_files:
                print(f"  {p}")
        if corpus_only_files:
            print("\ncorpus-only files:")
            for p in corpus_only_files:
                print(f"  {p}")

    if substantive and not args.quiet:
        print()
        print(f"{'file':<72} {'pkg+':>5} {'corp+':>6}  newer-side")
        for path, pkg_del, corpus_del, side in sorted(
            substantive, key=lambda x: -(x[1] + x[2])
        ):
            print(f"{path:<72} {pkg_del:>5} {corpus_del:>6}  {side}")
        print()
        print("Reconcile per-file with review; never copy one tree over the other wholesale.")

    return 1 if substantive else 0


if __name__ == "__main__":
    sys.exit(main())
