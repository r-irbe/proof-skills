# Lean 4 Utility Scripts (`scripts/lean/`)

These scripts are project-agnostic and portable across any Lean 4 repository. Run from your Lean project root or pass `--root` / `--lean-dir` / `--project` explicitly.

## Core Audit, Quality & Gate Scripts

- `axiom_audit.py` - Generate and parse a Lean axiom contamination report (`--lean-dir`, `--project`, `--expected-axioms`).
- `bridge_validator.py` - Check that cross-module references are backed by explicit imports (`--lean-dir`, `--project`).
- `proof_quality.py` - Static proof-quality heuristics over tactic-mode and term-mode proofs (`--lean-dir`, `--output`). Self-tests: `proof_quality_test.py`.
- `tautology_scan.py` - Vacuous, tautological, and stubbed theorem scanner (`--lean-dir`, `--allowlist`).
- `deep_audit_census.py` - Deep audit census over `.lean` modules (`--root`, `--lean-dir`).
- `workflow_gate.py` - Multi-gate workflow verifier for Lean formalizations (`--root`, `--config`).
- `enforce_all.sh` - Master shell gate runner (`LEAN_ROOT`, `PROJECT_DIR`, `SKILLS_DIR`).
- `council_precheck.sh` - Pre-review council static check runner (`LEAN_ROOT`, `PROJECT_DIR`).
- `ecosystem_health.py` - Skill/template/reference/override health verifier (`--root`, `--skills-dir`, `--overrides-dir`).
- `retro_recon.py` - Retroactive audit reconnaissance & module dependency profiler (`--root`, `--lean-dir`).
- `metric_sync.py` - Theorem/declaration count synchronization verifier (`--root`, `--lean-dir`).
- `replay_verify.sh` - Fresh replay verification via `lean4checker` (`LEAN_ROOT`, `PROJECT_NAME`).
- `review_coverage.py` - Verify theorem/lemma review records exist (`--lean-dir`, `--reviews-dir`).
- `import_hygiene_advisory.py` - Report duplicate imports, missing local targets, and source-level cycles (`--root`, `--project`).
- `check-native-decide.sh` - Ensure each `native_decide` call has a nearby KEEP justification.
- `check_dag_layers.sh` - Enforce configured layer ordering for local imports.
- `dep_graph.sh` - Emit a DOT dependency graph, optionally clustered by layer config.
- `council_stv.py` - Meek Single Transferable Vote (STV) tallying for multi-agent review councils.

## Census, Harvesting & Build Helpers

- `lean_lint_harvest.sh` - Harvest warnings and lints from Lean files (uses `lean-harvest.js` or `awk` fallback).
- `olean_census.lean` - Fast `.olean` environment declaration & axiom census script (`lake env lean olean_census.lean <Module>`).
- `gen_clangd.sh` - Generate `.clangd` configuration pointing to active elan toolchain C headers.
- `api_gap_scan.py` - Scan local Lean definitions against Mathlib API conventions.
- `census_docstrings.py` - Measure `/-- ... -/` docstring coverage across Lean modules (`--root`, `--lean-dir`).
- `example_doc_coverage.py` - Audit `example` blocks for accompanying docstrings (`--self-test`).
- `census_naming.py` - Check identifier naming conventions against Mathlib snake_case / UpperCamelCase rules.
- `concat_corpus.py` - Concatenate a Lean corpus in topological dependency order (`--root`, `--lean-dir`).
- `formalization_breakdown.py` - Multi-wave architectural deconstruction & DAG extractor for Lean codebases.
- `launch_visualizer.py` - Unified launcher for the standalone Lean 4 Formalization DAG Visualizer (`--preset`, `--presets-file`).
- `ontology_tactic_advisor.py` - ITP ontology & tactic recommendation advisor.
- `templates_to_md.py` - Convert `templates/Template_*.lean` literate Lean files into Markdown.

## Blueprint, Zettelkasten & Report Pipeline

- `blueprint_probe.py` - Verify `\lean{...}` declarations and `\leanok` coverage in Lean blueprints (`--root`, `--lean-dir`, `--blueprint-src`).
- `blueprint_tex_guard.py` - Static defect linter for blueprint/paper LaTeX sources (`--self-test`).
- `expand_blueprint.py` - Expand blueprint LaTeX macros and inline theorem dependencies (`--root`).
- `blueprint_to_report.py` - End-to-end Blueprint-to-Report CLI (`{ingest,plan,illustrate,diff,expand,guard}`).
- `scaffold_lean_zettel.py` - Scaffold Zettelkasten concept/theorem notes from Lean modules (`--root`, `--lean-dir`).
- `zettelkasten_lint.py` - Lint Markdown Zettelkasten notes for structure and reciprocal links (`--zk-dir`).
- `harvest_lean_prose.py` - Extract prose, docstrings, and theorem headers from Lean files (`--root`, `--lean-dir`).
- `harvest_verso.py` - Extract structured documentation from Verso-annotated Lean modules (`--root`).

## AltProof Elegance & Kernel Optimization Suite (`scripts/lean/altproof/`)

- `altproof/cost_ranker.py` (`altproof_cost_ranker.py`) - Two-axis cost model (elegance + kernel cost).
- `altproof/legibility.py` (`altproof_legibility.py`) - Verbose-lean4 discourse renderability scorer.
- `altproof/tactic_dispatcher.py` (`altproof_tactic_advisor.py`) - Automated tactic selector and two-axis scorer (`--self-test`).
- `altproof/extraction_detector.py` - Delimiter-aware duplicated subterm and `have`-block extraction detector (v3).
- `altproof/algorithm_class_detector.py` - Detector for algorithmic substitution opportunities (DP, tail recursion, Finset folds).
- `altproof/candidate_evaluator.py` - Two-axis Pareto evaluator for algorithmic substitution candidates.
- `altproof/candidate_patcher.py` - Structural patcher and transformation receipt generator.
- `altproof/apply_and_verify.py` - Automated candidate patch verification loop.
- `altproof/apply_pilot.py` - Repeatable pilot pipeline with `lake build` gate and rollback on failure.
- `altproof/benchmark_runner.py` - Corpus-wide optimization benchmark runner.
- `altproof/corpus_report.py` - Whole-corpus elegance report suite generator.
- `altproof/have_cluster.py` - Cross-theorem `have`-type shape clustering across files.
- `altproof/kernel_cost_harness.py` - Kernel elaboration heartbeat and wall-clock profiler via `lake env lean`.
- `altproof/report_renderer.py` - Non-judgmental verbose-sketch report renderer.
- `altproof/route_definitions.py` & `altproof/gen_route_table.py` - Single source of truth and generator for `route-table.json`.
- `altproof/teaching_priority.py` - Teaching-priority ranker (extraction value x low legibility).
- `altproof/axiom_profiles.py` - Constructive vs classical axiom-profile classifier.
