# Discovery ladder evaluation prompts

Use these prompts to test whether `lean-research` applies the discovery ladder
instead of making one-shot symbol or package claims. They are intentionally
short enough to run as manual checks or as entries in a future eval harness.

## Eval 1 — current-pin theorem lookup

**Prompt:**  
"I need a Lean theorem saying the diagonal entries of a positive semidefinite
matrix are nonnegative. Find it in mathlib and tell me whether I can use it."

**Expected behavior:**

- Runs R0/R1 before web search.
- Reports a current-pin source citation if found.
- States whether the candidate is ADOPT-NOW or ADOPT-LATER for the caller's
  context.
- Avoids claiming a symbol exists solely from memory or web snippets.

## Eval 2 — absent substrate

**Prompt:**  
"Does current mathlib have a ready-made Shannon entropy theorem for finite
probability measures, ideally Pinsker too? I want to replace my local proof."

**Expected behavior:**

- Searches at least local package source plus theorem-search services.
- Records at least three query reformulations before a negative claim.
- Separates "absent at current pin" from "mathematically unavailable".
- Produces a negative-result record and a research-more or local-proof route.

## Eval 3 — Reservoir package adoption

**Prompt:**  
"Could we add SciLean or CvxLean to get analysis theorems for our Lean project?
Please decide whether to adopt either package."

**Expected behavior:**

- Treats package adoption separately from theorem borrowing.
- Checks Reservoir and GitHub health signals, not just package names.
- Uses adoption classes with blockers and validation paths.
- Escalates if dependency risk or compatibility confidence is below the belief
  floor.

## Eval 4 — cross-domain literature anchor

**Prompt:**  
"This theorem looks like a random graph giant-component bound. Search Lean and
the literature and tell me if the statement is faithful enough to keep."

**Expected behavior:**

- Runs symbol/package/literature rungs rather than only web search.
- Distinguishes Lean formalization availability from scholarly truth.
- Produces a source-faithfulness class and confidence.
- Recommends proof, replace, quarantine, or HITL instead of silently keeping an
  unverifiable axiom.
