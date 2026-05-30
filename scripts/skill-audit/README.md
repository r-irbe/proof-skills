# Skill-audit tools

Tools for auditing the SKILL corpus structure, conformance, and routing graph.

## `check_conformance.py`

One-shot corpus audit: v2 conformance + handoff DAG + handbook cross-links +
inline `@skill` refs + relative Markdown links.

### Usage

```bash
# From repo root:
python3 scripts/skill-audit/check_conformance.py

# With outputs:
python3 scripts/skill-audit/check_conformance.py \
    --json /tmp/audit.json \
    --md   lab/skill-audit/audit-$(date +%F).md

# Exit-code modes:
python3 scripts/skill-audit/check_conformance.py --fail-on hard   # default: exit 1 on broken refs/links/schema
python3 scripts/skill-audit/check_conformance.py --fail-on any    # also exit 1 on orphans/dead-ends
python3 scripts/skill-audit/check_conformance.py --fail-on never  # always exit 0
```

### What it checks

| Check | Purpose | Hard-fail? |
|---|---|---|
| v2 conformance (USE FOR/DO NOT/TRIGGERS in description + ## Workflow/Recovery/Handoffs in body + tier in YAML) | Every non-REDIRECT SKILL.md should be v2 | ✓ |
| Invalid `handoffs.successors` / `handoffs.predecessors` refs | Every `skill:X` must resolve to a real skill or override | ✓ |
| `references/<name>-handbook.md` link integrity | Every layered SKILL must point at an existing handbook | ✓ |
| Handbook `extracted_from:` back-references | Handbook YAML preamble must back-link to its source SKILL | ✓ |
| Inline `@skill` refs | Active SKILL.md files must point only at existing non-REDIRECT skills | ✓ |
| Relative Markdown links | Ordinary non-image Markdown links in SKILL.md must resolve on disk | ✓ |
| Mutual peer pairs (X↔Y handoffs) | Reported (by-design collaboration pattern) | ✗ |
| True cycles (length ≥ 3) | Reported (editorial feedback loops are by-design) | ✗ |
| Orphans (no upstream) | Reported (entry points are intentional) | ✗ |
| Dead-ends (no downstream) | Reported (terminal operational tools are intentional) | ✗ |
| Tier distribution | Reported (helps spot missing `tier:` fields) | ✗ |

### Dependencies

- Python 3.7+
- PyYAML (`pip install pyyaml`)

### Output

The Markdown report can be committed to `lab/skill-audit/` as an audit
artifact (the file is structured to slot into the same folder as
`audit-2026-05-27-snapshot.md` and `audit-2026-05-27-handoff-dag.md`).

The JSON report is machine-readable for CI integration.

### Provenance

Promoted from inline audit Python that lived in
`audit-2026-05-27-snapshot.md` + `audit-2026-05-27-handoff-dag.md` commit
messages (passes 12 + 16). The promotion was tracked as the
"Promote inline audit Python to scripts/skill-audit/check_conformance.py"
item in the W17 HITL form.

If you want to extend it (e.g. add a content-fidelity check for layered
skills via the diff-harness pattern from passes 14-16), add a new
`audit_*()` function and include its results in the `report` dict and
`render_md()` formatter.
