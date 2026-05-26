# proof-skills

A bundle of [Agent Skills](https://agentskills.io) for writing
[Lean 4](https://github.com/leanprover/lean4) proofs against
[Mathlib4](https://github.com/leanprover-community/mathlib4). Installs
into any coding-agent harness via [APM](https://github.com/microsoft/apm).

```bash
apm install r-irbe/proof-skills
```

After install, each skill is hoisted into the harness's runtime
directory (Copilot, Claude Code, Cursor, OpenCode, Codex, Gemini, or
Windsurf) and becomes invocable by name. Pinning, single-skill
selection, and lockfile reproducibility work the same way they do
for any other APM package; the manifest is [`apm.yml`](apm.yml) and
the layout is APM's *skill collection* type.

If you would rather have the source tree on disk than depend on APM,
clone the repo with submodules:

```bash
git clone --recurse-submodules https://github.com/r-irbe/proof-skills
```

## What is in here

The repo collects three kinds of material that turn out to be useful
together when an agent is doing real proof work.

**Skills** (`skills/`, 53 folders) cover Lean toolchain setup, proof
tactics, MWE extraction, bisection, PR hygiene, Mathlib review,
domain-specific math reasoning, applied verticals, and end-to-end
process workflows like blueprint regeneration and retrospective
audits. Each folder ships a single `SKILL.md` that the runtime loads
on demand. A handful of folders under `skills/_overrides/` shadow
upstream [`leanprover/skills`](https://github.com/leanprover/skills)
entries that we needed to audit-modify; the dispatch order
(first-party → override → upstream vendor) is documented in
[`AGENT.md`](AGENT.md) §3.

**Templates** (`templates/`) are copy-pasteable Lean module
skeletons. Twelve v1 templates cover the common shapes (foundation,
analysis, dynamics, automation, performance, refactoring, …) and
twelve v2 production templates extracted in W6 (theorem, data module,
tactic helper, bridge, plus eight workflow artefacts: MWE, PR,
blueprint, zettelkasten, spec, bisect, council, retro log). The
cross-template conventions — file-doc header, section skeleton,
proof-comment tags, anti-patterns checklist — live in
[`templates/00-CONVENTIONS.md`](templates/00-CONVENTIONS.md).

**References and scripts** are background material a skill points at
when it needs to. `references/` collects theorem-search idioms
(Loogle, Moogle, LeanSearch, Mathlib doc-gen 4), proof-strategy
notes, and refactor playbooks. `scripts/lean/` ships project-agnostic
helpers: axiom audits, DAG layer checks, bridge validators,
zettelkasten linters. None of them hardcode a host project; they take
the project root as an argument.

## Tooling

`scripts/lint/check_skill.py` validates a `SKILL.md` against the v2
template. `scripts/lint/apm_validate.py` (hard-gated in CI) checks
that the package stays a valid APM skill collection: manifest keys
present, each `SKILL.md` has the agentskills.io-required `name` and
`description`, directory names match, no duplicates.
`scripts/eval/run_eval.py` is a v0 advisory eval harness;
`scripts/elo/elo.py` is a stdlib-only ELO calculator for cross-model
A/B benchmarks. The full eval/ELO production hardening is on the
roadmap (W8/W9 of the master plan).

## Project-specific overrides

The toolkit is deliberately project-agnostic — templates and skills
use `<Project>` / `<proj>` placeholders. Downstream projects encode
their concrete values in a thin override layer rather than forking
the templates. The reference implementation lives in this repo's
parent project at `docs/easci/lean/skills-overrides/`; the rule is
that an override file links back to the generic source and lists
only the deltas.

## Status

Apache-2.0, standalone repository (not a fork). Upstream
`leanprover/skills` is vendored as a read-only git submodule at
`vendor/leanprover-skills/` so its slugs remain dispatchable.
Structural changes (`AGENT.md`, top-level layout, license,
this README, submodule pin) trigger the HITL gate in
[`AGENT.md`](AGENT.md) §1; history rewrites and force-pushes are
explicitly off-limits.

See [`AGENT.md`](AGENT.md) for the full contract — belief threshold,
reversibility tiers, dispatch precedence, confidentiality rules — and
[`apm.yml`](apm.yml) for the package metadata.
