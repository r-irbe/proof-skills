#!/usr/bin/env python3
"""Combine coding-eval and lean-eval into one pairwise CSV, run elo.py."""
import json, csv, itertools, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
code = json.loads((HERE.parent / "coding" / "scores.json").read_text())
lean = json.loads((HERE.parent / "lean" / "scores.json").read_text())

MODELS = list(code.keys())

rows = []; case = 0

# coding-eval: per problem, more passes wins
for pid, _ in sorted(next(iter(code.values())).items()):
    for a, b in itertools.combinations(MODELS, 2):
        pa = code[a][pid]["pass"]; pb = code[b][pid]["pass"]
        winner = "a" if pa>pb else "b" if pb>pa else "draw"
        case += 1
        rows.append({"case_id": f"code-{case:03d}", "model_a": a, "model_b": b,
                     "winner": winner, "reasoning_effort_a": "", "reasoning_effort_b": ""})

code_case = case
# lean-eval: per problem, ok>not-ok wins
for pid, _ in sorted(next(iter(lean.values())).items()):
    for a, b in itertools.combinations(MODELS, 2):
        pa = 1 if lean[a][pid]["ok"] else 0
        pb = 1 if lean[b][pid]["ok"] else 0
        winner = "a" if pa>pb else "b" if pb>pa else "draw"
        case += 1
        rows.append({"case_id": f"lean-{case-code_case:03d}", "model_a": a, "model_b": b,
                     "winner": winner, "reasoning_effort_a": "", "reasoning_effort_b": ""})

out = HERE / "matches.csv"; out.parent.mkdir(exist_ok=True)
fields = ["case_id","model_a","model_b","winner","reasoning_effort_a","reasoning_effort_b"]
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

a_wins = sum(1 for r in rows if r['winner']=='a')
b_wins = sum(1 for r in rows if r['winner']=='b')
draws = sum(1 for r in rows if r['winner']=='draw')
print(f"Total matches: {len(rows)}  (code: 50, lean: 50)")
print(f"  A-wins={a_wins}  B-wins={b_wins}  draws={draws}")
print(f"  Decisive = {a_wins+b_wins} / {len(rows)}\n")

# Run elo.py
ELO = HERE.parent.parent.parent / "elo.py"
subprocess.run(["python3", str(ELO), "--matches", str(out), "--out", str(out.parent)], check=True)
print()
print((out.parent / "leaderboard.md").read_text())
