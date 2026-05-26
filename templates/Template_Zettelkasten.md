# Template_Zettelkasten.md — Zettelkasten note artefact

> **Status:** v2 production template (extracted from
> `_v2-proposals/workflow-templates-v2.md §4`).
> Use for **every** note in `zettelkasten/{fleeting,literature,permanent}/`.
> The `type` field in frontmatter selects the maturity level; the
> acceptance criteria in §5 tighten as the note matures.

---

## 1. When to use

* You captured an idea, observation, pitfall, or convention worth
  recording (`type: fleeting`).
* You read an external paper / blog / Zulip thread and want to record
  what's relevant (`type: literature`).
* You synthesised one or more fleeting/literature notes into a
  reusable, durable insight (`type: permanent`).

**Promotion path.** `fleeting → literature → permanent` is the
authoring lifecycle.  Each maturity step adds reproducibility
requirements (see §5).

---

## 2. Template

````markdown
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
tags: ["tag1", "tag2"]   # must be subset of zettelkasten/_tags.md
links:
  related:        ["ZK-…"]
  supports:       ["ZK-…"]
  contradicts:    ["ZK-…"]
  supersedes:     ["ZK-…"]   # this note replaces these
  superseded_by:  ["ZK-…"]   # this note is replaced by these (RECIPROCAL of `supersedes`)
skill: "skills/skills/lean-zettelkasten/SKILL.md@vX.Y.Z"
---

# ZK-YYYYMMDD-NNN — <title>

## §1 Content

One paragraph.  One idea.  Concrete enough that another agent reading
this in isolation can act on it.

## §2 Evidence

Verbatim Lean diagnostic, axiom trace, code snippet, or external
citation.  Quote rather than paraphrase.  Include file:line refs.

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
5. The note has been referenced by ≥ 2 other notes OR cited by ≥ 1
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
````

---

## 3. What v2 adds over v1

* Strict YAML frontmatter (replaces `## H2` field rows).
* `superseded_by` reciprocal link (was missing).
* `subtype` enum aligned to the directory tree.
* §4 reproducibility gated by type.
* §5 per-type acceptance criteria (graduation gates).
* Tag-set discipline (subset of `_tags.md`).

---

## 4. See also

* [`../zettelkasten/_index.md`](../zettelkasten/_index.md) — ZK navigator
* [`../zettelkasten/_tags.md`](../zettelkasten/_tags.md) — tag vocabulary
* [`Template_MWE.md`](./Template_MWE.md) — bug captures often graduate into ZK notes
* [`00-CONVENTIONS.md`](./00-CONVENTIONS.md) — frontmatter spine
* `_v2-proposals/workflow-templates-v2.md §4` — full gap analysis & evidence
