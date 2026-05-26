---
name: lean-doc-feedback
description: Bidirectional feedback loop between Lean 4 formalization and source documents. Use when Lean results should update the paper, or when paper changes should trigger re-verification. Covers automated gap detection, erratum generation, insight propagation, coverage synchronization, and the full paper-code alignment lifecycle.
---

# SK-37: Document-Results Feedback Loop

This skill bridges lean-doc-requirements (SK-09, forward direction: doc → Lean) and lean-doc-improvement (SK-10, reverse direction: Lean → doc) into a single bidirectional feedback system.

---

## Part 1 — The Feedback Cycle

```
    ┌─────────────────────────────────────────────┐
    │                                             │
    ▼                                             │
  DOCUMENT                                     DOCUMENT
  (paper)                                      UPDATE
    │                                             ▲
    │ Extract claims (SK-09)                      │ Apply corrections (SK-10)
    ▼                                             │
  REQUIREMENTS ──────────────────────────── RESULTS
    │                                             ▲
    │ Create specs (SK-05)                        │ Council review (SK-03)
    ▼                                             │
  SPECIFICATIONS ──► IMPLEMENTATION ──► PROOF ────┘
```

The cycle runs continuously: every proof completion triggers a backward check, every paper edit triggers a forward check.

---

## Part 2 — Forward Path (Document → Lean)

### 2.1 Trigger: Paper Section Changed

When a paper section is edited:

```
1. Detect changed section (git diff or manual trigger)
2. Re-extract claims for that section (SK-09 protocol)
3. Compare extracted claims with existing coverage matrix
4. For each NEW claim:
   a. Create specification (SK-05)
   b. Prioritize in triage (P1 if theorem, P2 if bound)
   c. Route to implementer
5. For each MODIFIED claim:
   a. Find corresponding Lean theorem
   b. Check if modification affects the formal statement
   c. IF yes: flag for Φ review, may need re-proof
   d. IF no: update coverage matrix metadata only
6. For each REMOVED claim:
   a. Mark corresponding theorem as "orphan" in coverage matrix
   b. Keep the theorem (don't delete proven code)
   c. Route to Ω for reclassification
```

### 2.2 Trigger: New Document Added

When a new document enters the project:

```
1. Run full extraction (SK-09) on entire document
2. Cross-reference all claims against existing Lean code
3. Produce: new_claims.md, already_covered.md, partial_coverage.md
4. Route new claims through the specification pipeline
5. Update project coverage matrix
```

### 2.3 Gap Detection

The forward path automatically detects coverage gaps:

| Gap Type | Detection Method | Action |
|---|---|---|
| Missing theorem | Claim extracted, no Lean match | Create specification |
| Partial coverage | Lean theorem exists but missing hypotheses | Flag for Φ review |
| Stale theorem | Paper claim changed, Lean theorem outdated | Re-specification |
| Orphan theorem | Lean theorem exists, paper claim removed | Reclassify |

---

## Part 3 — Backward Path (Lean → Document)

### 3.1 Trigger: Theorem Proven

When a theorem is proven and council-reviewed:

```
1. Update coverage matrix: claim → "covered"
2. Check if proof required ADDITIONAL hypotheses not in paper
   → YES: Generate erratum entry (hypothesis gap)
3. Check if proof achieved STRONGER result than paper claims
   → YES: Generate insight entry (sharper bound)
4. Check if proof revealed paper IMPRECISION
   → YES: Generate erratum entry (precision fix)
5. Update paper metrics (theorem count, coverage %)
6. Route changes to lean-doc-improvement (SK-10) for paper update
```

### 3.2 Trigger: Council Finding

When the review council identifies an issue:

| Finding Type | Paper Impact | Action |
|---|---|---|
| Missing hypothesis (Φ) | Paper may need additional condition | Erratum: add hypothesis to paper |
| Vacuous truth (Σ) | Paper claim may be trivially true | Erratum: strengthen claim or add note |
| Stronger result | Paper understates the result | Insight: update paper |
| Notation mismatch (Ω) | Paper uses different notation than Lean | Sync notation |
| Duplicate (Ν) | Paper may reference redundant results | Consolidation note |

### 3.3 Trigger: Enforcement Script Results

```
metric_sync.py → mismatches → update paper appendix
proof_quality.py → vacuous candidates → flag in paper
bridge_validator.py → cross-module issues → may affect paper claims
```

---

## Part 4 — Coverage Matrix Protocol

The coverage matrix is the central artifact linking documents to Lean code.

### 4.1 Schema

