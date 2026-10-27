---
name: "lean-quality-engine-handbook"
description: "Reference handbook for @lean-quality-engine."
extracted_from: "skills/lean-quality-engine/SKILL.md"
---

# SK-39: Quality Assurance Engine

The QA Engine is the system-level quality assurance orchestrator. While individual skills handle specific aspects (enforcement scripts check mechanics, council reviews check semantics, retroactive audit checks coverage), this skill coordinates them into a unified quality lifecycle.

---

## Part 1 — Quality Dimensions

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
| 🟢 **Exemplary** | 95–100 | Publication-ready |
| 🔵 **Good** | 80–94 | Solid, minor improvements possible |
| 🟡 **Acceptable** | 60–79 | Functional but gaps exist |
| 🟠 **Needs Work** | 40–59 | Significant quality issues |
| 🔴 **Critical** | 0–39 | Soundness or faithfulness issues |

---

## Part 2 — QA Gates

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

## Part 3 — QA Lifecycle

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

## Part 4 — Resilience & Creativity Enforcement

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

## Part 5 — Reliability Engineering

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

## Part 6 — Continuous Improvement

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

## Part 7 — QA Anti-Patterns

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

- [`../../templates/Template_Verification.md`](../../templates/Template_Verification.md) — Template: Axiom auditing and test completeness
- [`../../templates/Template_Performance.md`](../../templates/Template_Performance.md) — Template: Build-perf, parallelism, tactic speed
- [`../../scripts/lean/`](../../scripts/lean/) — Runnable enforcement scripts (axiom audit, import hygiene, proof quality)

---

## Operational Details (from `skills/lean-quality-engine/SKILL.md`)

# lean-quality-engine

> ⚠️ **MANDATORY** (hot-tier): the soundness and faithfulness gates in
> §Behavioural rules are hard gates — a failure HALTS the QA lifecycle.
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

1. **Discover** [discover] — read prior `Q_score`, list active milestone, locate latest enforcement / council / coverage artefacts.
2. **Run hard gates** [execute] — invoke `@lean-enforcement` for Q1 (axiom audit, sorry check, `lean_diagnostics` static abstract interpretation
   certificates: `NatSubTruncation`, `NatDivModByZero`, Zone DBM `decreasing_by` synthesis, Octagon conservation `±x_i ± x_j <= c`, Bourdoncle WTO loop
   widening, trace partitioning) and Q2 (faithfulness via doc-requirements traceability and `lean_counterexample_search` with Galois-guided hypothesis
   domain pruning `analyzeHeaderHypothesisDomains` / `pruneHeaderNatDomain`).
3. **Halt-check** [validate] — if Q1 or Q2 failed, STOP and route to recovery; do NOT proceed to soft gates.
4. **Run soft gates** [execute] — coverage (Q3), novelty (Q4), elegance (Q5 via `proof_quality.py`, `lean-rules` via `node
   tools/lean-lsp-mcp/bin/lean-rules.js`, and `pi-lens` via `pilens_ast_grep_search` / `pilens_diagnostics` as sub-second structural pre-checks before
   `lake build`), integration (Q6 via `bridge_validate.py` and `pi-harness-bridge` policy gates), documentation (Q7) via the appropriate scripts and
   council snapshots.
5. **Score** [validate] — compute weighted `Q_score`; compare to prior milestone; flag regressions ≥ 5 %.
6. **Persist** [persist] *(MANDATORY)* — write the `Q_score` breakdown to the project tracker, update milestone status, tick the QA checklist. Skipping
   Persist = incomplete.

## Recovery & STOP

- Q1 or Q2 fails → immediate STOP; escalate to human; do NOT compute `Q_score`.
- Enforcement script crashes ×3 in one lifecycle → STOP, file a bug against `@lean-enforcement`.
- `Q_score` regression ≥ 10 % vs prior milestone → STOP, ask before persisting.
- Confidence < 90 % on dimension weighting → STOP, ask.

## Handoffs

- **Predecessors / successors:** see FM `handoffs` (grammar from ADR-0080).
- **Source spec:** `specs/lean/quality-engine/requirements.md` — every G-rule traces to an AC there.
- **Related ADRs:** ADR-0076, ADR-0080.
- **Reference:** see [`REFERENCE.md`](./REFERENCE.md) for the seven-dimension matrix, weights, lifecycle phases, anti-patterns, and reliability-engineering
  details (original v1 content, preserved verbatim).

## Common failure modes

> AI agents commonly: score soft gates before hard gates pass; persist a `Q_score`
> that includes a failed hard gate; re-implement an enforcement check inline
> instead of calling `@lean-enforcement`; skip the regression delta against prior
> milestone. Full registry: GUARDRAILS.md §Agent failure taxonomy.
