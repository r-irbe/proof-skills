// tools/lean_lsp_mcp/src/index.ts
// Standalone Model Context Protocol (MCP) server for Lean 4 & C FFI.
// Strict 7-bit ASCII only (INV-001).

import * as fs from "node:fs";
import * as path from "node:path";
import { execSync, spawn, ChildProcess } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

export interface IleanSymbolEntry {
  filePath: string;
  line: number;
  col: number;
  endLine?: number;
  endCol?: number;
  module?: string;
  name?: string;
  kind?: string;
}

export interface IleanFile {
  version?: number;
  module?: string;
  directImports?: Array<[string, boolean, boolean, boolean]> | string[];
  decls?: Record<string, number[]>;
  entries?: Record<string, { line: number; col: number; endLine?: number; endCol?: number }>;
}

export interface McpToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface McpRequest {
  jsonrpc: "2.0";
  id?: number | string | null;
  method: string;
  params?: any;
}

export interface McpResponse {
  jsonrpc: "2.0";
  id: number | string | null;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export const TOOL_DEFINITIONS: McpToolDefinition[] = [
  {
    name: "lean_goal",
    description: "Queries interactive Lean 4 tactic proof state at cursor position ($/lean/plainGoal)",
    inputSchema: {
      type: "object",
      properties: {
        filePath: { type: "string", description: "Absolute or relative path to the .lean file" },
        line: { type: "integer", description: "1-based line number" },
        col: { type: "integer", description: "1-based column number" },
        character: { type: "integer", description: "Synonym for col" },
      },
      required: ["filePath", "line"],
    },
  },
  {
    name: "lean_term_goal",
    description: "Queries expected term type under cursor ($/lean/plainTermGoal)",
    inputSchema: {
      type: "object",
      properties: {
        filePath: { type: "string", description: "Absolute or relative path to the .lean file" },
        line: { type: "integer", description: "1-based line number" },
        col: { type: "integer", description: "1-based column number" },
        character: { type: "integer", description: "Synonym for col" },
      },
      required: ["filePath", "line"],
    },
  },
  {
    name: "lean_lookup_symbol",
    description: "Offline zero-latency symbol lookup and jump-to-definition via pre-compiled .ilean cache",
    inputSchema: {
      type: "object",
      properties: {
        symbol: { type: "string", description: "Lean declaration name (e.g. RealQ.bellmanOp or BoundedRewardKernel)" },
        preferOfflineIlean: { type: "boolean", description: "Use fast .ilean cache (default true)" },
      },
      required: ["symbol"],
    },
  },
  {
    name: "lean_module_hierarchy",
    description: "Forward and reverse module import dependency hierarchy analysis",
    inputSchema: {
      type: "object",
      properties: {
        moduleName: { type: "string", description: "Full module name (e.g. EASCI.ReinforcementLearning.Core)" },
        direction: { type: "string", enum: ["imports", "importedBy", "both"], description: "Direction of dependency traversal (default: both)" },
      },
      required: ["moduleName"],
    },
  },
  {
    name: "lean_c_ffi_inspect",
    description: "Cross-language C FFI inspector: Lean @[extern] declarations, C implementations, and Lean sysroot include flags",
    inputSchema: {
      type: "object",
      properties: {
        externName: { type: "string", description: "Optional Lean @[extern] identifier or C function name" },
        action: { type: "string", enum: ["sysroot", "inspect", "jump_to_c"], description: "FFI inspection action (default: inspect)" },
      },
    },
  },
];

export class Lean4IleanIndex {
  private projectRoot: string;
  private cache: Map<string, IleanFile> = new Map();
  private symbolIndex: Map<string, IleanSymbolEntry> = new Map();
  private moduleImportsMap: Map<string, string[]> = new Map();
  private moduleImportedByMap: Map<string, string[]> = new Map();

  constructor(projectRoot: string) {
    this.projectRoot = projectRoot;
  }

