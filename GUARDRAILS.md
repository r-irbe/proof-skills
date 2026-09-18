# GUARDRAILS — agent failure taxonomy

Central registry of measured agent failure classes for the Lean skills
bundle. Individual `SKILL.md` files cite this file from their *Common
failure modes* section as the full registry; the blockquote in each skill is
the short in-context list, and this file is the complete, deduplicated set.

Rules of maintenance:

- Every entry is bound to a **measured** failure — something an agent
  actually did and that cost a debugging or review cycle — not a stylistic
  preference. New entries arrive through a skill's *Common failure modes*
  blockquote first, then get an ID here.
- Entry IDs (`GT-xx`) are stable: never renumber, only add. Retired entries
  are marked *retired* with a reason, not deleted.
- The owning skill is the authority for the failure's remedy; the registry
  condenses, it does not override.

## Agent failure taxonomy

### Delegation & routing — [`lean-gateway`](skills/lean-gateway/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-01 | Does the delegated work themselves "to save a delegation" | Delegate; the gateway routes, domain skills execute |
| GT-02 | Picks a broad skill when a specific one exists | Match the most specific dispatch target |
| GT-03 | Retries a failed delegation instead of escalating | Escalate or hand off after failure, do not loop |
| GT-04 | Ignores context-collapse signals | Surface degradation; recommend a fresh session |
| GT-05 | Skips the per-task tracker update | Update the tracker as part of the handoff |

### Proof writing — [`lean-proof`](skills/lean-proof/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-06 | Writes 3–5 tactics before reading diagnostics | One tactic at a time, gated on `done`/diagnostics |
| GT-07 | Chases a linter warning while an unsolved-goals error is open | Error-priority order (G-3, G-4): errors before warnings |
| GT-08 | Fills helper-lemma `sorry`s before touching the target theorem | Target theorem first; helpers only as reached |
| GT-09 | Declares success while a `sorry` remains | Verify pass: no `sorry`, no error, diagnostics re-read |
| GT-10 | Fights `motive is not type correct` with more `rw` instead of generalising | Generalise-then-instantiate (G-9) |
| GT-11 | Retries `rw` with "pattern not found" on goals whose summand contains a non-reducible type synonym or a semireducible definition — the matcher runs below default transparency and cannot unfold these | `simp only` with the exact lemma list, then `exact` the residual identity; supply bare commutation lemmas as terms (they loop as simp lemmas); probe goal shapes with live LSP `plainGoal` queries, never file-polluting `trace_state` or `sorry` placeholders |

### Proof review — [`lean-proof-review`](skills/lean-proof-review/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-12 | Rewrites the proof inline instead of suggesting changes | Review produces findings, not silent rewrites |
| GT-13 | Approves at L4 without confirming L1/L2 passed | Checklist order is mandatory: L1 → L2 → L3 → L4 |
| GT-14 | Misses vacuous-truth L3 failures behind a clean `aesop` close | Inspect what `aesop` actually closed, not just that it closed |
| GT-15 | Cites a pitfall without quoting line numbers or the source rule | Every finding carries location + rule reference |
| GT-16 | Accepts an "independent routes" claim without checking it — when a project claims two or more independent proofs of one theorem, the routes may share machinery (imports, helper lemmas, substrate definitions) | Before repeating an independence claim in a verdict, verify the routes share no machinery; a shared-lemma discovery downgrades the claim to "partly independent" in the review record |

### Enforcement & gates — [`lean-enforcement`](skills/lean-enforcement/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-17 | Silently retries a blocking failure | A hard-gate failure halts; escalate, do not retry |
| GT-18 | Downgrades a hard gate to a soft one to "unblock progress" | Gate severity is frozen during a campaign |
| GT-19 | Runs `enforce_all.sh` when a single script would have answered the question | Run the narrowest gate that answers the question |
| GT-20 | Skips the structured-result emit step | Emit the structured result; skipping = incomplete |
| GT-21 | Trusts a green gate whose generated probe/scan manifest is stale — newly registered modules or targets are silently unscanned, and a summary can be clean while whole namespaces went unscanned | After registering new targets, regenerate generated probe scripts and rerun before quoting the result; treat per-item coverage gaps inside the gate's own report as findings, not noise; close unexplained gaps with a targeted spot-check (e.g. a single-declaration `#print axioms` probe) before declaring the gate clean |

### Quality scoring — [`lean-quality-engine`](skills/lean-quality-engine/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-22 | Scores soft gates before hard gates pass | Hard gates first; soft scores are conditional on them |
| GT-23 | Persists a `Q_score` that includes a failed hard gate | A failed hard gate invalidates the score |
| GT-24 | Re-implements an enforcement check inline instead of calling `@lean-enforcement` | Call the enforcement skill; do not fork checks |
| GT-25 | Skips the regression delta against the prior milestone | Every score carries a delta against the previous one |

