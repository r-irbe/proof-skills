---
name: "lean-dependency-management"
description: |
  USE FOR: evaluating Reservoir/GitHub Lean packages, toolchain pin bumps, and substrate vendoring.
  DO NOT USE FOR: ordinary lemma search (@lean-research) or broken-proof repair (@lean-proof-repair).
  TRIGGERS: Lean package, Reservoir, Lake dependency, Mathlib bump, vendor substrate, toolchain pin.
tier: warm
runtime_targets:
- copilot-cli
- claude-code
- antigravity
- pi
- cursor
- gemini-cli
dispatch_targets: []
handoffs:
  predecessors:
  - skill:lean-research
  - skill:lean-setup
  successors:
  - skill:lean-build
  - skill:lean-proof-repair
  - skill:lean-verification-gate
metadata:
  version: 0.4.0
  source_spec: Unified from lean-package-research and lean-vendor-substrate
  last_reviewed: 2026-11
---

# Lean 4 Package Evaluation, Pin Upgrades & Substrate Vendoring

Evaluate external Lean 4 packages on Reservoir/GitHub, plan compatible `lean-toolchain` + `lake-manifest.json`
upgrades, and execute license-verified, axiom-audited substrate vendoring when Lake `require` is unsuitable.

## Routing
- **USE FOR:** package discovery (`lean_search(source: "reservoir")`), Lake dependency vs. vendoring trade-offs,
  license/SPDX verification (`Apache-2.0` / `MIT`), and provenance-tracked vendoring.
- **DO NOT USE FOR:** general theorem search (`@lean-research`) or interactive tactic repair after bumping (`@lean-proof-repair`).

## Workflow
1. **Evaluate Candidates** -- Query Reservoir/GitHub for toolchain pin alignment, `sorry`/axiom cleanliness,
  maintenance velocity, and transitive dependency weight.
2. **Choose Integration Mode** -- Prefer pinned Lake `require` when toolchains align; choose isolated `Vendor/`
  subtree vendoring only when extracting a narrow `sorry`-free slice across incompatible pins.
3. **Verify License & Provenance** -- Confirm permissive SPDX license (`Apache-2.0` / `MIT`), preserve upstream
  `LICENSE` + copyright headers, and record exact upstream repo URL + commit SHA.
4. **Compile & Axiom-Lock** -- Build via `@lean-build`, repair API drift via `@lean-proof-repair`, and run
  `@lean-verification-gate` (`lean_axiom_closure`) over every imported/vendored declaration.

## Recovery & STOP
- Reject any upstream package with incompatible copyleft/missing license or custom `axiom` / `unsafe` declarations in the target slice.
- Never hand-edit `lake-manifest.json` hashes; always resolve pins through `lake update <pkg>`.

## Handoffs
- **Predecessors:** `lean-research`, `lean-setup`.
- **Successors:** `lean-build`, `lean-proof-repair`, `lean-verification-gate`.

## Detailed reference
- **Layer-1 Fast Lookup Card (read first)**:
  [`references/cards/lean-dependency-management-tables.md`](../../references/cards/lean-dependency-management-tables.md)
- Full handbook: [`../../references/handbooks/lean-dependency-management-handbook.md`](../../references/handbooks/lean-dependency-management-handbook.md)

## See also
- [`../lean-setup/SKILL.md`](../lean-setup/SKILL.md) -- Toolchain & Lake project setup
- [`../lean-proof-repair/SKILL.md`](../lean-proof-repair/SKILL.md) -- Repairing proofs across toolchain/Mathlib bumps
