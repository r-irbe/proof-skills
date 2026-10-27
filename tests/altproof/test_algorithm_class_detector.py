"""Unit tests for algorithm-class detector (A7).

Strict 7-bit ASCII only (INV-001).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2] / "scripts" / "lean"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from altproof.algorithm_class_detector import (
    detect_algorithm_opportunities,
)


def test_detect_exponential_enumeration():
    snippet = """
    def naivePermPermanent (A : Matrix (Fin n) (Fin n) Real) : Real :=
      Finset.univ.sum (fun (p : Equiv.Perm (Fin n)) => 1)
    """
    cands = detect_algorithm_opportunities(snippet, theorem="naivePermPermanent")
    assert len(cands) >= 1
    assert any(c.pattern == "exponential-enumeration" for c in cands)
    perm_cand = next(c for c in cands if c.pattern == "exponential-enumeration")
    assert perm_cand.estimated_kernel_speedup >= 10.0
    assert perm_cand.route == "algorithm-class-substitution"


def test_detect_wf_recursion():
    snippet = """
    def ackermann (m n : Nat) : Nat :=
      WellFounded.fix (measure (fun p : Nat * Nat => p.1 + p.2)) ...
    """
    cands = detect_algorithm_opportunities(snippet, theorem="ackermann")
    assert any(c.pattern == "nested-wf-recursion" for c in cands)


def test_detect_list_pipeline():
    snippet = """
    def sumEvens (n : Nat) : Nat :=
      (List.range n).map (fun x => x * 2) |>.foldl (+ + +) 0
    """
    cands = detect_algorithm_opportunities(snippet, theorem="sumEvens")
    assert any(c.pattern == "list-pipeline-overhead" for c in cands)


def test_detect_empty_or_clean():
    clean_snippet = """
    theorem add_comm (a b : Nat) : a + b = b + a := by omega
    """
    cands = detect_algorithm_opportunities(clean_snippet, theorem="add_comm")
    assert len(cands) == 0
