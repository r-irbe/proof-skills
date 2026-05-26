# Template v2 proposals

Three design-doc proposals for upgrading the existing
`templates/Template_*.md` set to a v2 shape grounded in production
Lean 4 / Mathlib4 evidence.

## What lives here

| File | Scope | Lines |
|---|---|---|
| `proof-templates-v2.md` | 4 proof-side templates: `Template_Theorem` (≈ `Template_Analysis`), `Template_DataModule` (≈ `Template_Foundation`), `Template_TacticHelper` (≈ `Template_Automation`), and the new `Template_Bridge` | ~1060 |
| `workflow-templates-v2.md` | 8 workflow templates (currently embedded in `lean-*` SKILL.md files): `Template_MWE`, `Template_PR`, `Template_Blueprint`, `Template_Zettelkasten`, `Template_Spec`, `Template_Bisect`, `Template_Council`, `Template_RetroLog` | ~1800 |
| `all-templates.md` | Comprehensive review of all 12 existing templates + 9 proposed new domain templates (Probability, Measure, InfoGeom, Bridge, Fractal/IFS, Consensus/BFT, Calculus, Tests, Graph) | ~1194 |

Each document follows the same shape per template:

1. **Current template gaps** — what's missing from the v1 baseline
2. **Evidence** — citations to actual Lean modules that illustrate
   the desired pattern
3. **Proposed v2 template** — copy-pasteable template body, wrapped
   in a fenced code block
4. **Diff summary** — what changed vs v1

## How to use

To produce a production template from one of these proposals:

1. Locate the `## N.3 Proposed v2 template` section for the template
   you want.
2. Copy the fenced code-block body.
3. Save it as `templates/<Template_Name>.md` (overwriting any v1
   placeholder).
4. Re-cite from the relevant `SKILL.md` `## See also` footer.

This extraction is intentionally manual — the proposals contain
editorial choices (what scope counts as v2, what example
identifiers to use, which SKILL.md cross-links remain valid) that
benefit from human review.

## Status

These proposals are the W6 deliverable of the master plan. The
existing `templates/Template_*.md` files remain in place as v1
placeholders so nothing currently consuming them breaks. Mechanical
extraction-and-replace is HITL-gated per `AGENT.md §1.2 #1`
(Confidence trigger — section structure, G-rules, handoff DAG, and
naming all require authorial decisions).
