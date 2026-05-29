import Mathlib.Algebra.BigOperators.Basic
import Mathlib.Data.Finset.Basic

open Finset BigOperators

theorem sum_one_to_hundred : ∑ i in Finset.range 101, i = 5050 := by
  rw [Finset.sum_range_id]
  -- Goal: 101 * (101 - 1) / 2 = 5050, closes by kernel reduction
  rfl
