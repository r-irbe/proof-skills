"""Unit tests for tools/altproof/apply_and_verify.py (Track 1).

Strict 7-bit ASCII only (INV-001).
"""

import pytest
from altproof.apply_and_verify import apply_and_verify_tactic


def test_apply_and_verify_tactic_matched():
    src = "theorem foo (x : Nat) : x + 0 = x := by linarith"
    res = apply_and_verify_tactic(src, target_pattern="linarith")
    assert res.success is True
    assert "omega" in res.transformed_text or "linarith" in res.transformed_text
    assert res.tactic_recommendation is not None
    assert len(res.verification_notes) >= 2


def test_apply_and_verify_tactic_unmatched():
    src = "theorem bar (x : Nat) : x = x := by rfl"
    res = apply_and_verify_tactic(src, target_pattern="non_existent_pattern")
    assert res.success is False
    assert res.transformed_text == src
    assert any("not found" in n for n in res.verification_notes)
