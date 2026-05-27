---
title: "Lean Research Handbook"
status: "reference"
extracted_from: "skills/lean-research/SKILL.md"
extracted_on: "2026-05-27"
scope: "Parts 1-9 (Research Triggers; Research Methods; Research Output Standards; Research Depth Levels; Epistemic Mapping Integration; Review Council Integration; Domain Skill Cross-References; Research Anti-Patterns; Typed Research Protocols (M / T / L / S / D / X / E))."
loader_hint: "Load when @lean-research routes here for methodology details; not needed for the dispatch decision."
---

# Lean Research Handbook

> **Layering note.** This file holds the deep methodology content
> previously embedded in [`skills/lean-research/SKILL.md`](../skills/lean-research/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + the parts index. This file holds the full
> encyclopaedia of research triggers; research methods; research output standards; research depth levels, etc.
> Zero fidelity loss vs the pre-layering revision.

---

## Part 1 — Research Triggers

| Situation | Research Type | Output |
|---|---|---|
| Theorem spec exists, proof strategy unknown | Strategy research | Tactic plan + ZK literature note |
| Tactic fails unexpectedly | Diagnostic research | Root cause + ZK fleeting note |
| Mathlib API is unfamiliar | API research | Usage guide + ZK literature note |
| Duplicate suspected by Ν | Deduplication research | Existing lemma chain + recommendation |
| Paper claim is ambiguous | Interpretation research | Formalization options + erratum if needed |
| Cross-module dependency unclear | Architecture research | Dependency analysis + bridge plan |
| `exact?` / `apply?` return too many results | Filtering research | Ranked candidates + rationale |
| New Mathlib version available | Compatibility research | Changelog review + migration notes |
| Proof is too long (>50 lines) | Simplification research | Alternative strategies |
| Lean community has relevant discussion | Community research | ZK literature note |

---

## Part 2 — Research Methods

### 2.1 Loogle Search (Mathlib Lemma Search)

**When:** Looking for Mathlib lemmas by type signature.

See also: [`theorem-search`](../../references/theorem-search.md).

| Query form | Use | Example |
|---|---|---|
| `Constant.name` | Find lemmas mentioning a constant | `Filter.Tendsto` |
| `"name_part"` | Find declarations by name substring | `"monotone"` |
| `_` wildcards | Match a structural statement pattern | `_ ∈ Set.Icc _ _` |
| `|- conclusion` | Pin the conclusion shape | `|- _ ≤ _` |
| comma filters | Intersect multiple filters | `Filter.Tendsto, "comp", |- _ → _` |

**Strategy:**
1. Start with the exact conclusion type
2. If no results, generalize (replace concrete types with variables)
3. If too many results, add hypothesis types
4. Verify candidates with `#check` and a local Lean command
5. Record useful finds in ZK literature note

### 2.2 exact? / apply? / rw? Output Analysis

**When:** Lean's suggest tactics return candidates.

```lean
-- In a proof:
theorem example : P := by
  exact?  -- returns candidates
  -- or
  apply?  -- returns candidates with remaining goals
  -- or
  rw?     -- returns rewrite candidates
```

**Analysis protocol:**
1. Collect all candidates
2. Filter by namespace relevance (prefer `Project.*` > `Mathlib.*` > generic)
3. Filter by hypothesis compatibility
4. Rank by simplicity (fewer intermediate lemmas = better)
5. Verify top candidates by substitution
6. Replace the search tactic with the suggested proof term or tactic script
7. Record the winning strategy in ZK note

### 2.3 #check / #find / namespace browsing

**When:** You know a name, namespace, or statement shape but not the exact
theorem.

```lean
#check Nat.add_comm      -- inspect a known declaration
#check @Nat.add_comm     -- show implicit arguments
#find _ + _ = _ + _      -- search by statement pattern
```

Use editor completion after a namespace prefix such as `Nat.`, `Finset.`, or
`Filter.`. Treat `#check` and `#find` as exploration commands: remove them from
finished proofs unless they are part of a deliberate test fixture.

### 2.4 Lean-auto + Duper Investigation

**When:** Standard tactics fail and you suspect a first-order or higher-order reasoning gap.

```lean
-- Try in this order:
by auto       -- lean-auto alone
by duper      -- Duper alone  
by auto; duper -- lean-auto simplification then Duper
```

**If `auto` solves it:** No further research needed, but record for future reference that this class of goals responds to `auto`.

**If `auto` fails:** Check if the goal requires:
- Higher-order reasoning (lean-auto is first-order focused)
- Nonlinear arithmetic
- Domain-specific rewrites that auto doesn't know

**Research output:** Strategy recommendation for the theorem spec.

### 2.5 Mathlib Documentation Research

**When:** Need to understand a Mathlib API or design pattern.

**Sources (priority order):**
1. Mathlib4 docs: `https://leanprover-community.github.io/mathlib4_docs/`
2. Mathlib source on GitHub: `leanprover-community/mathlib4`
3. Zulip discussions: `https://leanprover.zulipchat.com/`
4. Lean 4 documentation: `https://lean-lang.org/lean4/doc/`

**Protocol:**
1. Identify the specific API/concept
2. Search docs for the namespace
3. Read the module docstring
4. Find example usages in Mathlib source
5. Create ZK literature note with: namespace, key lemmas, usage pattern, gotchas

### 2.6 Academic Literature Research

**When:** Connecting formalization to published mathematical results.

**Protocol:**
1. Identify the mathematical domain of the theorem
2. Search for:
   - Existing Lean/Coq/Isabelle formalizations of the same result
   - Textbook proofs that might suggest a formalization strategy
   - Related formalization projects (e.g., Mathlib, Archive of Formal Proofs)
3. For each relevant source:
   - Create ZK literature note
   - Extract proof strategy insights
   - Note any hypotheses the source uses that differ from ours
4. Synthesize into a strategy recommendation

### 2.7 Lean Reservoir / Package Research

**When:** Wondering if an external Lean package provides helpful functionality.

**Check:** `https://reservoir.lean-lang.org/`

**Research questions:**
- Does a Lean 4 package exist for this mathematical domain?
- Is it compatible with our Lean/Mathlib version?
- Would importing it introduce dependency conflicts?
- Is the package actively maintained?

**Decision criteria:**
- Use package if: well-maintained, compatible, saves significant effort
- Don't use if: unmaintained, incompatible, only marginal benefit, introduces axiom risk

### 2.8 Tactic Behavior Investigation

**When:** A tactic behaves unexpectedly.

**Diagnostic protocol:**
1. Isolate the minimal goal state where the tactic fails
2. Check: is this a known limitation? (search Zulip/GitHub issues)
3. Try `set_option trace.aesop true` (or appropriate trace option) to see internals
4. Compare with similar goals where the tactic succeeds
5. Determine: bug, limitation, or user error
6. Record finding in ZK fleeting note → promote to permanent if it's a pattern

---

## Part 3 — Research Output Standards

### 3.1 Strategy Recommendation

After research, produce:

```markdown
# Research: [RESEARCH-YYYYMMDD-NNN]
## Target: [theorem name or specification ID]
## Question: [what needed investigation]

## Findings
1. [Finding 1 — with source reference]
2. [Finding 2 — with source reference]
3. [Finding 3 — with source reference]

## Recommended Strategy
- Primary approach: [tactic chain or proof outline]
- Fallback: [alternative if primary fails]
- Estimated complexity: [trivial/routine/moderate/hard]
- Key Mathlib lemmas: [list with full names]
- Risks: [potential issues with this approach]

## Zettelkasten Notes Created
- [ZK-YYYYMMDD-NNN] — [title] (literature/fleeting)
```

### 3.2 API Reference Card

For Mathlib API research:

```markdown
# API Card: [Namespace]
## Module: Mathlib.[path]
## Key Types: [list]
## Key Lemmas:
- `lemma_name` : [type signature] — [when to use]
- ...
## Common Patterns:
```lean
-- Pattern 1: [description]
example : ... := by
  [tactic sequence]
```
## Gotchas:
- [gotcha 1]
## See Also: [related namespaces]
```

---

## Part 4 — Research Depth Levels

### Quick (5 minutes)

- `exact?` / `apply?` on the current goal
- Check Tactics.lean for relevant custom tactic
- Check if a reusable lemma from the project covers it
- One Loogle query

### Standard (15 minutes)

- All of Quick, plus:
- Mathlib docs search for the relevant namespace
- Check 2-3 Zulip threads
- Try `auto` and `duper`
- Review one related theorem's proof in the project

### Deep (1 hour)

- All of Standard, plus:
- Read the Mathlib source for the relevant module
- Search academic literature for formalization strategies
- Check Lean Reservoir for helper packages
- Try 3+ alternative proof strategies
- Create detailed ZK literature note

### Exhaustive (research-level)

- All of Deep, plus:
- Read the original mathematical paper
- Compare with formalizations in other proof assistants (Coq, Isabelle)
- Explore generalizations
- Consider if a new tactic or automation is needed
- Create permanent ZK note with synthesis

---

## Part 5 — Epistemic Mapping Integration (Rumsfeld Matrix)

Every research task maps its findings to the four epistemic quadrants. See `epistemic-mapping/SKILL.md` for full methodology.

### 5.1 Quadrant Definitions (Quick Reference)

| Quadrant | Code | Meaning | Research Action |
|---|---|---|---|
| Known Knowns | KK | Proven in Lean, reviewed, documented | Verify still current |
| Known Unknowns | KU | Identified but not yet resolved | Primary research target |
| Unknown Knowns | UK | Knowledge exists but not indexed | Discovery: search ZK, Mathlib, literature |
| Unknown Unknowns | UU | Gaps we haven't identified | Systematic probing (see §5.3) |

### 5.2 Epistemic-Aware Research Protocol

Before starting any research task:

1. **Map the quadrant:** Which quadrant does this question live in?
2. **Check adjacency:** What KK items border this question? (may provide footholds)
3. **Scan for UK:** Before deep research, search ZK + Mathlib + project for existing answers
4. **Update the map:** After research completes, transition items between quadrants
5. **Score update:** Recalculate Epistemic Score for the affected module

### 5.3 Unknown-Unknown Discovery Methods

| Method | Protocol | When |
|---|---|---|
| Cross-domain probing | Ask: "Does domain X have a concept analogous to Y?" for each new domain skill | Deep/Exhaustive research |
| Boundary testing | Attempt to state/prove boundary conditions not in the spec | Standard+ research |
| Hypothesis negation | "What if this assumption were false?" systematically for each axiom | Deep research |
| Mathlib exploration | Browse Mathlib namespaces adjacent to the one in use | Standard research |
| External survey | Check what Coq/Isabelle/HOL formalizations cover that we don't | Exhaustive research |
| Council brainstorm | Full Research Council session with divergent exploration | Exhaustive research |
| Analogy sweep | For each domain skill, check if the current module's math has parallels | Deep research |
| Counterexample hunting | Attempt to construct counterexamples to all key theorems | Deep research |

### 5.4 Research Output → Epistemic Map Update

Every research output MUST include an epistemic transition log:

```markdown
## Epistemic Transitions
- KU → KK: [item] — now proven/documented (cite theorem or ZK note)
- UU → KU: [item] — discovered gap, now tracked (assigned research ID)
- UK → KK: [item] — existing knowledge indexed (cite source)
- New UU signals: [any hints of further unknown territory]
- Updated Epistemic Score: [module] [old] → [new]
```

---

## Part 6 — Review Council Integration

### 6.1 Review Council Research Dispatch

| Review Council Member | Dispatches Research When |
|---|---|
| Σ | Axiom contamination source unclear → diagnostic research |
| Φ | Paper claim ambiguous → interpretation research |
| Φ | Hypothesis may be insufficient → literature research |
| Ν | Potential duplicate → deduplication research |
| Ν | Proof too complex → simplification research |
| Λ | Quality improvement possible → strategy research |
| Ω | Naming conflict → API research for Mathlib convention |

### 6.2 Research Council Integration

The Research Council (see `research-council/SKILL.md`) is the dual system for systematic scholarship. The lean-research skill acts as the executor for both councils:

| Research Council Member | Research Type Dispatched |
|---|---|
| Α (Foundations Architect) | Foundational coverage — axioms, definitions, dependencies |
| Β (Structure Strategist) | Structural research — proof architectures, module organization |
| Γ (Methods Scholar) | Method research — tactics, strategies, Mathlib API patterns |
| Δ (Bounds Analyst) | Quantitative research — complexity, convergence rates, bounds |
| Ε (Applications Bridge) | Application research — domain connections, practical relevance |

### 6.3 Research Feedback

Research results feed back to both councils:
- Strategy recommendations → inform the implementer agent
- API cards → stored in ZK for all members to reference
- Diagnostic findings → update skill pitfall sections
- Literature notes → enrich all council members' domain knowledge
- Epistemic map updates → inform Research Council's coverage tracking

### 6.4 Research Persona (Researcher Agent)

When the gateway dispatches a research task, the Researcher agent:
1. Receives: theorem spec + council member's question + epistemic context
2. Selects research depth based on question complexity
3. Executes the appropriate research methods
4. Maps findings to epistemic quadrants
5. Produces: strategy recommendation + ZK notes + epistemic transitions
6. Returns to the dispatching council member

---

## Part 7 — Domain Skill Cross-References

For domain-specific research, delegate to the appropriate specialized skill:

| Domain | Skill | Key Topics |
|---|---|---|
| Logic, sets, algebra, category theory | `lean-math-foundations` | Typeclass tower, induction patterns, order theory |
| Real analysis, topology, measure theory | `lean-math-analysis` | Filters, continuity, differentiation, convex analysis |
| Nonlinear dynamics, Lyapunov, catastrophe | `lean-math-dynamical` | Phase portraits, bifurcation, control theory |
| Probability, Markov chains, time series | `lean-math-stochastic` | OKD dynamics, spectral gap, ergodic theory |
| Optimization, game theory, RL theory | `lean-math-optimization` | Bellman, Nash, multi-objective, decision theory |
| Graphs, lattices, DAGs, knowledge graphs | `lean-math-discrete` | Provenance DAGs, ontological reasoning, FSMs |
| AI safety, agentic, alignment | `lean-ai-formalization` | Safety envelopes, multi-agent, evolving agents |
| Knowledge rep, symbolic AI, legal reasoning | `lean-knowledge-formalization` | Argumentation, deontic logic, causal reasoning |
| Data/info security, access control | `lean-security-formalization` | CIA, BLP/RBAC, information flow, privacy |
| Intelligence analysis, strategy | `lean-applied-reasoning` | SATs, evidence reasoning, decision under uncertainty |
| Brainstorming, proof strategy design | `math-strategy-studio` | Problem decomposition, analogy, creative techniques |
| Rumsfeld matrix, coverage tracking | `epistemic-mapping` | Quadrant management, staleness, scoring |
| Project scheduling, milestones | `math-project-management` | WBS, critical path, risk, M0-M6 milestones |

### 7.1 Research Routing Decision

```
1. Is this a domain-specific question?
   YES → Consult the domain skill table above, extract the relevant methodology
   NO  → Use standard research methods (Part 2)

2. Is this an epistemic gap question?
   YES → Use epistemic mapping protocol (Part 5)
   NO  → Use standard research protocol

3. Does this need multiple domain perspectives?
   YES → Dispatch to Research Council for multi-member analysis
   NO  → Single researcher with domain skill reference suffices
```

---

## Part 8 — Research Anti-Patterns

| Anti-Pattern | Correction |
|---|---|
| Researching before reading the existing codebase | Always check Tactics.lean and the target module first |
| Deep research on trivial goals | Use `exact?` / `apply?` first — they often solve it directly |
| Ignoring lean-auto/Duper for first-order goals | Always try `auto` and `duper` before manual proof research |
| Not recording findings | Every non-trivial research produces at least one ZK note |
| Researching the same thing twice | Check ZK before starting — may already have the answer |
| Over-relying on one source | Cross-reference Mathlib docs, Zulip, and source code |
| Not verifying research findings | Always test recommended strategies in Lean before recommending |
| Importing packages without version check | Always verify compatibility with lakefile.lean versions |
| Skipping epistemic mapping | Every research MUST log epistemic transitions (Part 5.4) |
| No domain skill consultation | Always check if a specialized domain skill covers the topic (Part 7) |
| Ignoring Research Council for complex questions | Multi-domain or deep questions need council, not solo research |
| Not tracking UU discoveries | Unknown unknowns found during research must be logged immediately |

---

## Part 9 — Typed Research Protocols (M / T / L / S / D / X / E)

This skill absorbs the 7-type dispatch matrix previously hosted in
the standalone `lean-research-types` skill (now a redirect stub).  Use
the matrix when classifying an incoming research question; each type
has its own protocol headline, output template, and council routing.

### 9.1 Dispatch Matrix

| Research Type | Primary Skill | Council Member | Domain Skills |
|---|---|---|---|
| Type M (Mathematical) | `lean-research` | Γ (Methods) | math + domain clusters |
| Type T (Tactic / API) | `lean-proof-review` | Ν (Novelty) | — |
| Type L (Literature) | `lean-research` | Ε (Applications) | math + domain clusters |
| Type S (Safety / Soundness) | `lean-enforcement` | Σ (Soundness) | safety-relevant clusters |
| Type D (Design / Architecture) | `lean-specification` | Λ (Quality) | — |
| Type X (Cross-Domain) | domain skills | Β (Structure) | all domain clusters |
| Type E (Epistemic) | `epistemic-mapping` | Α (Foundations) | all |

### 9.2 Protocol Headlines

| Type | When | Protocol headline |
|---|---|---|
| M | Proving a theorem needing non-trivial mathematical insight | FORMALIZE → DECOMPOSE → SEARCH (internal/Mathlib/literature) → SYNTHESIZE → IMPLEMENT → VERIFY |
| T | Need the right tactic, lemma, or API for a specific goal | CLASSIFY goal type → TRY automated (`exact?` / `apply?` / `simp?` / `auto` / `duper`) → SEARCH Mathlib API → CHECK project custom tactics → REPORT |
| L | Need to understand what's known in formal-verification literature | DEFINE scope → SEARCH (Zettelkasten / Mathlib / Zulip / arXiv / Coq+Isabelle) → SYNTHESIZE → ZK OUTPUT |
| S | Verifying soundness, axiom-cleanliness, or safety relevance | AXIOM check → VACUITY check → FAITHFULNESS (delegate to Φ) → BOUNDARY check → CROSS-MODULE check |
| D | Deciding how to structure definitions, modules, or architecture | UNDERSTAND requirements → SURVEY patterns → EVALUATE options → PROTOTYPE → RECOMMEND |
| X | Connecting Lean formalization to domain knowledge | IDENTIFY domain → CONSULT domain skill → BRIDGE analysis → CROSS-REFERENCE → DOMAIN expert input |
| E | Probing for unknown unknowns or mapping knowledge coverage | RUN epistemic audit → DISPATCH targeted M/T/L for each KU → PROBE for UU (analogy / boundary / negation / counterexample) → UPDATE epistemic map |

### 9.3 Outputs

All seven types emit a structured deliverable using the per-type
template from
[`references/research-output-templates.md`](../../references/research-output-templates.md).
The Type-T entry also references the
[`theorem-search`](../../references/theorem-search.md) loop.

### 9.4 Queue & Budget

Multi-task scheduling (priority bands, parallelisation rules, budget
overrun handling) lives in
[`references/research-queue.md`](../../references/research-queue.md).
Budget overruns are a Trigger 1 (Confidence) signal under the HITL
contract.
