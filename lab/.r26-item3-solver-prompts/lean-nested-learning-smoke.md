# Task

Write a Lean 4 `structure MetaLearner` parameterised by an inner-learner type. Fields:
`inner : InnerLearner θ`, `metaStep : θ → θ`. Use `θ` as an implicit type parameter.
Reply with code only.

# HARD CONSTRAINTS

You MUST reply with exactly ONE Lean 4 code block fenced with ```lean and nothing else.

Do NOT include any of these in your response:
- Prose explanations (math/RL/concept narration)
- Markdown headers
- Lists or bullet points
- Discussion of alternatives
- Apology or hedging
- "Here is..." preambles
- Trailing commentary after the code block

If you cannot produce Lean 4 code that satisfies the request, reply with EXACTLY:

```lean
-- TASK INFEASIBLE: <one-line reason>
```

Otherwise the code block must be valid Lean 4 syntax (def / structure / theorem) that
matches the signature in the task. The Lean compiler must be able to parse it (placeholder
proofs `by sorry` or `by exact?` are allowed when a theorem is requested with no proof).

Begin your reply with the triple-backtick opening fence and end with the closing fence.
Output NOTHING outside the fences.
