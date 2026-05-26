# Lean 4 Module Dependency & Refactoring Guide

> Comprehensive reference for maintaining a clean, compilable Lean 4 project.
> Grounded in Mathlib4 conventions and generic Lean 4 project structures.

---

## 1. Module DAG: Why It Matters

### 1.1 Modules Must Form a DAG

Lean 4's module system requires that imports form a **Directed Acyclic Graph** (DAG).
This is a hard constraint — not a guideline:

```
✅  A → B → C         (acyclic: compiles)
❌  A → B → C → A     (cyclic: compilation error)
```

**Why?** Lean compiles modules in topological order. Each module's `.olean` (compiled
output) must be available before any module that imports it. A cycle means no valid
compilation order exists.

### 1.2 How Lake Detects Cycles

When you run `lake build`, Lake:

1. Parses every `import` statement across all `.lean` files
2. Constructs the full dependency graph
3. Attempts a **topological sort** of the graph
4. If topological sort fails → cycle detected → build error

The error message traces the cycle:
```
error: import cycle detected:
  MyProject.ModuleA → MyProject.ModuleB → MyProject.ModuleC → MyProject.ModuleA
```

### 1.3 What Happens When You Break the DAG

| Symptom | Cause |
|---------|-------|
| `import cycle detected` | Direct circular imports |
| `unknown identifier` after moving code | Broken import chain |
| Mysterious timeouts | Deep transitive import chains (not a cycle, but related) |
| `.olean` cache invalidation cascade | Editing a file low in the DAG |

### 1.4 Visualizing the Dependency Graph

Lake doesn't have a built-in graph export, but you can generate one:

```bash
# Quick Python script to generate a DOT graph from imports
find MyProject -name "*.lean" -exec grep -H "^import " {} \; | \
  sed 's|/|.|g; s|\.lean:import |" -> "|; s|^|"|; s|$|";|' | \
  (echo "digraph G {"; cat; echo "}") > deps.dot

# Render with Graphviz
dot -Tsvg deps.dot -o deps.svg
```

For this project, an example layered structure looks like:
```
Layer 0 (leaf):  Foundations  CoreTypes  Tactics
Layer 1:         BasicResults  Algebra  Predicates
Layer 2:         Dynamics  Stochastic  Composition
                 Application1  Application2
Layer 3 (top):   Stability
```

### 1.5 Layer Discipline

**Rule**: A module in Layer N may only import from Layers 0..N-1.
Never import from the same layer or above.

---

## 2. Module Splitting Patterns

### 2.1 When to Split a Module

Split when:
- **File exceeds ~800-1000 lines** — cognitive overhead, slow IDE feedback
- **Two logically distinct concerns** share a file (definitions vs. advanced theorems)
- **Build invalidation is too broad** — editing one theorem recompiles unrelated proofs
- **Import weight is high** — other modules import the file but only need a subset

Don't split prematurely — a 200-line focused file doesn't need splitting.

### 2.2 The `.Core` / `.Extensions` Pattern (the .Core / .Extensions style)

Many projects use this pattern:
```
MyProject/Catastrophe/
  Core.lean          -- Core definitions, structures, basic lemmas
  Singularities.lean -- Advanced theorems about singularities

MyProject/PhasePortrait/
  Core.lean          -- Core phase portrait types and operations
  Extensions.lean    -- Extended theorems, derived results

MyProject/Stochastic/
  Core.lean          -- Core stochastic CCV structures
  Information.lean   -- Information-theoretic results
```

**The umbrella file** re-imports everything:
```lean
-- MyProject/Catastrophe.lean
import MyProject.Catastrophe.Core
import MyProject.Catastrophe.Singularities
```

### 2.3 The Mathlib `.Defs` / `.Basic` / `.Instances` Pattern

Mathlib uses a finer-grained split for large theories:

| File | Contains | Imports |
|------|----------|---------|
| `Foo/Defs.lean` | Structures, inductive types, core `def`s | Minimal — only what definitions need |
| `Foo/Basic.lean` | Foundational lemmas, basic API | `Foo/Defs` |
| `Foo/Instances.lean` | Typeclass instances | `Foo/Defs`, possibly `Foo/Basic` |
| `Foo/Lemmas.lean` | Deeper theorems, advanced API | `Foo/Basic`, `Foo/Instances` |

