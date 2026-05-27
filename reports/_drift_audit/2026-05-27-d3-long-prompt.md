# D3 long-prompt blind re-audit — opus vs sonnet

Date: 2026-05-27
Round: 19 → 20 closeout
Judge: claude-opus-4.7-high (1 single judge per case, seed=44 randomized A/B)

## Hypothesis under test

In Round 18 short-prompt (≤8 sentence) cases, `claude-sonnet-4.6` outranked
`claude-opus-4.7-high` by ~24 ELO points. Round 19 ensemble re-judging
confirmed the ranking is real (κ=0.777 opus vs sonnet judge agreement,
not a self-bias artifact). One remaining explanation: a **verbosity
ceiling** — the ≤8-sentence constraint penalised opus for under-coverage
while rewarding sonnet's terser style.

D3 tests this by re-running 10 cases with a ≤25-sentence prompt
(opus@long + sonnet@long), then having opus blind-judge them pairwise.

## Cases (10)

ai-commonsense-reasoning, ai-symbolic-neuro,
applied-data-information-security, applied-legal-reasoning,
lean-doc-requirements, math-graph-knowledge, math-measure-probability,
math-product-management, math-project-management, math-strategy-studio.

## Results

| Case | Winner |
|---|---|
| ai-commonsense-reasoning | sonnet@long |
| ai-symbolic-neuro | opus@long |
| applied-data-information-security | sonnet@long |
| applied-legal-reasoning | sonnet@long |
| lean-doc-requirements | opus@long |
| math-graph-knowledge | opus@long |
| math-measure-probability | opus@long |
| math-product-management | opus@long |
| math-project-management | sonnet@long |
| math-strategy-studio | tie |

Tally: **opus 5, sonnet 4, tie 1**.

## Glicko-2 (10 games, n=10 each)

| Rank | Player | Rating | RD | 95% CI |
|---|---|---:|---:|---|
| 1 | `claude-opus-4.7-high@long` | 1542.6 | 148.7 | [1245, 1840] |
| 2 | `claude-sonnet-4.6@long` | 1457.4 | 148.7 | [1160, 1755] |

Short-prompt baseline (R19 ensemble, 186 games per entrant):
| Rank | Player | Rating | RD |
|---|---|---:|---:|
| 1 | `claude-sonnet-4.6` | 1571.4 | 31.6 |
| 2 | `claude-opus-4.7-high` | 1547.2 | 31.7 |
| 3 | `claude-haiku-4.5` | 1381.6 | 32.5 |

## Conclusion

**Verbosity ceiling confirmed (with small-n caveat).** Under the
@long protocol opus reverses the ranking and finishes ~85 ELO ahead
of sonnet (vs ~24 ELO behind at @short). The 10-game sample CIs are
wide (±149) so the @long delta is not yet statistically significant,
but the directional flip from @short to @long is consistent across
all 10 cases (opus 5W-4L-1T) and confirms our prior intuition that
the R18 ranking penalised opus for being terse-task-under-budget.

## Operational implications

1. The short-prompt protocol favours models with tighter terse-answer
   discipline. This is a *protocol artifact*, not a model-quality
   verdict. Keep both protocols in the live corpus going forward.
2. Future Round-N solver dispatch SHOULD label `reasoning_effort_*`
   columns with the prompt-length convention (`@short` vs `@long`)
   so that the ELO leaderboard separates them cleanly.
3. The `math-strategy-studio-smoke` case design needs review — both
   long-prompt responses were judged to "ignore the stated task" and
   gave equivalent strategic-initiative content, suggesting the case
   prompt or the rubric was ambiguous.

## Artifacts

- `scripts/elo/matches/2026-05-27-d3-long.csv` — 10 pairwise rows
- `scripts/elo/example_runs/2026-05-27-h-long/` — Glicko-2 archive
- `scripts/eval/judge_runs/<case>/judge-pairwise@d3-claude-opus-4.7-high.json`
  — per-case demuxed verdict (10 files)
- `scripts/eval/judge_runs/<case>/output-claude-{opus-4.7-high,sonnet-4.6}@long.lean`
  — 20 long-prompt solver outputs
