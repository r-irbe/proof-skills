import Std

def auditWave (importDAG : Std.HashMap String (List String)) (m : String) : Nat :=
  Id.run do
    let mut memo : Std.HashMap String Nat := Std.HashMap.empty
    let mut stack : List (String × Bool) := [(m, false)]
    while !stack.isEmpty do
      match stack with
      | [] => pure ()
      | (modName, expanded) :: rest =>
          stack := rest
          if expanded then
            let imports := importDAG.getD modName []
            let level :=
              match imports with
              | [] => 0
              | _ => 1 + imports.foldl (fun acc dep => max acc (memo.getD dep 0)) 0
            memo := memo.insert modName level
          else if memo.contains modName then
            pure ()
          else
            let imports := importDAG.getD modName []
            stack := (modName, true) :: stack
            for dep in imports.reverse do
              if !memo.contains dep then
                stack := (dep, false) :: stack
    pure (memo.getD m 0)
