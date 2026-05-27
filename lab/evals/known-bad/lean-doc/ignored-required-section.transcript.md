---
task_id: ignored-required-section
expected_max_score: 2
failure_mode: missing_required_section
notes: |
  Rubric §2 fires: skill SKILL.md explicitly mandates four sections
  (audience, vocabulary, examples, doc-comment-gaps). Response
  delivers two and stops without acknowledging the omission.
---

# Task

Write a doc-requirements document for `Mathlib.RingTheory.Ideal.Basic`
per the `lean-doc-requirements` skill. The skill specifies four
required sections: audience, required vocabulary, worked-example
checklist, and doc-comment-gap inventory.

# Response

# Doc Requirements: Mathlib.RingTheory.Ideal.Basic

## Audience

Graduate students with prior exposure to commutative algebra (Atiyah-
Macdonald level). Lean 4 + Mathlib familiarity assumed at the level
of `lean-math-foundations`.

## Required Vocabulary

- ideal of a commutative ring
- prime ideal, maximal ideal
- quotient ring
- principal ideal
- radical of an ideal

That covers what's needed to engage with the module.
