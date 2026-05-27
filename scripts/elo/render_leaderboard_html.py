#!/usr/bin/env python3
"""Render scripts/elo/example_runs/<archive>/ratings.json → lab/leaderboard.html.

Pure script, no deps beyond stdlib.
"""
from __future__ import annotations
import argparse, json, html, os, sys
from datetime import datetime, timezone

def render(ratings_path: str, out_path: str, sprint_label: str) -> None:
    data = json.load(open(ratings_path))
    players = data["players"]
    ranked = sorted(players.items(), key=lambda kv: kv[1]["rating"], reverse=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = []
    for rank, (pid, p) in enumerate(ranked, 1):
        rows.append(
            f"<tr>"
            f"<td class=rank>{rank}</td>"
            f"<td class=player><code>{html.escape(pid)}</code></td>"
            f"<td class=rating>{p['rating']:.1f}</td>"
            f"<td class=rd>±{p['rd']:.1f}</td>"
            f"<td class=ci>[{p['ci95_low']:.0f}, {p['ci95_high']:.0f}]</td>"
            f"<td class=games>{p['games']}</td>"
            f"</tr>"
        )
    rows_html = "\n".join(rows)
    htmltext = f"""<!doctype html>
<html lang=en>
<head>
<meta charset=utf-8>
<title>proof-skills leaderboard — {html.escape(sprint_label)}</title>
<style>
 body {{ font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        max-width: 920px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
 h1 {{ font-size: 1.5rem; margin-bottom: 0.2rem; }}
 .sub {{ color: #666; font-size: 0.95rem; margin-bottom: 1.4rem; }}
 table {{ border-collapse: collapse; width: 100%; font-size: 0.95rem; }}
 th, td {{ padding: 0.45rem 0.7rem; text-align: left; border-bottom: 1px solid #e3e3e3; }}
 th {{ background: #f7f7f7; font-weight: 600; }}
 td.rank, td.rating, td.rd, td.ci, td.games {{ text-align: right; font-variant-numeric: tabular-nums; }}
 td.rank {{ width: 3em; }}
 tr:hover td {{ background: #fafafa; }}
 code {{ background: #f0f0f0; padding: 1px 5px; border-radius: 3px; font-size: 0.9em; }}
 footer {{ margin-top: 1.5rem; color: #888; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>proof-skills leaderboard</h1>
<div class=sub>Sprint: {html.escape(sprint_label)} &middot; rendered {now}</div>
<table>
<thead>
<tr><th>Rank</th><th>Player</th><th>Rating</th><th>RD</th><th>95% CI</th><th>Games</th></tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
<footer>
Glicko-2 system (τ=0.5, RD_init=350, period_size=100 games). Source: <code>{html.escape(ratings_path)}</code>.<br>
Auto-generated; do not hand-edit. Regenerate with <code>scripts/elo/render_leaderboard_html.py</code>.
</footer>
</body>
</html>
"""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        f.write(htmltext)
    print(f"wrote {out_path} ({len(ranked)} players)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratings", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sprint", default="(unlabeled)")
    args = ap.parse_args()
    render(args.ratings, args.out, args.sprint)

if __name__ == "__main__":
    main()