  public refresh(): void {
    this.cache.clear();
    this.symbolIndex.clear();
    this.moduleImportsMap.clear();
    this.moduleImportedByMap.clear();

    const candidateRoots = [
      path.join(this.projectRoot, ".lake", "build", "lib", "lean"),
      path.join(this.projectRoot, ".lake", "build", "ir"),
      path.join(this.projectRoot, "docs", "easci", "lean", ".lake", "build", "lib", "lean"),
      path.join(this.projectRoot, "docs", "easci", "lean", ".lake", "build", "ir"),
    ];

    const visitedDirs = new Set<string>();
    for (const root of candidateRoots) {
      if (fs.existsSync(root) && !visitedDirs.has(root)) {
        visitedDirs.add(root);
        this.scanDir(root);
      }
    }

    // Build reverse importedBy graph
    for (const [mod, imps] of this.moduleImportsMap.entries()) {
      for (const imp of imps) {
        let list = this.moduleImportedByMap.get(imp);
        if (!list) {
          list = [];
          this.moduleImportedByMap.set(imp, list);
        }
        if (!list.includes(mod)) {
          list.push(mod);
        }
      }
    }
  }

  private scanDir(dir: string): void {
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          this.scanDir(fullPath);
        } else if (entry.isFile() && entry.name.endsWith(".ilean")) {
          this.loadIlean(fullPath);
        }
      }
    } catch {
      // Ignore unreadable directories
    }
  }

  private loadIlean(filePath: string): void {
    try {
      const raw = fs.readFileSync(filePath, "utf-8");
      const parsed: IleanFile = JSON.parse(raw);
      this.cache.set(filePath, parsed);

      const moduleName = parsed.module || "";

      // Derive source file path
      let sourceFile = "";
      if (moduleName) {
        const relLean = moduleName.replace(/\./g, "/") + ".lean";
        const candidate1 = path.join(this.projectRoot, "docs", "easci", "lean", relLean);
        const candidate2 = path.join(this.projectRoot, relLean);
        if (fs.existsSync(candidate1)) {
          sourceFile = path.relative(this.projectRoot, candidate1);
        } else if (fs.existsSync(candidate2)) {
          sourceFile = path.relative(this.projectRoot, candidate2);
        }
      }
      if (!sourceFile) {
        sourceFile = path.relative(this.projectRoot, filePath);
      }

      // 1. Process decls: Record<string, number[]>
      if (parsed.decls && typeof parsed.decls === "object") {
        for (const [sym, coords] of Object.entries(parsed.decls)) {
          if (Array.isArray(coords) && coords.length >= 2) {
            const line = ((coords[4] !== undefined ? coords[4] : coords[0]) ?? 0) + 1;
            const col = ((coords[5] !== undefined ? coords[5] : coords[1]) ?? 0) + 1;
            const endLine = coords[2] !== undefined ? coords[2] + 1 : undefined;
            const endCol = coords[3] !== undefined ? coords[3] + 1 : undefined;

            const entry: IleanSymbolEntry = {
              filePath: sourceFile,
              line,
              col,
              endLine,
              endCol,
              module: moduleName,
            };
            if (!this.symbolIndex.has(sym)) {
              this.symbolIndex.set(sym, entry);
            }
            if (moduleName && !sym.startsWith(moduleName)) {
              const fullSym = `${moduleName}.${sym}`;
              if (!this.symbolIndex.has(fullSym)) {
                this.symbolIndex.set(fullSym, entry);
              }
            }
          }
        }
      }

      // 2. Process entries (fallback format)
      if (parsed.entries && typeof parsed.entries === "object") {
        for (const [sym, pos] of Object.entries(parsed.entries)) {
          if (!this.symbolIndex.has(sym)) {
            this.symbolIndex.set(sym, {
              filePath: sourceFile,
              line: pos.line,
              col: pos.col,
              endLine: pos.endLine,
              endCol: pos.endCol,
              module: moduleName,
            });
          }
        }
      }

      // 3. Process directImports
      if (moduleName && parsed.directImports && Array.isArray(parsed.directImports)) {
        const imps: string[] = [];
        for (const item of parsed.directImports) {
          if (Array.isArray(item) && typeof item[0] === "string") {
            imps.push(item[0]);
          } else if (typeof item === "string") {
            imps.push(item);
          }
        }
        this.moduleImportsMap.set(moduleName, imps);
      }
    } catch {
      // Ignore unparseable or transient build lockfiles
    }
  }

  public lookupSymbol(symbol: string): IleanSymbolEntry | null {
    if (this.symbolIndex.size === 0) {
      this.refresh();
    }
    const exact = this.symbolIndex.get(symbol);
    if (exact) return exact;

    // Suffix match fallback (e.g. searching "bellmanOp" finds "RealQ.bellmanOp")
    for (const [k, v] of this.symbolIndex.entries()) {
      if (k.endsWith("." + symbol)) {
        return v;
      }
    }
    return null;
  }

  public getModuleImports(moduleName: string): string[] {
    if (this.moduleImportsMap.size === 0) {
      this.refresh();
    }
    return this.moduleImportsMap.get(moduleName) || [];
  }

  public getModuleImportedBy(moduleName: string): string[] {
    if (this.moduleImportedByMap.size === 0) {
      this.refresh();
    }
    return this.moduleImportedByMap.get(moduleName) || [];
  }

  public getAllIndexedSymbolsCount(): number {
    return this.symbolIndex.size;
  }
}

