---
name: "lean-gateway-handbook"
description: "Reference handbook for @lean-gateway."
extracted_from: "skills/lean-gateway/SKILL.md"
---

# Lean 4 Gateway Orchestrator

The gateway is the single entry point for all Lean 4 formalization work. It coordinates the skill ecosystem, prevents context collapse, maintains all feedback loops, and monitors system health.

---

## Part 1 — Skill Registry

| ID | Skill | Scope | Primary Agent Roles |
|---|---|---|---|
| `SK-01` | `lean-proof` | Single proof | Implementer |
| `SK-02` | `lean-proof-review` | Single proof/file review | Reviewer (any council member) |
| `SK-03` | `lean-review-council` | Multi-agent council review | 5 council members + chair |
| `SK-04` | `lean-zettelkasten` | Knowledge management | Synthesizer |
| `SK-05` | `lean-specification` | Theorem/tactic specification | Specifier, Designer |
| `SK-06` | `lean-setup` | Build and toolchain | DevOps |
| `SK-07` | `lean-gateway` | Orchestration (this skill) | Gateway Orchestrator |
| `SK-08` | `lean-retroactive-audit` | Existing project audit | Auditor council |
| `SK-09` | `lean-doc-requirements` | Extract requirements from documents | Φ (Statement Oracle) + Researcher |
| `SK-10` | `lean-doc-improvement` | Update documents from Lean results | Documenter + Ω (Integration) |
| `SK-11` | `lean-research` | Research to guide spec/review/ZK | Researcher |
| `SK-12` | `lean-math-foundations` | Logic, sets, algebra, category theory | Domain expert (foundations) |
| `SK-13` | `lean-math-analysis` | Real analysis, topology, measure theory | Domain expert (analysis) |
| `SK-14` | `lean-math-dynamical` | Nonlinear dynamics, Lyapunov, catastrophe | Domain expert (dynamical systems) |
| `SK-15` | `lean-math-stochastic` | Probability, Markov, time series, ergodic | Domain expert (stochastic) |
| `SK-16` | `lean-math-optimization` | Optimization, game theory, RL theory | Domain expert (optimization) |
| `SK-17` | `lean-math-discrete` | Graphs, lattices, DAGs, knowledge graphs | Domain expert (discrete) |
| `SK-18` | `lean-ai-formalization` | AI safety, agentic, alignment, high-stakes | Domain expert (AI) |
| `SK-19` | `lean-knowledge-formalization` | Knowledge rep, symbolic AI, legal reasoning | Domain expert (knowledge) |
| `SK-20` | `lean-security-formalization` | Data/info security, access control, privacy | Domain expert (security) |
| `SK-21` | `lean-applied-reasoning` | Intelligence, strategy, investigative | Domain expert (applied) |
| `SK-22` | `research-council` | Multi-agent research scholarship | 5 research members + chair |
| `SK-23` | `epistemic-mapping` | Rumsfeld matrix, coverage tracking | Epistemic Mapper |
| `SK-24` | `math-project-management` | Project scheduling, milestones, risk | Project Manager |
| `SK-25` | `math-strategy-studio` | Brainstorming, proof strategy, creativity | Strategy Designer |
| `SK-26` | `lean-mwe` | Minimal working examples | Reducer |
| `SK-27` | `lean-pr` | Pull request preparation | PR Manager |
| `SK-28` | `lean-bisect` | Git bisection for regressions | Debugger |
| `SK-29` | `lean-build` | Mathlib build infrastructure (**REDIRECT** — see `lean-build`) | Build Engineer |
| `SK-30` | `lean-pr` | Mathlib PR workflow (**REDIRECT** — see `lean-pr` + `references/upstream/mathlib4-pr.md`) | PR Manager |
| `SK-31` | `lean-proof-review` | Mathlib review standards (**REDIRECT** — see `references/upstream/mathlib4-review.md`) | Reviewer |
| `SK-32` | `lean-nested-learning` | Nested learning hierarchy, LaSalle, timescale separation | NL Specialist |
| `SK-33` | `lean-causal-reasoning` | Causal DAGs, KG quality gates, counterfactual | Causality Specialist |
| `SK-34` | `lean-bisect` | Nightly CI/build testing (**REDIRECT** — see `references/upstream/lean-nightly-infrastructure.md`) | CI Engineer |
| `SK-35` | `lean-retro-methodology` | RETRO protocol for retroactive formalization | RETRO Architect |
| `SK-36` | `lean-enforcement` | Programmatic quality enforcement (Python/shell) | Enforcement Engine |
| `SK-37` | `lean-doc-feedback` | Bidirectional document ↔ Lean feedback loop | Feedback Coordinator |
| `SK-38` | `lean-research` | Typed research protocols (M/T/L/S/D/X/E) (**REDIRECT** — folded into `lean-research` Part 9) | Research Specialist |
| `SK-39` | `lean-quality-engine` | Unified QA lifecycle, quality scoring, gates | QA Orchestrator |
| `SK-40` | `lean-integration-protocol` | Cross-skill integration, lifecycle templates, personas | Integration Architect |
| `SK-41` | `lean-math-dynamical` | Nonlinear dynamics, bifurcation, chaos, attractors | Domain expert (nonlinear) |
| `SK-42` | `lean-math-stochastic` | Time series, EWS, filtering, spectral analysis | Domain expert (time series) |
| `SK-43` | `lean-math-discrete` | Graph theory, knowledge graphs, ontologies | Domain expert (graphs/KG) |
| `SK-44` | `lean-math-stochastic` | Measure theory, probability, stochastic processes | Domain expert (measure/prob) |
| `SK-45` | `lean-math-foundations` | Abstract algebra, category theory, lattices | Domain expert (algebra/cat) |
| `SK-46` | `lean-math-optimization` | Optimization theory, game theory, mechanism design | Domain expert (optim/game) |
| `SK-47` | `lean-math-analysis` | Topology, real/functional analysis, metric spaces | Domain expert (topology) |
| `SK-48` | `lean-knowledge-formalization` | Symbolic AI, neuro-symbolic, KRR | Domain expert (symbolic AI) |
| `SK-49` | `lean-ai-formalization` | Agentic AI, multi-agent, evolving agents | Domain expert (agentic) |
| `SK-50` | `lean-ai-formalization` | Formally verifiable AI, high-stakes AI | Domain expert (verified AI) |
| `SK-51` | `lean-causal-reasoning` | Causal reasoning, deontic logic, counterfactuals | Domain expert (causal/deontic) |
| `SK-52` | `lean-knowledge-formalization` | Commonsense reasoning, qualitative physics, BDI | Domain expert (commonsense) |
| `SK-53` | `applied-legal-reasoning` | Legal argumentation, defeasible rules, compliance | Domain expert (legal) |
| `SK-54` | `lean-applied-reasoning` | Intelligence analysis, SATs, ACH, indicators | Domain expert (intelligence) |
| `SK-55` | `lean-applied-reasoning` | Strategy creation/analysis, wargaming, decision | Domain expert (strategy) |
| `SK-56` | `applied-data-information-security` | Data/info security, crypto, access control | Domain expert (security) |
| `SK-57` | `applied-engineering-disciplines` | Control, systems, reliability, signal processing | Domain expert (engineering) |
| `SK-58` | `math-product-management` | Theorem portfolio, RICE, roadmaps, value analysis | Product Manager |
| `SK-59` | `epistemic-discovery-engine` | Active UU hunting, sweeps, probes, anti-stagnation | Discovery Engine |
| `SK-60` | `research-synthesis-engine` | Knowledge synthesis dual to review council | Synthesis Engine |
| `SK-61` | `lean-blueprint` | Blueprint generation (LeanArchitect + leanblueprint) | Blueprint Architect |
| `SK-62` | `lean-report` | Blueprint-to-report (LaTeX with NL text) | Report Author |
| `SK-63` | `lean-build` | Agnostic Lake build skill (W4 Wave 2 — replaces `lean-build`) | Build Engineer |
| `SK-64` | `lean-proof-refactor` | Long-proof decomposition, helper-lemma extraction, regression gates | Editor / Refactor Specialist |
| `SK-65` | `lean-upstream-porting` | Corpus-to-Mathlib/stdlib upstream porting, branch hygiene, AI disclosure | Editor / Upstream Porter |
| `SK-66` | `lean-tautology-triage` | Triage of vacuous, tautological, `: True`, or bare `decide`/`rfl` theorems | Auditor / Triage Specialist |
| `SK-67` | `lean-package-research` | Upstream package ecosystem evaluation, dependency readiness, version pins | Researcher |
| `SK-68` | `lean-vendor-substrate` | Vendored upstream mathematical libraries, read-only boundary, fork sync | Substrate Steward |
| `SK-69` | `lean-formalization-breakdown` | Multi-wave architectural breakdown, static/kernel census, landmark DAG | Breakdown Curator |
| `SK-70` | `lean-dag-visualizer` | Interactive formalization DAG visualizer, topological depth, Tufte proof-walk | DAG Navigator |
| `SK-71` | `lean-pedagogical-exposition` | Textbook-grade mathematical narrative, proof walkthroughs, concept zettels | Pedagogy Author |
| `SK-72` | `lean-bigraph-modeling` | Robin Milner Bigraphical Reactive Systems (Place Graph + Link hyperedges) | Domain expert (bigraphs) |
| `SK-73` | `lean-convergence-verification` | Discrete Lyapunov energy contraction, loop bounds, ceiling division | Domain expert (convergence) |
| `SK-74` | `lean-core-only` | Stdlib/Core-only Lean 4 proving without Mathlib (`omega`, `grind`, induction) | Implementer (core-only) |
| `SK-75` | `lean-axiom-closure` | Compile-time transitive axiom closure lockdown (`#guard_msgs in #print axioms`) | Auditor (trust closure) |
| `SK-76` | `lean-deep-audit` | Whole-corpus 7-lens quality audit (trust lockdown, faithfulness, inhabitation) | Audit Director |
| `SK-77` | `lean-replay-verification` | Independent kernel replay (`lean4checker --fresh`, Comparator) | Auditor (kernel replay) |
| `SK-78` | `ai-guard-judge-eval` | Guard-style LLM judge benchmarking, band-stratified eval, schema adapters | Domain expert (AI guard eval) |
| `SK-79` | `lean-competitive-math` | Olympiad / contest formalization (MiniF2F, Putnam, IMO) | Domain expert (competition math) |


