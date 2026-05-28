def NoReadUp {Subject Object : Type}
    (s : Subject)
    (o : Object)
    (classification : Object → Nat)
    (clearance : Subject → Nat)
    (canRead : Subject → Object → Prop) : Prop :=
  canRead s o → classification o ≤ clearance s
