# Lint and package validation

This directory contains the package-level APM validator. The old prototype
`check_skill.py` and its generated `compliance-report.md` snapshot were
removed after the corpus reached full v2 conformance; use
`scripts/skill-audit/check_conformance.py` for schema, handoff, tier,
handbook-link, inline `@skill`, and relative Markdown-link checks.

## Current checks

```bash
# Validate apm.yml and every packaged first-party skill.
python3 scripts/lint/apm_validate.py --report

# Emit a machine-readable package summary.
python3 scripts/lint/apm_validate.py --json

# Full corpus conformance and routing-graph audit.
python3 scripts/skill-audit/check_conformance.py --fail-on hard
```

`apm_validate.py` is intentionally narrow: it verifies that this repository is
installable as an APM skill collection and that each packaged
`skills/<name>/SKILL.md` has valid frontmatter. It does not inspect override
skills, routing edges, or handbook extraction; those checks live in
`scripts/skill-audit/`.
