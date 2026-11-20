---
name: lean-corpus-audit-handbook
description: Unified reference handbook for @lean-corpus-audit (7-dimension QA engine,
  whole-corpus deep audit, and retroactive council onboarding).
extracted_from: skills/lean-corpus-audit/SKILL.md
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Whole-repository milestone health check | 7-dimension QA sweep | Run census + `proof_quality.py` + `FIDELITY-01..08` audit |
| Theorem `(a0 a1 a2 a3 : Nat)` fixed arity | `FIDELITY-08` (`OverConcreteFixedArity`) | Generalize to `List α` / `Fin n -> α` (`@lean-proof-refactor`) |
| `def checkFoo : Bool` with only `= true -> ...` | `FIDELITY-07` (`OneWayBoolChecker`) | Upgrade to bidirectional `iff` soundness + completeness |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Audit an existing Lean repo retroactively | `lean_metrics(action: "census")` + wave stratification | Audit Layer 0 foundations first before higher layers |
| Spot vacuous or truncated Nat theorems | Static fidelity scan (`FIDELITY-01..08`) | Route flagged declarations to `@lean-tautology-triage` |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Declaration census undercounts modules | Census ran mid-rebuild with partial `.olean` files | Finish `lake build` before running `lean_metrics` / `olean_census.lean` |
| High long-proof density (>80 LOC) | Monolithic tactic scripts without helper cuts | Dispatch batch to `@lean-proof-refactor` |

---

<!-- Merged from lean-quality-engine-handbook.md -->

# SK-39: Quality Assurance Engine

The QA Engine is the system-level quality assurance orchestrator. While individual skills handle specific aspects (enforcement scripts check mechanics, council reviews check semantics, retroactive audit checks coverage), this skill coordinates them into a unified quality lifecycle.

---

## Part 1 -- Quality Dimensions

Quality in a formal verification project has 7 dimensions:

| # | Dimension | Checked By | Gate |
|---|---|---|---|
| Q1 | **Soundness** | Axiom audit, Σ review, sorry check | Hard gate: blocks everything |
| Q2 | **Faithfulness** | Φ review, doc-requirements traceability | Hard gate: blocks paper claims |
| Q3 | **Completeness** | Coverage matrix, review coverage | Soft gate: may proceed with gaps |
| Q4 | **Novelty** | Ν review, duplicate detection | Advisory |
| Q5 | **Elegance** | Λ review, proof_quality.py | Advisory |
| Q6 | **Integration** | Ω review, bridge_validator.py | Soft gate |
| Q7 | **Documentation** | metric_sync.py, Zettelkasten lint | Soft gate |

### 1.1 Quality Score

```
Q_score = (Q1_weight × Q1) + (Q2_weight × Q2) + ... + (Q7_weight × Q7)

Where:
  Q1 (Soundness):     weight = 30, score = 100 if zero sorry + clean axioms, else 0
  Q2 (Faithfulness):  weight = 25, score = % of claims with faithful formalization
  Q3 (Completeness):  weight = 20, score = coverage_matrix.covered / total_claims × 100
  Q4 (Novelty):       weight = 5,  score = 100 - (duplicate_count / theorem_count × 100)
  Q5 (Elegance):      weight = 5,  score = 100 - (long_proofs + unused_hyps) / theorem_count × 100
  Q6 (Integration):   weight = 10, score = 100 if bridge_validator passes, else 50
  Q7 (Documentation): weight = 5,  score = 100 if metric_sync passes, else based on coverage
```

### 1.2 Quality Levels

| Level | Score | Meaning |
|---|---|---|
| 🟢 **Exemplary** | 95--100 | Publication-ready |
| 🔵 **Good** | 80--94 | Solid, minor improvements possible |
| 🟡 **Acceptable** | 60--79 | Functional but gaps exist |
| 🟠 **Needs Work** | 40--59 | Significant quality issues |
| 🔴 **Critical** | 0--39 | Soundness or faithfulness issues |

---

## Part 2 -- QA Gates

### 2.1 Per-Theorem Gate

Before a theorem is marked "complete":

