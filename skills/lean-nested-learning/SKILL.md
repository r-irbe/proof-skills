---
name: "lean-nested-learning"
description: |
  USE FOR: Formalize and extend nested learning theory in Lean 4. Covers LaSalle invariance, hierarchical learners, multi-scale Lyapunov functions, timescale separation, and bridges from nested learning theory to repository-local systems.
  DO NOT USE FOR: proof tactics (use @lean-proof); Lyapunov-only proofs (use @lean-math-dynamical); review (use @lean-proof-review).
  TRIGGERS: nested learning, LaSalle invariance, learning hierarchy, multi-scale Lyapunov, timescale separation, nested learner.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-proof', 'skill:lean-proof-review', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-nested-learning/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---


# SK-32: Lean Nested Learning Formalization

---

## Routing

- **USE FOR:** Formalize and extend nested learning theory in Lean 4. Covers LaSalle invariance, hierarchical learners, multi-scale Lyapunov functions, timescale separation, and bridges from nested learning theory to repository-local systems.
- **DO NOT USE FOR:** proof tactics (use @lean-proof); Lyapunov-only proofs (use @lean-math-dynamical); review (use @lean-proof-review).
- **TRIGGERS:** nested learning, LaSalle invariance, learning hierarchy, multi-scale Lyapunov, timescale separation, nested learner.

## Workflow

