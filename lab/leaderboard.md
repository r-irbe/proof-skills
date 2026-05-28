# Leaderboard (rolling)

**Current archive:** `scripts/elo/example_runs/2026-05-27-m-r25-median4/` (R25 item 5 — gpt-5.4 added as 4th judge; median-of-4 ensemble).

| Rank | Player | Rating | RD | 95 % CI | Games |
|---|---|---:|---:|---|---:|
| 1 | `claude-opus-4.7@default-effort` | 1725.0 | 36.3 | [1652, 1798] | 140 |
| 2 | `claude-sonnet-4.6` | 1568.0 | 22.5 | [1523, 1613] | 458 |
| 3 | `gpt-5.4` | 1532.9 | 23.4 | [1486, 1580] | 344 |
| 4 | `gpt-5.4@long` | 1512.3 | 26.2 | [1460, 1565] | 236 |
| 5 | `claude-opus-4.7-high` | 1495.1 | 22.2 | [1451, 1540] | 458 |
| 6 | `gpt-5.2` | 1461.2 | 26.2 | [1409, 1514] | 236 |
| 7 | `gpt-5.4-mini` | 1424.1 | 27.6 | [1369, 1479] | 236 |
| 8 | `claude-haiku-4.5` | 1391.0 | 22.9 | [1345, 1437] | 458 |

R25 item 5 effects: opus-default Δ-57 (gpt-5.4 stricter on applied-domain), gpt-5.4@long Δ-48, gpt-5.2 Δ-60; gpt-5.4 promoted to #3; sonnet steady; all baselines within ±60 of R24 (gate passes).

## Archive history

| Date | Archive dir | Sprint | Top entrant | Cumulative rows |
|---|---|---|---|---:|
| 2026-05-27 (m) | `2026-05-27-m-r25-median4/` | R25 item 5 — gpt-5.4 4th judge (median-of-4 ensemble) | opus-4.7@default-effort | 1283 |
| 2026-05-27 (l) | `2026-05-27-l-r25-per-rubric/` | R25 item 4 — per-rubric Glicko-2 split | (see per-rubric tables) | 1283 |
| 2026-05-27 (k) | `2026-05-27-k-r24/` | R24 3-judge ensemble re-judge (opus + haiku + sonnet) | opus-4.7@default-effort | 1283 |
| 2026-05-27 (j) | `2026-05-27-j-r23/` | R23 single-judge multi-entrant | opus-4.7@default-effort | 1283 |
| 2026-05-27 (i) | `2026-05-27-i/` | R22 Phase B1 (3-judge median) | sonnet-4.6 | 604 |
| 2026-05-27 (h) | `2026-05-27-h/` | R21 Phase B1 (2-judge median) | gpt-5.4 | 388 |
| 2026-05-27 (g) | `2026-05-27-g/` | R19 Phase B1 (3-judge stability) | sonnet-4.6 | 279 |
| 2026-05-27 (e) | `2026-05-27-e/` | R18 Phase D wave | sonnet-4.6 | 171 |
| 2026-05-27 (g) | `2026-05-27-g/` | R19 Phase B1 (3-judge stability) | sonnet-4.6 | 279 |
| 2026-05-27 (e) | `2026-05-27-e/` | R18 Phase D wave | sonnet-4.6 | 171 |

See `lab/reports/R23-report.md` for R23 methodology, single-judge
caveat, and 4-new-entrant analysis. See `lab/reports/R21-R22-report.md`
for ensemble methodology and the drift-audit Cohen's κ analysis.
