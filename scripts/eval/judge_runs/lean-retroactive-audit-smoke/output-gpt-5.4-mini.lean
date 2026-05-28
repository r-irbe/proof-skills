import Std

partial def auditWave (importDAG : Std.HashMap String (List String)) (m : String) : Nat :=
  let imports := importDAG.findD m []
  match imports with
  | [] => 0
  | xs => 1 + xs.foldl (fun acc imp => Nat.max acc (auditWave importDAG imp)) 0