export class LeanSysrootBridge {
  private static cachedPrefix: string | null = null;

  public static getPrefix(): string | null {
    if (!this.cachedPrefix) {
      try {
        const out = execSync("lean --print-prefix", { encoding: "utf-8" }).trim();
        this.cachedPrefix = out;
      } catch {
        return null;
      }
    }
    return this.cachedPrefix;
  }

  public static getIncludeFlags(): string[] {
    const prefix = this.getPrefix();
    if (!prefix) return [];

    const includeDir = path.join(prefix, "include");
    const clangDir = path.join(includeDir, "clang");
    const flags: string[] = [];

    if (fs.existsSync(includeDir)) {
      flags.push(`-I${includeDir}`);
    }
    if (fs.existsSync(clangDir)) {
      flags.push("-isystem", clangDir);
    }
    return flags;
  }

  public static inspectFFI(projectRoot: string, externName?: string): string {
    const flags = this.getIncludeFlags();
    const prefix = this.getPrefix();
    const lines: string[] = [
      "=== Lean 4 C FFI Environment ===",
      `Toolchain Prefix: ${prefix || "(not detected)"}`,
      `Sysroot Include Flags: ${flags.length > 0 ? flags.join(" ") : "(none)"}`,
    ];

    if (prefix) {
      const leanH = path.join(prefix, "include", "lean", "lean.h");
      const exists = fs.existsSync(leanH);
      lines.push(`Sysroot Header (lean/lean.h): ${exists ? "Found (" + leanH + ")" : "Not found"}`);
    }

    if (externName) {
      lines.push(`\nInspecting symbol: '${externName}'`);
      const matches: string[] = [];
      const scanLeanDir = (dir: string) => {
        if (!fs.existsSync(dir)) return;
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const e of entries) {
          if (e.name.startsWith(".") || e.name === "node_modules" || e.name === "fermats-last-theorem") continue;
          const p = path.join(dir, e.name);
          if (e.isDirectory()) {
            scanLeanDir(p);
          } else if (e.isFile() && e.name.endsWith(".lean")) {
            try {
              const content = fs.readFileSync(p, "utf-8");
              if (content.includes("extern") && content.includes(externName)) {
                matches.push(path.relative(projectRoot, p));
              }
            } catch {
              // Ignore unreadable files
            }
          }
        }
      };
      scanLeanDir(path.join(projectRoot, "docs", "easci", "lean"));
      scanLeanDir(path.join(projectRoot, "src"));

      if (matches.length > 0) {
        lines.push(`Found references in ${matches.length} file(s):`);
        for (const m of matches) lines.push(`  - ${m}`);
      } else {
        lines.push(`No @[extern "${externName}"] declarations located in project Lean files.`);
      }
    }

