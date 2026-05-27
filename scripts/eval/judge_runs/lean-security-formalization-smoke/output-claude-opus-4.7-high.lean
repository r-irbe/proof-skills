For subjects S, objects O, security levels with partial order ≤, classification c: O → L, and clearance λ: S → L, the Simple Security Property (no-read-up) states:

∀ s ∈ S, ∀ o ∈ O. read ∈ access(s, o) ⟹ c(o) ≤ λ(s)

That is, a subject s may read an object o only if the object's classification is dominated by the subject's clearance.