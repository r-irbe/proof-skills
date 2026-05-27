# Known-bad calibration corpus (`lean-setup-import` skill)

Per `lab/design/01-eval-framework.md §4.2` + ADR-0039. Each
`*.transcript.md` is a Lean setup/import response with an
`expected_max_score` in YAML frontmatter. The `lean-setup-import-quality`
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
| `fabricated-module.transcript.md` | `wrong_module` (`Mathlib.AllTheThings`) | score 2: fabricated module |
| `deep-internal-import.transcript.md` | `deep_internal_import` (`Init.System.IO`) | score 2: deeply-internal module |
| `syntactically-broken.transcript.md` | `parse_error` (`Import Mathlib::`) | score 1: syntactically broken |
| `empty-response.transcript.md` | `empty_response` (prose only) | score 1: no Lean code |
| `sorry-in-config.transcript.md` | `contains_sorry` (`import sorry`) | score 1: sorry in setup |

## Replies (captured offline)

Sub-folder `_replies/<task_id>/<judge-id>.json`. The judge ensemble
is the 3-model Anthropic family used for `lean-proof` (`claude-opus-4.7-high`,
`claude-sonnet-4.6`, `claude-opus-4.6`). Replies are bit-identical
artifacts produced once by the Copilot CLI sub-agent fleet via
`scripts/eval/graders/DISPATCH.md` Flavour A.

## Calibration history

| Date | Ensemble | flag_rate | false_flag_rate | Report |
|---|---|---|---|---|
| 2026-05-27 | opus-4.7-high + sonnet-4.6 + opus-4.6 | 5/5 = 100% | 0/0 (n/a) | `reports/_calibration/lean-setup-import-quality/ensemble-2026-05-27.json` |
| 2026-05-27 | + claude-haiku-4.5 + gpt-5.2 (**5-judge**) | 5/5 = 100% | 0/0 (n/a) | `reports/_calibration/lean-setup-import-quality/ensemble-5model-2026-05-27.json` |

## Reproducing

```bash
# Build prompts
for t in lab/evals/known-bad/lean-setup-import/*.transcript.md; do
  python3 scripts/eval/calibrate_judge.py build \
    --rubric scripts/eval/graders/rubrics/lean-setup-import-quality.yaml \
    --transcript "$t" \
    --out "/tmp/cal-setup/$(basename $t .transcript.md).txt"
done

# Dispatch each prompt to N judges (Copilot CLI `task` tool, one
# sub-agent per (transcript, judge) pair). Capture the JSON reply at
# lab/evals/known-bad/lean-setup-import/_replies/<task_id>/<judge>.json

# Re-aggregate offline
python3 scripts/eval/calibrate_judge.py check \
  --rubric scripts/eval/graders/rubrics/lean-setup-import-quality.yaml \
  --skill-dir lab/evals/known-bad/lean-setup-import \
  --label ensemble-2026-05-27 \
  --min-flag-rate 0.90
```