```
GATE: Theorem Completion
  MUST:
    □ Builds clean (no errors)
    □ No sorry in theorem body
    □ #print axioms shows no sorryAx
    □ At least 1 council member reviewed (Star or Pipeline)
  SHOULD:
    □ Full 5-member council review
    □ Specification exists (SK-05)
    □ Coverage matrix entry updated
    □ ZK note if novel pattern
```

### 2.2 Per-Module Gate

Before a module is marked "audited":

```
GATE: Module Audit Complete
  MUST:
    □ All theorems pass Per-Theorem Gate
    □ autoImplicit false set
    □ Module docstring present
    □ Section headers (-- §N)
    □ bridge_validator.py passes for this module
  SHOULD:
    □ proof_quality.py has no P1 findings for this module
    □ All theorems have specifications
    □ Coverage matrix shows >90% for this module's claims
    □ ZK permanent notes for patterns discovered
```

### 2.3 Project Milestone Gate

Before any project milestone:

```
GATE: Project Milestone
  MUST:
    □ enforce_all.sh exits 0
    □ Zero sorry across entire project
    □ Axiom audit clean (no sorryAx)
    □ Coverage matrix >80% overall
    □ All P0 findings resolved
    □ All P1 findings resolved or documented
  SHOULD:
    □ Coverage matrix >90% overall
    □ metric_sync.py shows no mismatches
    □ Zettelkasten has at least 1 note per module
    □ All modules council-reviewed at least once
    □ enforce_all.sh --strict exits 0
```

---

## Part 3 -- QA Lifecycle

### 3.1 Development Phase

During active development:
- Run `council_precheck.sh` before every review session
- Run `proof_quality.py` weekly
- Run `zettelkasten_lint.py` weekly
- Quality score tracking: monthly

### 3.2 Retroactive Audit Phase

During RETRO protocol:
- Run `retro_recon.py` at Phase R start
- Run `axiom_audit.py` at each wave completion
- Run `review_coverage.py` to track audit progress
- Run `bridge_validator.py` when modules change
- Quality score tracking: per wave

### 3.3 Steady-State Phase

After RETRO completes:
- Run `enforce_all.sh` before every milestone
- Run `metric_sync.py` before paper submissions
- Run `ecosystem_health.py` when skills change
- Quality score tracking: per RALPH project iteration

---

## Part 4 -- Resilience & Creativity Enforcement

### 4.1 Resilience Patterns

Resilience means the formalization project can handle:
- Library upgrades (Mathlib version bumps)
- Requirement changes (paper revisions)
- Personnel changes (new contributors)
- Tool changes (new tactics, automation)

**How enforced:**

| Resilience Aspect | Enforcement |
|---|---|
| API stability | bridge_validator.py + regression tests (nightly-testing SK-34) |
| Knowledge preservation | Zettelkasten + specifications (findable by anyone) |
| Convention consistency | council_precheck.sh + style checks |
| Process continuity | RETRO tracking documents + health dashboard |

### 4.2 Creativity Support

Creativity in a formal verification context means:
- Novel proof strategies (not just omega/simp for everything)
- Cross-domain connections (bridges between modules)
- Elegant formulations (simplifying complex concepts)
- New abstractions (reusable patterns in Tactics.lean)

**How supported:**

| Creativity Aspect | Support Mechanism |
|---|---|
| Strategy diversity | math-strategy-studio (SK-25) brainstorming sessions |
| Cross-domain connections | research-council (SK-22) multi-member analysis |
| Elegance | Λ (Quality Architect) review focus |
| New abstractions | lean-specification (SK-05) design phase |

### 4.3 Tactic Diversity Metric

```python
# Tactic diversity: higher = more diverse proof techniques
diversity = len(unique_tactics_used) / len(total_tactic_invocations)

# Target: diversity > 0.3 (at least 30% of tactic uses are distinct)
# Red flag: diversity < 0.15 (over-reliance on 1-2 tactics)
```

---

## Part 5 -- Reliability Engineering

### 5.1 Build Reliability

```
Build success rate = successful_builds / total_build_attempts
Target: 100% on main branch
```

