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

---

## Merged Domain Companion: `lean-ai-formalization` (Unified into `@lean-ai-formalization`)

# Agentic & Evolving AI Systems

Mathematical and architectural foundations for autonomous agents, multi-agent systems, evolving capabilities, and formally verified trust/safety dynamics.

---

## Routing

- **USE FOR:** Agentic AI systems, multi-agent coordination, evolving agents, agent lifecycle management, emergent behavior, and trust dynamics in
  autonomous systems. Use for reasoning about agent architectures, communication protocols, coalition formation, reputation systems, and the mathematical
  foundations of agentic safety and multi-agent trust formalization.
- **DO NOT USE FOR:** formal verification of those AI systems (use @lean-ai-formalization); high-stakes / verifiable AI mode (use
  @lean-ai-formalization); causal/deontic reasoning (use @lean-causal-reasoning).
- **TRIGGERS:** agentic AI, multi-agent, evolving agent, agent lifecycle, emergent behavior, trust dynamics, autonomous system.

## Workflow

1. Frame the system: how many agents, what each agent optimises for, what coordination signal exists, and which lifecycle phase (spawn / coordinate /
   evolve / retire) the question is about.
2. Pick the matching theoretical lens from the body — emergence, multi-agent game theory, mechanism design, evolutionary dynamics, or trust dynamics.
3. Run the reasoning at the methodological level; do not attempt formal proofs here. Belief floor 0.90 before publishing.
4. Hand off: to `@lean-ai-formalization` if a property needs Lean proof, to `@lean-ai-formalization` if the agents are safety-critical, to
   `@lean-zettelkasten` for the durable note.

## Recovery & STOP

- STOP if the question is about formal AI verification rather than agentic dynamics — hand to `@lean-ai-formalization`.
- STOP if the system collapses to single-agent — switch to whichever non-agentic AI skill matches (e.g., `@lean-knowledge-formalization` for KR,
  `@lean-knowledge-formalization` for reasoning).
- STOP if emergence analysis would require empirical simulation rather than methodological reasoning — escalate to `@research-council`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-ai-formalization`, `skill:lean-ai-formalization`, `skill:lean-zettelkasten`.

---

## Detailed reference

Full content for `lean-ai-formalization` lives in
[`references/lean-ai-formalization-handbook.md`](../../references/lean-ai-formalization-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Agent Architectures |
| Part 2 | Multi-Agent Coordination |
| Part 3 | Evolving Agents |
| Part 4 | Safety in Agentic Systems |
| Part 5 | Reputation & Trust Systems |
| Part 6 | Connection to Project Lean Modules |
| Part 7 | Research Frontiers |

---

## See also

- [`../../references/lean-ai-formalization-handbook.md`](../../references/lean-ai-formalization-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-ai-formalization/SKILL.md`](../lean-ai-formalization/SKILL.md) — Successor
- [`../lean-ai-formalization/SKILL.md`](../lean-ai-formalization/SKILL.md) — Successor
- [`../lean-zettelkasten/SKILL.md`](../lean-zettelkasten/SKILL.md) — Successor

# Ai Agentic Evolving Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-ai-formalization/SKILL.md`](../skills/lean-ai-formalization/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Agent Architectures

### 1.1 Agent Taxonomy (Russell & Norvig)

| Type | Description | Project Mapping |
|---|---|---|
| Simple reflex | Condition-action rules | Quality gate decisions |
| Model-based reflex | Internal state + world model | Phase classification |
| Goal-based | Plan to achieve goals | Pipeline optimization |
| Utility-based | Maximize expected utility | Reinforcement learning governance |
| Learning | Improve from experience | Nested learning hierarchy |

### 1.2 BDI Architecture (Belief-Desire-Intention)

- **Beliefs**: Agent's model of the world (knowledge state)
- **Desires**: Agent's goals (quality improvement, safety)
- **Intentions**: Agent's committed plans (governance actions)

