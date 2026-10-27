"""Legibility-cost v1 (S7) + Structural Logic Golfer & Semicolon Detector (Proposal 9A).

Scores a tactic proof block on:
  1. Verbose-lean4 discourse-move renderability (`steps`, `renderable`, `verbose_score`, `heavy_steps`).
  2. `numina-lean-agent` semicolon line-compression detector (`has_semicolons`, `semicolon_lines`)
     and 6-pattern structural golf opportunities (`golf_opportunities`).

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from have_cluster import detect_structural_golf_opportunities


@dataclass
class StepScore:
    step: str
    renderable: bool


RENDERABLE_PATTERNS = [
    re.compile(r"^exact\s+\S"),
    re.compile(r"^apply\s+\S"),
    re.compile(r"^have\s+\w+\s*:?=?\s*\S+"),
    re.compile(r"^(unfold|simp|simp_rw|rw|erw)\b"),
    re.compile(
        r"^(linarith|nlinarith|omega|ring|ring_nf|field_simp"
        r"|positivity|norm_num|rfl|exact\?|aesop|grind|decide|bv_decide"
        r"|sum_congr_ring|finset_nonneg|finset_mono|wellformed_tac|channel_fields"
        r"|alt_proof|elegance\?|bfs_elegance\?)\b"
    ),
    re.compile(
        r"^(constructor|refine|use|exists|intro|intros|induction"
        r"|cases|rcases|obtain|fin_cases)\b"
    ),
]


def load_shapes(_route_table_path: Path) -> list[re.Pattern]:
    """Kept for CLI compatibility; v1 uses RENDERABLE_PATTERNS."""
    return RENDERABLE_PATTERNS


def detect_semicolon_lines(proof_text: str) -> list[dict]:
    """Detect lines chaining multiple tactics with `;` (excluding `<;>` combinators and strings)."""
    hits: list[dict] = []
    for idx, raw_ln in enumerate((proof_text or "").splitlines(), start=1):
        stripped = raw_ln.strip()
        if not stripped or stripped.startswith("--"):
            continue
        # Mask `<;>` so only sequential `;` chains are flagged
        masked = stripped.replace("<;>", "   ")
        if ";" in masked:
            hits.append(
                {
                    "line": idx,
                    "text": stripped[:100],
                    "pattern": "SEMICOLON_LINE_COMPRESSION",
                }
            )
    return hits


def score_block(
    proof_text: str, patterns: list[re.Pattern] | None = None
) -> dict:
    patterns = patterns if patterns is not None else RENDERABLE_PATTERNS
    steps = [
        ln.strip()
        for ln in (proof_text or "").splitlines()
        if ln.strip() and not ln.strip().startswith("--")
    ]
    scored = [
        StepScore(
            step=st[:80],
            renderable=any(p.search(st) for p in patterns) and ";" not in st.replace("<;>", ""),
        )
        for st in steps
    ]
    total = len(scored)
    renderable = sum(1 for s in scored if s.renderable)
    semicolons = detect_semicolon_lines(proof_text or "")
    golf_opps = detect_structural_golf_opportunities(proof_text or "")
    return {
        "steps": total,
        "renderable": renderable,
        "verbose_score": (renderable / total) if total else 1.0,
        "heavy_steps": [s.step for s in scored if not s.renderable][:5],
        "has_semicolons": len(semicolons) > 0,
        "semicolon_lines": semicolons,
        "golf_opportunities": golf_opps,
    }


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            "usage: legibility.py <route-table.json|-> <block-file>",
            file=sys.stderr,
        )
        return 2
    patterns = (
        RENDERABLE_PATTERNS if argv[1] == "-" else load_shapes(Path(argv[1]))
    )
    block = Path(argv[2]).read_text(encoding="utf-8")
    print(json.dumps(score_block(block, patterns), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
