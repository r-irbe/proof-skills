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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--src",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="the lean project root (containing EASCI/); default: this script's parent's parent",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory; default: <src>/generated",
    )
    ap.add_argument("--project", type=str, default="EASCI", help="Project directory/namespace under --src")
    ap.add_argument(
        "--namespaces",
        action="store_true",
        help="wrap namespace-less root-decl files in module-mirroring namespaces (changes those full names)",
    )
    args = ap.parse_args()
    out_dir = args.out or (args.src / "generated")
    out_dir.mkdir(parents=True, exist_ok=True)

    text, manifest = concat(args.src, args.namespaces, args.project)

    lean_out = out_dir / f"{args.project}-concat.lean"
    json_out = out_dir / f"{args.project}-concat.manifest.json"
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