Formal semantics via modal logic:
- $B_i \phi$: Agent $i$ believes $\phi$
- $D_i \phi$: Agent $i$ desires $\phi$
- $I_i \phi$: Agent $i$ intends $\phi$
- Axioms: $I_i \phi \implies B_i \phi$ (intention requires belief)

### 1.3 Reactive Architectures

- **Subsumption**: Layered behavior with priority (Brooks)
- **Potential fields**: Gradient-based navigation
- **Stigmergy**: Indirect communication through environment
- **Project relevance**: Quality gates as reactive safety layers

---

## Part 2 — Multi-Agent Coordination

### 2.1 Communication Protocols

| Protocol | Semantics | Trust Implication |
|---|---|---|
| FIPA-ACL | Speech acts (inform, request, propose) | Messages carry performative force |
| Contract Net | Task allocation via bidding | Trust through repeated interaction |
| Auction | Resource allocation | Incentive-compatible mechanisms |
| Voting | Collective decision | Majority/supermajority rules |
| Consensus | Agreement protocol | Byzantine fault tolerance |

### 2.2 Coalition Formation

**Core (cooperative game theory):**
- Grand coalition value: $v(N)$
- Shapley value: Fair allocation based on marginal contributions
- Stability: No coalition $S$ can improve for all members

**Project formalization (AgenticSafety.lean):**
```
MultiAgentTrust (N : ℕ) — N-agent trust vector
trustConsensusDistance — distance to consensus
trust_consensus_at_target — convergence to shared trust level
```

### 2.3 Emergence & Self-Organization

| Phenomenon | Mechanism | Project Analog |
|---|---|---|
| Swarm intelligence | Local rules → global behavior | Pipeline composition |
| Stigmergy | Environmental signaling | Knowledge graph as shared state |
| Phase transitions | Critical mass effects | Regime classification boundaries |
| Attractor dynamics | Convergent collective behavior | Trust equilibrium |

---

## Part 3 — Evolving Agents

### 3.1 Agent Evolution Model

```
Agent lifecycle:
  BIRTH → LEARNING → COMPETENT → SPECIALIZING → EVOLVING → RETIREMENT

At each stage:
  - Capabilities change (expand or contract)
  - Trust must be re-established after capability change
  - Safety envelope must be re-verified
```

### 3.2 Capability Evolution

| Evolution Type | Formal Model | Verification Challenge |
|---|---|---|
| Skill acquisition | Expanding action space | Safety envelope re-check |
| Knowledge update | Belief revision | Consistency maintenance |
| Goal revision | Utility function change | Alignment preservation |
| Communication evolution | Protocol upgrade | Backward compatibility |
| Self-modification | Meta-level changes | Halting problem / undecidability |

### 3.3 Trust Under Evolution

When an agent evolves, trust dynamics change:
- **Trust reset**: After major capability change, trust returns to prior
- **Trust transfer**: New capability inherits partial trust from similar capabilities
- **Trust verification**: Formal proof that evolved agent still satisfies safety invariants

Project formalization:
```
stable_regime_trust_bound — trust bounded in stable regime
fast_trust_converges_faster — higher adaptation → faster convergence
trust_forms_lasalle_system — trust dynamics as Lyapunov system
```

### 3.4 Open-Ended Evolution

The hardest problem: agents that evolve in unpredictable ways.

**Formal challenges:**
- No fixed specification to verify against
- Safety properties must be preserved under unknown future changes
- Need "meta-safety" — safety invariants that hold regardless of evolution path

**Project approach:**
- Lyapunov barriers: Safety envelope that contracts but never breaks
- Nested learning: Higher levels constrain lower-level evolution
- Trust as sufficient statistic: Single measure that captures agent reliability

---

## Part 4 — Safety in Agentic Systems

### 4.1 Safety Properties