**Key principle**: `Defs` has the fewest imports possible, because every file that
needs your types will transitively pull in everything `Defs` imports.

### 2.4 How to Extract Lemmas Without Breaking Imports

**Step-by-step**:

1. Create the new file (e.g., `MyProject/Foo/Advanced.lean`)
2. Add the necessary imports at the top of the new file
3. **Cut** (not copy) the lemmas/theorems from the original file
4. **Paste** into the new file, inside the same namespace
5. In the umbrella file (`MyProject/Foo.lean`), add `import MyProject.Foo.Advanced`
6. Run `lake build` to verify

### 2.5 Using `export` to Maintain API Compatibility

When you move `theorem bar` from `A.lean` to `B.lean`, old consumers break.
Use `export` to keep the old API working:

```lean
-- A.lean (after moving bar to B.lean)
import MyProject.B

-- Re-export bar so consumers of A still find it
export MyProject.B (bar)
```

**Important**: `export` in Lean 4 re-exports names from a *namespace*, not from
a module. The moved definition must be in a namespace that matches.

---

## 3. Import Organization

### 3.1 Narrow vs. Broad Imports

| Style | Example | Build Cost | Clarity |
|-------|---------|-----------|---------|
| **Narrow** | `import Mathlib.Analysis.NormedSpace.Basic` | Low | High |
| **Broad** | `import Mathlib.Tactic` | High | Low |

**Always prefer narrow imports.** Each unnecessary transitive import:
- Increases cold build time
- Widens the `.olean` cache invalidation surface
- Makes dependency reasoning harder

### 3.2 Tactical Imports

```lean
-- ❌ BAD: imports ALL of Mathlib's tactics + their dependencies
import Mathlib.Tactic

-- ✅ GOOD: import only what you need
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
```

For this project, `MyProject.Tactics` centralizes commonly-needed tactics — import
that instead of broad Mathlib imports.

### 3.3 `assert_not_exists` — Dependency Guards (Mathlib)

Mathlib defines a command `assert_not_exists` in `Mathlib.Tactic.AssertExists`
(the exact path varies by version). It's used as a **dependency guard** at the
top of files:

```lean
import Mathlib.Tactic.AssertExists

-- Guard: this file must NOT transitively import Topology
assert_not_exists TopologicalSpace

-- If someone adds an import that pulls in Topology, this line
-- will fail at compile time, catching the dependency violation early.
```

**Usage pattern**:
```lean
-- File: MyProject/Catastrophe/Core.lean
-- Place after imports, before any definitions

assert_not_exists MyProject.Stability  -- Core must not depend on Layer 3
```

This is Mathlib-specific — not built into Lean 4 itself. For non-Mathlib projects,
you can implement a minimal version:

```lean
/-- Assert that a name does not exist in the current environment.
    Used as a dependency guard: if an unwanted import pulls in a definition,
    this command will fail, alerting you to the dependency violation. -/
syntax "assert_not_exists " ident : command

elab_rules : command
  | `(assert_not_exists $id:ident) => do
    let env ← Lean.getEnv
    if env.contains id.getId then
      throwError m!"Dependency guard failed: '{id.getId}' exists. " ++
        "An unwanted import may have been added."
