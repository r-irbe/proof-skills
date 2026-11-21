---
name: lean-dependency-management-handbook
description: Unified reference handbook for @lean-dependency-management (Reservoir/GitHub
  package evaluation, toolchain pins, and substrate vendoring).
extracted_from: skills/lean-dependency-management/SKILL.md
---

## Quick-Lookup Indexing Tables (`mathcomp-skills` Three-Entry-Point Pattern)

### Table 1: Goal-Shape-First (`templates` Entry Point)

| Goal / Term Shape | Primary Tactic / Pattern | Canonical Recipe / Notes |
| :--- | :--- | :--- |
| External package candidate on Reservoir | `lean_search(source: "reservoir")` | Check `lean-toolchain` match, license, and `0 sorry` status |
| Small external theorem slice on incompatible pin | Isolated `Vendor/<Pkg>/` vendoring | Preserve SPDX header, upstream URL + SHA, and run `lean_axiom_closure` |
| Double-blind supplement containing adapted external proofs | `altproof tree-shake --anonymize` + root `LICENSE` | Preserve third-party `Apache-2.0`/`MIT` copyright notices and `Adapted from` blocks |

### Table 2: Intent-First (`phrasebook` Entry Point)

| User / Engineer Intent | Recommended Tool / Idiom | Actionable Recipe |
| :--- | :--- | :--- |
| Bump `lean-toolchain` and Mathlib pin safely | `lake update` + `@lean-proof-repair` | Never hand-edit `lake-manifest.json` SHA hashes |
| Verify vendored code introduces no extra axioms | `@lean-verification-gate` | Audit transitive axioms of all vendored declarations |
| Prune unused git dependencies in standalone slice | `altproof tree-shake` (`usedExternalRoots`) | Automatically strips unimported direct git `require`s (e.g. `LSpec`) from `lakefile` & manifest |

### Table 3: Error / Bottleneck-First (`errors` Entry Point)

| Symptom / Error / Bottleneck | Root Cause | Remediating Fix |
| :--- | :--- | :--- |
| `lake update` version solver conflict | Transitive packages pin incompatible `lean-toolchain` | Align `lean-toolchain` to target Mathlib release tag first |
| Missing SPDX license on candidate repo | Unlicensed upstream code cannot be vendored | Halt vendoring and re-prove from mathematical literature |
| Anonymizer stripped third-party `MIT`/`Apache-2.0` copyright | Over-aggressive header replacement | Whitelist upstream open-source attributions and emit composite root `LICENSE` |

---

<!-- Merged from lean-package-research-handbook.md -->

# lean-package-research

Package research is separate from theorem lookup because dependency decisions
change reproducibility, build time, trust surface, and future maintenance. This
skill turns a candidate package or pin change into an adoption recommendation
with evidence, sequencing, and validation.

## Routing

- **USE FOR:** Lean 4 package and toolchain research -- evaluating
  Reservoir/GitHub packages, Mathlib/cslib pin changes, Lake dependency health,
  package adoption classes, update sequencing, and external theorem-substrate
  candidates.
- **DO NOT USE FOR:** ordinary theorem lookup without a package decision (use
  `@lean-research`); package-file mutation or `lake update` execution (delegate
  validation to `@lean-enforcement` under an edit claim); proof writing (use
  `@lean-proof`); general project QA (use `@lean-quality-engine`).
- **TRIGGERS:** Lean package, Reservoir, GitHub Lean repo, Lake dependency,
  lake-manifest, lean-toolchain, mathlib update, cslib update, package adoption,
  package pin, dependency health, external theorem substrate.

## Workflow

1. **Scope the package question** [discover] -- identify whether the caller wants
   theorem borrowing, dependency adoption, pin update, fork/vendor choice, or
   negative-result evidence. If the request only needs symbol lookup, hand off to
   `@lean-research`.
2. **Run the discovery ladder** [discover] -- use
   [`../../references/discovery-ladder.md`](../protocols/discovery-ladder.md)
   for Reservoir, GitHub, current-pin package source, theorem-search services,
   and literature checks. Record negative results rather than relying on memory.
3. **Assess dependency health** [validate] -- inspect Lake metadata, toolchain
   compatibility, maintenance status, archive/staleness, license visibility,
   transitive dependencies, binary fetches, and whether the package is already
   represented by Mathlib/cslib.
4. **Classify adoption** [validate] -- use ADOPT-NOW, ADOPT-LATER,
   RESEARCH-MORE, DO-NOT-ADOPT-NOW, or DO-NOT-ADOPT. Package adoption and theorem
   borrowing may receive different classes.
