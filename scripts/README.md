# Tooling and Validation Scripts

| Script | Purpose |
|---|---|
| `scripts/lint/apm_validate.py` | **Hard-gated in CI.** Checks the package stays a valid APM skill collection: manifest keys, required `name` + `description` per `SKILL.md`, directory-name match, no duplicates. |
| `scripts/skill-audit/check_conformance.py` | **Hard-gated in CI.** Checks v2 conformance, tier coverage, handoff DAG integrity, handbook links, inline `@skill` refs, and relative Markdown links. |
| `scripts/eval/run_eval.py` | Deterministic smoke runner for the 50-case suite. |
| `scripts/eval/calibrate_judge.py` | Pure replay calibration gate for known-bad judge corpora. |
| `scripts/eval/multi_model.py` | Converts persisted solver + judge artifacts into pairwise match rows. |
| `scripts/elo/glicko2.py` | Authoritative Glicko-2 leaderboard with uncertainty bands. |
| `scripts/elo/elo.py` | Legacy vanilla-ELO dashboard helper; do not use for release rankings. |