Enforced by: `council_precheck.sh` (build check) + nightly-testing (SK-34)

### 5.2 Review Reliability

```
Review coverage = theorems_with_review_record / total_theorems
Target: 100% for modules in steady state
```

Enforced by: `review_coverage.py`

### 5.3 Axiom Reliability

```
Axiom cleanliness = modules_with_clean_axioms / total_modules
Target: 100%
```

Enforced by: `axiom_audit.py`

### 5.4 Reliability Dashboard

```markdown
# Reliability Dashboard
| Metric | Value | Target | Status |
|---|---|---|---|
| Build success rate | 100% | 100% | 🟢 |
| Review coverage | 85% | 100% | 🟡 |
| Axiom cleanliness | 100% | 100% | 🟢 |
| Coverage matrix | 78% | 90% | 🟡 |
| Sorry count | 0 | 0 | 🟢 |
| Convention compliance | 95% | 100% | 🟢 |
| ZK health | 3 orphans | 0 | 🟡 |
| Metric sync | 2 stale | 0 | 🟡 |
```

---

## Part 6 -- Continuous Improvement

### 6.1 Quality Trend Tracking

After each QA gate check, record the quality score over time:

```markdown
| Date | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Total |
|---|---|---|---|---|---|---|---|---|
| 2025-07-18 | 100 | 75 | 78 | 95 | 85 | 100 | 60 | 83.5 |
| 2025-07-25 | 100 | 80 | 82 | 95 | 87 | 100 | 75 | 86.8 |
| 2025-08-01 | 100 | 85 | 88 | 97 | 88 | 100 | 90 | 91.0 |
```

### 6.2 Retrospective Protocol

After every milestone:
1. Run full `enforce_all.sh --strict`
2. Compute quality score
3. Identify the weakest dimension
4. Create improvement plan targeting that dimension
5. Update enforcement scripts if new checks needed
6. Record retrospective in Zettelkasten permanent note

### 6.3 Skill Improvement Feedback

When QA discovers systemic issues:
- Pattern: same issue across modules → update lean-proof-review checklist
- Pattern: confusion about process → update relevant skill documentation
- Pattern: enforcement gap → create new enforcement script
- Pattern: new best practice → create Zettelkasten permanent note + update skills

---

## Part 7 -- QA Anti-Patterns

| Anti-Pattern | Why It's Bad | Correction |
|---|---|---|
| Quality theater | Running scripts without acting on findings | Every finding gets a todo |
| Over-gating | Blocking work for P3 issues | Hard gates only for Q1+Q2 |
| Score gaming | Removing theorems to improve coverage % | Track absolute counts too |
| Metric blindness | Only checking what scripts measure | Council review catches semantic issues |
| Retroactive quality debt | "We'll clean up later" | Fix P0/P1 before adding new theorems |
| Ignoring trends | Only looking at current score | Track over time, alert on regression |
| Single-dimension focus | Only caring about soundness | All 7 dimensions matter for publication |

---

## See also

- [`../../templates/Template_Verification.md`](../../templates/core/Template_Verification.md) -- Template: Axiom auditing and test completeness
- [`../../templates/Template_Performance.md`](../../templates/core/Template_KernelWHNF.md) -- Template: Build-perf, parallelism, tactic speed
- [`../../scripts/lean/`](../../scripts/lean/) -- Runnable enforcement scripts (axiom audit, import hygiene, proof quality)

---

## Operational Details (from `skills/lean-quality-engine/SKILL.md`)

# lean-quality-engine

> ⚠️ **MANDATORY** (hot-tier): the soundness and faithfulness gates in
> §Behavioural rules are hard gates -- a failure HALTS the QA lifecycle.
> Skipping Persist = incomplete.

## Routing

- **USE FOR:** running the seven-dimension quality lifecycle (Q1 soundness, Q2 faithfulness, Q3 completeness, Q4 novelty, Q5 elegance, Q6 integration, Q7
  documentation); computing the weighted `Q_score`; deciding go/no-go at a milestone.
- **DO NOT USE FOR:** running a single script (delegate to `@lean-enforcement`); reviewing one proof (delegate to `@lean-proof-review`); facilitating a
  council session (delegate to `@lean-review-council`).
