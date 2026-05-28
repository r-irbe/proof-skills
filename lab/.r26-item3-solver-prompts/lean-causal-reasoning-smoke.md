# Task

Write a Lean 4 `def Causes` for a causal relation `Causes (X Y : Prop) : Prop` distinct from
biconditional `↔`. Reply with the Lean 4 code only — no prose. Include a comment line that
states why `Causes X Y` is NOT the same as `X ↔ Y`.

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
