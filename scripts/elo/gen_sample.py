#!/usr/bin/env python3
"""Generate the synthetic match dataset used by the prototype.

True skill ratings are hand-picked; outcomes are sampled from the logistic
Elo model with a small draw probability. Deterministic via fixed seed.

Run:
    python gen_sample.py --out sample_matches.csv --per-pair 8
"""
from __future__ import annotations

import argparse
import csv
import itertools
import random
from pathlib import Path

# (model, reasoning_effort, true_rating)
PLAYERS = [
    ("claude-opus-4.7",   "high", 1800),
    ("claude-opus-4.7",   "",     1700),
    ("claude-sonnet-4.6", "",     1600),
    ("gpt-5.4",           "",     1500),
    ("gpt-5-mini",        "",     1490),
    ("claude-haiku-4.5",  "",     1350),
]
DRAW_PROB = 0.08


def expected(ra: float, rb: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))


def generate(per_pair: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    case = 0
    pairings = list(itertools.combinations(PLAYERS, 2))
    # Interleave pairings so the CSV doesn't process all of one matchup first.
    for round_idx in range(per_pair):
        rng.shuffle(pairings)
        for (ma, ea, ra), (mb, eb, rb) in pairings:
            # Randomize side assignment so neither model is always "a".
            if rng.random() < 0.5:
                (ma, ea, ra), (mb, eb, rb) = (mb, eb, rb), (ma, ea, ra)
            pa = expected(ra, rb)
            roll = rng.random()
            if roll < DRAW_PROB:
                winner = "draw"
            elif roll < DRAW_PROB + (1 - DRAW_PROB) * pa:
                winner = "a"
            else:
                winner = "b"
            case += 1
            rows.append({
                "case_id": f"c{case:04d}",
                "model_a": ma,
                "model_b": mb,
                "winner": winner,
                "reasoning_effort_a": ea,
                "reasoning_effort_b": eb,
            })
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    fields = ["case_id", "model_a", "model_b", "winner",
              "reasoning_effort_a", "reasoning_effort_b"]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("sample_matches.csv"))
    p.add_argument("--per-pair", type=int, default=8)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit", type=int, default=0,
                   help="if >0, truncate to first N matches (for sensitivity runs)")
    args = p.parse_args()
    rows = generate(args.per_pair, args.seed)
    if args.limit:
        rows = rows[: args.limit]
    write_csv(rows, args.out)
    print(f"wrote {len(rows)} matches to {args.out}")


if __name__ == "__main__":
    main()
