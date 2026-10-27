#!/usr/bin/env python3
"""IEANTN-style per-declaration receipts for the EASCI Lean corpus.

Generates one machine-checkable verification artifact (a "receipt") per
top-level declaration of the selected modules.  A receipt records where the
declaration lives (file, line, source sha256), the toolchain it was checked
under, a deterministic timestamp, and the kernel-check evidence: a generated
probe file (`#check @Name` plus `#print axioms Name`) executed with
`lake env lean`, capturing exit code, captured output, and the output's
sha256.  A companion `fingerprints.json` records
{decl, source_sha256, receipt_sha256} per receipt: a diff line in that set
is a meaning-change candidate (IEANTN fingerprint semantics).

Determinism: given the same sources, the same toolchain, the same built
oleans, and the same timestamp basis, reruns produce byte-identical
receipts and byte-identical fingerprints.json.  There is no wall-clock in
the output bytes: `timestamp` is SOURCE_DATE_EPOCH if set, else the last
git commit date touching the source file, else the source file's mtime
(recorded in `timestamp_basis`).  JSON is emitted with sorted keys, fixed
indent, ASCII escaping, and a trailing newline; all paths are repo-root
relative with forward slashes; the random temp probe path is sanitised to
"<probe>" wherever it could leak into captured output.

Usage:
  python3 scripts/gen_receipts.py --module EASCI.PDG
  python3 scripts/gen_receipts.py --module EASCI.PDG --lean-root docs/easci/lean

Exit status: 0 iff every emitted receipt's kernel probe exited 0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
GENERATOR = "scripts/gen_receipts.py"
PROBE_SANITISED = "<probe>"
LEAN_ROOT_SANITISED = "<lean-root>"

DECL_RE = re.compile(
    r"^(?:(?:private|protected|noncomputable|unsafe|partial|scoped|local)\s+)*"
    r"(theorem|lemma|def|abbrev|instance|structure|inductive|opaque)\s+"
    r"([A-Za-z_][A-Za-z0-9_']*)"
)
NAMESPACE_RE = re.compile(r"^namespace\s+([A-Za-z0-9_.]+)")
END_RE = re.compile(r"^end(?:\s+([A-Za-z0-9_.]+))?\s*$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_line_structure(text: str) -> str:
    """Blank out Lean comments (nested block and line) and string-literal
    contents while preserving newlines, so declaration regexes never match
    inside comments and line numbers stay stable."""
    out: list[str] = []
    i, n = 0, len(text)
    depth = 0
    in_string = False
    in_line_comment = False
    while i < n:
        c = text[i]
        two = text[i : i + 2]
        if in_line_comment:
            if c == "\n":
                in_line_comment = False
                out.append(c)
            else:
                out.append(" ")
            i += 1
            continue
        if in_string:
            if c == "\\" and i + 1 < n:
                out.append("  ")
                i += 2
                continue
            if c == '"':
                in_string = False
                out.append('"')
                i += 1
                continue
            out.append(c if c == "\n" else " ")
            i += 1
            continue
        if depth > 0:
            if two == "/-":
                depth += 1
                out.append("  ")
                i += 2
                continue
            if two == "-/":
                depth -= 1
                out.append("  ")
                i += 2
                continue
            out.append(c if c == "\n" else " ")
            i += 1
            continue
        if two == "/-":
            depth += 1
            out.append("  ")
            i += 2
            continue
        if two == "--":
            in_line_comment = True
            out.append("  ")
            i += 2
            continue
        if c == '"':
            in_string = True
            out.append('"')
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def extract_declarations(source: bytes) -> list[dict]:
    """Top-level declarations of one .lean file, in source order.

    Returns dicts {name, module_suffix, kind, line}.  Private declarations
    are skipped: their environment names are mangled and cannot be probed
    from outside the module.  Nested namespaces and section variables are
    not tracked beyond the namespace prefix stack.
    """
    text = strip_line_structure(source.decode("utf-8", errors="replace"))
    decls: list[dict] = []
    ns_stack: list[str] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        ns = NAMESPACE_RE.match(line)
        if ns:
            ns_stack.extend(ns.group(1).split("."))
            continue
        end = END_RE.match(line)
        if end:
            if end.group(1):
                for _ in end.group(1).split("."):
                    if ns_stack:
                        ns_stack.pop()
            elif ns_stack:
                ns_stack.pop()
            continue
        if line[:1].isspace() or not line.strip():
            continue
        m = DECL_RE.match(line)
        if not m:
            continue
        modifiers = line[: m.start(1)]
        if re.search(r"\bprivate\b", modifiers):
            continue
        decls.append(
            {
                "name": m.group(2),
                "module": ".".join(ns_stack),
                "kind": m.group(1),
                "line": idx,
            }
        )
    return decls


def discover_modules(lean_root: Path, prefixes: list[str]) -> list[str]:
    """Modules under <lean_root>/EASCI whose dotted name matches one of the
    prefixes (exact or dotted-prefix match)."""
    root = lean_root / "EASCI"
    modules: list[str] = []
    for path in sorted(root.rglob("*.lean")):
        module = "EASCI." + path.relative_to(root).with_suffix("").as_posix().replace("/", ".")
        if any(module == p or module.startswith(p + ".") for p in prefixes):
            modules.append(module)
    return modules


def deterministic_timestamp(repo_root: Path, source_rel: Path, mtime_epoch: int) -> tuple[str, str]:
    """A timestamp that is a function of the inputs, not of the run wall
    clock: SOURCE_DATE_EPOCH, else the last git commit date touching the
    source file, else the file's mtime."""
    sde = os.environ.get("SOURCE_DATE_EPOCH")
    if sde is not None and sde.strip().isdigit():
        dt = datetime.fromtimestamp(int(sde), tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "SOURCE_DATE_EPOCH"
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%cI", "--", source_rel.as_posix()],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            dt = datetime.fromisoformat(proc.stdout.strip())
            dt = dt.astimezone(timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "git-commit-date"
    except OSError:
        pass
    dt = datetime.fromtimestamp(mtime_epoch, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "source-mtime"


def dump_json(obj: dict) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def sanitise(text: str, probe_path: Path, lean_root: Path) -> str:
    text = text.replace(str(probe_path), PROBE_SANITISED)
    text = text.replace(str(lean_root), LEAN_ROOT_SANITISED)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    script_dir = Path(__file__).resolve().parent
    default_repo = script_dir.parent
    parser.add_argument("--repo-root", type=Path, default=default_repo,
                        help="repository root (default: script's parent directory)")
    parser.add_argument("--lean-root", type=Path, default=None,
                        help="Lean project root (default: <repo-root>/docs/easci/lean)")
    parser.add_argument("--out", type=Path, default=None,
                        help="receipt output directory (default: <repo-root>/docs/tracking/receipts)")
    parser.add_argument("--module", action="append", default=[],
                        help="dotted module or module-prefix filter, e.g. EASCI.PDG (repeatable)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="per-probe timeout in seconds (default: 300)")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    lean_root = (args.lean_root or repo_root / "docs" / "easci" / "lean").resolve()
    out_root = (args.out or repo_root / "docs" / "tracking" / "receipts").resolve()
    toolchain_file = lean_root / "lean-toolchain"
    if not toolchain_file.exists():
        print(f"error: no lean-toolchain at {toolchain_file}", file=sys.stderr)
        return 2
    toolchain = toolchain_file.read_text(encoding="utf-8").strip()
    if not (lean_root / "lakefile.lean").exists() and not (lean_root / "lakefile.toml").exists():
        print(f"error: no lakefile under {lean_root}", file=sys.stderr)
        return 2

    prefixes = []
    for entry in args.module:
        prefixes.extend(p.strip() for p in entry.split(",") if p.strip())
    modules = discover_modules(lean_root, prefixes)
    if not modules:
        print(f"error: no modules matched prefixes {prefixes!r}", file=sys.stderr)
        return 2

    receipts: list[dict] = []
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="easci-receipts-") as tmp:
        tmp_dir = Path(tmp)
        for module in modules:
            source_path = lean_root.joinpath(*module.split(".")).with_suffix(".lean")
            if not source_path.exists():
                print(f"error: source file missing for module {module}", file=sys.stderr)
                return 2
            source_bytes = source_path.read_bytes()
            source_sha = sha256_bytes(source_bytes)
            source_rel = source_path.relative_to(repo_root)
            timestamp, ts_basis = deterministic_timestamp(repo_root, source_rel, int(source_path.stat().st_mtime))
            decls = extract_declarations(source_bytes)
            if not decls:
                print(f"note: {module}: no probeable top-level declarations")
                continue
            for decl in decls:
                full_name = (
                    f"{decl['module']}.{decl['name']}" if decl["module"] else decl["name"]
                )
                probe_lines = [
                    f"import {module}",
                    "",
                    f"#check @{full_name}",
                    f"#print axioms {full_name}",
                ]
                probe_body = ("\n".join(probe_lines) + "\n").encode("utf-8")
                probe_path = tmp_dir / f"{module}.{decl['name']}.probe.lean"
                probe_path.write_bytes(probe_body)
                try:
                    proc = subprocess.run(
                        ["lake", "env", "lean", str(probe_path)],
                        cwd=str(lean_root),
                        capture_output=True,
                        text=True,
                        timeout=args.timeout,
                        check=False,
                    )
                    stdout = sanitise(proc.stdout, probe_path, lean_root)
                    stderr = sanitise(proc.stderr, probe_path, lean_root)
                    exit_code = proc.returncode
                except subprocess.TimeoutExpired:
                    stdout = ""
                    stderr = f"probe timed out after {args.timeout}s"
                    exit_code = 124
                except OSError as exc:
                    stdout = ""
                    stderr = f"probe failed to run: {exc}"
                    exit_code = 127
                output_sha = sha256_bytes(stdout.encode("utf-8") + stderr.encode("utf-8"))
                receipt = {
                    "schema_version": SCHEMA_VERSION,
                    "generator": GENERATOR,
                    "decl": full_name,
                    "name": decl["name"],
                    "module": module,
                    "kind": decl["kind"],
                    "source": {
                        "file": source_rel.as_posix(),
                        "line": decl["line"],
                        "sha256": source_sha,
                    },
                    "toolchain": toolchain,
                    "timestamp": timestamp,
                    "timestamp_basis": ts_basis,
                    "probe": {
                        "file": PROBE_SANITISED,
                        "commands": ["lake env lean <probe>"],
                        "lines": probe_lines,
                    },
                    "kernel_check": {
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "output_sha256": output_sha,
                    },
                }
                receipt_dir = out_root / module
                receipt_dir.mkdir(parents=True, exist_ok=True)
                receipt_path = receipt_dir / f"{decl['name']}.receipt.json"
                receipt_bytes = dump_json(receipt)
                receipt_path.write_bytes(receipt_bytes)
                status = "ok" if exit_code == 0 else f"PROBE-EXIT-{exit_code}"
                print(f"{module}.{decl['name']}: {status} ({len(receipt_bytes)} bytes)")
                if exit_code != 0:
                    failures.append(full_name)
                receipts.append(
                    {
                        "decl": full_name,
                        "module": module,
                        "source_sha256": source_sha,
                        "receipt_sha256": sha256_bytes(receipt_bytes),
                    }
                )

    fingerprints = {
        "schema_version": SCHEMA_VERSION,
        "generator": GENERATOR,
        "fingerprints": sorted(receipts, key=lambda r: r["decl"]),
    }
    fingerprints_path = out_root / "fingerprints.json"
    fingerprints_path.write_bytes(dump_json(fingerprints))
    print(f"wrote {len(receipts)} receipts and {fingerprints_path.relative_to(repo_root)}")

    if failures:
        print(f"FAILED probes: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
