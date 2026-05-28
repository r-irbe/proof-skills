import Std.Data.HashMap

def auditWave (importDAG : Std.HashMap String (List String)) (m : String) : Nat :=
  let rec go (visited : List String) (node : String) : Nat :=
    if visited.contains node then 0
    else
      match importDAG.get? node with
      | none => 0
      | some [] => 0
      | some deps =>
        1 + deps.foldl (fun acc d => Nat.max acc (go (node :: visited) d)) 0
  go [] m