---

## Part 2 — Context Collapse Prevention

Context collapse occurs when an agent loses track of the broader goal, accumulates stale information, or enters semantic drift. The gateway implements these safeguards:

### 2.1 Context Windows

Every task operates within a declared context window:

```
CONTEXT WINDOW = {
  scope:       [theorem | file | module | project]
  artifacts:   [list of files/theorems in scope]
  skills:      [list of active skills]
  agents:      [list of active agents with roles]
  iteration:   [RALPH iteration number]
  health:      [green | yellow | red]
  budget:      [remaining agent launches / time]
}
```

### 2.2 Context Checkpoints

At every RALPH phase boundary, the gateway:
1. **Serializes** the current context window to a tracking document
2. **Validates** that no artifact has drifted out of scope
3. **Prunes** stale information (findings already resolved, agents completed)
4. **Refreshes** by re-reading the latest state of tracked files
5. **Measures** context size — if > 80% of capacity, trigger context compression

### 2.3 Context Compression Protocol

When context is at risk of overflow:
1. **Summarize** completed RALPH iterations into a single paragraph each
2. **Archive** resolved findings (move to session report, remove from active context)
3. **Collapse** agent dispatch history into a completion summary
4. **Retain** only: current iteration findings, active todos, pending votes, open disagreements
5. **Log** the compression event in the tracking document

