---
name: "ai-guard-judge-eval-handbook"
description: "Reference handbook for @ai-guard-judge-eval."
extracted_from: "skills/ai-guard-judge-eval/SKILL.md"
---

# ai-guard-judge-eval

## When to Use

- You have (or plan) an LLM judge that adjudicates flagged actions -
  commands, diffs, agent tool calls - and you must know its sensitivity,
  specificity, and stability before trusting it.
- You are comparing candidate judge models (e.g. a guard-tuned 4B vs a
  general 8B) and need a defensible, reproducible measurement.
- You changed the judge's prompt (rubric) and must prove the change helped
  without breaking specificity.
- You need to integrate a judge model whose native output format differs
  from your pipeline's contract, and record that adaptation honestly.

Not for: continuous-score quality rating (use post-hoc calibration per
Morandi 2026); preference ranking of chat models (use arena/Glicko-style
pairwise flows).

## Method

1. **Band-stratified item set (target 200-400).** Stratify real data
   through the deterministic gate: every ESCALATE, every BLOCK, a capped
   random WARN sample, a random ALLOW sample, plus synthetic adversarial
   probes ('unsafe' by construction). Record per item: band, label,
   label_source (operator / derived / synthetic), gate raw + effective
   verdicts. Labels are hypotheses; judge disagreements are the output.
   Keep hand-labelled anchors as a separate always-reported set.
2. **Band-wise runs.** Sensitivity is measured on unsafe bands (E/B/X),
   specificity on benign bands (N), the ambiguous band (W) is reported
   descriptively. Chunked runs by band keep each measurement inside one
   session and isolate failure modes.
3. **Per-judge schema adapters.** Heterogeneous models need per-model
   prompt styles AND parsers; record the translation (e.g. a 3-level
   native scale mapped to a 0-4 severity) as schema adaptation, not
   judging. Known traps, measured: thinking-mode models emit the answer
   in the thinking channel (disable thinking or read the channel); safety
   -tuned models override demanded JSON contracts with their native
   format (parse the native format); token caps truncate rationales
   before verdicts.
4. **Repeat-pass distributions.** Single passes cannot rank prompt
   generations (measured: verdict flips at temperature 0; a prompt change
   that 'improved' sensitivity in one pass regressed in the full set).
   Run --repeat 3+ and compare distributions per band.
5. **Audit everything.** Every judge decision row: judge_id, prompt_style,
   band, raw output digest, parsed finding. Rows are append-only with
   judge tags (three judges sharing one log without tags corrupts
   deduplication). Hash-chain the log when the judge feeds enforcement.

## Workflow

1. Extract the real command/decision corpus; dedup by exact text.
2. Run the deterministic gate + active profile over it; bucket by
   effective verdict; sample caps per class token for W.
3. Write synthetic probes covering each dangerous-verb family the
   gate defends (reverse shells, encoded pipes, credential exfil,
   persistence, destruction).
4. Emit the set with seed + label provenance in metadata; commit it.
5. Per judge: schema adapter + prompt style; smoke on 3 unsafe items
   (verify parseability) before any full run.
6. Full band runs; aggregate per band; record the table.
7. For rubric changes: gen N+1 runs full set x repeat 3; adopt only if
   target band improves AND benign specificity holds within one flip;
   register the distribution deltas and any negative results.

## Pitfalls

- Gate misfires contaminate derived labels (measured: 10/10 'escalate'
  items the judge rightly cleared were gate regex errors) - report
  E-band disagreements as label noise, then fix the gate separately.
- One over-broad regex caused 4 of 10 escalations (a config-write rule
  firing on config reads). Fix patterns at the source AND file the
  upstream finding: drift-parity with a source policy is not correctness.
- Flag-order and text-scanning quirks are portable: port rules verbatim
  and document the defect rather than silently fixing (parity audits).
- A hyper-recall judge (flags benign at 97%) and a high-specificity
  under-flagger can come from the same model family - never compare on
  one metric alone.
- Model management: pull GGUFs to an engine-neutral store and register
  engines by reference (Modelfile FROM <abs path>); opaque engine caches
  lock models to one runtime.

## Verification

- Set reproducibility: fixed seed rebuilds byte-identical item set.
- Parseability smoke (3 items/judge) before full runs; zero 'error'
  outcomes in a full run is the entry bar.
- Aggregate table: per-band sensitivity + specificity + speed, one row
  per judge, next to the always-reported hand-labelled anchors.
- Adoption gate: --repeat 3 distributions; target-band improvement with
  benign-band held within one flip; deltas recorded next to baselines.

## Recovery

- If a judge emits unparseable output during the 3-item smoke check, stop the full run and fix the per-judge schema adapter or disable thinking-channel
  capture before spending full-set compute.
- If E-band disagreements trace to deterministic gate regex false positives, record them as label noise and fix the gate pattern separately rather than
  tuning the judge rubric to mimic gate bugs.

## Handoffs

- **Predecessors:** `@applied-data-information-security` (policy threat model), `@lean-ai-formalization` (assurance requirements).
- **Successors:** `@lean-ai-formalization` (certification evidence), `@applied-engineering-disciplines` (reliability & testing integration).
