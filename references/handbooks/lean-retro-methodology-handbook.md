---
title: Lean Retro Methodology Handbook
status: reference
extracted_from: skills/lean-retro-methodology/SKILL.md
extracted_on: '2026-05-27'
scope: Parts 1-8 (The RETRO Protocol; Adapting to Project Scale; Enforcement Scripts;
  Cross-Skill Optimization; Personas and Roles; Tracking Documents; RALPH Loop for
  RETRO; Anti-Patterns to Avoid).
loader_hint: Load when @lean-retro-methodology routes here for methodology details;
  not needed for the dispatch decision.
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| Completed proof wave or refactor campaign | RETRO 5-step loop (`Refactor-Extract-Test-Refine-Optimize`) | Mine recurring tactic bottlenecks into reusable lemmas/rules |
| Reusable insight discovered during proving/review | Luhmann Zettelkasten note (`fleeting -> literature -> permanent`) | Link bidirectionally with `ZK-` IDs and declaration anchors |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Prevent repeating the same 20-step proof struggle next wave | Extract tactic phrasebook row + static lint rule | Update handbook table and regenerate `handbook-tables.v1.json` |
| Curate permanent knowledge notes without confidential leaks | `gardener.md` + `lean-retro-facilitator` | Keep public `proof-skills` notes strictly project-agnostic |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| Retrospective produces vague process wishes | Findings not bound to measured incidents | Bind every new rule/template change to a concrete failure or speedup metric |
| Orphan Zettelkasten notes with zero inbound/outbound links | Skipped index integration | Run Zettelkasten link check before closing `gardener` turn |

---

# Lean Retro Methodology Handbook

> **Layering note.** This file holds the deep methodology content
> previously embedded in [`skills/lean-retro-methodology/SKILL.md`](../../skills/lean-retro-methodology/SKILL.md).
> The SKILL.md keeps the dispatch contract (Routing / Workflow /
> Recovery / Handoffs) + the parts index. This file holds the full
> encyclopaedia of the retro protocol; adapting to project scale; enforcement scripts; cross-skill optimization, etc.
> Zero fidelity loss vs the pre-layering revision.

---

## Part 1 -- The RETRO Protocol

RETRO = **R**econnaissance → **E**stablish → **T**riage → **R**eview → **O**nboard

### Phase R -- Reconnaissance (Discovery)

**Goal:** Understand what exists. No changes.

**Agents:** 3 parallel discovery agents

```
PARALLEL:
  CENSUS_AGENT → {
    - Count lines/theorems/defs/sorry per module
    - Extract all theorem names + signatures
    - Detect axiom usage (#print axioms batch)
    - Report: census.md
  }
  DEPGRAPH_AGENT → {
    - Extract import graph via grep
    - Compute topological sort (dependency waves)
    - Identify circular or missing imports
    - Report: dependency_graph.md
  }
  COVERAGE_AGENT → {
    - Scan source documents (project-tufte.tex, tech reports)
    - Extract all mathematical claims (lean-doc-requirements skill)
    - Map claims to existing theorems
    - Report: coverage_matrix.md
  }
SYNC → RETRO_BASELINE = {census, depgraph, coverage}
```

**Enforcement script (Python):**
```python
# scripts/retro_reconnaissance.py
# Runs all discovery tasks and produces structured JSON
import subprocess, json, re, pathlib

def census(lean_dir):
    """Count theorems, defs, sorry, lines per module."""
    results = {}
    for f in pathlib.Path(lean_dir).glob("Project/*.lean"):
        module = f.stem
        text = f.read_text()
        results[module] = {
            "lines": len(text.splitlines()),
            "theorems": len(re.findall(r'^theorem\s', text, re.M)),
            "defs": len(re.findall(r'^(?:def|structure|inductive|class|noncomputable def)\s', text, re.M)),
            "sorry": len(re.findall(r'\bsorry\b', text)),
            "private_theorems": len(re.findall(r'^private theorem\s', text, re.M)),
        }
    return results

def dependency_graph(lean_dir):
    """Extract import edges."""
    edges = []
    for f in pathlib.Path(lean_dir).glob("Project/*.lean"):
        module = f.stem
        for line in f.read_text().splitlines():
            m = re.match(r'^import Project\.(\w+)', line)
            if m:
                edges.append({"from": module, "to": m.group(1)})
    return edges

def check_conventions(lean_dir):
    """Check autoImplicit, docstrings, section headers."""
    issues = []
    for f in pathlib.Path(lean_dir).glob("Project/*.lean"):
        module = f.stem
        text = f.read_text()
        if "autoImplicit false" not in text:
            issues.append({"module": module, "issue": "missing autoImplicit false", "severity": "P0"})
        if "/-!" not in text:
            issues.append({"module": module, "issue": "missing module docstring", "severity": "P2"})
        sections = re.findall(r'^-- §(\d+)', text, re.M)
        if not sections:
            issues.append({"module": module, "issue": "no section headers", "severity": "P3"})
    return issues
```

