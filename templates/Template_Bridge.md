# Template_Bridge.md — v2 upstream re-export façade Lean module

> **Status:** v2 production template (NEW — extracted from
> `_v2-proposals/proof-templates-v2.md §4`).
> Use this in **any** Lean 4 + Mathlib project for modules whose sole
> purpose is **re-exporting third-party symbols under a project-local
> namespace** with a documented pin and optional bridge-local
> primitives.
>
> No v1 predecessor — this template fills a gap in the existing set.

---

## 1. Why bridges exist (three reasons)

A bridge module exists for **one** of three reasons.  Pick yours and
state it in the file-doc top block:

1. **Naming.**  Project consumers want to write
   `<Project>.Bridges.X.Foo` instead of `<UpstreamLib>.Path.Foo`.  This
   keeps the import graph self-describing and lets future renames
   happen in the bridge instead of in every consumer.
2. **Stability.**  Insulate consumers from upstream renames, signature
   changes, or namespace reorganisations.  When upstream churns, only
   the bridge has to change.
3. **Gap-filling.**  Provide a project-local primitive that the
   upstream lacks **at the current pin**.  Track the upstream proposal
   in the file-doc so the local primitive can be retired when upstream
   lands.

---

## 2. When to use this template

Apply `Template_Bridge` when a module:

* Imports **one** specific upstream library file (`Mathlib.*`,
  `Cslib.*`, `Batteries.*`, a sibling project, …).
* Defines **only** `abbrev` / `notation` re-exports plus ≤ ~5
  bridge-local lemmas.
* Will be the **only allowed import path** for the upstream symbol
  from this project (enforced by `scripts/lean/bridge_validator.py`).

**Hard size limit.** A bridge that grows past ~60 LOC of theorem
content should be split: the bridge stays minimal; theorems move to
a [`Template_Theorem.md`](./Template_Theorem.md) file that *imports*
the bridge.

**Do NOT use** for:

* Intra-project re-exports → use [`Template_Index.md`](./Template_Index.md).
* Modules that compose upstream + project to prove a theorem →
  use [`Template_Theorem.md`](./Template_Theorem.md).
* Modules whose only API is project-internal types →
  use [`Template_DataModule.md`](./Template_DataModule.md).

---

## 3. Customisation checklist

| Placeholder        | Decide                                                              | Default                                                                  |
|--------------------|---------------------------------------------------------------------|--------------------------------------------------------------------------|
| `<Project>`        | Top-level namespace                                                 | Matches `package`                                                        |
| `<UpstreamLib>`    | Upstream library name                                               | E.g. `Mathlib`, `Cslib`, `Batteries`                                     |
| `<UpstreamName>`   | Module name under `<Project>.Bridges.`                              | Match the upstream concept (`Cslib.Logic.InferenceSystem` → `InferenceSystem`) |
| `<NarrowPath>`     | The **narrowest** upstream file you can import                      | NEVER `import Mathlib` / `import Cslib` umbrella                          |
| `<UpstreamType>`   | The exact upstream type-class / structure FQN                       | Verify via `#check` before committing                                    |
| Pin SHA            | 40-char commit SHA of upstream at time of write                     | Find in `lakefile.lean` `require`-block                                  |
| Migration tracking | Link to the upstream PR or local issue that will retire the bridge  | Skip if naming/stability-only                                            |

---

## 4. Mandatory metadata blocks

Every bridge must surface these four blocks in its file-doc:

* **Pin provenance** — Wave / batch tag, upstream-lib SHA, mathlib SHA,
  toolchain version.  Without this, a silent upstream rename appears as
  "missing symbol" at a future toolchain bump and there is no record of
  what was last verified.
* **Bridge namespace probe** — the **exact upstream FQN**, including
  the gotchas (`NOT cslib.X`, `NOT Cslib.X`, etc.).  This lets future
  readers grep upstream without chasing phantom symbols.
* **Re-export surface** — table of `local | upstream | notes` for every
  re-exported symbol.
* **Migration target** (only for gap-filling bridges) — what upstream
  change will retire the bridge-local primitives.

---

## 5. Full template

