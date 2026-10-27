#!/usr/bin/env python3
"""Concatenate the whole EASCI corpus into one namespace-scoped Lean file.

Deterministic: no timestamps; the same corpus state always produces the
same output bytes (sha256 stable). Order is topological by the modules'
EASCI-internal import graph (Kahn's algorithm, lexicographic tie-break).
All non-EASCI imports (Mathlib, Cslib, ...) are hoisted to one shared
header in first-encounter order, deduplicated.

Scoping: every module body is wrapped in its own `section ... end` so
that `open`, `set_option` and `variable` cannot leak into later modules.
By default every declaration keeps its exact corpus full name (root
declarations stay at root, namespaced ones stay in their namespaces).
With `--namespaces`, files that declare no namespace but DO carry
root-level declarations are additionally wrapped in their
module-mirroring namespace (EASCI/A/B.lean -> namespace EASCI.A.B),
which changes those declarations' full names - use only when the
consuming tool wants literal namespace coverage and name identity with
the corpus is not required.

Outputs (regenerable; gitignored):
  generated/EASCI-concat.lean         the giant file
  generated/EASCI-concat.manifest.json  per-module metadata + stats
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DECL_RE = re.compile(
    r"^(noncomputable\s+)?(private\s+|protected\s+|partial\s+)*"
    r"(theorem|lemma|def|instance|abbrev|structure|class|inductive|example|opaque)\b"
)
IMPORT_RE = re.compile(r"^import\s+(\S+)")
NS_RE = re.compile(r"^namespace\s+(\S+)")


def module_name(rel: str) -> str:
    """Suffix-less posix rel path EASCI/A/B -> the module name EASCI.A.B."""
    return rel.replace("/", ".")


def parse_module(path: Path) -> dict:
    """Split a module into imports and the remaining body."""
    imports: list[str] = []
    body_lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = IMPORT_RE.match(line)
        if m:
            imports.append(m.group(1))
        else:
            body_lines.append(line)
    body = "\n".join(body_lines)
    namespaces = [m.group(1) for line in body_lines if (m := NS_RE.match(line))]
    decls = sum(1 for line in body_lines if DECL_RE.match(line))
    has_root_decl = decls > 0 and not namespaces
    return {
        "imports": imports,
        "body": body,
        "namespaces": namespaces,
        "decl_count": decls,
        "has_root_decl": has_root_decl,
    }


def topo_order(modules: dict[str, dict], project: str = "EASCI") -> list[str]:
    """Kahn's algorithm over EASCI-internal imports; lexicographic tie-break."""
    internal: dict[str, list[str]] = {}
    for name, mod in modules.items():
        deps = []
        for imp in mod["imports"]:
            if imp.startswith(project) and imp in modules:
                deps.append(imp)
        internal[name] = deps

    dependents: dict[str, list[str]] = {n: [] for n in modules}
    indeg: dict[str, int] = dict.fromkeys(modules, 0)
    for name, deps in internal.items():
        for d in deps:
            dependents[d].append(name)
            indeg[name] += 1

    ready = sorted(n for n, d in indeg.items() if d == 0)
    order: list[str] = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for m in dependents[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort()
    if len(order) != len(modules):
        stuck = sorted(n for n, d in indeg.items() if d > 0)
        raise SystemExit(
            "ERROR: import cycle among: " + ", ".join(stuck[:10])
        )
    return order


def concat(src: Path, wrap_namespaces: bool, project: str = "EASCI") -> tuple[str, dict]:
    corpus = src / project
    files = sorted(corpus.rglob("*.lean"))
    if not files:
        raise SystemExit(f"ERROR: no .lean files under {corpus}")

    modules: dict[str, dict] = {}
    for f in files:
        rel = f.relative_to(src).with_suffix("").as_posix()  # EASCI/A/B
        modules[module_name(rel)] = {**parse_module(f), "rel": rel}

    order = topo_order(modules, project)

    # External imports in first-encounter (topological) order, deduplicated.
    external: list[str] = []
    seen: set[str] = set()
    for name in order:
        for imp in modules[name]["imports"]:
            if not (imp.startswith(project) and imp in modules) and imp not in seen:
                seen.add(imp)
                external.append(imp)

    total_decls = sum(m["decl_count"] for m in modules.values())
    out: list[str] = []
    out.append("/-! GENERATED ARTIFACT - do not edit; regenerate with")
    out.append("    docs/easci/lean/scripts/concat_corpus.py")
    out.append("")
    out.append(f"    modules: {len(modules)}")
    out.append(f"    declarations: {total_decls}")
    out.append(f"    mode: {'namespaces' if wrap_namespaces else 'name-preserving sections'}")
    out.append("")
    out.append("    One namespace-scoped concatenation of the EASCI corpus.")
    out.append("    Order: topological by internal imports. External imports are")
    out.append("    hoisted here. Each module body is scoped in its own section so")
    out.append("    open/set_option/variable cannot leak. Declaration full names are")
    out.append("    identical to the corpus except for root declarations of")
    out.append("    namespace-less files in --namespaces mode.")
    out.append("-/")

    manifest: dict = {
        "modules": [],
        "stats": {
            "file_count": len(modules),
            "decl_count": total_decls,
            "external_import_count": len(external),
            "mode": "namespaces" if wrap_namespaces else "sections",
        },
    }

    for imp in external:
        out.append(f"import {imp}")

    for name in order:
        mod = modules[name]
        out.append("")
        out.append("/-! " + "=" * 66)
        out.append(f"    module: {mod['rel']}.lean")
        out.append(f"    namespace(s): {', '.join(mod['namespaces']) if mod['namespaces'] else '(none declared - declarations at root)'}")
        out.append("    " + "=" * 66 + " -/")

        wrapped = False
        if wrap_namespaces and mod["has_root_decl"]:
            out.append(f"namespace {name}")
            wrapped = True

        # Always a synthetic section: scopes open/set_option/variable.
        out.append(f"section  -- scoped: {name}")
        out.append(mod["body"].rstrip())
        out.append(f"end  -- scoped: {name}")

        if wrapped:
            out.append(f"end  -- namespace {name}")

        manifest["modules"].append(
            {
                "module": name,
                "file": f"{mod['rel']}.lean",
                "namespaces": mod["namespaces"],
                "decl_count": mod["decl_count"],
                "root_decl_wrapped": wrapped,
                "easci_imports": [
                    i for i in mod["imports"] if i in modules
                ],
                "external_imports": [
                    i for i in mod["imports"] if i not in modules
                ],
            }
        )

    text = "\n".join(out) + "\n"
    manifest["stats"]["output_lines"] = text.count("\n")
    manifest["stats"]["output_sha256"] = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()
    return text, manifest


def strip_lean_comments(text: str) -> str:
    """Replaces all /- ... -/ and -- ... comments with spaces, preserving line numbers."""
    out = list(text)
    n = len(text)
    i = 0
    depth = 0
    in_string = False
    while i < n:
        if depth == 0 and not in_string:
            if text[i : i + 2] == "/-":
                depth = 1
                out[i] = " "
                out[i + 1] = " "
                i += 2
                continue
            elif text[i : i + 2] == "--":
                while i < n and text[i] != "\n":
                    out[i] = " "
                    i += 1
                continue
            elif text[i] == '"':
                in_string = True
                i += 1
                continue
        elif in_string:
            if text[i] == "\\" and i + 1 < n:
                i += 2
                continue
            elif text[i] == '"':
                in_string = False
            i += 1
            continue
        else:
            if text[i : i + 2] == "/-":
                depth += 1
                out[i] = " "
                out[i + 1] = " "
                i += 2
                continue
            elif text[i : i + 2] == "-/":
                depth -= 1
                out[i] = " "
                out[i + 1] = " "
                i += 2
                continue
            else:
                if text[i] != "\n":
                    out[i] = " "
                i += 1
                continue
        i += 1
    return "".join(out)


def audit_concat_outputs(lean_out: Path, json_out: Path) -> int:
    """Audit generated <Project>-concat.lean and <Project>-concat.manifest.json."""
    print("=== 1. MANIFEST AUDIT ===")
    if json_out.exists():
        mdata = json.loads(json_out.read_text(encoding="utf-8"))
        stats = mdata.get("stats", {})
        print(f"  - Modules: {stats.get('file_count', len(mdata.get('modules', [])))}")
        print(f"  - Declarations: {stats.get('decl_count', 0)}")
        print(f"  - External imports: {stats.get('external_import_count', 0)}")
    else:
        print(f"  [WARN] {json_out} not found")

    print("\n=== 2. CONCATENATED LEAN CODEBASE AUDIT ===")
    if not lean_out.exists():
        print(f"  [WARN] {lean_out} not found")
        return 1
    text = lean_out.read_text(encoding="utf-8")
    lines = text.splitlines()
    sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"  - Total lines: {len(lines):,}")
    print(f"  - File SHA-256: {sha256}")

    clean_text = strip_lean_comments(text)
    clean_lines = clean_text.splitlines()
    decl_pattern = re.compile(
        r"^\s*(?:noncomputable\s+|private\s+|protected\s+|scoped\s+)*"
        r"(theorem|lemma|def|abbrev|structure|inductive|class|instance|opaque|axiom)\s+([A-Za-z0-9_'.]+)"
    )
    counts: dict[str, int] = {}
    custom_axioms: list[tuple[int, str, str]] = []
    sorry_hits: list[int] = []
    admit_hits: list[int] = []
    for idx, line in enumerate(clean_lines, 1):
        m = decl_pattern.match(line)
        if m:
            kind, name = m.group(1), m.group(2)
            counts[kind] = counts.get(kind, 0) + 1
            if kind in ("axiom", "opaque"):
                custom_axioms.append((idx, kind, name))
        if re.search(r"\bsorry\b", line):
            sorry_hits.append(idx)
        if re.search(r"\badmit\b", line):
            admit_hits.append(idx)

    print("  - Declaration breakdown by keyword:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"      {k:12s}: {v:,}")
    print(f"  - Executable sorry tokens: {len(sorry_hits)}")
    print(f"  - Executable admit tokens: {len(admit_hits)}")
    print(f"  - Custom axiom/opaque declarations: {len(custom_axioms)}")
    return 1 if (sorry_hits or admit_hits) else 0


def main(argv: list[str] | None = None) -> int:
    _here = Path(__file__).resolve().parent
    if str(_here) not in sys.path:
        sys.path.insert(0, str(_here))
    try:
        from project_config import load_project_config
        _cfg = load_project_config()
        _default_src = _cfg.root
        _default_proj = _cfg.lean_dir if _cfg.lean_dir not in ("", ".") else _cfg.name
    except Exception:
        _default_src = Path.cwd()
        _default_proj = "EASCI"

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--src",
        type=Path,
        default=_default_src,
        help="the lean project root; default: auto-discovered project root",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory; default: <src>/generated",
    )
    ap.add_argument("--project", type=str, default=_default_proj, help="Project directory/namespace under --src")
    ap.add_argument(
        "--namespaces",
        action="store_true",
        help="wrap namespace-less root-decl files in module-mirroring namespaces (changes those full names)",
    )
    ap.add_argument(
        "--audit",
        action="store_true",
        help="run comment-aware declaration & forbidden-token audit on the concatenated corpus",
    )
    args = ap.parse_args(argv)
    out_dir = args.out or (args.src / "generated")
    out_dir.mkdir(parents=True, exist_ok=True)

    lean_out = out_dir / f"{args.project}-concat.lean"
    json_out = out_dir / f"{args.project}-concat.manifest.json"

    if not args.audit or not lean_out.exists():
        text, manifest = concat(args.src, args.namespaces, args.project)
        lean_out.write_text(text, encoding="utf-8")
        json_out.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        s = manifest["stats"]
        print(f"wrote {lean_out}  ({s['output_lines']} lines, sha256 {s['output_sha256'][:16]}...)")
        print(
            f"modules={s['file_count']} decls={s['decl_count']} "
            f"external_imports={s['external_import_count']} mode={s['mode']}"
        )

    if args.audit:
        return audit_concat_outputs(lean_out, json_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
