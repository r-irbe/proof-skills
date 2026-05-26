---
title: "Workflow templates v2 — eight Project workflow artefacts (MWE, PR, Blueprint, Zettelkasten, Spec, Bisect, Council, RetroLog)"
status: proposal
created: "2026-05-29"
updated: "2026-05-29"
author: "lab/template-improvements"
applies_to: "docs/project/lean/skills/templates/Template_{MWE,PR,Blueprint,Zettelkasten,Spec,Bisect,Council,RetroLog}.md (to be created)"
sources:
  - "docs/project/lean/skills/skills/lean-mwe/SKILL.md"
  - "docs/project/lean/skills/skills/lean-pr/SKILL.md"
  - "docs/project/lean/skills/skills/lean-blueprint/SKILL.md"
  - "docs/project/lean/skills/skills/lean-zettelkasten/SKILL.md"
  - "docs/project/lean/skills/skills/lean-specification/SKILL.md"
  - "docs/project/lean/skills/skills/lean-bisect/SKILL.md"
  - "docs/project/lean/skills/skills/lean-review-council/SKILL.md"
  - "docs/project/lean/skills/skills/lean-retro-methodology/SKILL.md"
  - "docs/project/lean/docs/refactor/wave-37/*.md (W37 reference wave)"
  - "docs/project/lean/docs/refactor/findings/wave-37-handoff.md"
  - "docs/project/lean/AGENT.md §Common Patterns + §When Adding New Theorems"
  - "docs/project/lean/skills/lab/design/04-template-v2-migration.md"
siblings:
  - "lab/design/04-template-v2-migration.md (SKILL.md frontmatter contract)"
  - "lab/design/05-zettelkasten.md"
---

# Workflow templates v2 — eight Project workflow artefacts

> **Status.** Proposal only. No `Template_MWE.md`, `Template_PR.md`,
> `Template_Blueprint.md`, `Template_Zettelkasten.md`, `Template_Spec.md`,
> `Template_Bisect.md`, `Template_Council.md`, or `Template_RetroLog.md`
> exists today in `docs/project/lean/skills/templates/`. The "v1" baseline
> is therefore the **set of embedded fragments** in the corresponding
> `lean-*` SKILL.md files plus the **ad-hoc shape** that real Project
> artefacts (wave dispatch docs, design critiques, handoffs) have
> converged on through W6 → W38 practice. This document compares those
> de-facto v1s against Project evidence, then proposes copy-pasteable v2
> templates that close the gaps.
>
> **Scope boundary.** This is a workflow-templates proposal. It is
> independent of, but compatible with, the SKILL.md frontmatter
> contract in `lab/design/04-template-v2-migration.md` (which targets
> the skill files themselves, not the artefacts they produce).

---

## Conventions used in every v2 template below

To keep the eight templates internally consistent, each v2 below uses
the same shape:

1. **YAML frontmatter** with `kind`, `id`, dates, author/agent,
   `status`, `inputs_read`, `refs`, and a `skill:` pointer back to the
   producing skill.
2. **§1 Context / Scope** — what this artefact is for, who it serves.
3. **§N …** — body sections specific to the artefact.
4. **§Reproducibility checklist** — pin/version capture, commands to
   re-run, expected outputs.
5. **§Acceptance criteria** — concrete, line-by-line "this artefact is
   good" gates. Always present.
6. **§Skill citation** — explicit back-pointer
   (`Produced by skills/skills/<slug>/SKILL.md vX.Y.Z`).

The `status` vocabulary is the same across all templates:
`draft | active | landed | superseded | rejected`.

---

# 1. Template_MWE.md (Minimal Working Example)

## 1.1 Current template gaps

The de-facto v1 for an MWE is the workflow embedded in
`lean-mwe/SKILL.md` (118 LOC). It defines the `lake exe minimize`
pipeline well, but there is **no artefact template** — the SKILL just
says "produce a `.out.lean` file and a bug report". Concretely:

- **No frontmatter contract.** Bug reports get pasted into GitHub
  issues with no captured pin (`mathlib_pin`, `lean_toolchain`), so the
  same MWE on a different toolchain is irreproducible. Compare W37
  artefacts, which always carry `lean_toolchain: v4.30.0-rc2 /
  mathlib_pin: 9491746 / cslib_pin: 6be5d16`
  (`wave-37/b1-a1-state-snapshot.md:11–14`).
- **No reproducibility checklist.** SKILL §4 has a 4-bullet "Checklist
  Before Filing" but nothing about which `lake env lean` command to
  paste into the report, what `lake --version` to record, or whether
  the file was minimized with `--resume`.
- **No project-specific acceptance criteria.** SKILL §4 has one bullet
  ("strip any sorry") but does not gate on the project invariant
  `unexpected − whitelisted = 0` (`AGENT.md §Hard Constraints`).
- **No back-pointer to the skill.** Once an MWE is on a GitHub issue
  there is no way to know it was produced by `lean-mwe` v0.X.
- **No worked example** of `#guard_msgs` vs `#guard_panic` side-by-side
  in the SKILL — the patterns are shown separately at lines 36–56.

## 1.2 Project evidence

1. `lean-mwe/SKILL.md:111` — the only "project-specific" guidance is one
   sentence about `grind` vs `omega`. No artefact template.
2. `wave-37/b1-a1-state-snapshot.md:11–14` — every real Project artefact
   pins the toolchain triple. MWE bug reports currently do not.
3. `AGENT.md:51–82 (Module Inventory)` — the project corpus has 22,312+
   LOC across 126 modules; an MWE from one module needs to record
   which one, so that a regression can be localised when the bug is
   fixed upstream.
4. `wave-37/b3-a3-todo-01-amari.md:60–72` — successful Project bug
   reports always include a `lake build` tail and a
   `#print axioms` block. The MWE skill mentions neither.
5. `skills/skills/lean-bisect/SKILL.md:5–13` — bisect explicitly states
   "Test files must be self-contained with no `Mathlib` imports."
   MWEs that feed bisect must therefore record their post-minimisation
   import count; SKILL has no such field.

## 1.3 Proposed v2 template

```markdown
---
kind: mwe
id: MWE-YYYYMMDD-NNN
title: "<one-line summary of the bug>"
status: draft         # draft | active | landed | superseded | rejected
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id or human>"
upstream: "lean4 | mathlib4 | cslib | lspec | leanblueprint | other"
upstream_issue: ""    # filled when filed; e.g. leanprover/lean4#1234
captured_from:
  module: "Project/Foundations/<…>.lean"
  line: 0
  commit: "<short-sha>"
toolchain:
  lean: "leanprover/lean4:vX.Y.Z-rcN"
  mathlib_pin: "<short-sha>"
  cslib_pin: "<short-sha>"
  lspec_pin: "<short-sha>"
minimizer:
  tool: "lake exe minimize"
  passes: ["delete", "import-inlining"]   # default both
  resumed: false
  rounds: 0
guard: "guard_msgs | guard_panic | exit_code"
skill: "skills/skills/lean-mwe/SKILL.md@vX.Y.Z"
refs:
  - "<related ZK note or wave doc>"
---

# MWE-YYYYMMDD-NNN — <title>

## §1 Symptom

One paragraph describing what goes wrong and why it surprised the
author. Quote the exact error or panic message verbatim.

## §2 Reproduction (final minimized file)

```lean
import <only-imports-that-survived-minimization>

/--
error: <exact verbatim diagnostic, including line numbers>
-/
#guard_msgs in
example : <goal> := by <tactic>
```

- **Imports remaining after minimisation:** N (target: 0, ≤2
  acceptable for Mathlib-rooted bugs)
- **LOC remaining after minimisation:** N (target: ≤20)

## §3 Reproducibility checklist

- [ ] `lake env lean MWE.lean` returns exit code 0 (guard passed)
- [ ] `lake --version` matches `toolchain.lean` in frontmatter
- [ ] `lean-toolchain` file in workspace pins exactly that release
- [ ] No `Mathlib` imports remain (or count ≤2 with explicit
      justification in §4)
- [ ] No `sorry` / `admit` anywhere in the file
- [ ] `#print axioms` on the minimal example shows only
      `{propext, Classical.choice, Quot.sound}` — extra axioms must be
      listed in §4

## §4 Provenance

Original site that triggered the bug:

- File:        `<Project/…/Module.lean:L>`
- Original commit: `<short-sha>`
- Original tactic: `<the tactic line that failed>`
- Suspected upstream component: `<elaborator | linter | simp set | …>`

Notes on imports / axioms that could not be removed and why.

## §5 Bisect handoff (optional but recommended)

If this MWE should feed `script/lean-bisect`:

- Self-contained?    yes / no
- Bisect range:      `<good-nightly>..<bad-nightly>` (or empty)
- Pass/fail mode:    exit-code | guard_msgs | ignore-messages
- Expected good sha: `<short-sha>` (verified locally)
- Expected bad sha:  `<short-sha>` (verified locally)

→ When this MWE is fed to `lean-bisect`, file the resulting
`Bisect-YYYYMMDD-NNN.md` and cross-link it in `refs:`.

## §6 Acceptance criteria

This MWE is "good" when **all** of the following hold:

1. The reproduction file in §2 compiles to the verbatim diagnostic
   under the pinned toolchain.