### 2.4 Drift Detection

The gateway monitors for these drift signals:

| Signal | Detection | Response |
|---|---|---|
| Scope creep | Agent references artifacts not in context window | Redirect or expand scope explicitly |
| Goal drift | Agent's output doesn't address any open finding | Pause agent, re-issue prompt with explicit goal |
| Repetition | Same finding/fix proposed 3+ times | Escalate to SDR or human review |
| Semantic incoherence | Agent output contradicts its own prior output | Restart agent with fresh context |
| Staleness | Agent references resolved finding as open | Refresh agent context from checkpoint |

---

## Part 3 — Feedback and Feedforward Loops

### 3.1 Feedback Loops (Outputs → Inputs)

```
┌─────────────────────────────────────────────────────────┐
│                    FEEDBACK LOOPS                        │
│                                                         │
│  Review findings ──► Specification revisions             │
│  Council votes ──► Proof rewrites                        │
│  Zettelkasten patterns ──► Skill improvements            │
│  Build errors ──► Tactic redesigns                       │
│  Paper updates ──► New requirements                      │
│  Audit results ──► Retroactive fix plans                 │
│  Research insights ──► Specification guidance             │
│  Enforcement violations ──► Priority P0 todos            │
│                                                         │
│  EVERY output of one skill is a potential input          │
│  to another. The gateway routes these signals.           │
└─────────────────────────────────────────────────────────┘
```

| Source skill | Signal | Target skill | Action |
|---|---|---|---|
| `lean-proof-review` | 🔴 finding | `lean-specification` | Revise spec |
| `lean-review-council` | Vote result | `lean-proof` | Implement fix |
| `lean-zettelkasten` | 3+ pattern cluster | `lean-proof-review` | Update checklist |
| `lean-doc-requirements` | New REQ | `lean-specification` | Create spec |
| `lean-research` | Literature finding | `lean-zettelkasten` | Create literature note |
| `lean-doc-improvement` | Metric update | `lean-gateway` | Refresh project state |
| `lean-doc-feedback` | Erratum discovered | `lean-doc-improvement` | Update paper |
| `lean-doc-feedback` | Coverage gap | `lean-doc-requirements` | Extract new claims |
| `lean-retroactive-audit` | Module report | `lean-review-council` | Schedule fixes |
| `lean-retro-methodology` | Wave complete | `lean-quality-engine` | QA gate check |
| `lean-enforcement` | Script violation | `lean-gateway` | Create P0 todo |
| `lean-enforcement` | Script pass | `lean-quality-engine` | Update score |
| `lean-quality-engine` | Gate blocked | `lean-gateway` | Pause, remediate |
| `lean-quality-engine` | Score regression | `lean-gateway` | Alert + improvement plan |
| `lean-research` | Type S finding | `lean-enforcement` | Sound. check dispatch |
| `lean-research` | Type D recommendation | `lean-specification` | Design spec update |
| enforcement scripts | Violation | `lean-gateway` | Create P0 todo |
| `lean-blueprint` | Missing decl error | `lean-enforcement` | Fix annotation |
| `lean-blueprint` | Dep graph reveals gap | `lean-retro-methodology` | Schedule audit |
| `lean-blueprint` | Coverage gap vs paper | `lean-doc-requirements` | Extract new claims |
| `lean-blueprint` | Rendered output | `lean-doc-improvement` | Update paper appendix |
| `lean-report` | Unclear theorem statement | `lean-specification` | Revise spec clarity |
| `lean-report` | Missing cross-refs | `lean-blueprint` | Re-annotate |
| `lean-report` | Dep graph anomaly | `lean-retro-methodology` | Schedule audit |
| `lean-report` | Unnarrated theorems | `lean-doc-improvement` | Flag coverage gap |
| `lean-report` | Paper inconsistency | `lean-doc-requirements` | Extract new claims |

