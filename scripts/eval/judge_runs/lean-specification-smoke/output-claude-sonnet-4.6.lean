theorem add_assoc_spec (a b c : Nat) (ha : 0 ≤ a) : a + (b + c) = (a + b) + c := by
  -- anchor: [T1.2]; source_spec: specs/arith/add_assoc.md
  exact Nat.add_assoc a b c
