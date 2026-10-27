---
garden_schema_version: "0.1"
taxonomy_version: "0.1.0"
doc_id: tacitdoc:README
title: "Golden-Case Suite (v1)"
document_role: reference
lifecycle_state: active
disposition: adopt
evidence_strength: direct
confidence: high
id: "REF-ALT-PROOF-COUNCIL-README"
maturity: "seedling"
verification: "unverified"
sources:
  - "docs/investigation-garden/altproof/COUNCIL_CHARTER.md"
  - "docs/investigation-garden/altproof/ALT_PROOF_META_TACTIC_DESIGN.md"
related:
  - "PLAN-ALT-PROOF-COUNCIL-CHARTER"
indexed-by:
  - "MOC-ALT-PROOF-COUNCIL"
---

# Golden-Case Suite (v1)

**Contract.** These fixtures are the alt-proof program's calibration
and regression baseline. Every fixture is a REAL decomposition the
long-proof campaign performed and kernel-verified (0 sorry/admit/
axiom throughout) - the sweep tool must, on each fixture's BEFORE
state, find the AFTER state's structure (or a legitimate
alternative the council ranks no worse).

**Uses** (per the design note sections 7-10):
1. **Cost-weight calibration** (ballot B1): the extraction-outranks
   default must rank each fixture's AFTER state above its BEFORE
   state; where it does not, the heuristic family gains a member.
2. **Robustness studies** (ballot B3): each transformation module
   (redirect, reflection, extraction) claims fixtures whose routes
   it exemplifies - a module emits default suggestions only after
   its claimed fixtures pass.
3. **Regression baseline**: when the sweep exists, its suggestions
   on these 17 proofs are pinned; behavior changes require a
   council note.

**Route coverage note**: 16 fixtures exemplify EXTRACTION; fixture
16 (gate_row_diff_bound, uniform-simp collapse) exemplifies
REFLECTION. No fixture yet exemplifies REDIRECT - the first
by_contra-heavy proof restructured by the tool becomes the first
redirect fixture (the JAR16 redirect procedure's corpus analogue).

**Aggregate** (from the campaign): 17 decompositions, 36 shared
lemmas extracted, 4 considered negatives (each with a recorded
reason), 0 regressions, 2 verified-Mathlib-absent upstreaming
candidates (one now PR #44591).
