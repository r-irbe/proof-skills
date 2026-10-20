#!/usr/bin/env python3
"""Blueprint-to-Report pipeline CLI (SK-62).

Implements the subcommands referenced in skills/lean-report/SKILL.md:
  - ingest     : Parse blueprint LaTeX/JSON artifacts into report_context.json
  - plan       : Derive chapter outlines and narrative arcs into report_plan.json
  - illustrate : Generate TikZ dependency figures from report_context.json
  - diff       : Compare two report_context.json snapshots to identify changed chapters
  - expand     : Delegate blueprint section expansion to expand_blueprint.py
  - guard      : Delegate LaTeX hygiene verification to blueprint_tex_guard.py

Strict 7-bit ASCII only (INV-001). Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent


def _parse_blueprint_tex(bp_dir: Path) -> list[dict]:
    nodes: list[dict] = []
    tex_files: list[Path] = []
    if bp_dir.is_file() and bp_dir.suffix == ".tex":
        tex_files = [bp_dir]
    elif bp_dir.is_dir():
        tex_files = sorted(bp_dir.rglob("*.tex"))

    block_re = re.compile(
        r"\\begin\{(theorem|lemma|definition|proposition|corollary)\}(.*?)\\end\{\1\}",
        re.S,
    )
    for tf in tex_files:
        text = tf.read_text(encoding="utf-8", errors="replace")
        for match in block_re.finditer(text):
            env = match.group(1)
            body = match.group(2)
            label_m = re.search(r"\\label\{([^}]+)\}", body)
            lean_m = re.search(r"\\lean\{([^}]+)\}", body)
            uses_m = re.search(r"\\uses\{([^}]+)\}", body)
            lean_name = lean_m.group(1).strip() if lean_m else ""
            module = lean_name.rsplit(".", 1)[0] if "." in lean_name else tf.stem
            deps = [
                d.strip()
                for d in (uses_m.group(1).split(",") if uses_m else [])
                if d.strip()
            ]
            nodes.append(
                {
                    "kind": env,
                    "label": label_m.group(1).strip() if label_m else "",
                    "name": lean_name,
                    "module": module,
                    "status": "proven" if "\\leanok" in body else "stated",
                    "deps": deps,
                    "source_file": str(tf),
                }
            )
    return nodes


def cmd_ingest(args: argparse.Namespace) -> int:
    bp_dir = Path(args.blueprint_dir)
    nodes_json = bp_dir / "nodes.json"
    if nodes_json.is_file():
        nodes = json.loads(nodes_json.read_text(encoding="utf-8"))
    else:
        fallback = Path("blueprint/src") if not bp_dir.exists() else bp_dir
        nodes = _parse_blueprint_tex(fallback)

    modules: dict[str, list[dict]] = {}
    for n in nodes:
        mod = n.get("module") or "Core"
        modules.setdefault(mod, []).append(n)

    context = {
        "blueprint_dir": str(bp_dir),
        "coverage_path": str(args.coverage) if args.coverage else None,
        "node_count": len(nodes),
        "module_count": len(modules),
        "modules": modules,
        "nodes": nodes,
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Ingested {len(nodes)} nodes across {len(modules)} modules -> {out_path}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    ctx_path = Path(args.context)
    context = json.loads(ctx_path.read_text(encoding="utf-8"))
    modules = context.get("modules", {})
    chapters = []
    for idx, (mod_name, mod_nodes) in enumerate(sorted(modules.items()), start=1):
        theorems = [n for n in mod_nodes if n.get("kind") in ("theorem", "lemma", "proposition", "corollary")]
        defs = [n for n in mod_nodes if n.get("kind") == "definition"]
        chapters.append(
            {
                "chapter": idx,
                "module": mod_name,
                "title": f"{mod_name} Formalization",
                "node_count": len(mod_nodes),
                "theorem_count": len(theorems),
                "definition_count": len(defs),
                "key_theorems": [t.get("name") or t.get("label") for t in theorems[:10]],
            }
        )
    plan = {
        "source_context": str(ctx_path),
        "chapter_count": len(chapters),
        "chapters": chapters,
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Planned {len(chapters)} chapters -> {out_path}")
    return 0


def cmd_illustrate(args: argparse.Namespace) -> int:
    ctx_path = Path(args.context)
    context = json.loads(ctx_path.read_text(encoding="utf-8"))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    modules = sorted(context.get("modules", {}).keys())
    lines = [
        "% Auto-generated TikZ module dependency map",
        "\\begin{tikzpicture}[node distance=1.8cm, auto]",
    ]
    for idx, mod in enumerate(modules[:20]):
        safe_label = re.sub(r"[^A-Za-z0-9]", "", mod) or f"M{idx}"
        safe_text = mod.replace("_", "\\_")
        lines.append(f"  \\node[draw, rectangle] ({safe_label}) at (0, -{idx}) {{{safe_text}}};")
    lines.append("\\end{tikzpicture}")
    fig_path = out_dir / "module_dependency_map.tex"
    fig_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated figure {fig_path}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    old_ctx = json.loads(Path(args.old).read_text(encoding="utf-8"))
    new_ctx = json.loads(Path(args.new).read_text(encoding="utf-8"))
    old_mods = old_ctx.get("modules", {})
    new_mods = new_ctx.get("modules", {})
    changed = []
    for mod in sorted(set(old_mods.keys()) | set(new_mods.keys())):
        if old_mods.get(mod) != new_mods.get(mod):
            changed.append(mod)
    print(json.dumps({"changed_modules": changed, "count": len(changed)}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "expand":
        target = HERE / "expand_blueprint.py"
        os.execv(sys.executable, [sys.executable, str(target), *argv[1:]])
    if argv and argv[0] == "guard":
        target = HERE / "blueprint_tex_guard.py"
        os.execv(sys.executable, [sys.executable, str(target), *argv[1:]])

    ap = argparse.ArgumentParser(description="Blueprint-to-Report pipeline CLI (SK-62)")
    sub = ap.add_subparsers(dest="subcommand", required=True)

    p_ing = sub.add_parser("ingest", help="Ingest blueprint artifacts into report_context.json")
    p_ing.add_argument("--blueprint-dir", default=".lake/build/blueprint", help="Blueprint directory")
    p_ing.add_argument("--coverage", default="docs/tracking/coverage_matrix.md", help="Coverage matrix path")
    p_ing.add_argument("--output", default="report/report_context.json", help="Output context JSON")
    p_ing.add_argument("--update", action="store_true", help="Incremental update mode")
    p_ing.set_defaults(func=cmd_ingest)

    p_plan = sub.add_parser("plan", help="Generate report_plan.json from report_context.json")
    p_plan.add_argument("--context", default="report/report_context.json", help="Input context JSON")
    p_plan.add_argument("--output", default="report/report_plan.json", help="Output plan JSON")
    p_plan.set_defaults(func=cmd_plan)

    p_ill = sub.add_parser("illustrate", help="Generate TikZ figures from report_context.json")
    p_ill.add_argument("--context", default="report/report_context.json", help="Input context JSON")
    p_ill.add_argument("--output-dir", default="report/figures", help="Output figures directory")
    p_ill.set_defaults(func=cmd_illustrate)

    p_diff = sub.add_parser("diff", help="Diff two report_context.json files")
    p_diff.add_argument("--old", required=True, help="Previous report_context.json")
    p_diff.add_argument("--new", required=True, help="Updated report_context.json")
    p_diff.set_defaults(func=cmd_diff)

    sub.add_parser("expand", help="Delegate to expand_blueprint.py")
    sub.add_parser("guard", help="Delegate to blueprint_tex_guard.py")

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