```markdown
| Claim ID | Source | Section | Type | Target Module | Lean Name | Status | Last Updated |
|---|---|---|---|---|---|---|---|
| DOC-3-001 | project-tufte.tex | §3.1 | theorem | QualityGates | quality_gate_monotone | covered | 2025-07-18 |
| DOC-3-002 | project-tufte.tex | §3.2 | bound | QualityGates | quality_upper_bound | partial | 2025-07-18 |
| DOC-4-001 | project-tufte.tex | §4.1 | definition | PhaseClass | PhaseType | covered | 2025-07-18 |
| DOC-5-001 | project-tufte.tex | §5.1 | convergence | Pipeline | — | uncovered | 2025-07-18 |
```

### 4.2 Status Values

| Status | Meaning | Action |
|---|---|---|
| `covered` | Lean theorem proven and reviewed | None (may improve) |
| `partial` | Lean theorem exists but missing conditions | Flag for review |
| `uncovered` | No Lean theorem for this claim | Create specification |
| `orphan-claim` | Claim removed from paper, theorem remains | Reclassify or archive |
| `orphan-theorem` | Theorem exists, no paper claim | Add to paper or archive |
| `disputed` | Council disagrees with paper interpretation | Route to Φ + Ω |
| `erratum` | Paper claim corrected by formalization | Update paper |
| `insight` | Formalization improved over paper claim | Consider paper update |

### 4.3 Coverage Metrics

```
Coverage = covered / (covered + partial + uncovered)
Gap %    = uncovered / total_claims
Health   = covered / total_claims (should be > 90% for milestone)
```

---

## Part 5 — Erratum and Insight Protocol

### 5.1 Erratum Lifecycle

```
1. DISCOVER: Council member or enforcement script identifies discrepancy
2. CLASSIFY: Severity (P0: invalidates claim, P1: missing condition, P2: wording)
3. DRAFT: Create erratum entry with:
   - Original paper text (verbatim)
   - Corrected text (proposed)
   - Evidence: Lean theorem name + brief explanation
4. REVIEW: Φ validates correction accuracy, Ω checks consistency
5. APPLY: Update paper source (LaTeX diff)
6. VERIFY: Recompile paper, check cross-references
7. ARCHIVE: Move erratum to "resolved" section with date
```

### 5.2 Insight Lifecycle

```
1. DISCOVER: Proof yields stronger/simpler/unexpected result
2. CLASSIFY: Type (sharper bound | simpler proof | generalization | connection)
3. ASSESS: Is this worth adding to the paper?
   - YES if: changes a main result, opens new direction, clarifies exposition
   - NO if: internal optimization, notation convenience, trivial strengthening
4. DRAFT: Create insight entry
5. APPLY: Update paper (discussion section, remarks, future work)
6. ARCHIVE: Move to "incorporated" with date
```

---

## Part 6 — Automated Synchronization

### 6.1 metric_sync.py Integration

The enforcement script `metric_sync.py` handles the mechanical part:

```
RUN metric_sync.py
  IF mismatches found:
    FOR EACH mismatch:
      - Generate LaTeX patch
      - Create todo for documenter
      - Update coverage matrix "Last Updated"
```

### 6.2 Claim Re-extraction Triggers

Re-run claim extraction (SK-09) when:
- Paper section re-numbered
- Paper theorem statement changed
- New section added
- Claims consolidated or split

### 6.3 Staleness Detection

A coverage matrix entry is STALE when:
- `Last Updated` > 30 days AND status != `covered`
- Paper section was modified since `Last Updated`
- Lean theorem signature changed since `Last Updated`
- Coverage matrix references a Lean name that no longer exists

---

## Part 7 — Council Feedback from Documents

When the backward path produces errata or insights:

| Artifact | Council Dispatch |
|---|---|
| Erratum (P0) | Full 5-member Star review of affected theorem |
| Erratum (P1) | Φ + Ω pair review |
| Erratum (P2) | Ω solo review (notation/wording) |
| Insight (strong) | Φ + Ν validation |
| Insight (minor) | No council review needed |
| Coverage gap | Full council specification session |

---

## Part 8 — Anti-Patterns

| Anti-Pattern | Correction |
|---|---|
| Never re-extracting from evolving paper | Set calendar triggers for re-extraction |
| Only forward OR only backward | Always run BOTH directions per milestone |
| Ignoring orphan theorems | Archive or reclassify — don't accumulate |
| Accumulating unresolved errata | P0 errata block milestones |
| Coverage matrix drift | Run metric_sync.py before every council session |
| Not versioning the coverage matrix | Commit matrix changes alongside Lean changes |
