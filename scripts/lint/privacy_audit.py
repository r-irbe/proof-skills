#!/usr/bin/env python3
"""Public confidentiality and host-path leak auditor for proof-skills.

Scans all tracked / unignored files in the repository (including text files,
ZIP/Kuzu `.kz` archives, and `.wasm` / ELF binaries) to guarantee zero leaks
of private project codenames, internal ADR/FSIA identifiers, private planning
documents, workstation hostnames, or developer home paths.

Exit codes:
  0  Zero confidentiality violations found.
  1  At least one violation found.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRS = {
    ".git",
    ".lake",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}

ARCHIVE_SUFFIXES = {".kz", ".zip"}
BINARY_SCAN_SUFFIXES = {".wasm", ".so", ".dylib", ".dll", ".node"}


def _build_forbidden_patterns() -> list[tuple[str, re.Pattern[str]]]:
    """Construct forbidden regexes via token assembly so raw grep stays clean."""
    rules: list[tuple[str, str]] = [
        ("private-project-upper", r"\b" + "EA" + "SCI" + r"\b"),
        ("private-project-lower", r"\b" + "ea" + "sci" + r"\b"),
        ("private-repo-hyphen", "tacit" + "-" + "mui"),
        ("private-ui-name", r"\b" + "Tacit" + "Flow" + r"\b"),
        (
            "private-project-title",
            r"(?<!somatic )(?<!extracting )(?<!Transparent and )\b"
            + "Tacit"
            + r"\b(?! [Kk]nowledge)",
        ),
        ("private-fleet-pkg", r"\b" + "Pi" + "Fleet" + r"\b"),
        ("private-pde-corpus", r"\b" + "NavierStokes" + "AndEuler" + r"\b"),
        ("internal-adr-id", r"\b" + "ADR-" + r"00\d{2}\b"),
        ("internal-fsia-id", r"\b" + "FSIA" + "-"),
        ("internal-master-plan", "MASTER" + "-PLAN" + r"\.md"),
        ("private-lab-id", r"\b" + "fi" + "lab" + r"\b"),
        ("private-dossier-id", "DOSSIER-" + "FI" + "LAB"),
        ("workstation-home-path", "/" + "home" + "/" + "radu"),
        ("internal-hostname-1", r"\b" + "irbe" + "station" + r"\b"),
        ("internal-hostname-2", r"\b" + "lava" + "pool" + r"\b"),
    ]
    return [(label, re.compile(expr)) for label, expr in rules]


FORBIDDEN_PATTERNS = _build_forbidden_patterns()
ASCII_RUN_RE = re.compile(rb"[\x20-\x7e]{5,}")


@dataclass
class Finding:
    file: str
    location: str
    rule: str
    match: str
    snippet: str


def _should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    return any(part in SKIP_DIRS for part in rel.parts)


def _scan_text(text: str, rel_file: str, inner_prefix: str = "") -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for rule_name, pat in FORBIDDEN_PATTERNS:
            m = pat.search(line)
            if m:
                loc = f"{inner_prefix}:{lineno}" if inner_prefix else f"L{lineno}"
                findings.append(
                    Finding(
                        file=rel_file,
                        location=loc,
                        rule=rule_name,
                        match=m.group(0),
                        snippet=line.strip()[:140],
                    )
                )
    return findings


def _scan_binary_bytes(data: bytes, rel_file: str, inner_prefix: str = "") -> list[Finding]:
    findings: list[Finding] = []
    for m_run in ASCII_RUN_RE.finditer(data):
        s = m_run.group(0).decode("ascii", errors="ignore")
        for rule_name, pat in FORBIDDEN_PATTERNS:
            m = pat.search(s)
            if m:
                loc = f"{inner_prefix}@0x{m_run.start():x}" if inner_prefix else f"@0x{m_run.start():x}"
                findings.append(
                    Finding(
                        file=rel_file,
                        location=loc,
                        rule=rule_name,
                        match=m.group(0),
                        snippet=s[:140],
                    )
                )
    return findings


def _scan_zip_bytes(data: bytes, rel_file: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                entry_bytes = zf.read(info.filename)
                try:
                    entry_text = entry_bytes.decode("utf-8")
                    findings.extend(_scan_text(entry_text, rel_file, inner_prefix=info.filename))
                except UnicodeDecodeError:
                    findings.extend(_scan_binary_bytes(entry_bytes, rel_file, inner_prefix=info.filename))
    except zipfile.BadZipFile:
        findings.extend(_scan_binary_bytes(data, rel_file))
    return findings


def audit_tree(root: Path) -> tuple[list[Finding], int]:
    self_path = Path(__file__).resolve()
    findings: list[Finding] = []
    scanned = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file() or _should_skip(path, root):
            continue
        if path.resolve() == self_path:
            continue

        scanned += 1
        rel_file = str(path.relative_to(root))
        raw = path.read_bytes()

        if path.suffix.lower() in ARCHIVE_SUFFIXES or raw.startswith(b"PK\x03\x04"):
            findings.extend(_scan_zip_bytes(raw, rel_file))
            continue

        if (
            path.suffix.lower() in BINARY_SCAN_SUFFIXES
            or raw.startswith(b"\x00asm")
            or raw.startswith(b"\x7fELF")
        ):
            findings.extend(_scan_binary_bytes(raw, rel_file))
            continue

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            findings.extend(_scan_binary_bytes(raw, rel_file))
            continue

        findings.extend(_scan_text(text, rel_file))

    return findings, scanned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit proof-skills for private identifier or path leaks.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to scan")
    parser.add_argument("--strict", action="store_true", help="Fail on any finding (default behavior)")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    findings, scanned = audit_tree(root)

    if args.json:
        payload = {
            "passed": len(findings) == 0,
            "files_scanned": scanned,
            "violations_count": len(findings),
            "violations": [asdict(f) for f in findings],
        }
        print(json.dumps(payload, indent=2))
    else:
        if findings:
            print(f"PRIVACY AUDIT FAILED: {len(findings)} violation(s) across {scanned} scanned files", file=sys.stderr)
            for f in findings[:50]:
                print(
                    f"  [{f.rule}] {f.file}:{f.location} matched {f.match!r} -> {f.snippet}",
                    file=sys.stderr,
                )
        else:
            print(f"PASS: privacy_audit scanned {scanned} files (text + archives + binaries), 0 violations.")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
