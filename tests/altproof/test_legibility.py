"""Golden tests for the legibility-cost proxy (S7 v1)."""

import importlib.util
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"
_mod_spec = importlib.util.spec_from_file_location(
    "legibility", _TOOLS / "legibility.py"
)
assert _mod_spec is not None and _mod_spec.loader is not None
legibility = importlib.util.module_from_spec(_mod_spec)
sys.modules["legibility"] = legibility
_mod_spec.loader.exec_module(legibility)

score_block = legibility.score_block
PATTERNS = legibility.RENDERABLE_PATTERNS


def test_all_named_steps_score_perfect():
    block = "  exact h\n  apply le_trans\n  rw [abs_mul]\n  ring\n  positivity"
    out = score_block(block, PATTERNS)
    assert out["verbose_score"] == 1.0
    assert out["heavy_steps"] == []


def test_calc_and_sequence_steps_are_heavy():
    block = ("  calc a + b = b + a := by ring\n"
             "    _ = c := by omega\n"
             "  have h := foo; have h2 := bar; grind")
    out = score_block(block, PATTERNS)
    assert out["verbose_score"] < 1.0
    assert any("calc" in h or ";" in h for h in out["heavy_steps"])


def test_comments_and_blank_lines_ignored():
    block = "-- a comment\n\n  exact h\n"
    out = score_block(block, PATTERNS)
    assert out["steps"] == 1 and out["verbose_score"] == 1.0


def test_altproof_tactics_score_renderable():
    block = "  sum_congr_ring\n  finset_nonneg\n  finset_mono\n  wellformed_tac [concOp]\n  channel_fields f\n  alt_proof"
    out = score_block(block, PATTERNS)
    assert out["steps"] == 6 and out["verbose_score"] == 1.0
    assert out["heavy_steps"] == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
