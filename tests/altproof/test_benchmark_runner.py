"""Tests for tools/altproof/benchmark_runner.py (Track 1).

Strict 7-bit ASCII only (INV-001).
"""

from pathlib import Path
import tempfile
import pytest

from altproof.benchmark_runner import scan_corpus, render_markdown_report


def test_scan_corpus_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        res = scan_corpus(tmp)
        assert res["files_scanned"] == 0
        assert res["total_candidates"] == 0
        assert res["top_10_targets"] == []


def test_scan_corpus_with_synthetic_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        f1 = tmp / "TestModule.lean"
        f1.write_text(
            """
            theorem testPerm : Equiv.Perm (Fin 3) := sorry
            theorem testPowerset : Finset.powerset (Fin 3) = {} := sorry
            """,
            encoding="utf-8",
        )
        res = scan_corpus(tmp)
        assert res["files_scanned"] == 1
        assert res["files_with_candidates"] == 1
        assert res["total_candidates"] >= 2
        assert len(res["top_10_targets"]) <= 10
        assert "exponential-enumeration" in res["pattern_distribution"]


def test_render_markdown_report():
    sample_data = {
        "files_scanned": 10,
        "files_with_candidates": 3,
        "total_candidates": 5,
        "pattern_distribution": {"exponential-enumeration": 2, "type-specialization-bottleneck": 3},
        "candidates_by_file": {},
        "top_10_targets": [],
    }
    md = render_markdown_report(sample_data)
    assert "# AltProof Corpus-Wide Optimization Benchmark" in md
    assert "Files Scanned**: 10" in md
    assert "exponential-enumeration" in md
