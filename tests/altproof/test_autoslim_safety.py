"""Verification receipts must not claim evidence from an unsuccessful CLI run."""
import json
from types import SimpleNamespace

import pytest
from altproof import autoslim
from altproof import apply_and_verify


def test_wrapper_preserves_symlink_paths_for_strict_engine_validation(tmp_path, monkeypatch):
    real = tmp_path / "real.lean"
    real.write_text("theorem demo : True := by trivial\n")
    alias = tmp_path / "alias.lean"
    alias.symlink_to(real)
    directory = tmp_path / "directory"
    directory.mkdir()
    link = tmp_path / "progress"
    link.symlink_to(directory, target_is_directory=True)
    seen = []
    monkeypatch.setattr(autoslim, "resolve_lean_autoslim_bin", lambda: (["node", "demo.js"], real))
    def run(cmd, **kwargs):
        seen[:] = cmd
        return SimpleNamespace(returncode=0, stdout="{}", stderr="")
    monkeypatch.setattr(autoslim.subprocess, "run", run)
    autoslim.run_autoslim(alias, checkpoint_dir=link)
    assert str(alias) in seen
    assert seen[seen.index("--checkpoint-dir") + 1] == str(link)


def test_resume_controls_and_incomplete_single_receipt(tmp_path, monkeypatch, capsys):
    target = tmp_path / "Demo.lean"
    target.write_text("theorem demo : True := by trivial\n")
    payload = {"schemaVersion": 1, "filePath": str(target), "completed": False,
               "stopReason": "attempt-budget", "verifiedCount": 0, "applied": False,
               "checkpointPath": str(tmp_path / "progress.jsonl")}
    monkeypatch.setattr(autoslim, "resolve_lean_autoslim_bin", lambda: (["node", "demo.js"], target))
    seen = []
    def run(cmd, **kwargs):
        seen[:] = cmd
        return SimpleNamespace(returncode=1, stdout=json.dumps(payload), stderr="")
    monkeypatch.setattr(autoslim.subprocess, "run", run)
    assert autoslim.run_autoslim(target, checkpoint_dir=tmp_path, resume=False,
                                group_size=3, max_verification_attempts=0) == payload
    for flag, value in [("--checkpoint-dir", str(tmp_path)), ("--group-size", "3"), ("--max-attempts", "0")]:
        assert seen[seen.index(flag) + 1] == value
    assert "--fresh" in seen
    assert autoslim.main([str(target), "--checkpoint-dir", str(tmp_path), "--fresh", "--group-size", "3", "--max-attempts", "0"]) == 1
    assert json.loads(capsys.readouterr().out) == payload


def test_nonzero_cli_exit_is_an_error_even_with_valid_json(tmp_path, monkeypatch):
    target = tmp_path / "Demo.lean"
    target.write_text("theorem demo : True := by trivial\n")
    monkeypatch.setattr(autoslim, "resolve_lean_autoslim_bin", lambda: (["node", "demo.js"], target))
    monkeypatch.setattr(autoslim.subprocess, "run", lambda *a, **kw: SimpleNamespace(
        returncode=1, stdout=json.dumps({"verifiedCount": 2}), stderr="verification failed"))
    with pytest.raises(RuntimeError, match="verification failed"):
        autoslim.run_autoslim(target)


def test_zero_candidate_receipt_does_not_claim_kernel_verification(tmp_path, monkeypatch):
    target = tmp_path / "Demo.lean"
    target.write_text("theorem demo : True := by trivial\n")
    monkeypatch.setattr(apply_and_verify, "run_autoslim", lambda *a, **kw: {
        "backendUsed": "none", "verifiedCount": 0, "candidatesDiscovered": 0, "edits": []})
    receipt = apply_and_verify.verify_file_with_lean(target)
    assert receipt.lean_verified is False
    assert receipt.verification_level == "not-performed"
    assert receipt.success is False


def test_batch_wrapper_forwards_all_targets(tmp_path, monkeypatch):
    targets = [tmp_path / "One.lean", tmp_path / "Two.lean"]
    for target in targets:
        target.write_text("theorem demo : True := by trivial\n")
    monkeypatch.setattr(autoslim, "resolve_lean_autoslim_bin", lambda: (["node", "demo.js"], targets[0]))
    seen = []
    def run(cmd, **kwargs):
        seen.extend(cmd)
        return SimpleNamespace(returncode=0, stdout=json.dumps({"kind": "batch", "reports": []}), stderr="")
    monkeypatch.setattr(autoslim.subprocess, "run", run)
    result = autoslim.run_autoslim(targets)
    assert result["kind"] == "batch"
    assert all(str(target) in seen for target in targets)


def test_host_tool_wins_over_stale_nested_tool_copy(tmp_path, monkeypatch):
    skills = tmp_path / "docs" / "skills"
    nested = skills / "tools" / "lean-lsp-mcp" / "bin" / "lean-autoslim.js"
    maintained = tmp_path / "packages" / "lean-analysis" / "bin" / "lean-autoslim.js"
    for candidate in (nested, maintained):
        candidate.parent.mkdir(parents=True)
        candidate.write_text("// fixture CLI\n")
    monkeypatch.delenv("LEAN_AUTOSLIM_BIN", raising=False)
    _, selected = autoslim.resolve_lean_autoslim_bin(skills_root=skills)
    assert selected == maintained


def test_partial_batch_preserves_receipt_and_cli_failure(tmp_path, monkeypatch, capsys):
    present = tmp_path / "Present.lean"
    missing = tmp_path / "Missing.lean"
    present.write_text("theorem demo : True := by trivial\n")
    payload = {"kind": "batch", "completed": False, "reports": [{"filePath": str(present)}],
               "failures": [{"filePath": str(missing), "error": "not found"}]}
    monkeypatch.setattr(autoslim, "resolve_lean_autoslim_bin", lambda: (["node", "demo.js"], present))
    monkeypatch.setattr(autoslim.subprocess, "run", lambda *a, **kw: SimpleNamespace(
        returncode=1, stdout=json.dumps(payload), stderr=""))
    assert autoslim.run_autoslim([present, missing]) == payload
    assert autoslim.main([str(present), str(missing)]) == 1
    assert json.loads(capsys.readouterr().out) == payload
