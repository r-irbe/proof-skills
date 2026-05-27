---
name: ai-agentic-evolving
description: |
  USE FOR: Agentic AI systems, multi-agent coordination, evolving agents, agent lifecycle management, emergent behavior, and trust dynamics in autonomous systems. Use for reasoning about agent architectures, communication protocols, coalition formation, reputation systems, and the mathematical foundations of the project's agentic safety and multi-agent trust formalization.
  DO NOT USE FOR: formal verification of those AI systems (use @lean-ai-formalization); high-stakes / verifiable AI mode (use @ai-high-stakes-verifiable); causal/deontic reasoning (use @ai-causal-deontic).
  TRIGGERS: agentic AI, multi-agent, evolving agent, agent lifecycle, emergent behavior, trust dynamics, autonomous system.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-ai-formalization', 'skill:ai-high-stakes-verifiable', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/ai-agentic-evolving/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Agentic & Evolving AI Systems

Mathematical and architectural foundations for autonomous agents, multi-agent systems, evolving capabilities, and the trust/safety dynamics formalized in the project.


## Routing

- **USE FOR:** Agentic AI systems, multi-agent coordination, evolving agents, agent lifecycle management, emergent behavior, and trust dynamics in autonomous systems. Use for reasoning about agent architectures, communication protocols, coalition formation, reputation systems, and the mathematical foundations of the project's agentic safety and multi-agent trust formalization.
- **DO NOT USE FOR:** formal verification of those AI systems (use @lean-ai-formalization); high-stakes / verifiable AI mode (use @ai-high-stakes-verifiable); causal/deontic reasoning (use @ai-causal-deontic).
- **TRIGGERS:** agentic AI, multi-agent, evolving agent, agent lifecycle, emergent behavior, trust dynamics, autonomous system.

## Workflow

1. Confirm the question / task is in scope by checking the **USE FOR** clause above; if any of the **DO NOT USE FOR** redirects apply, hand off and stop.
2. Consult the body of this skill (the existing Parts below) for the domain content; pick the smallest relevant section.
3. Execute the section's procedure; emit an output suitable for the listed successor skill(s). Belief floor: 0.90 before publishing.
4. On handoff, attach: scope, key findings, recommended next-skill call. Leave a Zettel breadcrumb when permanent.

## Recovery & STOP

- STOP if the task hits a topic redirected by **DO NOT USE FOR** — hand off to that skill rather than expanding scope here.
- STOP if belief is below 0.90 on a key claim — request HITL or escalate to `@lean-research` for evidence widening.
- STOP if the domain content below is insufficient for the question — log the gap as a research request and hand off to `@research-council` (or `@lean-research` for a single question).

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-ai-formalization`, `skill:ai-high-stakes-verifiable`, `skill:lean-zettelkasten`.

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
