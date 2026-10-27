#!/usr/bin/env python3
"""
scripts/lean/init_project.py
Bootstrap any existing or new Lean 4 / multi-prover project with proof-skills,
lean-analyzer, lean-lsp-mcp, and coding-agent configurations.

Usage:
  lean-skills init --target <dir> --mode submodule|global|weftd \
    --profile core,math,pack-altproof \
    --agents claude,gemini,cursor,pi,opencode,dsh,zed,weftd

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SKILLS_ROOT = HERE.parents[1]

SUPPORTED_AGENTS = (
    "claude",
    "gemini",
    "cursor",
    "pi",
    "opencode",
    "dsh",
    "zed",
    "weftd",
)

SUPPORTED_MODES = ("submodule", "global", "weftd")


def _default_lean_project_toml(
    project_name: str,
    mode: str,
    profiles: list[str],
    skills_rel_path: str,
) -> str:
    profile_list = ", ".join(f'"{p}"' for p in profiles)
    return f"""# lean-project.toml
# Project-level formalization configuration for proof-skills, lean-analyzer, and lean4-lsp-mcp.
# Strict 7-bit ASCII only (INV-001).

[project]
name = "{project_name}"
mode = "{mode}"
skills_path = "{skills_rel_path}"
profiles = [{profile_list}]
strict_zero_sorry = true
auto_implicit = false

[numeric_discipline]
mode = "standard"
scale_factor = 100
simplex_scale = 100
scaled_int_type = "Int"
in_simplex_pred = "InSimplex"
prefer_omega_over_linarith = true

[architecture.layers]
layer_0 = ["Foundations", "Tactics", "AltProof"]
layer_1 = ["Core", "Algebra", "Order"]
layer_2 = ["Analysis", "Dynamics", "Stochastic"]
layer_3 = ["Applications", "Verification"]
layer_4 = ["Tests", "Benchmarks"]

[[altproof.tactics]]
name = "alt_proof"
tactic = "alt_proof"
route = "general-automated-closer"
target_pattern = "general-automated-closer"
match_pattern = "alt_proof"
replacement = "alt_proof"
summary = "General multi-route automated closer"
estimated_heartbeats = 250

[[altproof.tactics]]
name = "sum_congr_ring"
tactic = "sum_congr_ring"
route = "finset-sum-linearity-pointwise-ring"
target_pattern = "finset-sum-linearity-pointwise-ring"
match_pattern = "Finset.sum"
replacement = "sum_congr_ring"
summary = "Normalize Finset.sum ring equality via Finset.sum_congr + ring"
estimated_heartbeats = 260

[[altproof.tactics]]
name = "finset_nonneg"
tactic = "finset_nonneg"
route = "finset-sum-nonneg-positivity"
target_pattern = "finset-sum-nonneg-positivity"
match_pattern = "0 <= Finset.sum"
replacement = "finset_nonneg"
summary = "Discharge 0 <= Finset.sum via Finset.sum_nonneg + positivity"
estimated_heartbeats = 240

[[altproof.tactics]]
name = "finset_mono"
tactic = "finset_mono"
route = "finset-sum-pointwise-monotonicity"
target_pattern = "finset-sum-pointwise-monotonicity"
match_pattern = "Finset.sum"
replacement = "finset_mono"
summary = "Discharge pointwise Finset.sum inequality via Finset.sum_le_sum"
estimated_heartbeats = 250

