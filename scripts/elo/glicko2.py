#!/usr/bin/env python3
"""Glicko-2 rating implementation per Glickman (2012).

Reference:
    Mark E. Glickman, "Example of the Glicko-2 system",
    Boston University, 2012-11-30.
    http://www.glicko.net/glicko/glicko2.pdf

This module ships the math for `lab/design/02-elo-system.md §3` (the
"Glicko-2" recommendation that replaces the vanilla ELO of `elo.py`).
It is additive: `elo.py` stays as the simple online-update
"dashboard view" of design §3.2 ("Vanilla ELO fallback for the
dashboard"); this module is the authoritative ranking system.

Design constants (default):
    initial rating r₀  = 1500
    initial RD φ₀      = 350
    initial vol σ₀     = 0.06
    system constant τ  = 0.5      (per design §3 table — LMSYS uses ~0.6)
    convergence ε      = 1e-6

Verified against Glickman's worked example (§5):
    player r=1500, RD=200, σ=0.06, τ=0.5 plays 3 games:
      vs r=1400, RD=30,  result 1.0
      vs r=1550, RD=100, result 0.0
      vs r=1700, RD=300, result 0.0
    → r_new ≈ 1464.06, RD_new ≈ 151.52, σ_new ≈ 0.05999...

CLI is CSV-compatible with the existing `elo.py`:

    python3 glicko2.py --matches sample_matches.csv --out out/

CSV schema (same as elo.py):
    case_id, model_a, model_b, winner, reasoning_effort_a, reasoning_effort_b
    winner ∈ {a, b, draw}
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GLICKO_SCALE = 173.7178       # convert between display ELO and internal μ
DEFAULT_R0 = 1500.0
DEFAULT_RD0 = 350.0
DEFAULT_VOL0 = 0.06
DEFAULT_TAU = 0.5
EPSILON = 1e-6


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class Rating:
    """Glicko-2 rating in *display* units (1500-centered)."""
    rating: float = DEFAULT_R0
    rd: float = DEFAULT_RD0
    vol: float = DEFAULT_VOL0

    @property
    def mu(self) -> float:
        return (self.rating - DEFAULT_R0) / GLICKO_SCALE

    @property
    def phi(self) -> float:
        return self.rd / GLICKO_SCALE


@dataclass
class Game:
    """One scored outcome from this player's perspective."""
    opponent: Rating
    score: float  # 1.0 win, 0.0 loss, 0.5 draw


@dataclass
class PlayerState:
    rating: Rating = field(default_factory=Rating)
    games: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def player_id(model: str, effort: str | None) -> str:
    """Same convention as elo.py: `(model, effort)` is one entrant."""
    e = (effort or "").strip()
    if e and e.lower() not in ("none", "n/a", "-"):
        return f"{model}@{e}"
    return model


def _score(winner: str) -> tuple[float, float]:
    w = winner.strip().lower()
    if w == "a":
        return 1.0, 0.0
    if w == "b":
        return 0.0, 1.0
    if w == "draw":
        return 0.5, 0.5
    raise ValueError(f"invalid winner: {winner!r} (expected a|b|draw)")


# ---------------------------------------------------------------------------
# Glicko-2 core (Glickman 2012, §5 numbered steps)
# ---------------------------------------------------------------------------

def _g(phi: float) -> float:
    """Step 3, g(φ) = 1 / sqrt(1 + 3φ²/π²)."""
    return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / (math.pi * math.pi))


def _E(mu: float, mu_j: float, phi_j: float) -> float:
    """Step 3, E(μ, μ_j, φ_j) = 1 / (1 + exp(−g(φ_j)·(μ − μ_j)))."""
    return 1.0 / (1.0 + math.exp(-_g(phi_j) * (mu - mu_j)))


