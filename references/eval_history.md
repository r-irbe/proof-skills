# Evaluation History & Fleet Patterns

## 1. Context and Motivation
Running multi-agent systems at scale introduces unique sandbox and coordination challenges not seen in single-turn code generation. Lessons captured from Rounds 18-21 of large-fleet ensemble work (involving hundreds of `task` dispatches per session for solver, judge, and calibration loops) inform our `AGENT.md` guidelines.

*   *Reference*: Shinn, N., et al. (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning." *NeurIPS*.
*   *Application*: Ensemble judging and pure-replay calibration strategies reduce the hallucination rate of multi-agent formalization loops.

## 2. Specific Patterns

1. **Haiku /tmp sandbox quirk:** `claude-haiku-4.5` agents sometimes refuse to write to `/tmp` citing sandbox limitations.
   - *Mitigation*: Inline prompts and use `write_agent` / `read_agent` from the parent process.
2. **Mac bash is 3.x:** Mac OS ships with an outdated bash version lacking associative arrays (`declare -A`).
   - *Mitigation*: Promotion scripts must use Python or explicitly call `bash 4+`.
3. **Median over Minority-Veto:** When N >= 3 judges are available, prefer `statistics.median` over `min(low_band)`. Minority-veto propagates any single <=floor judge regardless of how many score high (e.g., R19 lean-proof false-flag rate stuck at 20% due to this).
4. **32-concurrent dispatch cap:** Stay under 32 task dispatches in flight. Batch into waves of <= 30 with brief gaps.