- **TRIGGERS:** QA, quality gate, milestone check, project health, qa-engine, quality score, QA lifecycle.

## Behavioural rules (G-*)

- **G-1** (MUST): Q1 (soundness) and Q2 (faithfulness) MUST both pass before any other dimension is scored. [Trace: AC-01]
- **G-2** (MUST): A failed hard gate (Q1 or Q2) MUST halt the lifecycle and route to recovery, regardless of other dimension scores. [Trace: AC-02]
- **G-3** (MUST): Every dimension score MUST cite the underlying script or review record (no inferred scores). [Trace: AC-03]
- **G-4** (SHOULD): Soft gates (Q3, Q6, Q7) SHOULD report gaps but MAY proceed when the owner has accepted the risk in writing. [Trace: AC-04]
- **G-5** (MUST NOT): The engine MUST NOT re-implement checks owned by `@lean-enforcement`; it MUST call out to that skill. [Trace: AC-05]
- **G-6** (MUST): The weighted `Q_score` MUST be persisted to the repository's quality tracker with timestamp, commit, and per-dimension breakdown. [Trace:
  AC-06]
- **G-7** (SHOULD): When `Q_score` regresses ≥ 5 % vs prior milestone, the engine SHOULD escalate before proceeding. [Trace: AC-07]
- **G-8** (MUST): On any guard failure the skill MUST escalate per §Recovery & STOP. [Trace: AC-08]

## Workflow

1. **Discover** [discover] -- read prior `Q_score`, list active milestone, locate latest enforcement / council / coverage artefacts.
2. **Run hard gates** [execute] -- invoke `@lean-enforcement` for Q1 (axiom audit, sorry check, `lean_diagnostics` static abstract interpretation
   certificates: `NatSubTruncation`, `NatDivModByZero`, Zone DBM `decreasing_by` synthesis, Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop
   widening, trace partitioning) and Q2 (faithfulness via doc-requirements traceability and `lean_counterexample_search` with Galois-guided hypothesis
   domain pruning `analyzeHeaderHypothesisDomains` / `pruneHeaderNatDomain`).
3. **Halt-check** [validate] -- if Q1 or Q2 failed, STOP and route to recovery; do NOT proceed to soft gates.
4. **Run soft gates** [execute] -- coverage (Q3), novelty (Q4), elegance (Q5 via `proof_quality.py`, `lean-rules` via `node
   tools/lean-lsp-mcp/bin/lean-rules.js`, and `pi-lens` via `pilens_ast_grep_search` / `pilens_diagnostics` as sub-second structural pre-checks before
   `lake build`), integration (Q6 via `bridge_validate.py` and `pi-harness-bridge` policy gates), documentation (Q7) via the appropriate scripts and
   council snapshots.
5. **Score** [validate] -- compute weighted `Q_score`; compare to prior milestone; flag regressions ≥ 5 %.
6. **Persist** [persist] *(MANDATORY)* -- write the `Q_score` breakdown to the project tracker, update milestone status, tick the QA checklist. Skipping
   Persist = incomplete.

## Recovery & STOP

- Q1 or Q2 fails → immediate STOP; escalate to human; do NOT compute `Q_score`.
- Enforcement script crashes ×3 in one lifecycle → STOP, file a bug against `@lean-enforcement`.
- `Q_score` regression ≥ 10 % vs prior milestone → STOP, ask before persisting.
- Confidence < 90 % on dimension weighting → STOP, ask.

## Handoffs

- **Predecessors / successors:** see FM `handoffs`.
- **Source spec:** `specs/lean/quality-engine/requirements.md` -- every G-rule traces to an AC there.
- **Reference:** see [`REFERENCE.md`](lean-corpus-audit-handbook.md) for the seven-dimension matrix, weights, lifecycle phases, anti-patterns, and reliability-engineering
  details (original v1 content, preserved verbatim).

## Common failure modes

