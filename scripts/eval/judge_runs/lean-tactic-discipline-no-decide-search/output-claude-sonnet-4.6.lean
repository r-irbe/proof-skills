theorem sum_100 : (Finset.range 101).sum id = 5050 := by
  norm_num [Finset.sum_range_succ]
