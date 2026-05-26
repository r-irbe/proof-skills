# proof-skills

A standalone toolkit of [Agent Skills](https://agentskills.io) for
working with [Lean 4](https://github.com/leanprover/lean4) and
[Mathlib4](https://github.com/leanprover-community/mathlib4): formal-
verification helpers, math-domain skills, doc/review/research workflows,
zettelkasten patterns, and generic Lean tooling — all callable from any
Lean 4 project.

> **For AI agents.** Read [`AGENT.md`](AGENT.md) before touching any
> file. It defines the HITL gating contract (belief < 0.90 ⇒ ask),
> reversibility tiers, layout invariants, and the skill-dispatch
> precedence rule.

---

## Status

- Standalone repository — not a fork.
- License: Apache-2.0 (see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE)).
- Upstream `leanprover/skills` is referenced read-only as a git
  submodule at `vendor/leanprover-skills/`; local overrides live under
  `skills/_overrides/`.

---

## Layout

```
proof-skills/
├── AGENT.md                # agent contract (HITL, dispatch, governance)
├── LICENSE                 # Apache-2.0
├── NOTICE                  # upstream attribution per Apache-2.0 §4
├── README.md               # this file
├── skills/                 # first-party skills (53+ folders, one SKILL.md each)
│   └── _overrides/         # local overrides of upstream slugs
├── templates/              # copy-pasteable Lean module / proof / refactor templates
├── references/             # background knowledge (theorem search, Mathlib idioms, etc.)
├── scripts/                # tooling
│   ├── lean/               # generic Lean-4 helpers (axiom audit, DAG checks, bridge validators)
│   ├── check_skill.py      # SKILL.md v2 linter
│   └── check-structure     # repo layout check
├── zettelkasten/           # reserved for canonical ZK (W7 of master plan)
└── vendor/
    └── leanprover-skills/  # git submodule → leanprover/skills (read-only)
```

---

## Skill-dispatch quickstart

When an agent or loader asks for a skill by slug `<X>`, resolve in
this order (first hit wins):

1. `skills/<X>/` — first-party.
2. `skills/_overrides/<X>/` — local overrides of upstream slugs.
3. `vendor/leanprover-skills/skills/<X>/` — upstream fallback.

See [`AGENT.md` §3.1](AGENT.md#31-skill-dispatch-precedence) for the
authoritative rule.

---

## Install

```bash
git clone --recurse-submodules https://github.com/r-irbe/proof-skills.git
cd proof-skills
```

If you already cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

---

## Skill catalogue (highlights)

The `skills/` tree contains 50+ skills across these themes
(see each folder's `SKILL.md` for the agent-loadable contract):

- **Lean 4 / Mathlib**: `lean-proof`, `lean-bisect`, `lean-mwe`,
  `lean-pr`, `lean-setup`, `mathlib-build`, `mathlib-pr`,
  `mathlib-review`, `nightly-testing` (upstream + overrides).
- **Math domains**: `math-measure-probability`,
  `math-nonlinear-dynamics`, `math-time-series`, `math-topology-analysis`,
  `math-algebra-category`, `math-graph-knowledge`,
  `math-optimization-game`, `math-strategy-studio`, etc.
- **AI / reasoning**: `ai-causal-deontic`, `ai-symbolic-neuro`,
  `ai-agentic-evolving`, `ai-commonsense-reasoning`,
  `ai-high-stakes-verifiable`.
- **Lean-domain formalisations**: `lean-math-foundations`,
  `lean-math-analysis`, `lean-math-stochastic`, `lean-math-dynamical`,
  `lean-math-optimization`, `lean-math-discrete`,
  `lean-causal-reasoning`, `lean-ai-formalization`,
  `lean-security-formalization`.
- **Process / research**: `lean-research`, `lean-research-types`,
  `research-council`, `research-synthesis-engine`,
  `lean-review-council`, `lean-proof-review`, `lean-report`,
  `lean-blueprint`, `lean-retro-methodology`, `lean-retroactive-audit`,
  `lean-zettelkasten`, `epistemic-mapping`,
  `epistemic-discovery-engine`.
- **Applied verticals**: `applied-legal-reasoning`,
  `applied-data-information-security`,
  `applied-engineering-disciplines`, `applied-strategy-analysis`,
  `applied-intelligence-analysis`.
- **Docs / governance**: `lean-doc-improvement`,
  `lean-doc-requirements`, `lean-doc-feedback`,
  `lean-integration-protocol`, `lean-knowledge-formalization`,
  `lean-enforcement`, `lean-gateway`, `lean-specification`,
  `lean-nested-learning`.

---

## Templates and references

- `templates/` ships Lean module headers, proof-skeleton patterns, and
  refactor templates. Drop into any Lean 4 project; substitute the
  obvious placeholders (`MyProject`, `Foo`, etc.).
- `references/` is browsable background knowledge that individual
  skills link to from their `## See also` footers. Topics include
  theorem search (Loogle, Moogle, LeanSearch, Mathlib doc-gen 4),
  Mathlib refactor playbooks, proof strategy, etc.

---

## Tooling

- `scripts/check_skill.py` — validates `SKILL.md` against the v2
  template (frontmatter, sections, link integrity).
- `scripts/check-structure` — quick repo layout sanity check.
- `scripts/lean/` — generic Lean-4 helpers (axiom audit, DAG validators,
  bridge sanity checks, etc.). All take CLI flags or env vars for
  project paths — none hardcode a host project.

Eval / ELO scaffolding (advisory linter CI, skill eval harness, ELO
runner for cross-model skill benchmarking) lands in the W1 wave of the
master plan; the public scaffold will appear under `scripts/eval/` and
`scripts/elo/` once promoted from prototype.

---

## Contributing

The HITL contract in `AGENT.md` governs both AI agents and human
contributors making structural changes. Specifically:

- Any change to `AGENT.md`, top-level layout, license, NOTICE, or this
  README is a **Governance** trigger (hard HITL gate — ask first).
- History rewrites, force-pushes, and submodule pin bumps are
  `irreversible_data` (hard HITL gate).

PRs that add or modify a skill should keep example identifiers
obviously synthetic — no real downstream project names, no internal
ADR numbers, no internal directory paths. See `AGENT.md` §2.

---

## License

[Apache License 2.0](LICENSE). See [`NOTICE`](NOTICE) for upstream
attribution per Apache-2.0 §4.