```lean
/-
Copyright (c) <YEAR> <Project> Authors. All rights reserved.
Released under Apache 2.0 license.

# <Project>.Bridges.<UpstreamName> — facade over `<UpstreamLib>.<Path>`

<One-paragraph statement of purpose.  Pick exactly ONE of:
 1. **Naming**: project consumers want `<Project>.Bridges.X` not `Upstream.X`.
 2. **Stability**: insulate consumers from upstream renames.
 3. **Gap-filling**: provide a project-local primitive that the upstream
    lacks at the current pin.>

## Pin provenance

- Wave    : W##-B##-a# (<short-tag>)   (or: ADR / issue / PR id)
- <upstream-lib> pin  : <40-char SHA>   (`lakefile.lean:<line>`)
- mathlib pin          : <40-char SHA>
- toolchain            : leanprover/lean4:v4.##.#-<channel>

## Bridge namespace probe

Document the **exact** upstream FQN here so future readers do not chase
phantom symbols.  Example:

> Upstream symbol is `Cslib.Logic.InferenceSystem`
> (NOT `cslib.InferenceSystem`, NOT `Cslib.InferenceSystem`).
> Class is two-sorted on tag `S` + judgment carrier `α`.

## Re-export surface

| Local name        | Upstream FQN                                  | Notes                          |
|-------------------|-----------------------------------------------|--------------------------------|
| `System`          | `Cslib.Logic.InferenceSystem`                 | `abbrev`, two-sorted           |
| `DerivableIn`     | `Cslib.Logic.InferenceSystem.DerivableIn`     | `abbrev`                       |
| `Admissible`      | *bridge-local*                                | upstream lacks at this pin     |

## Migration target

When upstream lands `<expected-PR>` (tracking
`docs/<your-tracking-path>`), delete the bridge-local `Admissible`
block and re-export the upstream version.
-/

import <UpstreamLib>.<NarrowPath>
-- Import the *narrowest* upstream file possible.  Pulling
-- `import Cslib` (umbrella) defeats the bridge's stability purpose.

set_option autoImplicit false

namespace <Project>.Bridges.<UpstreamName>
-- Canonical form: dotted `namespace`.  Avoid nested `namespace`
-- blocks (`namespace A / namespace B`) — they make grep harder.

universe u v

-- ## Re-exports (`abbrev` form, with explicit `_root_.` upstream paths)

abbrev System (S : Type u) (α : Type u) : Type _ :=
  _root_.<UpstreamLib>.<Path>.<UpstreamType> S α

abbrev DerivableIn (S : Type u) {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] (a : α) : Prop :=
  _root_.<UpstreamLib>.<Path>.<UpstreamType>.DerivableIn S a

-- ## Bridge-local primitives (only when upstream lacks them)

/-- Bridge-local <X> (no upstream `<X>` primitive at pin `<SHA-7>`).
    Tracking the upstream proposal:
    https://github.com/<owner>/<repo>/pull/<NNN>. -/
def Admissible (S : Type u) {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] (R : α → Prop) : Prop :=
  ∀ a, R a → DerivableIn S a

-- ## Minimal API for the bridge-local primitive
-- Keep this tiny: monotonicity, trivial-case, and any one or two
-- lemmas downstream actively consumes.  Avoid building a full theory
-- inside a bridge — that belongs in a Theorem module.

theorem Admissible.mono {S : Type u} {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] {R R' : α → Prop}
    (hRR' : ∀ a, R' a → R a) (hR : Admissible S R) : Admissible S R' :=
  fun a hRa => hR a (hRR' a hRa)

theorem Admissible.false {S : Type u} {α : Type u}
    [_root_.<UpstreamLib>.<Path>.<UpstreamType> S α] :
    Admissible S (fun _ : α => False) :=
  fun _ h => h.elim

end <Project>.Bridges.<UpstreamName>

/- ## See also
   * `skills/templates/Template_Theorem.md` — for proof-heavy modules that
     should consume *only* the bridge, never the upstream directly
   * `skills/scripts/lean/bridge_validator.py` — CI check that downstream
     modules import via the bridge, not the upstream directly
   * `<Project>/Bridges/Examples/MathlibPartialOrder.lean` — naming-only example
   * `<Project>/Bridges/Examples/CslibInference.lean` — gap-filling example
-/
```

