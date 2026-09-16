#!/usr/bin/env node
// tools/lean_lsp_mcp/bin/lean-lsp-mcp.js
// Executable entrypoint for lean-lsp-mcp stdio server.
// Strict 7-bit ASCII only (INV-001).

import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import * as path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const entry = path.resolve(__dirname, "../src/index.ts");

const child = spawn(process.execPath, ["--experimental-strip-types", entry, ...process.argv.slice(2)], {
  stdio: "inherit",
});

child.on("exit", (code) => {
  process.exit(code ?? 0);
});