### Phase E -- Establish (Baseline)

**Goal:** Produce per-module baseline reports. Light review only.

Run Pipeline topology (Σ→Φ→Ν→Λ→Ω) per module in dependency wave order:

| Wave | Modules | Parallel |
|---|---|---|
| 1 | Tactics | No (single) |
| 2 | QualityGates | No (single) |
| 3 | PhaseClassification, PipelineAdaptive | Yes (2) |
| 4 | CCVGating, PhasePortrait | Yes (2) |
| 5 | CuspCatastrophe, ProvenanceChain | Yes (2) |
| 6 | LyapunovStability | No (single) |
| 7 | ReinforcementLearning | No (single) |
| 8 | AgenticSafety, StochasticCCV | Yes (2) |

Each baseline report uses Template 1 from lean-retroactive-audit.

### Phase T -- Triage (Prioritize)

**Goal:** Decide what to fix first.

The Triage Council (Ω + Planner) ranks all findings:

```
FOR finding IN all_baseline_findings:
  IF finding.sorry_count > 0: priority = P0
  ELIF finding.axiom_issue: priority = P0
  ELIF finding.vacuous_truth: priority = P1
  ELIF finding.missing_hypothesis: priority = P1
  ELIF finding.duplicate: priority = P2
  ELIF finding.quality_issue: priority = P2
  ELIF finding.convention_violation: priority = P3
  ELSE: priority = P3
```

Output: **Triage Report** with ordered fix list.

### Phase R -- Review (Deep Audit)

**Goal:** Full council review of each module.

Star topology per theorem, batched by module. Each theorem gets:
1. Full 5-member RALPH review
2. Retroactive specification (lean-specification format)
3. Zettelkasten notes for each observation
4. Coverage matrix update

### Phase O -- Onboard (Steady State)

**Goal:** Transition to ongoing review process.

Criteria:
- Zero sorry, clean axioms
- >90% paper coverage
- Every module council-reviewed at least once
- Zettelkasten populated with patterns
- Enforcement scripts in CI

---

## Part 2 -- Adapting to Project Scale

### Small Project (<2000 lines, <100 theorems)

- Skip Pipeline topology; use Star on entire modules
- Single wave review (no dependency ordering needed)
- 1 session for complete audit

### Medium Project (2000--10000 lines, 100--700 theorems)

- Use full RETRO protocol
- 3--5 sessions for complete audit
- Dependency wave ordering critical
- Focus on cross-module bridges

### Large Project (>10000 lines, >700 theorems)

- Full RETRO with meta-council oversight
- Hierarchical topology for project-level review
- Dedicated Synthesizer agent running continuously
- Wave-based scheduling with parallel councils
- Consider splitting into sub-projects

### The the project (current)

12 modules, 22,312 lines, ≥1,255 theorems, 290 definitions.
Classification: **Medium-to-Large** -- use full RETRO with dependency waves.

---

## Part 3 -- Enforcement Scripts

### 3.1 Pre-Review Gate (Python)

```python
# scripts/pre_review_gate.py
"""Must pass before any review session begins."""

def pre_review_check(lean_dir):
    """Returns list of blocking issues."""
    issues = []
    
    # 1. Build check
    result = subprocess.run(["lake", "build"], capture_output=True, cwd=lean_dir)
    if result.returncode != 0:
        issues.append(("P0", "Build fails", result.stderr.decode()[:500]))
    
    # 2. Sorry check
    for f in pathlib.Path(lean_dir).glob("Project/*.lean"):
        text = f.read_text()
        sorry_lines = [(i+1, line.strip()) for i, line in enumerate(text.splitlines()) 
                       if re.search(r'\bsorry\b', line) and not line.strip().startswith('--')]
        for line_num, line_text in sorry_lines:
            issues.append(("P0", f"sorry in {f.name}:{line_num}", line_text))
    
    # 3. autoImplicit check
    for f in pathlib.Path(lean_dir).glob("Project/*.lean"):
        if "autoImplicit false" not in f.read_text():
            issues.append(("P0", f"Missing autoImplicit false in {f.name}", ""))
    
    return issues
```

