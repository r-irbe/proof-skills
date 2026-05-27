In Mathlib4 (Lean 4) the lemma is `Nat.succ_pred_eq_of_pos` and lives in `Mathlib.Data.Nat.Basic` (file `Mathlib/Data/Nat/Basic.lean`). Its statement is:

    theorem Nat.succ_pred_eq_of_pos : ∀ {n : ℕ}, 0 < n → Nat.succ (Nat.pred n) = n

To use it in a rewrite you typically need a proof of `0 < n` in context:

    rw [Nat.succ_pred_eq_of_pos h]   -- where h : 0 < n

If you're on Lean 4 / Mathlib4 but the name isn't resolving, check `Nat.succ_pred_eq_of_ne_zero` or the core Std4 lemma `Nat.succ_pred_eq_of_pos` which may already be in `Init.Data.Nat.Basic` without a Mathlib import. You can locate it precisely with `#check Nat.succ_pred_eq_of_pos` or `exact?` / `apply?`. In Lean 3 Mathlib it's in `data.nat.basic` under the `nat` namespace as `nat.succ_pred_eq_of_pos`.