2. Frontmatter `toolchain.*` keys are all populated (no `?`, no `n/a`).
3. The file would be acceptable to file upstream as-is (no Project
   imports, no project-private namespaces, no `sorry`).
4. Reproduction is bounded: ≤20 LOC of body, ≤2 import lines.
5. `#print axioms` is captured in §4 if anything beyond the
   `{propext, Classical.choice, Quot.sound}` triple appears.
6. A `lean-bisect` handoff section exists (even if "n/a").

## §7 Skill citation

Produced by `skills/skills/lean-mwe/SKILL.md@vX.Y.Z`. See also
`skills/templates/Template_Foundation.md` for the starter module
shape from which §2 reproductions were factored.
```

## 1.4 Diff summary

- **+** YAML frontmatter (`kind`, `id`, `toolchain` triple,
  `minimizer.*`, `skill`) — none in v1.
- **+** §3 reproducibility checklist (5 gates) — v1 has 4 free-form
  bullets at SKILL.md:107–111.
- **+** §5 explicit bisect handoff block — v1 SKILL mentions bisect at
  §"Workflow for Mathlib Issues" (line 67–73) but never produces an
  artefact-level link.
- **+** §6 acceptance criteria — v1 has none.
- **+** §7 skill back-pointer — v1 has none.
- **~** §2 reproduction collapses v1's "Step 1 / Step 2" into one
  block with explicit LOC + import budget.

---

# 2. Template_PR.md (Pull Request artefact)

## 2.1 Current template gaps

`lean-pr/SKILL.md` (93 LOC) is a **conventions cheat-sheet** for the
upstream `leanprover/lean4` repo: commit-message format, changelog
labels, copyright headers. It is not an artefact template at all — it
tells you what *not* to put in the PR description ("No `## Summary`
header — just start with the text", line 84) but offers no concrete
shape for the description body, no checklist, and no link back to the
Project artefacts that motivated the PR.

The same problem applies to `mathlib-pr` (sibling skill) and to
Project-internal PRs (which are landed as wave commits with messages
like `W37 B2 Foundations UMB-triple`, see
`wave-37/b5-closeout.md:60–67`). Three concrete gaps:

- **No frontmatter** capturing target repo, branch, base sha, target
  release.
- **No reproducibility checklist** linking the PR to a buildable
  commit + the local `lake build` output.
- **No "what artefacts justify this PR" block** — wave PRs frequently
  carry 5+ supporting docs (state-snapshot, shard-plan, design-critique,
  closeout) and the PR body never enumerates them.

The body shape we *want* is the one that `wave-37/b5-closeout.md`
informally uses: dispatch summary table, gate verdicts table, metrics
table, commit lineage table.

## 2.2 Project evidence

1. `lean-pr/SKILL.md:79–87` — the only "PR conventions" section is 8
   lines and rules things out without saying what to put in.
2. `wave-37/b5-closeout.md:14–28` — real wave commits land with a
   detailed dispatch table; this is the de-facto PR body template that
   should be canonised.
3. `wave-37/b5-closeout.md:32–40` — gate verdicts table
   (`G-37-1..G-37-4`) is the artefact-level acceptance criteria block
   that PR bodies should mirror.
4. `wave-37/b5-closeout.md:43–55` — cumulative metrics table is the
   reproducibility block (jobs/modules/declarations/axiom counts).
5. `AGENT.md:289–360` — project-specific patterns that PR descriptions
   should explicitly check (Nat division, simplex, regime
   exhaustiveness, axiom invariant).

## 2.3 Proposed v2 template

```markdown
---
kind: pr
id: PR-YYYYMMDD-NNN          # local id; replace with upstream # when filed
title: "<type>: <imperative subject>"  # e.g. "feat: add fisherMatrix posDef variant"
status: draft                # draft | filed | review | merged | closed
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id or human>"
target_repo: "leanprover/lean4 | leanprover-community/mathlib4 | cslib | Project-internal"
target_branch: "master"
base_sha: "<short-sha>"
head_sha: "<short-sha>"
upstream_number: ""          # filled when filed; e.g. 1234
changelog_label: "changelog-{language|tactics|library|…|no}"
type: "feat | fix | doc | style | refactor | test | chore | perf"
toolchain:
  lean: "leanprover/lean4:vX.Y.Z"
  mathlib_pin: "<short-sha>"   # n/a if PR is to mathlib itself
  cslib_pin: "<short-sha>"
authority:
  - "<wave-NN/<shard>.md or spec id>"
  - "<MWE-id or bisect-id if applicable>"
skill: "skills/skills/lean-pr/SKILL.md@vX.Y.Z"  # or lean-mathlib-pr
---

# PR-YYYYMMDD-NNN — <title>

## §1 Description (PR body, ≤2 short paragraphs)

> Per `lean-pr/SKILL.md:79–87`: start with "This PR …". No `## Summary`
> header. No "Test plan" section. No "Implementation details" section.

This PR <imperative, present-tense one-liner>. <One sentence of why,
linking to the upstream issue or the project artefact that motivated it.>

<Optional second paragraph: any caveat, follow-up, or limitation.>

## §2 Change inventory

| File | LOC ± | Reason |
|---|---:|---|
| `<path/to/file.lean>` | +N / -M | <one-line reason> |
| `<path/to/another.lean>` | +N / -M | … |
| **Total** | **+N / -M** | |

- New theorems / defs: N
- Modified theorems / defs: N
- Removed theorems / defs: N (must be 0 in `mathlib4` unless deprecation
  protocol followed)

## §3 Reproducibility checklist

- [ ] Branch checks out at `head_sha` cleanly
- [ ] `lake build` (or `lake build Project` for project work) passes at
      `head_sha`; tail pasted below
- [ ] `#print axioms <new_theorem>` for every new public theorem shows
      only the standard triple `{propext, Classical.choice, Quot.sound}`
      (paste under §5)
- [ ] No new `sorry`, `admit`, or unwhitelisted `axiom`
- [ ] If `type: feat | fix`, a `changelog-*` label is set (see
      `lean-pr/SKILL.md:32–46`)
- [ ] If touching `src/Lean/`, `src/Std/`, `src/lake/Lake/`: `module` +
      `prelude` declarations present (see `lean-pr/SKILL.md:48–63`)
- [ ] Copyright header on every new file in `src/`
      (`lean-pr/SKILL.md:65–77`)

## §4 Build tail (paste verbatim)

```
✔ [N/N] Built <target> (Xs)
Build completed successfully (N jobs).
```

## §5 Axiom audit (paste verbatim)

```
'<new_theorem_1>' depends on axioms: [propext, Classical.choice, Quot.sound]
'<new_theorem_2>' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Any deviation from the standard triple must be justified in §6.

## §6 Justification of any deviations

- New axioms introduced: <list, with one-line rationale each; usually
  empty>
- Unwhitelisted axioms touched in call graph: <list; must be empty for
  upstream PRs>
- API breaking changes: <list; must be empty for `fix`/`doc`>

## §7 Authority chain

This PR is justified by:

1. `<wave-NN/<shard>.md>` — <one-line role: design / spec / critique>
2. `<MWE-id>` — <one-line role: motivating bug report> (optional)
3. `<bisect-id>` — <one-line role: regression isolation> (optional)
4. `<ZK-id>` — <one-line role: extracted convention> (optional)

## §8 Acceptance criteria

This PR is "good" when **all** of the following hold:

1. §1 description follows `lean-pr` conventions (starts with "This PR…",
   no banned section headers, imperative present-tense title).
2. §2 change inventory totals match `git diff --stat` at `head_sha`.
3. §3 checklist is all ticked or has an explicit waiver inline.
4. §4 build tail and §5 axiom audit are verbatim, not paraphrased.
5. §6 deviations list is empty OR every deviation has an authority
   reference in §7.
6. `target_repo`, `target_branch`, `base_sha`, `head_sha`,
   `changelog_label`, and `type` in frontmatter are all populated
   before status moves from `draft` to `filed`.

## §9 Skill citation

Produced by `skills/skills/lean-pr/SKILL.md@vX.Y.Z` (or
`skills/skills/mathlib-pr/SKILL.md@vX.Y.Z` for mathlib4 contributions).
```

## 2.4 Diff summary

- **+** Full YAML frontmatter — v1 has none (skill is conventions-only).
- **+** §2 change inventory table — v1 has nothing.
- **+** §3 reproducibility checklist (7 gates) cross-linking the
  skill's existing rules (`module`/`prelude`, copyright header,
  changelog label).
- **+** §4 / §5 verbatim build + axiom blocks (mirrors the project W37
  closeout pattern at `wave-37/b5-closeout.md:43–55`).
- **+** §7 authority chain — v1 has no concept; v2 makes the
  MWE/Bisect/Spec/Council artefacts that justify the PR machine-linkable.
- **+** §8 acceptance criteria — v1 has none.
- **~** §1 keeps v1's banned-header rule but reframes it as a
  call-out, so v2 is back-compatible with the existing convention.

---

# 3. Template_Blueprint.md

## 3.1 Current template gaps

`lean-blueprint/SKILL.md` (677 LOC) is the most thorough of the eight
skills, but it documents the **pipeline** (`ANALYZE → ANNOTATE →
SCAFFOLD → EXTRACT → RENDER`), not the **artefact** that the pipeline
should leave behind. There is no `blueprint-run.md`-style record of
"this run was at sha X, used mathlib pin Y, produced these LaTeX
files, took N minutes, here is the dependency graph".