    return lines.join("\n");
  }
}

export function formatGoalAsMarkdown(goalText: string): string {
  if (!goalText || goalText.trim().length === 0) {
    return "No active goals (proof complete or out of tactic scope).";
  }
  return "```lean\n" + goalText.trim() + "\n```";
}

export class LakeServerManager {
  private projectRoot: string;
  private activeSession: {
    child: ChildProcess;
    leanRoot: string;
    nextId: number;
    pendingRequests: Map<number, { resolve: (val: any) => void; reject: (err: any) => void }>;
    openedFiles: Set<string>;
    buffer: Buffer;
  } | null = null;

  constructor(projectRoot: string) {
    this.projectRoot = projectRoot;
  }

  public findLeanRoot(targetFile: string): string {
    let curr = path.dirname(path.resolve(targetFile));
    while (curr !== path.dirname(curr)) {
      if (
        fs.existsSync(path.join(curr, "lakefile.lean")) ||
        fs.existsSync(path.join(curr, "lakefile.toml")) ||
        fs.existsSync(path.join(curr, "lean-toolchain"))
      ) {
        return curr;
      }
      curr = path.dirname(curr);
    }
    const easciLean = path.join(this.projectRoot, "docs", "easci", "lean");
    if (fs.existsSync(path.join(easciLean, "lakefile.lean"))) {
      return easciLean;
    }
    return this.projectRoot;
  }

  private async ensureSession(targetFile: string): Promise<NonNullable<LakeServerManager["activeSession"]>> {
    const leanRoot = this.findLeanRoot(targetFile);
    if (this.activeSession && this.activeSession.leanRoot === leanRoot) {
      return this.activeSession;
    }
    this.dispose();

    const session: NonNullable<LakeServerManager["activeSession"]> = {
      child: spawn("lake", ["serve"], {
        cwd: leanRoot,
        stdio: ["pipe", "pipe", "ignore"],
      }),
      leanRoot,
      nextId: 1,
      pendingRequests: new Map(),
      openedFiles: new Set(),
      buffer: Buffer.alloc(0),
    };

    session.child.stdout?.on("data", (chunk: Buffer) => {
      session.buffer = Buffer.concat([session.buffer, chunk]);
      while (true) {
        const idx = session.buffer.indexOf("\r\n\r\n");
        if (idx === -1) break;
        const header = session.buffer.subarray(0, idx).toString("utf-8");
        const match = header.match(/Content-Length:\s*(\d+)/i);
        if (!match) {
          session.buffer = session.buffer.subarray(idx + 4);
          continue;
        }
        const len = parseInt(match[1], 10);
        if (session.buffer.length < idx + 4 + len) break;
        const body = session.buffer.subarray(idx + 4, idx + 4 + len).toString("utf-8");
        session.buffer = session.buffer.subarray(idx + 4 + len);
        try {
          const parsed = JSON.parse(body);
          if (parsed.id !== undefined && session.pendingRequests.has(parsed.id)) {
            const handler = session.pendingRequests.get(parsed.id)!;
            session.pendingRequests.delete(parsed.id);
            if (parsed.error) {
              handler.reject(new Error(parsed.error.message || JSON.stringify(parsed.error)));
            } else {
              handler.resolve(parsed.result);
            }
          }
        } catch {
          // Ignore parse errors on corrupted frames
        }
      }
    });

    session.child.on("error", (err) => {
      process.stderr.write(`[lean-lsp-mcp] lake serve process error: ${err.message}\n`);
    });

    session.child.on("exit", (code) => {
      process.stderr.write(`[lean-lsp-mcp] lake serve exited with code ${code}\n`);
      this.activeSession = null;
    });

    this.activeSession = session;

    // Send initialize request
    await this.sendRequest(session, "initialize", {
      processId: process.pid,
      rootUri: pathToFileURL(leanRoot).href,
      capabilities: {},
    });

    // Send initialized notification
    this.sendNotification(session, "initialized", {});

    return session;
  }

