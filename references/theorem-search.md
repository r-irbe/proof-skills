# Lean theorem-search reference

Use this reference when a proof is blocked because the right theorem, tactic,
or API name is unknown. The goal is to turn search into a reproducible loop:
query broadly, narrow by type/namespace, verify inside Lean, and paste only the
verified proof term or tactic script into the final proof.

## Decision tree

| Situation | First tool | Then |
|---|---|---|
| You know a declaration or constant name | Loogle | Add a conclusion filter with `|-` |
| You know the mathematical idea in prose | LeanSearch | Verify candidates with `#check` and `exact?` |
| You have the current proof state | `exact?`, `apply?`, `rw?`, `simp?` | Paste the suggested term/script, not the search tactic |
| You know the statement shape | `#find` or Loogle pattern | Add type annotations to reduce noise |
| You know the namespace | `#check Namespace.name` and editor completion | Search sibling lemmas by name |

## Loogle query patterns

Loogle is structural search. Start with one broad filter, then intersect
filters with commas.

| Query form | Finds | Example |
|---|---|---|
| `Constant.name` | Lemmas mentioning a constant | `Filter.Tendsto` |
| `"name_part"` | Declarations with a name substring | `"monotone"` |
| `_ * (_ ^ _)` | Statement containing a shape | `_ * (_ ^ _)` |
| `?a + ?a` | Repeated metavariable pattern | `?a + ?a` |
| `|- conclusion` | Conclusion shape | `|- tsum _ = _ * tsum _` |
| `A, B, |- C` | Intersection of filters | `Nat.succ, "lt", |- _ < _` |
| `⊢ (_ : Type _)` | Definitions/types | `⊢ (_ : Type _)` |
| `⊢ (_ : Prop)` | Theorems/proofs | `⊢ (_ : Prop)` |

Workflow:

1. Copy the goal conclusion and replace unknown parts with `_`.
2. Add one relevant constant, such as `Finset.sum` or `Filter.Tendsto`.
3. Add a name substring only after the structural query is too broad.
4. Verify candidates with `#check` and a local Lean command.

## Lean-side search commands

```lean
-- Inspect a declaration.
#check Nat.add_comm
#check @Nat.add_comm

-- Search by statement pattern.
#find _ + _ = _ + _
#find (_ : Nat) + _ = _ + _

-- Search from a tactic state.
example : target := by
  exact?  -- exact term that closes the goal
  apply?  -- lemma that reduces the goal to subgoals
  rw?     -- rewrite lemma search
  simp?   -- emits a reproducible `simp only [...]`
```

Search commands are diagnostic. Remove `exact?`, `apply?`, `rw?`, `simp?`,
`#find`, and exploratory `#check` commands from committed proof files unless
they are inside a deliberate test fixture.

## Candidate verification protocol

For each promising theorem:

1. Run `#check theorem_name` or `#check @theorem_name`.
2. Try the candidate in the smallest local goal.
3. Run `lake env lean <file>` from the project root.
4. If the candidate closes a proof, replace the search command with the
   concrete term or tactic script it suggested.
5. If the candidate is reusable, record the namespace, lemma name, and example
   in the research output or project notes.

## Per-project notes (example shape)

A host project will typically pin its own conventions in its top-level
`AGENT.md` or equivalent. A representative shape (substitute your own
project slug for `<Project>`):

- Check `<Project>/Tactics.lean` before adding helper lemmas; reuse
  before extending.
- Prefer the project's declared tactic order. A common default that
  works well as a starting point: `grind`, `omega`, `norm_num`, explicit
  `simp only [...]`, `nlinarith`, `linarith`, `ring`, `positivity`,
  `field_simp`, `decide`, then `aesop`.
- `native_decide` is rarely a safe search shortcut. Prefer `decide`
  unless the project owner has documented an explicit exception (it
  trusts native code paths that bypass the kernel).
- Use `lake env lean`, not bare `lean`, so the search runs with the
  project toolchain, Lake environment, and dependencies.

## Sources

- Local project guidance: the host project's `AGENT.md` and its
  per-project `Tactics.lean` file (path varies by project).
- Local research: `../../research/lean4-ecosystem-tools.md`.
- External tools: Loogle, LeanSearch, Mathlib tactic documentation, and
  Mathlib source under `../../.lake/packages/mathlib/Mathlib/Tactic.lean`.
