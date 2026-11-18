"""Transformation receipts must describe real changes and verifier evidence."""
from importlib import import_module
from pathlib import Path
import pytest

# Standalone analyzer and proof-skills use different package roots.
ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT / "scripts/lean" if (ROOT / "scripts/lean/altproof").is_dir() else ROOT / "python/src"))


def candidate(pattern):
    detector = import_module("altproof.algorithm_class_detector")
    evaluator = import_module("altproof.candidate_evaluator")
    return evaluator.evaluate_candidate(detector.AlgorithmCandidate(
        theorem="toy", pattern=pattern, evidence="List.range",
        suggested_replacement="structural-fold", estimated_kernel_speedup=3.0))


@pytest.mark.parametrize("pattern", ["unknown-pattern", "list-pipeline-overhead"])
def test_unsupported_or_unmatched_patch_is_not_applied(pattern):
    patcher = import_module("altproof.candidate_patcher")
    source = "theorem toy : True := by trivial"
    transformed, receipt = patcher.apply_candidate_patch(source, candidate(pattern))
    assert transformed == source
    assert receipt is not None
    assert receipt.status == "not-applied"
    assert receipt.lines_saved == 0
    assert receipt.patched_snippet == receipt.original_snippet


def test_list_fold_uses_real_lean_addition_syntax():
    patcher = import_module("altproof.candidate_patcher")
    source = "(List.range n).map (fun x => x * 2) |>.foldl (\u00b7 + \u00b7) 0"
    transformed, receipts = patcher.patch_list_pipeline(source)
    assert transformed == "Finset.sum (Finset.range n) (fun x => x * 2)"
    assert len(receipts) == 1
    assert receipts[0].status == "applied-unverified"
    assert receipts[0].lines_saved == 0


@pytest.mark.parametrize("seed", ["01", "0x10", "0.5", "0suffix"])
def test_fold_zero_must_be_entire_literal(seed):
    patcher = import_module("altproof.candidate_patcher")
    source = f"(List.range n).map (fun x => x * 2) |>.foldl (\u00b7 + \u00b7) {seed}"
    transformed, receipts = patcher.patch_list_pipeline(source)
    assert transformed == source
    assert receipts == []


@pytest.mark.parametrize("report,mode", [
    ({"verifiedCount": 1, "backendUsed": "static"}, "auto"),
    ({"verifiedCount": 1}, "batch"),
    ({"verifiedCount": 1, "backendUsed": "batch", "finalCheckPassed": False}, "batch"),
    ({"verifiedCount": 1, "backendUsed": "lsp", "completed": False}, "lsp"),
])
def test_kernel_receipt_requires_positive_backend_evidence(tmp_path, monkeypatch, report, mode):
    verifier = import_module("altproof.apply_and_verify")
    source = tmp_path / "Toy.lean"
    source.write_text("theorem toy : True := by trivial")
    monkeypatch.setattr(verifier, "run_autoslim", lambda *args, **kwargs: report)
    result = verifier.verify_file_with_lean(source, mode=mode)
    assert result.success is False
    assert result.lean_verified is False


def test_kernel_cli_rejects_unverified_count(tmp_path, monkeypatch, capsys):
    verifier = import_module("altproof.apply_and_verify")
    source = tmp_path / "Toy.lean"
    source.write_text("theorem toy : True := by trivial")
    monkeypatch.setattr(verifier, "run_autoslim", lambda *args, **kwargs: {
        "verifiedCount": 1, "backendUsed": "static"})
    assert verifier.main([str(source), "--kernel-verify"]) == 2
    assert "TRANSFORMED_KERNEL_VERIFIED" not in capsys.readouterr().out


@pytest.mark.parametrize("backend_key", ["backendUsed", "modeUsed"])
@pytest.mark.parametrize("backend", ["batch", "lsp"])
def test_explicit_successful_kernel_backend_is_retained(tmp_path, monkeypatch, backend_key, backend):
    verifier = import_module("altproof.apply_and_verify")
    source = tmp_path / "Toy.lean"
    source.write_text("theorem toy : True := by trivial")
    report = {"verifiedCount": 1, backend_key: backend,
              "completed": True, "finalCheckPassed": True}
    monkeypatch.setattr(verifier, "run_autoslim", lambda *args, **kwargs: report)
    result = verifier.verify_file_with_lean(source)
    assert result.success is True
    assert result.lean_verified is True
    assert result.verification_level == f"lean-kernel-{backend}"


@pytest.mark.parametrize("operator", ["(+)", "(+ + +)"])
def test_invalid_lean_operators_are_not_transformed(operator):
    patcher = import_module("altproof.candidate_patcher")
    source = f"(List.range n).map (fun x => x * 2) |>.foldl {operator} 0"
    transformed, receipts = patcher.patch_list_pipeline(source)
    assert transformed == source
    assert receipts == []