### 3.2 Post-Review Validation (Python)

```python
# scripts/post_review_validate.py
"""Validates that all review artifacts are complete."""

def validate_session(session_dir):
    """Check review session completeness."""
    checks = []
    
    # Every theorem has a vote record
    report = (pathlib.Path(session_dir) / "session_report.md").read_text()
    theorems_reviewed = re.findall(r'\| (\w+) \|', report)
    votes = re.findall(r'✅|🟡|🟠|🔴', report)
    
    if len(votes) < len(theorems_reviewed) * 5:
        checks.append(("INCOMPLETE", "Not all members voted on all theorems"))
    
    # P0 issues have action items
    p0_findings = re.findall(r'🔴.*', report)
    action_items = re.findall(r'- \[ \].*', report)
    if len(p0_findings) > len(action_items):
        checks.append(("INCOMPLETE", "P0 findings without action items"))
    
    return checks
```

### 3.3 Coverage Matrix Sync (Python)

```python
# scripts/coverage_sync.py
"""Keep coverage matrix in sync with actual Lean code."""

def sync_coverage(lean_dir, matrix_path):
    """Check that coverage matrix matches actual code."""
    # Extract all theorem names from Lean
    lean_theorems = set()
    for f in pathlib.Path(lean_dir).glob("Project/*.lean"):
        for m in re.finditer(r'^theorem\s+(\w+)', f.read_text(), re.M):
            lean_theorems.add(m.group(1))
    
    # Parse coverage matrix
    matrix = pathlib.Path(matrix_path).read_text()
    matrix_theorems = set(re.findall(r'\| \w+ \| .+ \| .+ \| .+ \| (\w+) \|', matrix))
    
    # Find discrepancies
    in_lean_not_matrix = lean_theorems - matrix_theorems
    in_matrix_not_lean = matrix_theorems - lean_theorems
    
    return {
        "orphan_theorems": sorted(in_lean_not_matrix),
        "stale_entries": sorted(in_matrix_not_lean),
        "coverage_rate": len(matrix_theorems & lean_theorems) / max(len(lean_theorems), 1)
    }
```

### 3.4 Zettelkasten Linter (Python)

```python
# scripts/zettelkasten_lint.py
"""Find disconnected notes, missing links, stale references."""

def lint_zettelkasten(zk_dir):
    """Audit Zettelkasten health."""
    issues = []
    notes = {}
    
    for f in pathlib.Path(zk_dir).rglob("ZK-*.md"):
        text = f.read_text()
        note_id = f.stem
        links = re.findall(r'\[\[ZK-[^\]]+\]\]', text)
        tags = re.findall(r'Tags:\s*(.+)', text)
        notes[note_id] = {"path": f, "links": links, "tags": tags}
    
    # Orphan detection
    all_linked = set()
    for n in notes.values():
        all_linked.update(re.findall(r'ZK-\d{8}-\d{3}', ' '.join(n["links"])))
    
    for nid in notes:
        if nid not in all_linked and notes[nid]["links"] == []:
            issues.append(("ORPHAN", f"{nid} has no incoming or outgoing links"))
    
    # Tag consistency
    all_tags = set()
    for n in notes.values():
        for t in n["tags"]:
            all_tags.update(tag.strip() for tag in t.split(','))
    
    return {"issues": issues, "total_notes": len(notes), "total_tags": len(all_tags)}
```

---

## Part 4 -- Cross-Skill Optimization

### 4.1 lean-proof-review Integration

The retroactive process feeds back into lean-proof-review by:
1. Discovering new pitfall patterns during audit → add to Common Lean Pitfalls
2. Finding new tactic patterns → add to Proof Search Priority table
3. Identifying new reusable lemmas → add to Tactics.lean reference
4. Updating tactic coverage (all `proj_*` tactics now DEPRECATED, 0 cross-module uses) → update custom tactic table to reflect deprecation

### 4.2 lean-review-council Integration

The retroactive process uses the council as its primary review mechanism:
- Star topology for per-theorem audit
- Pipeline topology for per-module baseline
- Mesh topology for cross-module gap analysis
- Hierarchical topology for project-level triage

### 4.3 lean-specification Integration

Every audited theorem gets a retroactive specification:
- Reverse-engineered from existing code (not forward-designed)
- Cross-referenced with coverage matrix
- Stored in the same format as forward specifications

### 4.4 lean-zettelkasten Integration

The audit is the richest source of Zettelkasten notes:
- Fleeting notes during every review (patterns, surprises, pitfalls)
- Literature notes from Mathlib/paper research during audit
- Permanent notes synthesized after each module audit
- Index maintenance after each wave