### 3.2 Feedforward Loops (Planning → Execution)

```
┌─────────────────────────────────────────────────────────┐
│                   FEEDFORWARD LOOPS                      │
│                                                         │
│  Paper claims ──► Requirements ──► Specifications        │
│  Specifications ──► Proof designs ──► Implementations    │
│  Audit plan ──► Module schedule ──► Council dispatch     │
│  Research plan ──► Literature search ──► ZK notes        │
│  Gap analysis ──► New theorem plan ──► Spec + Impl       │
│                                                         │
│  Planning drives execution. The gateway schedules        │
│  feedforward chains for maximum parallelism.             │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Loop Health Monitoring

Every loop is monitored for:
- **Latency:** How long between signal emission and consumption
- **Throughput:** Signals processed per RALPH iteration
- **Backlog:** Unprocessed signals queued
- **Starvation:** A target skill receiving no signals for 2+ iterations

---

## Part 4 — Fan-In and Fan-Out

### 4.1 Fan-Out (One → Many)

When a single event triggers multiple parallel actions:

```
Paper claim discovered
    ├──► Specifier: create REQ
    ├──► Researcher: find related Mathlib results
    ├──► Ν (Novelty Scout): check for duplicates
    └──► Documenter: update coverage matrix
```

**Gateway dispatch:** Launch all downstream agents simultaneously. No agent waits for another in a pure fan-out.

### 4.2 Fan-In (Many → One)

When multiple agents must complete before a decision:

```
Council review (5 parallel agents)
    Σ findings ─┐
    Φ findings ─┤
    Ν findings ─┼──► Voting synchronization ──► Decision
    Λ findings ─┤
    Ω findings ─┘
```

**Gateway sync:** Wait for all agents to report. If one agent is slow (>2× median completion time), issue a warning and optionally proceed with 4/5 votes.

### 4.3 Fan-In → Fan-Out Chains

Common pattern: fan-in to a decision point, then fan-out to execute the decision.

```
5 reviewers ──fan-in──► vote ──fan-out──► {fixer, documenter, synthesizer}
```

The gateway manages these chains as first-class constructs, tracking each stage.

---

## Part 5 — Topology Selection

The gateway selects the review/work topology based on scope:

| Trigger | Scope | Topology | Skills activated |
|---|---|---|---|
| `review theorem X` | 1 theorem | Star (5 parallel) | SK-02, SK-03 |
| `review file X.lean` | 1 file | Pipeline (staged) | SK-02, SK-03, SK-04 |
| `review module X` | 1 module | Pipeline + Star per theorem | SK-02, SK-03, SK-04, SK-10 |
| `review project` | All modules | Mesh (dependency waves) | All skills |
| `retroactive audit` | Existing project | RETRO protocol (5-phase) | SK-08, SK-35, SK-03, SK-09, SK-11, SK-36 |
| `specify new theorems` | Paper section | Fan-out to specifiers | SK-05, SK-09, SK-11 |
| `improve docs` | Paper + Lean | Bidirectional feedback | SK-37, SK-09, SK-10, SK-11 |
| `research topic X` | External | Typed research pipeline | SK-38, SK-11, SK-04, SK-12..21 |
| `research council session` | Multi-domain | Star (5 parallel) + Synthesis | SK-22, SK-38, SK-11, SK-23, SK-12..21 |
| `epistemic audit` | Module/project | Pipeline (map → probe → update) | SK-23, SK-22, SK-11 |
| `strategy session` | Proof/module | Hub-and-spoke | SK-25, SK-11, domain skills |
| `project status` | Project-wide | Collect-and-report | SK-24, SK-23, SK-07 |
| `quality gate check` | Module/project | Pipeline (enforce → score → gate) | SK-39, SK-36 |
| `enforcement run` | Project-wide | Sequential pipeline | SK-36 |
| `milestone review` | Project-wide | Full QA pipeline | SK-39, SK-36, SK-37, SK-03 |
| `generate blueprint` | Project-wide | Pipeline (analyze → annotate → scaffold → extract → render) | SK-61, SK-35, SK-36, SK-10 |
| `update blueprint` | Project-wide | Pipeline (annotate → extract → render) | SK-61 |
| `deploy blueprint` | Project-wide | CI push | SK-61, SK-34 |
| `generate report` | Project-wide | Pipeline (ingest → plan → narrate → illustrate → assemble → compile) | SK-62, SK-61, SK-60, SK-39 |
| `update report` | Project-wide | Pipeline (re-narrate changed chapters → compile) | SK-62 |
| `compile report` | Project-wide | LaTeX → PDF | SK-62 |

---

## Part 6 — Health Dashboard

The gateway maintains a health dashboard updated at every RALPH phase boundary:

```markdown
# Gateway Health Dashboard
## Timestamp: [ISO-8601]

### System Health: [🟢 GREEN / 🟡 YELLOW / 🔴 RED]

### Active Context Windows
| CW-ID | Scope | Iteration | Health | Agents | Open findings |
|---|---|---|---|---|---|
| CW-001 | Project/Lyapunov | 3 | 🟢 | 5 | 2 |
| CW-002 | Project/RL | 1 | 🟢 | 5 | 7 |

