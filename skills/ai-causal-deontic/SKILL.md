---
name: ai-causal-deontic
description: |
  USE FOR: Causal reasoning, counterfactual analysis, and deontic logic for AI systems. Use for formalizing cause-effect relationships (Pearl's hierarchy), interventional reasoning, structural causal models, counterfactual simulation, obligation/permission/prohibition reasoning, normative systems, and legal/ethical rule formalization in Lean 4.
  DO NOT USE FOR: formalising those models in Lean (use @lean-causal-reasoning); agentic AI behaviour (use @ai-agentic-evolving); commonsense reasoning (use @ai-commonsense-reasoning).
  TRIGGERS: causal, counterfactual, Pearl hierarchy, deontic, obligation, permission, structural causal model.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-causal-reasoning', 'skill:lean-knowledge-formalization', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/ai-causal-deontic/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Causal Reasoning & Deontic Logic

Formal frameworks for reasoning about causes, effects, counterfactuals, and normative obligations.


## Routing

- **USE FOR:** Causal reasoning, counterfactual analysis, and deontic logic for AI systems. Use for formalizing cause-effect relationships (Pearl's hierarchy), interventional reasoning, structural causal models, counterfactual simulation, obligation/permission/prohibition reasoning, normative systems, and legal/ethical rule formalization in Lean 4.
- **DO NOT USE FOR:** formalising those models in Lean (use @lean-causal-reasoning); agentic AI behaviour (use @ai-agentic-evolving); commonsense reasoning (use @ai-commonsense-reasoning).
- **TRIGGERS:** causal, counterfactual, Pearl hierarchy, deontic, obligation, permission, structural causal model.

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
- **Successors:** `skill:lean-causal-reasoning`, `skill:lean-knowledge-formalization`, `skill:lean-zettelkasten`.

---

## Part 1 — Pearl's Causal Hierarchy

### 1.1 Three Levels of Causal Reasoning

| Level | Name | Typical Query | Operator | Formalization |
|---|---|---|---|---|
| 1 | Association | $P(y \mid x)$ | Conditioning | Standard probability |
| 2 | Intervention | $P(y \mid do(x))$ | do-calculus | Truncated factorization |
| 3 | Counterfactual | $P(y_x \mid x', y')$ | Structural equations | Twin network / abduction |

### 1.2 Structural Causal Models (SCM)

An SCM $\mathcal{M} = \langle U, V, F, P(U) \rangle$ where:
- $U$: Exogenous (background) variables
- $V$: Endogenous variables
- $F$: Structural equations $V_i = f_i(\text{pa}_i, U_i)$
- $P(U)$: Distribution over exogenous variables

**Lean formalization pattern:**
```
structure CausalModel where
  vars : Type
  exogenous : Type
  structural : vars → (vars → Prop) → exogenous → Prop
  acyclicity : WellFounded (influences structural)
```

### 1.3 do-Calculus

Three rules for identifying causal effects from observational data:

| Rule | Description | Condition |
|---|---|---|
| Rule 1 (Insertion/deletion of observations) | $P(y \mid do(x), z, w) = P(y \mid do(x), w)$ | $(Y \perp\!\!\!\perp Z \mid X, W)_{G_{\overline{X}}}$ |
| Rule 2 (Action/observation exchange) | $P(y \mid do(x), do(z), w) = P(y \mid do(x), z, w)$ | $(Y \perp\!\!\!\perp Z \mid X, W)_{G_{\overline{X}\underline{Z}}}$ |
| Rule 3 (Insertion/deletion of actions) | $P(y \mid do(x), do(z), w) = P(y \mid do(x), w)$ | $(Y \perp\!\!\!\perp Z \mid X, W)_{G_{\overline{X}\overline{Z(W)}}}$ |

### 1.4 Identifiability Criteria

| Criterion | Description | Applicability |
|---|---|---|
| Back-door | Adjust for confounders blocking back-door paths | Common, simple |
| Front-door | Mediate through intermediate variable | When no valid adjustment set |
| Instrumental variable | Exploit exogenous variation | Econometrics, natural experiments |
| General ID algorithm | Complete identification algorithm | Any semi-Markovian model |

---

## Part 2 — Counterfactual Reasoning

### 2.1 Counterfactual Computation (3 Steps)

1. **Abduction**: Given evidence, infer $P(U \mid \text{evidence})$
2. **Action**: Modify structural equations (intervention)
3. **Prediction**: Compute outcome under modified model

### 2.2 Potential Outcomes Framework

- **Rubin causal model**: $Y_i(1), Y_i(0)$ — potential outcomes under treatment/control
- **ATE**: $\mathbb{E}[Y(1) - Y(0)]$ — average treatment effect
- **CATE**: $\mathbb{E}[Y(1) - Y(0) \mid X = x]$ — conditional on covariates
- **Project mapping**: OKD phase transitions as "treatment" effects on knowledge quality

### 2.3 Counterfactual Stability

When is a counterfactual claim robust?
- **Monotonicity**: Outcome monotonic in treatment
- **Counterfactual stability**: Small perturbations in $U$ → small perturbations in counterfactual outcome
- **Project**: Phase transitions exhibit cusp-catastrophe counterfactual behavior (sudden jumps)

---

## Part 3 — Causal Discovery

### 3.1 Methods

| Method | Type | Assumptions | Output |
|---|---|---|---|
| PC algorithm | Constraint-based | Faithfulness, no latent confounders | CPDAG |
| FCI | Constraint-based | Allows latent confounders | PAG |
| GES | Score-based | BIC score, decomposable | CPDAG |
| NOTEARS | Continuous optimization | Acyclicity constraint | DAG |
| Causal transformers | Deep learning | Large observational data | DAG |

### 3.2 Causal Graphs in the project

```
Project Causal DAG (formalized in ProvenanceChain.lean):
  Stakeholder → Requirements → Phase classification
  Phase classification → Quality thresholds → Gate decisions
  Gate decisions → Knowledge state → Phase transitions
  Phase transitions → OKD trajectory → Final quality
```

---

## Part 4 — Deontic Logic

### 4.1 Standard Deontic Logic (SDL)

| Operator | Symbol | Reading | Formal |
|---|---|---|---|
| Obligation | $O(p)$ | "It ought to be that $p$" | $O(p) \equiv \neg P(\neg p)$ |
| Permission | $P(p)$ | "It is permitted that $p$" | $P(p) \equiv \neg O(\neg p)$ |
| Prohibition | $F(p)$ | "It is forbidden that $p$" | $F(p) \equiv O(\neg p)$ |

### 4.2 Paradoxes and Extensions

| Paradox | Description | Resolution |
|---|---|---|
| Ross's paradox | $O(p) \to O(p \lor q)$ — obliged to mail → obliged to mail or burn | Input/output logic |
| Contrary-to-duty | What obligations apply when one is violated? | Defeasible deontic logic |
| Free choice | $P(p \lor q)$ doesn't entail $P(p) \land P(q)$ | Bilateral norms |
| Chisholm | Nested conditional obligations conflict | Dyadic deontic logic |

### 4.3 Deontic Logic for AI Governance

| Governance Rule | Deontic Formalization |
|---|---|
| Gate must be passed before advancement | $O(\text{pass}(g_i) \to \text{before}(\text{phase}_{i+1}))$ |
| Safety envelope must be maintained | $F(\text{violate}(\text{safety\_envelope}))$ |
| Trust must converge | $O(\text{eventually}(\text{converged}(\tau)))$ |
| Provenance must be recorded | $O(\text{record}(\text{provenance}(a)))$ for all actions $a$ |

### 4.4 Input/Output Logic (Makinson & van der Torre)

```
Input/Output pairs: (a, x) meaning "given input a, output x"
Four operators: out_1 (simple), out_2 (+SI), out_3 (+CT), out_4 (+SI+CT)
Permission: negative (not forbidden) vs positive (explicitly permitted)
```

project application: Quality gates as I/O norms mapping observation states to action obligations.

---

## Part 5 — Normative Multi-Agent Systems

### 5.1 Norm Types

| Norm Type | Example in the project |
|---|---|
| Regulative | "Agents SHALL pass quality gate" |
| Constitutive | "Meeting threshold counts as passing" |
| Procedural | "Review must precede approval" |
| Institutional | "Council member has assessment authority" |

### 5.2 Norm Compliance

- **Regimented**: System physically prevents violations (hard constraints)
- **Regulated**: System detects and sanctions violations (soft constraints with enforcement)
- **Project**: Quality gates are regimented; trust scores are regulated

### 5.3 Norm Conflict Resolution

| Strategy | Description | Project approach |
|---|---|---|
| Priority ordering | Higher-priority norm wins | Safety > quality > efficiency |
| Specificity | More specific norm overrides general | Phase-specific thresholds override defaults |
| Temporal | Later norm supersedes earlier | RETRO audit can update gates |

---

## Part 6 — Connection to Project Lean Modules

| Module | Causal/Deontic Aspect |
|---|---|
| ProvenanceChain.lean | Causal DAG of evidence, intervention tracking |
| QualityGates.lean | Deontic obligations (gate passage requirements) |
| AgenticSafety.lean | Safety obligations, prohibition of envelope violation |
| PhaseClassification.lean | Causal model of classification → gate → transition |
| Tactics.lean | Reasoning automation for causal/deontic proofs |
| KnowledgePhasePortrait.lean | Causal dynamics of phase transitions |

---

## Part 7 — Epistemic Mapping

| KK | KU | UU |
|---|---|---|
| SCM theory well-established | Full do-calculus in Lean 4 | Causal reasoning under deep uncertainty |
| SDL axiomatized | I/O logic Lean formalization | Emergent norms in multi-agent systems |
| Back-door criterion proven | Automated causal discovery verification | Counterfactual stability for chaotic systems |
| Project causal DAG identified | GAI causal reasoning regulation | Ethical AI as deontic system |
