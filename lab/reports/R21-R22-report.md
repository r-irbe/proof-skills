# Rounds 21 & 22 — Ensemble judging methodology & leaderboard

**Date:** 2026-05-27
**Sprint scope:** R21 = 2-judge median per case (opus_R20 + sonnet_R21);
R22 = 3-judge median per case (adds opus-4.6 + 4 cal corpora extensions).

This report consolidates two consecutive ELO/eval expansion rounds
landed on the standalone `r-irbe/proof-skills` fork and bumped into
the `tacit-mui` superrepo as submodule `wave-3`.

## Methodology

### Ensemble judging design (R19 → R22 evolution)

Per design `lab/design/01-eval-framework.md` §4.2 (LLM judge minority
veto) + ADR-0039 (calibrated judges):

- **R19 baseline:** single-judge canonical score per (case, solver).
  Inherent risk of self-bias.
- **R21:** 2-judge median (`opus_R20` + `sonnet_R21`), Cohen's κ
  audit confirmed substantial agreement (κ = 0.777, see
  `reports/_drift_audit/2026-05-27-b1-ensemble-kappa.md`).
- **R22:** 3-judge median (`opus_R20` + `sonnet_R21` + `opus_R22`).
  Cohen's κ across all 3 pairs ≥ 0.83 (almost-perfect band, Landis
  & Koch 1977). Of 36 cases, 7 shifted score by +1 — opus-4.6 was
  systematically slightly less harsh than the R21 pair. Net
  4-entrant ELO movement was within the 75-pt regression-gate
  tolerance.

### Calibration corpus expansion (R22 Phase F2)

ADR-0039 requires a known-bad corpus that the LLM-judge ensemble
flags ≥ 90 % of as ≤ pass_floor before the judge can be trusted in
CI. Before R22 there were 3 corpora (`lean-doc-quality`,
`research-synthesis-quality`, `applied-domain-quality`) plus the
original `lean-proof` corpus.

R22 added 20 new transcripts:

| Cluster | New transcripts | Total | Flag rate |
|---|---:|---:|---:|
| `lean-doc` | +5 | 15 | 92.86 % (13/14 negatives) |
| `research-synthesis` | +5 | 15 | 100.00 % |
| `applied-domain` | +5 | 15 | 100.00 % |
| `lean-tactic-discipline` *(new)* | +5 | 5 | 100.00 % |

The new `lean-tactic-discipline` cluster covers Lean-specific tactic
discipline failures (banned `exact?` / `apply?`, `decide` on large
`Fin`, `native_decide` without justification, `omega` on non-linear
goals, recursion without termination proof). Rubric:
`scripts/eval/graders/rubrics/lean-tactic-discipline-quality.yaml`.

All 4 cluster gates pass at 90 % minimum flag-rate threshold under
the 3-judge ensemble (3 × 20 = 60 judge replies harvested via the
inline-reply mitigation pattern documented in AGENT.md §1.5.1).

## Leaderboard (post R22 Phase B1)

Glicko-2 archived at `scripts/elo/example_runs/2026-05-27-i/`.

| Rank | Player | Rating | RD | 95 % CI | Games |
|---|---|---:|---:|---|---:|
| 1 | `claude-sonnet-4.6` | 1574.3 | 25.1 | [1524, 1624] | 330 |
| 2 | `gpt-5.4` | 1548.9 | 26.8 | [1495, 1602] | 216 |
| 3 | `claude-opus-4.7-high` | 1508.7 | 24.8 | [1459, 1558] | 330 |
| 4 | `claude-haiku-4.5` | 1406.8 | 26.1 | [1355, 1459] | 330 |

**Δ vs R21 archive `2026-05-27-h/`:**

| Player | R21 → R22 | Direction |
|---|---:|---|
| `claude-sonnet-4.6` | 1564.27 → 1574.27 | +10.00 |
| `gpt-5.4` | 1569.80 → 1548.85 | -20.95 |
| `claude-opus-4.7-high` | 1528.54 → 1508.73 | -19.81 |
| `claude-haiku-4.5` | 1369.96 → 1406.76 | +36.80 |

All movements within the 75-pt regression tolerance. The 3rd judge
(opus-4.6) tightened verdicts on 7/36 cases, mostly pulling
opus_R20 + sonnet_R21 medians upward — which lowered gpt-5.4 and
opus-4.7-high a few points while haiku climbed because its outputs
got more 3s than 2s under opus-4.6.

## Match volume after ingestion

| Round | Live CSV rows | Δ |
|---|---:|---:|
| R18 phase D | 171 | +153 |
| R19 phase B1 | 279 | +108 |
| R21 phase B1 | 388 | +109 |
| R22 phase B1 | 604 | +216 |

The R22 increment is larger (4 entrants × C(4,2)=6 pairs per case
× 36 cases) because the R22 cases now include `output-gpt-5.4.lean`
as a 4th solver alongside opus-high / sonnet / haiku.

## Cumulative commits

**Fork `r-irbe/proof-skills`:**

- `b6f9e0a` — R21 complete (2-judge ensemble + cal corpora)
- (current pass) — R22 complete (3-judge ensemble + 4 cal corpora
  extensions + new `lean-tactic-discipline` cluster + drift audit +
  ELO refresh)

**Superrepo `tacit-mui` `wave-3`:**

- `f5104e5` — R21 submodule bump
- (current pass) — R22 submodule bump

## Carried-over to next round (R23 candidates)

The R22 HITL form selected the maximum-effort path including 4 LLM
solver/judge waves (C1, D1×2, E1) that were not dispatched this
pass due to context budget; their generated prompts are reproducible
artifacts in `/tmp/round22/{c1,d1mini,d1gpt52,e1}_prompts/`. The
session-wide `/tmp` write ban (now affecting *all* judge models, not
just haiku) makes dispatch-and-harvest more expensive than estimated.
R23 should either:

1. Pre-bake all sub-agent JSON outputs to inline-reply harvested
   form (the verified working mitigation), batched ≤ 6 per agent;
   or
2. Run the same dispatches via the Anthropic SDK directly once
   `run_multi_model.py` Flavour B is implemented.

The C1/D1/E1 waves remain genuine extensions of the methodology
(long-prompt variant, mini/gpt-5.2 entrants, effort sweep) and are
durably scoped for the next pass.
