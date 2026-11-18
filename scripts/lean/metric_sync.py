#!/usr/bin/env python3
"""
Metric Synchronization Enforcement
Compares Lean project metrics with paper appendix values.
Reports mismatches between actual codebase state and documented metrics.
Referenced by lean-doc-improvement Part 6 and lean-gateway SK-06.

Usage:
    python3 scripts/metric_sync.py [--lean-dir Project] [--paper docs/paper.tex]
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lean_source_lex import neutralize_lean_source


def compute_lean_metrics(lean_dir: Path) -> dict[str, int]:
    """Compute actual metrics from the Lean codebase."""
    metrics: dict[str, int] = {
        "total_lines": 0,
        "total_theorems": 0,
        "total_lemmas": 0,
        "total_definitions": 0,
        "total_sorry": 0,
        "module_count": 0,
    }

    prefix = r"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|public|noncomputable|unsafe|partial|local|meta)\s+)*"
    theorem_pattern = re.compile(prefix + r"theorem\s+", re.MULTILINE)
    lemma_pattern = re.compile(prefix + r"lemma\s+", re.MULTILINE)
    def_pattern = re.compile(prefix + r"(?:def|structure|inductive|class|abbrev)\s+", re.MULTILINE)
    sorry_pattern = re.compile(r"\bsorry\b")

    if not lean_dir.is_dir():
        raise ValueError(f"Lean directory does not exist: {lean_dir}")
    for lean_file in sorted(lean_dir.rglob("*.lean")):
        if any(part.startswith(".") for part in lean_file.relative_to(lean_dir).parts):
            continue
        metrics["module_count"] += 1
        with open(lean_file, encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()

        metrics["total_lines"] += len(lines)
        content = neutralize_lean_source(content)
        content = re.sub(r"«[^»]*»", lambda m: "".join("\n" if c == "\n" else " " for c in m.group()), content)
        metrics["total_theorems"] += len(theorem_pattern.findall(content))
        metrics["total_lemmas"] += len(lemma_pattern.findall(content))
        metrics["total_definitions"] += len(def_pattern.findall(content))
        metrics["total_sorry"] += len(sorry_pattern.findall(content))

    return metrics


def extract_paper_metrics(paper_path: Path) -> dict[str, int | None]:
    """Extract metrics claimed in the paper/appendix.
    Returns None for metrics not found in the paper.
    """
    metrics: dict[str, int | None] = {
        "total_lines": None,
        "total_theorems": None,
        "total_definitions": None,
        "total_lemmas": None,
        "total_sorry": None,
        "module_count": None,
    }

    if not paper_path.exists():
        return metrics

    with open(paper_path, encoding="utf-8") as f:
        content = f.read()

    # Explicit source metrics avoid conflating compiled declarations or unrelated
    # theorem counts in prose with this recursive textual source census.
    explicit = {}
    for key, value in re.findall(r"^%\s*lean-metric\s+(\w+)\s*:\s*(\d+)\s*$", content, re.MULTILINE):
        if key in explicit and explicit[key] != value:
            raise ValueError(f"Conflicting paper claims for {key}")
        explicit[key] = value
    for key in metrics:
        if key in explicit:
            metrics[key] = int(explicit[key])
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Sync Lean metrics with paper")
    parser.add_argument(
        "--lean-dir", type=Path, default=Path("Project"), help="Directory containing .lean files"
    )
    parser.add_argument(
        "--paper", type=Path, default=Path("docs/paper.tex"), help="Paper LaTeX file to check"
    )
    args = parser.parse_args()

    if not args.paper.is_file():
        parser.error(f"Paper does not exist: {args.paper}")
    try:
        actual = compute_lean_metrics(args.lean_dir)
    except ValueError as exc:
        parser.error(str(exc))
    if actual["module_count"] == 0:
        parser.error("No Lean source files in the requested coverage set")
    try:
        paper = extract_paper_metrics(args.paper)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Source coverage: {args.lean_dir.resolve()}, recursive, hidden directories excluded")
    print("Counts are lexical source metrics, not a kernel census. Paper claims require % lean-metric KEY: VALUE.")

    print("Metric Sync Report")
    print("=" * 60)
    print(f"{'Metric':<25} {'Lean (actual)':<15} {'Paper (claimed)':<15} {'Status'}")
    print("-" * 60)

    mismatches = 0
    unknowns = 0

    display_names = {
        "total_lines": "Lines of code",
        "total_theorems": "Theorems",
        "total_lemmas": "Lemmas",
        "total_definitions": "Definitions",
        "total_sorry": "Sorry count",
        "module_count": "Modules",
    }

    for key in [
        "total_lines",
        "total_theorems",
        "total_lemmas",
        "total_definitions",
        "total_sorry",
        "module_count",
    ]:
        actual_val = actual.get(key, 0)
        paper_val = paper.get(key)
        name = display_names.get(key, key)

        if paper_val is None:
            status = "not in paper"
            unknowns += 1
        elif actual_val == paper_val:
            status = "✓ match"
        else:
            status = "✗ MISMATCH"
            mismatches += 1

        paper_str = str(paper_val) if paper_val is not None else "--"
        print(f"  {name:<23} {actual_val:<15} {paper_str:<15} {status}")

    print("-" * 60)
    thm_plus_lem = actual["total_theorems"] + actual["total_lemmas"]
    print(f"  {'Theorems + Lemmas':<23} {thm_plus_lem:<15}")
    print()

    if mismatches > 0:
        print(f"FAIL: {mismatches} metric(s) out of sync with paper")
        sys.exit(1)
    elif unknowns > 0:
        print(f"WARN: {unknowns} metric(s) not found in paper (may need manual check)")
        sys.exit(2)
    else:
        print("OK: All metrics in sync")
        sys.exit(0)


if __name__ == "__main__":
    main()
