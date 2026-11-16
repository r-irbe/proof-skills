"""Unit tests for tools/altproof/apply_and_verify.py (Track 1).

Scoped Unicode policy (INV-001; typographic-free by default).
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


def test_autoslim_cli_and_kernel_verify_wiring(monkeypatch, tmp_path):
    import altproof.apply_and_verify as aav
    import altproof.autoslim as autoslim_mod
    from altproof import cli as cli_mod

    sample = tmp_path / "Sample.lean"
    sample.write_text("theorem demo (n : Nat) : n + 0 = n := by\n  have h := n\n  omega\n", encoding="utf-8")

    fake_report = {
        "schemaVersion": 1,
        "filePath": str(sample),
        "backendUsed": "batch",
        "applied": False,
        "dryRun": True,
        "altProofAvailable": False,
        "importInserted": False,
        "candidatesDiscovered": 1,
        "verifiedCount": 1,
        "rejectedCount": 0,
        "netLinesSaved": 2,
        "netBytesSaved": 18,
        "linesBefore": 3,
        "linesAfter": 1,
        "edits": [
            {
                "theoremName": "demo",
                "route": "nat-truncation-omega",
                "newText": "by omega",
                "linesSaved": 2,
                "bytesSaved": 18,
            }
        ],
        "rejected": [],
    }

    monkeypatch.setattr(autoslim_mod, "run_autoslim", lambda *a, **kw: fake_report)
    monkeypatch.setattr(aav, "run_autoslim", lambda *a, **kw: fake_report)

    md = autoslim_mod.format_autoslim_markdown(fake_report)
    assert "demo" in md and "by omega" in md

    rc = cli_mod.main(["autoslim", str(sample), "--markdown"])
    assert rc == 0

    res = aav.verify_file_with_lean(sample, apply=False)
    assert res.lean_verified is True
    assert res.success is True
    assert res.verification_level == "lean-kernel-batch"