  private sendRequest(
    session: NonNullable<LakeServerManager["activeSession"]>,
    method: string,
    params: any
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = session.nextId++;
      const timer = setTimeout(() => {
        session.pendingRequests.delete(id);
        reject(new Error(`Timeout waiting for LSP response to ${method} (id: ${id})`));
      }, 15000);

      session.pendingRequests.set(id, {
        resolve: (val) => {
          clearTimeout(timer);
          resolve(val);
        },
        reject: (err) => {
          clearTimeout(timer);
          reject(err);
        },
      });

      const msg = JSON.stringify({ jsonrpc: "2.0", id, method, params });
      const header = `Content-Length: ${Buffer.byteLength(msg, "utf-8")}\r\n\r\n`;
      session.child.stdin?.write(header + msg);
    });
  }

  private sendNotification(
    session: NonNullable<LakeServerManager["activeSession"]>,
    method: string,
    params: any
  ): void {
    const msg = JSON.stringify({ jsonrpc: "2.0", method, params });
    const header = `Content-Length: ${Buffer.byteLength(msg, "utf-8")}\r\n\r\n`;
    session.child.stdin?.write(header + msg);
  }

  public async getGoal(filePath: string, line: number, col: number): Promise<string> {
    const absPath = path.isAbsolute(filePath) ? filePath : path.resolve(this.projectRoot, filePath);
    if (!fs.existsSync(absPath)) {
      return `File not found: ${filePath}`;
    }

    try {
      const session = await this.ensureSession(absPath);
      const uri = pathToFileURL(absPath).href;

      if (!session.openedFiles.has(absPath)) {
        const text = fs.readFileSync(absPath, "utf-8");
        this.sendNotification(session, "textDocument/didOpen", {
          textDocument: {
            uri,
            languageId: "lean4",
            version: 1,
            text,
          },
        });
        session.openedFiles.add(absPath);
      }

      const res = await this.sendRequest(session, "$/lean/plainGoal", {
        textDocument: { uri },
        position: {
          line: Math.max(0, line - 1),
          character: Math.max(0, col - 1),
        },
      });

      const goalText = res?.rendered || (Array.isArray(res?.goals) ? res.goals.join("\n\n") : "");
      return formatGoalAsMarkdown(goalText);
    } catch (err: any) {
      return `Lake LSP error: ${err.message || String(err)}`;
    }
  }

  public async getTermGoal(filePath: string, line: number, col: number): Promise<string> {
    const absPath = path.isAbsolute(filePath) ? filePath : path.resolve(this.projectRoot, filePath);
    if (!fs.existsSync(absPath)) {
      return `File not found: ${filePath}`;
    }

    try {
      const session = await this.ensureSession(absPath);
      const uri = pathToFileURL(absPath).href;

      if (!session.openedFiles.has(absPath)) {
        const text = fs.readFileSync(absPath, "utf-8");
        this.sendNotification(session, "textDocument/didOpen", {
          textDocument: {
            uri,
            languageId: "lean4",
            version: 1,
            text,
          },
        });
        session.openedFiles.add(absPath);
      }

      const res = await this.sendRequest(session, "$/lean/plainTermGoal", {
        textDocument: { uri },
        position: {
          line: Math.max(0, line - 1),
          character: Math.max(0, col - 1),
        },
      });

      const goalText = res?.rendered || res?.goal || "";
      return formatGoalAsMarkdown(goalText);
    } catch (err: any) {
      return `Lake LSP error: ${err.message || String(err)}`;
    }
  }

  public dispose(): void {
    if (this.activeSession) {
      try {
        this.activeSession.child.kill();
      } catch {
        // Process might have already terminated
      }
      this.activeSession = null;
    }
  }
}

export class McpServer {
  private projectRoot: string;
  private ileanIndex: Lean4IleanIndex;
  private lakeManager: LakeServerManager;
  private buffer: string = "";

  constructor(projectRoot: string = process.cwd()) {
    this.projectRoot = projectRoot;
    this.ileanIndex = new Lean4IleanIndex(projectRoot);
    this.ileanIndex.refresh();
    this.lakeManager = new LakeServerManager(projectRoot);
  }

