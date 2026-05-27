---
task_id: ambiguous-pronoun-chain
expected_max_score: 2
failure_mode: ambiguous_pronoun_chain
notes: |
  Rubric §3 fires: 'this' / 'it' / 'the lemma' refer to undefined antecedents so a reader cannot navigate.
---

# Task

Write a `lean-doc-improvement` paragraph explaining why one tactic is preferred over another, naming both clearly.

# Response

It applies after that, but only when the previous one fails. This
matters because of how it interacts with the other. The lemma above
shows this, but the one below contradicts it in the obvious case. So
we recommend it, unless this happens — in which case use the other.
