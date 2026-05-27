∀d ∀t (Driver(d) ∧ AtIntersection(d, t) ∧ FacingSignal(d, s, t) ∧ Red(s, t) → Stops(d, t))

Where:
- Driver(d): d is a driver
- AtIntersection(d, t): d is at an intersection at time t
- FacingSignal(d, s, t): d faces traffic signal s at time t
- Red(s, t): signal s shows red at time t
- Stops(d, t): d comes to a complete stop at time t
