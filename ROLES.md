For a detailed explanation of the Swarm methodology and multi-agent theory, see [`references/swarm_methodology.md`](references/swarm_methodology.md).

# Multi-Agent Lifecycle Roles

## 1. Specifier
- **Skills**: `lean-specification`, `lean-blueprint`, `lean-mwe`, `lean-doc-requirements`
- **Output**: Well-typed `.lean` declarations with `sorry` placeholders
- **Stop Condition**: Clean elaboration without type errors -> Hands off to Prover

## 2. Prover
- **Skills**: `lean-proof`, `lean-setup`, `lean-build`, `lean-gateway`
- **Rules**:
  - No `trace_state` or diagnostic comments in source files
  - Harvest `Try this` code actions
  - Tactic hierarchy: `rfl` -> `omega` / `linarith` -> `simp only` -> `aesop` -> `exact?`
- **Stop Condition**: All goals closed (`0 sorry`) -> Hands off to Auditor

## 3. Auditor
- **Skills**: `lean-proof-review`, `lean-enforcement`, `lean-tautology-triage`, `lean-bisect`, `lean-pr`
- **Output**: Refactored, minimized proofs, bounded heartbeats, zero warnings
- **Stop Condition**: All linters pass and `lake build` green -> Hands off to Gardener

## 4. Gardener
- **Skills**: `lean-zettelkasten`, `lean-retro-methodology`, `lean-retroactive-audit`, `lean-review-council`
- **Stop Condition**: New patterns indexed, scratch memory purged

## Handoff Protocol
- **Format**: JSON schema defined in [`templates/handoff_protocol.json`](templates/handoff_protocol.json)
