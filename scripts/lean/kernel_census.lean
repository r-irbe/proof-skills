import Lean
import Lean.Replay

set_option autoImplicit false
open Lean

partial def censusFiles (dir : System.FilePath) : IO (Array System.FilePath) := do
  let mut result := #[]
  for entry in ← dir.readDir do
    if ← entry.path.isDir then
      result := result ++ (← censusFiles entry.path)
    else if entry.path.extension == some "olean" then
      result := result.push entry.path
  return result

-- Kernel.replay and collectAxioms are Lean APIs; the foreign cold-replay draft
-- motivated this adapter, but remains unmodified and is not a runtime dependency.
#eval show MetaM Unit from do
  let some directory ← IO.getEnv "KERNEL_CENSUS_LIB_DIR" | throwError "Missing census artifact view"
  let base : System.FilePath := directory
  let files := (← censusFiles base).qsort (fun a b => a.toString < b.toString)
  if files.isEmpty then throwError "Empty compiled scope"
  searchPathRef.modify (base :: ·)
  let mut targetModules : NameSet := {}
  let mut imports : Array Import := #[]
  for file in files do
    let relative := (file.toString.dropPrefix (directory ++ "/")).toString
    let name := ((relative.dropEnd 6).toString.replace "/" ".").toName
    targetModules := targetModules.insert name
    imports := imports.push { module := name, importAll := true }
  -- Explicitly enable initializers before loading the imported extension.
  unsafe enableInitializersExecution
  -- Load the
  -- compiler's exported axiom extension rather than repeatedly walking Mathlib.
  let fullEnv ← importModules imports {} 0 (leakEnv := true) (loadExts := true) (level := .private)
  let mut constants : Std.HashMap Name ConstantInfo := {}
  let mut repeatedTheorems : Array String := #[]
  let keepAlive ← IO.mkRef (#[] : Array CompactedRegion)
  let mut externalNames : NameSet := {}
  let mut external : Array Import := #[]
  for file in files do
    let (header, region) ← readModuleData file
    let mut data := header
    keepAlive.modify (·.push region)
    if header.isModule then
      let parts ← readModuleDataParts #[file, ⟨file.toString ++ ".server"⟩, ⟨file.toString ++ ".private"⟩]
      for part in parts do keepAlive.modify (·.push part.2)
      data := (parts.map (·.1)).back!
    for imp in data.imports do
      if !targetModules.contains imp.module && !externalNames.contains imp.module then
        externalNames := externalNames.insert imp.module
        external := external.push imp
    for info in data.constants do
      if let some previous := constants[info.name]? then
        match previous, info with
        | .thmInfo a, .thmInfo b =>
          if a == b then repeatedTheorems := repeatedTheorems.push info.name.toString
          else throwError "Conflicting repeated theorem {info.name}"
        | _, _ => throwError "Duplicate non-theorem constant {info.name}"
      else
        constants := constants.insert info.name info
  let externalEnv ← importModules external {} 0 (level := .private)
  for (name, _) in constants.toList do
    if (externalEnv.toKernelEnv.find? name).isSome then
      throwError "Target constant already in replay base: {name}"
  let mut privateTheorems := 0
  let mut axiomAudited := 0
  let mut theorems := 0
  let mut definitions := 0
  let mut declaredAxioms := 0
  let mut skippedUnsafe := 0
  let mut skippedPartial := 0
  let mut eligible : Array Name := #[]
  let mut theoremNames : Array String := #[]
  let mut distinct : NameSet := {}
  let mut bad : Array String := #[]
  for (name, info) in constants.toList do
    if info.isUnsafe then skippedUnsafe := skippedUnsafe + 1
    else if info.isPartial then skippedPartial := skippedPartial + 1
    else eligible := eligible.push name
    match info with
    | .thmInfo _ =>
      theorems := theorems + 1
      if isPrivateName name then privateTheorems := privateTheorems + 1
      theoremNames := theoremNames.push name.toString
      if info.isUnsafe || info.isPartial then throwError "Unreplayed theorem: {name}"
    | .defnInfo _ => definitions := definitions + 1
    | .axiomInfo _ => declaredAxioms := declaredAxioms + 1
    | _ => pure ()
    if !info.isUnsafe && !info.isPartial then
      axiomAudited := axiomAudited + 1
      if ((fullEnv.setExporting false).toKernelEnv.find? name).isNone then
        throwError "Theorem absent from axiom environment: {name}"
      let axioms ← withEnv fullEnv do collectAxioms name
      for ax in axioms do
        distinct := distinct.insert ax
        if ax != ``propext && ax != ``Classical.choice && ax != ``Quot.sound then
          bad := bad.push s!"{name}: {ax}"
  IO.println "KERNEL_CENSUS_STAGE: cold-replay"
  let replayedEnv ← Kernel.Environment.replay constants externalEnv.toKernelEnv
  let mut replayed := 0
  for name in eligible do
    if (replayedEnv.find? name).isNone then throwError "Missing replayed constant: {name}"
    replayed := replayed + 1
  let retained ← keepAlive.get
  let report := Json.mkObj [
    ("repeatedIdenticalTheorems", toJson repeatedTheorems),
    ("modules", toJson files.size), ("constants", toJson constants.size),
    ("theorems", toJson theorems), ("privateTheorems", toJson privateTheorems),
    ("axiomAudited", toJson axiomAudited), ("definitions", toJson definitions),
    ("declaredAxioms", toJson declaredAxioms), ("eligible", toJson eligible.size),
    ("replayed", toJson replayed), ("skippedUnsafe", toJson skippedUnsafe),
    ("skippedPartial", toJson skippedPartial), ("loadedParts", toJson retained.size),
    ("distinctAxioms", toJson (distinct.toList.map Name.toString)),
    ("disallowedAxiomUses", toJson bad.size), ("badAxiomUses", toJson bad),
    ("constantNames", toJson ((constants.toList.map (fun p => p.1.toString)).toArray.qsort (· < ·))),
    ("theoremNames", toJson (theoremNames.qsort (· < ·)))]
  IO.println s!"KERNEL_CENSUS_JSON:{report.compress}"
  if declaredAxioms > 0 || !bad.isEmpty then throwError "Disallowed kernel axioms"
