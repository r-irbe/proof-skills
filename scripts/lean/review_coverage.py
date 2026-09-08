#!/usr/bin/env python3
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
"""
Review Coverage Enforcement for Lean 4 projects.

Verifies every theorem/lemma in a Lean source directory has a corresponding
review record.

Usage:
    python3 scripts/lean/review_coverage.py --lean-dir MyProject [--reviews-dir reviews]
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from axiom_audit import strip_comments_preserving_newlines
except ImportError:  # direct-script execution from another cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from axiom_audit import strip_comments_preserving_newlines


def extract_theorems(lean_dir: Path) -> dict[str, list[tuple[str, int]]]:
    """Extract all theorem/lemma names from .lean files (recursive).
    Returns {module_name: [(theorem_name, line_number), ...]}

    Subdirectories are included (module name = relative path with `/`
    replaced by `.`); `Tests/`, `.scratch/`, and hidden dirs are excluded.

    Comments are stripped (line structure preserved) before matching so
    prose lines inside doc comments that begin with the word `theorem`/
    `lemma` are not counted as declarations.
    """
    pattern = re.compile(r"^(theorem|lemma)\s+(\S+)", re.MULTILINE)
    results: dict[str, list[tuple[str, int]]] = {}

    for lean_file in sorted(lean_dir.rglob("*.lean")):
        rel = lean_file.relative_to(lean_dir)
        parts = rel.parts
        if any(p in ("Tests", ".scratch") or p.startswith(".") for p in parts):
            continue
        module = ".".join([*parts[:-1], lean_file.stem])
        theorems = []
        try:
            source = strip_comments_preserving_newlines(
                lean_file.read_text(encoding="utf-8")
            )
        except OSError as exc:
            print(f"warning: skipping unreadable {lean_file}: {exc}", file=sys.stderr)
            continue
        for i, line in enumerate(source.splitlines(), 1):
            m = pattern.match(line)
            if m:
                theorems.append((m.group(2), i))
        if theorems:
            results[module] = theorems

    return results


def find_review_records(reviews_dir: Path) -> set[str]:
    """Find all theorem names that have review records."""
    reviewed: set[str] = set()
    if not reviews_dir.exists():
        return reviewed

    # `\w.` plus `'`: Lean identifier constituents include trailing primes
    # (`hasDerivAt'`, `G4'_implies_G4`).
    name_pattern = re.compile(r"##\s*Theorem:\s*`?([\w.']+)`?", re.IGNORECASE)

    for review_file in reviews_dir.rglob("*.md"):
        try:
            content = review_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"warning: skipping unreadable {review_file}: {exc}", file=sys.stderr)
            continue
        for m in name_pattern.finditer(content):
            reviewed.add(m.group(1))

    return reviewed


def main():
    parser = argparse.ArgumentParser(
        description="Check review coverage for Lean 4 theorems"
    )
    parser.add_argument(
        "--lean-dir", type=Path, required=True, help="Directory containing .lean files"
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=Path("reviews"),
        help="Directory containing review records",
    )
    args = parser.parse_args()

    theorems = extract_theorems(args.lean_dir)
    reviewed = find_review_records(args.reviews_dir)

    total = 0
    covered = 0
    uncovered_list: list[tuple[str, str, int]] = []

    for module, thms in theorems.items():
        for name, line in thms:
            total += 1
            if name in reviewed:
                covered += 1
            else:
                uncovered_list.append((module, name, line))

    pct = (covered / total * 100) if total > 0 else 0

    print(f"Review Coverage: {covered}/{total} ({pct:.1f}%)")
    print(f"{'=' * 50}")

    if uncovered_list:
        print(f"\nUncovered theorems ({len(uncovered_list)}):")
        for module, name, line in uncovered_list:
            print(f"  {module}.lean:L{line}  {name}")
        sys.exit(1)
    else:
        print("\nAll theorems have review records.")
        sys.exit(0)


if __name__ == "__main__":
    main()
