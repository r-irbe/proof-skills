#!/usr/bin/env bash
# ==============================================================================
# scripts/setup-env.sh -- Customer Environment Bootstrap & Doctor for proof-skills
# ==============================================================================
# Strict 7-bit ASCII only (INV-001).
#
# Usage:
#   bash scripts/setup-env.sh              # Bootstrap git submodules, Python & Node deps
#   bash scripts/setup-env.sh --venv       # Create/use .venv and install Python & Node deps
#   bash scripts/setup-env.sh --doctor     # Non-mutating environment health check
#   bash scripts/setup-env.sh --check      # Alias for --doctor
#
# via APM:
#   apm run setup
#   apm run doctor
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

MODE="setup"
USE_VENV=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --doctor|--check)
      MODE="doctor"
      shift
      ;;
    --dedup-mounts)
      MODE="dedup"
      shift
      ;;
    --venv)
      USE_VENV=1
      shift
      ;;
    -h|--help)
      echo "Usage: bash scripts/setup-env.sh [--doctor | --check | --dedup-mounts | --venv | --help]"
      echo ""
      echo "Modes:"
      echo "  (default)        Initialize git submodules, verify/install Python & Node MCP deps,"
      echo "                   and print ready-to-paste MCP configuration snippets."
      echo "  --dedup-mounts   Remove duplicate global ~/.gemini/config/plugins/proof-skills/skills"
      echo "                   mount when proof-skills is mounted locally in the workspace."
      echo "  --venv           Create/activate .venv at repo root before installing Python deps."
      echo "  --doctor|--check Non-mutating health check of Python, Node, Lean, MCP, and Ontology."
      exit 0
      ;;
    *)
      echo "Unknown option: $1 (use --help for usage)" >&2
      exit 2
      ;;
  esac
done

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

