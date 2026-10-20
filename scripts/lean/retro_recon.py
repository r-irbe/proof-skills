#!/usr/bin/env python3
"""
Retro Reconnaissance -- Automated Discovery for Retroactive Audit
Produces census, dependency graph, convention compliance, and coverage matrix
for an existing Lean 4 project. First step of the RETRO protocol (SK-35).

Usage:
    python3 scripts/retro_recon.py [--lean-dir EASCI] [--output docs/tracking/recon_report.md]
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def census(lean_dir: Path) -> dict[str, dict]:
    """Count theorems, defs, sorry, lines, sections per module."""
    results = {}
    thm_pattern = re.compile(r"^(theorem|lemma)\s+(\S+)", re.MULTILINE)
    def_pattern = re.compile(
        r"^(def|noncomputable def|structure|inductive|class|abbrev)\s+(\S+)", re.MULTILINE
    )
    sorry_pattern = re.compile(r"\bsorry\b")
    section_pattern = re.compile(r"^-- §(\d+)", re.MULTILINE)
    private_pattern = re.compile(r"^private\s+(theorem|lemma|def)\s+(\S+)", re.MULTILINE)
    instance_pattern = re.compile(r"^instance\s+", re.MULTILINE)

    for f in sorted(lean_dir.glob("*.lean")):
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        thms = thm_pattern.findall(text)
        defs = def_pattern.findall(text)
        sorry_matches = [
            (i + 1, line.strip())
            for i, line in enumerate(lines)
            if sorry_pattern.search(line) and not line.strip().startswith("--")
        ]
        sections = section_pattern.findall(text)
        privates = private_pattern.findall(text)
        instances = instance_pattern.findall(text)

        results[f.stem] = {
            "file": f.name,
            "lines": len(lines),
            "theorems": len(thms),
            "theorem_names": [t[1] for t in thms],
            "definitions": len(defs),
            "definition_names": [d[1] for d in defs],
            "sorry_count": len(sorry_matches),
            "sorry_locations": sorry_matches,
            "sections": sorted(set(sections)),
            "privates": len(privates),
            "instances": len(instances),
        }
    return results


def dependency_graph(lean_dir: Path, project: str | None = None) -> dict:
    proj = project or lean_dir.resolve().name
    """Extract import edges and compute topological order."""
    edges = []
    modules = set()
    imports_map: dict[str, list[str]] = {}

    for f in sorted(lean_dir.glob("*.lean")):
        module = f.stem
        modules.add(module)
        deps = []
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(rf"^import\s+{re.escape(proj)}\.(\w+)", line)
            if m:
                target = m.group(1)
                edges.append({"from": module, "to": target})
                deps.append(target)
        imports_map[module] = deps

    # Topological sort (Kahn's algorithm)
    in_degree = defaultdict(int)
    for mod in modules:
        in_degree[mod] = 0
    for edge in edges:
        in_degree[edge["from"]] += 1  # depends on 'to'

    # Actually: 'from' imports 'to', so 'to' must come first
    adj: dict[str, list[str]] = defaultdict(list)
    dep_count: dict[str, int] = {}
    for mod in modules:
        dep_count[mod] = len(imports_map.get(mod, []))
    for edge in edges:
        adj[edge["to"]].append(edge["from"])

    queue = [m for m in modules if dep_count[m] == 0]
    topo_order = []
    while queue:
        queue.sort()
        current = queue.pop(0)
        topo_order.append(current)
        for dependent in adj[current]:
            dep_count[dependent] -= 1
            if dep_count[dependent] == 0:
                queue.append(dependent)

    # Group into waves (modules with same depth)
    depth: dict[str, int] = {}
    for mod in topo_order:
        if not imports_map.get(mod):
            depth[mod] = 0
        else:
            depth[mod] = max(depth.get(dep, 0) for dep in imports_map[mod]) + 1

    waves: dict[int, list[str]] = defaultdict(list)
    for mod, d in sorted(depth.items(), key=lambda x: x[1]):
        waves[d].append(mod)

    return {
        "edges": edges,
        "topological_order": topo_order,
        "waves": {k: sorted(v) for k, v in sorted(waves.items())},
        "imports": {k: sorted(v) for k, v in imports_map.items()},
    }


def convention_check(lean_dir: Path) -> list[dict]:
    """Check coding conventions across all modules."""
    issues = []

    for f in sorted(lean_dir.glob("*.lean")):
        module = f.stem
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()

        # autoImplicit false
        if "set_option autoImplicit false" not in text:
            issues.append(
                {
                    "module": module,
                    "severity": "P0",
                    "rule": "autoImplicit",
                    "message": "Missing set_option autoImplicit false",
                }
            )

        # Module docstring
        if "/-!" not in text:
            issues.append(
                {
                    "module": module,
                    "severity": "P2",
                    "rule": "docstring",
                    "message": "Missing module docstring (/-! ... -/)",
                }
            )

        # Section headers
        section_headers = re.findall(r"^-- §\d+", text, re.MULTILINE)
        if not section_headers:
            issues.append(
                {
                    "module": module,
                    "severity": "P3",
                    "rule": "sections",
                    "message": "No section headers (-- §N ...)",
                }
            )

        # Long lines (>120 chars)
        long_lines = [(i + 1, len(line)) for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            issues.append(
                {
                    "module": module,
                    "severity": "P3",
                    "rule": "line-length",
                    "message": f"{len(long_lines)} line(s) > 120 chars (max: {max(ll[1] for ll in long_lines)})",
                }
            )

        # Namespace/section balance check: named `namespace X` and named
        # `section X` blocks both close with `end X` (or bare `end`).
        # Counting only `namespace` produced false positives on modules
        # using named sections (e.g. LyapunovStability `section
        # LTS_Lyapunov_Bridge`).  Bare `end` (no trailing whitespace) also
        # closes a block but is not matched by `^end\s`; named blocks are
        # the dominant pattern, so the balance is computed on named opens
        # vs all `end` lines.
        ns_open = len(re.findall(r"^namespace\s", text, re.MULTILINE))
        sec_open = len(re.findall(r"^section\s", text, re.MULTILINE))
        ns_close = len(re.findall(r"^end\s", text, re.MULTILINE))
        if ns_open + sec_open != ns_close:
            issues.append(
                {
                    "module": module,
                    "severity": "P1",
                    "rule": "namespace-balance",
                    "message": f"Unbalanced namespace/section: {ns_open} namespace + {sec_open} section opens vs {ns_close} ends",
                }
            )

        # Unused imports (heuristic: import X but X. never appears after import block)
        for line in lines:
            m = re.match(r"^import\s+([\w.]+)", line)
            if m:
                imported = m.group(1).split(".")[-1]
                # Very rough heuristic -- only flag obvious cases
                if imported not in text[text.index(line) + len(line) :]:
                    # Don't flag EASCI self-imports or Mathlib
                    if not m.group(1).startswith("Mathlib") and not m.group(1).startswith("EASCI"):
                        pass  # Too noisy; skip for now

    return issues


def generate_report(census_data: dict, dep_data: dict, conv_issues: list, output: Path) -> None:
    """Generate the Markdown reconnaissance report."""
    total_lines = sum(m["lines"] for m in census_data.values())
    total_thms = sum(m["theorems"] for m in census_data.values())
    total_defs = sum(m["definitions"] for m in census_data.values())
    total_sorry = sum(m["sorry_count"] for m in census_data.values())

    lines = [
        "# RETRO Reconnaissance Report",
        "",
        "## Summary",
        f"- **Modules:** {len(census_data)}",
        f"- **Total lines:** {total_lines:,}",
        f"- **Theorems + Lemmas:** {total_thms}",
        f"- **Definitions:** {total_defs}",
        f"- **Sorry count:** {total_sorry}",
        f"- **Convention issues:** {len(conv_issues)}",
        "",
        "## Module Census",
        "",
        "| Module | Lines | Theorems | Defs | Sorry | Sections | Private |",
        "|---|---|---|---|---|---|---|",
    ]

    for module in sorted(census_data.keys()):
        m = census_data[module]
        sects = ", ".join(m["sections"][:5]) + ("..." if len(m["sections"]) > 5 else "")
        lines.append(
            f"| {module} | {m['lines']} | {m['theorems']} | {m['definitions']} "
            f"| {m['sorry_count']} | {sects or '--'} | {m['privates']} |"
        )

    lines.extend(
        [
            "",
            "## Dependency Waves (Audit Order)",
            "",
        ]
    )

    for wave_num, mods in sorted(dep_data["waves"].items()):
        parallel = "parallel" if len(mods) > 1 else "single"
        lines.append(f"**Wave {wave_num}** ({parallel}): {', '.join(mods)}")

    lines.extend(
        [
            "",
            "## Import Graph",
            "",
        ]
    )
    for module, deps in sorted(dep_data["imports"].items()):
        if deps:
            lines.append(f"- {module} -> {', '.join(deps)}")
        else:
            lines.append(f"- {module} (root -- no imports)")

    if conv_issues:
        lines.extend(
            [
                "",
                "## Convention Issues",
                "",
                "| Module | Severity | Rule | Message |",
                "|---|---|---|---|",
            ]
        )
        for issue in sorted(conv_issues, key=lambda i: (i["severity"], i["module"])):
            lines.append(
                f"| {issue['module']} | {issue['severity']} | {issue['rule']} | {issue['message']} |"
            )

    if total_sorry > 0:
        lines.extend(
            [
                "",
                "## Sorry Locations (P0)",
                "",
            ]
        )
        for module, data in sorted(census_data.items()):
            for line_num, line_text in data["sorry_locations"]:
                lines.append(f"- `{module}.lean:L{line_num}`: {line_text}")

    lines.extend(
        [
            "",
            "---",
            "*Generated by retro_recon.py*",
        ]
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="RETRO Reconnaissance for EASCI")
    parser.add_argument(
        "--lean-dir", type=Path, default=Path("EASCI"), help="Directory containing .lean files"
    )
    parser.add_argument(
        "--project", type=str, default=None, help="Project root namespace (defaults to lean-dir basename)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/tracking/recon_report.md"),
        help="Output report path",
    )
    parser.add_argument("--json", type=Path, default=None, help="Also output raw data as JSON")
    args = parser.parse_args()

    if not args.lean_dir.exists():
        print(f"Lean directory not found: {args.lean_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {args.lean_dir}...")
    census_data = census(args.lean_dir)
    print(f"  Found {len(census_data)} modules")

    dep_data = dependency_graph(args.lean_dir, getattr(args, 'project', None))
    print(f"  Dependency waves: {len(dep_data['waves'])}")

    conv_issues = convention_check(args.lean_dir)
    print(f"  Convention issues: {len(conv_issues)}")

    generate_report(census_data, dep_data, conv_issues, args.output)
    print(f"Report written to {args.output}")

    if args.json:
        json_data = {
            "census": {
                k: {kk: vv for kk, vv in v.items() if kk != "sorry_locations"}
                for k, v in census_data.items()
            },
            "dependencies": dep_data,
            "convention_issues": conv_issues,
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        print(f"JSON data written to {args.json}")


if __name__ == "__main__":
    main()