5. **Plan sequencing** [execute] -- list exact files that would change, commands
   that must run, rollback/preflight steps, and which validation owner should run
   them. Do not mutate package files from this skill.
6. **Persist handoff** [persist] -- return a compact package card with evidence,
   confidence, adoption class, validation commands, blockers, and HITL questions.

## Package card format

```markdown
## Package research card: <package or pin>

- Question:
- Candidate:
- Current project pins/toolchain:
- Sources checked:
- Theorem/substrate value:
- Dependency health:
- Adoption class:
- Confidence:
- Required validation:
- Write targets if later authorized:
- Rollback:
- HITL needed:
```

## Recovery & STOP

- STOP if the package would require editing `lean-toolchain`, `lakefile.lean`, or
  `lake-manifest.json` without an explicit edit claim and human authorization.
- STOP if the adoption class is ADOPT-NOW but confidence is below the local
  belief floor, validation is unknown, or the dependency graph is dirty.
- STOP if a package is archived, stale, or has unclear transitive dependencies
  and the caller asks for immediate adoption; return RESEARCH-MORE or
  DO-NOT-ADOPT-NOW with evidence.
- STOP if a theorem-search hit cannot be re-verified at source; downgrade symbol
  borrow confidence and hand off to `@lean-research`.

## Handoffs

- **Predecessors:** `@lean-research` for symbol/literature leads,
  `@lean-integration-protocol` for project integration boundaries,
  `agent:gateway` for package-focused user requests.
- **Successors:** `@lean-research` for deeper theorem lookup,
  `@lean-enforcement` for validation commands, `@lean-quality-engine` for
  milestone/package-health scoring.
- **References:** discovery ladder
  ([`../../references/discovery-ladder.md`](../protocols/discovery-ladder.md))
  and eval prompts
  ([`../../references/discovery-ladder-evals.md`](../protocols/discovery-ladder-evals.md)).


---

<!-- Merged from lean-vendor-substrate-handbook.md -->

# lean-vendor-substrate

Vendoring is the sanctioned alternative to re-derivation when a needed theorem
exists as `sorry`-free, permissively-licensed Lean 4 source that does not (yet)
live in a pinned dependency. Re-deriving from scratch when the source is
Apache-2.0 or MIT is strictly worse: it discards CI-verified correctness and
invites transcription errors. This skill executes the vendoring; the adoption
decision belongs to `@lean-package-research`.

## Workflow

1. **Verify provenance before copying anything** [discover] -- record the
   upstream repository, the exact commit hash, the date, and the license. Fetch
   the license text into the project (e.g. a `LICENSES/<name>-<license>.txt`
   file) unless the upstream ships one at the vendored path. A vendoring
   without a pinned commit is not reviewable; refuse to proceed without one.
2. **Check the license and the sorry-status claim** [validate] -- confirm the
   license is permissive and compatible with the project license. If upstream
   claims CI-verified `sorry`-freedom, verify it locally after the port rather
   than trusting the claim; if the claim cannot be re-verified, downgrade to
   RESEARCH-MORE in `@lean-package-research` terms.
3. **Minimize the adaptation surface** [execute] -- port the upstream files with
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
   - when the target pin is NEWER than the one upstream compiled at, expect
     elaboration-transparency drift before API drift -- run the pin-drift
     playbook (below) on the first build's error list.
4. **Register the subtree** [execute] -- add the vendored modules to the build
   (library globs or umbrella imports), wire them so the default build target
   and CI compile them transitively, and add any vendored license text to the
   project's license directory.
5. **Run the full gate suite with the vendored-duality rule** [persist] --
   correctness gates (build with zero errors and zero `sorry` warnings,
   import/DAG discipline, axiom audit over every declaration) run over the
   vendored subtree exactly as over project code. Style and proof-quality
   gates are EXEMPT for vendored directories, configured via an explicit
   exclusion flag in the style tool, because vendored code is upstream-faithful
   and its quality findings belong upstream. The exemption must be a gate
   configuration change, never an unreviewed wholesale skip.
6. **Record the provenance row and the upgrade path** [persist] -- one row per
   vendored file or subtree: local path, upstream repo, license, vendoring
   date, pinned commit, what was changed and why, and the upgrade path
   (re-vendor from the upstream pin and re-run the gate suite). Downstream
   readers must be able to diff the vendored subtree against upstream.

## Pin-drift playbook (toolchain migration)

The recurring failure class when re-vendoring across a toolchain bump is not
Mathlib API drift but *elaboration-transparency drift*: the rewrite matcher
and instance resolution change what they unfold. Symptom → root cause → fix,
in the order a real port typically hits them:

- **`rw`/`simp` report "function expected" or a type mismatch on goals that
  *apply* an upstream type abbreviation (`T := ...`).** Root cause: the
  matcher runs at `.implicit` transparency, where a semireducible def does
  not unfold (hierarchy `none < reducible < instances < implicit < default <
  all`; lean4 #13368/#13637). Fix: mark the abbreviation `@[reducible]` with
  an in-file marker; reducible unfolding is the safe direction.
- **After that, `ext` (or `funext`) introduces two binders where the proof
  expected one.** Root cause: the equality's type now unfolds to a Pi, so the
  extension tactic keeps extending. Fix: use `funext` for exactly the levels
  the proof supplies, or adapt the proof term to the doubly-extended goal.
- **`failed to synthesize DecidablePred p` for a comprehension over a
  semireducible predicate, despite `open Classical` or a local
  `propDecidable`.** Root cause: *using* `propDecidable` requires
  sort-checking the predicate application at `.instances` transparency, where
  the semireducible def does not unfold. Fix: declare the instance directly,
  `letI : DecidablePred p := fun a => Classical.propDecidable (p a)` -- it
  must be `letI` (zeta-reducible) with the exact lambda body; an opaque
  `haveI` fvar fails the synthesized-vs-inferred defeq check against the
  goal's inline instance term.
- **"no goals to be solved" on a standalone `rfl` after an `rw` that upstream
  needed.** Root cause: newer pins auto-close `rw` goals by `rfl`. Fix: delete
  the trailing `rfl`; pure pin drift, no content change.
- **Deprecated-lemma warnings on the first build** (e.g. `Set.mem_setOf_eq`
  → `Set.mem_ofPred_eq`). Root cause: pin-bump deprecation renames. Fix:
  sweep the whole vendored tree for the renamed names before the first build
  cycle.
- **`unexpected token` / parse failure on `∑` or `∏` in code that compiled
  at an older pin, or boilerplate `open scoped BigOperators` that now gates
  nothing.** Root cause: Mathlib split the big-operator notation out of the
  scoped `BigOperators` scope into root scope (and deleted the
  `Mathlib.Algebra.BigOperators.Basic` umbrella import); the scope now gates
  only the `𝔼` expectation notation. Fix: delete the vestigial open when only
  sum/prod are used (keep it only for `Finset.expect`); import
  `Mathlib.Algebra.BigOperators.Group.Finset.Basic` for the lemma set.
  Notation-scope drift is elaboration-visibility drift: the syntax is live as
  soon as any transitively imported module provides it.

Two meta-rules that each cost a debugging cycle in a real port:

- **Fix errors in declaration order and rebuild per module.** A failed tactic
  poisons the goal state for the rest of its declaration; downstream failures --
  even ones with an apparent independent cause -- can vanish when the earlier
  error is fixed. Do not batch-fix from the bottom of the error list.
- **Probe goals with live `lean_goal` MCP queries, never with file-polluting `trace_state` or `sorry` placeholders (`GT-11`)**, when a
  rewrite fails and the goal shape is unknown; live LSP output is definitive
  and leaves nothing to revert.

For axiom evidence after the port: a generated corpus-wide probe script can
have coverage gaps (declarations inside `namespace` blocks are routinely
missed). Regenerate the probe script after registering new modules, and treat
targeted `#print axioms <name>` runs in a scratch file as the authoritative
per-theorem evidence when a full-audit report shows unexplained gaps.

## Recovery & STOP

- STOP if the license is missing, unclear, copyleft-incompatible, or the
  upstream repo cannot be authenticated; return to `@lean-package-research`
  with the evidence.
- STOP if the port requires changes beyond import/namespace/option handling to
  make it compile (elaboration drift deeper than mechanical rewrites); surface
  the drift as a decision -- either document a minimal, marker-commented
  adaptation or park the vendoring and record the blocker.
- STOP if the local sorry/axiom audit finds findings inside the vendored
  subtree after the port; a vendored subtree must be at least as clean as the
  project's correctness bar.
- RECOVERY if the build breaks only on Mathlib API drift or
  elaboration-transparency drift (pin-drift playbook): fix by adapting call
  sites inside the vendored file with a marker comment per change, never by
  restructuring upstream definitions.

## Handoffs

- **Predecessors:** `@lean-package-research` for the adoption decision and
  package card, `@lean-research` for the source-discovery ladder (confirm
  absence at the pin, find permissive-license candidates), `agent:gateway` for
  vendoring-focused user requests.
- **Successors:** `@lean-enforcement` to run and own the gate results,
  `@lean-quality-engine` for milestone/package-health scoring,
  `@lean-proof-review` to review any corpus-authored wrapper modules built on
  top of the vendored substrate.

