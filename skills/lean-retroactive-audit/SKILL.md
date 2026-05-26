---
name: lean-retroactive-audit
description: Apply the review council system retroactively to an existing large Lean 4 project. Use when onboarding an existing codebase to the council review framework. Covers module discovery, dependency analysis, incremental audit scheduling, baseline establishment, gap analysis, and the catch-up RALPH cycle for bringing an existing project to full review coverage.
---

# Lean 4 Retroactive Audit

Systematic methodology for applying the 5-member review council, Zettelkasten, and specification framework to a large existing Lean 4 codebase that was developed before these systems were in place.

---

## Part 1 — The Retroactive Challenge

Existing projects have:
- Theorems with no specification documents
- Proofs with no review records
- Implicit knowledge not captured in Zettelkasten
- Paper cross-references that may be incomplete or stale
- Convention violations accumulated over time
- Possible undetected pitfalls, duplicates, or missing hypotheses

The retroactive audit creates a **baseline** and then systematically raises every artifact to full council-reviewed status.

---

## Part 2 — Phase 0: Discovery

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

## Part 3 — Phase 1: Baseline Establishment

### 3.1 Per-Module Baseline Report

For each module, produce (using Pipeline topology — Σ, Φ, Ν, Λ, Ω in sequence):

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
[P0/P1/P2/P3 — should this module be deeply audited first or last?]

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

## Part 4 — Phase 2: Incremental Deep Audit

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
- Axioms: [Σ's report — clean / issues]
- Novelty: [Ν's classification]
- Quality score: [Λ's assessment]
- Convention compliance: [Ω's report]

### Recommended Actions
- [ ] [Action 1 — e.g., "add missing hypothesis h : n > 0"]
- [ ] [Action 2 — e.g., "replace bare aesop with aesop? output"]
- [ ] [Action 3 — e.g., "add docstring"]
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

## Part 5 — Phase 3: Gap Analysis and Extension

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

## Part 6 — Phase 4: Steady-State Transition

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

## Part 7 — Parallel Audit Dispatch

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
