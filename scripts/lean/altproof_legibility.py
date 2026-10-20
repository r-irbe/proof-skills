"""Legibility-cost v1 (S7): the verbose-ability proxy.

The design note's second elegance axis: a proof step that renders as
ONE discourse move (Fix/Since/We-conclude, per verbose-lean4) is cheap
for a human reader; a multi-line calc dance is expensive. v1 scores a
block by matching each tactic line against the route table's match
shapes - a matched step is a named lemma call (one sentence); an
unmatched step is scored heavy. verbose_score = renderable/total.

This is a PROXY, not the full distance-to-verbose-rendering metric
(the real one needs the discourse-move route per step; v1 uses
route-table membership as the renderability test).
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StepScore:
    step: str
    renderable: bool


# v1 (revised): the route table's `match` fields turned out to be PROSE
# route semantics for the ranker, not syntactic renderability
# signatures - so renderability is tested structurally instead. A step
# renders as one discourse move (per the verbose-lean4 discipline) when
# it is a single named-lemma application or one-token closer; `;`
# sequences and calc chains are heavy.
RENDERABLE_PATTERNS = [
    re.compile(r"^exact\s+\S"),
    re.compile(r"^apply\s+\S"),
    re.compile(r"^have\s+\w+\s*:?=?\s*\S+"),
    re.compile(r"^(unfold|simp|simp_rw|rw|erw)\b"),
    re.compile(r"^(linarith|nlinarith|omega|ring|ring_nf|field_simp"
               r"|positivity|norm_num|rfl|exact\?|aesop|grind|decide"
               r"|sum_congr_ring|finset_nonneg|finset_mono|wellformed_tac|channel_fields"
               r"|alt_proof|elegance\?)\b"),
    re.compile(r"^(constructor|refine|use|exists|intro|intros|induction"
               r"|cases|rcases|obtain|fin_cases)\b"),
]


def load_shapes(_route_table_path: Path) -> list[re.Pattern]:
    """Kept for CLI compatibility; v1 uses RENDERABLE_PATTERNS (see
    module docstring for why the route table's prose shapes are not
    renderability tests)."""
    return RENDERABLE_PATTERNS


def score_block(proof_text: str, patterns: list[re.Pattern]) -> dict:
    steps = [
        ln.strip()
        for ln in (proof_text or "").splitlines()
        if ln.strip() and not ln.strip().startswith("--")
    ]
    scored = [
        StepScore(
            step=st[:80],
            renderable=any(p.search(st) for p in patterns),
        )
        for st in steps
    ]
    total = len(scored)
    renderable = sum(1 for s in scored if s.renderable)
    return {
        "steps": total,
        "renderable": renderable,
        "verbose_score": (renderable / total) if total else 1.0,
        "heavy_steps": [s.step for s in scored if not s.renderable][:5],
    }


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: legibility.py <route-table.json|-> > <block-file>",
              file=sys.stderr)
        return 2
    patterns = (RENDERABLE_PATTERNS if argv[1] == "-"
                else load_shapes(Path(argv[1])))
    block = Path(argv[2]).read_text(encoding="utf-8")
    print(json.dumps(score_block(block, patterns), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