| Property | Formal | Project Module |
|---|---|---|
| Alignment | Agent's utility aligns with principal's | AlignedReward (Tactics.lean) |
| Corrigibility | Agent allows correction/shutdown | Safety envelope constraint |
| Non-deception | Agent reports truthfully | Trust dynamics |
| Non-manipulation | Agent doesn't exploit principal | Game-theoretic formulation |
| Containment | Agent actions bounded | SafetyEnvelope (AgenticSafety.lean) |

### 4.2 Multi-Agent Safety

**Compositional safety:**
- Individual safety ⟹ collective safety? (Not always!)
- Need: compositional verification methods

**Project formalization:**
```
envelope_monotone_conjunction — conjunction of safe envelopes is safe
action_preserves_envelope — safe actions stay in envelope
MultiAgentTrust — trust vector for N agents
```

### 4.3 Formal Verification Approaches

| Approach | What it Proves | Scalability |
|---|---|---|
| Model checking | Temporal logic properties on finite models | Exponential in states |
| Theorem proving (Lean) | Universal properties by proof | Human-guided |
| Runtime verification | Properties hold on observed traces | Online but incomplete |
| Shielding | Safety filter on output actions | Real-time |
| Abstract interpretation | Sound overapproximation of behaviors | Automatic but imprecise |

---

## Part 5 — Reputation & Trust Systems

### 5.1 Trust Models

| Model | Basis | Project Connection |
|---|---|---|
| Direct | Personal interaction history | Trust simplex dynamics |
| Reputation | Aggregated community assessment | Multi-agent trust consensus |
| Credential | Verified capabilities | Safety envelope certification |
| Institutional | Backed by organization | Governance hierarchy |
| Computational | Algorithmic verification | Lean proof as perfect trust |

### 5.2 Trust Dynamics Mathematics

**Trust update (Project model):**
- Trust $\tau \in [0,1]$ — scalar per-capability trust
- Update: $\tau_{t+1} = (1-\alpha)\tau_t + \alpha \cdot \text{observation}$
- Convergence: exponential with rate $\alpha$
- Multi-agent consensus: $\tau_i \to \bar{\tau}$ (average)

**Formal properties (proven in AgenticSafety.lean):**
- Trust is Lyapunov-stable (trust_forms_lasalle_system)
- Trust converges to target (trust_consensus_at_target)
- Higher learning rate → faster convergence (fast_trust_converges_faster)

---

## Part 6 — Connection to Project Lean Modules

| Module | Agentic Aspect |
|---|---|
| AgenticSafety.lean | Multi-agent trust, safety envelopes, trust adaptation |
| ReinforcementLearning.lean | MDP, safe exploration, governance convergence |
| LyapunovStability.lean | Governance Lyapunov, multi-scale stability |
| Tactics.lean | ProjectHierarchy, AlignedReward, nested learning |
| StochasticCCV.lean | Stochastic trust dynamics on simplex |

---

## Part 7 — Research Frontiers

### 7.1 Open Problems

| Problem | Status | Impact |
|---|---|---|
| Formal alignment verification | Early research | Provably aligned agents |
| Compositional multi-agent safety | Active research | Scalable safety proofs |
| Trust under distribution shift | Partially formalized | Robust trust dynamics |
| Open-ended safe evolution | Open problem | The holy grail |
| Emergent behavior prediction | Theoretically hard | Early warning systems |

### 7.2 Epistemic Mapping

| KK | KU | UU |
|---|---|---|
| Single-agent Lyapunov safety | Multi-agent compositional safety proof | Emergent behavior from composition |
| Trust convergence bounds | Trust under adversarial agents | Trust gaming strategies |
| Fixed-capability safety | Evolving-capability safety | Self-modifying agent safety |

---

## Merged Domain Companion: `lean-ai-formalization` (Unified into `@lean-ai-formalization`)

# High-Stakes & Formally Verifiable AI

Mathematical frameworks for AI systems where correctness, safety, and auditability are non-negotiable.

---

## Routing