---

## 6. Inline anti-patterns

```lean
-- ANTI-PATTERN: `export` from a bridge module.  Bridges are namespace-locked
-- on purpose — consumers must write `<Project>.Bridges.X.Foo` so that the
-- import graph is auditable.  Use `abbrev`, not `export`.

-- ANTI-PATTERN: importing the upstream umbrella (`import Cslib`,
-- `import Mathlib`).  Defeats the stability purpose.  Pin to the narrowest
-- upstream file that supplies the symbols you re-export.

-- ANTI-PATTERN: building a full theory on top of a bridge-local primitive.
-- If `Admissible` grows past ~5 lemmas, promote it to a Theorem module that
-- *imports* the bridge.  Bridges should stay ≤ ~60 LOC.

-- ANTI-PATTERN: bypassing the bridge from a consumer module.
-- `scripts/lean/bridge_validator.py` will catch direct upstream imports.

-- ANTI-PATTERN: forgetting the upstream SHA pin block.  Without it, a
-- silent upstream rename will appear as "missing symbol" at a future
-- toolchain bump and there will be no record of what was last verified.
```

---

## 7. Worked 12-LOC example (naming-only bridge)

```lean
namespace MyProj.Bridges.MathlibPartialOrder

universe u

/-- Re-export Mathlib's `PartialOrder` under the project namespace, pinned to
    Mathlib SHA <SHA-7>. -/
abbrev PartialOrder (α : Type u) : Type u := _root_.PartialOrder α

/-- Bridge-local convenience: pull `le_refl` to a fully-qualified form so that
    project-side proofs can write `MyProj.Bridges.MathlibPartialOrder.refl x`. -/
theorem refl {α : Type u} [PartialOrder α] (x : α) : x ≤ x := le_refl x

end MyProj.Bridges.MathlibPartialOrder
```

---

## 8. CI enforcement (`bridge_validator.py`)

A bridge is only as useful as its enforcement.  Ship a CI check that
fails if any non-bridge consumer imports the upstream directly:

```python
# scripts/lean/bridge_validator.py — sketch
"""Fail if any <Project>/*.lean (excluding <Project>/Bridges/*) imports
`<UpstreamLib>.*` directly. Bridges are the only legitimate consumer."""

import pathlib, re, sys

PROJECT_ROOT = pathlib.Path("<Project>")
BRIDGE_DIR   = PROJECT_ROOT / "Bridges"
UPSTREAM_RE  = re.compile(r"^\s*import\s+(<UpstreamLib>\.\S+)", re.M)

violations = []
for lean_file in PROJECT_ROOT.rglob("*.lean"):
    if BRIDGE_DIR in lean_file.parents:
        continue
    for match in UPSTREAM_RE.finditer(lean_file.read_text()):
        violations.append(f"{lean_file}: imports {match.group(1)} directly")

if violations:
    print("Bridge bypass detected:")
    for v in violations: print(f"  - {v}")
    sys.exit(1)
```

Wire it into CI as `bridge-validate` between `lake build` and your
linter.

---

## 9. What this template fills in the existing set

| vs. existing template          | Delta                                                                                                                |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------|
| [`Template_Index.md`](./Template_Index.md)        | `Template_Index` re-exports *sibling project* modules; `Template_Bridge` re-exports *third-party upstream* modules. Adds SHA pin, FQN-disambiguation block, and bridge-local primitives. |
| [`Template_Application.md`](./Template_Application.md) | `Template_Application` composes intra-project modules into theorems; `Template_Bridge` does not prove theorems beyond ≤ 5 monotonicity/triviality lemmas about bridge-local primitives. |

---

## 10. See also

* [`Template_Theorem.md`](./Template_Theorem.md) — the consumer-side template
* [`Template_DataModule.md`](./Template_DataModule.md) — for carrier-type modules a bridge might re-export
* [`Template_Index.md`](./Template_Index.md) — for intra-project re-exports