> AI agents commonly: score soft gates before hard gates pass; persist a `Q_score`
> that includes a failed hard gate; re-implement an enforcement check inline
> instead of calling `@lean-enforcement`; skip the regression delta against prior
> milestone. Full registry: GUARDRAILS.md §Agent failure taxonomy.


---

<!-- Merged from lean-deep-audit-handbook.md -->

# The Deep-Audit Program (whole-corpus, seven lenses)

## Why

Per-theorem review scales linearly with attention and decays with
session turnover. A deep audit is a PROGRAM: mechanical censuses first
(deterministic, re-runnable, seconds), human verdicts second (bounded
lists), remediations tracked to closure with evidence. Every finding
is registered even when the disposition is "belong to another lane" -
an unregistered finding gets rediscovered.

## Workflow (run priorities in this order)

1. **P1 - Trust-base lockdown.** Every declaration's transitive axiom
   closure restricted to the declared allowlist, enforced in the normal
   build. EXECUTOR: the `lean-axiom-closure` skill (vendored metaprogram
   + FinalCheck consumer). Expected first catches: `sorryAx` behind
   wrappers/aliases, `native_decide` (`Lean.ofReduceBool`), custom
   axioms.
2. **P2 - Literature faithfulness, tower by tower.** For each
   foundational module: read every core definition; compare with the
   cited formula; classify faithful-formula / scoped-specialization /
   free-record-proxy. The proxy signature: a structure with free
   fields + arithmetic defs over those fields + projection-style
   theorems, while the module prose narrates mathematics the code
   never touches. Template-residue corroborating evidence: placeholder
   author strings, identical skeleton across a file family, imports
   that do not reach the claimed subject area. Disposition for guest
   material belongs to the owning lane under whatever guest-corpus
   contract exists - register, do not auto-delete.
3. **P3 - Spec-baking scan.** `tautology_scan.py` (references/scripts/):
   theorems whose entire proof body is a trivial form (`rfl`, bare
   `simp`, `decide`, `assumption`) or a bare hypothesis/projection
   (`h.1`). Candidates, not verdicts: triage each as definitional-ok /
   rewrite-the-statement / own-lane. Keep the human verdict layer
   separate from the generated report (regeneration must not lose it).
4. **P4 - Inhabitation census.** `deep_audit_census.py` (P4 half):
   every structure/class/inductive - instance/deriving-witnessed,
   term-witnessed, or unexplained. The unexplained list is a REVIEW
   LIST, not a defect count: classify parameterized instances the
   scanner cannot see, proof-only types where inhabitation is
   meaningless, genuinely uninhabited-but-meaningful (add witnesses),
   and vacuous types with unsatisfiable fields (the real catch).
5. **P5 - Type continuity.** `deep_audit_census.py` (P5 half): type
   basenames declared in more than one module (duplication candidates:
   same-concept-redeclared -> consolidate; same-name-different-concept
   -> rename), plus the shared-foundation ranking (true foundations
   are the basenames referenced by the most modules).
6. **P6 - Sign/domain/index pilot.** Review ONE order-trap tower with
   the checklist: ordering hypotheses structural (fields, not
   preconditions); boundary ties explicit + theorem-backed; severity/
   order maps total + injective + extremes proven; sign exposure
   Nat-pipeline preferred, every Real op domain-proven; concrete cases
   by `decide`; cross-hierarchy bridges operational-equivalence-proven
   OR no-go-documented; scale mismatches guarded in docstrings. Then
   generalize the checklist to the remaining towers.
7. **P7 - Statement-shape review.** Per-declaration verdicts (keep /
   subsumed-by-mathlib / packaging-honest-statement) over the generic
   towers, with every mathlib adjacency consumed rather than
   duplicated. Zero-coverage claims require a grep over the pinned
   mathlib tree, never recollection.
8. **P8 - Remediation queue.** Every finding lands with: what, where,
   severity, disposition owner. Close findings same-session when the
   fix is one theorem or one docstring; route the rest with precise
   pointers.

## Cross-cutting disciplines (G-*)

- **G-1** (MUST): evidence before verdicts - a missing bridge, a gap,
  or a zero-coverage claim is stated only after a grep / `lake env lean`
  `#check` proves it. One pilot's wrong conjecture corrected on evidence
  is a success, not a failure; an uncorrected one is not.