[[altproof.tactics]]
name = "bv_decide"
tactic = "bv_decide"
route = "bitvector-fixed-width-word"
target_pattern = "bitvector-fixed-width-word"
match_pattern = "BitVec"
replacement = "bv_decide"
summary = "Discharge bitvector / fixed-width word goals via bv_decide"
estimated_heartbeats = 180
"""


def _default_subst_table(project_name: str) -> dict[str, Any]:
    ns = project_name.replace("-", "_").title().replace("_", "")
    return {
        "schema_version": "1.0.0",
        "project": project_name,
        "substitutions": {
            "<Project>": ns,
            "<proj>": project_name.lower().replace("-", "_"),
            "<ScaledInt>": "Int",
            "<StandardScale>": "100",
            "<InSimplex>": "InSimplex",
            "<TacticsImport>": "AltProof.Tactics",
            "<DefaultArithTactic>": "omega",
            "<DefaultSumTactic>": "sum_congr_ring",
            "{{PROJECT_NAMESPACE}}": ns,
            "{{TACTICS_IMPORT}}": "AltProof.Tactics",
            "{{DEFAULT_ARITH_TACTIC}}": "omega",
            "{{DEFAULT_SUM_TACTIC}}": "sum_congr_ring",
        },
    }


def _mcp_server_entry(mode: str, skills_rel_path: str) -> dict[str, Any]:
    if mode == "submodule":
        mcp_bin = f"{skills_rel_path}/tools/lean-lsp-mcp/bin/lean-lsp-mcp.js"
        kz_path = f"{skills_rel_path}/kuzu/prover_knowledge.kz"
    else:
        mcp_bin = str(SKILLS_ROOT / "tools" / "lean-lsp-mcp" / "bin" / "lean-lsp-mcp.js")
        kz_path = str(SKILLS_ROOT / "kuzu" / "prover_knowledge.kz")

    return {
        "command": "node",
        "args": [mcp_bin],
        "env": {
            "PROVER_KNOWLEDGE_KZ": kz_path,
            "LOOMDB_RUNTIME_DIR": ".cache/proof-skills",
        },
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="ascii") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")


def init_project(
    target_dir: Path,
    mode: str = "submodule",
    profiles: list[str] | None = None,
    agents: list[str] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Bootstrap a target directory with proof-skills and agent configurations."""
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode '{mode}'. Choose from: {SUPPORTED_MODES}")

    target = target_dir.resolve()
    target.mkdir(parents=True, exist_ok=True)
    project_name = target.name or "lean-project"

    selected_profiles = profiles or ["core", "math", "pack-altproof"]
    selected_agents = [a.strip().lower() for a in (agents or ["claude", "gemini", "cursor", "pi", "weftd"]) if a.strip()]
    for a in selected_agents:
        if a not in SUPPORTED_AGENTS:
            raise ValueError(f"Unsupported agent '{a}'. Supported: {SUPPORTED_AGENTS}")

    skills_rel = "vendor/proof-skills" if mode == "submodule" else str(SKILLS_ROOT)
    created_files: list[str] = []

    # 1. lean-project.toml
    toml_path = target / "lean-project.toml"
    if force or not toml_path.exists():
        toml_path.write_text(
            _default_lean_project_toml(project_name, mode, selected_profiles, skills_rel),
            encoding="ascii",
        )
        created_files.append(str(toml_path.relative_to(target)))

    # 2. skills-overrides/subst_table.json
    subst_path = target / "skills-overrides" / "subst_table.json"
    if force or not subst_path.exists():
        _write_json(subst_path, _default_subst_table(project_name))
        created_files.append(str(subst_path.relative_to(target)))

    mcp_entry = _mcp_server_entry(mode, skills_rel)

    # 3. Root .mcp.json (used by Claude Code, Gemini, OpenCode, DSH, Zed)
    if any(a in selected_agents for a in ("claude", "gemini", "opencode", "dsh", "zed", "pi")):
        mcp_json_path = target / ".mcp.json"
        if force or not mcp_json_path.exists():
            _write_json(mcp_json_path, {"mcpServers": {"lean-lsp": mcp_entry}})
            created_files.append(".mcp.json")

    # 4. Agent-specific files
    if "claude" in selected_agents:
        claude_cfg = target / ".claude" / "settings.json"
        if force or not claude_cfg.exists():
            _write_json(
                claude_cfg,
                {
                    "skillsDir": f"{skills_rel}/skills",
                    "overridesDir": "skills-overrides",
                    "mcpServers": {"lean-lsp": mcp_entry},
                },
            )
            created_files.append(".claude/settings.json")

    if "gemini" in selected_agents:
        gemini_cfg = target / ".gemini" / "settings.json"
        if force or not gemini_cfg.exists():
            _write_json(
                gemini_cfg,
                {
                    "skillsDir": f"{skills_rel}/skills",
                    "mcpServers": {"lean-lsp": mcp_entry},
                },
            )
            created_files.append(".gemini/settings.json")

    if "cursor" in selected_agents:
        cursor_cfg = target / ".cursor" / "mcp.json"
        if force or not cursor_cfg.exists():
            _write_json(cursor_cfg, {"mcpServers": {"lean-lsp": mcp_entry}})
            created_files.append(".cursor/mcp.json")

    if "pi" in selected_agents:
        pi_cfg = target / ".pi" / "settings.json"
        if force or not pi_cfg.exists():
            _write_json(
                pi_cfg,
                {
                    "skills": [f"{skills_rel}/skills"],
                    "profiles": selected_profiles,
                    "mcpServers": {"lean-lsp": mcp_entry},
                },
            )
            created_files.append(".pi/settings.json")

    if "opencode" in selected_agents:
        oc_cfg = target / "opencode.json"
        if force or not oc_cfg.exists():
            _write_json(
                oc_cfg,
                {
                    "mcp": {"lean-lsp": {"type": "local", **mcp_entry}},
                    "skills_path": f"{skills_rel}/skills",
                },
            )
            created_files.append("opencode.json")

    if "dsh" in selected_agents:
        dsh_cfg = target / ".dsh" / "config.json"
        if force or not dsh_cfg.exists():
            _write_json(
                dsh_cfg,
                {
                    "skills_path": f"{skills_rel}/skills",
                    "mcp_servers": {"lean-lsp": mcp_entry},
                },
            )
            created_files.append(".dsh/config.json")

    if "zed" in selected_agents:
        zed_cfg = target / ".zed" / "settings.json"
        if force or not zed_cfg.exists():
            _write_json(
                zed_cfg,
                {
                    "context_servers": {
                        "lean-lsp": {
                            "command": {
                                "path": mcp_entry["command"],
                                "args": mcp_entry["args"],
                                "env": mcp_entry["env"],
                            }
                        }
                    }
                },
            )
            created_files.append(".zed/settings.json")

    if "weftd" in selected_agents or mode == "weftd":
        weft_cfg = target / ".weft" / "config.json"
        if force or not weft_cfg.exists():
            _write_json(
                weft_cfg,
                {
                    "plugin": "@r-irbe/weftd/lean",
                    "mode": mode,
                    "skillsRoot": skills_rel,
                    "profiles": selected_profiles,
                    "mcpServer": "lean-lsp",
                    "loomdbRuntimeDir": ".cache/proof-skills",
                    "gates": ["G0_PREFLIGHT", "G4_PROOF_FIDELITY", "G7_AXIOM_CLOSURE"],
                },
            )
            created_files.append(".weft/config.json")

    return {
        "ok": True,
        "target": str(target),
        "project": project_name,
        "mode": mode,
        "profiles": selected_profiles,
        "agents": selected_agents,
        "created_files": created_files,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap a Lean 4 / multi-prover project with proof-skills and agent configs"
    )
    parser.add_argument("--target", default=".", help="Target project directory (default: current directory)")
    parser.add_argument(
        "--mode",
        choices=list(SUPPORTED_MODES),
        default="submodule",
        help="Integration mode: submodule (vendor/proof-skills), global, or weftd (oh-my-agents plugin)",
    )
    parser.add_argument(
        "--profile",
        default="core,math,pack-altproof",
        help="Comma-separated skill profiles (default: core,math,pack-altproof)",
    )
    parser.add_argument(
        "--agents",
        default="claude,gemini,cursor,pi,weftd",
        help=f"Comma-separated coding agents ({','.join(SUPPORTED_AGENTS)})",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing config files")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args(argv)

    profiles = [p.strip() for p in args.profile.split(",") if p.strip()]
    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    res = init_project(Path(args.target), mode=args.mode, profiles=profiles, agents=agents, force=args.force)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=True))
    else:
        print(f"Bootstrapped project '{res['project']}' at {res['target']} (mode={res['mode']})")
        print(f"Created/updated {len(res['created_files'])} files: {', '.join(res['created_files'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
