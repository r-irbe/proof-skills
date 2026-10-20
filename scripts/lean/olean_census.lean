import Lean

open Lean

partial def getOleanFiles (dir : System.FilePath) : IO (Array System.FilePath) := do
  let mut results := #[]
  for entry in (<- dir.readDir) do
    let p := entry.path
    if (<- p.isDir) then
      results := results ++ (<- getOleanFiles p)
    else if p.extension == some "olean" then
      results := results.push p
  return results

def main (args : List String) : IO Unit := do
  let baseDir : System.FilePath := if args.isEmpty then ".lake/build/lib/lean" else args.head!
  let files <- getOleanFiles baseDir
  let sortedFiles := files.qsort (fun a b => a.toString < b.toString)
  IO.println "=== Binary OLean Kernel Census ==="
  IO.println s!"Total .olean files found: {sortedFiles.size}"
  
  let mut totalTheorems : Nat := 0
  let mut totalDefs : Nat := 0
  let mut totalAxioms : Nat := 0
  let mut totalConstants : Nat := 0
  let mut axiomList : List (Prod String Name) := []

  for f in sortedFiles do
    let (modData, _) <- readModuleData f.toString
    totalConstants := totalConstants + modData.constants.size
    for c in modData.constants do
      match c with
      | ConstantInfo.thmInfo _ => totalTheorems := totalTheorems + 1
      | ConstantInfo.defnInfo _ => totalDefs := totalDefs + 1
      | ConstantInfo.axiomInfo ax =>
        totalAxioms := totalAxioms + 1
        axiomList := (f.toString, ax.name) :: axiomList
      | _ => pure ()

  IO.println s!"Total kernel constants: {totalConstants}"
  IO.println s!"Kernel theorems:        {totalTheorems}"
  IO.println s!"Kernel definitions:     {totalDefs}"
  IO.println s!"Kernel axioms:          {totalAxioms}"

  if totalAxioms > 0 then
    IO.println "WARNING: Axioms detected:"
    for (mod, ax) in axiomList do
      IO.println s!"  {mod}: {ax}"
  else
    IO.println "Kernel axiom check PASSED: 0 axioms across all compiled modules."
