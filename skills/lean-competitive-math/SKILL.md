---
name: "lean-competitive-math"
description: |
  USE FOR: formalizing a Project-Euler / competition-math problem as a Lean 4 theorem that asserts a concrete numeric answer, proving it, verifying the answer actually computes (native_decide / #eval), then improving the proof from a compiler-trusted answer-check toward a kernel-checked or structural (closed-form) proof. Owns the answer-check-to-structural ladder (Bronze native_decide -> Silver decide / norm_num -> Gold characterising property / closed form) and its L3 non-triviality carve-out for legitimate native_decide answer-checks. Alias: euler-prover.
  DO NOT USE FOR: writing the theorem statement in isolation (use @lean-specification); one-tactic-at-a-time proof authoring or error triage (use @lean-proof); generic single-proof audit outside the carve-out (use @lean-proof-review); Mathlib API / lemma discovery (use @lean-research); project-wide quality scoring (use @lean-quality-engine); open problems with no known numeric answer (this skill requires a known target).
  TRIGGERS: Project Euler, competition math, euler-prover, numeric answer theorem, answer = N, native_decide answer-check, computed constant, closed-form proof.
tier: "hot"
runtime_targets: [copilot-cli, claude-code]
dispatch_targets: []
handoffs:
  predecessors: ["skill:lean-gateway", "skill:lean-specification", "skill:lean-research"]
  successors: ["skill:lean-proof", "skill:lean-proof-review", "skill:lean-quality-engine"]
metadata:
  version: "0.1.0"
  source_spec: "skills/lean-competitive-math/SKILL.md (this file)"
  last_reviewed: "2026-07-05"
---

# lean-competitive-math (euler-prover)

> **MANDATORY** (hot-tier): the answer-check gate (G-2), the axiom audit (G-4),
> and the no-sorry gate (G-5) are hard gates. A `native_decide` answer-check is
> allowed ONLY as a Bronze rung that ships WITH a structural-proof follow-up
> filed (G-6) -- otherwise it is an ordinary one-tactic `decide` and
> `@lean-proof-review` L3 flags it. Skipping Persist = incomplete.

Formalize a Project-Euler / competition-math problem as a Lean 4 theorem that
pins the concrete numeric answer, prove it, VERIFY the answer computes, then
IMPROVE the proof up the trust ladder. This skill owns the move that trips the
generic review gate -- closing `theorem eulerN : answer = <KNOWN> := by
native_decide` -- and gives it a governed home with an explicit carve-out.

---

## Routing

- **USE FOR:** formalizing a Project-Euler / competition-math problem as a Lean 4
  theorem asserting a concrete numeric answer; getting a first green proof
  (typically Bronze `native_decide`); verifying the answer computes (`#eval` +
  the theorem closes); auditing the compiler-trust axiom via `#print axioms`;
  and driving the improvement pass up the ladder Bronze (`native_decide`) ->
  Silver (`decide` / `norm_num`) -> Gold (characterising property / closed form).
- **DO NOT USE FOR:** authoring the theorem statement alone (use `@lean-specification`);
  writing tactics one step at a time or triaging tactic errors (use `@lean-proof`);
  generic single-proof audit outside the carve-out (use `@lean-proof-review`);
  Mathlib API / lemma discovery (use `@lean-research`); project-wide quality
  scoring (use `@lean-quality-engine`); open problems with no known numeric
  answer (this skill requires a known target).
- **TRIGGERS:** Project Euler, competition math, euler-prover, numeric answer
  theorem, answer = N, native_decide answer-check, computed constant, closed-form
  proof.

## Behavioural rules (G-*)

- **G-1** (MUST): The theorem MUST pin the expected numeric answer as the
  right-hand side (`theorem eulerN : answer = <KNOWN>`), never an existential,
  an opaque bound, or a `True`-shaped restatement. [Trace: AC-EM-01]
- **G-2** (MUST): Before claiming done, the skill MUST verify the answer computes
  -- `#eval answer` MUST print `<KNOWN>` AND the theorem MUST close (via
  `native_decide` or `decide`). A statement that type-checks but does not
  evaluate to the target is NOT done. [Trace: AC-EM-02]
- **G-3** (SHOULD): The skill SHOULD run the improvement pass -- replace
  `native_decide` with a kernel-checked or structural proof along the ladder
  Bronze (`native_decide`) -> Silver (`decide` / `norm_num`) -> Gold
  (characterising property / closed form). [Trace: AC-EM-03]
- **G-4** (MUST): When a `native_decide` answer-check ships, the skill MUST record
  its justification -- the compiler-trust axiom (in current Lean a generated
  `<thm>._native.native_decide.ax_*`, underpinned by `Lean.ofReduceBool` /
  `Lean.trustCompiler`) -- and MUST audit it with `#print axioms eulerN`.
  [Trace: AC-EM-04]
- **G-5** (MUST NOT): The skill MUST NOT close with `sorry` or `admit`; a
  placeholder answer-check is not a proof and MUST NOT be persisted as one.
  [Trace: AC-EM-05]
- **G-6** (MUST): L3 carve-out -- a one-tactic `native_decide` (or `decide`)
  close on the answer theorem is legitimate at `@lean-proof-review` L3
  (non-triviality) IFF a structural-proof follow-up task is filed. Absent that
  follow-up it MUST be flagged exactly like any other one-tactic `decide`
  (mirrors `@lean-proof-review` G-5). [Trace: AC-EM-06]
- **G-7** (MUST): On any guard failure the skill MUST escalate per Recovery &
  STOP; it MUST NOT silently downgrade a gate or ship a Bronze proof past a
  fired trigger. [Trace: AC-EM-07]

## Workflow

Discover -> Plan -> Execute -> Validate -> Persist.

1. **Discover** [discover] -- read the problem; extract the KNOWN numeric answer
   from its source; locate or request the Lean/Mathlib encoding of `answer`;
   confirm `lake env lean` (or `lean`) resolves. If the theorem statement is not
   yet written, pull it from `@lean-specification`.
2. **Plan** [discover] -- choose the encoding of `answer` (Finset / List
   enumeration vs closed form) and the ladder rung to aim for. If the encoding
   or a needed Mathlib primitive is uncertain, hand to `@lean-research`. STOP if
   the answer is unknown / the problem is open (this skill needs a known target).
3. **Execute** [execute] -- state `theorem eulerN : answer = <KNOWN>` (G-1);
   get a first GREEN proof, typically Bronze `native_decide`; delegate
   tactic-level work and error triage to `@lean-proof`. Keep `#eval answer` as a
   live sanity check next to the theorem.
4. **Validate** [validate] -- confirm `#eval answer` prints `<KNOWN>` and the
   theorem closes (G-2); run `#print axioms eulerN` and record the compiler-trust
   axiom whenever `native_decide` shipped (G-4); confirm no `sorry` / `admit`
   (G-5); run the improvement pass as far up the ladder as feasible (G-3); route
   the file to `@lean-proof-review` under the L3 carve-out (G-6).
5. **Persist** [persist] *(MANDATORY)* -- commit the Lean file plus the
   `#print axioms` result; whenever a `native_decide` answer-check remains, FILE
   the structural-proof follow-up task the carve-out requires (G-6); update the
   state tracker / tick `tasks.md`; emit a fleeting note via `@lean-zettelkasten`
   if a reusable Euler pattern surfaced. **Skipping Persist = incomplete.**

## Recovery & STOP

- **Novelty** -- answer unknown or the problem is open: STOP. This skill requires
  a known numeric target; ask for the target or decline.
- **Confidence** -- `native_decide` is the only feasible close and no
  structural follow-up can be scoped: STOP at belief < 0.90 and ask before
  shipping a permanent Bronze proof.
- Both `decide` and `native_decide` fail (recursion depth, timeout): STOP; hand
  the encoding to `@lean-research` for a closed-form / structural reduction
  before retrying (kernel `decide` blows `maxRecDepth` on large enumerations).
- **Conflict** -- the encoded `answer` does not match the problem's intended
  quantity: STOP; re-anchor the statement via `@lean-specification` before
  proving.
- **Governance / Irreversible** -- removing `native_decide` would change the
  theorem's trust surface in a way the owner has not accepted: STOP; do NOT
  silently swap axioms; ask.
- Same proof strategy fails 3 times: STOP; escalate to a human or hand to
  `@lean-proof` to isolate the failure.

## Handoffs

- **Predecessors:** `@lean-gateway` routes the task; `@lean-specification`
  supplies the theorem statement; `@lean-research` supplies the encoding and the
  Mathlib primitives.
- **Successors:** `@lean-proof` (tactic-level proving), `@lean-proof-review`
  (audits under the L3 carve-out), `@lean-quality-engine` (project QA).
- **Source spec:** this file (self-specified); every G-rule's `AC-EM-NN` is the
  correspondingly-numbered guarantee in this card.
- **Related ADRs:** ADR-0076 (skill-as-contract), ADR-0080 (handoff DAG).
- **Reference:** [`references/lean4-number-theory.md`](references/lean4-number-theory.md)
  -- Mathlib number-theory facilities, the Bronze/Silver/Gold tactic ladder, and
  the `native_decide` trust note. Template:
  [`Template_Euler.md`](Template_Euler.md) -- per-problem Lean file template with
  a verified Euler-1 example.

## Common failure modes

> AI agents commonly: state an existential or a bound instead of the exact
> numeric answer; declare done on a green `native_decide` without ever running
> `#print axioms`; leave a Bronze `native_decide` answer-check permanent with no
> structural follow-up filed (defeating the L3 carve-out); reach for kernel
> `decide` at a scale that blows `maxRecDepth` and then give up; paper a gap with
> `sorry`. Full registry: `GUARDRAILS.md` (Agent failure taxonomy).

## See also

- [`references/lean4-number-theory.md`](references/lean4-number-theory.md) -- Mathlib number-theory facilities + Bronze/Silver/Gold ladder + axiom-audit trust note (this skill's handbook).
- [`Template_Euler.md`](Template_Euler.md) -- per-problem Lean file template with a verified Euler-1 example.
- [`../lean-specification/SKILL.md`](../lean-specification/SKILL.md) -- Predecessor (theorem statement).
- [`../lean-research/SKILL.md`](../lean-research/SKILL.md) -- Predecessor (Mathlib encoding).
- [`../_overrides/lean-proof/SKILL.md`](../_overrides/lean-proof/SKILL.md) -- Successor (tactic-level proving).
- [`../lean-proof-review/SKILL.md`](../lean-proof-review/SKILL.md) -- Successor (audit under the L3 carve-out).
- [`../lean-quality-engine/SKILL.md`](../lean-quality-engine/SKILL.md) -- Successor (project QA).
- [`../lean-gateway/SKILL.md`](../lean-gateway/SKILL.md) -- Predecessor / router.
- [`../../references/lean4-tactic-hierarchy.md`](../../references/lean4-tactic-hierarchy.md) -- tactic priority table (`decide` vs `native_decide`).
- [`../../references/lean4-proof-strategy.md`](../../references/lean4-proof-strategy.md) -- one-step-at-a-time proof strategy.
