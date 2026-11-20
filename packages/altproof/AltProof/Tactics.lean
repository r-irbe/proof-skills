/-
Copyright (c) 2026 Proof-Skills. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Proof-Skills Contributors
SPDX-License-Identifier: Apache-2.0
-/

import AltProof.Core
import AltProof.Closers

set_option autoImplicit false

/-!
# AltProof.Tactics -- Speculative Alternative-Proof & Elegance Meta-Tactics

Composes `AltProof.Core` (20-route advisor, `eqsat_rw`, `backchain`, `contra_direct`,
`kernel_decide`, `eval_nat%`, `preunfold%`, `swar_unroll%`) and
`AltProof.Closers` (`sum_congr_ring`, `calc_ring_sum`, `gcongr_pos`, `finset_nonneg`,
`finset_mono`, `convex_comb`, `markov_row_sum`, `matrix_pos`, `sup_norm_scale`,
`deriv_quot_ring`, and finite/norm bridge lemmas) into:

1. **`alt_proof` Meta-Tactic**: ordered automated reduction cascade.
2. **Speculative `elegance?` & `bfs_elegance?` Interactive Explorers**:
   AST feature detection, `withoutModifyingState` heartbeat profiling, `computeCostX10`
   ranking, and `TryThis` suggestion emission.

Production modules that only require non-interactive proof-body closers can import
`AltProof.Closers` directly without pulling in interactive advisor infrastructure.
-/

open Lean Meta Elab Tactic
open scoped BigOperators

namespace AltProof.Tactics

export AltProof.Core (
  Route
  routeTable
  CostWeights
  computeCostX10
  TwoAxisScore
  routesToJson
  GoalFeatures
  exprContainsConst
  extractExprFeatures
  extractGoalFeatures
  filterRelevantRoutes
  EqSatRule
  EqSatNode
  saturateEquality
  evalEqsatRw
  evalClosedNatExpr
  preunfoldExprWith
  buildUnrolledLoop
)

export AltProof.Closers (
  specializePointwiseHyps
  evalFinsetNonneg
  evalFinsetMono
  unpackContextAndHyps
  instantiateLocalForallEqsAndBounds
  evalConvexComb
  evalMarkovRowSum
  evalMatrixPos
  sup'_const_mul_of_nonneg
  fin_card_filter_Ico
  natAbs_le_div_of_cast_abs_le
  zero_sum_vecMul_l1_le_of_entry_floor
)

/-- `alt_proof`: ordered automated reduction cascade that attempts fast kernel-friendly
    closers (`rfl`, `assumption`, `bv_decide`, `decide`, `omega`, `ring`, `sum_congr_ring`,
    `calc_ring_sum`, `finset_nonneg`, `finset_mono`, `convex_comb`, `markov_row_sum`, `matrix_pos`,
    `sup_norm_scale`, `deriv_quot_ring`, `gcongr_pos`, `positivity`, `linarith`, `nlinarith`,
    `norm_num`, `eqsat_rw`, `contra_direct`, `backchain`, `aesop`). -/
syntax (name := altProofTactic) "alt_proof" : tactic

macro_rules
  | `(tactic| alt_proof) => `(tactic|
      first
      | rfl
      | assumption
      | bv_decide
      | decide
      | omega
      | (ring; done)
      | (sum_congr_ring; done)
      | (calc_ring_sum; done)
      | (finset_nonneg; done)
      | (finset_mono; done)
      | (convex_comb; done)
      | (markov_row_sum; done)
      | (matrix_pos; done)
      | (sup_norm_scale; done)
      | (deriv_quot_ring; done)
      | gcongr_pos
      | (positivity; done)
      | linarith
      | nlinarith
      | (norm_num; done)
      | (eqsat_rw; done)
      | (contra_direct; done)
      | backchain
      | (aesop; done))

/-- Result of speculatively probing a candidate tactic in `withoutModifyingState`. -/
structure CandidateResult where
  tacticSyntax : String
  heartbeats : Nat
  costX10 : Int
deriving Inhabited, Repr

/-- Speculatively run `tacStx` without modifying proof state; return `some CandidateResult`
    if the tactic closes all goals. Measures exact kernel/elaborator heartbeats via `IO.getNumHeartbeats`
    inside a fresh `withCurrHeartbeats` window so probing 15+ candidate closers never starves
    the caller's outer `maxHeartbeats` budget. -/