### Feedback Loop Status
| Loop | Latency | Backlog | Status |
|---|---|---|---|
| review → spec | 0 iter | 0 | 🟢 |
| ZK → skill-update | 1 iter | 3 notes | 🟡 |
| audit → fix | 0 iter | 0 | 🟢 |

### Agent Pool
| Role | Active | Completed | Failed | Queued |
|---|---|---|---|---|
| Reviewer | 5 | 12 | 0 | 3 |
| Specifier | 2 | 5 | 0 | 1 |
| Implementer | 3 | 8 | 1 | 2 |
| Documenter | 1 | 4 | 0 | 0 |
| Synthesizer | 1 | 2 | 0 | 0 |
| Researcher | 1 | 3 | 0 | 0 |

### Anti-Collapse Metrics
| Metric | Value | Threshold | Status |
|---|---|---|---|
| Max RALPH iteration | 3 | 7 | 🟢 |
| Context utilization | 45% | 80% | 🟢 |
| Stale findings | 0 | 5 | 🟢 |
| Repetition count | 1 | 3 | 🟢 |
| Agent failure rate | 2% | 10% | 🟢 |

### Todo Summary
| Priority | Open | In progress | Done |
|---|---|---|---|
| P0 | 0 | 0 | 3 |
| P1 | 2 | 1 | 8 |
| P2 | 5 | 2 | 12 |
| P3 | 3 | 0 | 4 |
```

### Health Thresholds

| Condition | Threshold | Escalation |
|---|---|---|
| 🟢 Green | All metrics within bounds | Continue normally |
| 🟡 Yellow | Any metric at 70%+ of threshold | Alert, increase monitoring frequency |
| 🔴 Red | Any metric exceeds threshold | Pause new work, diagnose, checkpoint all contexts |

---

## Part 7 — Task Routing Protocol

When a task arrives at the gateway:

```python
def route_task(task):
    # 1. Classify
    task_type = classify(task)  # review | specify | implement | audit | research | document
    scope = determine_scope(task)  # theorem | file | module | project
    
    # 2. Check health
    if system_health == RED:
        queue_task(task, priority=task.priority)
        return "QUEUED — system in RED state, resolving existing issues"
    
    # 3. Select topology
    topology = select_topology(task_type, scope)
    
    # 4. Check dependencies
    blocked_by = check_dependencies(task)
    if blocked_by:
        queue_task(task, blocked_by=blocked_by)
        return f"BLOCKED by {blocked_by}"
    
    # 5. Allocate context window
    cw = allocate_context_window(task, scope)
    
    # 6. Dispatch
    agents = dispatch_agents(topology, cw)
    
    # 7. Monitor
    register_monitoring(cw, agents, feedback_loops)
    
    return f"DISPATCHED: {len(agents)} agents in {topology} topology"