Concrete gaps:

- **No run-record template.** A blueprint is regenerated periodically.
  Each regeneration should produce a one-page artefact answering:
  what was the source sha, what annotations were added/changed, which
  modules are now blueprint-covered, what is the cumulative coverage
  percentage, where are the rendered outputs.
- **No coverage table contract.** SKILL §3.3 ("Blueprint Candidate
  Selection") talks about which decls to annotate but provides no
  per-module coverage table for the artefact.
- **No reproducibility checklist.** The five pipeline stages each have
  validation in SKILL §9.3 (lines 587–600), but those validations are
  in the SKILL, not in a per-run artefact, so they are not auditable
  after the fact.
- **No skill back-pointer in the rendered output.** The published
  blueprint web page does not say "produced by lean-blueprint vX.Y.Z
  on date Z from sha W".

## 3.2 Project evidence

1. `lean-blueprint/SKILL.md:541–600` — the SKILL has a 9-bullet
   "First-Time Setup" + "Validation Checks" but no artefact template
   to capture the result of running them.
2. `wave-37/b5-closeout.md:43–55` — Project publishes cumulative metrics
   tables for every wave; the same pattern should apply to blueprint
   runs.
3. `lean-blueprint/SKILL.md:491–512 (Part 8 — Project-specific
   Configuration)` — defines module ordering and cross-module bridges
   to highlight, but does not specify how a blueprint *run* records
   compliance with that configuration.
4. `lab/proto/skills-v2/lean-blueprint/SKILL.md:7–17` — the prototype
   v2 SKILL already pins `version: 0.2.0`, `source_spec`,
   `last_reviewed` in frontmatter, but the artefact it produces
   inherits none of that.
5. `wave-37/b3-a1-br-01-feasibility.md:25–73` — bridge feasibility
   docs already enumerate Mathlib decls with file:line citations;
   blueprint runs should produce the same machine-readable table.

## 3.3 Proposed v2 template

```markdown
---
kind: blueprint-run
id: BP-YYYYMMDD-NNN
status: draft                # draft | landed | superseded
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id>"
source:
  repo: "r-irbe/tacit-mui"
  branch: "wave-3"
  sha: "<short-sha>"
toolchain:
  lean: "leanprover/lean4:vX.Y.Z"
  mathlib_pin: "<short-sha>"
  leanblueprint: "<pip version>"
  leanarchitect: "<lake version>"
  graphviz: "<system version>"
outputs:
  pdf: "blueprint/web/blueprint.pdf"
  web: "blueprint/web/index.html"
  dep_graph: "blueprint/web/dep_graph_document.html"
  raw_tex: ".lake/build/blueprint/library/"
skill: "skills/skills/lean-blueprint/SKILL.md@vX.Y.Z"
predecessor: "BP-YYYYMMDD-NNN"   # previous run for diff; empty if first
---

# BP-YYYYMMDD-NNN — Blueprint regeneration at `<short-sha>`

## §1 Scope of this run

- Mode: `full | incremental` (incremental = only modules changed since
  predecessor sha)
- Modules in scope: N (of M total in repo)
- New `@[blueprint]` annotations added this run: N
- Removed / modified annotations: N
- Modules newly blueprint-covered: N
- Predecessor run: <BP-id or "first run">

## §2 Coverage table (per cluster)

| Cluster | Modules covered | Decls annotated | Decls in scope | Coverage % | Δ vs predecessor |
|---|---:|---:|---:|---:|---:|
| Foundations.Algorithms | … | … | … | … | … |
| Foundations.Designs | … | … | … | … | … |
| Foundations.AnalyticCombinatorics | … | … | … | … | … |
| Foundations.InformationGeometry | … | … | … | … | … |
| Foundations.FractalGeometry | … | … | … | … | … |
| **Total** | **N** | **N** | **N** | **N%** | **±N%** |

## §3 Cross-cluster bridges highlighted

> Per `lean-blueprint/SKILL.md §8.2`, bridges receive distinguished
> color coding. Enumerate every bridge present at this sha.

| Bridge id | LHS cluster | RHS cluster | Decl(s) | File:line |
|---|---|---|---|---|
| BR-W37-01 | InformationGeometry | FractalGeometry | `klDiv_moranWeights_uniform_nonneg` | `Project/Bridges/InfoGeom_FractalGeom_Sketch.lean:L` |
| … | … | … | … | … |

## §4 Pipeline stage report

| Stage | Status | Duration | Notes |
|---|---|---:|---|
| ANALYZE  | ✅ | Ns | M modules, E edges |
| ANNOTATE | ✅ | Ns | N annotators (fan-out), N new annotations |
| SCAFFOLD | ✅ | Ns | content.tex deltas: +N / -N |
| EXTRACT  | ✅ | Ns | `lake build :blueprint` GREEN |
| RENDER   | ✅ | Ns | `leanblueprint {pdf,web}` GREEN |

## §5 Reproducibility checklist

- [ ] `git checkout <source.sha>` clean
- [ ] `lean-toolchain` matches `toolchain.lean`
- [ ] `lake update` pinned to `toolchain.mathlib_pin`
- [ ] `pip show leanblueprint` matches `toolchain.leanblueprint`
- [ ] `dot -V` (graphviz) matches `toolchain.graphviz`
- [ ] `lake build :blueprint` produces the file tree under
      `outputs.raw_tex`
- [ ] `leanblueprint pdf` produces `outputs.pdf` (non-empty)
- [ ] `leanblueprint web` produces `outputs.web` (non-empty)
- [ ] `outputs.dep_graph` opens in a browser without 404s
- [ ] Per-module coverage in §2 sums to the row total
- [ ] Every `BR-*` row in §3 corresponds to a real file:line at
      `source.sha`

## §6 Acceptance criteria

This blueprint run is "good" when **all** of the following hold:

1. All five pipeline stages in §4 are ✅ with non-empty durations.
2. Total coverage % in §2 is **monotone non-decreasing** vs the
   predecessor run (or this is the first run).
3. Every bridge listed in §3 has a corresponding `@[blueprint]`
   annotation in the source (verify by `grep -n "@\[blueprint\]"`).
4. §5 reproducibility checklist is fully ticked.
5. The rendered web page footer includes "Produced by lean-blueprint
   vX.Y.Z at <source.sha>" (skill back-pointer in the artefact).
6. If incremental mode: the predecessor run id in frontmatter resolves
   to an existing `BP-*` file.

## §7 Skill citation

Produced by `skills/skills/lean-blueprint/SKILL.md@vX.Y.Z`. The
pipeline contract is at `lean-blueprint/SKILL.md §2` (Part 2 —
Pipeline Architecture). Project cluster ordering and bridge colour
coding are at `lean-blueprint/SKILL.md §8.1–§8.3`.
```

## 3.4 Diff summary

- **+** Run-record artefact concept — v1 has none.
- **+** Per-cluster coverage table with Δ vs predecessor.
- **+** Bridge inventory cross-referenced to file:line.
- **+** Pipeline stage report table with duration + GREEN/RED.
- **+** §5 reproducibility checklist consolidating SKILL §9.3
  scattered guidance into a single ticklist.
- **+** Skill back-pointer required in the rendered web footer.

---

# 4. Template_Zettelkasten.md

## 4.1 Current template gaps

The de-facto v1 is `lean-zettelkasten/SKILL.md §"Note Format"`
(lines 36–63) and the duplicate Template 4 in
`lean-review-council/SKILL.md §"Template 4: Zettelkasten Note"`
(lines 749–773). The two copies are similar but **not byte-identical**:
the council variant omits the `Status` field and uses `member-name`
instead of `Σ / Φ / Ν / Λ / Ω / SYN`. This template drift is itself a
gap.

Other concrete gaps:

- **YAML frontmatter is mixed with `## H2` Markdown headers.** The
  current "frontmatter" is `## Type / ## Created / ## Updated`
  — these are body sections, not YAML, so they are not
  machine-extractable by the linter sketched in
  `lab/design/04-template-v2-migration.md §5`.
- **No `superseded_by` reciprocity rule.** The `Supersedes` link is
  in the format but the inverse `superseded_by` is not, so the index
  cannot tell whether a note is still authoritative.
- **No acceptance criteria.** SKILL says "do NOT spend time
  perfecting" (line 80) for fleeting notes, but provides no graduation
  gate for "ready to promote to permanent".
- **`fleeting/`, `literature/`, `permanent/` subtree is not yet
  populated.** `docs/project/lean/docs/zettelkasten/` contains only
  `_index.md` and `_tags.md` (verified). The first batch of notes
  needs a stricter template than the SKILL provides.

## 4.2 Project evidence

1. `lean-zettelkasten/SKILL.md:36–63` — current note format,
   header-based.
2. `lean-review-council/SKILL.md:749–773` — duplicate note format,
   drifted.
3. `docs/project/lean/docs/zettelkasten/_index.md:1–3` — index has 0
   notes; this is the moment to lock the v2 template before drift
   accumulates.
4. `lean-zettelkasten/SKILL.md:65–69` — ID convention
   `ZK-YYYYMMDD-NNN`; v2 keeps this.
5. `lean-zettelkasten/SKILL.md §"Disconnected note detection"` and
   `_tags.md:7–22` — the index/tag automation needs YAML frontmatter
   to function reliably.

## 4.3 Proposed v2 template

```markdown
---
kind: zettel
id: ZK-YYYYMMDD-NNN
title: "<concise insight, ≤80 chars>"
type: fleeting        # fleeting | literature | permanent
subtype: ""           # permanent only: tactics | pitfalls | conventions | cross-module | proofs
status: active        # active | superseded | disputed | archived
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Σ | Φ | Ν | Λ | Ω | SYN | <agent-id>"
source:
  kind: "theorem | module | review-session | external-url | wave-shard"
  ref: "<Project/…/Module.lean#thm_name or URL or wave-NN/shard.md>"
tags: ["tag1", "tag2"]   # must be subset of _tags.md
links:
  related: ["ZK-…"]
  supports: ["ZK-…"]
  contradicts: ["ZK-…"]
  supersedes: ["ZK-…"]      # this note replaces these
  superseded_by: ["ZK-…"]   # this note is replaced by these (RECIPROCAL of `supersedes`)
skill: "skills/skills/lean-zettelkasten/SKILL.md@vX.Y.Z"
---

# ZK-YYYYMMDD-NNN — <title>

## §1 Content

One paragraph. One idea. Concrete enough that another agent reading
this in isolation can act on it.

## §2 Evidence

Verbatim Lean diagnostic, axiom trace, code snippet, or external
citation. Quote rather than paraphrase. Include file:line refs.

```lean
-- minimal illustrative snippet (≤ 10 LOC)
```

## §3 Context

- Source theorem / module / session: <ref>
- Why this matters: <one sentence>
- Scope: <project-wide | cluster: <name> | module-local>

## §4 Reproducibility (literature / permanent only)

For fleeting notes: skip this section.

For literature / permanent notes:

- [ ] The Evidence block in §2 can be reproduced at pin
      `mathlib_pin: <sha>` / `lean_toolchain: <release>`
- [ ] If the note cites an external paper / Zulip thread, the URL
      resolves and a permalink (Zulip message id, arXiv abs id, DOI)
      is included
- [ ] If the note generalises from N examples, all N are linked under
      `links.supports`

## §5 Acceptance criteria

By type:

**Fleeting** is "good" when:
1. §1 captures one idea (no compound observations).
2. `source.ref` resolves at creation time.
3. At least one tag from `_tags.md` is present.
4. Author is identified.

**Literature** is "good" when fleeting criteria + §4 reproducibility
hold, plus the external citation is permalinked.

**Permanent** is "good" when fleeting + literature criteria hold, plus:
5. The note has been referenced by ≥2 other notes OR cited by ≥1
   subsequent wave artefact.
6. `subtype` is set and the file lives under
   `permanent/<subtype>/ZK-….md`.
7. All `links.supersedes` targets have matching `links.superseded_by`
   pointing back (reciprocity verified).
8. Tags are a subset of `_tags.md`; new tags require a `_tags.md` PR
   landed in the same commit.

## §6 Skill citation

Produced by `skills/skills/lean-zettelkasten/SKILL.md@vX.Y.Z`.
Promotion (fleeting → literature → permanent) follows
`lean-zettelkasten/SKILL.md §"Creating Notes"` and
`§"Synthesis Workflow"`.
```

## 4.4 Diff summary

- **+** Strict YAML frontmatter (replaces `## H2` field rows).
- **+** `superseded_by` reciprocal link (was missing).
- **+** `subtype` enum aligned to existing directory tree
  (`tactics/pitfalls/conventions/cross-module/proofs`).
- **+** §4 reproducibility (gated by type, off for fleeting).
- **+** §5 per-type acceptance criteria (graduation gates from
  fleeting → literature → permanent).
- **+** Tag-set discipline (subset of `_tags.md`, new tags require
  same-commit edit).
- **=** Author vocabulary (`Σ | Φ | Ν | Λ | Ω | SYN | <agent-id>`)
  resolves the council-skill drift in favour of the
  lean-zettelkasten SKILL spelling.

---

# 5. Template_Spec.md (Theorem specification)

## 5.1 Current template gaps

`lean-specification/SKILL.md` (267 LOC) defines a **three-part**
specification (`Requirement` / `Design` / `Documentation`) and
distributes each part as its own Markdown block. The current shape
has several gaps:

- **Three separate documents per theorem is heavy.** Project ships
  ≥1255 theorems; one
  `REQ-….md + DES-….md + DOC-….md` per theorem is unmanageable. The
  templates should be **collapsible into one file** with three
  sections, keyed by a single `SPEC-id`.
- **`sorry -- placeholder` in the design block** (SKILL line 60)
  contradicts `AGENT.md` hard constraint that the project corpus carries
  zero sorry. Specs that ship with `sorry` placeholders accidentally
  leak into pinned commits.
- **`proj_simplex` / `proj_lyapunov` / `proj_exhaust` are flagged
  DEPRECATED** in the SKILL itself (line 73–74) yet remain in the
  template tactic-candidate table. Deprecated entries in the template
  cause novice agents to invoke retired tactics.
- **No frontmatter.** The three-part spec has no `status` field, no
  `mathlib_pin`, no `predecessor_spec` field, so the spec lifecycle
  (proposed → approved → implemented → merged) is invisible to tooling.
- **No reproducibility / acceptance section.** The three parts each
  end with a `### Validation` or `### Acceptance Criteria` checklist,
  but the lists are unticked free-form prose, not gates.

## 5.2 Project evidence

1. `lean-specification/SKILL.md:46, 73, 74` — `sorry` placeholder +
   DEPRECATED tactics still present in the template.
2. `lean-specification/SKILL.md §"Part 1: Requirement"` (lines 16–46)
   — already has good content; v2 keeps it and adds frontmatter.
3. `wave-37/b3-a1-br-01-feasibility.md:75–95` — real Project feasibility
   docs already use a per-candidate table with `feasibility:
   READY/PARTIAL/BLOCKED` columns; specs should adopt the same shape.
4. `wave-37/b3-a3-todo-01-amari.md:30–43` — real spec-execution docs
   carry a "Verdict" line + substrate-gap citation; v2 specs should
   capture this on the way in, not just on the way out.
5. `AGENT.md §"When Adding New Theorems"` (lines 360–370) — already
   defines a 6-step procedure; the spec template should be a
   strict superset of those 6 steps.

## 5.3 Proposed v2 template

```markdown
---
kind: spec
id: SPEC-YYYYMMDD-NNN
title: "<theorem one-liner, ≤80 chars>"
status: proposed             # proposed | approved | implemented | reviewed | merged | rejected
priority: P2                 # P0-blocker | P1-critical | P2-important | P3-enhancement
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id>"
paper_claim:
  source: "project-tufte.tex §N"
  ref: "<equation / proposition / corollary id>"
  quote: "<exact text from paper>"
domain:
  module: "Project/Foundations/<…>.lean"
  section: "§N"
toolchain:
  lean: "leanprover/lean4:vX.Y.Z"
  mathlib_pin: "<short-sha>"
predecessors: []             # ["SPEC-…", …] upstream theorems
successors: []               # ["SPEC-…", …] downstream theorems
skill: "skills/skills/lean-specification/SKILL.md@vX.Y.Z"
---

# SPEC-YYYYMMDD-NNN — <title>

## §1 Requirement (what + why)

### 1.1 Paper claim

- Source: §<section> of `project-tufte.tex`
- Equation / Proposition: <ref>
- Quote: "<exact text from paper>"

### 1.2 English statement

"<Plain-English translation. One sentence.>"

### 1.3 Preconditions

- <hypothesis 1>
- <hypothesis 2>
- <type constraints, bounds, simplex membership>

### 1.4 Domain placement

- Module: `Project/<…>.lean` §<N>
- DAG layer: <0 | 1 | 2 | 3 | 4> (per `AGENT.md §"DAG Build Layers"`)
- Related existing theorems: <names>

## §2 Design (how)

### 2.1 Lean signature (final form; NO `sorry`)

```lean
theorem <name> {params : Types}
    (h₁ : <condition₁>) (h₂ : <condition₂>) :
    <conclusion> :=
  by /- proof sketch goes in §2.2; final signature must NOT carry a
        placeholder body. Until ready, leave the body blank and mark
        status: proposed (not implemented). -/
```

> v2 rule: a spec at `status: proposed` may omit the proof body
> entirely. A spec at `status: implemented` MUST carry a proof body
> with **no `sorry` and no `admit`** (see `AGENT.md §"Hard
> Constraints"`).

### 2.2 Proof strategy

1. <high-level step>
2. <high-level step>
3. <high-level step>

### 2.3 Tactic candidates

> Per `AGENT.md §"Proof Search Strategy"`. Deprecated Project tactics
> (`proj_simplex`, `proj_lyapunov`, `proj_exhaust`) MUST NOT
> appear in this table.

| Step | Primary | Fallback | Notes |
|---|---|---|---|
| 0 | `grind` | `grind` | always first |
| 1 | `omega` | `linarith` | Nat / Int |
| 2 | `nlinarith` | `ring` + `positivity` | Real with products |
| 3 | `simp [<lemma>]` | `unfold` + `omega` | unfold + close |

### 2.4 Dependencies

- Upstream lemmas (mathlib or Project): <list>
- Upstream definitions: <list>
- Upstream modules to `import`: <list>

### 2.5 Difficulty + fallback

- Estimated: trivial | moderate | hard | research
- Rationale: <one sentence>
- Fallback if primary strategy fails:
  1. <alternative>
  2. <decomposition into sub-lemmas, each its own SPEC-id>

## §3 Documentation

### 3.1 Docstring (≤ 5 lines)

```lean
/-- One sentence summary. References paper §N equation E.
    Used by: <downstream theorem names>. -/
```

### 3.2 Paper appendix update

- [ ] Per-module theorem count in `project-tufte.tex` `\description`
- [ ] Total metrics in contribution inventory + Lean appendix sidenote
- [ ] If validating a new paper claim: add to enumerated properties
      list + verification mapping table

## §4 Reproducibility checklist

- [ ] `lake build Project.<Module>` GREEN at `toolchain.mathlib_pin`
- [ ] `lake build` (full) GREEN — 0 errors, 0 new warnings
- [ ] `#print axioms <name>` shows only
      `{propext, Classical.choice, Quot.sound}`
- [ ] No `sorry`, no `admit`, no unwhitelisted `axiom`
- [ ] `grep -n "theorem <name>" Project/*.lean` returns exactly 1 hit
      (no duplicate)
- [ ] AGENT.md "When Adding New Theorems" 6-step procedure executed in
      full

## §5 Acceptance criteria

This spec is "good" when **all** of the following hold:

By status:

**`proposed`** is good when:
1. §1 Requirement is complete (paper claim quoted, English stated,
   preconditions enumerated, domain placement set).
2. §2.1 signature type-checks (statement-only; no body required).
3. §2.4 dependencies are real (file:line references resolve).
4. `predecessors` in frontmatter list every transitively-required SPEC.

**`implemented`** adds:
5. Proof body is present and contains no `sorry`, no `admit`.
6. §4 reproducibility checklist is fully ticked.
7. `successors` in frontmatter is updated to include any new specs
   that depend on this one.

**`merged`** adds:
8. The theorem is referenced in `docs/project/project-tufte.tex` per §3.2.
9. A `PR-id` link is added to `refs:` and resolves to a merged PR.

## §6 Skill citation

Produced by `skills/skills/lean-specification/SKILL.md@vX.Y.Z`. The
authority on tactic choice is `AGENT.md §"Proof Search Strategy"` and
`skills/references/lean4-proof-strategy.md`. Hard constraints on
sorry/axioms come from `AGENT.md §"Hard Constraints"`.
```

## 5.4 Diff summary

- **+** Collapses three v1 files (`REQ-` + `DES-` + `DOC-`) into a
  single `SPEC-id` file with three sections.
- **+** Full YAML frontmatter (`status`, `priority`, `paper_claim`,
  `predecessors`, `successors`).
- **-** Removes `sorry -- placeholder` from the template signature
  (v1 SKILL line 60); replaces with explicit "proposed = no body,
  implemented = no sorry" rule.
- **-** Removes DEPRECATED Project tactics from §2.3 tactic-candidates
  table.
- **+** §4 reproducibility checklist tied to AGENT.md 6-step
  procedure.
- **+** §5 per-status acceptance criteria
  (`proposed → implemented → merged` lifecycle gates).
- **+** Skill back-pointer + AGENT.md cross-link.

---

# 6. Template_Bisect.md

## 6.1 Current template gaps

`lean-bisect/SKILL.md` (85 LOC) documents the `script/lean-bisect`
tool but produces **no artefact** for the bisection run. A bisect
result is currently just stdout pasted into an issue or a wave doc,
which is fine for one-off runs but useless for regression tracking
when the same bug recurs.

Concrete gaps:

- **No record of which MWE was bisected.** The skill says "Create a
  minimal test case" (line 71) and stops; the bisect result and the
  MWE are not linked.
- **No record of the bisect command, range, or timeout.** Critical for
  reproduction.
- **No "what changed in the offending commit" block.** The skill
  finds the commit but does not record the diff summary, so the
  artefact has to be re-derived to be useful.
- **No project-specific gates.** The skill (line 79) warns about
  reproducing with the same tactic (`grind` first) but does not gate
  the artefact on it.
- **No skill back-pointer + no link to a downstream PR/issue.**

## 6.2 Project evidence

1. `lean-bisect/SKILL.md:60–66` — Options like `--timeout`,
   `--ignore-messages`, `--nightly-only`; never recorded in an
   artefact.
2. `lean-bisect/SKILL.md:67–74` — Workflow for Mathlib issues
   explicitly chains MWE → bisect, but no shared id schema is
   proposed.
3. `wave-32/b1-shard-plan.md:305` — "per-row `lake build` bisects
   cleanly" — Project relies on bisectability of its own history; bisect
   artefacts should be first-class.
4. `wave-14/DECISION-LOG.md:117` — atomic commits chosen specifically
   to make bisection unambiguous; the artefact should record which
   commit-boundary policy was in force.
5. `lean-bisect/SKILL.md:79` — project-specific "grind first" rule is
   present but not enforceable without an artefact ticklist.

## 6.3 Proposed v2 template

```markdown
---
kind: bisect
id: BISECT-YYYYMMDD-NNN
title: "<regression one-liner>"
status: draft                # draft | running | landed | superseded
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id>"
upstream: "lean4 | mathlib4 | cslib | Project-internal"
mwe_ref: "MWE-YYYYMMDD-NNN"  # required if Mathlib-rooted; required
                              # also for Project regressions if a minimal
                              # test was authored
range:
  good: "<short-sha or nightly-YYYY-MM-DD>"
  bad:  "<short-sha or nightly-YYYY-MM-DD>"
options:
  timeout_s: 60
  ignore_messages: false
  nightly_only: false
  selftest_passed: true
result:
  commit: "<short-sha>"            # the bisect-identified commit
  author: "<commit-author>"
  message_subject: "<commit subject line>"
  files_touched: 0
  loc_changed: "+N / -M"
skill: "skills/skills/lean-bisect/SKILL.md@vX.Y.Z"
refs:
  - "<related ZK or wave doc>"
---

# BISECT-YYYYMMDD-NNN — <title>

## §1 Symptom

What changed between `range.good` and `range.bad`. Paste the
diagnostic delta verbatim:

```
# at <range.good>
<output>

# at <range.bad>
<output>
```

## §2 MWE feeding this bisect

- File: `<path/to/MWE.lean>`
- Frontmatter id: `<MWE-id>` (full artefact at `…/MWE-….md`)
- Self-contained? yes (no Mathlib imports) / no (justification:
  <reason — bisect will fail outside Mathlib-pinned ranges>)
- LOC: N
- Guard: `guard_msgs | guard_panic | exit_code`

## §3 Bisect command (verbatim)

```bash
script/lean-bisect <path/to/MWE.lean> \
    <range.good>..<range.bad> \
    --timeout <options.timeout_s> \
    [--ignore-messages] [--nightly-only]
```

- Endpoint verification: `script/lean-bisect ... --selftest` →
  `options.selftest_passed`.
- Bisect steps performed: N
- Wall-clock duration: HH:MM:SS

## §4 Identified commit

- SHA: `<result.commit>`
- Author: `<result.author>`
- Subject: `<result.message_subject>`
- Files touched: <result.files_touched>
- LOC: `<result.loc_changed>`
- Permalink: `https://github.com/<upstream>/commit/<result.commit>`

### Diff summary (paste `git show --stat <result.commit>`)

```
<paste>
```

### Root-cause hypothesis (one paragraph)

<Your best guess at why this commit changes the diagnostic captured in
§1. Cite specific changed files / lines.>

## §5 Reproducibility checklist

- [ ] MWE at `mwe_ref` compiles to the §1 "bad" diagnostic at
      `range.bad` and the "good" diagnostic at `range.good`
- [ ] `range.good` and `range.bad` are both reachable via
      `elan install <release>`
- [ ] The `script/lean-bisect` command in §3 can be re-run on a fresh
      checkout and yields the same `result.commit`
- [ ] `options.selftest_passed: true` was recorded before the run
- [ ] Project tactic discipline: if the MWE was reduced from Project, the
      original tactic was `grind` (or another Project tactic) and the
      MWE preserves that tactic (per `lean-bisect/SKILL.md:79`)
- [ ] If `ignore_messages: true`, the rationale is in §1 (e.g.
      "diagnostic wording changed; only exit code matters")

## §6 Acceptance criteria

This bisect is "good" when **all** of the following hold:

1. `mwe_ref` resolves and the linked MWE has `status: active | landed`.
2. `range.good` and `range.bad` are both valid release identifiers (a
   tag, a nightly-YYYY-MM-DD, or a commit reachable from the upstream
   branch).
3. `result.commit` was reproducible on a re-run from a clean checkout
   (§5 box ticked).
4. §3 records the exact command (no `<…>` placeholders left).
5. §4 includes the `git show --stat` paste AND a one-paragraph
   root-cause hypothesis.
6. If `upstream != Project-internal`, a downstream
   issue/PR link is recorded in `refs:` once the bisect is filed.
7. The artefact ends with §7 skill citation.

## §7 Skill citation

Produced by `skills/skills/lean-bisect/SKILL.md@vX.Y.Z`. The MWE that
feeds this bisect is produced by `skills/skills/lean-mwe/SKILL.md`
(see `Template_MWE.md`). Upstream filing follows
`skills/skills/lean-pr/SKILL.md` (see `Template_PR.md`).
```

## 6.4 Diff summary

- **+** Bisect artefact concept (v1 has only stdout).
- **+** `mwe_ref` field linking MWE ↔ bisect artefacts by id.
- **+** Verbatim command block (with `--selftest` precondition).
- **+** `git show --stat` paste of the identified commit.
- **+** Root-cause hypothesis paragraph.
- **+** §5 enforces the project's `grind`-first rule as a checklist gate
  (was prose-only in v1 SKILL line 79).
- **+** §6 acceptance criteria; in particular, re-run reproducibility.

---

# 7. Template_Council.md (Council review / design critique)

## 7.1 Current template gaps

The de-facto v1 is split across:

- `lean-review-council/SKILL.md §"Template 1: Council Session Report"`
  (lines 654–691)
- the actual `b*-design-critique-a*.md` files in
  `refactor/wave-29/`, `wave-37/`, etc.

The SKILL template uses an emoji severity scale (`🔴/🟠/🟡/✅`) and
five-member voting columns; the real wave artefacts use a different
scale (`Blocking / Non-Blocking / Suggestion`) and a single-reviewer
`PASS-WITH-FIXES` / `GO with amendments` verdict format. This drift
is the central gap.

Other gaps:

- **No frontmatter contract.** Real wave artefacts already pin
  `wave / batch / agent / pin_head / mathlib_pin / cslib_pin /
  lean_toolchain` (see `wave-37/b1-a5-design-critique.md:1–20`); the
  SKILL template does not.
- **No amendments table.** Real critique docs always carry a
  numbered amendments table (`M-1 … M-N`) with `Severity / Proposed
  amendment / Adoption recommendation` columns — see
  `wave-37/b1-a5-design-critique.md:72–82`. The SKILL template has
  only a vague `### Action Items` bullet list.
- **No "inputs audited" list.** Real critiques enumerate every doc
  read (`inputs_audited:` in frontmatter); without it, a re-runner
  cannot verify the critique was on the right baseline.
- **No acceptance criteria for the critique itself.** What makes a
  critique "good"? Currently undefined.

## 7.2 Project evidence

1. `lean-review-council/SKILL.md:654–691` — the SKILL Template 1 with
   emoji scale + 5-column vote table.
2. `wave-37/b1-a5-design-critique.md:1–20` — real critique frontmatter
   with full pin triple + `authority:` list.
3. `wave-37/b1-a5-design-critique.md:72–82` — real `M-1..M-N`
   amendments table (8 amendments, `Severity / Proposed amendment /
   Adoption recommendation` columns).
4. `wave-29/b1-design-critique-a5.md:32` — verdict format
   `PASS-WITH-FIXES (N BLOCKER, M MAJOR, K MINOR, L NIT)`.
5. `wave-27/b4-critique-a5.md:1–17` — `inputs_audited:` is
   exhaustive (15 docs); critiques without this list are
   non-reproducible.

## 7.3 Proposed v2 template

```markdown
---
kind: council-review
id: COUNCIL-YYYYMMDD-NNN     # or W<NN>-B<N>-a<N>-design-critique
title: "<one-line scope>"
status: draft                # draft | landed | superseded
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
agent: "<agent-id>"           # primary critic
council_role: "a5-critique"   # or Σ | Φ | Ν | Λ | Ω if single-member
mode: "single-critic | full-council"
session: "<session-id>"
wave: 0
batch: 0
shard: ""
pin_head: "<short-sha>"
mathlib_pin: "<short-sha>"
cslib_pin: "<short-sha>"
lspec_pin: "<short-sha>"
lean_toolchain: "leanprover/lean4:vX.Y.Z"
inputs_audited:
  - "<path/to/doc.md>"
  - "<path/to/another.md>"
sibling_artifacts_inferred_only: []   # docs referenced but not yet read
verdict: "GO | GO-WITH-AMENDMENTS | NO-GO | PASS-WITH-FIXES"
counts:
  blocking: 0
  major: 0
  minor: 0
  nit: 0
skill: "skills/skills/lean-review-council/SKILL.md@vX.Y.Z"
---

# COUNCIL-YYYYMMDD-NNN — <title>

## §0 Executive verdict

**<verdict>**. <One paragraph summary: what was reviewed, what the
critique concluded, what the next action is.>

Severity scale (single-critic mode): **Blocking / Non-Blocking /
Suggestion**.
Five-member voting (full-council mode): see §3.

## §1 Pressure-test summary (single-critic mode)

Bullet list of risks discovered, each ≤2 sentences, each tagged with a
proposed amendment id (`M-N`).

- **<topic>**: <observation>. → M-1
- **<topic>**: <observation>. → M-2
- …

## §2 Amendments table

| M-id | Concern | Severity | Proposed amendment | Adoption recommendation |
|---|---|---|---|---|
| **M-1** | <one-line concern> | Blocking | <concrete fix> | **ADOPT** |
| **M-2** | <one-line concern> | Non-Blocking | <concrete fix> | **ADOPT-EQUIVALENT** |
| **M-N** | … | Suggestion | <concrete fix> | **DEFER** |

> Adoption recommendation vocabulary:
> **ADOPT** (apply verbatim) ·
> **ADOPT-EQUIVALENT** (apply a functionally-equivalent change) ·
> **DEFER** (carry to the next wave) ·
> **REJECT** (with rationale).

## §3 Review findings table (full-council mode only)

| Member | Finding | Severity | Evidence | Line |
|---|---|---|---|---|
| Σ | <kernel finding> | Blocking | `#print axioms` output | L42 |
| Φ | <statement finding> | Non-Blocking | English translation | L10 |
| Ν | <novelty finding> | Suggestion | `exact?` result | L10 |
| Λ | <quality finding> | Non-Blocking | step count = N | L42-80 |
| Ω | <integration finding> | Non-Blocking | grep result | all |

### Votes

| Σ | Φ | Ν | Λ | Ω | Decision |
|---|---|---|---|---|---|
| ✅ | 🟡 | ✅ | 🟠 | ✅ | Approved with amendments |

## §4 Specific notes by review dimension

(Free-form; one short subsection per axis: scope, staging, gates,
dependencies, conventions, anti-collapse safeguards.)

## §5 Reproducibility checklist

- [ ] All docs in `inputs_audited` resolve at `pin_head`
- [ ] `lake build Project` (or relevant target) GREEN at `pin_head`
- [ ] Every M-id in §2 cross-references a file:line in an input doc
- [ ] If `mode: full-council`, every council member has a row in §3
- [ ] If `mode: single-critic`, the `agent` field identifies the
      reviewing agent and `council_role: a5-critique` (or equivalent)
- [ ] `verdict` matches the §0 paragraph wording

## §6 Acceptance criteria

This critique is "good" when **all** of the following hold:

1. `inputs_audited` enumerates ≥1 doc and is not "TBD".
2. §0 verdict matches `verdict` in frontmatter.
3. §2 amendments table is non-empty if `verdict ∈ {GO-WITH-AMENDMENTS,
   NO-GO, PASS-WITH-FIXES}`; may be empty only if `verdict: GO`.
4. Severity counts in frontmatter (`counts.{blocking, major, minor,
   nit}`) sum to the §2 amendment count.
5. Every BLOCKER amendment carries an **ADOPT** recommendation OR a
   `verdict: NO-GO` justification.
6. The next-action (which downstream artefact must apply the
   amendments — a `b1-integration.md`, a follow-up spec, a PR) is
   named in §0.

## §7 Skill citation

Produced by `skills/skills/lean-review-council/SKILL.md@vX.Y.Z`. The
five-member roster (Σ / Φ / Ν / Λ / Ω) is at
`lean-review-council/SKILL.md §"Part 1 — The Five Council Members"`.
Topology selection follows
`lean-review-council/SKILL.md §"Part 4 — Council Topologies"`.
```

## 7.4 Diff summary

- **+** Frontmatter reconciles wave-doc shape with the SKILL Template 1
  (adds `wave/batch/shard/pin_head/mathlib_pin/cslib_pin/
  lean_toolchain/inputs_audited/verdict/counts`).
- **+** §2 amendments table canonicalised (was: ad-hoc per-wave
  `M-N` tables; v2 fixes the column set).
- **+** Bimodal template (`single-critic` vs `full-council`) — v1
  SKILL only describes full council; real wave critiques are nearly
  always single-critic.
- **+** §5 reproducibility checklist; §6 acceptance criteria.
- **=** Verdict vocabulary unified
  (`GO | GO-WITH-AMENDMENTS | NO-GO | PASS-WITH-FIXES`) from existing
  wave usage.
- **+** Severity-count cross-check between frontmatter and table body.

---

# 8. Template_RetroLog.md (Retro / wave closeout)

## 8.1 Current template gaps

There is no `docs/project/lean/docs/retro/` directory and no formal retro
template. The closest v1 is `lean-retro-methodology/SKILL.md` (451
LOC), which describes the **RETRO protocol** (Reconnaissance →
Establish → Triage → Review → Onboard), and the de-facto closeout
shape used in `wave-37/b5-closeout.md` and
`findings/wave-37-handoff.md`. Concrete gaps:

- **No artefact template at all.** Each wave closeout is rewritten
  from scratch; the column set of the metrics table drifts slightly
  between waves.
- **No "what we learned" section.** Closeouts capture metrics, gate
  verdicts, and carry-forward queues — but no **lessons learned**
  section that feeds back into AGENT.md, skills, or the
  zettelkasten. This is precisely the retro role.
- **No skill-evolution block.** When a wave reveals a new convention
  (e.g. W37's "cluster-umbrella convention",
  `wave-37/b5-closeout.md:89–91`), the convention is mentioned but
  never explicitly proposed as a SKILL.md edit or a ZK note. The
  retro template should make that handoff mandatory.
- **No reproducibility checklist.** Metrics are pasted but the script
  that produced them is not recorded.

## 8.2 Project evidence

1. `lean-retro-methodology/SKILL.md:14–93` — RETRO protocol described
   as a workflow; no per-retro artefact specified.
2. `wave-37/b5-closeout.md` (entire file) — de-facto retro shape:
   dispatch summary table (§1), gate verdicts (§2), cumulative metrics
   (§3), commit lineage (§4), carry-forward (§5), conventions locked
   (§6), procedure invocations (§7), verdict (§8).
3. `findings/wave-37-handoff.md:1–28` — handoff frontmatter pattern
   (`wave / batch / agent / shard / session / branch / pin_head /
   mathlib_pin / cslib_pin / lspec_pin / lean_toolchain / authored_at
   / authored_by / inputs_read / authority / status`).
4. `wave-37/b5-closeout.md:89–96` — "New convention locked at W37"
   is informative but not actionable; v2 retros should make this a
   formal SKILL/ZK edit proposal.
5. `lean-retro-methodology/SKILL.md §"Phase O — Onboard"` — RETRO
   ends with onboarding new collaborators; the retro artefact is the
   first thing a new agent reads, so its acceptance criteria must be
   strict.

## 8.3 Proposed v2 template

```markdown
---
kind: retro-log
id: RETRO-YYYYMMDD-WAVE-NN      # or RETRO-YYYYMMDD-PHASE-VII-NN
title: "<wave NN | phase VII Wave NN> close-out"
status: draft                    # draft | landed | superseded
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
authored_by: "<agent-id>"        # usually orchestrator
wave: 0
phase: ""                        # e.g. "Phase VII"
session: "<session-id>"
branch: "wave-3"
pin_head_at_close: "<short-sha>"
predecessor_close: "<short-sha>" # previous wave's close commit
mathlib_pin: "<short-sha>"
cslib_pin: "<short-sha>"
lspec_pin: "<short-sha>"
lean_toolchain: "leanprover/lean4:vX.Y.Z"
verdict: "COMPLETE | COMPLETE-WITH-DEFERRALS | INCOMPLETE | ABORTED"
inputs_read:
  - "<predecessor handoff>"
  - "<all b*-closeout.md in this wave>"
  - "<MASTER-PLAN-V<N>.md §<row>>"
skill: "skills/skills/lean-retro-methodology/SKILL.md@vX.Y.Z"
---

# RETRO-YYYYMMDD-WAVE-NN — <title>

## §1 Dispatch summary

| Batch / Shard | Mode | Verdict | Files touched | LOC |
|---|---|---|---:|---:|
| B1-a1 state-snapshot | DOC | LANDED | 1 | 196 |
| B1-a2 substrate-verified | DOC | LANDED | 1 | 203 |
| … | … | … | … | … |

Total source LOC delta this wave: **+N / -M**.
Total doc LOC delta this wave: **+N**.

## §2 Gate verdicts

| Gate | Definition | Verdict | Evidence |
|---|---|---|---|
| G-NN-1 | <gate text> | PASS / FAIL / N-A | `<sha or doc ref>` |
| G-NN-2 | … | … | … |

## §3 Cumulative metrics (at close)

| Metric | Predecessor close | This close | Δ |
|---|---:|---:|---:|
| `lake build Project` jobs | … | … | ± |
| Modules | … | … | ± |
| Declarations (total) | … | … | ± |
| Named declarations | … | … | ± |
| Source-scan axioms | … | … | ± |
| Whitelisted axioms | … | … | ± |
| `unexpected − whitelisted` (must = 0) | 0 | **0** ✅ | 0 |
| Forbidden tokens (`sorry`/`admit`) | 0 | **0** ✅ | 0 |

> Generated by `scripts/<axiom_audit.py | metrics script>` at
> `pin_head_at_close`. Command recorded in §7.

## §4 Wave commit lineage

| # | sha | Batch | One-line description |
|---:|---|---|---|
| 1 | `<sha>` | B1 | pre-flight bundle |
| 2 | `<sha>` | B2 | <description> |
| … | … | … | … |

## §5 Carry-forward to next wave

> Authoritative reference: `findings/wave-<NN+1>-handoff.md` (link
> when written).

- **OQ-W<NN+1>-<TAG>-01** (P1) — <one-line scope>
- **OQ-W<NN+1>-<TAG>-02** (P2) — <one-line scope>
- …

Resolved this wave (close OQ tickets here):
- OQ-W<NN>-<TAG>-XX → resolved at `<sha>` (`<batch>-<shard>.md`)

## §6 Lessons learned & skill evolution

> **v2-only section.** Mandatory. Every retro must list at least
> one of:
>
> 1. **New conventions** (free-form), and for each one:
>    - Proposed SKILL.md edit (path + diff sketch)
>    - Proposed AGENT.md addition (section + one-paragraph rule)
>    - Proposed ZK note (id + title)
> 2. **Anti-pattern observed** (free-form), and for each one:
>    - Counter-pattern recorded in a ZK note
>    - Skill/AGENT.md guardrail proposed
> 3. **Tooling delta** (script changes, new lake targets, etc.) with
>    paths.

Example:
- **Convention C-W37-1** — cluster-umbrella import-only modules.
  - SKILL.md edit: `skills/templates/Template_Index.md` add §X.
  - AGENT.md edit: §"DAG Build Layers" add row for L4 umbrellas.
  - ZK note: `ZK-2026-05-28-001 — cluster-umbrella convention`.

## §7 Reproducibility checklist

- [ ] `git log --oneline <predecessor_close>..<pin_head_at_close>`
      matches §4 lineage row-for-row
- [ ] Metrics in §3 reproduce from
      `python3 scripts/<axiom_audit.py>` at `pin_head_at_close`
- [ ] `lake build Project` GREEN at `pin_head_at_close`; job count
      equals §3 "lake build jobs"
- [ ] `grep -rn "sorry\|admit" Project/` returns 0 (or only matches
      inside string literals / comments documented in §3)
- [ ] Every gate row in §2 has a `<sha or doc ref>` that resolves
- [ ] Every OQ ticket in §5 is either an existing
      `findings/wave-NN-handoff.md` ticket or newly assigned here
      with a unique id

## §8 Acceptance criteria

This retro is "good" when **all** of the following hold:

1. Frontmatter `verdict` is set and matches §1 / §3 evidence.
2. §3 row `unexpected − whitelisted` = 0 OR `verdict` is one of
   `COMPLETE-WITH-DEFERRALS` / `INCOMPLETE` / `ABORTED` with rationale
   in §6.
3. §4 lineage is gap-free between `predecessor_close` and
   `pin_head_at_close`.
4. §5 carry-forward includes at least the resolution status of every
   OQ ticket inherited from the predecessor handoff.
5. §6 lessons-learned is non-empty (at least one item across
   Conventions / Anti-patterns / Tooling).
6. Every proposed SKILL/AGENT/ZK edit in §6 names a real path.
7. §7 reproducibility checklist is fully ticked OR has an explicit
   waiver inline citing the failing box.
8. The retro is paired with a `findings/wave-<NN+1>-handoff.md`
   linked in §5.

## §9 Skill citation

Produced by `skills/skills/lean-retro-methodology/SKILL.md@vX.Y.Z`.
The RETRO protocol phases (R/E/T/R/O) are defined at
`lean-retro-methodology/SKILL.md §"Part 1 — The RETRO Protocol"`.
Wave-level cumulative-metrics format is inherited from
`docs/project/lean/docs/refactor/wave-37/b5-closeout.md` (de-facto v1).
```

## 8.4 Diff summary

- **+** Promotes wave closeout from de-facto pattern to a templated
  artefact with formal frontmatter.
- **+** §6 "Lessons learned & skill evolution" — completely new,
  closes the gap that previously kept wave conventions trapped in
  closeout prose.
- **+** §7 reproducibility checklist — formerly implicit.
- **+** §8 acceptance criteria — including the project invariant
  `unexpected − whitelisted = 0` gate.
- **=** Adopts the column set of W37's `b5-closeout.md` (dispatch
  summary, gate verdicts, cumulative metrics, commit lineage,
  carry-forward) as the canonical shape.
- **+** Skill back-pointer + AGENT.md cross-link.

---

# Cross-template recommendations

The eight v2 templates above share enough structure that a small set
of cross-cutting rules is worth pulling out explicitly. These are
intended to be enforced by the future linter sketched in
`lab/design/04-template-v2-migration.md §5`.

## CR-1 — Shared frontmatter spine

Every workflow artefact (not just SKILL.md) MUST carry these YAML
keys, in this order:

```yaml
---
kind: <one of: mwe | pr | blueprint-run | zettel | spec | bisect |
              council-review | retro-log>
id: <KIND-YYYYMMDD-NNN or kind-specific scheme>
title: "<≤80 chars>"
status: <draft | active | landed | superseded | rejected>
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id or human>"
skill: "skills/skills/<slug>/SKILL.md@vX.Y.Z"
refs: []
---
```

Kind-specific keys (e.g. `toolchain`, `range`, `verdict`,
`pin_head`) are layered on top per template. Linter rule: missing any
spine key → WARN; missing `skill` back-pointer → ERROR.

## CR-2 — Pin triple as a first-class object

Any artefact that depends on a build state MUST carry the pin triple
under a `toolchain:` key (or, for wave/retro docs, as
`mathlib_pin / cslib_pin / lspec_pin / lean_toolchain` flat keys, for
back-compat with existing wave conventions):

```yaml
toolchain:
  lean: "leanprover/lean4:vX.Y.Z[-rcN]"
  mathlib_pin: "<short-sha>"
  cslib_pin: "<short-sha>"        # optional if not used
  lspec_pin: "<short-sha>"        # optional if not used
```

Templates that need it (v2): MWE, PR, Blueprint, Spec, Bisect,
Council, Retro. The only template that does NOT need it is
Zettelkasten (fleeting/literature notes may pre-date any build).

## CR-3 — Skill back-pointer is the linker

`skill: "skills/skills/<slug>/SKILL.md@vX.Y.Z"` is mandatory in every
artefact. This allows:
- Bidirectional auditing: a SKILL audit can list its outstanding
  artefacts; an artefact audit can identify deprecated producers.
- Version skew detection: when a SKILL bumps `metadata.version`,
  pre-existing artefacts under the old version are still
  reproducible.
- Routing in the gateway (`lean-gateway/SKILL.md`): the gateway can
  resolve any artefact to its producer skill in one hop.

## CR-4 — Embedded examples in the template body

Every v2 template SHOULD include at least one **inline embedded
example** for its non-trivial sections (the §2 reproduction in MWE,
the §2 change inventory + §4 build tail in PR, the §2 Lean signature
in Spec, the §2 amendments table in Council, the §3 metrics table in
Retro). The example is part of the template — agents copy-paste it
and replace placeholders.

This is a workflow concession: prose-only templates lead to drift;
copy-paste templates do not.

## CR-5 — Reproducibility checklist is always penultimate

Every v2 template ends with the same two-section pair:

- §N − 1: **Reproducibility checklist** (`- [ ] …` boxes; concrete
  shell commands or file:line refs)
- §N: **Acceptance criteria** (numbered "good when all of the
  following hold")

This is the single most consistent rule across the eight templates.
The reason to keep it last is that the reproducibility / acceptance
section is the **API** the artefact exposes to downstream consumers
(linter, gateway, council, future agents). Anything above the line is
content; this section is contract.

## CR-6 — Status vocabulary is shared

Across all eight templates:

| status         | meaning                                              |
|----------------|------------------------------------------------------|
| `draft`        | being written; do not consume                        |
| `active`       | in flight (multi-turn artefacts: ZK, blueprint runs) |
| `landed`       | complete; the artefact is now authoritative         |
| `superseded`   | replaced by a successor (`refs:` or kind-specific)  |
| `rejected`     | will not be pursued; preserved for context          |

Templates may add kind-specific synonyms (`filed` for PR, `merged` for
PR/Spec, `running` for Bisect) but MUST also map to the base
vocabulary.

## CR-7 — Reciprocal links

When a template carries a `predecessor`, `predecessors`, or
`supersedes` link to another artefact, that other artefact MUST carry
the reciprocal (`successor[s]` or `superseded_by`) — verified by the
linter. Currently violated by:
- ZK notes (v1) — fixed in Template_Zettelkasten v2 by adding
  `superseded_by`.
- Spec lifecycle (v1) — fixed in Template_Spec v2 by adding
  `successors`.
- Blueprint runs (v1) — fixed by `predecessor:` field in
  Template_Blueprint v2.

## CR-8 — Authority chain across templates

The eight templates form a small DAG:

```
MWE ─┐
     ├──► Bisect ──► PR
Spec ┘                ▲
                      │
Council ─► Retro ─────┘
                ▲
Zettelkasten ◄──┴── (lessons learned)
                ▲
Blueprint ──────┘ (annotations cite SPECs and ZK notes)
```

Edges are encoded via `refs:` and kind-specific link keys
(`mwe_ref`, `authority`, `predecessors`/`successors`,
`predecessor_close`/`pin_head_at_close`). Every PR's `§7 Authority
chain` should resolve to at least one of: Spec, MWE, Bisect, ZK,
Council, Retro. If a PR has no upstream artefact, that itself is a
finding worth a ZK note.

## CR-9 — Template lifecycle and ownership

These templates live at `docs/project/lean/skills/templates/Template_*.md`
alongside the existing 12 Lean-module templates. Each new template
file gets:

1. A `README.md` row in `skills/templates/README.md §"Template
   Navigator"` (the existing table at lines 22–35 must be extended).
2. A `metadata.version` semver-style header at the top of the file
   itself (e.g. `<!-- template version: 2.0.0; last_reviewed: YYYY-MM-DD -->`).
3. A back-pointer in the producing SKILL.md's `## See also` block.

When the eight `Template_*.md` files are created, the SKILL files
themselves should add a final `## See also` line:

- `lean-mwe/SKILL.md` → `Template_MWE.md`
- `lean-pr/SKILL.md` → `Template_PR.md`
- `lean-blueprint/SKILL.md` → `Template_Blueprint.md`
- `lean-zettelkasten/SKILL.md` → `Template_Zettelkasten.md` (and
  remove the duplicate Template 4 from `lean-review-council/SKILL.md`
  to fix the drift identified in §4.1)
- `lean-specification/SKILL.md` → `Template_Spec.md`
- `lean-bisect/SKILL.md` → `Template_Bisect.md`
- `lean-review-council/SKILL.md` → `Template_Council.md`
- `lean-retro-methodology/SKILL.md` → `Template_RetroLog.md`

## CR-10 — Rollout sequence

Suggested commit order, minimising mid-flight drift:

1. **Template_Zettelkasten.md** first — it is the substrate other
   templates link into; locking it stops further drift in
   `_index.md` / `_tags.md`.
2. **Template_Spec.md** + **Template_MWE.md** — these feed everything
   else (PRs, Bisects, Councils).
3. **Template_Bisect.md** — depends on MWE; produces input for PR.
4. **Template_PR.md** — depends on Spec, MWE, Bisect.
5. **Template_Council.md** — depends on Spec, PR (it critiques them).
6. **Template_RetroLog.md** — depends on Council, PR, Spec
   (closes out a wave's combined output).
7. **Template_Blueprint.md** — last; consumes annotated Spec output
   and may itself produce ZK notes about coverage gaps.

After landing each template, run the linter from
`lab/design/04-template-v2-migration.md §5` against the
corresponding skill to confirm the `## See also` back-pointer and the
`metadata.version` bump are present.

---

## Sources (recap)

All citations above use `path:line` format. The most heavily-cited
sources are:

- `skills/skills/lean-mwe/SKILL.md` (118 LOC) — v1 MWE workflow
- `skills/skills/lean-pr/SKILL.md` (93 LOC) — v1 PR conventions
- `skills/skills/lean-blueprint/SKILL.md` (677 LOC) — v1 blueprint
- `skills/skills/lean-zettelkasten/SKILL.md` (180 LOC) — v1 ZK
- `skills/skills/lean-specification/SKILL.md` (267 LOC) — v1 spec
- `skills/skills/lean-bisect/SKILL.md` (85 LOC) — v1 bisect
- `skills/skills/lean-review-council/SKILL.md` (1420 LOC) — v1 council
- `skills/skills/lean-retro-methodology/SKILL.md` (451 LOC) — v1 retro
- `docs/project/lean/docs/refactor/wave-37/` (entire wave) — de-facto
  artefact shapes
- `docs/project/lean/docs/refactor/findings/wave-37-handoff.md` —
  handoff frontmatter pattern
- `docs/project/lean/AGENT.md` §"Common Patterns and Pitfalls" + §"When
  Adding New Theorems" + §"Hard Constraints"
- `docs/project/lean/skills/lab/design/04-template-v2-migration.md` —
  sibling SKILL.md v2 contract; this document is the artefact-side
  complement

## What this document does NOT do

- Does not create any of the eight `Template_*.md` files. That is the
  next commit, after this proposal is reviewed.
- Does not edit any existing SKILL.md (`See also` back-pointers, fixing
  the council ↔ zettelkasten duplicate template). Those edits land
  with the corresponding new template file.
- Does not specify the linter (CR-1 / CR-7 enforcement). The linter
  proposal lives in `lab/design/04-template-v2-migration.md §5` and
  needs an extension to cover the new `kind:` values introduced here.
- Does not propose retiring any existing Template_* (Lean-module
  templates 1–12). The eight new templates are additive, sit alongside
  the existing 12, and are clearly distinguished by `kind:` in
  frontmatter and by README-Navigator grouping.
