// tools/lean_lsp_mcp/tests/test_lean_lsp_mcp.mjs
// Unit and integration test suite for lean-lsp-mcp standalone module
// Strict 7-bit ASCII only (INV-001).

import assert from "node:assert";
import { spawn } from "node:child_process";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import {
    Lean4IleanIndex,
    LeanSysrootBridge,
    formatGoalAsMarkdown,
    McpServer,
    TOOL_DEFINITIONS,
} from "../src/index.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pkgRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(pkgRoot, "../../../../");

console.log("=== Testing lean-lsp-mcp (proof-skills) Suite ===");

// 1. formatGoalAsMarkdown
{
    const emptyGoal = formatGoalAsMarkdown("");
    assert.strictEqual(
        emptyGoal,
        "No active goals (proof complete or out of tactic scope).",
        "Empty goal string returns proof complete message"
    );

    const activeGoal = formatGoalAsMarkdown("case intro\nx : Nat\n|- x + 0 = x");
    assert.strictEqual(
        activeGoal,
        "```lean\ncase intro\nx : Nat\n|- x + 0 = x\n```",
        "Active goal formatted with lean markdown block"
    );
    console.log("  - formatGoalAsMarkdown: PASS");
}

// 2. LeanSysrootBridge
{
    const flags = LeanSysrootBridge.getIncludeFlags();
    assert(Array.isArray(flags), "Flags is an array");
    if (flags.length > 0) {
        assert(flags[0].startsWith("-I"), "First flag starts with -I");
        assert(flags.some(f => f.includes("include")), "Contains include directory");
    }
    const ffiReport = LeanSysrootBridge.inspectFFI(repoRoot, "nonexistent_extern");
    assert(ffiReport.includes("Lean 4 C FFI Environment"), "FFI report contains header");
    console.log("  - LeanSysrootBridge: PASS");
}

// 3. Lean4IleanIndex
{
    const index = new Lean4IleanIndex(repoRoot);
    index.refresh();
    const missing = index.lookupSymbol("NonExistentSymbol12345");
    assert.strictEqual(missing, null, "Missing symbol lookup returns null");

    const found = index.lookupSymbol("BoundedRewardKernel");
    if (found) {
        assert(found.filePath.includes(".lean"), "Found symbol has Lean source path");
        assert(typeof found.line === "number" && found.line > 0, "Found symbol has positive line number");
        console.log(`    * Found BoundedRewardKernel at ${found.filePath}:${found.line}:${found.col}`);
    }
    console.log("  - Lean4IleanIndex: PASS");
}

// 4. McpServer Protocol Handlers (In-memory)
{
    const server = new McpServer(repoRoot);

    const initRes = await server.handleMessage({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
            protocolVersion: "2024-11-05",
            capabilities: {},
            clientInfo: { name: "test-client", version: "1.0.0" },
        },
    });
    assert(initRes && initRes.result.serverInfo.name === "lean-lsp-mcp", "initialize response ok");

    const listRes = await server.handleMessage({
        jsonrpc: "2.0",
        id: 2,
        method: "tools/list",
    });
    assert(listRes && Array.isArray(listRes.result.tools) && listRes.result.tools.length === 5, "5 tools listed");

    server.dispose();
    console.log("  - McpServer Dispatch: PASS");
}

console.log("=== All proof-skills lean-lsp-mcp Tests Passed ===");
