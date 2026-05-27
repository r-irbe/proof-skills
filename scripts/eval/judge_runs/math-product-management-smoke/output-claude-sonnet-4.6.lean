Now I have a clear picture of the current formalisation state. Here are the three highest-priority open formalisation tasks, ranked by the product of impact × confidence ÷ effort:

**1. Decompose `asyncIterate_lyapunovSupNorm_descent_at_window` (93 lines, P2)**
Impact: HIGH — this is the longest P2 proof and sits on the async Q-learning convergence critical path; a split exposes reusable lemmas for the entire `ReinforcementLearning` cluster. Confidence: HIGH — the proof already closes, so the decomposition is mechanical extraction of the `have`-chain. Effort: LOW-MEDIUM (one focused session).

**2. Fix unused hypothesis `hpq` in `PMF.llr_toMeasure_ae_eq_log_ratio`**
Impact: MEDIUM-HIGH — unused hypotheses in the KL-divergence / LLR surface are a correctness smell; removing `hpq` forces explicit proof that the conclusion is independent of it, potentially surfacing a latent bug. Confidence: VERY HIGH — the lint finding is deterministic. Effort: LOW (single-theorem fix, likely one `_root_.` or `simp only` adjustment).

**3. Reduce the remaining three heartbeat overrides in `CCVEContraction.lean` (800K + 1M) and `Contraction.lean` (1M)**
Impact: HIGH — heartbeat overrides are the only remaining category blocking a fully default-budget build; eliminating them removes fragility against future Mathlib elaborator regressions. Confidence: MEDIUM — W12 proved it viable for `floor_div_simplex_L1` (115→89 lines, override dropped); the same `have`-chain extraction strategy transfers directly. Effort: MEDIUM (three theorems, bisection + helper extraction per theorem, ~2–3 sessions).