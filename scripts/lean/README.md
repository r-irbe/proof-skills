# Lean 4 utility scripts

These scripts are project-agnostic. Run from the directory containing your Lean project, or pass paths explicitly.

- `templates_to_md.py` — Convert `templates/Template_*.lean` literate Lean files into Markdown. Example: `python3 scripts/lean/templates_to_md.py --src-dir templates --dst-dir templates`.
- `check-native-decide.sh` — Ensure each `native_decide` call has a nearby KEEP justification. Example: `scripts/lean/check-native-decide.sh MyProject`.
- `axiom_audit.py` — Generate and parse a Lean axiom contamination report. Example: `python3 scripts/lean/axiom_audit.py --lean-dir MyProject --project MyProject --expected-axioms expected_axioms.json`.
- `bridge_validator.py` — Check that cross-module references are backed by explicit imports. Example: `python3 scripts/lean/bridge_validator.py --lean-dir MyProject --project MyProject`.
- `proof_quality.py` — Run static proof-quality heuristics over both tactic-mode (`:= by …`) and term-mode (`:= <term>`) proofs, including long proofs (with a structural branch-point signal), vacuity, `: True` stubs, term-mode truth witnesses (`trivial`/`⟨⟩`), bare `decide` (severity calibrated by whether the target is a concrete closed proposition), and reflexive `rfl` candidates, then write a Markdown report. The declaration parser recognises `example` and the `private`/`protected`/`public`/`scoped`/`noncomputable` modifiers. Example: `python3 scripts/lean/proof_quality.py --lean-dir MyProject --output proof_quality.md`. Acceptance probes: `python3 scripts/lean/proof_quality_test.py`.
- `import_hygiene_advisory.py` — Report duplicate imports, missing local targets, and source-level cycles. Example: `python3 scripts/lean/import_hygiene_advisory.py --root MyProject --project MyProject --markdown`.
- `review_coverage.py` — Verify theorem/lemma review records exist. Example: `python3 scripts/lean/review_coverage.py --lean-dir MyProject --reviews-dir reviews`.
- `zettelkasten_lint.py` — Lint Markdown Zettelkasten notes for structure and links. Example: `python3 scripts/lean/zettelkasten_lint.py --zk-dir zettelkasten`.
- `check_dag_layers.sh` — Enforce configured layer ordering for local imports. Example: `scripts/lean/check_dag_layers.sh MyProject layer_config.json`.
- `dep_graph.sh` — Emit a DOT dependency graph, optionally clustered by layer config. Example: `scripts/lean/dep_graph.sh --project MyProject MyProject layer_config.json | dot -Tsvg -o deps.svg`.
