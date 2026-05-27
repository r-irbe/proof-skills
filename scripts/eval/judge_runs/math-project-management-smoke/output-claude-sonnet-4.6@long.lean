The project has five tasks with the following durations and dependencies.

Task A — Requirements Gathering — 3 days, no predecessors.
Task B — Formal Specification Writing — 5 days, depends on A.
Task C — Model and Schema Design — 4 days, depends on A.
Task D — Verification and Proof — 6 days, depends on both B and C.
Task E — Documentation and Review — 2 days, depends on D.

Forward pass (Early Start / Early Finish):
A: ES=0, EF=3.
B: ES=3, EF=8.
C: ES=3, EF=7.
D: ES=max(EF_B, EF_C)=max(8,7)=8, EF=14.
E: ES=14, EF=16.
Project duration = 16 days.

Backward pass (Late Start / Late Finish, working from project end):
E: LF=16, LS=14.
D: LF=14, LS=8.
B: LF=8, LS=3.
C: LF=8, LS=4.
A: LF=min(LS_B, LS_C)=min(3,4)=3, LS=0.

Total Float (LS minus ES):
A: 0. B: 0. C: 1 (non-critical). D: 0. E: 0.

Critical path is A → B → D → E with a total length of 3+5+6+2 = 16 days.
Task C has one day of float; it can slip by one day without affecting the project end date.
Any delay on A, B, D, or E directly extends delivery.
To compress the schedule, target D (6 days) first as it has the greatest duration on the critical path and offers the highest leverage for crashing.
