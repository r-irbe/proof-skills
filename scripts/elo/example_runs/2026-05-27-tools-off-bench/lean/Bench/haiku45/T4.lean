theorem t4 (a b : Nat) (h : a ≤ b) : a + 1 ≤ b + 1 :=  exact Nat.succ_le_succ h