---

## Part 5 -- Personas and Roles

### 5.1 RETRO-Specific Roles

| Role | Symbol | Responsibility | Active in Phase |
|---|---|---|---|
| Census Agent | `CA` | Automated discovery, counting, scanning | R |
| Coverage Mapper | `CM` | Document-to-theorem mapping | R, T |
| Triage Coordinator | `TC` | Priority assignment, fix ordering | T |
| Retroactive Specifier | `RS` | Reverse-engineer specifications | R (review) |
| Fix Implementer | `FI` | Execute P0/P1 fixes | R (review) |
| Migration Tracker | `MT` | Track retro→steady state transition | O |

### 5.2 Existing Roles (from other skills)

All roles from lean-review-council (Σ, Φ, Ν, Λ, Ω) are used in Phases E and R.
All roles from lean-specification (Specifier, Designer) are used in Phase R.
Synthesizer from lean-zettelkasten is used throughout.

---

## Part 6 -- Tracking Documents

### 6.1 Master Retroactive Audit Register

```
docs/project/lean/docs/tracking/retro_register.md
```

Tracks: which modules are in which RETRO phase, which theorems have been audited, which fixes are pending.

### 6.2 Coverage Matrix

```
docs/project/lean/docs/tracking/coverage_matrix.md
```

Bidirectional trace: document claim ↔ specification ↔ Lean theorem.

### 6.3 Triage Report

```
docs/project/lean/docs/tracking/triage_report.md
```

Ordered fix list with priorities, assignments, and status.

### 6.4 Wave Progress Dashboard

```markdown
# RETRO Wave Progress
| Wave | Modules | Phase | Theorems Audited | Findings Open | P0 | P1 |
|---|---|---|---|---|---|---|
| 1 | Tactics | Review | 58/77 | 3 | 0 | 1 |
| 2 | QualityGates | Baseline | 0/64 | -- | -- | -- |
| ... | ... | ... | ... | ... | ... | ... |
```

---

## Part 7 -- RALPH Loop for RETRO

Each RETRO phase has its own RALPH loop:

### Reconnaissance RALPH
- **R**: Run census, depgraph, coverage scripts
- **A**: Classify project scale, identify immediate P0 issues
- **L**: Note any surprises about the codebase structure
- **P**: Design baseline schedule (wave ordering)
- **H**: Produce RETRO_BASELINE documents

### Triage RALPH
- **R**: Read all baseline reports
- **A**: Classify every finding by priority
- **L**: Identify patterns (e.g., "all modules missing docstrings")
- **P**: Create ordered fix list
- **H**: Produce triage report, assign fixes

### Review RALPH (per theorem)
- **R**: 5-member Star topology review
- **A**: Classify findings, vote
- **L**: Create Zettelkasten notes
- **P**: Plan fixes for any findings
- **H**: Execute fixes, update tracking

### Onboard RALPH
- **R**: Verify transition criteria
- **A**: Identify any remaining gaps
- **L**: Document the retroactive process itself (meta-learning)
- **P**: Design steady-state review schedule
- **H**: Enable CI enforcement, archive retro-specific documents

---

## Part 8 -- Anti-Patterns to Avoid

1. **Boiling the ocean**: Don't try to audit everything in one session. Use waves.
2. **Fix-before-audit**: Don't fix issues before establishing the baseline. Measure first.
3. **Convention tyranny**: Don't block P0 fixes on P3 convention issues. Fix soundness first.
4. **Specification theater**: Don't create specifications for trivially verified theorems. Focus specs on complex/novel results.
5. **Zettelkasten dump**: Don't create notes for every observation. Create notes for patterns across 2+ observations.
6. **Parallel overload**: Don't launch more parallel agents than you can track. Use the gateway health dashboard.
7. **Ignoring the dependency graph**: Always audit upstream modules before downstream ones.

---

## Annex: Luhmann Zettelkasten Knowledge Graph & Note Synthesis

# lean-zettelkasten

> Cold-tier skill -- invoked explicitly by name (`@lean-zettelkasten`) from
> review and synthesis flows. No MANDATORY preamble: the gates in §Behavioural
> rules are advisory and reviewed at synthesis time rather than per-note.
> Persist is still required but is local to the
> `docs/project/lean/docs/zettelkasten/` tree.

## Routing

- **USE FOR:** creating a fleeting note from a council observation; creating a literature note when citing lean-pitfalls / Mathlib docs / a paper;
  promoting a cluster of ≥3 notes to a permanent note via the Synthesizer; bidirectional linking (`Related`, `Contradicts`, `Supports`, `Supersedes`);
  running orphan / island / contradiction / staleness / coverage scans; updating `_index.md` and `_tags.md`.
