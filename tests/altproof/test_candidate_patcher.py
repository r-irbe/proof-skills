"""Unit tests for AltProof candidate patcher (A4).

Strict 7-bit ASCII only (INV-001).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2] / "scripts" / "lean"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from altproof.algorithm_class_detector import AlgorithmCandidate
from altproof.candidate_evaluator import evaluate_candidate
from altproof.candidate_patcher import (
    apply_candidate_patch,
    patch_list_pipeline,
)


def test_patch_list_pipeline():
    original = """
    def sumEvens (n : Nat) : Nat :=
      (List.range n).map (fun x => x * 2) |>.foldl (+ + +) 0
    """
    patched, receipts = patch_list_pipeline(original)
    assert len(receipts) == 1
    assert "Finset.sum (Finset.range n) (fun x => x * 2)" in patched
    assert receipts[0].pattern == "list-pipeline-overhead"


def test_apply_candidate_patch():
    cand = AlgorithmCandidate(
        theorem="testThm",
        pattern="list-pipeline-overhead",
        evidence="List.range",
        suggested_replacement="Finset.sum",
        estimated_kernel_speedup=3.5,
    )
    ec = evaluate_candidate(cand)
    original = "(List.range n).map (fun x => x * 2) |>.foldl (+ + +) 0"
    patched, receipt = apply_candidate_patch(original, ec)
    assert receipt is not None
    assert "Finset.sum" in patched


def test_apply_candidate_patch_general():
    cand = AlgorithmCandidate(
        theorem="spectralRadiusBound",
        pattern="exponential-matrix-unfolding",
        evidence="A ^ n",
        suggested_replacement="GelfandFormula",
        estimated_kernel_speedup=12.0,
    )
    ec = evaluate_candidate(cand)
    original = "theorem spectralRadiusBound : True := by trivial"
    patched, receipt = apply_candidate_patch(original, ec)
    assert receipt is not None
    assert receipt.theorem == "spectralRadiusBound"
    assert receipt.pattern == "exponential-matrix-unfolding"
    assert receipt.estimated_speedup == 12.0

