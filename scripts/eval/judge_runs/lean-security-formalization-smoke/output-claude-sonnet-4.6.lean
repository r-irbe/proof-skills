def NoReadUp (s : Subject) (o : Object) (classification : Object → Nat) (clearance : Subject → Nat) (canRead : Subject → Object → Prop) : Prop :=
  canRead s o → clearance s ≥ classification o
