import Mathlib

open scoped BigOperators
open Finset

example : (∑ i in Finset.range 100, (i + 1 : Nat)) = 5050 := by
  calc
    (∑ i in Finset.range 100, (i + 1 : Nat))
        = (∑ i in Finset.range 100, (i : Nat)) + (∑ _i in Finset.range 100, (1 : Nat)) := by
            simpa using
              (Finset.sum_add_distrib (s := Finset.range 100)
                (f := fun i : Nat => (i : Nat)) (g := fun _ : Nat => (1 : Nat)))
    _ = (100 * (100 - 1)) / 2 + 100 := by
            simp [Finset.sum_range_id]
    _ = 5050 := by
            norm_num
