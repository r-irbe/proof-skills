---
name: "lean-vendor-substrate"
description: |
  USE FOR: executing a decided vendoring of a permissively-licensed Lean 4
  formalization into a project tree — verifying license and provenance, pinning
  the upstream commit, rewriting imports and namespaces, handling module-local
  options/instances during a toolchain-version migration, registering the
  vendored subtree in the build, and running the correctness gates over the
  result. Use this once a package-research decision (ADOPT-NOW for vendoring)
  has been made and the operator is authorized to mutate project files.
  DO NOT USE FOR: deciding whether to adopt or vendor a package (use
  @lean-package-research); running the verification suite as the gate owner
  (use @lean-enforcement under an edit claim); searching for a theorem without
  a vendoring decision (use @lean-research); license litigation (STOP and ask a
  human).
  TRIGGERS: vendor, vendoring, vendored code, upstream formalization, import
  rewrite, namespace rename, commit pin, upstream pin, license vendoring,
  Apache-2.0 vendor, MIT vendor, re-vendor, vendor upgrade, port upstream file,
  pin adaptation, sorry-free upstream.
tier: "warm"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-package-research", "skill:lean-research", "agent:gateway"]
  successors: ["skill:lean-enforcement", "skill:lean-quality-engine", "skill:lean-proof-review"]
metadata:
  version: "0.1.0"
  source_spec: "skills/lean-vendor-substrate/SKILL.md (this file)"
---

# lean-vendor-substrate

Vendoring is the sanctioned alternative to re-derivation when a needed theorem
exists as `sorry`-free, permissively-licensed Lean 4 source that does not (yet)
live in a pinned dependency. Re-deriving from scratch when the source is
Apache-2.0 or MIT is strictly worse: it discards CI-verified correctness and
invites transcription errors. This skill executes the vendoring; the adoption
decision belongs to `@lean-package-research`.

## Workflow

1. **Verify provenance before copying anything** [discover] — record the
   upstream repository, the exact commit hash, the date, and the license. Fetch
   the license text into the project (e.g. a `LICENSES/<name>-<license>.txt`
   file) unless the upstream ships one at the vendored path. A vendoring
   without a pinned commit is not reviewable; refuse to proceed without one.
2. **Check the license and the sorry-status claim** [validate] — confirm the
   license is permissive and compatible with the project license. If upstream
   claims CI-verified `sorry`-freedom, verify it locally after the port rather
   than trusting the claim; if the claim cannot be re-verified, downgrade to
   RESEARCH-MORE in `@lean-package-research` terms.
3. **Minimize the adaptation surface** [execute] — port the upstream files with
   these mechanical changes and nothing else:
   - rewrite import paths to the project pin;
   - rename the namespace to the project convention, preserving authorship
     headers verbatim (copyright, license, authors lines stay in-file);
   - record the upstream commit in each file header;
   - mark every substantive deviation from upstream with an in-file marker
     comment that names the migration (source toolchain → target toolchain) and
     the reason. Typical deviations: a module-local decidability instance the
     upstream got from `open Classical` scoped instances; an upstream lemma
     chain that does not elaborate at the target pin, replaced by carrying the
     missing step as an explicit hypothesis; hypotheses that become dead after
     an adaptation, dropped with a marker.
   - handle module-level options per file: if upstream relied on a lakefile
     default such as `autoImplicit true`, keep that per vendored module and
     document it in-file; never silently switch vendored modules to project
     conventions.
4. **Register the subtree** [execute] — add the vendored modules to the build
   (library globs or umbrella imports), wire them so the default build target
   and CI compile them transitively, and add any vendored license text to the
   project's license directory.
5. **Run the full gate suite with the vendored-duality rule** [persist] —
   correctness gates (build with zero errors and zero `sorry` warnings,
   import/DAG discipline, axiom audit over every declaration) run over the
   vendored subtree exactly as over project code. Style and proof-quality
   gates are EXEMPT for vendored directories, configured via an explicit
   exclusion flag in the style tool, because vendored code is upstream-faithful
   and its quality findings belong upstream. The exemption must be a gate
   configuration change, never an unreviewed wholesale skip.
6. **Record the provenance row and the upgrade path** [persist] — one row per
   vendored file or subtree: local path, upstream repo, license, vendoring
   date, pinned commit, what was changed and why, and the upgrade path
   (re-vendor from the upstream pin and re-run the gate suite). Downstream
   readers must be able to diff the vendored subtree against upstream.

## Recovery & STOP

- STOP if the license is missing, unclear, copyleft-incompatible, or the
  upstream repo cannot be authenticated; return to `@lean-package-research`
  with the evidence.
- STOP if the port requires changes beyond import/namespace/option handling to
  make it compile (elaboration drift deeper than mechanical rewrites); surface
  the drift as a decision — either document a minimal, marker-commented
  adaptation or park the vendoring and record the blocker.
- STOP if the local sorry/axiom audit finds findings inside the vendored
  subtree after the port; a vendored subtree must be at least as clean as the
  project's correctness bar.
- RECOVERY if the build breaks only on Mathlib API drift: fix by adapting
  call sites inside the vendored file with a marker comment per change, never
  by restructuring upstream definitions.

## Handoffs

- **Predecessors:** `@lean-package-research` for the adoption decision and
  package card, `@lean-research` for the source-discovery ladder (confirm
  absence at the pin, find permissive-license candidates), `agent:gateway` for
  vendoring-focused user requests.
- **Successors:** `@lean-enforcement` to run and own the gate results,
  `@lean-quality-engine` for milestone/package-health scoring,
  `@lean-proof-review` to review any corpus-authored wrapper modules built on
  top of the vendored substrate.
