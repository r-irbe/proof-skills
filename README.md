<div align="center">

# proof-skills

**A bundle of [Agent Skills](https://agentskills.io) for Lean 4 + Mathlib4 proof work.**

Tactics · domain math · doc / review / research workflows · zettelkasten · generic tooling.

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Lean 4](https://img.shields.io/badge/Lean-4-2D3748.svg?logo=lean&logoColor=white)](https://github.com/leanprover/lean4)
[![Mathlib4](https://img.shields.io/badge/Mathlib-4-4E7CD0.svg)](https://github.com/leanprover-community/mathlib4)
[![APM](https://img.shields.io/badge/APM-skill_collection-6e5494.svg)](https://github.com/microsoft/apm)
[![Skills](https://img.shields.io/badge/skills-53-2c974b.svg)](skills/)

</div>

---

## Quick start

Install into any coding-agent harness via [APM](https://github.com/microsoft/apm):

```bash
apm install r-irbe/proof-skills                       # entire bundle
apm install r-irbe/proof-skills --skill lean-proof    # single skill
apm install r-irbe/proof-skills#v0.1.0                # version-pinned
```

After installation, each skill is hoisted into the harness's runtime
directory — Copilot, Claude Code, Cursor, OpenCode, Codex, Gemini, or
Windsurf — and becomes invocable by name. Pinning, single-skill
selection, and lockfile reproducibility work the same way they do for
any other APM package; the manifest is [`apm.yml`](apm.yml) and the
layout is APM's *skill collection* type.

Prefer the source tree on disk instead?

```bash
git clone --recurse-submodules https://github.com/r-irbe/proof-skills
```

---

## What is in here

| Directory | What it holds | Loaded by |
|---|---|---|
| [`skills/`](skills/) | 53 first-party `SKILL.md` files: toolchain setup, proof tactics, MWE extraction, bisection, PR hygiene, Mathlib review, domain math, applied verticals, and end-to-end process workflows (blueprint regeneration, retrospective audits). | Harness, on demand. |
| [`skills/_overrides/`](skills/_overrides/) | Shadows of [`leanprover/skills`](https://github.com/leanprover/skills) entries that needed audit-modification. Dispatch order **first-party → override → upstream vendor** is documented in [`AGENT.md`](AGENT.md) §3. | Harness, on demand. |
| [`templates/`](templates/) | copy-pasteable Lean module skeletons: foundation, analysis, dynamics, automation, performance, refactoring, theorem, data module, tactic helper, bridge, MWE, PR, blueprint, zettelkasten, spec, bisect, council, retro log), etc. Cross-template conventions live in [`templates/00-CONVENTIONS.md`](templates/00-CONVENTIONS.md). | Author, copy-paste. |
| [`references/`](references/) | background notes a skill points at when needed: theorem-search idioms (Loogle, Moogle, LeanSearch, Mathlib doc-gen 4), proof-strategy notes, refactor playbooks, ergodic/IVT/time-series patterns, Mathlib4 conventions. | Skill, by link. |
| [`scripts/`](scripts/) | Project-agnostic helpers: axiom audits, DAG layer checks, bridge validators, zettelkasten linters, eval/ELO harnesses. None hardcodes a host project; each takes the project root as an argument. | Skill / CI / author. |
| [`zettelkasten/`](zettelkasten/) | Repo-internal knowledge graph (fleeting · literature · permanent · index · tags) that captures cross-skill insights. | Synthesizer skills. |
| [`vendor/`](vendor/) | Pinned git submodules of upstream sources (e.g. `leanprover-skills`) for transparent re-dispatch. | Override dispatch. |

---

## Repository layout

```text
proof-skills/
├── apm.yml                  # APM manifest — package metadata
├── AGENT.md                 # Agent contract: belief threshold, dispatch precedence, …
├── README.md                # You are here
├── LICENSE · NOTICE         # Apache-2.0
├── skills/                  # 53 first-party SKILL.md + _overrides/
├── templates/               # 32 Lean module skeletons (v1 + v2)
├── references/              # 13 background notes (Loogle, Moogle, …)
├── scripts/
│   ├── lean/                # axiom_audit, bridge_validator, dep_graph, …
│   ├── lint/                # check_skill.py, apm_validate.py
│   ├── eval/                # run_eval.py (v0 advisory)
│   ├── elo/                 # elo.py (stdlib-only ELO)
│   └── check-structure/     # repo-shape sanity checks
├── zettelkasten/            # fleeting · literature · permanent
└── vendor/leanprover-skills # pinned upstream submodule
```

---

## Tooling

| Script | Purpose |
|---|---|
| [`scripts/lint/check_skill.py`](scripts/lint/check_skill.py) | Validates a `SKILL.md` against the template. |
| [`scripts/lint/apm_validate.py`](scripts/lint/apm_validate.py) | **Hard-gated in CI.** Checks the package stays a valid APM skill collection: manifest keys, required `name` + `description` per `SKILL.md`, directory-name match, no duplicates. |
| [`scripts/eval/run_eval.py`](scripts/eval/run_eval.py) | v0 advisory eval harness. |
| [`scripts/elo/elo.py`](scripts/elo/elo.py) | stdlib-only ELO calculator for cross-model A/B benchmarks. |

---

## Project-specific overrides

The toolkit is **deliberately project-agnostic** — templates and skills
use `<Project>` / `<proj>` placeholders. Downstream projects encode
their concrete values in a thin override layer rather than forking the
templates; the rule is that an override file **links back to the
generic source and lists only the deltas**.

---

## Status & contracts

| Document | Covers |
|---|---|
| [`AGENT.md`](AGENT.md) | Full agent contract — belief threshold, reversibility tiers, dispatch precedence, confidentiality rules. **Required reading before any edit.** |
| [`apm.yml`](apm.yml) | Package metadata: name, version, license, keywords, repository. |
| [`templates/00-CONVENTIONS.md`](templates/00-CONVENTIONS.md) | Cross-template conventions: file-doc header, section skeleton, proof-comment tags, anti-patterns checklist. |

---

<div align="center">
<sub>
Apache-2.0 · authored by <a href="https://github.com/r-irbe">@r-irbe</a> ·
issues & PRs welcome at
<a href="https://github.com/r-irbe/proof-skills">github.com/r-irbe/proof-skills</a>
</sub>
</div>
