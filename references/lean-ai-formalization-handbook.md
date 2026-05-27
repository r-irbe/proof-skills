---
title: "Lean Ai Formalization Handbook"
status: "reference"
extracted_from: "skills/lean-ai-formalization/SKILL.md"
extracted_on: "2026-05-27"
scope: "Part 1 — AI Safety Properties; Part 2 — Agentic AI; Part 4 — High-Stakes AI Verification; Part 5 — Neural Network Properties; Part 6 — Multi-Agent Composition; Part 7 — Commonsense and Causal Reasoning; Part 8 — Research Council Integration"
loader_hint: "Load when @lean-ai-formalization routes here for details; not needed for the dispatch decision."
---

# Lean Ai Formalization Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-ai-formalization/SKILL.md`](../skills/lean-ai-formalization/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — AI Safety Properties

### 1.1 Property Taxonomy

| Property Class | Examples | Formalization Approach |
|---|---|---|
| **Safety** | "Never enter unsafe state" | Invariant: `∀ n, x_n ∈ SafeSet` |
| **Liveness** | "Eventually reach good state" | `∃ N, ∀ n ≥ N, x_n ∈ GoodSet` |
| **Robustness** | "Small perturbation → small change" | Continuity/Lipschitz |
| **Fairness** | "No group systematically disadvantaged" | Statistical parity bounds |
| **Transparency** | "Decision traceable to inputs" | Provenance chain completeness |
| **Alignment** | "Utility matches human preferences" | Reward shaping correctness |
| **Containment** | "Agent stays within capability bounds" | Safety envelope invariant |

### 1.2 Project Safety Formalization Patterns

```lean
-- Safety envelope: agent actions bounded by trust-derived limits
structure SafetyEnvelope where
  trustR : ℕ  -- recognition trust (×100)
  trustS : ℕ  -- structuring trust (×100)
  trustK : ℕ  -- knowledge trust (×100)
  simplex : trustR + trustS + trustK = 100
  actionBound : ℕ  -- derived from trust vector

-- Safety invariant: every action within envelope
theorem safety_invariant (env : SafetyEnvelope) (action : ℕ) 
    (h : action ≤ env.actionBound) : action ∈ SafeSet := by
  -- WIP placeholder: derive from envelope constraints
  -- In production: grind [SafetyEnvelope.simplex, SafetyEnvelope.actionBound]
  sorry

-- Composition: envelope for system of agents
-- Key: composition of safe agents may not be safe (emergence)
-- Project addresses this via trust-gated composition
```

---

## Part 2 — Agentic AI

**AgenticSafety module** — one of 12 Project modules (project total: 22,312 lines, ≥1,255 theorems, **zero sorry**)

### 2.1 Agent Models

```lean
-- Single agent
structure Agent (State Action Obs : Type) where
  policy : Obs → Action
  observe : State → Obs
  act : State → Action → State

-- Multi-agent system
structure MultiAgent (n : ℕ) (State Action Obs : Type) where
  agents : Fin n → Agent State Action Obs
  compose : (Fin n → Action) → State → State  -- joint action effect

-- Project: each pipeline stage is an agent
-- Trust vector governs agent authority
```

### 2.2 Evolving Agents

```lean
-- Agent that updates its own policy:
structure EvolvingAgent (State Action Obs Param : Type) where
  policy : Param → Obs → Action
  learn : List (Obs × Action × ℝ) → Param → Param
  -- Learning modifies the parameter space

-- Safety under evolution:
-- ∀ parameters reachable by learning, safety envelope is maintained
-- This requires: safety invariant robust to parameter perturbation
-- Project: trust contraction bounds parameter drift
```

### 2.3 Agentic AI Safety Properties

