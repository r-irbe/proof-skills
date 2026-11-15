---
id: zk-index
title: Proof-skills zettelkasten -- index
created: 2026-05-27
updated: 2026-11-15
type: literature
tags: [moc, index, seed]
refs:
  - zk-001
  - zk-002
  - zk-003
  - zk-004
  - zk-005
  - zk-006
  - zk-007
  - zk-008
  - zk-009
  - zk-010
  - zk-011
  - zk-012
  - zk-013
  - zk-014
  - zk-015
status: validated
confidence: high
---

# Proof-skills zettelkasten -- index

This is the entry-point Map-of-Content for the fifteen permanent notes in `proof-skills` (`v0.5.0`).
The notes follow a simplified Luhmann 3-tier model (`fleeting -> literature -> permanent`) and anchor the toolkit's template-v2 contracts, evaluation methodology, SAIR kernel WHNF laws, spec-compute duality, proof-carrying hardware codegen, two-tier WASM static analysis, and pure-Lean equality saturation.

## Permanent note catalogue

| ID | Title | Tier-1 tag | Confidence |
|---|---|---|---|
| [[zk-001]] | Fork rationale and project-agnostic override architecture | provenance | high |
| [[zk-002]] | Skill-template v2 frontmatter contract | template-contract | high |
| [[zk-003]] | AgentRx 9-category failure taxonomy | taxonomy | high |
| [[zk-004]] | BACM -- Burst-And-Compact-Memory context pattern | pattern | high |
| [[zk-005]] | TDAD -- Test-Driven Agent Definition (4-role loop) | methodology | high |
| [[zk-006]] | Four orthogonal skill evaluation targets | evals | high |
| [[zk-007]] | Glicko-2 and ELO ranking for stochastic agents | ranking | high |
| [[zk-008]] | Lean 4 unified tactic priority hierarchy | tactics | high |
| [[zk-009]] | Skill consolidation rubric -- merge, split, keep | governance | high |
| [[zk-010]] | Multi-model cost-quality Pareto across model x reasoning-effort | synthesis | high |
| [[zk-011]] | SAIR 39 kernel WHNF laws and nat_lit mechanics | sair | high |
| [[zk-012]] | Abstraction-concrete duality and hot parameterization penalty | duality | high |
| [[zk-013]] | Proof-carrying hardware codegen -- PolyBitOp, CheckedWord, and N01..N12 | codegen | high |
| [[zk-014]] | Two-tier WASM static analyzer and 5-role 21-tool MCP architecture | mcp | high |
| [[zk-015]] | Pure-Lean equality saturation and cross-ITP concordance | eqsat | high |

## Reading paths

- **Toolkit & override architecture** -- [[zk-001]] -> [[zk-002]] -> [[zk-009]] -> [[zk-014]].
- **Evaluation & ranking** -- [[zk-006]] -> [[zk-005]] -> [[zk-003]] -> [[zk-007]] -> [[zk-010]] -> [[zk-004]].
- **Lean 4 proving, equality saturation & cross-ITP porting** -- [[zk-008]] -> [[zk-015]] -> [[zk-014]].
- **Kernel WHNF superoptimization & hardware codegen** -- [[zk-011]] -> [[zk-012]] -> [[zk-013]].

## Invariants enforced by `scripts/lean/zettelkasten_lint.py`

1. Every note has a YAML frontmatter block declaring `id`, `title`, `created`, `updated`, `type`, `tags`, `refs`, `status`, and `confidence`.
2. Every permanent note has `>= 2` outgoing `refs:` to other permanent notes and `>= 1` incoming link.
3. Every permanent note stays concise (`<= 300` words).
4. Every outgoing `refs:` entry is matched by an inline `[[zk-NNN]]` wikilink in the body, and vice versa.
5. Zero private downstream identifiers or repository-external paths appear in any note.
