# Evaluation History & Fleet Patterns

Lessons captured from Rounds 18-21 of large-fleet ensemble work:

1. **Haiku /tmp sandbox quirk:** claude-haiku-4.5 agents sometimes refuse to write to /tmp. Mitigation: inline prompts and use write_agent/read_agent.
2. **Mac bash is 3.x:** It lacks associative arrays (`declare -A`). Use Python.
3. **Median over Minority-Veto:** When N >= 3 judges are available, prefer `statistics.median` over `min(low_band)`.
4. **32-concurrent dispatch cap:** Stay under 32 task dispatches in flight.
