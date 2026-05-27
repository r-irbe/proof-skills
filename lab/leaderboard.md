# Leaderboard (rolling)

**Current archive:** `scripts/elo/example_runs/2026-05-27-k-r24/` (post-R24 3-judge ensemble re-judge).

| Rank | Player | Rating | RD | 95 % CI | Games |
|---|---|---:|---:|---|---:|
| 1 | `claude-opus-4.7@default-effort` | 1781.7 | 37.0 | [1708, 1856] | 140 |
| 2 | `gpt-5.4@long` | 1560.9 | 26.3 | [1508, 1614] | 236 |
| 3 | `claude-sonnet-4.6` | 1545.7 | 22.5 | [1501, 1591] | 458 |
| 4 | `gpt-5.2` | 1520.7 | 26.3 | [1468, 1573] | 236 |
| 5 | `gpt-5.4` | 1506.2 | 23.5 | [1459, 1553] | 344 |
| 6 | `claude-opus-4.7-high` | 1476.5 | 22.3 | [1432, 1521] | 458 |
| 7 | `gpt-5.4-mini` | 1421.8 | 27.7 | [1366, 1477] | 236 |
| 8 | `claude-haiku-4.5` | 1381.1 | 23.0 | [1335, 1427] | 458 |

## Archive history

| Date | Archive dir | Sprint | Top entrant | Cumulative rows |
|---|---|---|---|---:|
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
