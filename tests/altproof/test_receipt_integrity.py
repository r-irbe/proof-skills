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
    assert result.success is False
    assert result.lean_verified is True
    assert result.verification_level == f"lean-kernel-{backend}"


@pytest.mark.parametrize("operator", ["(+)", "(+ + +)"])
def test_invalid_lean_operators_are_not_transformed(operator):
    patcher = import_module("altproof.candidate_patcher")
    source = f"(List.range n).map (fun x => x * 2) |>.foldl {operator} 0"
    transformed, receipts = patcher.patch_list_pipeline(source)
    assert transformed == source
    assert receipts == []


@pytest.mark.parametrize("replacement", ["linarith", ""])
def test_identical_text_is_not_a_patch(replacement):
    patcher = import_module("altproof.candidate_patcher")
    source = "theorem toy : 1 < 2 := by linarith"
    target = "linarith" if replacement else ""
    result = patcher.patch_candidate(source, target, replacement)
    assert result.patched is False
    assert result.transformed_text == source


def test_structural_noop_cli_is_skipped(tmp_path, capsys):
    verifier = import_module("altproof.apply_and_verify")
    source = "theorem toy : 1 < 2 := by linarith"
    result = verifier.apply_and_verify_tactic(source)
    assert result.success is False
    assert result.transformed_text == source
    target = tmp_path / "Toy.lean"
    target.write_text(source)
    assert verifier.main([str(target)]) == 2
    assert "TRANSFORMED_UNVERIFIED" not in capsys.readouterr().out


def test_selected_candidate_only_changes_its_located_declaration():
    detector = import_module("altproof.algorithm_class_detector")
    evaluator = import_module("altproof.candidate_evaluator")
    patcher = import_module("altproof.candidate_patcher")
    fold = "(List.range n).map (fun x => x * 2) |>.foldl (\u00b7 + \u00b7) 0"
    first = f"def first (n : Nat) : Nat := {fold}\n"
    second = f"def second (n : Nat) : Nat := {fold}\n"
    source = first + second
    candidates = detector.detect_algorithm_opportunities(source, theorem="second")
    selected = [c for c in candidates if c.pattern == "list-pipeline-overhead"][-1]
    transformed, receipt = patcher.apply_candidate_patch(source, evaluator.evaluate_candidate(selected))
    assert transformed == first + "def second (n : Nat) : Nat := Finset.sum (Finset.range n) (fun x => x * 2)\n"
    assert receipt.theorem == "second"
    assert receipt.original_snippet == fold


@pytest.mark.parametrize("location", [None, -1, True, 9999])
def test_unlocated_selected_candidate_cannot_edit_unrelated_match(location):
    patcher = import_module("altproof.candidate_patcher")
    source = "def other (n : Nat) := (List.range n).map (fun x => x * 2) |>.foldl (\u00b7 + \u00b7) 0\n"
    selected = candidate("list-pipeline-overhead")
    if location is not None:
        selected.candidate.details["line_offset"] = location
    transformed, receipt = patcher.apply_candidate_patch(source, selected)
    assert transformed == source
    assert receipt.status == "not-applied"


@pytest.mark.parametrize("publish", [False, True])
def test_kernel_cli_distinguishes_verified_proposal_and_publication(tmp_path, monkeypatch, capsys, publish):
    verifier = import_module("altproof.apply_and_verify")
    source = tmp_path / "Toy.lean"
    original = "theorem toy : True := by trivial"
    replacement = "theorem toy : True := by exact True.intro"
    source.write_text(original)
    def run(*args, **kwargs):
        if publish:
            source.write_text(replacement)
        return {"verifiedCount": 1, "backendUsed": "batch", "completed": True,
                "finalCheckPassed": True, "applied": publish}
    monkeypatch.setattr(verifier, "run_autoslim", run)
    argv = [str(source), "--kernel-verify"] + (["--apply"] if publish else [])
    assert verifier.main(argv) == 0
    output = capsys.readouterr().out
    assert ("TRANSFORMED_KERNEL_VERIFIED" in output) is publish
    assert ("PROPOSED_KERNEL_VERIFIED" in output) is not publish
    assert source.read_text() == (replacement if publish else original)


def test_kernel_apply_without_actual_change_is_not_transformed(tmp_path, monkeypatch):
    verifier = import_module("altproof.apply_and_verify")
    source = tmp_path / "Toy.lean"
    source.write_text("theorem toy : True := by trivial")
    monkeypatch.setattr(verifier, "run_autoslim", lambda *args, **kwargs: {
        "verifiedCount": 1, "backendUsed": "batch", "applied": True})
    result = verifier.verify_file_with_lean(source, apply=True)
    assert result.lean_verified is True
    assert result.success is False


def test_changed_structural_proposal_still_reports_success():
    verifier = import_module("altproof.apply_and_verify")
    source = "theorem toy (x : Real) : x = x := by rfl"
    result = verifier.apply_and_verify_tactic(source, target_pattern="rfl")
    assert result.success is True
    assert result.changed is True
    assert result.applied is False
    assert result.transformed_text == "theorem toy (x : Real) : x = x := by linarith"


def test_empty_target_cannot_insert_at_every_character():
    patcher = import_module("altproof.candidate_patcher")
    result = patcher.patch_candidate("by trivial", "", "insertion")
    assert result.patched is False
    assert result.transformed_text == "by trivial"
