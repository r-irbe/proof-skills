---
name: "lean-causal-reasoning-handbook"
description: "Unified reference handbook for @lean-causal-reasoning (Causal DAGs, Pearl Ladder, Counterfactuals, Deontic Logic & Provenance Bridges in Lean 4)."
extracted_from: "skills/lean-causal-reasoning/SKILL.md"
---

# SK-33: Lean Causal Reasoning Formalization

---

## Routing

- **USE FOR:** Formalize causal DAGs, knowledge graph quality gates, counterfactual reasoning, and provenance bridges in Lean 4. Use for causal reasoning
  structures and their integration with repository-local verification pipelines.
- **DO NOT USE FOR:** causal methodology not in Lean (use @lean-causal-reasoning); knowledge graph formalisation generally (use @lean-knowledge-formalization);
  general AI formalisation (use @lean-ai-formalization).
- **TRIGGERS:** causal DAG, counterfactual proof, provenance bridge, causal Lean, knowledge graph gate.

## Workflow

1. Identify the causal object: DAG, structural causal model, counterfactual query, provenance bridge, or knowledge-graph gate.
2. Pick the encoding pattern from the body; verify Mathlib primitives (graph, probability) at the pin.
3. Write the Lean encoding; surface identifiability + acyclicity proof obligations.
4. Hand off: to `@lean-proof-review` for review, to `@lean-knowledge-formalization` for KR integration, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is causal-methodological (not Lean) — delegate to `@lean-causal-reasoning`.
- STOP if the question is about general KR (not causal) — delegate to `@lean-knowledge-formalization`.
- STOP if Mathlib primitives are missing — escalate to `@lean-research`.

## Handoffs

- **Predecessors:** `agent:gateway`, `skill:lean-research`.
- **Successors:** `skill:lean-proof-review`, `skill:lean-knowledge-formalization`, `skill:lean-zettelkasten`.

---

## Identity

You are the **Causal Reasoning Specialist** — responsible for formalizing and extending causal/counterfactual reasoning structures in the host repository's
Lean 4 codebase. This covers knowledge-graph quality gates, causal DAG structures, and their integration with local knowledge-validation stages.

## Scope

### In scope
- Causal-link and causal-DAG encodings: interventions, counterfactuals, effects, acyclicity, and depth.
- Knowledge-graph quality gates: typed edges, confidence thresholds, graph size/min-confidence summaries, and monotonicity lemmas.
- Provenance bridges: connecting causal DAGs to repository-local provenance or audit-trail structures.
- Legal reasoning formalization: counterfactual analysis for intelligence/legal domains.

### Out of scope
- RL/MDP machinery — use lean-ai-formalization
- Lyapunov stability — use lean-nested-learning or lean-math-dynamical
- Pure set theory / foundations — use lean-math-foundations

## Key Structures

Do not assume repository-local Lean modules, tactics, or namespaces exist unless the host repository explicitly provides them. Treat the names below as
roles to instantiate against local code.

| Role | Typical type | Purpose |
|---|---|---|---|
| Causal link | structure | intervention → counterfactual → effect |
| Causal DAG | inductive / structure | node/edge tree for causal chains |
| DAG depth | def | chain depth, often comparable to provenance depth |
| Knowledge-graph edge | structure | source, target, relation type, confidence |
| Knowledge graph | def / structure | collection of typed edges |
| Graph size | def | edge or node count |
| Minimum confidence | def | minimum confidence across edges |
| Confidence lower-bound theorem | theorem | all edges ≥ τ → graph minimum ≥ τ |
| Provenance chain | inductive / structure | staged audit or evidence chain |
| Well-formedness predicate | def | DAG validity predicate |

## RALPH Loop

### R — Review
1. Build the local causal / graph / provenance modules with targeted `lake build`.
2. Check causal structures compose with provenance or audit-trail chains.
3. Verify knowledge-graph quality-gate theorems have no `sorry`.