def tryCandidateCloser (tacName : String) (tacStx : Syntax) (steps : Nat := 1) : TacticM (Option CandidateResult) := do
  withCurrHeartbeats <| withoutModifyingState do
    try
      let hbStart ← IO.getNumHeartbeats
      evalTactic tacStx
      let rem ← getUnsolvedGoals
      if rem.isEmpty then
        let hbEnd ← IO.getNumHeartbeats
        let hbDelta := hbEnd - hbStart
        let kUnits := hbDelta / 1000
        let cost := computeCostX10 steps 0 false kUnits
        return some { tacticSyntax := tacName, heartbeats := hbDelta, costX10 := cost }
      else
        return none
    catch _ =>
      return none

/-- Bounded depth-$D$ ($D \le 3$) in-kernel `withoutModifyingState` Best-First Search. -/
def tryBfsCandidateClosers (feats : GoalFeatures) : TacticM (Array (CandidateResult × TSyntax `tactic)) := do
  let mut bfsCandidates : List (Nat × String × TacticM (TSyntax `tactic)) := [
    (2, "intros; alt_proof", `(tactic| (intros; alt_proof))),
    (2, "constructor <;> alt_proof", `(tactic| (constructor <;> alt_proof)))
  ]
  if feats.hasNegOrContra then
    bfsCandidates := bfsCandidates ++ [
      (2, "contra_direct", `(tactic| contra_direct)),
      (2, "push Not; alt_proof", `(tactic| (push Not; alt_proof))),
      (3, "intros; push Not; alt_proof", `(tactic| (intros; push Not; alt_proof)))
    ]
  if feats.hasFinsetSum then
    bfsCandidates := bfsCandidates ++ [
      (2, "intros; sum_congr_ring", `(tactic| (intros; sum_congr_ring))),
      (2, "intros; calc_ring_sum", `(tactic| (intros; calc_ring_sum))),
      (2, "intros; finset_mono", `(tactic| (intros; finset_mono))),
      (2, "intros; finset_nonneg", `(tactic| (intros; finset_nonneg)))
    ]
  bfsCandidates := bfsCandidates ++ [
    (2, "norm_cast; alt_proof", `(tactic| (norm_cast; alt_proof))),
    (2, "push_cast; ring", `(tactic| (push_cast; ring))),
    (2, "field_simp; ring", `(tactic| (field_simp; ring))),
    (3, "intros; constructor <;> alt_proof", `(tactic| (intros; constructor <;> alt_proof)))
  ]
  let mut successes : Array (CandidateResult × TSyntax `tactic) := #[]
  for (depth, name, mkStx) in bfsCandidates do
    let tacStx ← mkStx
    if let some res ← tryCandidateCloser name tacStx (steps := depth) then
      successes := successes.push (res, tacStx)
  return successes.qsort (fun (a, _) (b, _) =>
    if a.costX10 != b.costX10 then a.costX10 < b.costX10 else a.heartbeats < b.heartbeats)

/-- `bfs_elegance?`: Bounded depth-$D$ ($D \le 3$) in-kernel `withoutModifyingState` Best-First
    Search explorer. -/
syntax (name := bfsEleganceTactic) "bfs_elegance?" : tactic

/-- `elegance?`: AST-aware speculative route & tactic explorer. -/
syntax (name := eleganceTactic) "elegance?" : tactic

@[tactic eleganceTactic, tactic bfsEleganceTactic]
def evalElegance : Tactic := fun stx =>
  withTheReader Core.Context ({ · with maxHeartbeats := 0 }) do
    let goal ← getMainGoal
    let target ← instantiateMVars (← goal.getType)
    let targetStr := toString (← ppExpr target)
    let feats ← extractGoalFeatures goal
    let relRoutes := filterRelevantRoutes feats
    logInfo m!"[AltProof.elegance?] Active Goal: {targetStr}"
    logInfo m!"[AltProof.elegance?] AST Features: finsetSum={feats.hasFinsetSum}, abs={feats.hasAbs}, iteDecide={feats.hasIteOrDecide}, natInt={feats.hasNatArith}, bitVec={feats.hasBitVec}, eq={feats.hasEquality}, neg={feats.hasNegOrContra}"
    logInfo m!"[AltProof.elegance?] Relevant Routes ({relRoutes.length}/{routeTable.length}):"
    for r in relRoutes do
      logInfo m!"  * [{r.family}] {r.id}: {r.rewriteHint} ({r.costHint})"

    let runBoundedProbe (name : String) (tacStx : Syntax) (steps : Nat := 1) : TacticM (Option CandidateResult) :=
      withTheReader Core.Context ({ · with maxHeartbeats := 200000000 }) do
        tryCandidateCloser name tacStx (steps := steps)

    let bitVecCandidates : List (String × TacticM (TSyntax `tactic)) :=
      if feats.hasBitVec then [("bv_decide", `(tactic| bv_decide))] else []
    let eqCandidates : List (String × TacticM (TSyntax `tactic)) :=
      if feats.hasEquality then [("eqsat_rw", `(tactic| eqsat_rw))] else []
    let candidates : List (String × TacticM (TSyntax `tactic)) := bitVecCandidates ++ [
      ("rfl", `(tactic| rfl)),
      ("assumption", `(tactic| assumption)),
      ("kernel_decide", `(tactic| kernel_decide)),
      ("grind_close", `(tactic| grind_close)),
      ("simp_all", `(tactic| (simp_all; done))),
      ("norm_cast", `(tactic| (norm_cast; done))),
      ("backchain", `(tactic| backchain)),
      ("contra_direct", `(tactic| contra_direct)),
      ("decide", `(tactic| decide)),
      ("omega", `(tactic| omega)),
      ("ring", `(tactic| ring))
    ] ++ eqCandidates ++ [
      ("sum_congr_ring", `(tactic| sum_congr_ring)),
      ("calc_ring_sum", `(tactic| calc_ring_sum)),
      ("finset_nonneg", `(tactic| finset_nonneg)),
      ("finset_mono", `(tactic| finset_mono)),
      ("convex_comb", `(tactic| convex_comb)),
      ("markov_row_sum", `(tactic| markov_row_sum)),
      ("matrix_pos", `(tactic| matrix_pos)),
      ("sup_norm_scale", `(tactic| sup_norm_scale)),
      ("deriv_quot_ring", `(tactic| deriv_quot_ring)),
      ("gcongr_pos", `(tactic| gcongr_pos)),
      ("positivity", `(tactic| positivity)),
      ("linarith", `(tactic| linarith)),
      ("nlinarith", `(tactic| nlinarith)),
      ("norm_num", `(tactic| norm_num)),
      ("aesop", `(tactic| aesop))
    ]
    let mut successes : Array (CandidateResult × TSyntax `tactic) := #[]
    for (name, mkStx) in candidates do
      let tacStx ← mkStx
      if let some res ← runBoundedProbe name tacStx (steps := 1) then
        successes := successes.push (res, tacStx)

    let sorted := successes.qsort (fun (a, _) (b, _) =>
      if a.costX10 != b.costX10 then a.costX10 < b.costX10 else a.heartbeats < b.heartbeats)

    if h : 0 < sorted.size then
      let (best, bestStx) := sorted[0]
      logInfo m!"[AltProof.elegance?] Speculative Closers ({sorted.size} succeeded): best = `{best.tacticSyntax}` (costX10={best.costX10}, heartbeats={best.heartbeats})"
      for (c, _) in sorted do
        logInfo m!"  + `{c.tacticSyntax}`: heartbeats={c.heartbeats}, costX10={c.costX10}"
      Tactic.TryThis.addSuggestion stx bestStx (origSpan? := some stx)
    else
      let bfsSorted ← withTheReader Core.Context ({ · with maxHeartbeats := 400000000 }) do
        tryBfsCandidateClosers feats
      if hBfs : 0 < bfsSorted.size then
        let (bestBfs, bestBfsStx) := bfsSorted[0]
        logInfo m!"[AltProof.elegance?] Depth<=3 In-Kernel BFS Closers ({bfsSorted.size} succeeded): best = `{bestBfs.tacticSyntax}` (costX10={bestBfs.costX10}, heartbeats={bestBfs.heartbeats})"
        for (c, _) in bfsSorted do
          logInfo m!"  + [BFS] `{c.tacticSyntax}`: heartbeats={c.heartbeats}, costX10={c.costX10}"
        Tactic.TryThis.addSuggestion stx bestBfsStx (origSpan? := some stx)
      else
        logInfo m!"[AltProof.elegance?] Goal requires multi-step decomposition (0 single-step or depth<=3 BFS closers succeeded)."

end AltProof.Tactics

namespace AltProof

export AltProof.Tactics (
  Route
  routeTable
  CostWeights
  computeCostX10
  TwoAxisScore
  routesToJson
  GoalFeatures
  exprContainsConst
  extractExprFeatures
  extractGoalFeatures
  filterRelevantRoutes
  EqSatRule
  EqSatNode
  saturateEquality
  evalEqsatRw
  evalClosedNatExpr
  preunfoldExprWith
  buildUnrolledLoop
  specializePointwiseHyps
  evalFinsetNonneg
  evalFinsetMono
  unpackContextAndHyps
  instantiateLocalForallEqsAndBounds
  evalConvexComb
  evalMarkovRowSum
  evalMatrixPos
  sup'_const_mul_of_nonneg
  fin_card_filter_Ico
  natAbs_le_div_of_cast_abs_le
  zero_sum_vecMul_l1_le_of_entry_floor
  CandidateResult
  tryCandidateCloser
  tryBfsCandidateClosers
  evalElegance
)

end AltProof
