A 5-task formalisation project's critical path is the longest chain of dependent tasks from start to finish, determining the minimum total project duration; any delay on this chain delays the whole project.

Since you didn't provide the specific tasks, durations, or dependency structure, I'll demonstrate the method on a representative example and give you the general procedure to apply to your own data.

Example project (durations in days):
- A: Draft formal specification — 5 days, no predecessors
- B: Define notation and axioms — 3 days, depends on A
- C: Encode in proof assistant — 7 days, depends on B
- D: Peer review of draft — 4 days, depends on A
- E: Final consolidation and write-up — 2 days, depends on C and D

Step 1 — Forward pass (earliest start ES, earliest finish EF = ES + duration):
- A: ES=0, EF=5
- B: ES=5, EF=8
- C: ES=8, EF=15
- D: ES=5, EF=9
- E: ES=max(EF of C, EF of D)=max(15,9)=15, EF=17

Project duration = 17 days.

Step 2 — Backward pass (latest finish LF, latest start LS = LF − duration), starting from project end = 17:
- E: LF=17, LS=15
- D: LF=15, LS=11
- C: LF=15, LS=8
- B: LF=8, LS=5
- A: LF=5, LS=0

Step 3 — Slack (LS − ES) for each task:
- A: 0, B: 0, C: 0, D: 6, E: 0

Step 4 — Critical path = tasks with zero slack, in dependency order: A → B → C → E, total length 5 + 3 + 7 + 2 = 17 days.

Task D has 6 days of float and is not critical.

General procedure for your own 5 tasks:
1. List each task with its duration and immediate predecessors.
2. Enumerate every path from a start task (no predecessors) to an end task (no successors).
3. Sum durations along each path.
4. The critical path is the path with the maximum total duration; that sum is the project's minimum completion time.
5. Tasks on that path have zero slack and must not slip.

If you share the actual 5 tasks, their durations, and dependencies, I can compute the exact critical path for your project.
