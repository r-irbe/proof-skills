def auditWave (importDAG : Std.HashMap String (List String)) (m : String) : Nat :=
  let rec go (visited : Std.HashSet String) (m : String) : Nat :=
    if visited.contains m then 0
    else
      match importDAG.get? m with
      | some imports =>
        if imports.isEmpty then 0
        else
          let visited' := visited.insert m
          1 + (imports.map (go visited') |>.foldl Nat.max 0)
      | none => 0
  go Std.HashSet.empty m
