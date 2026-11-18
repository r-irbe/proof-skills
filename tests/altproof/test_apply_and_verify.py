"""Unit tests for tools/altproof/apply_and_verify.py (Track 1).

Scoped Unicode policy (INV-001; typographic-free by default).
"""

import pytest
from altproof.apply_and_verify import apply_and_verify_tactic


def test_apply_and_verify_tactic_identical_recommendation_is_skipped():
    src = "theorem foo (x : Nat) : x + 0 = x := by linarith"
    res = apply_and_verify_tactic(src, target_pattern="linarith")
    assert res.success is False
    assert res.changed is False
    assert res.transformed_text == src
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
    assert res.success is False
    assert res.verification_level == "lean-kernel-batch"


def test_tree_shake_cli_and_trace_symbols_json_keys(monkeypatch, tmp_path):
    import json
    import altproof.tree_shake as ts_mod
    from altproof import cli as cli_mod
    from altproof.trace_symbols import TraceIndex
    from altproof.tactic_dispatcher import recommend_tactics

    lib_dir = tmp_path / ".lake" / "build" / "lib" / "lean" / "DemoPkg"
    lib_dir.mkdir(parents=True)
    ilean_payload = {
        "version": 5,
        "module": "DemoPkg.Sample",
        "decls": {"DemoPkg.Sample.foo": [1, 0, 1, 20]},
        "references": {
            json.dumps({"c": {"m": "DemoPkg.Sample", "n": "DemoPkg.Sample.bar"}}): {
                "definition": [2, 0, 2, 20],
                "usages": [[1, 10, 1, 13, "DemoPkg.Sample.foo"]],
            }
        },
    }
    (lib_dir / "Sample.ilean").write_text(json.dumps(ilean_payload), encoding="utf-8")
    idx = TraceIndex(tmp_path)
    assert "DemoPkg.Sample.bar" in idx.all_defined_symbols
    assert "DemoPkg.Sample.DemoPkg.Sample.bar" not in idx.all_defined_symbols

    fake_ts = {
        "schemaVersion": 1,
        "entryModules": ["DemoPkg.Sample"],
        "granularity": "declaration",
        "dryRun": True,
        "anonymized": True,
        "totalCorpusModules": 10,
        "fileImportClosureModules": 4,
        "keptModulesCount": 2,
        "reachableDeclarationsCount": 7,
        "prunedDeclarationsCount": 15,
        "totalLinesBefore": 500,
        "totalLinesAfter": 120,
        "lineReductionPct": 76.0,
        "byteReductionPct": 74.5,
        "anonymityLeakHits": [],
    }
    monkeypatch.setattr(ts_mod, "run_tree_shake", lambda *a, **kw: fake_ts)
    assert cli_mod.main(["tree-shake", "DemoPkg.Sample", "--anonymize", "--markdown"]) == 0

    recs = recommend_tactics("|- Finset.sum Finset.univ (Matrix.vecMul d M) = Finset.sum Finset.univ d")
    assert any(r.tactic == "markov_row_sum" for r in recs)