- **USE FOR:** Formally verifiable AI, high-stakes AI systems, safety-critical deployment, certification, and regulatory compliance. Use for reasoning
  about AI systems that must be provably correct, auditable, or certifiable — medical AI, autonomous vehicles, legal decision support,
  military/intelligence systems, and mathematically rigorous AI governance.
- **DO NOT USE FOR:** formal verification proofs in Lean (use @lean-ai-formalization); agentic AI dynamics (use @lean-ai-formalization); causal/deontic
  reasoning (use @lean-causal-reasoning).
- **TRIGGERS:** high stakes, verifiable AI, safety critical, certification, regulatory compliance, AI assurance.

## Workflow

1. Identify the verification class: certification (regulatory), assurance case (engineering), or formal property (mathematical).
2. Pick the matching framework from the body (ISO 21448, ASIL, formal-property catalog).
3. Produce the verification artifact appropriate for the class — assurance argument, requirement decomposition, or property statement ready for
   `@lean-ai-formalization`.
4. Hand off: to `@lean-ai-formalization` for the proof, to `@applied-data-information-security` for security-specific properties, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the property is informally argued but needs a Lean proof — hand directly to `@lean-ai-formalization`.
- STOP if the system is agentic/emergent — delegate dynamics modelling to `@lean-ai-formalization` first.
- STOP if the certification target is jurisdiction-specific and not in the body — escalate to `@applied-legal-reasoning`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-ai-formalization`, `skill:lean-security-formalization`, `skill:applied-data-information-security`.

---

## Detailed reference

Full content for `lean-ai-formalization` lives in
[`references/lean-ai-formalization-handbook.md`](../../references/lean-ai-formalization-handbook.md).
Load that file when the skill is convened; the SKILL.md only carries
the dispatch contract and the parts index.

| Section | Topic |
|---|---|
| Part 1 | Verification Hierarchy |
| Part 2 | Safety Standards & Certification |
| Part 3 | Formal Safety Analysis |
| Part 4 | Provably Robust AI |
| Part 5 | Decision Support in High-Stakes Domains |
| Part 6 | Connection to Project Lean Modules |
| Part 7 | Research Directions |

---

## See also

- [`../../references/lean-ai-formalization-handbook.md`](../../references/lean-ai-formalization-handbook.md) — Full handbook (extracted from this skill)
- [`../lean-ai-formalization/SKILL.md`](../lean-ai-formalization/SKILL.md) — Successor
- [`../lean-security-formalization/SKILL.md`](../lean-security-formalization/SKILL.md) — Successor
- [`../applied-data-information-security/SKILL.md`](../applied-data-information-security/SKILL.md) — Successor

# Ai High Stakes Verifiable Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-ai-formalization/SKILL.md`](../skills/lean-ai-formalization/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Verification Hierarchy

### 1.1 Levels of Assurance

| Level | Assurance | Method | Cost | Project Analog |
|---|---|---|---|---|
| 0 | None | Trust the developer | Low | No gates |
| 1 | Testing | Test cases | Medium | Unit tests |
| 2 | Static analysis | Automated checking | Medium | Enforcement scripts |
| 3 | Model checking | Exhaustive finite-state | High | `decide` proofs |
| 4 | Theorem proving | Universal mathematical proof | Very high | Lean 4 proofs |
| 5 | Certified compilation | Proof carried to runtime | Extreme | Future work |

### 1.2 What Can Be Formally Verified?

| Property Type | Verifiable? | Method | Example |
|---|---|---|---|
| Type safety | Yes | Type system | Lean kernel checking |
| Functional correctness | Yes (with spec) | Theorem proving | Gate monotonicity |
| Termination | Semi-decidable | Well-founded recursion | Lean's termination checker |
| Safety invariants | Yes | Inductive invariants | Safety envelope preservation |
| Liveness | Yes (for finite) | Temporal logic | Eventually converges |
| Fairness | Partially | Probabilistic proofs | Unbiased trust allocation |
| Alignment | Research frontier | Utility alignment proofs | AlignedReward in Tactics.lean |

### 1.3 What Cannot Be Formally Verified?

- **Specification correctness**: Is the spec what we actually want? (faithfulness gap)
- **Environmental assumptions**: Does the environment match our model?
- **Distributional robustness**: Will it work on data unlike training data?
- **Emergent properties**: Properties arising from composition, not design

→ These are precisely where the Review Council (Φ member) and epistemic mapping provide value.

---

## Part 2 — Safety Standards & Certification

### 2.1 Relevant Standards

| Standard | Domain | Key Requirement | Formalization Relevance |
|---|---|---|---|
| DO-178C | Aviation software | Verification objectives per criticality level | Lean proofs as verification evidence |
| ISO 26262 | Automotive | ASIL levels (A-D), safety goals | Safety envelope as ASIL artifact |
| IEC 61508 | Industrial | SIL levels (1-4), safety functions | Quantitative safety metrics |
| ISO/IEC 42001 | AI management | AI risk assessment, governance | Project framework as compliance tool |
| EU AI Act | Regulatory | Risk categories, conformity assessment | Quality gates as compliance gates |
| NIST AI RMF | US framework | Govern, Map, Measure, Manage | Maps to Project phases |

### 2.2 Project as Compliance Framework

```
EU AI Act category    →  Project mapping
───────────────────────────────────────
Unacceptable risk     →  Safety envelope FORBIDS
High risk             →  Full Project pipeline + Lean verification
Limited risk          →  Project with reduced gate thresholds  
Minimal risk          →  Light Project monitoring only
```

### 2.3 Certification Evidence from Lean

Lean proofs produce certification artifacts:
- **Machine-checked proofs** — independent of developer trust
- **Axiom audit** — what foundational assumptions are used
- **Coverage matrix** — which claims have been verified
- **Review records** — council review documentation

---

## Part 3 — Formal Safety Analysis

### 3.1 Hazard Analysis Methods

| Method | Description | Formalization Potential |
|---|---|---|
| FMEA | Failure modes and effects | Enumerate failure states in Lean |
| FTA | Fault tree analysis | Boolean algebra proofs |
| STPA | Systems-theoretic process analysis | Control structure verification |
| HAZOP | Deviation analysis | Property negation testing |

### 3.2 Safety Cases

A safety case is a structured argument that a system is safe.

**GSN (Goal Structuring Notation):**
```
Top claim: "System is acceptably safe"
  └─ Strategy: "Argument over identified hazards"
      ├─ Sub-claim: "Hazard H1 is mitigated"
      │   └─ Evidence: Lean proof of safety_envelope_preserved
      ├─ Sub-claim: "Hazard H2 is mitigated"
      │   └─ Evidence: Lean proof of trust_convergence_bound
      └─ Sub-claim: "All hazards identified"
          └─ Evidence: Epistemic mapping shows no UU in safety domain
```

### 3.3 Assurance Argument Patterns

| Pattern | Description | Project Implementation |
|---|---|---|
| Monotonic safety | Safety always increases with quality | Gate monotonicity proofs |
| Bounded degradation | Performance degrades gracefully | Lyapunov bounds |
| Fail-safe | System enters safe state on failure | Safety envelope default |
| Defense in depth | Multiple independent safety layers | Nested learning hierarchy |

---

## Part 4 — Provably Robust AI

### 4.1 Adversarial Robustness

- **$\epsilon$-ball robustness**: $\forall x' \in B(x, \epsilon): f(x') = f(x)$
- **Certified robustness**: Provable bound on maximum perturbation
- **Randomized smoothing**: Probabilistic robustness certificate

