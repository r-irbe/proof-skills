import Mathlib

open Finset

example : ∑ i in Finset.range 101, i = 5050 := by
  rw [Finset.sum_range_id]
  norm_num
