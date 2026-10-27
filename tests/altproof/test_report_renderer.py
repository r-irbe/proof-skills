"""Tests for the report renderer v1."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"))

from extraction_detector import Candidate
from report_renderer import BlockReport, render_block, render_file, render_report


def _cand(kind="duplicated-subterm", evidence="x * x", occ=4, saving=3):
    return Candidate(
        theorem="t", kind=kind, evidence=evidence, occurrences=occ, estimated_lines_saved=saving
    )


def test_render_block_has_sketch_and_verdict():
    b = BlockReport(
        line_start=10,
        line_end=14,
        proof_text="  calc x * x + x * x = 2 * (x * x) := by omega",
        candidates=[_cand()],
    )
    out = render_block(b)
    assert "Current proof:" in out and "```lean" in out
    assert "An alternative worth knowing:" in out
    assert "x * x" in out and "occurs 4 times" in out
    assert "cost" in out and "->" in out
    # C4 posture: the verdict line marks the current proof correct
    assert "current proof is correct" in out.lower()
    assert "two-axis:" in out
    assert "elegance_cost:" in out and "kernel_cost:" in out and "legibility:" in out


def test_render_block_no_judgment_words():
    b = BlockReport(line_start=1, line_end=2, proof_text="  exact h", candidates=[_cand()])
    out = render_block(b).lower()
    for w in ("bad", "wrong", "should"):
        assert w not in out


def test_have_block_sketch_phrasing():
    b = BlockReport(
        line_start=1,
        line_end=3,
        proof_text="  have h1 : a = a := rfl\n  exact h1",
        candidates=[_cand(kind="have-block", evidence="h1", occ=1, saving=1)],
    )
    out = render_block(b)
    assert "h1" in out and "reusable" in out


def test_render_file_empty():
    assert "No extraction candidates" in render_file("F.lean", [])


def test_render_report_orders_by_candidate_count():
    files = {
        "A.lean": [BlockReport(1, 2, "x", [_cand()])],
        "B.lean": [BlockReport(1, 2, "x", [_cand(), _cand()])],
    }
    out = render_report(files)
    assert out.index("## B.lean") < out.index("## A.lean")