### 4.2 Distributional Robustness

- **Worst-case over uncertainty set**: $\min_\theta \max_{P \in \mathcal{P}} \mathbb{E}_P[\ell(\theta)]$
- **Wasserstein balls**: Robustness over distributions within Wasserstein distance
- **Project**: OKD dynamics robust under perturbation of transition matrix

### 4.3 Causal Robustness

-  **Invariant prediction**: Properties stable under interventions
- **Transportability**: Results transfer across environments
- **Project**: Causal DAG formalization ensures structural invariance

---

## Part 5 — Decision Support in High-Stakes Domains

### 5.1 Medical AI

| Requirement | Verification Method |
|---|---|
| Diagnostic accuracy | Statistical validation + formal bounds |
| Explanation quality | Causal reasoning formalization |
| Bias absence | Fairness proofs on decision boundary |
| Privacy preservation | Information-theoretic bounds |

### 5.2 Legal Decision Support

| Requirement | Verification Method |
|---|---|
| Rule application correctness | Deontic logic formalization |
| Precedent consistency | Knowledge graph reasoning |
| Procedural fairness | Access control formalization |
| Transparency | Provenance chain verification |

### 5.3 Intelligence Analysis

| Requirement | Verification Method |
|---|---|
| Evidence chain integrity | Provenance DAG verification |
| Hypothesis consistency | Satisfiability checking |
| Bias mitigation | Epistemic mapping (UU detection) |
| Confidence calibration | Probabilistic bounds |

