import Std

open Std

def auditWave (importDAG : Std.HashMap String (List String)) (m : String) : Nat :=
  let rec go (fuel : Nat) (mod : String) : Nat :=
    match fuel with
    | 0 => 0
    | fuel + 1 =>
      match importDAG.find? mod with
      | none => 0
      | some imps =>
        match imps with
        | [] => 0
        | _ :: _ =>
          let maxImp := imps.foldl (fun acc im => Nat.max acc (go fuel im)) 0
          1 + maxImp
  go importDAG.size m