### A — Analyze
1. Identify missing causal reasoning theorems (transitivity, d-separation)
2. Assess whether CausalDAG needs enrichment (typed edges, weights)
3. Check alignment with paper's knowledge validation requirements

### L — Lean (Implement)
1. Add causal transitivity theorem: if A→B and B→C, then causal chain A→C
2. Prove KG composition: merging two quality-gated KGs preserves the gate
3. Bridge causal-DAG depth to provenance-chain depth for unified depth bounds.

### P — Present
1. Report new theorem count
2. Document causal structures in module docstring

### H — Harvest
1. Record patterns in lean-zettelkasten
2. Update epistemic map

## Proof Patterns

### Pattern 1: KG Quality Gate
```lean
-- To prove KG minimum confidence ≥ threshold:
theorem my_kg_quality (g : List KGEdge) (τ : Nat) 
    (h : ∀ e, e ∈ g → e.confidence ≥ τ) (hne : g ≠ []) :
    KnowledgeGraph.minConfidence g ≥ τ := by
  exact kg_min_confidence_bound g τ h hne
```

### Pattern 2: Causal Chain Depth
```lean
-- Depth is always ≥ 1:
theorem depth_pos (d : CausalDAG) : d.depth ≥ 1 := by
  cases d <;> simp [CausalDAG.depth] <;> omega
```

## Dependencies

- Imports: local causal-structure and provenance/audit-trail modules, when present.
- Feeds: lean-knowledge-formalization, lean-applied-reasoning, lean-doc-requirements

---

## Merged Domain Companion: `lean-causal-reasoning` (Unified into `@lean-causal-reasoning`)

# Causal Reasoning & Deontic Logic

Formal frameworks for reasoning about causes, effects, counterfactuals, and normative obligations.

---

## Routing

- **USE FOR:** Causal reasoning, counterfactual analysis, and deontic logic for AI systems. Use for formalizing cause-effect relationships (Pearl's
  hierarchy), interventional reasoning, structural causal models, counterfactual simulation, obligation/permission/prohibition reasoning, normative
  systems, and legal/ethical rule formalization in Lean 4.
- **DO NOT USE FOR:** formalising those models in Lean (use @lean-causal-reasoning); agentic AI behaviour (use @lean-ai-formalization); commonsense reasoning
  (use @lean-knowledge-formalization).
- **TRIGGERS:** causal, counterfactual, Pearl hierarchy, deontic, obligation, permission, structural causal model.

## Workflow