- **DO NOT USE FOR:** running the review council itself (use `@lean-review-council`); reviewing a specific proof (use `@lean-proof-review`); updating
  external papers from Lean results (use `@lean-doc-improvement`); authoring the council retro / methodology (use `@lean-retro-methodology`); generating a
  project blueprint (use `@lean-blueprint`).
- **TRIGGERS:** zettel, ZK-, fleeting note, permanent note, synthesis.

## Behavioural rules (G-*)

- **G-1** (MUST): Every note MUST use the `ZK-YYYYMMDD-NNN` ID grammar, with `NNN` sequential within that date. [Trace: AC-01]
- **G-2** (MUST): Every note MUST declare `Type`, `Created`, `Author`, `Source`, and at least one tag. [Trace: AC-02]
- **G-3** (SHOULD): Fleeting notes SHOULD remain minimal -- capture the observation; do not perfect prose. [Trace: AC-03]
- **G-4** (MUST): A permanent note MUST link to all source fleeting/literature notes it synthesises, and the sources MUST be marked `superseded`. [Trace: AC-04]
- **G-5** (MUST NOT): The skill MUST NOT promote a cluster to a permanent note unless ≥3 source notes converge on the pattern. [Trace: AC-05]
- **G-6** (SHOULD): The skill SHOULD propose a downstream `@lean-proof-review` or `@lean-quality-engine` skill update when a permanent note implies a
  methodology change. [Trace: AC-06]

## Workflow

1. **Discover** [discover] -- read the triggering event (council session, new literature citation, scheduled scan). Locate `_index.md`, current note counts,
   recent tag activity.
2. **Plan** [discover] -- pick note type (fleeting / literature / permanent) or scan type (orphan / island / contradiction / staleness / coverage). For
   permanent promotion, verify ≥3 source notes (G-5). STOP if cluster size < 3 and downgrade to literature note.
3. **Execute** [execute] -- write the note(s) under the correct directory (`fleeting/`, `literature/`, or `permanent/<category>/`); establish bidirectional
   links; flag contradictions for SDR.
4. **Verify** [validate] -- re-check ID uniqueness, link reciprocity, tag presence (G-1, G-2). Max 3 re-checks then escalate.
5. **Persist** [persist] -- commit the new/updated notes, update `_index.md` and `_tags.md`, and (if applicable) open a skill-update proposal for
   `@lean-proof-review` or `@lean-quality-engine` (G-6). Persist is local to `docs/project/lean/docs/zettelkasten/`.

## Recovery & STOP

- Permanent-note promotion attempted with < 3 source notes → STOP, downgrade to literature note (G-5).
- Contradiction detected during synthesis → STOP this synthesis pass; emit a fleeting note flagging both sides for SDR.
- Orphan scan returns > 10 % of notes orphaned → STOP, hand off to `@lean-retro-methodology` for a knowledge-coverage retro.
- Confidence < 80 % on which category a permanent note belongs in (`tactics/`, `pitfalls/`, `conventions/`, `cross-module/`, `proofs/`) → STOP, ask.

## Handoffs

- **Predecessors / successors**: see FM `handoffs`. Inbound: `@lean-proof-review`, `@lean-review-council`, `@lean-retro-methodology`, and `@lean-proof`
  (post-proof pattern capture) seed fleeting notes. Outbound: `@lean-doc-improvement` consumes permanent notes that imply paper updates;
  `@lean-quality-engine` consumes permanent notes that imply skill or methodology changes.
- **Source spec**: `specs/lean/zettelkasten/requirements.md` -- every G-rule traces to an AC there.

## Common failure modes

> AI agents commonly: over-polish fleeting notes (defeats the speed of
> capture); promote 1--2-note clusters to permanent notes; create permanent
> notes without back-linking the sources or marking them `superseded`;
> silently resolve a contradiction instead of flagging it for SDR; skip
> `_index.md` and `_tags.md` updates so the graph view rots. Full registry:
> `GUARDRAILS.md §Agent failure taxonomy`.

## See also

- This `SKILL.md` is the canonical v2 zettelkasten contract for this package.
- [`../../zettelkasten/_index.md`](../../zettelkasten/_index.md) -- live ZK index this skill maintains.
- [`../lean-doc-feedback/SKILL.md`](../../skills/lean-doc-sync/SKILL.md) -- v2 sibling on the documentation side of the DAG.

