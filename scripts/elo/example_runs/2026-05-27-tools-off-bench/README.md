# Tools-Off Bench — 5 Models × 5 Coding + 5 Lean Problems

**Date:** 2026-05-27
**Driver:** GitHub Copilot CLI (Claude Opus 4.7 1M)
**Goal:** Produce a *real* Elo ranking by pitting 5 models against each other on tasks where they cannot delegate the answer to a Python interpreter or to a search engine — only reasoning is allowed.

This run was assembled to put the [`elo.py`](../../elo.py) script through a non-toy workload that exercises **its full I/O contract** (`--matches CSV --out DIR`) on data sourced from real model comparisons, **not** from synthetic priors.

---

## TL;DR — final leaderboard

100 matches (50 coding + 50 lean), K=32, R₀=1500:

| Rank | Model                          | Rating  | Games |
| ---: | ------------------------------ | ------: | ----: |
|    1 | `claude-opus-4.7-high`         | 1541.3  |    40 |
|    2 | `claude-sonnet-4.6`            | 1539.7  |    40 |
|    3 | `gpt-5.4`                      | 1539.1  |    40 |
|    4 | `claude-opus-4.7`              | 1517.3  |    40 |
|    5 | `claude-haiku-4.5`             | 1362.7  |    40 |

20 decisive matches, 80 draws.

---

## Method

### Battery 1 — Coding-by-execution (`coding/`)

5 Python problems, each with a hidden 10-test suite verified to pass on a reference solution before models were prompted:

- **P1**  `count_inversions(arr: list[int]) -> int`
- **P2**  `is_balanced(s: str) -> bool`
- **P3**  `longest_palindrome_subseq(s: str) -> int`
- **P4**  `fizzbuzz_count(n: int) -> int` — count `k ∈ 1..n` with `(k%3==0) XOR (k%5==0)`
- **P5**  `min_jumps(arr: list[int]) -> int` — min jumps to reach the last index; `-1` if unreachable

Per (model, problem): score = passes out of 10. Per pair-of-models on a problem: more passes wins; tied = draw.

### Battery 2 — Lean-proof-by-build (`lean/`)

5 Lean 4 theorems graded by `lake build` (stdlib only — no Mathlib needed):

- **T1**  `theorem t1 (a b c : Nat) : a + b + c = c + b + a`
- **T2**  `theorem t2 (n : Nat) : 2 * n = n + n`
- **T3**  `theorem t3 {α : Type _} (l : List α) : l.reverse.reverse = l`
- **T4**  `theorem t4 (a b : Nat) (h : a ≤ b) : a + 1 ≤ b + 1`
- **T5**  `theorem t5 (n : Nat) (h : 0 < n) : ∃ m, n = m + 1`

Per (model, problem): score = 1 if Lean accepts the file, 0 otherwise.

### Aggregation (`combined/`)

10 problems × C(5,2) = 10 pairwise comparisons each = **100 matches** fed to `elo.py` as one CSV.

---

## Where the differentiation came from

The 20 decisive matches all trace to **two bugs**:

1. **`claude-opus-4.7` on P5** — its `min_jumps` returns `jumps` early when `i == n-1` without checking whether the last index is actually reachable. Fails 5/10 cases including `[1,1,1,1]` → 2 (expected 3) and `[3,2,1,0,4]` → 1 (expected -1). See [`coding/responses/claude-opus-4.7.txt`](coding/responses/claude-opus-4.7.txt).
2. **`claude-haiku-4.5` on T1–T4** — wrote bare tactic names (`omega`, `simp`, `exact`) as term-mode proofs. Lean requires a `by …` block after `:=` for tactic invocation. Only T5 used proper term syntax (`match n with …`) and compiled. See [`lean/responses/claude-haiku-4.5.txt`](lean/responses/claude-haiku-4.5.txt) and [`lean/Bench/haiku45/`](lean/Bench/haiku45).

The other three models swept both batteries.

---

## What this run is *not*

- **Not a definitive ranking.** Sample size is small (10 problems, 5 models). Tie-breaking among `opus-4.7-high` / `sonnet-4.6` / `gpt-5.4` (each swept) is essentially K-factor noise from match order.
- **Not tool-use evaluation.** Tool use was explicitly forbidden in prompts. A separate run with tool use enabled showed *zero* differentiation across all 5 models on integer-answer math (every model used Python and got every answer right) — see the "ceiling-effect" commentary in the parent CLI session.
- **Not a proof-skills regression.** It does not exercise the skill pages themselves — only the `elo.py` aggregator + a representative harness for what driving it with real-model output looks like.

---

## Reproducing

Prerequisites: `python3`, `lean 4.30.0` / `lake` (via `elan`), 5 model agents reachable from the driver.

### Coding battery

```bash
cd coding/
python3 tests.py                # verifies reference solutions (sanity)
# dispatch prompt.txt to each model, save responses to responses/<full-model-name>.txt
python3 grade.py                # writes scores.json + prints scoreboard
python3 build_csv.py            # writes matches.csv
python3 ../../../elo.py --matches matches.csv --out .
```

### Lean battery

```bash
cd lean/
mkdir -p .lake && cd ..         # scratch project at this directory
# Repurpose this directory's Bench/ tree as a lake_lib (see ../../gen_sample.py for an inline lakefile)
cd lean/
# dispatch prompt.txt to each model, save to responses/<full-model-name>.txt
python3 grade.py                # creates per-model Bench/<short>/T*.lean files and runs lake build
python3 ../coding/build_csv.py  # (with lean-aware variant; this run used the combined builder)
```

### Combined

```bash
cd combined/
python3 build.py                # reads ../coding/scores.json + ../lean/scores.json → matches.csv + invokes elo.py
```

---

## Files

| Path                                       | What                                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------ |
| `coding/prompt.txt`                        | Exact prompt sent to each of 5 models                                    |
| `coding/tests.py`                          | Reference solutions + hidden test suites (50 tests total)                |
| `coding/responses/<model>.txt`             | Raw model output (function definitions only, no markdown fences)         |
| `coding/grade.py`                          | Extracts code, execs, runs tests, writes `scores.json`                   |
| `coding/build_csv.py`                      | Score → pairwise `matches.csv` for `elo.py`                              |
| `coding/{matches.csv, ratings.json, leaderboard.md}` | `elo.py` output on coding-only matches                         |
| `lean/prompt.txt`                          | Exact prompt sent to each model                                          |
| `lean/responses/<model>.txt`               | Raw proof terms / `by`-blocks per problem                                |
| `lean/Bench/<short>/T<n>.lean`             | Per-model per-problem standalone Lean file (graded by `lake build`)      |
| `lean/grade.py`                            | Writes `Bench/<short>/T<n>.lean` and runs `lake build` to compute pass   |
| `lean/scores.json`                         | `{model → {T1..T5 → {ok: bool, log: str}}}`                              |
| `combined/build.py`                        | Reads both `scores.json` files, emits combined `matches.csv`, runs `elo.py` |
| `combined/{matches.csv, ratings.json, leaderboard.md}` | Final combined-Elo output                                    |

---

## Authorship

Driven autonomously by the GitHub Copilot CLI session at `/Users/radu/.copilot/session-state/e67b2c5b-66ce-4a86-8ffa-1f639dbe94b8/`. The 5 model agents were dispatched via the `task` tool with explicit `model:` overrides. Each agent ran in its own subprocess with no shared state.