| Property | Formal Statement | Project Module |
|---|---|---|
| Trust contraction | `|t_{n+1} - t*| ≤ α|t_n - t*|`, `α < 1` | AgenticSafety |
| Envelope monotonicity | More trust → larger envelope | AgenticSafety |
| Composition safety | Join of safe envelopes is safe | AgenticSafety |
| Trust asymptotic stability | `t_n → t*` as `n → ∞` | AgenticSafety |
| Authority bounded | Agent action ≤ trust-derived bound | AgenticSafety |
| Human override | Human can always reduce trust to 0 | (Design principle) |
| Full tR/tS/tK Lyapunov contraction | `trust_multicomponent_exact` | AgenticSafety |
| Lyapunov decrease for multi-agent lists | `trustLyapunov_list_decrease` | AgenticSafety |
| L1 trust contraction | `trust_L1_exact` / `trust_L1_contraction` | AgenticSafety |

### 2.4 Tactic Priority for AI Safety Proofs

Current project codebase: 22,312 lines across 12 modules, ≥1,255 theorems, **zero sorry**.

| Priority | Tactic | Use Case |
|---|---|---|
| 1 | `grind` | Most goals — replaces omega/linarith in many cases |
| 2 | `omega` | Pure `ℕ`/`ℤ` arithmetic |
| 3 | `nlinarith` | Nonlinear real arithmetic |
| 4 | `norm_num` | Numeric computations |
| 5 | `decide` | Finite/decidable propositions |
| 6 | `field_simp` + `ring` | Field equations |

> **Deprecated:** `proj_decide`, `proj_lyapunov`, `proj_stoch`, `proj_gate` are fully removed.

### 2.5 Recent Module Additions

New sections added across modules (relevant to AI safety formalization):

| Section | Module | Content |
|---|---|---|
| §12b phase-cusp bridge | PhasePortrait | Connects phase dynamics to cusp catastrophe potential |
| §13 PhaseVelocityState | PhasePortrait | Velocity field on phase space for convergence proofs |
| §13 PipelineHealthMetrics | PipelineAdaptive | Formal health metrics for adaptive pipeline stages |
| §19 Coercivity | CuspCatastrophe | Coercivity of the cusp potential (unbounded growth away from equilibria) |
| §23 RevocationRecord | ProvenanceChain | Revocation tracking for knowledge provenance entries |
| §34 uniformTransitionQ | StochasticCCV | Uniform stochastic transition kernel for CCV Markov chain |

---

### 3.1 Reward Specification

```lean
-- Reward function must capture intended behavior:
-- R : State → Action → ℝ

-- Reward shaping: R' = R + F where F is potential-based
-- Theorem: potential-based shaping preserves optimal policy
-- (Ng et al., 1999 — formalize in Lean)

-- Project: reward = pipelineHealth (Nat-scaled composite metric)
-- Alignment: pipelineHealth correctly captures quality of externalization
```

### 3.2 Specification Gaming

```lean
-- Specification gaming: agent maximizes reward without achieving intent
-- Formal test: does the reward function have unintended optima?

-- For Project: prove that maximizing pipelineHealth requires:
-- 1. Gate passage at each stage
-- 2. Provenance completeness
-- 3. Peer validation
-- (Not just gaming a single metric)
```

### 3.3 Inverse Reward Design

```lean
-- Given observed expert behavior, infer the reward function
-- Relevant to the project's Experience stage: extracting tacit preferences
-- Formalization: IRL as constrained optimization
-- Show: recovered reward is consistent with observed behavior
```

---

## Part 4 — High-Stakes AI Verification

### 4.1 EU AI Act Compliance Properties

```lean
-- Article 9: Risk management system
-- Formalize: every AI-assisted decision has a risk assessment
-- theorem risk_managed : ∀ decision, ∃ assessment, ...

-- Article 13: Transparency
-- Formalize: every output traceable to inputs + model
-- theorem transparent : ∀ output, provenance output ≠ ∅

-- Article 14: Human oversight
-- Formalize: human can intervene at any stage
-- theorem human_override : ∀ stage, ∃ human_action, override stage human_action

-- Project: PROV-O provenance + quality gates + Consolidation-stage human review
-- directly implement these requirements
```

### 4.2 Law Enforcement Directive Properties

```lean
-- LED Article 11: Automated decisions affecting individuals
-- Formalize: every automated decision has human review
-- Project: Consolidation stage = mandatory human review
-- theorem led_compliance : ∀ decision, ∃ human_reviewer, reviewed decision human_reviewer
```

