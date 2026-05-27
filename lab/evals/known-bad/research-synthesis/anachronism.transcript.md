---
task_id: anachronism
expected_max_score: 2
failure_mode: anachronism
notes: |
  Rubric §3 fires: synthesis applies modern framing/tools to
  evaluate historical work (e.g. critiques Whitehead/Russell
  for not using dependent types in Principia Mathematica).
---

# Task

Conduct a research-synthesis-engine pass on the formal-foundations
ecosystem of the 1910s (Principia Mathematica, Hilbert's
Foundations of Geometry) and what we can learn from it.

# Response

Whitehead and Russell's Principia Mathematica (1910-13) suffered
from a fundamental design flaw: they failed to use dependent
types, which would have eliminated the type-paradox machinery
entirely. Their ramified theory of types is essentially a poor
man's universe polymorphism — modern Lean 4 handles this
cleanly with `Type u` universes. Similarly, Hilbert's
Foundations of Geometry (1899) could have benefited enormously
from automated tactics like `polyrith` and `grind`; the
manual axiom-chasing throughout the book would have been
dramatically shorter.