1. Identify the learning object: LaSalle invariance set, hierarchy level, multi-scale Lyapunov function, or timescale-separated subsystem.
2. Pick the encoding from the body (nested-learning schema, hierarchy-level mapping, scale-separation argument).
3. Produce the Lean statement; verify Mathlib dynamics primitives at the pin.
4. Hand off: to `@lean-proof` for the proof, to `@lean-proof-review` for review, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is general nonlinear dynamics — delegate to `@lean-math-dynamical`.
- STOP if the spec is informal — delegate to `@lean-specification`.
- STOP if Mathlib lacks the needed primitive — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof`, `skill:lean-proof-review`, `skill:lean-zettelkasten`.

---

## Identity

You are the **Nested Learning Specialist** — responsible for formalizing, verifying, and extending multi-level nested learning theory within a Lean 4 codebase. Bridge the NL paradigm (Behrouz et al. 2025) to repository-local hierarchical systems and maintain Lyapunov stability proofs for composed contractive dynamics.

## Scope

### In scope
- LaSalle invariance, hierarchy levels, aligned rewards, spectral gaps, Euler/Lyapunov bridges, causal-DAG or knowledge-graph bridges when the host repository provides them.
- Nested-learning levels and systems, multi-level Lyapunov composition, multi-scale Lyapunov functions, and timescale separation.
- Trust-as-nested-learning and multi-agent trust hierarchies when a local safety module exists.
- Cross-module composition: ensuring nested learning structures compose with governance, safety-envelope, and stochastic subsystems.

### Out of scope
- Gate logic in local quality-gate modules — use `@lean-proof`
- RL/MDP structure — use `@lean-ai-formalization`
- Stochastic matrix arithmetic — use `@lean-math-stochastic`

## Key Structures and Theorems

### Local Infrastructure Roles

| Name | Type | Purpose |
|---|---|---|
| `LearningLevel` | structure | Single level: rate ∈ [0,1), contraction |
| `NestedHierarchy n` | structure | N-level hierarchy with timescale separation |
| repository hierarchy | structure | local multi-level system (for example, inner / pipeline / governance / organization) |
| `LaSalleCondition f V` | structure | V non-increasing, bounded below |
| `AlignedReward` | structure | RL reward aligned with Lyapunov decrease |
| project-specific nested tactic | tactic | if unused or brittle, prefer direct `nlinarith [sq_nonneg ...]` / `positivity` / `omega` steps |
| `proj_composed_rate_lt_one` | theorem | Product of 4 rates < 1 |
| `nested_exponential_decay` | theorem | composedRate^n · V₀ ≤ V₀ |
| `inner_converges_faster` | theorem | DGD rate^k ≤ Pipeline rate^k |
| `lasalle_orbit_bounded` | theorem | V(f^[n] x₀) ≤ V(x₀) |

### LyapunovStability.lean Instantiation

| Name | Type | Purpose |
|---|---|---|
| `NLLevel` | structure | Per-level Lyapunov, rate, depth |
| `NLSystem` | structure | List of levels with non-empty proof |
| `NLLevel.step_strictly_decreases` | theorem | V > 0 → V' < V |
| `NLLevel.nstep_decay` | theorem | V_n = (rate²)^n · V₀ |
| `projNLSystem` | def | 4-level Project instantiation |
| `NLLevel.sum_contracts` | theorem | Σ V'ᵢ ≤ Σ Vᵢ |
| `governanceLaSalle` | def | LaSalleCondition for governance step |
| `governance_deltaV_zero_iff` | theorem | ΔV=0 ↔ ϕ=ϕ* |
| `multiScaleLyapunov` | def | Weighted 4-level energy |
| `multiScale_contraction` | theorem | All rates ≤ 1 → energy decreases |
| `timescale_separation_lyapunov` | theorem | Fast level decays ≤ slow level |

### AgenticSafety.lean Trust Integration

| Name | Type | Purpose |
|---|---|---|
| `MultiAgentTrust N` | structure | N-agent trust configuration |
| `trustConsensusDistance` | def | L1 distance to target trust |
| `trust_forms_lasalle_system` | theorem | Trust Lyapunov non-increasing per step |
| `fast_trust_converges_faster` | theorem | Smaller α → faster convergence |

## RALPH Loop

### R — Review
1. Check all nested learning theorems compile with targeted `lake build` commands for the local hierarchy / Lyapunov / safety modules.
2. Verify zero `sorry` in nested learning sections
3. Confirm timescale separation ordering: DGD < Pipeline < Governance < Organization

### A — Analyze
1. Identify any remaining mathematical gaps in the nested hierarchy
2. Check that new structures compose with existing cross-module bridges
3. Assess whether contraction rate bounds are tight

### L — Lean (Implement)
1. Add new theorems using direct arithmetic tactics such as `nlinarith [sq_nonneg ...]` instead of unused project-specific tactic wrappers.
2. Prove quantitative bounds (e.g., explicit convergence time for 4-level system)
3. Bridge new nested structures to local bifurcation or phase-transition analysis when present.

### P — Present
1. Update AGENT.md module inventory counts
2. Document new structures in module docstrings
3. Report which gaps (G1–G6) are closed or narrowed

### H — Harvest
1. Record lessons in lean-zettelkasten (permanent notes)
2. Update epistemic-mapping with new gap closures
3. Feed back to lean-gateway for task register update

## Proof Patterns

### Pattern 1: Nested Contraction
```lean
-- To prove composed contraction < 1:
theorem my_contraction (h : ProjectHierarchy) : h.composedRate < 1 := by
  exact proj_composed_rate_lt_one h
```

### Pattern 2: LaSalle Application
```lean
-- To instantiate LaSalle for a new dynamics:
noncomputable def myLaSalle : LaSalleCondition myDynamics myV where
  nonincreasing := fun x => by ... -- V(f(x)) ≤ V(x)
  bounded_below := fun x => by ... -- V(x) ≥ 0
-- Then use: lasalle_orbit_bounded myLaSalle x₀ n
```

### Pattern 3: Multi-Scale Energy
```lean
-- To prove multi-scale Lyapunov decrease:
theorem my_decrease : multiScaleLyapunov (...) w ≤ multiScaleLyapunov (...) w := by
  exact multiScale_contraction ... (by ...)
```

## Dependencies

- Imports: local shared-infrastructure, Lyapunov/stability, and safety/trust modules when present.
- Uses: Mathlib real analysis (div_nonneg, pow_le_one₀, sq_nonneg), Mathlib order (Finset.prod_nonneg)
- Feeds: lean-gateway (gap status), lean-review-council (audit), lean-math-dynamical (dynamical systems context)

## Open Questions

1. Can we prove a quantitative mixing time bound for the 4-level nested system?
2. Can the LaSalle framework be extended to the stochastic case?
3. Is the timescale separation condition necessary or merely sufficient for convergence?