1. Classify the question: causal-effect identification, counterfactual evaluation, deontic-norm modelling, or legal-deontic encoding.
2. Pick the matching framework from the body (Pearl's do-calculus, structural causal model, standard deontic logic, dyadic deontic logic).
3. Apply the framework to the concrete scenario; document identifiability conditions and norm interactions.
4. Hand off: to `@lean-causal-reasoning` for Lean encoding, to `@applied-legal-reasoning` for legal-policy mapping, to `@lean-zettelkasten`.

## Recovery & STOP

- STOP if the question is about Lean formalisation — delegate to `@lean-causal-reasoning`.
- STOP if the question is purely legal (not deontic-logic) — delegate to `@applied-legal-reasoning`.
- STOP if a causal-effect identifiability claim cannot be established from the body — escalate to `@research-council`.

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
- **Pipeline mapping**: phase transitions as "treatment" effects on quality or safety outcomes

### 2.3 Counterfactual Stability

When is a counterfactual claim robust?
- **Monotonicity**: Outcome monotonic in treatment
- **Counterfactual stability**: Small perturbations in $U$ → small perturbations in counterfactual outcome
- **Pipeline example**: phase transitions can exhibit threshold or bifurcation-like counterfactual behavior (sudden jumps)

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

### 3.2 Causal Graphs in a Verification Pipeline

```
Example causal DAG:
  Stakeholder → Requirements → Phase classification
  Phase classification → Quality thresholds → Gate decisions
  Gate decisions → Knowledge state → Phase transitions
  Phase transitions → System trajectory → Final quality
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

Common application: quality gates as I/O norms mapping observation states to action obligations.

---

## Part 5 — Normative Multi-Agent Systems

### 5.1 Norm Types

| Norm Type | Example in a verification pipeline |
|---|---|
| Regulative | "Agents SHALL pass quality gate" |
| Constitutive | "Meeting threshold counts as passing" |
| Procedural | "Review must precede approval" |
| Institutional | "Council member has assessment authority" |

### 5.2 Norm Compliance

- **Regimented**: System physically prevents violations (hard constraints)
- **Regulated**: System detects and sanctions violations (soft constraints with enforcement)
- **Example**: quality gates can be regimented while trust scores or review confidence are regulated

### 5.3 Norm Conflict Resolution

| Strategy | Description | Common approach |
|---|---|---|
| Priority ordering | Higher-priority norm wins | Safety > quality > efficiency |
| Specificity | More specific norm overrides general | Phase-specific thresholds override defaults |
| Temporal | Later norm supersedes earlier | RETRO audit can update gates |

---

## Part 6 — Host-Repository Lean Extension Points

Do not assume repository-local Lean modules, tactics, or namespaces exist unless the host repository explicitly provides them. When local modules exist,
map them by role:

| Local extension point | Causal/deontic aspect |
|---|---|
| Provenance / audit trail module | causal DAG of evidence, intervention tracking |
| Quality-gate module | deontic obligations and gate-passage requirements |
| Safety module | safety obligations and prohibited envelope violations |
| Classification module | causal model of classification → gate → transition |
| Tactic-helper module | reasoning automation for causal/deontic proofs |
| Dynamics module | causal dynamics of phase transitions |

---

## Part 7 — Epistemic Mapping

| KK | KU | UU |
|---|---|---|
| SCM theory well-established | Full do-calculus in Lean 4 | Causal reasoning under deep uncertainty |
| SDL axiomatized | I/O logic Lean formalization | Emergent norms in multi-agent systems |
| Back-door criterion proven | Automated causal discovery verification | Counterfactual stability for chaotic systems |
| Pipeline causal DAG identified | GAI causal reasoning regulation | Ethical AI as deontic system |

---
## Goal-Shape Templates (templates)

| Goal Shape | Target Mechanism | Proof Template |
| :--- | :--- | :--- |
| DAG acyclicity `¬ Reachable G u u` | Topological rank `rank u < rank v` | `intro h; have := rank_lt_of_reachable h; omega` |
| Interventional distribution `do(X := x)` | Truncated factorization / edge surgery | `unfold intervene; split_ifs <;> simp only [...]` |
| Deontic obligation `Obliged P → Permitted P` | Standard Deontic Logic (`KD` axiom) | `intro h_ob; exact kd_serial h_ob` |

## Intent-to-Tactic Phrasebook (phrasebook)

| Causal / Deontic Intent | Lean 4 Tactic / Pattern | Notes |
| :--- | :--- | :--- |
| Prove finite causal graph is a DAG without path cycles | Witness a strict topological ranking `rank : V → Nat` | Reduces graph acyclicity to `omega` on `rank u < rank v` |
| Evaluate Pearl Level-3 counterfactual in finite Structural Causal Model | `unfold counterfactual abduce intervene; decide` | Decidable on finite exogenous domains |
| Discharge provenance-chain transitivity | `Relation.TransGen.trans` | Standard transitive closure composition |

## Error-to-Fix Table (errors)

| Error / Symptom | Root Cause | Fix |
| :--- | :--- | :--- |
| Cycle induction hangs on `Reachable` | Missing acyclicity witness | Add `∀ u v, Edge u v → rank u < rank v` and induct on `rank` |
| Chiseling / contrary-to-duty paradox in deontic model | Naive `Obliged` predicate without world/state transition | Index deontic modalities by pre/post state `(s, s')` |