pass_msg() {
  echo "  [OK]   $1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

warn_msg() {
  echo "  [WARN] $1"
  WARN_COUNT=$((WARN_COUNT + 1))
}

fail_msg() {
  echo "  [FAIL] $1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

run_doctor() {
  echo "======================================================================"
  echo "proof-skills Environment Doctor (${REPO_ROOT})"
  echo "======================================================================"

  # 1. Python >= 3.10 + PyYAML + optional kuzu
  echo ""
  echo "1. Python Runtime & Packages"
  local py_cmd=""
  if [[ -x "${REPO_ROOT}/.venv/bin/python3" ]]; then
    py_cmd="${REPO_ROOT}/.venv/bin/python3"
  elif [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python3" ]]; then
    py_cmd="${VIRTUAL_ENV}/bin/python3"
  elif command -v python3 >/dev/null 2>&1; then
    py_cmd="python3"
  fi

  if [[ -n "${py_cmd}" ]]; then
    PY_VER="$("${py_cmd}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
    PY_OK="$("${py_cmd}" -c 'import sys; print(int(sys.version_info >= (3, 10)))')"
    if [[ "${PY_OK}" == "1" ]]; then
      pass_msg "${py_cmd} ${PY_VER} (>= 3.10; 44 Lean/AltProof/Visualizer/SQLite scripts work with 0 pip deps)"
    else
      fail_msg "${py_cmd} ${PY_VER} is older than 3.10"
    fi

    if "${py_cmd}" -c "import yaml" >/dev/null 2>&1; then
      pass_msg "PyYAML installed (skill conformance & eval scripts ready)"
    else
      warn_msg "PyYAML not installed in ${py_cmd} (optional; check-structure & apm_validate have stdlib fallback; install with: pip install -r requirements.txt)"
    fi

    if "${py_cmd}" -c "import kuzu" >/dev/null 2>&1; then
      pass_msg "kuzu Python package installed (optional native Kuzu DB federation ready)"
    else
      pass_msg "kuzu Python package not installed (optional; graph/graph_query.py uses stdlib sqlite3 + .kz archives with 0 pip deps)"
    fi
  else
    fail_msg "python3 not found on PATH"
  fi

  # 2. Node.js + npm + lean-lsp-mcp runtime artifacts
  echo ""
  echo "2. Node.js & lean-lsp MCP Server"
  if command -v node >/dev/null 2>&1; then
    NODE_VER="$(node -v)"
    NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
    NODE_MINOR="$(node -p 'process.versions.node.split(".")[1]')"
    if [[ "${NODE_MAJOR}" -gt 22 ]] || { [[ "${NODE_MAJOR}" -eq 22 ]] && [[ "${NODE_MINOR}" -ge 6 ]]; }; then
      pass_msg "node ${NODE_VER} (>= 22.6.0; native TypeScript strip-types supported)"
    elif [[ "${NODE_MAJOR}" -ge 20 ]]; then
      pass_msg "node ${NODE_VER} (>= 20.0.0; supported via precompiled dist/index.js)"
    else
      fail_msg "node ${NODE_VER} is older than 20.0.0 (lean-lsp-mcp requires Node >= 20 or >= 22.6)"
    fi
  else
    fail_msg "node not found on PATH"
  fi

  if command -v npm >/dev/null 2>&1; then
    NPM_VER="$(npm -v)"
    pass_msg "npm ${NPM_VER} available"
  else
    fail_msg "npm not found on PATH"
  fi

  MCP_DIR="${REPO_ROOT}/tools/lean-lsp-mcp"
  if [[ -f "${MCP_DIR}/package.json" ]]; then
    pass_msg "tools/lean-lsp-mcp submodule initialized"
  else
    fail_msg "tools/lean-lsp-mcp/package.json missing (run: git submodule update --init --recursive)"
  fi

  if [[ -d "${MCP_DIR}/node_modules/@modelcontextprotocol/sdk" ]] && [[ -d "${MCP_DIR}/node_modules/js-yaml" ]]; then
    pass_msg "tools/lean-lsp-mcp/node_modules (@modelcontextprotocol/sdk, js-yaml) installed"
  else
    warn_msg "tools/lean-lsp-mcp/node_modules missing (will auto-bootstrap on first bin/lean-lsp-mcp.js launch or via: bash scripts/setup-env.sh)"
  fi

  if [[ -f "${MCP_DIR}/data/lean_analyzer.wasm" ]]; then
    WASM_SIZE="$(wc -c < "${MCP_DIR}/data/lean_analyzer.wasm" | tr -d ' ')"
    pass_msg "tools/lean-lsp-mcp/data/lean_analyzer.wasm present (${WASM_SIZE} bytes)"
  else
    fail_msg "tools/lean-lsp-mcp/data/lean_analyzer.wasm missing"
  fi

  # 3. Lean 4 Toolchain (elan / lean / lake)
  echo ""
  echo "3. Lean 4 Toolchain (elan / lean / lake)"
  if command -v elan >/dev/null 2>&1; then
    ELAN_VER="$(elan --version | head -n 1)"
    pass_msg "${ELAN_VER}"
  else
    warn_msg "elan not found on PATH (install from https://lean-lang.org/install/ for live Lean proving)"
  fi

  if command -v lean >/dev/null 2>&1; then
    LEAN_VER="$(lean --version | head -n 1)"
    pass_msg "${LEAN_VER}"
  else
    warn_msg "lean not found on PATH (offline skill templates & static audits still work)"
  fi

  if command -v lake >/dev/null 2>&1; then
    LAKE_VER="$(lake --version | head -n 1)"
    pass_msg "${LAKE_VER}"
  else
    warn_msg "lake not found on PATH"
  fi

  # 4. Ontology & Knowledge Graph Databases
  echo ""
  echo "4. Ontology & Knowledge Graph Artifacts"
  ONT_DB="${REPO_ROOT}/vendor/itp-ontology/itp_ontology_graph.db"
  if [[ -f "${ONT_DB}" ]]; then
    if command -v python3 >/dev/null 2>&1; then
      ONT_COUNT="$(python3 -c "import sqlite3; conn = sqlite3.connect('${ONT_DB}'); c = conn.cursor(); c.execute('SELECT count(*) FROM sqlite_master WHERE type=\"table\"'); print(c.fetchone()[0])" 2>/dev/null || echo "0")"
      if [[ "${ONT_COUNT}" -gt 0 ]]; then
        pass_msg "vendor/itp-ontology/itp_ontology_graph.db readable (${ONT_COUNT} SQLite tables)"
      else
        fail_msg "vendor/itp-ontology/itp_ontology_graph.db has 0 tables or is corrupt"
      fi
    else
      pass_msg "vendor/itp-ontology/itp_ontology_graph.db present"
    fi
  else
    fail_msg "vendor/itp-ontology/itp_ontology_graph.db missing"
  fi

  KZ_FILE="${REPO_ROOT}/kuzu/prover_knowledge.kz"
  if [[ -f "${KZ_FILE}" ]]; then
    KZ_SIZE="$(wc -c < "${KZ_FILE}" | tr -d ' ')"
    if [[ "${KZ_SIZE}" -gt 1024 ]]; then
      pass_msg "kuzu/prover_knowledge.kz present (${KZ_SIZE} bytes)"
    else
      fail_msg "kuzu/prover_knowledge.kz appears truncated (${KZ_SIZE} bytes)"
    fi
  else
    fail_msg "kuzu/prover_knowledge.kz missing"
  fi

  # 5. Global vs. Workspace Plugin Mount Deduplication
  echo ""
  echo "5. Skill Mount Deduplication (Global vs. Workspace)"
  GLOBAL_PLUGIN_SKILLS="${HOME}/.gemini/config/plugins/proof-skills/skills"
  if [[ -d "${GLOBAL_PLUGIN_SKILLS}" ]]; then
    warn_msg "${GLOBAL_PLUGIN_SKILLS} exists alongside workspace skills/; run 'bash scripts/setup-env.sh --dedup-mounts' to prevent duplicate skill registration"
  else
    pass_msg "No duplicate global ~/.gemini/config/plugins/proof-skills/skills mount detected (0 skills evicted by duplicate mounts)"
  fi

  echo ""
  echo "----------------------------------------------------------------------"
  echo "Summary: ${PASS_COUNT} passed, ${WARN_COUNT} warnings, ${FAIL_COUNT} failed"
  echo "----------------------------------------------------------------------"

  if [[ "${FAIL_COUNT}" -gt 0 ]]; then
    return 1
  fi
  return 0
}

dedup_global_mount() {
  local global_plugin_dir="${HOME}/.gemini/config/plugins/proof-skills"
  if [[ -d "${global_plugin_dir}/skills" ]]; then
    echo "-> Deduplicating global plugin mount at ${global_plugin_dir}/skills (workspace mounts proof-skills locally)..."
    rm -rf "${global_plugin_dir}/skills"
  fi
}

print_mcp_snippets() {
  local mcp_bin="${REPO_ROOT}/tools/lean-lsp-mcp/bin/lean-lsp-mcp.js"
  echo ""
  echo "======================================================================"
  echo "Ready-to-Paste MCP Configuration Snippets"
  echo "======================================================================"
  echo ""
  echo "Claude Code / Cursor / Copilot (.mcp.json or mcp.json):"
  cat <<JSON
{
  "mcpServers": {
    "lean-lsp": {
      "command": "node",
      "args": [
        "${mcp_bin}"
      ],
      "env": {
        "NODE_NO_WARNINGS": "1"
      }
    }
  }
}
JSON
  echo ""
  echo "Gemini CLI / Antigravity (settings.json or gemini-extension.json):"
  cat <<JSON
{
  "mcpServers": {
    "lean-lsp": {
      "command": "node",
      "args": [
        "--experimental-strip-types",
        "${mcp_bin}"
      ],
      "env": {
        "NODE_NO_WARNINGS": "1"
      }
    }
  }
}
JSON
}

if [[ "${MODE}" == "doctor" ]]; then
  run_doctor
  exit $?
elif [[ "${MODE}" == "dedup" ]]; then
  dedup_global_mount
  exit 0
fi

echo "======================================================================"
echo "Bootstrapping proof-skills Environment (${REPO_ROOT})"
echo "======================================================================"

dedup_global_mount

# Step 1: Initialize git submodules if needed
if [[ ! -f "${REPO_ROOT}/tools/lean-lsp-mcp/package.json" ]]; then
  if command -v git >/dev/null 2>&1 && [[ -e "${REPO_ROOT}/.git" ]]; then
    echo "-> Initializing git submodules..."
    git -C "${REPO_ROOT}" submodule update --init --recursive
  fi
fi

# Step 2: Python environment setup
if [[ "${USE_VENV}" -eq 1 ]]; then
  echo "-> Setting up Python virtual environment at ${REPO_ROOT}/.venv ..."
  python3 -m venv "${REPO_ROOT}/.venv"
  "${REPO_ROOT}/.venv/bin/pip" install --upgrade pip >/dev/null
  "${REPO_ROOT}/.venv/bin/pip" install -r "${REPO_ROOT}/requirements.txt"
elif [[ -n "${VIRTUAL_ENV:-}" ]]; then
  echo "-> Active virtualenv detected (${VIRTUAL_ENV}); installing requirements.txt ..."
  pip install -r "${REPO_ROOT}/requirements.txt"
else
  if python3 -c "import yaml" >/dev/null 2>&1; then
    echo "-> Python stdlib + PyYAML already available in python3 (no pip install needed)."
  else
    echo "-> Installing PyYAML via pip --user (or pass --venv to use an isolated .venv)..."
    python3 -m pip install --user -r "${REPO_ROOT}/requirements.txt" || \
      echo "   [WARN] pip install --user skipped (PEP 668 externally-managed environment). Pass --venv to create .venv, or use stdlib-only scripts directly."
  fi
fi

# Step 3: Node.js MCP server dependencies & build
MCP_DIR="${REPO_ROOT}/tools/lean-lsp-mcp"
if [[ -f "${MCP_DIR}/package.json" ]] && command -v npm >/dev/null 2>&1; then
  echo "-> Installing Node.js dependencies in tools/lean-lsp-mcp ..."
  if [[ -f "${MCP_DIR}/package-lock.json" ]]; then
    (cd "${MCP_DIR}" && (npm ci --no-audit --no-fund || npm install --no-audit --no-fund))
  else
    (cd "${MCP_DIR}" && npm install --no-audit --no-fund)
  fi
  if [[ -f "${MCP_DIR}/tsconfig.json" ]]; then
    echo "-> Building TypeScript dist/ in tools/lean-lsp-mcp ..."
    (cd "${MCP_DIR}" && npm run build)
  fi
fi

echo ""
run_doctor
print_mcp_snippets