---

## Part 6 — Connection to Project Lean Modules

| Project Module | High-Stakes Aspect |
|---|---|
| QualityGates.lean | Compliance gates with formal thresholds |
| AgenticSafety.lean | Safety envelopes, trust certification |
| ProvenanceChain.lean | Audit trail, evidence chain |
| LyapunovStability.lean | Stability certificates |
| ReinforcementLearning.lean | Bounded regret, safe exploration |
| All modules | Zero sorry = complete verification |

---

## Part 7 — Research Directions

### 7.1 Open Problems

| Problem | Impact | Approach |
|---|---|---|
| Specification completeness | Are we verifying the right thing? | Epistemic mapping + council review |
| Runtime monitoring | Online verification | Lean-verified monitors |
| Continuous certification | Re-certify after updates | RETRO audit protocol |
| Multi-system composition | Verified subsystems → verified system? | Compositional verification |

### 7.2 Epistemic Mapping

| KK | KU | UU |
|---|---|---|
| Gate monotonicity proven | Full FMEA formalization | Novel failure modes from composition |
| Axiom cleanliness | Certified compilation pipeline | Runtime verification gaps |
| Safety envelope algebra | Regulatory mapping completeness | Cross-jurisdictional requirements |

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Typeclass / Lemma | Proof Template |
| :--- | :--- | :--- |
| `SafetyInv (step state action)` | Inductive safety barrier | `unfold SafetyInv step; omega` (or `linarith`) |
| `Simplex3 p q r` (`p + q + r = 100`) | Scaled-integer simplex invariant | `rcases h with ⟨hp, hq, hr, hsum⟩; omega` |
| Escalation gate `risk ≥ threshold → route = .human` | High-stakes guard | `intro h_risk; unfold route; split_ifs <;> omega` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Formalization Intent | Lean 4 Tactic / Pattern | Notes |
| :--- | :--- | :--- |
| Prove safety invariant preserved across N agent steps | `induction n with \| zero => ... \| succ n ih => ...` | Induct on trace/horizon length |
| Falsify candidate guard threshold before proving | `lean_counterexample_search(strategy: "dense")` | Catches off-by-one boundary leaks (`<` vs `<=`) |
| Verify non-vacuity of safety contract | Construct explicit witness `example : ∃ s, SafetyInv s` | Prevents contradictory precondition bugs |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Guard proof passes trivially for all inputs | Precondition `risk > 100` is unsatisfiable on `[0, 100]` | Run `@lean-tautology-triage` and add inhabited witness theorem |
| `Nat.sub` underflow in trust-decay update | `trust - penalty` truncates at `0` | Guard with `min trust penalty` or `if penalty <= trust` + `omega` |