```

---

## Part 8 — Cross-Skill Coordination Matrix

Defines how skills interact — which skills can call which, and through what interface:

| Caller | Can invoke | Interface | Direction |
|---|---|---|---|
| `lean-gateway` | ALL skills | Task dispatch | →  |
| `lean-review-council` | `lean-proof-review`, `lean-zettelkasten`, `lean-specification` | RALPH phases | → |
| `lean-retroactive-audit` | `lean-review-council`, `lean-doc-requirements`, `lean-research` | Audit plan | → |
| `lean-retro-methodology` | `lean-retroactive-audit`, `lean-enforcement`, `lean-review-council`, `lean-doc-feedback` | RETRO phases | → |
| `lean-doc-requirements` | `lean-specification`, `lean-research` | REQ documents | → |
| `lean-doc-improvement` | `lean-zettelkasten` | Update records | → |
| `lean-doc-feedback` | `lean-doc-requirements`, `lean-doc-improvement`, `lean-enforcement` | Bidirectional | ↔ |
| `lean-research` | `lean-zettelkasten`, `lean-doc-requirements`, domain skills (SK-12..21) | Findings | → |
| `lean-research` | `lean-research`, domain skills (SK-12..21), `epistemic-mapping` | Typed dispatch | → |
| `lean-specification` | `lean-proof`, `lean-research` | Design | → |
| `lean-zettelkasten` | `lean-proof-review` (skill updates) | Permanent notes | → |
| `lean-enforcement` | `lean-gateway` (violations), `lean-quality-engine` (reports) | Script results | → |
| `lean-quality-engine` | `lean-enforcement`, `lean-review-council`, `lean-doc-feedback` | QA gates | → |
| `research-council` | `lean-research`, `lean-research`, `epistemic-mapping`, domain skills (SK-12..21) | Research dispatch | → |
| `epistemic-mapping` | `lean-research`, `research-council` | Gap signals | → |
| `math-project-management` | `lean-gateway`, `epistemic-mapping`, `lean-quality-engine` | Schedule/risk | → |
| `math-strategy-studio` | `lean-research`, domain skills (SK-12..21) | Strategy plans | → |
| domain skills (SK-12..21) | `lean-research`, `lean-zettelkasten` | Domain guidance | → |
| `lean-nested-learning` (SK-32) | `lean-math-dynamical`, `lean-math-analysis` | NL domain | → |
| `lean-causal-reasoning` (SK-33) | `lean-math-discrete`, `lean-knowledge-formalization` | Causal domain | → |
| ANY skill | `lean-gateway` | Status reports, escalations | ← |

**Invariant:** No skill modifies another skill's SKILL.md without a council vote (4/5 approval).

---

## Part 9 — Global Tracking Documents

The gateway maintains these project-level documents:

### 9.1 Master Task Register

```
docs/project/lean/docs/tracking/task_register.md
```
All tasks across all skills, with status, assignment, priority, dependencies.

### 9.2 Coverage Matrix

```
docs/project/lean/docs/tracking/coverage_matrix.md
```
Maps every paper claim (§, equation, proposition) to its REQ-ID, theorem name, review status.

### 9.3 Health Log

```
docs/project/lean/docs/tracking/health_log.md
```
Timestamped health dashboard snapshots, context collapse events, escalations.

### 9.4 Skill Version Registry

```
docs/project/lean/docs/tracking/skill_versions.md
```
Version history of all skills, what changed, which RALPH iteration triggered it.

### 9.5 Agent Dispatch Log

```
docs/project/lean/docs/tracking/dispatch_log.md
```
Every agent launched: role, task, start time, end time, outcome.

---

## Part 10 — Hierarchy Management

### 10.1 Hierarchy Levels

```
Level 0: Gateway Orchestrator (this skill)
Level 1: Skill coordinators (council chairs, audit leaders)
Level 2: Council members / Individual agents
Level 3: Sub-agents (within a RALPH phase)
```

### 10.2 Escalation Path

```
Sub-agent issue → Council member → Council chair (Ω) → Gateway → Human
```

Each level can resolve issues within its scope. Escalation occurs when:
- The issue crosses skill boundaries (→ Gateway)
- The RALPH iteration cap is hit (→ Gateway)
- A 🔴 block cannot be resolved by SDR (→ Gateway → Human)

### 10.3 Authority Matrix

| Action | Level 0 | Level 1 | Level 2 |
|---|---|---|---|
| Dispatch agents | ✅ | ✅ (within own skill) | ❌ |
| Modify SKILL.md | ✅ (after vote) | Propose only | ❌ |
| Modify AGENTS.md | ✅ (after vote) | Propose only | ❌ |
| Create todos | ✅ | ✅ | ✅ |
| Block a review | ❌ | ✅ (chair) | ✅ (veto power) |
| Escalate to human | ✅ | ✅ | ✅ |
| Compress context | ✅ | ✅ (own CW) | ❌ |
| Pause system | ✅ | ❌ | ❌ |

---

## Part 11 — Enforcement Script Orchestration

The gateway integrates with lean-enforcement (SK-36) to run programmatic checks at key lifecycle points. All workflow invocations MUST pass through the `workflow_gate.py` enforcer.

### 11.1 Script Inventory

| Script | Purpose | Run By Gateway When |
|---|---|---|
| `council_precheck.sh` | Build + sorry + conventions | Before any council session |
| `axiom_audit.py` | Axiom contamination scan | After build succeeds |
| `review_coverage.py` | Theorem review tracking | After review sessions |
| `metric_sync.py` | Paper ↔ code metric alignment | Before milestones |
| `zettelkasten_lint.py` | ZK structural health | Weekly / after synthesis |
| `retro_recon.py` | RETRO Phase R discovery | At audit start |
| `bridge_validator.py` | Cross-module import validation | After module changes |
| `proof_quality.py` | Static proof quality analysis | Before reviews |
| `ecosystem_health.py` | Skill ecosystem integrity | After skill changes |
| `enforce_all.sh` | All-in-one pipeline | Before milestones |
| **`workflow_gate.py`** | **Workflow gate enforcer — validates mandatory gates before any step** | **Every workflow invocation** |

### 11.2 Gateway Dispatch Logic

```python
def dispatch_enforcement(event_type, scope):
    """Gateway decides which scripts to run for each event."""
    scripts = {
        'pre_review':    ['council_precheck.sh'],
        'post_review':   ['review_coverage.py'],
        'post_build':    ['axiom_audit.py'],
        'post_refactor': ['bridge_validator.py', 'proof_quality.py'],
        'pre_milestone': ['enforce_all.sh --strict'],
        'retro_start':   ['retro_recon.py'],
        'skill_change':  ['ecosystem_health.py'],
        'weekly':        ['zettelkasten_lint.py', 'metric_sync.py'],
    }
    return scripts.get(event_type, [])
```

### 11.3 Mandatory Workflow Invocation Protocol

**Every workflow MUST be invoked through `workflow_gate.py`.** This closes the two highest-risk enforcement gaps:
- **G5:** Council precheck is programmatically enforced (not just documented)
- **G7:** Gateway dispatch rules are executable code (not just pseudocode)

```bash
# Before council review session:
python3 scripts/workflow_gate.py --workflow council_review --step pre_check

# Before dispatching council members:
python3 scripts/workflow_gate.py --workflow council_review --step dispatch_members

# Before milestone release:
python3 scripts/workflow_gate.py --workflow milestone --step pre_milestone