### 4.3 Formal Verification Methods

| Method | What it verifies | Lean approach |
|---|---|---|
| Invariant checking | Safety properties | Inductive invariant proof |
| Model checking | Finite-state temporal properties | Decidable + exhaustive |
| Abstract interpretation | Over-approximate reachable states | Galois connection framework |
| Deductive verification | General properties | Full Lean proof |
| Runtime monitoring | Properties during execution | (Complementary, not in Lean) |

---

## Part 5 — Neural Network Properties

### 5.1 Formalizable Properties

```lean
-- Lipschitz continuity: ‖f(x) - f(y)‖ ≤ L‖x - y‖
-- → Robustness to input perturbation
-- Lean: LipschitzWith L f

-- Monotonicity: x ≤ y → f(x) ≤ f(y)
-- → Preserves ordering of inputs
-- Lean: Monotone f

-- Boundedness: ‖f(x)‖ ≤ B for all x in domain
-- → Output containment
-- Lean: BoundedContinuousFunction or explicit bound

-- Compositional stability: layerwise contraction → global stability
-- Lean: contraction factor < 1 at each layer → geometric decay
```

### 5.2 Project AI Component Properties

| Component | Property | Verification |
|---|---|---|
| GenAI text generation | Output bounded by prompt + template | Provenance check |
| Quality gate classifier | Monotone in quality score | Prove monotonicity |
| Phase classifier | Correct thresholds | Decide on finite cases |
| Trust update rule | Contraction toward target | Contraction proof |
| Alert aggregation | Lattice properties (sup/inf) | Lattice axioms |

---

## Part 6 — Multi-Agent Composition

### 6.1 Compositional Safety

```lean
-- Assume-guarantee reasoning:
-- If agent A guarantees property P assuming property Q from environment,
-- and agent B guarantees Q assuming P,
-- then the composition satisfies both P and Q.

-- Project: each stage guarantees output quality assuming input quality
-- Pipeline composition: prove end-to-end quality
theorem pipeline_safety
    (h_each : ∀ stage, input_quality stage ≥ threshold → output_quality stage ≥ threshold)
    (h_init : input_quality Stage.E ≥ threshold) :
    ∀ stage, output_quality stage ≥ threshold := by
  -- WIP placeholder: induction on pipeline stages
  -- In production: induction stage <;> grind [h_each, h_init]
  sorry
```

### 6.2 Emergence and Interaction Effects

```lean
-- Non-compositional properties: properties that hold for individual agents
-- but not for the composition (or vice versa)

-- Project formalizes this via:
-- 1. Trust-gated interaction (agents can't exceed their authority)
-- 2. Safety envelope bounds on joint actions
-- 3. Supervisor agent (Consolidation-stage human) for emergence detection
```

---

## Part 7 — Commonsense and Causal Reasoning

### 7.1 Causal Models in Lean

```lean
-- Structural causal model: X_i = f_i(Pa(X_i), U_i)
-- where Pa(X_i) are parents in the causal DAG and U_i are noise

-- Formalization: DAG + structural equations
structure CausalModel (V : Type) (Val : V → Type) where
  dag : DAG V
  mechanism : (v : V) → (∀ w, dag.edge w v → Val w) → Val v
  -- each variable is a deterministic function of its parents
```

### 7.2 Interventions and Counterfactuals

```lean
-- do-calculus: P(Y | do(X = x)) ≠ P(Y | X = x) in general
-- Intervention: replace mechanism for X with constant x
-- Counterfactual: what would Y have been if X had been x?

-- Project: causal model of knowledge pipeline
-- Intervention: what if we bypass quality gate G2?
-- Counterfactual: what would quality have been with different prompts?
```

---

## Part 8 — Research Council Integration

Consolidated into the single canonical routing matrix:
[`references/research-council-skill-map.md`](../../references/research-council-skill-map.md)
(see the "AI formalisation" section).  When dispatching a question to
a council member, cite that table rather than restating the rows here.

---
