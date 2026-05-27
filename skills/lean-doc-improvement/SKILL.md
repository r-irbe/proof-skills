---
name: lean-doc-improvement
description: |
  USE FOR: Update academic papers, technical reports, and documentation based on results from Lean 4 formalization. Use when formal verification reveals paper imprecisions, missing hypotheses, sharper bounds, new insights, or when metrics need synchronization. Covers paper appendix updates, verification tables, erratum entries, insight propagation, and metric synchronization between Lean and documents.
  DO NOT USE FOR: extracting requirements from papers (use @lean-doc-requirements); blueprint generation (use @lean-blueprint); report compilation (use @lean-report).
  TRIGGERS: update paper, doc improvement, paper revision, documentation update from Lean, doc-feedback consumer.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ['agent:gateway', 'skill:lean-research']
  successors: ['skill:lean-doc-feedback', 'skill:lean-report', 'skill:lean-zettelkasten']
metadata:
  version: "0.2.0"
  source_spec: "skills/lean-doc-improvement/SKILL.md (this file)"
  last_reviewed: "2026-05-27"
---

# Lean 4 Results-to-Document Improvement

Systematically update documents when Lean formalization produces new insights, corrections, or metrics.


## Routing

- **USE FOR:** Update academic papers, technical reports, and documentation based on results from Lean 4 formalization. Use when formal verification reveals paper imprecisions, missing hypotheses, sharper bounds, new insights, or when metrics need synchronization. Covers paper appendix updates, verification tables, erratum entries, insight propagation, and metric synchronization between Lean and documents.
- **DO NOT USE FOR:** extracting requirements from papers (use @lean-doc-requirements); blueprint generation (use @lean-blueprint); report compilation (use @lean-report).
- **TRIGGERS:** update paper, doc improvement, paper revision, documentation update from Lean, doc-feedback consumer.

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
- **Successors:** `skill:lean-doc-feedback`, `skill:lean-report`, `skill:lean-zettelkasten`.

---

## Part 1 — Trigger Events

| Trigger | Action | Priority |
|---|---|---|
| `sorry` removed (new proof completed) | Update coverage metrics | P2 |
| Hypothesis added to theorem | Check if paper claim needs corresponding condition | P1 |
| Hypothesis removed (stronger result) | Update paper to state stronger result | P1 |
| Counter-example found during review | Erratum entry + paper correction | P0 |
| Statement corrected (Φ finding) | Erratum entry + paper correction | P0 |
| New bridge theorem proven | Add to paper's formalization appendix | P2 |
| Duplicate detected by Ν | Note in appendix if paper references both | P3 |
| Quality improvement (Λ refactoring) | No paper change needed (internal) | — |
| Convention change (Ω finding) | No paper change usually (internal) | — |
| New Zettelkasten permanent note | Consider for paper discussion section | P3 |
| Axiom issue detected by Σ | Critical erratum if affects paper claims | P0 |

---

## Part 2 — Document Update Types

### 2.1 Metric Synchronization

The paper's appendix contains formalization metrics that must stay in sync:

```markdown
## Metrics to Synchronize
- Total lines of Lean code: [from `wc -l Project/*.lean`]
- Total theorems: [from `grep -c "^theorem\|^lemma" Project/*.lean`]
- Total definitions: [from `grep -c "^def\|^structure\|^inductive\|^class" Project/*.lean`]
- Sorry count: [from `grep -c "sorry" Project/*.lean`]
- Module count: [from `ls Project/*.lean | wc -l`]
- Lean version: [from `lean --version`]
- Mathlib version: [from lakefile.lean]
- Build status: [from `lake build` exit code]
- Axiom cleanliness: [all/not-all modules pass `#print axioms` check]
```

### 2.2 Verification Table

The paper should contain (or be updated with) a verification mapping:

```latex
\begin{table}[h]
\caption{Formal Verification Mapping}
\begin{tabular}{llll}
Paper Claim & Lean Theorem & Module & Status \\
\hline
Thm 3.1 & \texttt{quality\_gate\_monotone} & QualityGates & \checkmark \\
Prop 4.2 & \texttt{phase\_classification\_complete} & PhaseClassification & \checkmark \\
% ... generated from coverage matrix
\end{tabular}
\end{table}
```

### 2.3 Erratum Entries

When formalization reveals a paper error:

```markdown
## Erratum: [ERR-YYYYMMDD-NNN]
- Paper location: §N.M, [Theorem/Equation] N
- Original claim: [verbatim from paper]
- Issue: [missing hypothesis / incorrect bound / wrong quantifier order / ...]
- Corrected claim: [corrected version]
- Evidence: Project/[Module].lean:[theorem_name] — [brief explanation]
- Discovered by: [council member] during [Phase N audit / review session ID]
- Impact: [minor wording fix / substantive correction / invalidates downstream claim]
```

### 2.4 Insight Notes

When formalization yields positive insights (not corrections):

```markdown
## Insight: [INS-YYYYMMDD-NNN]
- Source: Project/[Module].lean:[theorem_name]
- Type: [sharper bound | simpler proof | unexpected connection | generalization]
- Description: [what was discovered]
- Paper action: [add to discussion / add remark / extend result / no action]
```

---

## Part 3 — Update Workflow

### 3.1 Individual Theorem Completion

When a theorem is proven and council-reviewed:

```
1. Check coverage matrix → find corresponding paper claim
2. IF claim status was "uncovered" → update to "covered"
3. IF proof required additional hypotheses not in paper:
   a. Create erratum entry
   b. Draft LaTeX correction
   c. Route to Φ for validation
   d. Apply to paper source
4. IF proof achieved stronger result than paper claimed:
   a. Create insight note
   b. Draft LaTeX improvement
   c. Route to Ω for consistency check
   d. Apply to paper source
5. Update metrics (theorem count, sorry count, coverage %)
6. Update verification table
```

### 3.2 Batch Update After Audit Wave

After completing a retroactive audit wave:

```
1. Run metric sync script → generate diffs
2. Regenerate verification table from coverage matrix
3. Collect all erratum entries from the wave → batch review
4. Collect all insight notes → assess for paper inclusion
5. Update paper appendix with new metrics
6. Update paper body with corrections (P0/P1 errata)
7. Create Zettelkasten permanent note summarizing the wave's findings
```

### 3.3 Paper Revision Protocol

For non-trivial paper changes:

```
1. Draft the change (LaTeX diff)
2. Route through council:
   - Φ: Does the new text accurately reflect the formal result?
   - Ν: Is the change consistent with other paper claims?
   - Λ: Is the exposition clear?
   - Ω: Do cross-references and numbering still work?
3. Apply change
4. Verify paper compiles (LaTeX build)
5. Update traceability records
```

---

## Part 4 — LaTeX Integration Patterns

### 4.1 Auto-Generated Content Markers

Place markers in the LaTeX source for auto-updatable sections:

```latex
% AUTO-GENERATED: DO NOT EDIT MANUALLY
% Source: docs/tracking/coverage_matrix.md
% Last sync: [ISO-8601]
\begin{table}[h]
...
\end{table}
% END AUTO-GENERATED
```

### 4.2 Conditional Formatting

For claims whose formal status changed:

```latex
% UPDATED per ERR-20250718-001: added hypothesis (q > 0)
\begin{theorem}[Quality Gate Monotonicity]
For all quality scores $q \in (0, 1]$ ... % was $q \in [0, 1]$
\end{theorem}
```

### 4.3 Verification Badges

In the paper appendix, each claim can carry a status:

```latex
\newcommand{\verified}{\textcolor{green}{\checkmark}}
\newcommand{\partial}{\textcolor{orange}{$\sim$}}
\newcommand{\unverified}{\textcolor{red}{$\times$}}

Theorem 3.1 \verified{} % quality_gate_monotone in QualityGates.lean
```

---

## Part 5 — Feedback to Other Skills

### 5.1 To lean-doc-requirements

When updating the paper reveals:
- New claims that were added during revision → extract as new requirements
- Claims that were split or merged → update corresponding specifications
- Sections restructured → re-run extraction on affected sections

### 5.2 To lean-zettelkasten

Each erratum and insight becomes a Zettelkasten entry:
- Erratum → fleeting note tagged `#erratum #[module]`
- Insight → literature note or permanent note depending on significance
- Pattern of errata (e.g., "paper consistently omits positivity hypotheses") → permanent note

### 5.3 To lean-review-council

Findings during document update may trigger:
- Re-review of related theorems (if paper context changes interpretation)
- Specification update (if paper claim was the source of truth and it changed)
- Convention updates (if paper naming differs from Lean naming)

---

## Part 6 — Metric Dashboard

### 6.1 Sync Status Template

```markdown
# Metric Sync Dashboard
## Last sync: [ISO-8601]

| Metric | Paper Value | Lean Value | Status |
|---|---|---|---|
| Total lines | 8,994 | [computed] | [match/stale] |
| Theorems | 611 | [computed] | [match/stale] |
| Sorry count | 0 | [computed] | [match/stale] |
| Modules | 12 | [computed] | [match/stale] |
| Coverage % | [N]% | [computed] | [match/stale] |
| Lean version | 4.28.0 | [computed] | [match/stale] |
| Mathlib version | 4.28.0 | [computed] | [match/stale] |

## Stale Metrics: [N]
## Errata Pending Paper Update: [N]
## Insights Pending Assessment: [N]
```

### 6.2 Automation

The `metric_sync.py` enforcement script (see lean-gateway SK-06 enforcement scripts) automates:
1. Extract current Lean metrics
2. Parse paper appendix for stated metrics
3. Diff and report mismatches
4. Generate PR-ready LaTeX patch if mismatches found