# RETRO audit phases:
python3 scripts/workflow_gate.py --workflow retro_audit --step recon
python3 scripts/workflow_gate.py --workflow retro_audit --step establish
python3 scripts/workflow_gate.py --workflow retro_audit --step triage
python3 scripts/workflow_gate.py --workflow retro_audit --step review
python3 scripts/workflow_gate.py --workflow retro_audit --step onboard

# Check status of all active workflows:
python3 scripts/workflow_gate.py --status
```

**Gate enforcement guarantees:**
1. **Prerequisite ordering:** Step B cannot run until step A has passed
2. **Script execution:** Required scripts are run and must exit 0
3. **Staleness protection:** Script results expire after 30 minutes (configurable)
4. **State persistence:** All gate checks are recorded in `docs/tracking/workflow_state/`
5. **Blocking vs advisory:** Blocking gates return exit code 1 (hard stop); advisory gates return 0 with warnings

**Available workflows:**

| Workflow | Steps | Blocking Gates |
|---|---|---|
| `council_review` | pre_check → dispatch_members → collect_votes → sdr → close_session | pre_check, dispatch_members, collect_votes, close_session |
| `retro_audit` | recon → establish → triage → review → onboard | All 5 steps |
| `milestone` | pre_milestone → council_review_all → metric_sync → release | All 4 steps |
| `spec_lifecycle` | requirements → design → documentation → approval | requirements, design, approval |
| `forward_sync` | extract_claims → specify → research → implement → review → index | extract_claims, specify, implement, review |
| `backward_sync` | detect_changes → generate_patches → apply_patches → verify_sync | All 4 steps |

---

## Part 12 — Full Ecosystem Topology Diagram

```
                        ┌─────────────────────────┐
                        │  lean-gateway (SK-07)    │
                        │  Orchestrator (75 skills)│
                        └──────────┬──────────────┘
                                   │
    ┌──────────────┬───────────────┼───────────────┬──────────────┐
    │              │               │               │              │
┌───▼───┐    ┌─────▼─────┐   ┌────▼────┐   ┌──────▼──────┐ ┌────▼────┐
│REVIEW │    │ RESEARCH  │   │DOCUMENT │   │ KNOWLEDGE   │ │QUALITY  │
│cluster│    │ cluster   │   │ cluster │   │ cluster     │ │cluster  │
└───┬───┘    └─────┬─────┘   └────┬────┘   └──────┬──────┘ └────┬────┘
    │              │              │                │              │
 SK-02,03,05   SK-11,22,38    SK-09,10,37      SK-04,23,25   SK-08,35,36,39
 SK-66         SK-67          SK-61,62,70,71   ZK,epist,     SK-75,76,77
 proof,council  research,      doc,blueprint,   strategy      enforce,QA,
 spec,triage    pkg-research   report,viz,ped                 axiom,replay
    │              │                                             │
┌───▼───┐    ┌─────▼─────┐                                 ┌────▼────┐
│DOMAIN │    │ EPISTEMIC │                                 │ INFRA   │
│cluster│    │ cluster   │                                 │ cluster │
└───┬───┘    └─────┬─────┘                                 └────┬────┘
    │              │                                             │
 SK-12..21      SK-23,59,60                                  SK-01,06,26..28
 SK-32,33       epist-map,                                   SK-63..65,68,69,74
 SK-72,73,79    discovery,                                   prove,build,setup,
 specialists    synthesis                                    refactor,port,core
    │
┌───▼───────────────────────────────┐
│ EXPANDED DOMAIN SKILLS            │
│ SK-41..58, SK-78                  │
├───────────────────────────────────┤
│ Math: SK-41..47                   │
│  nonlinear, timeseries, graph/KG, │
│  measure/prob, algebra/cat,       │
│  optim/game, topology             │
│ AI: SK-48..52, SK-78              │
│  symbolic, agentic, verifiable,   │
│  causal/deontic, commonsense,     │
│  guard-judge-eval                 │
│ Applied: SK-53..57                │
│  legal, intelligence, strategy,   │
│  security, engineering            │
│ Management: SK-58                 │
│  product management               │
└───────────────────────────────────┘

  Fan-in to gateway: ALL 75 first-party skills report status/escalations ← SK-07
  Fan-out from gateway: SK-07 dispatches to ANY skill →
