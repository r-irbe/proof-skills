"""Candidate evaluator v1 for AltProof algorithm-class substitution (A3).

Evaluates algorithm candidates against two-axis cost metrics (elegance vs kernel cost),
calculates net improvement delta, and produces ranked suggestions for tactical replacement.
Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import sys as _sys; from pathlib import Path as _Path
if str(_Path(__file__).resolve().parent) not in _sys.path:
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
from algorithm_class_detector import (
    AlgorithmCandidate,
    detect_algorithm_opportunities,
)
from cost_ranker import TwoAxisScore, Weights, cost


@dataclass
class EvaluatedCandidate:
    """An algorithm candidate scored along the two-axis cost model."""

    candidate: AlgorithmCandidate
    before_score: TwoAxisScore
    after_score: TwoAxisScore
    net_improvement: float
    recommended: bool = True
    notes: list[str] = field(default_factory=list)


def evaluate_candidate(
    cand: AlgorithmCandidate,
    baseline_lines: float = 20.0,
    baseline_kernel_seconds: float = 1.5,
    weights: Weights | None = None,
) -> EvaluatedCandidate:
    """Evaluate a single candidate against the two-axis cost model."""
    w = weights or Weights()

    # Model expected line and kernel delta based on speedup and legibility
    speedup = max(cand.estimated_kernel_speedup, 1.0)
    after_kernel_seconds = baseline_kernel_seconds / speedup

    # Line count delta: algorithmic substitution might add or save lines
    after_lines = baseline_lines * (0.8 if cand.pattern == "list-pipeline-overhead" else 1.1)

    shared_lemmas = 1 if cand.pattern in ("exponential-enumeration", "nested-wf-recursion") else 0

    before_c = cost(lines=baseline_lines, kernel_cost=baseline_kernel_seconds, w=w)
    after_c = cost(
        lines=after_lines,
        shared_lemmas=shared_lemmas,
        upstream=False,
        kernel_cost=after_kernel_seconds,
        w=w,
    )

    net_delta = before_c - after_c

    before_score = TwoAxisScore(
        elegance_cost=baseline_lines * w.per_line,
        kernel_cost=baseline_kernel_seconds,
        legibility="high",
    )
    after_score = TwoAxisScore(
        elegance_cost=after_lines * w.per_line - shared_lemmas * w.per_shared_lemma,
        kernel_cost=after_kernel_seconds,
        legibility=cand.legibility_tradeoff,
    )

    notes = [
        f"Pattern: {cand.pattern}",
        f"Speedup: {speedup:.1f}x",
        f"Replacement: {cand.suggested_replacement}",
    ]

    return EvaluatedCandidate(
        candidate=cand,
        before_score=before_score,
        after_score=after_score,
        net_improvement=net_delta,
        recommended=net_delta > 0.0,
        notes=notes,
    )


def rank_algorithm_substitutions(
    source_text: str,
    theorem: str = "",
    baseline_lines: float = 20.0,
    baseline_kernel_seconds: float = 1.5,
    weights: Weights | None = None,
) -> list[EvaluatedCandidate]:
    """Detect and rank all algorithm substitution opportunities in source text."""
    raw_candidates = detect_algorithm_opportunities(source_text, theorem=theorem)
    evaluated = [
        evaluate_candidate(
            c,
            baseline_lines=baseline_lines,
            baseline_kernel_seconds=baseline_kernel_seconds,
            weights=weights,
        )
        for c in raw_candidates
    ]
    # Rank descending by net improvement
    return sorted(evaluated, key=lambda ec: ec.net_improvement, reverse=True)
