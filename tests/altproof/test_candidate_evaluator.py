"""Unit tests for AltProof candidate evaluator (A3).

Strict 7-bit ASCII only (INV-001).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2] / "scripts" / "lean"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from altproof.candidate_evaluator import (
    evaluate_candidate,
    rank_algorithm_substitutions,
)
from altproof.algorithm_class_detector import AlgorithmCandidate


def test_evaluate_candidate():
    cand = AlgorithmCandidate(
        theorem="testThm",
        pattern="exponential-enumeration",
        evidence="Equiv.Perm",
        suggested_replacement="dynamic programming",
        estimated_kernel_speedup=25.0,
        legibility_tradeoff="medium",
    )
    evaluated = evaluate_candidate(cand, baseline_lines=30.0, baseline_kernel_seconds=5.0)
    assert evaluated.recommended is True
    assert evaluated.net_improvement > 0.0
    assert evaluated.after_score.kernel_cost < evaluated.before_score.kernel_cost


def test_rank_algorithm_substitutions():
    snippet = """
    def naivePermPermanent (A : Matrix (Fin n) (Fin n) Real) : Real :=
      Finset.univ.sum (fun (p : Equiv.Perm (Fin n)) => 1)

    def sumEvens (n : Nat) : Nat :=
      (List.range n).map (fun x => x * 2) |>.foldl (+ + +) 0
    """
    ranked = rank_algorithm_substitutions(snippet, theorem="multiTest")
    assert len(ranked) >= 2
    # The top candidate should have higher net improvement
    assert ranked[0].net_improvement >= ranked[1].net_improvement
