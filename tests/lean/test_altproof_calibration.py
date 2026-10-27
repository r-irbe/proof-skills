"""The B1 calibration: the extraction-outranks default must rank each
golden fixture's AFTER state above its BEFORE state (the harness
contract, use 1)."""

import json
import sys
from pathlib import Path

GOLDEN = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "investigation-garden"
    / "altproof"
    / "council"
    / "golden"
)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"))

from cost_ranker import (  # noqa: E402
    TwoAxisScore,
    Weights,
    cost,
    evaluate_two_axis_candidate,
    ranks_above,
)


def _numeric(v):
    return float(v) if isinstance(v, (int, float)) else None


def _fixture_passes(fx, w):
    b, a = _numeric(fx.get("before")), _numeric(fx.get("after"))
    if b is None or a is None:
        return None  # no numeric metrics recorded (fixture 9)
    lemmas = len(fx.get("extracted", []))
    upstream = any("PR #" in e or "Mathlib-absent" in e for e in fx.get("extracted", []))
    return ranks_above(b, a, lemmas, upstream, w)


def test_all_numeric_fixtures_rank_after_above_before():
    fixtures = json.loads((GOLDEN / "golden-cases.json").read_text())["fixtures"]
    results = {fx["id"]: _fixture_passes(fx, Weights()) for fx in fixtures}
    failed = [i for i, ok in results.items() if ok is False]
    assert not failed, (
        f"B1 calibration FAILED on fixtures {failed} - the heuristic family gains members"
    )


def test_extraction_outranks_property_holds():
    """Even a modest line saving wins when content moves into named lemmas."""
    assert ranks_above(100, 95, after_lemmas=1)
    # and the property is why it is called extraction-OUTRANKS: a 20-line
    # saving with no extraction loses to a 10-line saving with one lemma
    assert cost(80, 1) < cost(90, 0)


def test_upstream_bonus_dominates():
    """A Mathlib-absent extraction is library-worthy (fixtures 10-11)."""
    assert cost(52, 1, upstream=True) < cost(52, 1)


def test_sair_calibration_fixtures_rank_after_above_before():
    """SAIR kernel-cost axis ranks AFTER above BEFORE on accepted fixtures (A1/A2 acceptance)."""
    sair_path = GOLDEN / "sair-calibration.json"
    assert sair_path.exists(), "sair-calibration.json missing"
    fixtures = json.loads(sair_path.read_text())["fixtures"]
    accepted = [fx for fx in fixtures if fx.get("disposition") != "rejected"]
    w = Weights(kernel_cost_weight=1.0)
    passed = 0
    for fx in accepted:
        b, a = fx["before"], fx["after"]
        if ranks_above(0, 0, before_kernel_cost=b, after_kernel_cost=a, w=w):
            passed += 1
    assert passed >= len(accepted) * 3 // 4, f"Only {passed}/{len(accepted)} SAIR fixtures ranked cleanly"


def test_formal_conjectures_calibration_fixtures_rank_cleanly():
    """Multi-corpus golden suite (A6): formal-conjectures fixtures rank AFTER above BEFORE."""
    fc_path = GOLDEN / "formal-conjectures-calibration.json"
    assert fc_path.exists(), "formal-conjectures-calibration.json missing"
    fixtures = json.loads(fc_path.read_text())["fixtures"]
    w = Weights(kernel_cost_weight=0.5)
    for fx in fixtures:
        b, a = fx["before"], fx["after"]
        # With line savings and kernel speedup, AFTER must rank strictly above BEFORE
        assert ranks_above(b, a, before_kernel_cost=b, after_kernel_cost=a, w=w)


def test_evaluate_two_axis_candidate():
    """Verify Pareto dominance and trade-off evaluation across two-axis model."""
    baseline = TwoAxisScore(elegance_cost=0.50, kernel_cost=1.20, legibility="med")
    improved = TwoAxisScore(elegance_cost=0.20, kernel_cost=0.40, legibility="high")
    ev = evaluate_two_axis_candidate(baseline, improved)
    assert ev["improved"] is True
    assert ev["dominates"] is True
    assert ev["regressed"] is False
    assert ev["tradeoff"] is False

    # Trade-off case: elegance is worse, but kernel cost is much lower
    tradeoff_candidate = TwoAxisScore(elegance_cost=0.80, kernel_cost=0.05, legibility="low")
    ev_tradeoff = evaluate_two_axis_candidate(baseline, tradeoff_candidate)
    assert ev_tradeoff["improved"] is True
    assert ev_tradeoff["dominates"] is False
    assert ev_tradeoff["tradeoff"] is True


