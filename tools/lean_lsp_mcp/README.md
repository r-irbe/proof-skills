# lean-lsp-mcp -- Standalone Lean 4 & C FFI Model Context Protocol Server

`lean-lsp-mcp` is an open-source, standalone Model Context Protocol (MCP) server
providing AI coding agents (Claude Code, Cursor, Windsurf, Zed, Antigravity) with
high-performance tools for Lean 4 formal verification, offline navigation, and C FFI
inspection.

Strict 7-bit ASCII only.

---

## 1. Key Capabilities

1. **Interactive Proof State (`lean_plain_goal`)**: Queries `$/lean/plainGoal` via
   persistent `lake serve` child processes, formatting proof goals directly into
   markdown without file pollution.
2. **Expected Term Types (`lean_plain_term_goal`)**: Queries `$/lean/plainTermGoal`
   for exact sub-term typing and implicit argument inspection.
3. **Sub-millisecond Offline Navigation (`lean_jump_definition`)**: Direct binary
   JSON parsing of pre-compiled `.lake/build/ir/**/*.ilean` files, returning
   instant symbol definitions without waiting for compiler elaboration.
4. **Module Dependency Hierarchy (`lean_module_dag`)**: Fast forward (`imports`)
   and reverse (`importedBy`) DAG traversal, determining blast radius before edits.
5. **Cross-Language C FFI Navigation (`lean_c_ffi`)**: Bidirectional resolution
   between Lean `@[extern]` declarations and human-authored C FFI implementations,
   plus automatic injection of `lean --print-prefix` headers into `clangd`.
6. **Code Action Harvesting (`lean_code_actions`)**: Retrieval of suggested `Try this`
   proof scripts from search tactics (`exact?`, `simp?`, `grind?`).

---

## 2. Architecture

```text
+-----------------------------------------------------------------------------+
|                          lean-lsp-mcp ARCHITECTURE                          |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [ AI Host ] (Claude Code / Cursor / Windsurf / Antigravity)                |
|       |                                                                     |
|  stdio JSON-RPC (MCP Protocol)                                              |
|       v                                                                     |
|  [ lean-lsp-mcp Server ]                                                    |
|    |-- Request Dispatcher & Cache Manager                                   |
|    |-- .ilean Zero-Latency Indexer (Sub-millisecond offline symbol lookup)  |
|    |-- Lake Server Process Manager (Persistent `lake serve` session)        |
|    |-- Clangd C FFI Sysroot Bridge (Injects `lean --print-prefix` headers)  |
|       |                                                                     |
|       +---> Lean 4 Toolchain (`lake serve` / `elan`)                        |
|       +---> Clangd Language Server (`clangd`)                               |
|       +---> Project Filesystem (`.lake/build/ir/**/*.ilean`, `.olean`)      |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## 3. Tool Specifications

### `lean_plain_goal`
- **Arguments**:
  - `filePath` (string, required): Absolute or relative path to the `.lean` file.
  - `line` (number, 1-indexed): Cursor line position.
  - `character` (number, 1-indexed): Cursor column position.
- **Returns**: Markdown-rendered proof state with open goals, hypotheses, and types.

### `lean_plain_term_goal`
- **Arguments**:
  - `filePath` (string, required)
  - `line` (number)
  - `character` (number)
- **Returns**: Markdown-rendered expected term type at cursor position.

### `lean_jump_definition`
- **Arguments**:
  - `symbol` (string, required): Qualified symbol name (e.g. `Simplex.volume`).
  - `sourceFile` (string, optional): Context file for relative namespace resolution.
  - `preferOfflineIlean` (boolean, default `true`): Use sub-millisecond `.ilean` cache.
- **Returns**: Target file path, line number, and character range.

### `lean_module_dag`
- **Arguments**:
  - `moduleName` (string, required): Dot-separated module name (e.g. `EASCI.Simplex`).
  - `direction` (enum: `"imports" | "importedBy"`, default `"imports"`).
- **Returns**: List of direct and transitive module dependencies.

### `lean_c_ffi`
- **Arguments**:
  - `symbol` (string, required): Declaration name or C function identifier.
  - `action` (enum: `"jump_to_c" | "jump_to_lean" | "inspect_ir"`).
- **Returns**: Target location or compiled C99 IR excerpt.

---

## 4. Configuration Across Agent Hosts

### Claude Code (`~/.claude/claude_desktop_config.json` or project `.mcp.json`)
```json
{
  "mcpServers": {
    "lean-lsp": {
      "command": "node",
      "args": ["/absolute/path/to/tacit-mui/tools/lean_lsp_mcp/dist/index.js"],
      "env": {
        "PATH": "/home/radu/.elan/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### Cursor & Windsurf (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "lean-lsp": {
      "command": "node",
      "args": ["/absolute/path/to/tacit-mui/tools/lean_lsp_mcp/dist/index.js"]
    }
  }
}
```