```

### 12.1 Cluster Responsibilities

| Cluster | Skills | Primary Function |
|---|---|---|
| **Review** | SK-02, SK-03, SK-05, SK-66 | Verify proof correctness, specification, and non-triviality |
| **Research** | SK-11, SK-22, SK-38, SK-67 | Find knowledge, methods, literature, and package ecosystem readiness |
| **Document & Blueprint** | SK-09, SK-10, SK-37, SK-61, SK-62, SK-70, SK-71 | Bidirectional paper ↔ Lean sync, blueprints, DAG visualizer, pedagogy |
| **Quality & Audit** | SK-08, SK-35, SK-36, SK-39, SK-69, SK-75, SK-76, SK-77 | Enforce quality, axiom lockdown, kernel replay, deep audit, QA gates |
| **Domain (core)** | SK-12..21, SK-32, SK-33, SK-72, SK-73, SK-79 | Lean formalization domain expertise (incl. bigraphs, convergence, contest math) |
| **Domain (math)** | SK-41..47 | Pure/applied math domain knowledge |
| **Domain (AI)** | SK-48..52, SK-78 | AI domain knowledge (symbolic, agentic, causal, verifiable, guard-judge eval) |
| **Domain (applied)** | SK-53..57 | Applied domain knowledge (legal, intel, strategy, security, engineering) |
| **Domain (mgmt)** | SK-24, SK-58 | Project + product management |
| **Knowledge** | SK-04, SK-25 | Knowledge management, brainstorming |
| **Epistemic** | SK-23, SK-59, SK-60 | Epistemic mapping, UU discovery, research synthesis |
| **Infrastructure & Editor** | SK-01, SK-06, SK-26..28, SK-63..65, SK-68, SK-74 | Proving, core-only profile, Lake build, MWE, bisect, PRs, refactoring, porting, vendor substrate |

---

## Operational Details (from `skills/lean-gateway/SKILL.md`)

# lean-gateway

> ⚠️ **MANDATORY** (hot-tier): the gateway NEVER does substantive proof or
> documentation work — every operation is a delegation. Skipping Persist
> (the global task tracker) = incomplete.

## Routing

- **USE FOR:** receiving a Lean 4 task at session start, decomposing it into phases, routing each phase to the appropriate skill in
  [`REFERENCE.md`](./REFERENCE.md) Part 1's registry; deciding fan-in vs fan-out vs sequential topology; maintaining the per-task state document; detecting
  context-collapse signals and prescribing a fresh session.
- **DO NOT USE FOR:** writing a proof (delegate to `@lean-proof`); reviewing a proof (delegate to `@lean-proof-review`); editing docs (delegate to
  `@lean-doc-improvement`); running scripts (delegate to `@lean-enforcement`).
- **TRIGGERS:** gateway, orchestrate, route, dispatch, top-level, context collapse, fan-out, fan-in, ecosystem health.

## Behavioural rules (G-*)

- **G-1** (MUST NOT): The gateway MUST NOT execute substantive proof, doc, or research work itself; every such operation MUST be a delegation. [Trace: AC-01]
- **G-2** (MUST): Each phase MUST be routed to exactly one owning skill from the registry; if no clear owner exists, the gateway MUST escalate per
  §Recovery & STOP. [Trace: AC-02]
- **G-3** (MUST): Fan-out topology (parallel skills) MUST converge through a documented fan-in (a single skill that integrates the results). [Trace: AC-03]
- **G-4** (SHOULD): The gateway SHOULD prefer the most specific skill in the registry over a broader one (e.g. `@lean-blueprint` over
  `@lean-doc-improvement` for blueprint work). [Trace: AC-04]
- **G-5** (MUST): On any of the documented context-collapse signals (≥ 2 from `AGENTS.md`), the gateway MUST recommend a fresh session before continuing.
  [Trace: AC-05]
- **G-6** (MUST): The gateway MUST maintain the per-task tracker (phase status, owner, predecessors, successors, sign-offs); a missing tracker entry = a
  missing delegation. [Trace: AC-06]
- **G-7** (SHOULD NOT): The gateway SHOULD NOT silently retry a failed downstream delegation; it MUST escalate per §Recovery & STOP. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] — receive the task, locate prior tracker for this scope (if any), enumerate the candidate skills from the registry.
2. **Plan** [discover] — partition the task into phases; for each phase, pick the owning skill; choose topology (sequential / fan-out / fan-in / hybrid);
   STOP if confidence < 90 %.
3. **Delegate** [execute] — invoke each phase's owning skill in the chosen order; capture the returned artefact reference + sign-off state.
4. **Integrate** [validate] — when fanning in, confirm every parallel branch returned a sign-off; halt on any unsigned branch.
5. **Health-check** [validate] — sweep for context-collapse signals; recommend a fresh session if ≥ 2 are present.
6. **Persist** [persist] *(MANDATORY)* — update the per-task tracker (phase status, owner, artefact links, sign-offs); update the ecosystem-health
   dashboard; tick the global tasks list. Skipping Persist = incomplete.

## Recovery & STOP

- No clear owning skill for a phase → STOP, ask which skill to add or extend.
- A downstream skill returns a hard failure → STOP, do NOT silently retry; escalate to that skill's owner.
- Fan-in fails because a parallel branch is unsigned → STOP, complete the missing branch before integrating.
- ≥ 2 context-collapse signals from `AGENTS.md` → STOP, recommend a fresh session.
- Confidence < 90 % on phase decomposition or topology → STOP, ask.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Dispatch targets:** see FM `dispatch_targets` for the full set of downstream skills the gateway may delegate to.
- **Source spec:** `specs/lean/gateway/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the full skill registry, context-collapse signal list, feedback-loop topology, fan-in/fan-out
  patterns, health dashboard schema, hierarchy management, enforcement-script orchestration, and ecosystem topology diagram (original v1 content, preserved
  verbatim).

## Common failure modes

> AI agents commonly: do the work themselves "to save a delegation"; pick a
> broad skill when a specific one exists; retry a failed delegation instead of
> escalating; ignore context-collapse signals; skip the per-task tracker update.
> Full registry: GUARDRAILS.md §Agent failure taxonomy.
