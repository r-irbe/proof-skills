# 04 — Template v2 migration (historical)

**Status:** RECONSTRUCTED stub (R27 audit). Historical reference only.

## 1. What this was

The W6 wave promoted a "templates v2" proposal set that updated the
canonical case YAML shape. Several reports reference it as the source of
the current `id / skill / input.prompt / expected_output_substring` shape
seen in `scripts/eval/cases/`.

## 2. Current state of cases

All 50 active smoke case YAMLs use the v2 shape:

```yaml
id: <case-slug>
title: "<human-readable title>"
skill: <skill-slug>          # the SKILL.md this case targets
difficulty: <easy|medium|hard>
ensemble_rubric: <rubric>    # R27 audit: now explicit on every case
input:
  prompt: |
    <prompt body>
  expected_output_substring: |
    <one or more substrings the answer should contain>
expected:
  contains:
    - <regex>
  not_contains:
    - <regex>
```

R27 audit added the `ensemble_rubric:` field to the cases that previously
lacked it, and later rounds preserved that explicit field as the suite grew to
50 smoke cases.

## 3. Migration provenance

The migration ran in W6 (commits referenced in `lab/reports/_archive/`).
Historical context only — re-do of this migration is not anticipated.

## 4. Pointers

- Current case examples: `scripts/eval/cases/lean-add-comm-multi.yaml`,
  `scripts/eval/cases/applied-legal-reasoning-smoke.yaml`.
- Rubric authoring: `scripts/eval/graders/rubrics/*.yaml`.
