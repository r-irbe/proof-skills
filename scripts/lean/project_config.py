#!/usr/bin/env python3
"""Declarative Lean 4 project & workspace configuration loader.

Walks upward from `start_dir` (default: cwd) to discover `lean-project.toml`
(or `.lean-analyzer.toml`), or falls back to zero-config `lakefile.lean` /
`lakefile.toml` auto-discovery.

Strict 7-bit ASCII only (INV-001). Zero external dependencies (uses stdlib
`tomllib` on Python >=3.11 with a pure-stdlib TOML parser fallback).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


CONFIG_FILENAMES = ("lean-project.toml", ".lean-analyzer.toml")
LAKEFILE_NAMES = ("lakefile.lean", "lakefile.toml")

LEAN_LIB_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*lean_lib\s+([A-Za-z0-9_'`]+)",
    re.MULTILINE,
)
PACKAGE_LEAN_RE = re.compile(
    r"^\s*package\s+([A-Za-z0-9_'`.\-]+)",
    re.MULTILINE,
)
DEFAULT_TARGET_LIB_RE = re.compile(
    r"@\[default_target\]\s*lean_lib\s+([A-Za-z0-9_'`]+)",
    re.MULTILINE,
)
TOML_LEAN_LIB_RE = re.compile(
    r'\[\[lean_lib\]\][^\[]*?name\s*=\s*"([^"]+)"',
    re.DOTALL,
)
TOML_PACKAGE_NAME_RE = re.compile(
    r'^\s*name\s*=\s*"([^"]+)"',
    re.MULTILINE,
)


def _strip_quotes(name: str) -> str:
    n = name.strip()
    if n.startswith("`"):
        n = n[1:]
    return n.strip('"\'')


def _parse_toml_text(text: str) -> dict[str, Any]:
    if tomllib is not None:
        return tomllib.loads(text)
    return _fallback_parse_toml(text)


def _fallback_parse_toml(text: str) -> dict[str, Any]:
    """Minimal stdlib TOML parser supporting tables, array-of-tables, arrays, strings, ints, floats, bools."""
    root: dict[str, Any] = {}
    current: dict[str, Any] = root
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        in_str = False
        clean_chars = []
        for ch in raw:
            if ch == '"':
                in_str = not in_str
            if ch == "#" and not in_str:
                break
            clean_chars.append(ch)
        line = "".join(clean_chars).strip()
        i += 1
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            path = [p.strip().strip('"') for p in line[2:-2].split(".")]
            target = root
            for part in path[:-1]:
                target = target.setdefault(part, {})
            arr = target.setdefault(path[-1], [])
            new_obj: dict[str, Any] = {}
            arr.append(new_obj)
            current = new_obj
            continue
        if line.startswith("[") and line.endswith("]"):
            path = [p.strip().strip('"') for p in line[1:-1].split(".")]
            target = root
            for part in path:
                target = target.setdefault(part, {})
            current = target
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            key = k.strip().strip('"')
            val_str = v.strip()
            while val_str.startswith("[") and not val_str.endswith("]") and i < len(lines):
                nxt = lines[i].split("#", 1)[0].strip()
                val_str += " " + nxt
                i += 1
            current[key] = _parse_toml_val(val_str)
    return root


def _parse_toml_val(val_str: str) -> Any:
    s = val_str.strip()
    if s in ("true", "false"):
        return s == "true"
    if s.startswith('"') and s.endswith('"'):
        return json.loads(s)
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_toml_val(x) for x in _split_top_level(inner)]
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def _split_top_level(s: str) -> list[str]:
    parts: list[str] = []
    cur: list[str] = []
    depth = 0
    in_str = False
    quote_ch = ""
    for ch in s:
        if in_str:
            cur.append(ch)
            if ch == quote_ch:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            quote_ch = ch
            cur.append(ch)
        elif ch == "[":
            depth += 1
            cur.append(ch)
        elif ch == "]":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            item = "".join(cur).strip()
            if item:
                parts.append(item)
            cur = []
        else:
            cur.append(ch)
    tail = "".join(cur).strip()
    if tail:
        parts.append(tail)
    return parts


def parse_lakefile_targets(project_root: Path) -> dict[str, Any]:
    """Parse package name, lean_lib targets, and primary library directory from lakefile."""
    lake_lean = project_root / "lakefile.lean"
    lake_toml = project_root / "lakefile.toml"
    libs: list[str] = []
    default_libs: list[str] = []
    package_name: str | None = None

    if lake_lean.is_file():
        content = lake_lean.read_text(encoding="utf-8", errors="replace")
        pm = PACKAGE_LEAN_RE.search(content)
        if pm:
            package_name = _strip_quotes(pm.group(1))
        for m in LEAN_LIB_RE.finditer(content):
            lib = _strip_quotes(m.group(1))
            if lib not in libs:
                libs.append(lib)
        for m in DEFAULT_TARGET_LIB_RE.finditer(content):
            lib = _strip_quotes(m.group(1))
            if lib not in default_libs:
                default_libs.append(lib)
    elif lake_toml.is_file():
        content = lake_toml.read_text(encoding="utf-8", errors="replace")
        pm = TOML_PACKAGE_NAME_RE.search(content)
        if pm:
            package_name = _strip_quotes(pm.group(1))
        for m in TOML_LEAN_LIB_RE.finditer(content):
            lib = _strip_quotes(m.group(1))
            if lib not in libs:
                libs.append(lib)

    lean_dir: str | None = None
    for cand in [*default_libs, *libs]:
        if (project_root / cand).is_dir():
            lean_dir = cand
            break
    if lean_dir is None and package_name and (project_root / package_name).is_dir():
        lean_dir = package_name
    if lean_dir is None:
        for child in sorted(project_root.iterdir()) if project_root.is_dir() else []:
            if child.is_dir() and child.name[:1].isupper() and not child.name.startswith("."):
                if any(child.rglob("*.lean")):
                    lean_dir = child.name
                    break
    if lean_dir is None:
        lean_dir = default_libs[0] if default_libs else (libs[0] if libs else (package_name or "."))

    project_name = lean_dir if lean_dir != "." else (package_name or project_root.name)
    return {
        "name": project_name,
        "package_name": package_name or project_name,
        "lean_dir": lean_dir,
        "lean_libs": libs,
        "default_libs": default_libs,
    }


def discover_modules(project_root: Path, lean_dir: str) -> list[str]:
    """Discover top-level module names under `<project_root>/<lean_dir>/*.lean` or `.lake/build/lib/lean/`."""
    src_base = project_root if lean_dir in ("", ".") else (project_root / lean_dir)
    mods: list[str] = []
    if src_base.is_dir():
        for p in sorted(src_base.glob("*.lean")):
            if p.stem != "Main" and not p.stem.startswith("_"):
                mods.append(p.stem)
    if not mods:
        olean_base = project_root / ".lake" / "build" / "lib" / "lean"
        if lean_dir not in ("", ".") and (olean_base / lean_dir).is_dir():
            olean_base = olean_base / lean_dir
        if olean_base.is_dir():
            for p in sorted(olean_base.glob("*.olean")):
                if p.stem not in mods:
                    mods.append(p.stem)
    return mods


@dataclass
class ProjectConfig:
    root: Path
    config_path: Path | None
    raw: dict[str, Any] = field(default_factory=dict)
    name: str = "Project"
    lean_dir: str = "."
    lean_libs: list[str] = field(default_factory=list)
    exclude_dirs: list[str] = field(default_factory=list)
    expected_axioms: list[str] = field(
        default_factory=lambda: ["propext", "Quot.sound", "Classical.choice"]
    )
    core_modules: list[str] = field(default_factory=list)

    @property
    def corpus_dir(self) -> Path:
        return self.root if self.lean_dir in ("", ".") else (self.root / self.lean_dir)

    @property
    def workspace_root(self) -> Path:
        ws = self.raw.get("workspace", {})
        rel = ws.get("repo_root")
        if rel:
            return (self.root / rel).resolve()
        return self.root

    @property
    def workspace_mirrors(self) -> dict[str, str]:
        ws = self.raw.get("workspace", {})
        mirrors = ws.get("mirrors", {})
        return {str(k): str(v) for k, v in mirrors.items()}

    @property
    def architecture_tiers(self) -> dict[str, list[str]]:
        arch = self.raw.get("architecture", {})
        tiers = arch.get("tiers", {})
        return {str(k): [str(x) for x in v] for k, v in tiers.items() if isinstance(v, list)}

    @property
    def architecture_layers(self) -> list[list[str]]:
        arch = self.raw.get("architecture", {})
        layers_tbl = arch.get("layers", {})
        if isinstance(layers_tbl, dict) and "order" in layers_tbl:
            return [[str(m) for m in grp] for grp in layers_tbl["order"]]
        if isinstance(layers_tbl, list):
            return [[str(m) for m in grp] for grp in layers_tbl]
        return []

    @property
    def altproof_tactics(self) -> list[dict[str, Any]]:
        ap = self.raw.get("altproof", {})
        tactics = ap.get("tactics", [])
        return list(tactics) if isinstance(tactics, list) else []

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "config_path": str(self.config_path) if self.config_path else None,
            "name": self.name,
            "lean_dir": self.lean_dir,
            "lean_libs": self.lean_libs,
            "exclude_dirs": self.exclude_dirs,
            "expected_axioms": self.expected_axioms,
            "core_modules": self.core_modules,
            "workspace_root": str(self.workspace_root),
            "workspace_mirrors": self.workspace_mirrors,
            "architecture_tiers": self.architecture_tiers,
            "architecture_layers": self.architecture_layers,
            "altproof_tactics": self.altproof_tactics,
            "raw": self.raw,
        }


def find_project_root(start_dir: Path | str | None = None) -> tuple[Path, Path | None]:
    """Walk upward from `start_dir` to find `lean-project.toml` or `lakefile.lean`/`lakefile.toml`."""
    if start_dir is None:
        env_root = os.environ.get("LEAN_PROJECT_ROOT")
        start = Path(env_root).resolve() if env_root else Path.cwd().resolve()
    else:
        start = Path(start_dir).resolve()
    if start.is_file():
        start = start.parent

    cur = start
    while True:
        for cfg_name in CONFIG_FILENAMES:
            cand = cur / cfg_name
            if cand.is_file():
                return cur, cand
        for lf in LAKEFILE_NAMES:
            if (cur / lf).is_file():
                # Check if a parent workspace has a lean-project.toml that mirrors this subpackage
                p = cur.parent
                while True:
                    for cfg_name in CONFIG_FILENAMES:
                        if (p / cfg_name).is_file():
                            return cur, (p / cfg_name)
                    if p.parent == p:
                        break
                    p = p.parent
                return cur, None
        nested = cur / "docs" / "easci" / "lean" / "lean-project.toml"
        if nested.is_file():
            return nested.parent, nested
        nested_lf = cur / "docs" / "easci" / "lean" / "lakefile.lean"
        if nested_lf.is_file():
            return nested_lf.parent, None
        if cur.parent == cur:
            break
        cur = cur.parent

    return start, None


def load_project_config(start_dir: Path | str | None = None) -> ProjectConfig:
    """Load declarative `ProjectConfig` from `lean-project.toml` or auto-discover from `lakefile`."""
    root, cfg_path = find_project_root(start_dir)
    raw: dict[str, Any] = {}
    if cfg_path is not None and cfg_path.is_file():
        raw = _parse_toml_text(cfg_path.read_text(encoding="utf-8"))

    lf_info = parse_lakefile_targets(root)
    proj_sec = raw.get("project", {})
    axioms_sec = raw.get("axioms", {})

    name = str(proj_sec.get("name") or lf_info["name"])
    lean_dir = str(proj_sec.get("lean_dir") or lf_info["lean_dir"])
    lean_libs = list(proj_sec.get("lean_libs") or lf_info["lean_libs"] or [name])
    exclude_dirs = [str(x) for x in proj_sec.get("exclude_dirs", [])]
    expected_axioms = [
        str(x)
        for x in axioms_sec.get(
            "expected", ["propext", "Quot.sound", "Classical.choice"]
        )
    ]
    core_modules = [
        str(x)
        for x in proj_sec.get("core_modules")
        or discover_modules(root, lean_dir)
    ]

    return ProjectConfig(
        root=root,
        config_path=cfg_path,
        raw=raw,
        name=name,
        lean_dir=lean_dir,
        lean_libs=lean_libs,
        exclude_dirs=exclude_dirs,
        expected_axioms=expected_axioms,
        core_modules=core_modules,
    )


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Inspect discovered Lean 4 project configuration.")
    ap.add_argument("--root", type=Path, default=None, help="Starting directory (default: cwd)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()
    cfg = load_project_config(args.root)
    if args.json:
        print(json.dumps(cfg.to_dict(), indent=2))
    else:
        print(f"Project:     {cfg.name}")
        print(f"Root:        {cfg.root}")
        print(f"Config:      {cfg.config_path or '(auto-discovered from lakefile)'}")
        print(f"Lean dir:    {cfg.lean_dir}")
        print(f"Libraries:   {', '.join(cfg.lean_libs)}")
        print(f"Modules:     {len(cfg.core_modules)} ({', '.join(cfg.core_modules[:8])}...)")
