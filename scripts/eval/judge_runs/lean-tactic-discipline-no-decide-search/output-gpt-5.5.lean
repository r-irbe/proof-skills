```lean
import Mathlib

open Finset

theorem sum_one_to_100 : (∑ i in Icc 1 100, i) = 5050 := by
  norm_num [sum_Icc_eq_sum_range]
```
