"""Unit tests for AltProof tactic dispatcher (A5).

Strict 7-bit ASCII only (INV-001).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2] / "scripts" / "lean"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from altproof.tactic_dispatcher import dispatch_and_score, recommend_tactics


def test_recommend_omega_for_nat():
    goal = "n + 1 <= 2 * n + 3"
    recs = recommend_tactics(goal)
    assert any(r.tactic == "omega" for r in recs)
    top = recs[0]
    assert top.estimated_heartbeats <= 300


def test_recommend_linarith_for_real():
    goal = "x + y <= 1.0 (where x y : Real)"
    recs = recommend_tactics(goal)
    assert any(r.tactic == "linarith" for r in recs)


def test_recommend_aesop_for_inductive():
    goal = "Tree.size t >= 0"
    proof = "induction t with | leaf => constructor | node l r => cases l"
    recs = recommend_tactics(goal, current_proof_text=proof)
    assert any(r.tactic == "aesop" for r in recs)


def test_recommend_decide_for_finite():
    goal = "x in Fin 5"
    recs = recommend_tactics(goal)
    assert any(r.tactic == "decide" for r in recs)


def test_recommend_sum_congr_ring():
    goal = "Finset.sum s (fun i => f i) - Finset.sum s (fun i => g i) = Finset.sum s (fun i => f i - g i)"
    recs = recommend_tactics(goal)
    assert any(r.tactic == "sum_congr_ring" for r in recs)
    assert not any(r.tactic == "omega" for r in recs)


def test_recommend_finset_nonneg():
    goal = "0 <= Finset.sum s (fun i => (u i) ^ 2)"
    recs = recommend_tactics(goal)
    assert any(r.tactic == "finset_nonneg" for r in recs)


def test_recommend_finset_mono():
    goal = "Finset.sum s (fun i => w i * f i) <= Finset.sum s (fun i => w i * g i)"
    recs = recommend_tactics(goal)
    assert any(r.tactic == "finset_mono" for r in recs)
    assert any(r.tactic == "sum_congr_ring" for r in recs)
    # Also detects Finset.sum_le_sum in proof text
    recs_from_proof = recommend_tactics("a <= b", current_proof_text="refine Finset.sum_le_sum fun i _ => ?_")
    assert any(r.tactic == "finset_mono" for r in recs_from_proof)


def test_recommend_wellformed_tac():
    goal = "Opinion.WellFormed ccvOp4"
    proof = "refine <?_, ?_, ?_, ?_, ?_>; intro i; fin_cases i <;> norm_num"
    recs = recommend_tactics(goal, current_proof_text=proof)
    assert any(r.tactic == "wellformed_tac" for r in recs)


def test_recommend_channel_fields():
    goal = "Channel (Fin 3) (Fin 2)"
    recs = recommend_tactics(goal)
    assert any(r.tactic == "channel_fields" for r in recs)


def test_recommend_solve_by_elim():
    goal = "P -> Q"
    proof = "intro h; apply h1; apply h2"
    recs = recommend_tactics(goal, current_proof_text=proof)
    assert any(r.tactic == "solve_by_elim" for r in recs)
    assert not any(r.tactic == "omega" for r in recs)


def test_recommend_empty_inputs():
    assert recommend_tactics("", "") == []
    assert recommend_tactics(None, None) == []


def test_dispatch_and_score_summary():
    out = dispatch_and_score(
        "Finset.sum s (fun i => c i * f i) <= Finset.sum s (fun i => c i * g i)",
        "  refine Finset.sum_le_sum fun i _ => ?_\n  exact mul_le_mul_of_nonneg_left (h i) (hc i)",
    )
    assert out["best_tactic"] == "finset_mono"
    assert out["legibility"]["steps"] == 2
    assert out["legibility"]["verbose_score"] == 1.0
    assert out["baseline_cost_x10"] == 2


def test_multiline_lsp_goal_no_hypothesis_bleed():
    # Hypothesis has Finset.sum <= 1 and 0 <= c, but target conclusion after |- is a sum equality
    goal = (
        "s : Finset Nat\n"
        "f : Nat -> Real\n"
        "h_le : Finset.sum s f <= 1\n"
        "h_nonneg : 0 <= c\n"
        "|- Finset.sum s (fun i => 2 * f i) = Finset.sum s (fun i => f i + f i)"
    )
    recs = recommend_tactics(goal)
    assert recs[0].tactic == "sum_congr_ring"
    assert not any(r.tactic == "finset_mono" for r in recs)
    assert not any(r.tactic == "finset_nonneg" for r in recs)


def test_finset_sum_over_fin_does_not_recommend_decide():
    goal = "Finset.sum univ (fun i : Fin 3 => 2 * f i) = Finset.sum univ (fun i : Fin 3 => f i + f i)"
    recs = recommend_tactics(goal)
    assert recs[0].tactic == "sum_congr_ring"
    assert not any(r.tactic == "decide" for r in recs)