### Blueprint & planning — [`lean-blueprint`](skills/lean-blueprint/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-26 | Skips the Persist step | Persist is mandatory (FSIA-R-11-09) |
| GT-27 | Over-annotates stable modules | Annotation budget goes to unstable surfaces |
| GT-28 | Re-runs `lake build` instead of escalating on third failure | Same-error ×3 → STOP and escalate |

### Competitive math — [`lean-competitive-math`](skills/lean-competitive-math/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-29 | States an existential or a bound instead of the exact numeric answer | Answer form must match the requested form exactly |
| GT-30 | Declares done on a green `native_decide` without ever running `#print axioms` | Axiom-probe every `native_decide` result |
| GT-31 | Leaves a Bronze `native_decide` answer-check permanent with no structural follow-up filed | Bronze results require a filed structural follow-up |
| GT-32 | Reaches for kernel `decide` at a scale that blows `maxRecDepth`, then gives up | Scale-check before `decide`; fall back to structural proof |
| GT-33 | Papers a gap with `sorry` | `sorry` is a hard gate failure, never a submission state |

### Knowledge graph — [`lean-zettelkasten`](skills/lean-zettelkasten/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-34 | Over-polishes fleeting notes (defeats the speed of capture) | Fleeting = fast; polish happens at promotion |
| GT-35 | Promotes 1–2-note clusters to permanent notes | Promotion needs a genuine cluster |
| GT-36 | Creates permanent notes without back-linking the sources or marking them `superseded` | Back-links and supersession marks are part of the note |
| GT-37 | Silently resolves a contradiction instead of flagging it for SDR | Contradictions are flagged, never silently resolved |
| GT-38 | Skips `_index.md` and `_tags.md` updates so the graph view rots | Index updates are part of the write path |

### Epistemic mapping — [`epistemic-mapping`](skills/epistemic-mapping/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-39 | Picks the first framing encountered | Enumerate competing framings before choosing |
| GT-40 | Merges contested terms | Keep contested terms separate until resolved |
| GT-41 | Omits citations for "obvious" nodes | Every node carries its citation |

### Documentation feedback — [`lean-doc-feedback`](skills/lean-doc-feedback/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-42 | Rewrites instead of annotating | Feedback annotates; it does not rewrite |
| GT-43 | Omits rubric anchors | Findings anchor to rubric items |
| GT-44 | Bundles many findings into one comment | One finding per comment |

### Environment setup — [`lean-setup`](skills/lean-setup/SKILL.md)

