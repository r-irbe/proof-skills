/-
  scripts/lean/olean_census.lean
  Standalone Lean 4 environment & .olean declaration census utility.
  Counts constants, theorems, definitions, inductive types, and checks
  transitive axiom hygiene in the loaded environment.
  Scoped Unicode policy (INV-001; typographic-free by default).
-/
import Lean

open Lean

namespace OleanCensus

structure CensusSummary where
  totalDecls : Nat := 0
  theorems   : Nat := 0
  defs       : Nat := 0
  axioms     : Nat := 0
  inductives : Nat := 0
  quotients  : Nat := 0
  deriving Repr, Inhabited

/-- Classify every declaration in the current `Environment`. -/
def collectEnvCensus (env : Environment) : CensusSummary :=
  env.constants.fold (init := {}) fun acc _ cinfo =>
    let base := { acc with totalDecls := acc.totalDecls + 1 }
    match cinfo with
    | .thmInfo _   => { base with theorems   := base.theorems + 1 }
    | .defnInfo _  => { base with defs       := base.defs + 1 }
    | .axiomInfo _ => { base with axioms     := base.axioms + 1 }
    | .inductInfo _ => { base with inductives := base.inductives + 1 }
    | .quotInfo _  => { base with quotients  := base.quotients + 1 }
    | _            => base

/-- Permitted standard axioms in Lean 4 contest & high-assurance gates. -/
def isPermittedStandardAxiom (n : Name) : Bool :=
  n == ``propext || n == ``Classical.choice || n == ``Quot.sound

/-- Return all axioms in `env` outside `[propext, Classical.choice, Quot.sound]`. -/
def nonStandardAxiomsInEnv (env : Environment) : Array Name :=
  env.constants.fold (init := #[]) fun acc name cinfo =>
    match cinfo with
    | .axiomInfo _ =>
      if isPermittedStandardAxiom name then acc else acc.push name
    | _ => acc

end OleanCensus
