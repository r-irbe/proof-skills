# Compiled kernel census and receipt freshness

Run the generic adapter from the toolkit root (secure rebuild output handling currently requires POSIX):

```sh
python3 scripts/lean/kernel_census.py --project-root /path/to/project --prefix MyProject --receipt /path/to/project/.lake/kernel-census/MyProject.json
```

Default `--mode check` launches neither Lean nor a build. It requires a complete,
successful schema-v2 receipt and verifies SHA-256 fingerprints of the current
source/module set, compiled artifacts and sidecars, project configuration,
adapter/helper, compiler executable and compiled import-library context. File
size and mtime alone do not establish unchanged contents. Imported digests are
reused only when resolved path, device, inode, size, mtime and ctime all match
and the timestamp is at least two seconds old. Source and target artifact bytes
are still hashed. `--rehash-imports` reads and hashes every import again. Missing/failed,
malformed, legacy and stale receipts return nonzero and cannot be gate eligible.

Use `--mode rebuild` explicitly to build the default target and every selected
source module, capture the context, run the kernel replay/axiom audit and publish
an atomic receipt. A per-output OS advisory lock refuses concurrent writers and releases after a crash. A
failed build removes the previous success receipt; no stale success is retained
as the result of that attempt. The JSON stdout is a bounded summary; exact
constant/theorem names and context manifests remain in the receipt.

The producer uses Lean's supported replay and transitive axiom APIs. All eligible
constants are replayed and axiom audited; unsafe/partial exclusions are counted.
Only `propext`, `Classical.choice` and `Quot.sound` are permitted. Identical
serialized theorem records count once, with repeats recorded; conflicts fail.
Private and persistent generated declarations are included. Discarded anonymous
examples and external imported-library bodies are outside compiled replay scope.

`lean_metrics` exposes `action: kernel_census` through the same adapter. Its
`mode: check` is read-only; `mode: rebuild` explicitly writes artifacts and
receipts. Use an MCP installation nested inside this toolkit, or set
`LEAN_PROOF_SKILLS_ROOT` in the MCP server environment. Requested projects cannot
supply executable adapters to default checks. Never substitute static
source counts for this compiled evidence. Never relabel legacy receipts fresh.

Old host-level wrapper entry points may preserve their explicit `--output`
build usage. The generic command defaults to checking a `--receipt`.

Existing unrelated, legacy or published evidence files cannot be overwritten by
rebuild. Choose a new cache path. New mutable-cache receipts identify themselves
explicitly. Logs and receipts are replaced atomically, avoiding hard-link
truncation. Source entries must be confined regular files; FIFOs and symlinks
are refused. Active compiler resolution is queried through `elan which lean`
without starting Lean; raw import search order is preserved in the fingerprint.
Custom environment inputs are hashed without recording their values; transport
variables (`CODEX_*`, `_`, `PWD`, `OLDPWD`, `SHLVL`) are not admitted build inputs.
Freshness covers the recorded build context, not arbitrary external I/O or
volatile transport inputs used by executable Lake configuration.

Digest reuse relies on normal local-filesystem identity/ctime semantics. Strict
rehash is available when independent byte reads are required. Producer snapshots
before and after replay always perform full import hashing.
