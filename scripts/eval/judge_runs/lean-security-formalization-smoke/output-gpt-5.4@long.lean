universe u v

def NoReadUp {Subject : Type u} {Object : Type v}
    (s : Subject) (o : Object)
    (classification : Object → Nat)
    (clearance : Subject → Nat)
    (canRead : Subject → Object → Prop) : Prop :=
  canRead s o → classification o ≤ clearance s
