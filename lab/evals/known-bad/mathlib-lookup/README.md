# Known-bad calibration corpus (`mathlib-lookup` skill)

Per `lab/design/01-eval-framework.md §4.2` + ADR-0039. Each
`*.transcript.md` is a Mathlib-lookup response with an
`expected_max_score` in YAML frontmatter. The `mathlib-lookup-quality`
rubric uses `pass_floor=4`, `threshold=4`, `floor=2`: scores ≤ 2 are
flagged.

* **Negatives** (`expected_max_score ≤ 2`) — should be flagged. The
  judge ensemble must flag ≥ 90% of these (recall gate).
* **Adversarial positives** — not yet authored for this skill. When
  added, the false-flag gate in CI should be lowered from `1.00` to a
  realistic ceiling.

## Corpus (2026-05-27 — 5 negatives, 0 adversarial)

| Transcript | Failure mode | Rubric clause |
|---|---|---|
| `fabricated-lemma.transcript.md` | `fabricated_name` (`Finset.card_disjoint_union_le`) | score 1: fabricated lemma |
| `wrong-namespace.transcript.md` | `wrong_namespace` (`Set.card_union_le` for Finset task) | score 2: wrong namespace |
| `coq-style-name.transcript.md` | `wrong_library` (`Finset.cardinal_union_le_addition`) | score 1: fabricated / non-Mathlib naming |
| `empty-response.transcript.md` | `empty_response` (no lemma named) | score 1: empty |
| `wrong-signature.transcript.md` | `wrong_signature` (invented `Disjoint` hyp on `Finset.card_union_le`) | score 2: wrong signature |

## Replies (captured offline)

Sub-folder `_replies/<task_id>/<judge-id>.json`. The judge ensemble
is the 3-model Anthropic family used for `lean-proof` (`claude-opus-4.7-high`,
`claude-sonnet-4.6`, `claude-opus-4.6`). Replies are bit-identical
artifacts produced once by the Copilot CLI sub-agent fleet via
`scripts/eval/graders/DISPATCH.md` Flavour A.

## Calibration history

| Date | Ensemble | flag_rate | false_flag_rate | Report |
|---|---|---|---|---|
| 2026-05-27 | opus-4.7-high + sonnet-4.6 + opus-4.6 | 5/5 = 100% | 0/0 (n/a) | `reports/_calibration/mathlib-lookup-quality/ensemble-2026-05-27.json` |

## Reproducing

```bash
# Build prompts
for t in lab/evals/known-bad/mathlib-lookup/*.transcript.md; do
  python3 scripts/eval/calibrate_judge.py build \
    --rubric scripts/eval/graders/rubrics/mathlib-lookup-quality.yaml \
    --transcript "$t" \
    --out "/tmp/cal-lookup/$(basename $t .transcript.md).txt"
done

# Dispatch each prompt to N judges (Copilot CLI `task` tool, one
# sub-agent per (transcript, judge) pair). Capture the JSON reply at
# lab/evals/known-bad/mathlib-lookup/_replies/<task_id>/<judge>.json

# Re-aggregate offline
python3 scripts/eval/calibrate_judge.py check \
  --rubric scripts/eval/graders/rubrics/mathlib-lookup-quality.yaml \
  --skill-dir lab/evals/known-bad/mathlib-lookup \
  --label ensemble-2026-05-27 \
  --min-flag-rate 0.90
```
