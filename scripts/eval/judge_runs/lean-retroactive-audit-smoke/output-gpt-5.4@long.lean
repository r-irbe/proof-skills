import Std

def auditWave (importDAG : Std.HashMap String (List String)) (m : String) : Nat :=
  let rec go (fuel : Nat) (mod : String) : Nat :=
    match fuel with
    | 0 => 0
    | fuel + 1 =>
        match importDAG.get? mod with
        | none => 0
        | some deps =>
            match deps with
            | [] => 0
            | _ => 1 + deps.foldl (fun acc dep => Nat.max acc (go fuel dep)) 0
  go importDAG.size m
