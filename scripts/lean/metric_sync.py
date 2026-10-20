#!/usr/bin/env python3
"""
Metric Synchronization Enforcement
Compares Lean project metrics with paper appendix values.
Reports mismatches between actual codebase state and documented metrics.
Referenced by lean-doc-improvement Part 6 and lean-gateway SK-06.

Usage:
    python3 scripts/metric_sync.py [--lean-dir EASCI] [--paper docs/easci-tufte.tex]
"""

import argparse
import re
import sys
from pathlib import Path


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

    theorem_pattern = re.compile(r"^theorem\s+", re.MULTILINE)
    lemma_pattern = re.compile(r"^lemma\s+", re.MULTILINE)
    def_pattern = re.compile(r"^(def|structure|inductive|class)\s+", re.MULTILINE)
    sorry_pattern = re.compile(r"\bsorry\b")

    for lean_file in sorted(lean_dir.glob("*.lean")):
        metrics["module_count"] += 1
        with open(lean_file, encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()

        metrics["total_lines"] += len(lines)
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
        "total_sorry": None,
        "module_count": None,
    }

    if not paper_path.exists():
        return metrics

    with open(paper_path, encoding="utf-8") as f:
        content = f.read()

    # Common patterns in LaTeX for stating metrics
    patterns = {
        "total_lines": [
            r"(\d[\d,]+)\s*lines?\s*of\s*(?:Lean|formal)",
            r"lines?\s*(?:of\s*code)?[:\s]*(\d[\d,]+)",
        ],
        "total_theorems": [
            r"(\d[\d,]+)\s*theorems?",
            r"theorems?[:\s]*(\d[\d,]+)",
        ],
        "total_definitions": [
            r"(\d[\d,]+)\s*definitions?",
        ],
        "total_sorry": [
            r"(\d+)\s*sorry",
            r"sorry[:\s]*(\d+)",
            r"zero\s*sorry",
        ],
        "module_count": [
            r"(\d+)\s*modules?",
            r"modules?[:\s]*(\d+)",
        ],
    }

    for key, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, content, re.IGNORECASE)
            if m:
                if "zero" in pat.lower():
                    metrics[key] = 0
                else:
                    val = m.group(1).replace(",", "")
                    metrics[key] = int(val)
                break

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Sync Lean metrics with paper")
    parser.add_argument(
        "--lean-dir", type=Path, default=Path("EASCI"), help="Directory containing .lean files"
    )
    parser.add_argument(
        "--paper", type=Path, default=Path("docs/easci-tufte.tex"), help="Paper LaTeX file to check"
    )
    args = parser.parse_args()

    actual = compute_lean_metrics(args.lean_dir)
    paper = extract_paper_metrics(args.paper)

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
        sys.exit(0)
    else:
        print("OK: All metrics in sync")
        sys.exit(0)


if __name__ == "__main__":
    main()
