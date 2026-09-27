# Agents (pi-subagents distribution)

pi-native agent definitions binding this skill corpus. These are
**distribution copies**: pi discovers agents from the project
`<root>/.pi/agents/` directory (preferred), legacy `<root>/.agents/`, or the
user directories — NOT from this submodule directly.

## Install

Pick one:

1. **Copy** the desired `*.md` files into your project's `.pi/agents/`
   directory (git-track them; regenerate on submodule bump, never
   hand-drift).
2. **Point** `PI_SUBAGENT_EXTRA_AGENT_DIRS` at this directory (session-level
   discovery; no copy).

The `skillPath: ../skills` frontmatter resolves relative to the agent file,
so copies must preserve the sibling layout (copy this whole `agents/`
directory next to a `skills/` directory), or the `skills:` selections fall
back to normal pi skill discovery.

## Inventory

- `proof-reviewer.md` — L1-L4 proof review binding `lean-proof-review`,
  `lean-proof`, `lean-enforcement`; GUARDRAILS mandatory read.
- `enforcement-auditor.md` — gate/harness audit binding `lean-enforcement`,
  `lean-quality-engine`; AOR-11 coverage-set discipline.
- `formalization-breakdown-curator.md` — multi-wave formalization archaeology binding `lean-formalization-breakdown`,
  `lean-blueprint`, `lean-enforcement`; census, DAG depth, landmark extraction.
- `math-pedagogy-author.md` — mathematical narrative and textbook-grade exposition binding `lean-pedagogical-exposition`,
  `lean-blueprint`, `lean-doc-improvement`.

All are read-only analysts (`tools: read, grep, find, ls, bash`) and
package-qualified under `proof-skills`.
