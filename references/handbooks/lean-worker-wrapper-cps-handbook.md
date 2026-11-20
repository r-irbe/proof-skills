---
name: lean-worker-wrapper-cps-handbook
description: Reference handbook for GHC Core-to-Core transformations (Worker/Wrapper unboxing, Join Points, SpecConstr call-pattern specialization, and defunctionalized CPS) in Lean 4 kernel WHNF.
extracted_from: skills/lean-proof-refactor/SKILL.md
---

# GHC Core Worker/Wrapper, Join Points, SpecConstr & Defunctionalized CPS Handbook (Lean 4)

## Overview & Compiler Optimization Principles

The Glasgow Haskell Compiler (GHC) Core language represents decades of optimization theory for pure functional languages. Key transformations include:
1. **Worker/Wrapper Transformation** (Peyton Jones, Launchbury, Gill; 1991): Splits functions into an exported wrapper that unpacks arguments and an unboxed worker running in tight loops.
2. **Join Points** (Maurer, Downen, Ariola, Peyton Jones; PLDI 2017): Local tail-called continuations that never escape, preserving subterm sharing without closure allocation.
3. **SpecConstr** (Peyton Jones; 2007): Call-pattern specialization that unrolls recursive functions for known constructor shapes.
4. **Defunctionalized CPS** (Reynolds 1972, Danvy & Nielsen 2001): Replaces higher-order function closures with first-order algebraic data types.

When applied to the Lean 4 kernel, these transformations resolve major performance bottlenecks:
- Eliminates typeclass dictionary projections and structure boxing inside hot `@Nat.rec` steps.
- Preserves pointer-based DAG sharing in the kernel's `m_whnf` cache (`KERNEL-LAW-01`).
- Eliminates environment allocation and `instantiate_rev` overhead caused by loose bound variables (`KERNEL-LAW-04`).

---

## Architectural Mechanisms in Lean 4 Kernel WHNF

```
+-----------------------------------------------------------------------+
| Outer Wrapper (Public API)                                            |
| - Unpacks structures, typeclasses, and validates preconditions        |
| - Prepares monomorphic, unboxed scalar registers (< 2^63)             |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
| Inner Worker (Monomorphic Loop Core)                                  |
| - Runs purely on unboxed scalar variables via @Nat.rec                |
| - Tail-recursive accumulator passing                                  |
| - Reaches Join Points without lambda allocation                       |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
| Join Points & SpecConstr Branches                                     |
| - Factor merge points into local definitions preserving DAG sharing   |
| - Specialize state transitions for known constructor shapes           |
+-----------------------------------------------------------------------+
```

---

## Canonical Lean 4 Implementation Exemplar

```lean
set_option autoImplicit false

namespace WorkerWrapperCore

/-! ### 1. Defunctionalized Continuations -/

/-- First-order continuation token eliminating closure allocations. -/
inductive EvalCont where
  | halt : EvalCont
  | addK : Nat -> EvalCont -> EvalCont
  | mulK : Nat -> EvalCont -> EvalCont
  deriving Repr, DecidableEq

def applyCont : EvalCont -> Nat -> Nat
  | .halt, val => val
  | .addK n k, val => applyCont k (val + n)
  | .mulK n k, val => applyCont k (val * n)

/-! ### 2. Worker/Wrapper Unboxing Split -/

/-- Rich structured input argument. -/
structure Config where
  rounds : Nat
  salt   : Nat
  offset : Nat

/-- Monomorphic inner worker operating on primitive unboxed scalars. -/
def worker (rounds : Nat) (salt offset acc : Nat) : Nat :=
  @Nat.rec (fun _ => Nat -> Nat)
    (fun a => a)
    (fun _ loop a =>
      -- Join point: common update step preserved across branches
      let joinPoint := fun x => loop (x + salt)
      if a % 2 == 0 then
        joinPoint (a + offset)
      else
        joinPoint (a + offset + 1))
    rounds
    acc

/-- Outer wrapper: unpacks Config, initializes scalars, returns result. -/
@[inline] def computePipeline (cfg : Config) (initial : Nat) : Nat :=
  worker cfg.rounds cfg.salt cfg.offset initial

/-! ### 3. SpecConstr Call-Pattern Specialization -/

inductive Mode | fast | accurate

/-- Specialized loop variants eliminating runtime constructor matching. -/
def workerFast (n : Nat) (acc : Nat) : Nat :=
  @Nat.rec (fun _ => Nat) acc (fun _ a => a + 1) n

def workerAccurate (n : Nat) (acc : Nat) : Nat :=
  @Nat.rec (fun _ => Nat) acc (fun _ a => a + 2) n

@[inline] def dispatchMode (m : Mode) (n : Nat) (acc : Nat) : Nat :=
  match m with
  | .fast     => workerFast n acc
  | .accurate => workerAccurate n acc

end WorkerWrapperCore
```

---

## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| Typeclass dictionaries in tight recursor | `Worker/Wrapper Monomorphization` | `def worker (x : Nat) : Nat; @[inline] def wrapper [C] (x) := worker x` |
| Merge branch subterms duplicating AST | `Join Point Abstraction` | `let joinPt := fun acc => ...; if c then joinPt a else joinPt b` |
| Inductive constructor match in loop body | `SpecConstr Specialization` | `def workerA ...; def workerB ...; match c with \| .A => workerA \| .B => workerB` |
| Higher-order continuation closure `(a -> b) -> b` | `Defunctionalized Inductive Cont` | `inductive Cont \| halt \| step (k : Cont); def applyCont : Cont -> a -> b` |
| Non-tail-recursive tuple re-boxing | `Tail-Call Scalar Accumulator` | `@Nat.rec (fun _ => Nat -> Nat -> Nat) (fun a b => a) (fun _ loop a b => loop (a+1) b)` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Mathematical Intent | Lean 4 / Mathlib Tactic | Notes |
| :--- | :--- | :--- |
| Apply Worker/Wrapper split | `Unpack structure at entry` | Keeps inner loop free of projections, dictionaries, and boxing |
| Establish Join Point in recursor | `let joinPt := fun ...` | Retains single shared subterm node in kernel pointer cache |
| Specialize call pattern (SpecConstr) | `Split into monomorphic workers` | Eliminates inner pattern matching and branching overhead |
| Defunctionalize closure continuation | `First-order inductive dispatch` | Replaces lambda closures with token constructor matching |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Excessive `instantiate_rev` overhead in kernel | Lambda abstractions with open bound variables in loop | Lift to top-level auxiliary definition or defunctionalize into first-order inductive type |
| Heap allocation inside recursor step | Constructor boxing `(a, b)` on each step | Unbox into separate scalar accumulator arguments in `@Nat.rec` |
| Typeclass projection cannot be reduced | Opaque dictionary in kernel | Supply explicit monomorphic instance or use Worker/Wrapper to eliminate typeclass before loop |
| Stack overflow on deep CPS reduction | Non-tail-recursive continuation chain | Convert continuation evaluator to tail-recursive accumulator loop |
