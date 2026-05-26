# `check_skill.py` — prototype SKILL.md linter

**Status:** prototype (shape-only). Not wired into CI.
**Contract:** [`specs/templates/skill-template.md`](../../../../../filab-doc-experiment/specs/templates/skill-template.md)
**Forward refs:** ADR-0076 (FM schema), ADR-0080 (handoff DAG ID grammar).

## What it checks

Per file, the linter emits **pass / warn / fail** findings across these
buckets:

| Bucket                  | Rule (summary)                                                                                                  | Severity        |
|-------------------------|-----------------------------------------------------------------------------------------------------------------|-----------------|
| Frontmatter             | YAML block at file head, ends with `---`, parses as a mapping                                                   | fail            |
| Required FM keys        | `name`, `description`, `tier` are present and non-empty                                                         | fail            |
| Tier value              | `tier` ∈ {`hot`, `warm`, `cold`}                                                                                | fail            |
| Description markers     | Literal `USE FOR:` and `DO NOT USE FOR:`                                                                        | fail            |
| Description triggers    | Literal `TRIGGERS:`                                                                                             | warn            |
| Required body sections  | `## Routing`, `## Behavioural rules`, `## Workflow`, `## Recovery & STOP`, `## Handoffs`                        | fail (presence) |
| G-rules present         | At least one `G-N` line anchored as `G-1:` / `**G-1**` / similar                                                | fail            |
| G-rule modal keywords   | At least one G-line carries `MUST` / `SHOULD` / `MUST NOT` / `SHOULD NOT`                                       | fail            |
| Workflow numbered steps | `## Workflow` slice contains ≥2 numbered steps (`1.`, `2.`, …)                                                  | fail            |
| Workflow phase tags     | Workflow slice mentions all four of `[discover]`, `[execute]`, `[validate]`, `[persist]`                        | warn            |
| Hot-tier MANDATORY      | `tier: hot` ⇒ MANDATORY notice in body                                                                          | warn            |
| Handoffs ID grammar     | If `handoffs.predecessors` / `successors` present, every entry matches `<kind>:<slug>` per ADR-0080             | fail            |

**Out of scope (semantic adequacy):** G-rule trace integrity, source-spec
existence, dispatch_targets extraction correctness, `metadata.version` /
`last_reviewed` pairing, runtime-target validity, R250 auto-load extensions.
Those land in later slots and are the author's / reviewer's responsibility.

## How to run

```bash
# Lint one file or one directory tree (recursive on SKILL.md)
python3 scripts/lint/check_skill.py skills/

# Verbose: print every check including passes
python3 scripts/lint/check_skill.py -v skills/lean-blueprint/

# Markdown compliance table (used to produce compliance-report.md)
python3 scripts/lint/check_skill.py skills/ --report

# Machine-readable findings
python3 scripts/lint/check_skill.py skills/ --json
```

Exit code: `0` if every file passes, `1` if any file fails, `2` on
argument / IO error.

Dependencies: Python 3.9+, PyYAML (already on the dev image).

## Self-test 1 — proto v2 skills (positive control)

Three reference SKILL.md files live in `skills/` covering
all three tiers:

| skill              | tier | purpose                                                |
|--------------------|------|--------------------------------------------------------|
| `lean-blueprint`   | hot  | exercises MANDATORY block, 8 G-rules, 7-step workflow  |
| `epistemic-mapping`| warm | omits MANDATORY block (allowed); 5 G-rules             |
| `lean-doc-feedback`| cold | minimal compliant shape; 4 G-rules                     |

```
$ python3 scripts/lint/check_skill.py skills/
PASS  skills/epistemic-mapping/SKILL.md  (0 fail, 0 warn)
PASS  skills/lean-blueprint/SKILL.md     (0 fail, 0 warn)
PASS  skills/lean-doc-feedback/SKILL.md  (0 fail, 0 warn)
summary: 3/3 files passed
```

| skill              | tier | desc_markers | sections | g_rules | workflow | overall |
|--------------------|------|--------------|----------|---------|----------|---------|
| epistemic-mapping  | ✓    | ✓            | ✓        | ✓       | ✓        | ✓       |
| lean-blueprint     | ✓    | ✓            | ✓        | ✓       | ✓        | ✓       |
| lean-doc-feedback  | ✓    | ✓            | ✓        | ✓       | ✓        | ✓       |

## Self-test 2 — real corpus (62 skills, negative control)

Every existing SKILL.md predates the template, so a near-100 % failure
rate is the expected baseline. The linter quantifies the migration gap:

```
$ python3 scripts/lint/check_skill.py skills/
summary: 0/62 files passed
```

**Per-check breakdown across the 62 real skills:**

| Check                                | pass | fail | warn | check-not-run |
|--------------------------------------|-----:|-----:|-----:|--------------:|
| frontmatter present                  |   62 |    0 |    0 |             0 |
| frontmatter.tier present             |    0 |   62 |    0 |             0 |
| frontmatter.tier valid               |    0 |    0 |    0 |            62 |
| description has `USE FOR:`           |    0 |   62 |    0 |             0 |
| description has `DO NOT USE FOR:`    |    0 |   62 |    0 |             0 |
| description has `TRIGGERS:`          |    0 |    0 |   62 |             0 |
| section `## Routing`                 |    5 |   57 |    0 |             0 |
| section `## Behavioural rules`       |    0 |   62 |    0 |             0 |
| section `## Workflow`                |   13 |   49 |    0 |             0 |
| section `## Recovery & STOP`         |    0 |   62 |    0 |             0 |
| section `## Handoffs`                |    0 |   62 |    0 |             0 |
| G-rules present                      |    0 |   62 |    0 |             0 |
| G-rules carry MUST/SHOULD/MUST NOT   |    0 |    0 |    0 |            62 |
| workflow numbered steps              |    2 |    1 |    0 |            59 |
| workflow phase tags                  |    0 |    0 |    3 |            59 |
| hot-tier MANDATORY block             |    0 |    0 |    0 |            62 |

(*"check-not-run"* = the check is gated by an earlier failure — e.g. no
`tier` value to validate; no workflow body to count steps in.)

**Gap signal:** 100 % of the corpus is missing the entire body skeleton
(Routing / Behavioural rules / Recovery / Handoffs) and none carry
G-rules or a typed tier. The migration is structural, not cosmetic. The
13 skills that do have a `## Workflow` header still don't tag steps.

Full row-per-skill table: [`compliance-report.md`](./compliance-report.md).

## Files

```
scripts/lint/
├── README.md             this file
├── check_skill.py        the linter (~300 LOC, stdlib + PyYAML)
└── compliance-report.md  full row-per-skill table for the 62 real skills
```

## Known limitations (prototype)

- Section detection is header-text + substring; a skill that talks about
  "routing" in body prose without a `## Routing` header will still fail
  (correct) but a skill that has `### Routing rules` will pass on
  substring match (acceptable for a prototype).
- G-rule counting is anchor-based (`G-N`), not full grammar — adjacent
  modal-keyword check is a sample, not per-rule.
- No spec-trace check (e.g. `AC-N` resolves); ADR-0076 §gates will own
  that once the validator slot lands.
- No CI integration; this is a local dev tool.
