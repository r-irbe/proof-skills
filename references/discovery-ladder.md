# Lean discovery ladder

Use this reference when a Lean task depends on finding an existing theorem,
package, tactic, or literature anchor before writing new code. The ladder keeps
research reproducible: each rung has a purpose, a stopping condition, and a
negative-result record so later agents do not repeat the same weak search.

## 1. Select the question type

| Type | Use when | Primary output |
|---|---|---|
| Symbol | Looking for an existing theorem, definition, instance, tactic, or namespace. | Candidate symbol list with current-pin verification. |
| Package | Deciding whether a Reservoir/GitHub package should become a dependency or research input. | Adoption class: ADOPT-NOW, ADOPT-LATER, RESEARCH-MORE, DO-NOT-ADOPT. |
| Literature | Checking whether a statement shape matches a scholarly theorem or is a novel claim. | Source-faithfulness class and citation trail. |
| Strategy | Choosing how to prove, refactor, or decompose a formalization. | Recommended strategy plus risk notes. |

If a question spans more than one type, run the relevant rungs in parallel and
record which result controls the downstream decision.

## 2. Rung order

| Rung | Action | Stop when | Record on miss |
|---|---|---|---|
| R0 Local inventory | Search the host repo for exact names, nearby modules, imports, and existing wrappers. | A local declaration already solves or constrains the task. | Paths searched, terms used, and whether names were normalized. |
| R1 Current-pin package source | Search installed package sources, especially Mathlib and domain dependencies under `.lake/packages/`. | A candidate symbol is found and can be cited at file:line. | Package pin, directories searched, exact query variants. |
| R2 Theorem search services | Query Loogle, Moogle, LeanSearchClient, or equivalent public theorem search. | A candidate can be re-verified in package source or docs. | At least three reformulations and the service URL/date. |
| R3 Reservoir package scan | Search Reservoir by topic, package slug, imports, examples, and dependency health. | A package has a maintained, relevant, version-compatible candidate. | Slug normalization, archive/staleness signals, dependency concerns. |
| R4 GitHub code search | Search exact Lean symbols, statement fragments, package module names, and paper theorem names. | A maintained repo gives reusable evidence or an import path. | Queries, repo health, license/maintenance caveats. |
| R5 Literature/web | Search arXiv, DOI pages, textbooks, docs, and upstream issue/PR discussions. | Statement has a credible mathematical or engineering anchor. | Search strings, no-result warnings, and novelty risk. |
| R6 Synthesis/council | Reconcile conflicting candidates via a review or research council. | One recommendation reaches the skill repo's confidence floor. | Conflict summary, confidence, and HITL question if below threshold. |

## 3. Verification rules

- Re-verify any web or search-service hit against local source at the current pin
  before using it in a proof plan. A search result is a lead, not evidence.
- Prefer exact file:line citations for installed package source. For web-only
  literature, cite stable URLs and enough bibliographic detail to re-find the
  result.
- Treat package adoption as a separate decision from theorem borrowing. A package
  may be useful for research without being safe as a dependency.
- Do not call a negative result exhaustive unless R0-R5 ran, the query variants
  are recorded, and the remaining gap is classified.
- If confidence is below the local belief floor, return a structured HITL
  question instead of silently choosing a theorem, package, or proof route.

## 4. Negative-result record

Use this compact block in findings, handoffs, or zettels:

```markdown
### Discovery ladder record

- Question:
- Type: Symbol | Package | Literature | Strategy
- Current pins / toolchain:
- R0 local inventory:
- R1 current-pin package source:
- R2 theorem search services:
- R3 Reservoir:
- R4 GitHub:
- R5 literature/web:
- R6 synthesis/council:
- Result: FOUND | NOT FOUND | PARTIAL | CONFLICT
- Confidence:
- Downstream action:
```

## 5. Adoption classes for packages and symbols

| Class | Meaning | Required evidence |
|---|---|---|
| ADOPT-NOW | Safe to use immediately if the caller has an edit claim. | Current-pin symbol/package verified, compatible API, validation command known. |
| ADOPT-LATER | Valuable but blocked by sequencing, baseline, version, or proof-design work. | Clear value, concrete blocker, and a later validation path. |
| RESEARCH-MORE | Promising but insufficiently verified. | Specific unanswered questions and next queries. |
| DO-NOT-ADOPT-NOW | Not suitable for the current lane, but may be revisited. | Staleness, incompatibility, unclear license, or excessive dependency risk. |
| DO-NOT-ADOPT | Should not be used for this project class. | Archived/unmaintained, unsafe, irrelevant, or inconsistent with project policy. |

## 6. Handoff expectations

Every handoff from research to proof, review, package planning, or source editing
should include:

1. The controlling rung result and confidence.
2. Candidate symbols/packages with source verification status.
3. Negative-result record for missing substrates.
4. Required validation command before implementation.
5. A HITL question when adoption or mathematical validity is below confidence.
