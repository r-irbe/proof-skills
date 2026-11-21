/-
Copyright (c) 2026 Proof-Skills Contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import Lean
import Lean.Replay

set_option autoImplicit false

/-!
# Cold In-Process Kernel Replay & Transitive Axiom Closure Auditor

Replays 100% of compiled `.olean` constants in a target Lake build library directory
(`COLD_REPLAY_LIB_DIR`, defaulting to `.lake/build/lib/lean`) from scratch on top of
external dependency modules alone via `Lean.Kernel.Environment.replay`, and audits
transitive axiom footprints across every theorem via `Lean.collectAxioms`.

Usage:
```bash
COLD_REPLAY_LIB_DIR=.lake/build/lib/lean lake env lean scripts/lean/cold_kernel_replay.lean
```
-/

open Lean

partial def collectOleans (dir : System.FilePath) : IO (Array System.FilePath) := do
  let mut out := #[]
  for ent in (← dir.readDir) do
    let p := ent.path
    if (← p.isDir) then
      out := out ++ (← collectOleans p)
    else if p.extension == some "olean" then
      out := out.push p
  return out

#eval show MetaM Unit from do
  let envLib ← (IO.getEnv "COLD_REPLAY_LIB_DIR" : IO _)
  let baseDir : System.FilePath := envLib.getD ".lake/build/lib/lean"
  if !(← baseDir.pathExists) then
    throwError s!"COLD_REPLAY_LIB_DIR does not exist: {baseDir}"

  let files ← collectOleans baseDir
  if files.isEmpty then
    throwError s!"Zero .olean artifacts found under {baseDir}; run `lake build` first."

  let sorted := files.qsort (fun a b => a.toString < b.toString)
  let mut sliceModNames : NameSet := {}
  let mut allImports : Array Import := #[]
  let mut seenImports : NameSet := {}

  for f in sorted do
    let rel := (f.toString.dropPrefix (baseDir.toString ++ "/")).toString
    let modName := (((rel.dropEnd 6).toString).replace "/" ".").toName
    sliceModNames := sliceModNames.insert modName
    if !seenImports.contains modName then
      seenImports := seenImports.insert modName
      allImports := allImports.push { module := modName }

  let fullEnv ← (importModules allImports {} 0 : IO _)

  let mut totalConsts : Nat := 0
  let mut totalThms : Nat := 0
  let mut totalDefs : Nat := 0
  let mut sourceAxioms : Nat := 0
  let mut badAxiomUses : List (Name × Name) := []
  let mut distinctAxioms : NameSet := {}
  let allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]

  let mut allSliceConsts : Std.HashMap Name ConstantInfo := {}
  let mut extImportSet : NameSet := {}
  let mut extImports : Array Import := #[]

  for f in sorted do
    let (modData, _) ← (readModuleData f.toString : IO _)
    for imp in modData.imports do
      if !sliceModNames.contains imp.module && !extImportSet.contains imp.module then
        extImportSet := extImportSet.insert imp.module
        extImports := extImports.push { module := imp.module }
    totalConsts := totalConsts + modData.constants.size
    for c in modData.constants do
      allSliceConsts := allSliceConsts.insert c.name c
      match c with
      | .thmInfo _ =>
        totalThms := totalThms + 1
        let axs ← withEnv fullEnv do collectAxioms c.name
        for ax in axs do
          distinctAxioms := distinctAxioms.insert ax
          if !allowed.contains ax then
            badAxiomUses := (c.name, ax) :: badAxiomUses
      | .defnInfo _ => totalDefs := totalDefs + 1
      | .axiomInfo _ => sourceAxioms := sourceAxioms + 1
      | _ => pure ()

  let freshExtEnv ← (importModules extImports {} 0 : IO _)
  let _ ← (Lean.Kernel.Environment.replay allSliceConsts freshExtEnv.toKernelEnv : IO _)

  IO.println s!"COLD_REPLAY_MODULES: {sorted.size}"
  IO.println s!"COLD_REPLAY_CONSTANTS: {totalConsts}"
  IO.println s!"COLD_REPLAY_THEOREMS: {totalThms}"
  IO.println s!"COLD_REPLAY_DEFINITIONS: {totalDefs}"
  IO.println s!"COLD_REPLAY_SOURCE_AXIOMS: {sourceAxioms}"
  IO.println s!"COLD_REPLAY_DISTINCT_AXIOMS: {distinctAxioms.toList}"
  IO.println s!"COLD_REPLAY_DISALLOWED_AXIOM_USES: {badAxiomUses.length}"
  IO.println s!"COLD_REPLAY_VERIFIED_CONSTANTS: {allSliceConsts.size} PASSED"
  if sourceAxioms > 0 || !badAxiomUses.isEmpty then
    throwError s!"Cold kernel replay / axiom audit failed: sourceAxioms={sourceAxioms}, bad={badAxiomUses}"
