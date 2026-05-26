#!/usr/bin/env python3
"""Prototype ELO calculator for pairwise model comparisons.

Usage:
    python elo.py --matches sample_matches.csv --out out/

Status: prototype. Single file, stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

DEFAULT_K = 32.0
DEFAULT_R0 = 1500.0


def expected_score(ra: float, rb: float) -> float:
    """P(a beats b) under the logistic Elo model."""
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))


def player_id(model: str, effort: str | None) -> str:
    """Each (model, reasoning_effort) tuple is its own player."""
    effort = (effort or "").strip()
    if effort and effort.lower() not in ("none", "n/a", "-"):
        return f"{model}@{effort}"
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


def compute_elo(
    matches: list[dict],
    k: float = DEFAULT_K,
    r0: float = DEFAULT_R0,
) -> tuple[dict[str, float], dict[str, int]]:
    """Pure function. Process matches in order; return (ratings, game_counts).

    Each match dict must contain: model_a, model_b, winner. Optional:
    reasoning_effort_a, reasoning_effort_b. winner ∈ {a, b, draw}.
    """
    ratings: dict[str, float] = {}
    games: dict[str, int] = {}
    for m in matches:
        a = player_id(m["model_a"], m.get("reasoning_effort_a"))
        b = player_id(m["model_b"], m.get("reasoning_effort_b"))
        ratings.setdefault(a, r0)
        ratings.setdefault(b, r0)
        games[a] = games.get(a, 0) + 1
        games[b] = games.get(b, 0) + 1
        sa, sb = _score(m["winner"])
        ea = expected_score(ratings[a], ratings[b])
        eb = 1.0 - ea
        ratings[a] += k * (sa - ea)
        ratings[b] += k * (sb - eb)
    return ratings, games


def load_matches(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def render_leaderboard_md(
    leaderboard: list[tuple[str, float]],
    games: dict[str, int],
    k: float,
    r0: float,
    n_matches: int,
) -> str:
    lines = [
        "# ELO Leaderboard",
        "",
        f"_K={k:g}, R₀={r0:g}, {len(leaderboard)} players, {n_matches} matches_",
        "",
        "| Rank | Player | Rating | Games |",
        "|-----:|--------|-------:|------:|",
    ]
    for i, (p, r) in enumerate(leaderboard, 1):
        lines.append(f"| {i} | {p} | {r:.1f} | {games[p]} |")
    lines.append("")
    return "\n".join(lines)


def write_outputs(
    ratings: dict[str, float],
    games: dict[str, int],
    out_dir: Path,
    k: float,
    r0: float,
    n_matches: int,
) -> list[tuple[str, float]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    leaderboard = sorted(ratings.items(), key=lambda kv: kv[1], reverse=True)
    payload = {
        "k_factor": k,
        "r0": r0,
        "n_matches": n_matches,
        "players": [
            {"player": p, "rating": round(r, 2), "games": games[p]}
            for p, r in leaderboard
        ],
    }
    (out_dir / "ratings.json").write_text(json.dumps(payload, indent=2) + "\n")
    (out_dir / "leaderboard.md").write_text(
        render_leaderboard_md(leaderboard, games, k, r0, n_matches)
    )
    return leaderboard


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Prototype ELO calculator")
    p.add_argument("--matches", required=True, type=Path, help="input CSV")
    p.add_argument("--out", required=True, type=Path, help="output directory")
    p.add_argument("--k", type=float, default=DEFAULT_K, help="K-factor (default 32)")
    p.add_argument("--r0", type=float, default=DEFAULT_R0, help="initial rating (default 1500)")
    args = p.parse_args(argv)

    matches = load_matches(args.matches)
    ratings, games = compute_elo(matches, k=args.k, r0=args.r0)
    leaderboard = write_outputs(
        ratings, games, args.out, k=args.k, r0=args.r0, n_matches=len(matches)
    )

    print(f"Processed {len(matches)} matches across {len(ratings)} players "
          f"(K={args.k:g}, R₀={args.r0:g}).")
    print("Top 5:")
    for i, (player, rating) in enumerate(leaderboard[:5], 1):
        print(f"  {i}. {player:40s} {rating:7.1f}  ({games[player]} games)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