  public getIleanIndex(): Lean4IleanIndex {
    return this.ileanIndex;
  }

  public getLakeManager(): LakeServerManager {
    return this.lakeManager;
  }

  public async handleMessage(req: any): Promise<McpResponse | null> {
    if (!req || typeof req !== "object") return null;
    const { id, method, params } = req;

    // Notifications (no id)
    if (id === undefined || id === null) {
      if (method === "notifications/initialized" || method === "initialized") {
        return null;
      }
      return null;
    }

    try {
      switch (method) {
        case "initialize":
          return {
            jsonrpc: "2.0",
            id,
            result: {
              protocolVersion: "2024-11-05",
              capabilities: {
                tools: {},
              },
              serverInfo: {
                name: "lean-lsp-mcp",
                version: "0.1.0",
              },
            },
          };

        case "ping":
          return {
            jsonrpc: "2.0",
            id,
            result: {},
          };

        case "tools/list":
          return {
            jsonrpc: "2.0",
            id,
            result: {
              tools: TOOL_DEFINITIONS,
            },
          };

        case "tools/call": {
          const toolName = params?.name;
          const toolArgs = params?.arguments || {};
          const contentText = await this.executeTool(toolName, toolArgs);
          return {
            jsonrpc: "2.0",
            id,
            result: {
              content: [
                {
                  type: "text",
                  text: contentText,
                },
              ],
              isError: false,
            },
          };
        }

        default:
          return {
            jsonrpc: "2.0",
            id,
            error: {
              code: -32601,
              message: `Method not found: ${method}`,
            },
          };
      }
    } catch (err: any) {
      return {
        jsonrpc: "2.0",
        id,
        result: {
          content: [
            {
              type: "text",
              text: `Error executing tool: ${err.message || String(err)}`,
            },
          ],
          isError: true,
        },
      };
    }
  }

  public async executeTool(name: string, args: any): Promise<string> {
    switch (name) {
      case "lean_goal":
      case "lean_plain_goal": {
        const filePath = args.filePath || args.path || args.file;
        if (!filePath) {
          throw new Error("Missing required argument: 'filePath'");
        }
        const line = Number(args.line ?? 1);
        const col = Number(args.col ?? args.character ?? 1);
        return await this.lakeManager.getGoal(filePath, line, col);
      }

      case "lean_term_goal":
      case "lean_plain_term_goal": {
        const filePath = args.filePath || args.path || args.file;
        if (!filePath) {
          throw new Error("Missing required argument: 'filePath'");
        }
        const line = Number(args.line ?? 1);
        const col = Number(args.col ?? args.character ?? 1);
        return await this.lakeManager.getTermGoal(filePath, line, col);
      }

      case "lean_lookup_symbol":
      case "lean_jump_definition": {
        const symbol = args.symbol;
        if (!symbol) {
          throw new Error("Missing required argument: 'symbol'");
        }
        const match = this.ileanIndex.lookupSymbol(symbol);
        if (!match) {
          return `Symbol '${symbol}' not found in .ilean cache. Ensure the Lean project is compiled via 'lake build'.`;
        }
        return [
          `Symbol: ${symbol}`,
          `File: ${match.filePath}`,
          `Position: line ${match.line}, col ${match.col}` + (match.endLine ? ` to line ${match.endLine}, col ${match.endCol}` : ""),
          match.module ? `Module: ${match.module}` : "",
        ].filter(Boolean).join("\n");
      }

      case "lean_module_hierarchy":
      case "lean_module_dag": {
        const moduleName = args.moduleName;
        if (!moduleName) {
          throw new Error("Missing required argument: 'moduleName'");
        }
        const direction = args.direction || "both";
        const imports = (direction === "imports" || direction === "both")
          ? this.ileanIndex.getModuleImports(moduleName)
          : [];
        const importedBy = (direction === "importedBy" || direction === "both")
          ? this.ileanIndex.getModuleImportedBy(moduleName)
          : [];

        const lines: string[] = [`Module: ${moduleName}`];
        if (direction === "imports" || direction === "both") {
          lines.push(`Direct Imports (${imports.length}):`);
          if (imports.length === 0) {
            lines.push("  (none)");
          } else {
            for (const imp of imports) lines.push(`  - ${imp}`);
          }
        }
        if (direction === "importedBy" || direction === "both") {
          lines.push(`Imported By (${importedBy.length}):`);
          if (importedBy.length === 0) {
            lines.push("  (none)");
          } else {
            for (const by of importedBy) lines.push(`  - ${by}`);
          }
        }
        return lines.join("\n");
      }

      case "lean_c_ffi_inspect":
      case "lean_c_ffi": {
        const externName = args.externName || args.symbol;
        return LeanSysrootBridge.inspectFFI(this.projectRoot, externName);
      }

      default:
        throw new Error(`Unknown tool: '${name}'`);
    }
  }

