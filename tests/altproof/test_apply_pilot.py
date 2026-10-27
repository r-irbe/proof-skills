"""Golden tests for the repeatable pilot pipeline (S4)."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"
_mod_spec = importlib.util.spec_from_file_location(
    "apply_pilot", _TOOLS / "apply_pilot.py"
)
assert _mod_spec is not None and _mod_spec.loader is not None
apply_pilot = importlib.util.module_from_spec(_mod_spec)
sys.modules["apply_pilot"] = apply_pilot
_mod_spec.loader.exec_module(apply_pilot)


def _toy_project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    inner = proj / "EASCI"
    inner.mkdir(parents=True)
    (inner / "X.lean").write_text(
        "theorem foo : True := by\n  have h : 0 <= x + y := by omega\n  trivial\n",
        encoding="utf-8",
    )
    return proj


def _spec(proj: Path, old: str = "  have h : 0 <= x + y := by omega") -> dict:
    return {
        "project": str(proj),
        "module": "EASCI.X",
        "commit": False,
        "edits": [
            {
                "op": "insert_before",
                "file": "EASCI/X.lean",
                "anchor": "theorem foo",
                "content": "abbrev sum_nonneg_toy (x y : Nat) := 0 <= x + y\n",
            },
            {"op": "replace", "file": "EASCI/X.lean",
             "old": old, "new": "  have h := sum_nonneg_toy x y"},
        ],
        "message": "pilot: toy",
    }


def test_green_applies_edits(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, "", ""))
    proj = _toy_project(tmp_path)
    out = apply_pilot.run_pilot(_spec(proj))
    assert out["status"] == "OK"
    text = (proj / "EASCI" / "X.lean").read_text(encoding="utf-8")
    assert "abbrev sum_nonneg_toy" in text and "have h := sum_nonneg_toy x y" in text


def test_red_reverts_all_files(tmp_path, monkeypatch):
    def fake_run(cmd, **k):
        rc = 1 if cmd[:2] == ["lake", "build"] else 0
        return subprocess.CompletedProcess(cmd, rc, "", "error: bad")
    monkeypatch.setattr(subprocess, "run", fake_run)
    proj = _toy_project(tmp_path)
    out = apply_pilot.run_pilot(_spec(proj))
    assert out["status"] == "FAILED"
    assert "error: bad" in out["log_tail"]
    text = (proj / "EASCI" / "X.lean").read_text(encoding="utf-8")
    assert "sum_nonneg_toy" not in text  # fully reverted


def test_missing_anchor_fails_before_any_write(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("build must not run when anchors fail")
    monkeypatch.setattr(subprocess, "run", boom)
    proj = _toy_project(tmp_path)
    spec = _spec(proj, old="this site does not exist")
    with pytest.raises(ValueError, match="replace site not found"):
        apply_pilot.run_pilot(spec)
    text = (proj / "EASCI" / "X.lean").read_text(encoding="utf-8")
    assert "sum_nonneg_toy" not in text  # no partial write


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