- **G-2** (MUST): censuses are deterministic scripts (commit them),
  reports are generated artifacts, verdicts are human layers - keep the
  layers separable so regeneration never loses analysis.
- **G-3** (MUST): every remediation carries its owner; a finding
  without an owner is a wish.
- **G-4** (SHOULD): re-run censuses after landing fixes - reports drift
  as the corpus moves under them.

## Pitfalls

- The naive reference-count loop (per-line x per-basename) is
  O(lines x types) and times out on real corpora; the two-pass
  precompiled-alternation form runs in seconds (the shipped script does
  this).
- Instance regexes see simple-identifier forms only
  (`instance : Inhabited T`); parameterized instances
  (`Inhabited (T x)`) land in the unexplained list by construction -
  that is what the review pass is for.
- Scanner line numbers drift with any upstream edit; re-run before
  quoting them.
- Guest/template families inflate proxy findings; their disposition is
  governance (owner decision), not the auditor's.

## Verification

- Each census: re-runs byte-identical on an unchanged corpus; counts
  quoted with the run command.
- P1: the build fails on a deliberately introduced `sorry` (verify the
  failure path once during setup).
- The program itself: the remediation queue only ever shrinks by
  closure commits or owner-routing records - never by silence.

## Recovery

- If a census script times out or drifts after upstream edits, re-run the precompiled two-pass scanner on a clean tree before quoting line numbers or counts.
- If a module family is guest or template material, register the finding in the remediation queue and escalate disposition to the owning lane rather than
  deleting modules unilaterally.

## Handoffs

- **Predecessors:** `@lean-gateway` (top-level routing), `@lean-quality-engine` (project QA orchestration).
- **Successors:** `@lean-axiom-closure` (P1 executor), `@lean-tautology-triage` (P3 candidate triage), `@lean-proof-review` (per-module review).

## See also

- [`references/scripts/tautology_scan.py`](../../scripts/lean/proof_quality.py) - P3 spec-baking and trivial-proof scanner.
- [`references/scripts/deep_audit_census.py`](../../scripts/lean/formalization_breakdown.py) - P4 inhabitation and P5 type-continuity census scanner.


---

<!-- Merged from lean-retroactive-audit-handbook.md -->

# Lean Retroactive Audit Handbook

