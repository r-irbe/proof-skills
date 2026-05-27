#!/usr/bin/env python3
"""Build pairwise-match CSV from coding-eval scores.
Per problem, A vs B: more passes wins, equal is draw."""
import json, csv, itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
scores = json.loads((HERE / "scores.json").read_text())
MODELS = list(scores.keys())
PROBLEMS = list(next(iter(scores.values())).keys())

rows = []; case = 0
for pid in PROBLEMS:
    for a, b in itertools.combinations(MODELS, 2):
        pa = scores[a][pid]["pass"]
        pb = scores[b][pid]["pass"]
        winner = "a" if pa>pb else "b" if pb>pa else "draw"
        case += 1
        rows.append({"case_id": f"c{case:03d}", "model_a": a, "model_b": b,
                     "winner": winner, "reasoning_effort_a": "", "reasoning_effort_b": ""})

out = HERE / "matches.csv"
fields = ["case_id","model_a","model_b","winner","reasoning_effort_a","reasoning_effort_b"]
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

a_wins = sum(1 for r in rows if r['winner']=='a')
b_wins = sum(1 for r in rows if r['winner']=='b')
draws  = sum(1 for r in rows if r['winner']=='draw')
print(f"wrote {len(rows)} matches: A-wins={a_wins} B-wins={b_wins} draws={draws}")
print("Decisive matches:")
for r in rows:
    if r["winner"] != "draw":
        w = r["model_a"] if r["winner"]=="a" else r["model_b"]
        l = r["model_b"] if r["winner"]=="a" else r["model_a"]
        print(f"  {r['case_id']}: {w}  beat  {l}")
