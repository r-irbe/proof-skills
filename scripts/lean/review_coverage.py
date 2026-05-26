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
import os
import re
import sys
from pathlib import Path


def extract_theorems(lean_dir: Path) -> dict[str, list[tuple[str, int]]]:
    """Extract all theorem/lemma names from .lean files.
    Returns {module_name: [(theorem_name, line_number), ...]}
    """
    pattern = re.compile(r'^(theorem|lemma)\s+(\S+)', re.MULTILINE)
    results: dict[str, list[tuple[str, int]]] = {}

    for lean_file in sorted(lean_dir.glob('*.lean')):
        module = lean_file.stem
        theorems = []
        with open(lean_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
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

    name_pattern = re.compile(r'##\s*Theorem:\s*`?(\S+?)`?', re.IGNORECASE)

    for review_file in reviews_dir.rglob('*.md'):
        with open(review_file, 'r', encoding='utf-8') as f:
            content = f.read()
        for m in name_pattern.finditer(content):
            reviewed.add(m.group(1))

    return reviewed


def main():
    parser = argparse.ArgumentParser(description='Check review coverage for Lean 4 theorems')
    parser.add_argument('--lean-dir', type=Path, required=True,
                        help='Directory containing .lean files')
    parser.add_argument('--reviews-dir', type=Path, default=Path('reviews'),
                        help='Directory containing review records')
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


if __name__ == '__main__':
    main()
