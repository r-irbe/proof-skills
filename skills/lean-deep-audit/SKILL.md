---
name: "lean-deep-audit"
description: |
  USE FOR: running a systematic whole-corpus quality audit over a large Lean
  formalization project - trust-base lockdown, literature faithfulness
  (free-record-proxy detection), spec-baking (tautology) scans, inhabitation
  coverage, type-continuity/duplication censuses, sign/domain/ordering
  reviews, and the remediation-queue discipline that closes findings.
  DO NOT USE FOR: reviewing a single theorem's proof (@lean-proof-review);
  the compile-time axiom lockdown itself (@lean-axiom-closure, this
  program's P1 executor); replay/verification cadence
  (@lean-replay-verification); naming/style conventions (@lean-naming or
  the project's own).
  TRIGGERS: deep audit, corpus audit, whole-corpus review, faithfulness
  review, scalar proxy, free-record proxy, veneer, spec baking, tautology
  scan, inhabitation census, duplication census, guest corpus triage,
  placeholder authors, template-generated modules, remediation queue.
tier: "cold"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
---

# The Deep-Audit Program (whole-corpus, seven lenses)

## Why

Per-theorem review scales linearly with attention and decays with
session turnover. A deep audit is a PROGRAM: mechanical censuses first
(deterministic, re-runnable, seconds), human verdicts second (bounded
lists), remediations tracked to closure with evidence. Every finding
is registered even when the disposition is "belong to another lane" -
an unregistered finding gets rediscovered.

## The program (run priorities in this order)

1. **P1 - Trust-base lockdown.** Every declaration's transitive axiom
   closure restricted to the declared allowlist, enforced in the normal
   build. EXECUTOR: the `lean-axiom-closure` skill (vendored metaprogram
   + FinalCheck consumer). Expected first catches: `sorryAx` behind
   wrappers/aliases, `native_decide` (`Lean.ofReduceBool`), custom
   axioms.
2. **P2 - Literature faithfulness, tower by tower.** For each
   foundational module: read every core definition; compare with the
   cited formula; classify faithful-formula / scoped-specialization /
   free-record-proxy. The proxy signature: a structure with free
   fields + arithmetic defs over those fields + projection-style
   theorems, while the module prose narrates mathematics the code
   never touches. Template-residue corroborating evidence: placeholder
   author strings, identical skeleton across a file family, imports
   that do not reach the claimed subject area. Disposition for guest
   material belongs to the owning lane under whatever guest-corpus
   contract exists - register, do not auto-delete.
3. **P3 - Spec-baking scan.** `tautology_scan.py` (references/scripts/):
   theorems whose entire proof body is a trivial form (`rfl`, bare
   `simp`, `decide`, `assumption`) or a bare hypothesis/projection
   (`h.1`). Candidates, not verdicts: triage each as definitional-ok /
   rewrite-the-statement / own-lane. Keep the human verdict layer
   separate from the generated report (regeneration must not lose it).
4. **P4 - Inhabitation census.** `deep_audit_census.py` (P4 half):
   every structure/class/inductive - instance/deriving-witnessed,
   term-witnessed, or unexplained. The unexplained list is a REVIEW
   LIST, not a defect count: classify parameterized instances the
   scanner cannot see, proof-only types where inhabitation is
   meaningless, genuinely uninhabited-but-meaningful (add witnesses),
   and vacuous types with unsatisfiable fields (the real catch).
5. **P5 - Type continuity.** `deep_audit_census.py` (P5 half): type
   basenames declared in more than one module (duplication candidates:
   same-concept-redeclared -> consolidate; same-name-different-concept
   -> rename), plus the shared-foundation ranking (true foundations
   are the basenames referenced by the most modules).
6. **P6 - Sign/domain/index pilot.** Review ONE order-trap tower with
   the checklist: ordering hypotheses structural (fields, not
   preconditions); boundary ties explicit + theorem-backed; severity/
   order maps total + injective + extremes proven; sign exposure
   Nat-pipeline preferred, every Real op domain-proven; concrete cases
   by `decide`; cross-hierarchy bridges operational-equivalence-proven
   OR no-go-documented; scale mismatches guarded in docstrings. Then
   generalize the checklist to the remaining towers.
7. **P7 - Statement-shape review.** Per-declaration verdicts (keep /
   subsumed-by-mathlib / packaging-honest-statement) over the generic
   towers, with every mathlib adjacency consumed rather than
   duplicated. Zero-coverage claims require a grep over the pinned
   mathlib tree, never recollection.
8. **P8 - Remediation queue.** Every finding lands with: what, where,
   severity, disposition owner. Close findings same-session when the
   fix is one theorem or one docstring; route the rest with precise
   pointers.

## Cross-cutting disciplines (G-*)

- **G-1** (MUST): evidence before verdicts - a missing bridge, a gap,
  or a zero-coverage claim is stated only after a grep / `lake env lean`
  `#check` proves it. One pilot's wrong conjecture corrected on evidence
  is a success, not a failure; an uncorrected one is not.
- **G-2** (MUST): censuses are deterministic scripts (commit them),
  reports are generated artifacts, verdicts are human layers - keep the
  layers separable so regeneration never loses analysis.
- **G-3** (MUST): every remediation carries its owner; a finding
  without an owner is a wish.
- **G-4** (SHOULD): re-run censuses after landing fixes - reports drift
  as the corpus moves under them.

## Pitfalls

- The naive reference-count loop (per-line x per-basename) is
  O(lines x types) and times out on real corpora; the two-pass
  precompiled-alternation form runs in seconds (the shipped script does
  this).
- Instance regexes see simple-identifier forms only
  (`instance : Inhabited T`); parameterized instances
  (`Inhabited (T x)`) land in the unexplained list by construction -
  that is what the review pass is for.
- Scanner line numbers drift with any upstream edit; re-run before
  quoting them.
- Guest/template families inflate proxy findings; their disposition is
  governance (owner decision), not the auditor's.

## Verification

- Each census: re-runs byte-identical on an unchanged corpus; counts
  quoted with the run command.
- P1: the build fails on a deliberately introduced `sorry` (verify the
  failure path once during setup).
- The program itself: the remediation queue only ever shrinks by
  closure commits or owner-routing records - never by silence.