def _new_volatility(phi: float, vol: float, v: float, delta: float, tau: float) -> float:
    """Step 5: iterative volatility update via Illinois algorithm (regula falsi)."""
    a = math.log(vol * vol)
    delta_sq = delta * delta
    phi_sq = phi * phi

    def f(x: float) -> float:
        ex = math.exp(x)
        num = ex * (delta_sq - phi_sq - v - ex)
        den = 2.0 * (phi_sq + v + ex) ** 2
        return num / den - (x - a) / (tau * tau)

    # Step 5.2: initial bracketing.
    A = a
    if delta_sq > phi_sq + v:
        B = math.log(delta_sq - phi_sq - v)
    else:
        k = 1
        while f(a - k * tau) < 0:
            k += 1
            if k > 100:
                raise RuntimeError("volatility bracketing failed (k>100)")
        B = a - k * tau

    fA = f(A)
    fB = f(B)

    # Step 5.4: Illinois iteration.
    while abs(B - A) > EPSILON:
        C = A + (A - B) * fA / (fB - fA)
        fC = f(C)
        if fC * fB <= 0:
            A, fA = B, fB
        else:
            fA = fA / 2.0
        B, fB = C, fC

    return math.exp(A / 2.0)


def update_player(rating: Rating, games: list[Game], *, tau: float = DEFAULT_TAU) -> Rating:
    """One Glicko-2 rating-period update. Returns a new Rating."""
    # Step 2: convert to internal scale.
    mu = rating.mu
    phi = rating.phi
    vol = rating.vol

    if not games:
        # Step 6 (inactive player): only RD grows.
        new_phi = math.sqrt(phi * phi + vol * vol)
        return Rating(
            rating=rating.rating,
            rd=new_phi * GLICKO_SCALE,
            vol=vol,
        )

    # Step 3 + 4: estimated variance v and improvement Δ.
    v_inv = 0.0
    delta_sum = 0.0
    for g in games:
        mu_j = g.opponent.mu
        phi_j = g.opponent.phi
        gj = _g(phi_j)
        Ej = _E(mu, mu_j, phi_j)
        v_inv += gj * gj * Ej * (1.0 - Ej)
        delta_sum += gj * (g.score - Ej)
    v = 1.0 / v_inv
    delta = v * delta_sum

    # Step 5: new volatility.
    new_vol = _new_volatility(phi, vol, v, delta, tau)

    # Step 6: pre-rating-period RD.
    phi_star = math.sqrt(phi * phi + new_vol * new_vol)

    # Step 7: new RD and rating.
    new_phi = 1.0 / math.sqrt(1.0 / (phi_star * phi_star) + 1.0 / v)
    new_mu = mu + new_phi * new_phi * delta_sum

    # Step 8: back to display scale.
    return Rating(
        rating=new_mu * GLICKO_SCALE + DEFAULT_R0,
        rd=new_phi * GLICKO_SCALE,
        vol=new_vol,
    )


# ---------------------------------------------------------------------------
# Match-history orchestration
# ---------------------------------------------------------------------------

def compute_glicko2(
    matches: list[dict],
    *,
    r0: float = DEFAULT_R0,
    rd0: float = DEFAULT_RD0,
    vol0: float = DEFAULT_VOL0,
    tau: float = DEFAULT_TAU,
    period_size: int = 100,
) -> tuple[dict[str, PlayerState], dict[str, int]]:
    """Group matches into rating periods; update each entrant once per period.

    Glicko-2 is designed for batch updates — the design doc §3 specifies
    "1 week or 100 games per entrant, whichever first." We use the
    100-games batching here since CSV input is order-only.

    `matches`: list of dicts with keys
        model_a, model_b, winner ∈ {a,b,draw},
        reasoning_effort_a (opt), reasoning_effort_b (opt).
    Returns:
        (states_by_pid, game_counts_by_pid).
    """
    states: dict[str, PlayerState] = {}
    games_by_pid: dict[str, list[Game]] = {}
    counts: dict[str, int] = {}

    def _ensure(pid: str) -> PlayerState:
        if pid not in states:
            states[pid] = PlayerState(rating=Rating(rating=r0, rd=rd0, vol=vol0))
            games_by_pid[pid] = []
            counts[pid] = 0
        return states[pid]

    def _flush(pid: str) -> None:
        st = states[pid]
        st.rating = update_player(st.rating, games_by_pid[pid], tau=tau)
        games_by_pid[pid] = []

    for row in matches:
        pid_a = player_id(row["model_a"], row.get("reasoning_effort_a"))
        pid_b = player_id(row["model_b"], row.get("reasoning_effort_b"))
        sa, sb = _score(row["winner"])

        st_a = _ensure(pid_a)
        st_b = _ensure(pid_b)
        # Use the *current* rating snapshot as the opponent — Glickman's
        # rating-period model assumes opponents are static within a period.
        opp_a = replace(st_a.rating)
        opp_b = replace(st_b.rating)
        games_by_pid[pid_a].append(Game(opponent=opp_b, score=sa))
        games_by_pid[pid_b].append(Game(opponent=opp_a, score=sb))
        counts[pid_a] += 1
        counts[pid_b] += 1

        if len(games_by_pid[pid_a]) >= period_size:
            _flush(pid_a)
        if len(games_by_pid[pid_b]) >= period_size:
            _flush(pid_b)

    # Final partial-period flush (covers all entrants with pending games).
    for pid in list(states):
        if games_by_pid[pid]:
            _flush(pid)

    return states, counts