```

### 3.4 Transitive Import Costs

Every `import` is transitive. If `A` imports `B` and `B` imports `C`:
- Building `A` requires `C.olean` to exist
- Editing `C` invalidates both `B.olean` and `A.olean`
- `A` sees all declarations from both `B` and `C`

**Minimize the depth and breadth of your import tree.**

### 3.5 Finding Unused Imports

There is no official `lake shake` command (as of 2024-2025). Strategies:

1. **VSCode Lean extension**: Grays out unused imports in the editor
2. **Manual removal + rebuild**: Comment out suspect imports, run `lake build`
3. **Script approach**: Parse `.olean` dependency info vs. actual usage

```bash
# Quick check: comment out an import and see if build breaks
sed -i.bak 's/^import MyProject.Foo/-- import MyProject.Foo/' MyProject/Bar.lean
lake build MyProject.Bar  # if it succeeds, the import was unused
mv MyProject/Bar.lean.bak MyProject/Bar.lean  # restore if needed
```

---

## 4. Refactoring Workflow

### 4.1 Step-by-Step: Splitting a Large File

```
BEFORE:  MyProject/BigModule.lean (1200 lines)
AFTER:   MyProject/BigModule/Core.lean     (~400 lines, definitions)
         MyProject/BigModule/Theorems.lean  (~400 lines, main results)
         MyProject/BigModule/Advanced.lean  (~400 lines, advanced results)
         MyProject/BigModule.lean           (umbrella: 3 import lines)
```

**Procedure**:

```bash
# 1. Create the directory
mkdir -p MyProject/BigModule

# 2. Create Core.lean with the definitions
#    - Move structures, inductive types, basic defs
#    - Add minimal imports at the top
#    - Keep the same namespace

# 3. Create Theorems.lean
#    - import MyProject.BigModule.Core at the top
#    - Move main theorems here

# 4. Create Advanced.lean
#    - import MyProject.BigModule.Core (and .Theorems if needed)
#    - Move advanced results here

# 5. Replace BigModule.lean with umbrella imports:
cat > MyProject/BigModule.lean << 'EOF'
import MyProject.BigModule.Core
import MyProject.BigModule.Theorems
import MyProject.BigModule.Advanced
EOF

# 6. Validate
lake build
```

### 4.2 Moving Definitions Between Modules

1. **Identify dependencies**: What does the definition depend on? What depends on it?
2. **Move the definition** to the target module
3. **Add necessary imports** in the target module
4. **Update the source module** to import the target (if it still needs the definition)
5. **Use `export`** if you need backward compatibility
6. **Search and update consumers**:
   ```bash
   # Find all files that reference the moved definition
   grep -r "movedDefinitionName" MyProject/ --include="*.lean"
   ```
7. **Build and fix**: `lake build 2>&1 | head -50`

### 4.3 Updating Imports Across Consumers

```bash
# Find all files importing the old module
grep -rl "import MyProject.OldModule" MyProject/ --include="*.lean"

# Bulk update (use sed cautiously)
# Better: update manually, guided by `lake build` errors
```

### 4.4 Validation Checklist

```bash
# 1. Clean build (nuclear option — slow but definitive)
lake clean && lake build

# 2. Incremental build (fast, usually sufficient)
lake build

# 3. Build a specific module to isolate errors
lake build MyProject.PhasePortrait

# 4. Check for unused imports (manual)
# Comment out suspects, rebuild

# 5. Verify layer discipline
# Check that no Layer 1 module imports from Layer 2+
grep "^import" MyProject/Predicates.lean
# Should only show Layer 0 imports
```

---

## 5. Namespace Management

### 5.1 `namespace` vs `section` vs Bare Declarations

| Construct | Effect on Names | Variables | When to Use |
|-----------|----------------|-----------|-------------|
| `namespace Foo` | Prefixes declarations with `Foo.` | No auto-binding | Organizing API, grouping related defs |
| `section` | No name prefix | Auto-universalizes `variable`s | Sharing hypotheses across lemmas |
| Bare | Root namespace | None | Small utility files, one-off defs |

**Example — combining them**:
```lean
namespace MyProject.Catastrophe

section CuspProperties
variable {V : Type*} [NormedAddCommGroup V]
variable (cusp : CuspPoint V)

theorem cusp_bounded : ‖cusp.val‖ ≤ cusp.bound := by ...
theorem cusp_nonzero : cusp.val ≠ 0 := by ...

end CuspProperties

end MyProject.Catastrophe
```

### 5.2 `open ... in` vs Global `open`

```lean
-- ✅ PREFERRED: scoped open — affects only the next declaration
open Real in
theorem my_thm : exp 0 = 1 := by norm_num

-- ⚠️  USE SPARINGLY: global open — affects rest of file
open Real
-- Everything below sees Real's namespace unqualified

