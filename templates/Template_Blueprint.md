# Template_Blueprint.md — Blueprint regeneration run-record

> **Status:** v2 production template (extracted from
> `_v2-proposals/workflow-templates-v2.md §3`).
> Use to record a `leanblueprint` regeneration (full or incremental).
> Each instantiation is a Markdown file under
> e.g. `docs/blueprint/runs/BP-YYYYMMDD-NNN.md`.

---

## 1. When to use

* You ran `lake build :blueprint` and/or `leanblueprint {pdf,web}` at
  a specific commit and want to record the inputs, outputs, and
  coverage delta.
* You want a stable run-record so the next run can be compared against
  this one (incremental mode tracks `predecessor` runs).

---

## 2. Template

````markdown
---
kind: blueprint-run
id: BP-YYYYMMDD-NNN
status: draft                # draft | landed | superseded
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "<agent-id>"
source:
  repo: "<owner>/<repo>"
  branch: "<branch>"
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

| Cluster                  | Modules covered | Decls annotated | Decls in scope | Coverage % | Δ vs predecessor |
|--------------------------|----------------:|----------------:|---------------:|-----------:|-----------------:|
| <cluster-1>              |               … |               … |              … |          … |                … |
| <cluster-2>              |               … |               … |              … |          … |                … |
| **Total**                | **N**           | **N**           | **N**          | **N%**     | **±N%**          |

## §3 Cross-cluster bridges highlighted

> Bridges receive distinguished colour-coding in the rendered graph.
> Enumerate every bridge present at this sha.

| Bridge id | LHS cluster | RHS cluster | Decl(s) | File:line |
|-----------|-------------|-------------|---------|-----------|
| BR-…      | …           | …           | `<decl>` | `<path>:L` |
| …         | …           | …           | …       | …         |

## §4 Pipeline stage report

| Stage    | Status | Duration | Notes                                              |
|----------|--------|---------:|----------------------------------------------------|
| ANALYZE  | ✅      |       Ns | M modules, E edges                                 |
| ANNOTATE | ✅      |       Ns | N annotators (fan-out), N new annotations          |
| SCAFFOLD | ✅      |       Ns | content.tex deltas: +N / -N                        |
| EXTRACT  | ✅      |       Ns | `lake build :blueprint` GREEN                      |
| RENDER   | ✅      |       Ns | `leanblueprint {pdf,web}` GREEN                    |

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

Produced by `skills/skills/lean-blueprint/SKILL.md@vX.Y.Z`.
````

---

## 3. What v2 adds over v1

* Run-record artefact concept (none in v1).
* Per-cluster coverage table with Δ vs predecessor.
* Bridge inventory cross-referenced to file:line.
* Pipeline stage report table with duration + GREEN/RED.
* §5 reproducibility checklist.

---

## 4. See also

* [`Template_RetroLog.md`](./Template_RetroLog.md) — wave closeouts cite the latest BP-id
* [`00-CONVENTIONS.md`](./00-CONVENTIONS.md) — frontmatter spine
* `_v2-proposals/workflow-templates-v2.md §3` — full gap analysis & evidence
