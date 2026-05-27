#!/usr/bin/env python3
"""Sanity tests for `glicko2.py`.

The single critical test is **Glickman 2012 §5** — the worked example
that appears verbatim in his PDF and on the Glicko-2 website. Any
correct implementation must reproduce the published expected values to
~4 significant figures.

Run as a script (no test framework required):

    python3 scripts/elo/glicko2_test.py

Exits 0 on success, 1 on any check failure.
"""

from __future__ import annotations

import csv
import math
import sys
import tempfile
from pathlib import Path

# Import the implementation alongside this script.
sys.path.insert(0, str(Path(__file__).parent))
from glicko2 import (  # noqa: E402
    DEFAULT_TAU,
    Game,
    Rating,
    compute_glicko2,
    update_player,
)


def _approx(actual: float, expected: float, tol: float, label: str) -> bool:
    if math.isnan(actual):
        print(f"FAIL {label}: got NaN")
        return False
    if abs(actual - expected) > tol:
        print(f"FAIL {label}: expected {expected:.4f}, got {actual:.4f} "
              f"(|Δ|={abs(actual - expected):.4f} > tol {tol})")
        return False
    print(f"PASS {label}: {actual:.4f} (expected {expected:.4f})")
    return True


def test_glickman_worked_example() -> bool:
    """Glickman 2012 §5: player r=1500, RD=200, σ=0.06, τ=0.5; 3 games.

    Expected output values (from the paper):
        new rating r' ≈ 1464.06
        new RD φ'    ≈ 151.52
        new vol σ'   ≈ 0.05999
    """
    player = Rating(rating=1500, rd=200, vol=0.06)
    games = [
        Game(opponent=Rating(rating=1400, rd=30,  vol=0.06), score=1.0),
        Game(opponent=Rating(rating=1550, rd=100, vol=0.06), score=0.0),
        Game(opponent=Rating(rating=1700, rd=300, vol=0.06), score=0.0),
    ]
    updated = update_player(player, games, tau=DEFAULT_TAU)

    ok = True
    ok &= _approx(updated.rating, 1464.06, 0.05, "Glickman §5 rating")
    ok &= _approx(updated.rd,      151.52, 0.05, "Glickman §5 RD")
    ok &= _approx(updated.vol,     0.05999, 0.0001, "Glickman §5 vol")
    return ok


def test_inactive_player_only_grows_rd() -> bool:
    """Per Glicko-2 §6: a rated player who plays no games keeps the same
    rating but their RD grows toward 350.
    """
    r0 = Rating(rating=1700, rd=80, vol=0.06)
    r1 = update_player(r0, [], tau=DEFAULT_TAU)
    ok = True
    ok &= _approx(r1.rating, 1700.0, 1e-9, "inactive rating unchanged")
    if r1.rd <= r0.rd:
        print(f"FAIL inactive RD must grow: {r0.rd:.2f} → {r1.rd:.2f}")
        ok = False
    else:
        print(f"PASS inactive RD grew: {r0.rd:.2f} → {r1.rd:.2f}")
    return ok


def test_symmetric_draw_no_movement() -> bool:
    """Two equally-rated, equally-confident players draw → no rating change."""
    a = Rating(rating=1500, rd=50, vol=0.06)
    b = Rating(rating=1500, rd=50, vol=0.06)
    a2 = update_player(a, [Game(opponent=b, score=0.5)], tau=DEFAULT_TAU)
    b2 = update_player(b, [Game(opponent=a, score=0.5)], tau=DEFAULT_TAU)
    ok = True
    ok &= _approx(a2.rating, 1500.0, 0.001, "symmetric draw: A rating unchanged")
    ok &= _approx(b2.rating, 1500.0, 0.001, "symmetric draw: B rating unchanged")
    return ok


def test_winner_gains_loser_loses() -> bool:
    """Sanity: a higher-rated player beating a lower-rated one shifts ratings
    in the expected direction (winner up, loser down)."""
    a = Rating(rating=1500, rd=200, vol=0.06)
    b = Rating(rating=1500, rd=200, vol=0.06)
    a2 = update_player(a, [Game(opponent=b, score=1.0)], tau=DEFAULT_TAU)
    b2 = update_player(b, [Game(opponent=a, score=0.0)], tau=DEFAULT_TAU)
    ok = True
    if not (a2.rating > a.rating):
        print(f"FAIL winner did not gain rating: {a.rating} → {a2.rating}")
        ok = False
    else:
        print(f"PASS winner gained: {a.rating} → {a2.rating:.2f}")
    if not (b2.rating < b.rating):
        print(f"FAIL loser did not lose rating: {b.rating} → {b2.rating}")
        ok = False
    else:
        print(f"PASS loser lost:    {b.rating} → {b2.rating:.2f}")
    # Symmetric magnitudes (both used same RD, same opponent rating).
    delta_a = a2.rating - 1500
    delta_b = 1500 - b2.rating
    ok &= _approx(delta_a, delta_b, 0.01, "symmetric Δ magnitudes")
    return ok


def test_cli_smoke_against_csv() -> bool:
    """End-to-end: write 4 matches to CSV, run compute_glicko2, verify
    output shape + ordering."""
    matches = [
        {"case_id": "c1", "model_a": "alpha", "model_b": "beta",
         "winner": "a", "reasoning_effort_a": "", "reasoning_effort_b": ""},
        {"case_id": "c2", "model_a": "alpha", "model_b": "beta",
         "winner": "a", "reasoning_effort_a": "", "reasoning_effort_b": ""},
        {"case_id": "c3", "model_a": "alpha", "model_b": "beta",
         "winner": "a", "reasoning_effort_a": "", "reasoning_effort_b": ""},
        {"case_id": "c4", "model_a": "alpha", "model_b": "beta",
         "winner": "a", "reasoning_effort_a": "", "reasoning_effort_b": ""},
    ]
    states, counts = compute_glicko2(matches, period_size=100)
    ok = True
    if "alpha" not in states or "beta" not in states:
        print(f"FAIL missing players: {sorted(states)}")
        return False
    if not (states["alpha"].rating.rating > states["beta"].rating.rating):
        print(f"FAIL ordering: alpha={states['alpha'].rating.rating:.2f} "
              f"beta={states['beta'].rating.rating:.2f}")
        ok = False
    else:
        print(f"PASS ordering alpha > beta: "
              f"{states['alpha'].rating.rating:.2f} > "
              f"{states['beta'].rating.rating:.2f}")
    if counts["alpha"] != 4 or counts["beta"] != 4:
        print(f"FAIL game counts: alpha={counts['alpha']} beta={counts['beta']}")
        ok = False
    else:
        print(f"PASS game counts both = 4")
    return ok


def main() -> int:
    print("=" * 60)
    print("Glicko-2 sanity tests")
    print("=" * 60)
    results = [
        test_glickman_worked_example(),
        test_inactive_player_only_grows_rd(),
        test_symmetric_draw_no_movement(),
        test_winner_gains_loser_loses(),
        test_cli_smoke_against_csv(),
    ]
    passed = sum(results)
    total = len(results)
    print("=" * 60)
    print(f"{passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
