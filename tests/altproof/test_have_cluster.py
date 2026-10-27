"""Golden tests for cross-theorem have-clustering (S5 v1)."""

import importlib.util
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2] / "scripts" / "lean" / "altproof"
_spec = importlib.util.spec_from_file_location("have_cluster", _TOOLS / "have_cluster.py")
assert _spec is not None and _spec.loader is not None
have_cluster = importlib.util.module_from_spec(_spec)
sys.modules["have_cluster"] = have_cluster
_spec.loader.exec_module(have_cluster)

cluster_haves = have_cluster.cluster_haves


def test_same_shape_different_names_unify():
    a = "theorem t1 : True := by\n  have h_one : 0 <= x + y + z := by omega\n  trivial\n"
    b = "theorem t2 : True := by\n  have other : 0 <= x + y + z := by omega\n  trivial\n"
    out = cluster_haves({"A.lean": a, "B.lean": b, "C.lean": a})
    assert any("0 <= x + y + z" in k for k in out)
    key = next(k for k in out if "0 <= x + y + z" in k)
    assert out[key]["n_files"] == 3  # A, B, and the A-copy in C


def test_trivial_haves_dropped_and_threshold_respected():
    a = "theorem t : True := by\n  have hp : p := hp\n  trivial\n"
    b = a
    out = cluster_haves({"A.lean": a, "B.lean": b})
    assert out == {}


def test_capture_bounded_to_indentation_block():
    src = (
        "theorem t : True := by\n"
        "  have lost : ARunawayPropName\n"
        "  calc x = y := by rfl\n"
        "theorem u : True := by\n"
        "  have found : QLongerShape := by trivial\n"
        "  trivial\n"
    )
    out = cluster_haves({"A.lean": src, "B.lean": src, "C.lean": src})
    shapes = list(out)
    assert any("QLongerShape" in s for s in shapes)
    assert not any("calc" in s for s in shapes)
    assert not any("ARunawayPropName" in s for s in shapes)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


def test_capture_tail_at_adjacent_have_is_cut():
    from have_cluster import cluster_haves
    src = (
        "theorem t : True := by\n"
        "  have h₁ : x = c₁.hSimplex\n"
        "  have h₂ : y = c₂.hSimplex := by rfl\n"
        "  trivial\n"
    )
    out = cluster_haves({"A.lean": src, "B.lean": src, "C.lean": src})
    for k in out:
        assert "have" not in k
