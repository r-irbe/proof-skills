# Project Structure Overview

This document provides a comprehensive, layered map of the repository structure. For a quick conceptual overview, please refer to the `README.md`.

## Root Configurations and Contracts
*   `apm.yml`: The APM manifest holding package metadata (version, license, keywords).
*   `AGENT.md`: The strict, machine-readable contract defining HITL (Human-In-The-Loop) triggers, reversibility tiers, and dispatch precedence.
*   `ROLES.md`: The operational contract defining the multi-agent Stanford ACE Prover Swarm pipeline (Specifier, Prover, Auditor, Gardener).
*   `GUARDRAILS.md`: The dense, machine-readable taxonomy of measured agent failure classes.
*   `TAXONOMY.md`: Human-readable classification mapping skills into Kernel, Roles, and Facets.
*   `FACETS.md`: Human-readable catalog of the specialized domain facets (Math, AI, Governance).

## Skill Directories
*   `skills/`: Contains the first-party `SKILL.md` files representing individual capabilities (e.g., Lean compilation, proof tactics, PR hygiene).
*   `skills/_overrides/`: Holds local overrides and legacy redirect stubs for deprecated slugs.
*   `vendor/leanprover-skills/`: Pinned upstream git submodule providing transparent read-only fallback skills.

## Supplemental Knowledge and Templates
*   `templates/`: Lean module skeletons and workflow templates. Contains cross-template conventions (e.g., `00-CONVENTIONS.md`) and extracted artifacts like the `handoff_protocol.json`.
*   `references/`: This directory. Contains the deeply-layered technical context, evaluation histories, architectural schemas, and literature citations.
*   `zettelkasten/`: The repo-internal knowledge graph (fleeting, literature, permanent) that captures cross-session insights and tactic patterns.

## Tooling and Evaluation
*   `scripts/lean/`: Generic, project-agnostic Lean 4 scripts (axiom audits, bridge validators).
*   `scripts/lint/`: APM package validation tools.
*   `scripts/skill-audit/`: Scripts to check v2 conformance and handoff DAG integrity.
*   `scripts/eval/`: Tooling for deterministic runs, LLM-judge replays, and model calibration.
*   `scripts/elo/`: Glicko-2 leaderboard scripts and live match corpus ranking.
*   *See `scripts/README.md` for a detailed matrix of script purposes.*
