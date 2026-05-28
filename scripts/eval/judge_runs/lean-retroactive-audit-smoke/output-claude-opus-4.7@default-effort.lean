partial def auditWave (importDAG : Std.HashMap String (List String)) (m : String) : Nat :=
  match importDAG.get? m with
  | none => 0
  | some [] => 0
  | some imps =>
    1 + imps.foldl (fun acc i => Nat.max acc (auditWave importDAG i)) 0
