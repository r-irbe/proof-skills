# lean-serve-broker

One `lake serve` per Lean project, shared by every LSP consumer.

## Why

`lake serve` holds the whole import graph in memory (hundreds of MB to several
GB with Mathlib). Before the broker, each consumer spawned its own instance:
every lean-lsp-mcp session, every pi-lens pass, every ad-hoc client. The
broker multiplexes ONE server process behind a unix socket, so memory is paid
once and all consumers see the same elaboration state.

## Usage

Nothing to run by hand. Consumers attach automatically:

- **lean-lsp-mcp**: `ensureSession` spawns the attach client instead of
  `lake serve` (default since 2026-09-21; set `LEAN_SERVE_DIRECT=1` to opt out).
- **pi-lens**: `.pi-lens.json` routes `.lean` files at the attach client via a
  custom LSP server.

Manual control:

```bash
python3 lean_serve_broker.py status   # clients, building state, pids
python3 lean_serve_broker.py stop     # graceful shutdown of broker + server
```

## How it works

- The first attach client spawns the broker daemon; uniqueness is guarded by
  `flock` on a state lock (`~/.local/state/lean-serve-broker/<hash>/`).
- The broker performs the real LSP `initialize` handshake once and serves
  canned responses to every attaching client (LSP servers accept one
  initialize per connection).
- Client request ids are rewritten into a global namespace so responses route
  back to the right client; server notifications (publishDiagnostics) are
  broadcast to all clients.
- Client `shutdown`/`exit` are intercepted: one consumer cannot kill the
  shared server. The broker idles out (`LEAN_SERVE_IDLE_S`, default 900 s)
  after the last client disconnects.
- A monitor detects running `lake build` processes in the project root and
  exposes them via `status.json`; new textDocument requests are held for a
  bounded window (`LEAN_SERVE_BUILD_WAIT_MS`, default 60000) so diagnostics
  are requested against fresh builds, not mid-build state.

## Etiquette (binding on agents)

1. Never spawn `lake serve` directly; attach through the broker.
2. `lake build` remains the compile path and is safe to run while the broker
   is up; the broker detects it and gates elaboration briefly.
3. Do not kill `lake`/`lean` processes to "reset" LSP state; use
   `lean_serve_broker.py stop`, which tears the server down cleanly.
4. Avoid two clients editing the same file simultaneously (didChange versions
   are last-writer-wins); read-only diagnostics consumers are unaffected.

## Environment

| Variable | Default | Meaning |
| --- | --- | --- |
| `LEAN_SERVE_STATE_HOME` | `~/.local/state/lean-serve-broker` | State directory root |
| `LEAN_SERVE_IDLE_S` | `900` | Idle seconds before broker exit |
| `LEAN_SERVE_BUILD_WAIT_MS` | `60000` | Bounded hold during lake builds |
| `LEAN_SERVE_BROKER_SERVER` | `lake serve` | Server command override (tests) |
| `LEAN_SERVE_DIRECT` | unset | lean-lsp-mcp: bypass broker, spawn privately |

Tests: `pytest tests/test_lean_serve_broker.py` (fake LSP server, no Lean
toolchain needed). ASCII-only per INV-001.
