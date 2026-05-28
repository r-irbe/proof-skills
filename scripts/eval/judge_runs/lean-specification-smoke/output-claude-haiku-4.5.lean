theorem add_comm_spec (a b : Nat) : a + b = b + a := by
    -- anchor: [T1.1]; source_spec: specs/arith/add_comm.md
    exact Nat.add_comm a b