# ---------------------------------------------------------------------------
# CSV I/O + reports
# ---------------------------------------------------------------------------

def read_matches(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_ratings_json(out_dir: Path, states: dict[str, PlayerState], counts: dict[str, int]) -> Path:
    payload = {
        "rating_system": "glicko-2",
        "scale": "display (1500-centered)",
        "players": {
            pid: {
                "rating": round(st.rating.rating, 2),
                "rd": round(st.rating.rd, 2),
                "vol": round(st.rating.vol, 5),
                "games": counts[pid],
                "ci95_low": round(st.rating.rating - 2.0 * st.rating.rd, 2),
                "ci95_high": round(st.rating.rating + 2.0 * st.rating.rd, 2),
            }
            for pid, st in states.items()
        },
    }
    out = out_dir / "ratings.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return out


def write_leaderboard(out_dir: Path, states: dict[str, PlayerState], counts: dict[str, int]) -> Path:
    rows = sorted(
        ((pid, st.rating, counts[pid]) for pid, st in states.items()),
        key=lambda x: -x[1].rating,
    )
    lines = [
        "# Glicko-2 leaderboard",
        "",
        f"System constant τ = {DEFAULT_TAU}; initial RD = {DEFAULT_RD0}; "
        f"period size = 100 games.",
        "",
        "| Rank | Player | Rating | RD | 95% CI | Games |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for i, (pid, r, n) in enumerate(rows, start=1):
        lo = r.rating - 2 * r.rd
        hi = r.rating + 2 * r.rd
        lines.append(
            f"| {i} | `{pid}` | {r.rating:.1f} | {r.rd:.1f} "
            f"| [{lo:.0f}, {hi:.0f}] | {n} |"
        )
    out = out_dir / "leaderboard.md"
    out.write_text("\n".join(lines) + "\n")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--matches", required=True, type=Path,
                   help="CSV of pairwise matches (see module docstring)")
    p.add_argument("--out", required=True, type=Path,
                   help="Output directory (created if missing)")
    p.add_argument("--tau", type=float, default=DEFAULT_TAU,
                   help=f"System constant (default {DEFAULT_TAU})")
    p.add_argument("--period-size", type=int, default=100,
                   help="Games per rating period per entrant (default 100)")
    args = p.parse_args(list(argv) if argv is not None else None)

    if not args.matches.exists():
        print(f"ERROR: --matches {args.matches} does not exist", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)

    matches = read_matches(args.matches)
    if not matches:
        print(f"ERROR: no rows in {args.matches}", file=sys.stderr)
        return 2

    states, counts = compute_glicko2(
        matches, tau=args.tau, period_size=args.period_size
    )

    rj = write_ratings_json(args.out, states, counts)
    lb = write_leaderboard(args.out, states, counts)
    print(f"wrote {rj}")
    print(f"wrote {lb}")
    print()
    print("Top 5:")
    top = sorted(states.items(), key=lambda kv: -kv[1].rating.rating)[:5]
    for pid, st in top:
        r = st.rating
        print(f"  {r.rating:7.1f}  ±{r.rd:5.1f}  ({counts[pid]:>4} games)  {pid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