> **Layering note.** This file holds the deep content previously
> embedded in [`skills/lean-retroactive-audit/SKILL.md`](../../skills/lean-corpus-audit/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + a parts index. This file holds the full
> encyclopaedia. Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- The Retroactive Challenge

Existing projects have:
- Theorems with no specification documents
- Proofs with no review records
- Implicit knowledge not captured in Zettelkasten
- Paper cross-references that may be incomplete or stale
- Convention violations accumulated over time
- Possible undetected pitfalls, duplicates, or missing hypotheses

The retroactive audit creates a **baseline** and then systematically raises every artifact to full council-reviewed status.

---

## Part 2 -- Phase 0: Discovery

### 2.1 Automated Census

Run the census script to extract the project's current state:

```bash
# Count theorems, definitions, sorry instances per module
for f in the project/*.lean; do
  module=$(basename "$f" .lean)
  thms=$(grep -c "^theorem\|^lemma" "$f")
  defs=$(grep -c "^def\|^structure\|^inductive\|^class" "$f")
  sorries=$(grep -c "sorry" "$f")
  echo "$module: $thms theorems, $defs defs, $sorries sorry"
done

# Extract all theorem names
grep -n "^theorem\|^lemma" Project/*.lean > docs/tracking/theorem_census.txt

# Check axioms for all modules
for f in the project/*.lean; do
  module=$(basename "$f" .lean)
  echo "=== $module ===" >> docs/tracking/axiom_audit.txt
  # Each theorem's axioms would be checked via lean script
done

# Convention check
grep -L "autoImplicit false" Project/*.lean  # modules missing autoImplicit
grep -c "^/-!" Project/*.lean  # modules with/without module docstrings
```

### 2.2 Dependency Graph Extraction

```bash
# Extract import graph
grep "^import Project" Project/*.lean | sed 's/import //' > docs/tracking/import_graph.txt
```

### 2.3 Paper Coverage Mapping

For each section in `project-tufte.tex`:
1. List all mathematical claims (equations, propositions, corollaries)
2. For each claim, search for a corresponding theorem in the Lean codebase
3. Record in coverage matrix: `{claim, module, theorem_name, status}`

Status values: `covered` | `partial` (theorem exists but doesn't match exactly) | `uncovered` | `no-claim` (theorem with no paper counterpart)

---

## Part 3 -- Phase 1: Baseline Establishment

### 3.1 Per-Module Baseline Report

For each module, produce (using Pipeline topology -- Σ, Φ, Ν, Λ, Ω in sequence):

```markdown
# Baseline Report: Project/[Module].lean
## Date: [ISO-8601]
## Auditor: Retroactive Audit Council

### Census
- Lines: [N]
- Theorems: [N]
- Definitions: [N]
- Sorry count: [N]
- `#print axioms` status: [clean / N issues]

### Convention Compliance
- [ ] `set_option autoImplicit false` present
- [ ] Module docstring (`/-! ... -/`) present
- [ ] Section headers (`-- §N`) present and sequential
- [ ] Naming conventions followed: [N violations]
- [ ] Paper cross-reference in module header

### Quick Scan (per member)
- Σ: [N] axiom issues ([N] sorry, [N] trustCompiler)
- Φ: [N] suspected statement issues (to be verified in deep audit)
- Ν: [N] potential duplicates (to be verified)
- Λ: [N] quality anti-patterns (to be verified)
- Ω: [N] convention violations

### Priority Classification
[P0/P1/P2/P3 -- should this module be deeply audited first or last?]

### Estimated Deep Audit Effort
[N theorems × [est. time per theorem] = total]
```

### 3.2 Project Baseline Summary

Aggregated from all module baselines:

```markdown
# Project Baseline Summary
## Total: [N] lines, [N] theorems, [N] definitions, [N] sorry
## Paper coverage: [N/M] claims covered ([X]%)
## Convention compliance: [N/M] modules fully compliant ([X]%)
## Axiom cleanliness: [N/M] modules clean ([X]%)

### Audit Schedule
| Wave | Modules | Priority | Est. theorems |
|---|---|---|---|
| 1 | Tactics | P0 (shared dep) | 44 |
| 2 | QualityGates | P1 | 39 |
| ... | ... | ... | ... |
```

---

## Part 4 -- Phase 2: Incremental Deep Audit

### 4.1 Audit Schedule

Modules are audited in dependency order (upstream first), matching the Mesh topology waves:

```
Wave 1: Tactics (all other modules depend on this)
Wave 2: QualityGates
Wave 3: PhaseClassification, PipelineAdaptive
Wave 4: CCVGating, PhasePortrait
Wave 5: CuspCatastrophe, ProvenanceChain
Wave 6: LyapunovStability
Wave 7: ReinforcementLearning
Wave 8: AgenticSafety, StochasticCCV
```

Within each wave, independent modules are audited in parallel (separate council instances).

### 4.2 Per-Theorem Deep Audit

For each theorem in the current wave, the council executes a full RALPH cycle using Star topology:

```
PARALLEL:
  Σ → run #print axioms, check sorry chain
  Φ → translate to English, check hypotheses, cross-ref paper
  Ν → run exact?, check Tactics.lean, classify novelty
  Λ → count steps, check tactics, assess quality
  Ω → check conventions, naming, section placement
SYNC → vote → record in module review report
```

### 4.3 Retroactive Specification Generation

Each audited theorem gets a **retroactive specification**:

```markdown
# Retroactive Spec: [RETRO-YYYYMMDD-NNN]
## Theorem: [name]
## Module: Project/[Module].lean
## Line: [N]

### Reverse-Engineered Requirement
- Paper claim: [mapped from coverage matrix, or "no direct claim"]
- English statement: [Φ's translation]
- Hypotheses: [as-is from the Lean signature]
- Missing hypotheses (if any): [Φ's findings]

### Proof Assessment
- Axioms: [Σ's report -- clean / issues]
- Novelty: [Ν's classification]
- Quality score: [Λ's assessment]
- Convention compliance: [Ω's report]

### Recommended Actions
- [ ] [Action 1 -- e.g., "add missing hypothesis h : n > 0"]
- [ ] [Action 2 -- e.g., "replace bare aesop with aesop? output"]
- [ ] [Action 3 -- e.g., "add docstring"]
```

### 4.4 Fix Prioritization

After auditing a module, fixes are prioritized:

| Priority | Category | Examples |
|---|---|---|
| P0 | `sorry` removal, axiom contamination | `sorryAx` in dependency chain |
| P1 | Statement correctness | Missing hypothesis, vacuous truth |
| P2 | Quality improvement | Replace opaque tactics, add `calc` blocks |
| P3 | Convention alignment | Naming, docstrings, section headers |

---

## Part 5 -- Phase 3: Gap Analysis and Extension

After all modules are baseline-audited:

### 5.1 Coverage Gaps

From the coverage matrix, identify:
- Paper claims with no corresponding theorem → create specifications
- Theorems with no paper claim → document rationale or flag for review
- Partial coverage (theorem exists but doesn't match exactly) → revise theorem or create additional lemma

### 5.2 Cross-Module Gaps

From the dependency graph and bridge theorem inventory:
- Module pairs with expected but missing bridge theorems
- One-directional bridges that should be bidirectional
- Orphan theorems not referenced by any downstream module

### 5.3 Knowledge Gaps

From the Zettelkasten (populated during the audit):
- Areas with many fleeting notes but no permanent synthesis
- Tags with no notes (expected coverage but no observations)
- Literature notes with no corresponding formal verification

---

## Part 6 -- Phase 4: Steady-State Transition

### 6.1 Transition Criteria

The project transitions from "retroactive audit" to "steady-state review" when:

- [ ] All modules have baseline reports
- [ ] All P0 issues resolved (zero sorry, clean axioms)
- [ ] All P1 issues resolved or documented with caveats
- [ ] Coverage matrix is >90% for paper claims
- [ ] Every module has been through at least one full council review
- [ ] Zettelkasten has permanent notes for major proof patterns
- [ ] All skills are calibrated to project-specific conventions

### 6.2 Post-Transition Protocol

After transition:
- New theorems follow the specification → council review pipeline
- Changes to existing theorems trigger incremental council review
- Zettelkasten is maintained by ongoing synthesis
- Skills are updated based on accumulated permanent notes
- Enforcement scripts run in CI

---

## Part 7 -- Parallel Audit Dispatch

### Maximum Parallelism Strategy

```
Phase 0 (Discovery):
  PARALLEL:
    census_agent → automated census
    depgraph_agent → dependency graph
    coverage_agent → paper coverage mapping

Phase 1 (Baseline):
  FOR EACH module (in dependency wave order):
    PARALLEL (within a wave):
      council_instance_A → baseline(module_1)
      council_instance_B → baseline(module_2)
    SEQUENTIAL (across waves):
      wave_1 complete → wave_2 starts

Phase 2 (Deep Audit):
  FOR EACH wave:
    FOR EACH module IN wave (PARALLEL):
      FOR EACH theorem IN module (PARALLEL, batched):
        council → Star topology review
        spec_agent → retroactive specification
        doc_agent → documentation update
      SYNC module → module review report
    SYNC wave

Phase 3 (Gap Analysis):
  PARALLEL:
    coverage_agent → gap identification
    crossmod_agent → bridge gap analysis
    zk_agent → knowledge gap synthesis

Phase 4 (Transition):
  SEQUENTIAL:
    verify all criteria → transition to steady state
```

### Agent Cascade on Completion

When any audit agent completes:
1. Record results in tracking documents
2. If theorem passes → launch doc_agent for retroactive spec
3. If theorem fails → launch todo_agent to create fix tasks
4. If fix tasks created → launch implementer_agent for P0 tasks immediately
5. If module complete → launch report_agent for module review report
6. If wave complete → launch next wave's audit councils

