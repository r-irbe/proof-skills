# LLM-judge dispatch orchestration

The grader in `graders/llm_judge.py` is intentionally **pure**: it
builds the prompt from a case + response + rubric, and parses a
judge's reply, but it never calls an API. The actual LLM call
happens in an *orchestrator* one layer up. This file documents two
flavours of orchestrator we currently support.

## Why is dispatch separated from grading?

Three reasons:

1. **Provider-agnostic.** Today we call Anthropic + a local Copilot CLI
   sub-agent. Tomorrow we may add OpenAI, vLLM, a self-hosted model,
   or a queued judge. The grader doesn't change.
2. **Replayable.** Judge replies are saved as JSON next to the case
   output. Re-running the grader against a stored reply costs $0 and
   gives a bit-identical `GradeResult`.
3. **Cost-aware.** Dispatch is the only step that costs money. Putting
   it in an orchestrator the human can see makes the budget visible.

## Flavour A — Local Claude sub-agent (Copilot CLI)

This is what the `r-irbe/proof-skills` toolkit uses to validate the
harness without consuming Anthropic API budget. The Copilot CLI's
`task` tool dispatches to a fresh Claude instance with `--model`
selection from the published roster.

Procedure:

1. Build the prompt: `python3 scripts/eval/graders/llm_judge.py build
   --case … --rubric … --response … --out judge_runs/<case>/prompt.txt`.
2. From the orchestrator session, dispatch one `task` per judge in
   the ensemble. Use the prompt text as the task body. The first
   character of the task body MUST be the judge's identity statement
   ("You are acting as an impartial LLM judge…"), to anchor the
   sub-agent.
3. Capture each task's reply (a single-line JSON object) into
   `judge_runs/<case>/judge-<model_id>.json`.
4. Grade with `python3 scripts/eval/graders/llm_judge.py grade
   --case … --rubric … --judge-reply judge-<m1>.json
   --judge-reply judge-<m2>.json … --out grade.json`.

The dispatch is currently manual (one `task` invocation per judge)
because the Copilot CLI doesn't expose a programmatic batch API for
sub-agents. A future `run_multi_judge.py` could automate this once
that API lands.

## Flavour B — Anthropic SDK (`run_multi_model.py`, future)

Per design `lab/design/01-eval-framework.md §6`, a production runner
will batch judge calls via the Anthropic / OpenAI SDKs with proper
parallelism, retry, rate-limit handling, and cost telemetry. The
*output* shape (one `judge-<id>.json` per ensemble member) stays
identical so the grader and downstream baseline diff are unchanged.

This flavour is API-budget-gated and not implemented yet.

## Anti-bias controls (per design §4.2)

The grader applies one mitigation in code (`_blind_response`, strips
model identity from the response payload before substituting into the
prompt). All other mitigations live in the rubric YAML and the
dispatch procedure:

- **Blinding** — done by the grader's `build_prompt(..., blind=True)`.
- **Position-swap** — for pairwise judges, run twice with A/B then B/A
  and only count if both agree (else draw). Done by the orchestrator.
- **Anti-length / anti-position** — instructions in `prompts/judge.txt`.
- **Self-consistency** — `rubric.bias_mitigations.self_consistency_runs`.

## Calibration (ADR-0039)

Before any LLM-judge enters CI on the deterministic-pass-rate gate,
run it across `lab/evals/known-bad/<skill>/*.transcript.md` (when that
directory exists) and confirm it flags ≥90 % as ≤2. Persist the
calibration in `reports/_calibration/<rubric>/<judge-model>.json`.
This is currently aspirational — the known-bad corpus does not exist
yet.

## File-layout invariants

For a single case `<C>` graded by `n` judges:

```
scripts/eval/judge_runs/<C>/
├── response.txt              # the candidate response (single-model case)
├── output-<player-id>.lean   # candidate response (multi-model case)
├── judge-<judge-id>.json     # raw judge reply (one per ensemble member)
└── grade.json                # aggregated GradeResult
```

For multi-model match generation (W9), one `output-<id>.lean` +
`judge-<id>.json` pair per entrant. `multi_model.py` consumes that
shape and emits pairwise CSV rows for `glicko2.py`.
