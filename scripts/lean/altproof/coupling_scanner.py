#!/usr/bin/env python3
"""Statement-level coupling scanner (T2, COUPLING_REGISTER.md).

Scans Lean 4 production modules for `theorem` and `lemma` declarations whose
statement headers mention `Real` (or Unicode real symbol) and classifies each
statement by its operator vocabulary into:
  - `abstraction-safe`: only ring/order/sum/matrix vocabulary (generalizable
    over ordered commutative rings or additive groups);
  - `nat-mixed`: statement mixes `Real` with `Nat` / scaled-integer (`x100`)
    arithmetic or `Finset.range` / `Nat` casts;
  - `real-specific`: statement relies on analytic, transcendental, metric,
    filter, derivative, or measure-theoretic vocabulary (`sqrt`, `exp`, `log`,
    `Tendsto`, `nhds`, `deriv`, `Measurable`, `ENNReal`, `NNReal`, etc.).

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

DECL_START_RE = re.compile(
    r"^\s*(?:@(?:[^\n]+)\s+)*(?:noncomputable\s+|private\s+|protected\s+)*"
    r"(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_']*)",
    re.MULTILINE,
)

REAL_TOKEN_RE = re.compile(r"(?:\bReal\b|\u211d)")

REAL_SPECIFIC_RE = re.compile(
    r"\b(?:"
    r"sqrt|exp|log|sin|cos|tan|arcsin|arccos|arctan|sinh|cosh|tanh|"
    r"Tendsto|atTop|nhds|Filter|Continuous|ContinuousOn|Differentiable|"
    r"HasDerivAt|deriv|iteratedDeriv| Measure|Measurable|ENNReal|NNReal|"
    r"Metric|dist|ball|closedBall| Normed|CompleteSpace|CauchySeq|"
    r" sSup| sInf| iSup| iInf| Real\.pi| Complex"
    r")\b"
)

NAT_MIXED_RE = re.compile(
    r"(?:\bNat\b|\u2115|\bFinset\.range\b|\b100\b|\b1000\b|\b10000\b|"
    r"\bSimplex\d*\b|\bScaled\b|\bx100\b|\bbps\b|\bNat\.cast\b)"
)

HISTORICAL_SNAPSHOT_2026_10_14 = {
    "captured_at": "2026-10-14",
    "total_real_statements": 2548,
    "classes": {
        "abstraction-safe": {"count": 1764, "share_pct": 69.2},
        "nat-mixed": {"count": 533, "share_pct": 20.9},
        "real-specific": {"count": 251, "share_pct": 9.9},
    },
    "abstraction_safe_family_leaders": {
        "CuspCatastrophe": 435,
        "StochasticCCV": 390,
        "ReinforcementLearning": 338,
        "AgenticSafety": 226,
        "LyapunovStability": 123,
    },
}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/-.*?-/", " ", text, flags=re.DOTALL)
    text = re.sub(r"--[^\n]*", " ", text)
    return text


def _extract_statement_headers(source: str) -> list[tuple[str, str, str]]:
    """Return list of (kind, name, header_text) for each theorem/lemma."""
    clean = _strip_comments(source)
    results: list[tuple[str, str, str]] = []
    for match in DECL_START_RE.finditer(clean):
        kind = match.group(1)
        name = match.group(2)
        start = match.start()
        tail = clean[start : start + 4000]
        # Find the proof separator `:= by` or `:=` at paren/bracket depth 0
        depth = 0
        end_idx = len(tail)
        i = 0
        while i < len(tail) - 1:
            ch = tail[i]
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth = max(0, depth - 1)
            elif depth == 0 and tail[i : i + 2] == ":=":
                end_idx = i
                break
            elif depth == 0 and tail[i : i + 6] == "\nwhere":
                end_idx = i
                break
            i += 1
        header = tail[:end_idx].strip()
        results.append((kind, name, header))
    return results


def _family_of_path(rel_path: str) -> str:
    parts = Path(rel_path).parts
    # e.g. MyProject/Stochastic/Doeblin.lean -> Stochastic
    if len(parts) >= 3:
        return parts[1]
    if len(parts) == 2:
        return Path(parts[1]).stem
    return parts[0] if parts else "root"


def classify_statement(header: str) -> str:
    """Classify a `Real`-typed theorem statement into one of three coupling classes."""
    if REAL_SPECIFIC_RE.search(header):
        return "real-specific"
    if NAT_MIXED_RE.search(header):
        return "nat-mixed"
    return "abstraction-safe"


def scan_corpus(corpus_root: Path) -> dict:
    """Scan all production `.lean` files under `corpus_root`."""
    lean_files = sorted(
        p
        for p in corpus_root.rglob("*.lean")
        if ".scratch" not in p.parts
        and "Tests" not in p.parts
        and ".lake" not in p.parts
    )
    class_counts: Counter[str] = Counter()
    family_safe_counts: Counter[str] = Counter()
    family_totals: Counter[str] = Counter()
    total_decls = 0
    real_decls = 0

    for path in lean_files:
        try:
            rel = str(path.relative_to(corpus_root.parent))
        except ValueError:
            rel = str(path)
        source = path.read_text(encoding="utf-8", errors="replace")
        file_has_real = bool(REAL_TOKEN_RE.search(source))
        headers = _extract_statement_headers(source)
        total_decls += len(headers)
        fam = _family_of_path(rel)
        for _kind, _name, header in headers:
            if not (REAL_TOKEN_RE.search(header) or (file_has_real and "variable" in source)):
                continue
            if not REAL_TOKEN_RE.search(header):
                continue
            real_decls += 1
            cls = classify_statement(header)
            class_counts[cls] += 1
            family_totals[fam] += 1
            if cls == "abstraction-safe":
                family_safe_counts[fam] += 1

    total = max(1, real_decls)
    live_classes = {
        cls: {
            "count": class_counts.get(cls, 0),
            "share_pct": round(100.0 * class_counts.get(cls, 0) / total, 1),
        }
        for cls in ("abstraction-safe", "nat-mixed", "real-specific")
    }
    top_families = dict(family_safe_counts.most_common(10))

    return {
        "schema_version": "1.0",
        "scanner": "crates/lean-analyzer/python/src/altproof/coupling_scanner.py",
        "telemetry_not_authority": True,
        "cannot_authorize": [
            "gate_pass",
            "ship_readiness",
            "production_certification",
        ],
        "historical_baseline_2026_10_14": HISTORICAL_SNAPSHOT_2026_10_14,
        "live_scan": {
            "production_files_scanned": len(lean_files),
            "total_theorem_lemma_decls": total_decls,
            "explicit_real_header_statements": real_decls,
            "classes": live_classes,
            "abstraction_safe_by_family": top_families,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="altproof coupling-scan",
        description="Run T2 statement-level Real-coupling scan across a Lean corpus",
    )
    parser.add_argument(
        "corpus_root",
        nargs="?",
        default=None,
        help="Path to Lean production directory (default: discovered via lean-project.toml or .)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to write JSON manifest",
    )
    args = parser.parse_args(argv)
    if args.corpus_root is None:
        from .project_config import load_project_config
        target_root = load_project_config().corpus_dir
    else:
        target_root = Path(args.corpus_root)
    payload = scan_corpus(target_root)
    text = json.dumps(payload, indent=2) + "\n"
    if args.out is not None:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