-- ✅ GOOD: selective open — only bring specific names
open Real (exp log sqrt)
```

**Rule of thumb**: Use `open ... in` for individual theorems. Use global `open` only
when nearly every declaration in the file needs it. Never use global `open` in
library files meant for wide import.

### 5.3 `protected` and `private` Modifiers

```lean
namespace Foo

-- private: visible only within this FILE
-- Not accessible from importing modules at all.
-- The internal name is mangled to prevent external use.
private def helperImpl : Nat := 42

-- protected: accessible only via fully-qualified name Foo.bar
-- Cannot be used as just `bar` even if `open Foo` is active.
-- Use for names that would clash (like Foo.zero, Foo.add).
protected def bar : Nat := 0

-- Regular: accessible as Foo.baz or just baz when Foo is opened
def baz : Nat := 1

end Foo

-- From another file:
open Foo
#check baz          -- ✅ works
#check bar          -- ❌ error (protected)
#check Foo.bar      -- ✅ works
#check helperImpl   -- ❌ error (private, wrong file)
```

### 5.4 `export` for Selective Re-export

```lean
-- Bring specific names from a namespace into the CURRENT namespace
-- (not just the current scope — it's permanent for this namespace)

namespace MyProject
export MyProject.Catastrophe.Core (CuspPoint CuspMorphism)
-- Now MyProject.CuspPoint works without opening CuspCatastrophe.Core
end MyProject
```

### 5.5 Avoiding Namespace Pollution

1. **Don't globally `open` heavily-populated namespaces** (like `Nat`, `List`, `Real`)
2. **Use `open ... in`** for per-declaration scoping
3. **Use `protected`** for names that would clash (`.zero`, `.one`, `.add`, etc.)
4. **Use `private`** for implementation details
5. **Prefer qualified names** in library code meant for wide import

---

## 6. Cross-Module Patterns

### 6.1 Referencing Theorems from Other Modules

Simply `import` the module and use the fully-qualified name:

```lean
import MyProject.Catastrophe.Core

-- Reference a theorem from the imported module
example : ... := MyProject.Catastrophe.Core.cusp_bounded ...

-- Or open the namespace for convenience
open MyProject.Catastrophe.Core in
example : ... := cusp_bounded ...
```

### 6.2 Typeclass Instances Across Modules

Typeclass instances are **globally visible** once their defining module is imported.
This is by design — instance resolution searches all imported instances.

```lean
-- In MyProject/Catastrophe/Core.lean
instance : Inhabited CuspPoint where
  default := ⟨0, by norm_num⟩

-- In ANY file that imports Core.lean:
-- This instance is automatically available for resolution.
-- No `open` needed — instances don't respect namespace boundaries.
```

**Controlling instance scope**:

| Modifier | Scope | Use When |
|----------|-------|----------|
| `instance` | Global (all importers) | Standard, always-valid instance |
| `local instance` | Current section only | Temporary override for a proof |
| `scoped instance` | Active when namespace is `open`ed | Domain-specific instance |

```lean
-- Only active when `open MyProject.Experimental` is in scope
namespace MyProject.Experimental
scoped instance : Add CuspPoint where
  add := experimentalAdd
end MyProject.Experimental
```

### 6.3 `@[simp]` Lemma Scoping and Side Effects

`@[simp]` lemmas are **globally propagated** through imports. This is powerful
but dangerous:

```lean
-- In Core.lean
@[simp] theorem cusp_zero : cusp 0 = default := by ...
-- ⚠️  This simp lemma is now active in EVERY file that imports Core.lean
```

**Best practices**:
- Only mark lemmas `@[simp]` if they are **universally useful simplifications**
- For domain-specific simplifications, use `scoped`:

```lean
namespace MyProject.CatastropheSimps
scoped attribute [simp] cusp_zero cusp_one cusp_add_comm
end MyProject.CatastropheSimps

-- Users opt in:
open scoped MyProject.CatastropheSimps in
theorem my_thm : ... := by simp  -- cusp_zero etc. are active here
```

- For one-off simplifications, use `simp only [...]` instead of `@[simp]`

**Common pitfall**: Adding a `@[simp]` lemma in a low-level module can cause
`simp` loops or unexpected behavior in distant, unrelated modules.

### 6.4 `@[ext]` Attribute Propagation

`@[ext]` generates extensionality lemmas and registers them for the `ext` tactic.
Like `@[simp]`, these propagate through imports:

```lean
@[ext]
structure CuspPoint where
  x : ℝ
  y : ℝ
-- Generates CuspPoint.ext : ∀ a b, a.x = b.x → a.y = b.y → a = b
-- This ext lemma is available in ALL importing modules
```

**Rule**: Apply `@[ext]` to the structure definition itself (in `Defs` or `Core`).
Don't scatter `@[ext]` lemmas across multiple files for the same type.

### 6.5 Summary: Attribute Scope Control

```
@[simp] lemma foo ...     -- Global: active everywhere after import
@[local simp] lemma foo   -- Section-local: active only in current section
scoped attribute [simp] foo -- Namespace-scoped: active only when namespace is opened

instance ...               -- Global: available to all importers
local instance ...         -- Section-local: current section only
scoped instance ...        -- Active only when namespace is opened

private def ...            -- File-local: invisible outside this file
protected def ...          -- Must use fully-qualified name (even with open)
```

---

## 7. Project-Specific Recommendations

### 7.1 Layer Architecture

Document the dependency layers in your `lakefile.lean` header comment and
maintain this invariant:

```
Layer 0 (leaf)  →  imports nothing from your project (only Mathlib/cslib)
Layer 1         →  imports only from Layer 0
Layer 2         →  imports from Layers 0-1
Layer 3 (top)   →  imports from Layers 0-2
```

### 7.2 Separate `lean_lib` Target for Foundations

Split Layer 0 into its own `lean_lib` target so editing higher-layer modules
does not invalidate the foundation `.olean` files:

```lean
lean_lib MyProjectFoundation where
  globs := #[
    .submodules `MyProject.Tactics,
    .submodules `MyProject.Foundations,
    .submodules `MyProject.Classifiers,
    .submodules `MyProject.Profiling
  ]