| ID | Failure class | Remedy |
| --- | --- | --- |
| GT-45 | Re-runs `cmake --preset release` on every build | Reuse the configured build; rebuild only on config change |
| GT-46 | Links only stage1 and forgets stage0 | Both stages link |
| GT-47 | Pins only `lean-toolchain` and forgets the three sibling files | Pin all four sibling files together |
| GT-48 | Declares success on a green `lean --version` without checking `lake env lean --version` | Both version probes must agree before handoff |
| GT-49 | Hands off to `@lean-proof` while the two `--version` commands disagree | Resolve the toolchain mismatch before handoff |
| GT-50 | Treats destructive-command approvals as reusable prose, or HITL rulings as free text | Destructive commands require single-use sha256+TTL approval ledger records; HITL gates are JSON-schema-typed packets (approve/reject/defer) — see the filab investigation plan (PLAN-FILAB-DEEP-INV) for the full design |
| GT-51 | Ships a gate that lacks one of the four quality properties, or claims enforcement without a binding control | Every gate must be machine-verifiable, bounded (numeric threshold), committed (evidence recorded), and rollback-safe — else advisory; mark each rule `runtime-enforceable: Y\|N` with a named binding control; advisory→blocking promotion requires a 30-day clean baseline (filab third-look, N1) |
| GT-52 | Treats a mandatory-read bypass as an invisible exception, or records rationale only in prose | Bypasses are first-class auditable events: canonical syntax, JSONL audit row written before the call returns, per-row PR review, repeat-offender escalation; encode why-provenance in `Lore-*`-style commit trailers for machine queryability (filab third-look, N6) |
| GT-53 | Conflates capability tiers into one enum, or gates irreversible actions with re-runnable checks | Capability tiers are distinct newtypes per surface over a base ladder; irreversible actions fail closed with signed risk-acceptance; environment scrubbing re-opens threat surfaces — prefer per-subject opt-in with dual-digest audit rows (filab third-look, N8; extends GT-50) |
| GT-54 | Reads a passing check as closure, or treats a frozen measured NO-GO as liftable by offline work | Passing checks are telemetry, never closure; a frozen measured NO-GO is TERMINAL and lifts only through named human acts (SEAL + powered IRB study + sealed rerun) — q AGENTS.md MASTER BLOCKER pattern (q investigation, C1) |
| GT-55 | Grants a governance tool authority by default, or lets it judge its own output | Governance-tool lifecycle: staged authority promotion (warn-first → blocking ratchet after 3 clean rounds, human `--strict` opt-in); honesty-wall "WHAT THIS IS NOT" headers; approval-language denylist with negation exceptions; falsifier non-vacuity proofs (rejects adversarial auto-approve AND accepts well-formed input); worker contracts stdlib-only, no I/O/randomness/network (q investigation, C2) |
| GT-56 | Lets one artifact affirm what another denies, or leaves human escalation unnamed | Layered denial: no single artifact may affirm what another denies; human acts are named and scarce (SEAL, HITL ratification, paste-into-ledger); analysis/execution separated by repo layout; provenance to the byte (filenames carry UTC/host/SHA/dirty) (q investigation, C9) |
| GT-57 | Installs a hard barrier without naming its mandate, or lets eager sealing/clamping stop all progress | Barrier proportionality: hard stops (terminal NO-GO, frozen clamp, no-bypass block) are reserved for the subset mandated by regulation, procedure, or law — every hard barrier must cite its mandate in a barrier registry, and an unjustified hard barrier is itself a defect. Everywhere else the design is fail-open with compensating controls: provisional continuation in a quarantined scope (no protected-path writes, reversible, enhanced audit trail), reduced blast radius, additional review. Blocked ≠ stopped (operator directive 2026-09-15; scopes GT-54/55/56) |
| GT-58 | Leaves human-approved work stalled behind a gate, or uses promotion timeouts by default | Continuity under approval: once a human approves via the HITL gate, a stalled pipeline is a defect — approved-but-blocked items carry escalation SLAs with named owners and auto-escalate on expiry. Promotion timeouts are the exception, not the mechanism: use them sparingly, only where a rule class explicitly defines them (e.g. GT-55's ratchet), never as a generic barrier. Where continuation is safe, proceed provisionally with the compensating controls of GT-57 and reconcile at the gate (operator directive 2026-09-15) |
| GT-59 | Lets capability expansion ride on prose rules, scalar trust scores, or untraceable overrides | Capability-governance baseline: append-only ADR ledger at a fixed root with irreversible gate progressions; `CAPABILITY_EXPANSION = always_hitl` behind a static reversible-op whitelist; bash-only-first action surface — a specialized tool must justify a ≥5% task-success uplift; a ~100-line minimal-agent reference keeps the floor honest; operator overrides mint verifiable receipts (Blake3) that become audit rows; trust stays a composite vector with per-dimension vetoes, never a scalar (filab fourth look, N-1/N-2) |

| GT-60 | Lets a gate pass by exiting 0 on its error path, or syncs gate outcomes nowhere | Enforcement parity: a gate is a gate only when its failure path denies — gate errors and config failures must DENY (fail-closed BLOCK exit code), violation events must land in an event log with a gate→HITL sync queue, and the stub confession ("not yet fully implemented") is a defect class of its own; parity CI replays gate invocations against fixtures so an exit-0 stub cannot masquerade as enforcement (filab seventh look, X-6; the legacy G5 vs nomikon gate_hook.rs arc) |

| GT-61 | Treats a status string as a validation event, or audits one trust regime and assumes the other | Two-regime validation: EXECUTED validation lives only in gate/council ledgers (verbatim decision_source with timestamp + named approver, last_validated dates, canonical-flip flags, staged pending_actions, implementation_state); status strings (validation_status: pending/validated) are PLEDGES with zero executions unless bound to a ledger row — audit both regimes independently, never infer one from the other (q fifth look, Y-3: 0/24 learning notes executed vs gate ledgers running) |
| GT-62 | Lets a pipeline stage run out-of-order, or authors from unaccepted inputs | Pipeline-as-permissions: each stage's tool REFUSES to run before its gate — an ADR moves proposed -> accepted only behind a recorded human decision_signoff; specs are authored only from ACCEPTED ADRs; tasks enforce the AC <-> design-component <-> TASK isomorphism with [Fit:] thresholds; eval dispatch fails closed on unbound cases (algos authoring pipeline, K-2/K-3) |
| GT-63 | Trusts a single-threshold gate to carry both publication and acceptance, or treats a council score as authority | Calibrated two-band council gates: Gate A (publish, lower threshold) and Gate B (council, higher threshold) are distinct decisions — the verdict is a SIGNAL, a named human decision_signoff decides, minority-veto Devil's-Advocate aggregation is recorded in an immutable COUNCIL-VERDICT, and a good-faith revision may LOWER a score (never inflate it) (algos fourth look, L-3: the keystone rule that let parallel Opus-4.8 waves run trustworthily) |

## Source-of-truth note

The per-skill blockquotes remain the operative in-context reminders; this
registry is the consolidated view. When a blockquote and this registry
disagree, fix both in the same commit — the blockquote is the dispatch-time
surface, the registry is the audit surface.
