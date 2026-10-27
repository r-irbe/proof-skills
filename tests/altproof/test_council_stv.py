"""Golden tests for the council STV counter (charter mechanics).

Fixtures cover the four canonical scenarios: first-round majority,
elimination flip via transfer, the deterministic tiebreak, and the
exhausted-ballots NO_QUORUM path.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2] / "scripts" / "lean"
_spec = importlib.util.spec_from_file_location("council_stv", _TOOLS / "council_stv.py")
assert _spec is not None and _spec.loader is not None
council_stv = importlib.util.module_from_spec(_spec)
sys.modules["council_stv"] = council_stv
_spec.loader.exec_module(council_stv)

Ballot = council_stv.Ballot


def test_first_round_majority():
    ballots = [Ballot(f"v{i}", ["A"]) for i in range(4)] + [Ballot("v9", ["B"])]
    out = council_stv.count_stv(["A", "B", "C"], ballots)
    assert out["winner"] == "A"
    assert out["no_quorum"] is False
    assert len(out["rounds"]) == 1


def test_elimination_flip_via_transfer():
    # A:2 B:2 C:3 -> quota 4; C eliminated in round 1? No: C has 3 (fewest is A/B at 2, tie -> A lex).
    # After A eliminated, its 2 ballots rank B second -> B reaches 4 >= quota 4.
    ballots = [
        Ballot("v1", ["A", "B"]),
        Ballot("v2", ["A", "B"]),
        Ballot("v3", ["B"]),
        Ballot("v4", ["B"]),
        Ballot("v5", ["C"]),
        Ballot("v6", ["C"]),
        Ballot("v7", ["C"]),
    ]
    out = council_stv.count_stv(["A", "B", "C"], ballots)
    assert out["winner"] == "B"
    assert out["rounds"][0]["eliminated"] == "A"


def test_tiebreak_is_deterministic():
    # A and B tied at the bottom; the lexicographically smallest id (A) is eliminated.
    ballots = [Ballot("v1", ["C"]), Ballot("v2", ["C"]), Ballot("v3", ["B"]), Ballot("v4", ["A"])]
    out = council_stv.count_stv(["A", "B", "C"], ballots)
    assert out["rounds"][0]["eliminated"] == "A"
    assert out["winner"] == "C"


def test_no_quorum_last_survivor():
    ballots = [Ballot("v1", ["A"]), Ballot("v2", ["B"]), Ballot("v3", ["C"])]
    out = council_stv.count_stv(["A", "B", "C"], ballots)
    assert out["no_quorum"] is True
    assert out["winner"] in {"A", "B", "C"}


def test_abstention_shrinks_quota_only():
    ballots = [Ballot("v1", ["A"]), Ballot("v2", ["A"]), Ballot("v3", []), Ballot("v4", ["B"])]
    out = council_stv.count_stv(["A", "B"], ballots)
    # 3 valid ballots -> quota 2; A has 2 -> wins round 1.
    assert out["quota"] == 2
    assert out["winner"] == "A"


def test_json_roundtrip():
    payload = {
        "options": ["A", "B"],
        "ballots": [{"voter": "v1", "ranking": ["A"]}, {"voter": "v2", "ranking": ["B"]}],
    }
    ballots = council_stv.ballots_from_json(payload)
    out = council_stv.count_stv(payload["options"], ballots)
    assert out["no_quorum"] is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