```

**Benefit**: Editing `MyProject.Predicates` (Layer 1) does NOT invalidate the
foundation `.olean` files. Lake skips recompiling them entirely.

### 7.3 When to Create a New Sub-Module

For modules that already have a `.Core` file:
- Add new files alongside `Core.lean` in the directory
- The umbrella file (e.g., `Catastrophe.lean`) auto-imports everything

For modules that are single files:
- Split when the file exceeds ~800 lines OR has distinct concerns
- Create a directory with the module name, add `Core.lean`, move the originals

### 7.4 Import Ordering Convention

Within each file, order imports as:
```lean
-- 1. Mathlib imports (alphabetical)
import Mathlib.Analysis.NormedSpace.Basic
import Mathlib.Topology.Basic

-- 2. Project foundation imports
import MyProject.Tactics

-- 3. Project peer imports (same or lower layer)
import MyProject.Catastrophe.Core
```

---

## 8. Quick Reference

### Build Commands
```bash
lake build                              # Full build
lake build MyProject.Stochastic         # Single module
lake build -j $(nproc)                  # Parallel build
lake clean && lake build                # Cold rebuild (slow)
lake exe cache get                      # Download Mathlib .olean cache
```

### Debugging Import Issues
```bash
# What does module X import (direct)?
head -20 MyProject/ModuleName.lean

# What files reference a definition?
grep -r "definitionName" MyProject/ --include="*.lean"

# What layer is a module in?
# Check lakefile.lean header comment

# Does removing an import break the build?
# Comment it out, run: lake build MyProject.ModuleName
```

### Refactoring Checklist
- [ ] Identify what to move and where
- [ ] Check nothing in the target creates a cycle
- [ ] Create new file(s) with correct imports
- [ ] Move code, keeping same namespace
- [ ] Update umbrella imports
- [ ] Add `export` for backward compatibility if needed
- [ ] Run `lake build`
- [ ] Grep for broken references
- [ ] Verify layer discipline is maintained
