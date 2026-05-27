Let L be a security lattice with partial order ≤, where x ≤ y means "x is dominated by y" or "y is at least as classified as x."
Each subject s has a clearance label clr(s) ∈ L and each object o has a classification label cls(o) ∈ L.
The Bell-LaPadula simple-security condition (no-read-up) requires that a read by subject s of object o is permitted only if cls(o) ≤ clr(s).
Equivalently, the transition rule for a read request is enabled only when dominates(clr(s), cls(o)) holds.
A system state σ satisfies no-read-up iff for every actual read edge (s,o) present in σ, cls(o) ≤ clr(s).
Thus a subject at Secret may read Confidential and Secret objects, but not Top Secret objects.