  public startStdio(): void {
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk: string) => {
      this.buffer += chunk;
      this.processBuffer();
    });
    process.stdin.on("end", () => {
      this.lakeManager.dispose();
      process.exit(0);
    });
  }

  private async processBuffer(): Promise<void> {
    while (true) {
      if (this.buffer.startsWith("Content-Length:")) {
        const headerEnd = this.buffer.indexOf("\r\n\r\n");
        if (headerEnd === -1) break;
        const header = this.buffer.slice(0, headerEnd);
        const match = header.match(/Content-Length:\s*(\d+)/i);
        if (!match) {
          this.buffer = this.buffer.slice(headerEnd + 4);
          continue;
        }
        const len = parseInt(match[1], 10);
        if (this.buffer.length < headerEnd + 4 + len) break;
        const body = this.buffer.slice(headerEnd + 4, headerEnd + 4 + len);
        this.buffer = this.buffer.slice(headerEnd + 4 + len);
        await this.dispatchRaw(body, true);
      } else {
        const newlineIdx = this.buffer.indexOf("\n");
        if (newlineIdx === -1) break;
        const line = this.buffer.slice(0, newlineIdx).trim();
        this.buffer = this.buffer.slice(newlineIdx + 1);
        if (line.length > 0) {
          await this.dispatchRaw(line, false);
        }
      }
    }
  }

  private async dispatchRaw(rawJson: string, useContentLength: boolean): Promise<void> {
    let req: any;
    try {
      req = JSON.parse(rawJson);
    } catch (err: any) {
      this.sendError(null, -32700, "Parse error: " + err.message, useContentLength);
      return;
    }
    const res = await this.handleMessage(req);
    if (res !== null) {
      this.sendResponse(res, useContentLength);
    }
  }

  private sendResponse(res: McpResponse, useContentLength: boolean): void {
    const json = JSON.stringify(res);
    if (useContentLength) {
      const header = `Content-Length: ${Buffer.byteLength(json, "utf-8")}\r\n\r\n`;
      process.stdout.write(header + json);
    } else {
      process.stdout.write(json + "\n");
    }
  }

  private sendError(id: any, code: number, message: string, useContentLength: boolean): void {
    const errRes: McpResponse = {
      jsonrpc: "2.0",
      id: id ?? null,
      error: { code, message },
    };
    this.sendResponse(errRes, useContentLength);
  }

  public dispose(): void {
    this.lakeManager.dispose();
  }
}

// Standalone Server Entry
export function main(): void {
  const projectRoot = process.cwd();
  const server = new McpServer(projectRoot);
  process.stderr.write(`[lean-lsp-mcp] Initialized for project ${projectRoot}\n`);
  server.startStdio();
}

function checkIsMain(): boolean {
  if (!process.argv[1]) return false;
  try {
    const argvPath = fs.realpathSync(path.resolve(process.argv[1]));
    const modulePath = fs.realpathSync(fileURLToPath(import.meta.url));
    return argvPath === modulePath;
  } catch {
    return path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
  }
}

if (checkIsMain()) {
  main();
}


