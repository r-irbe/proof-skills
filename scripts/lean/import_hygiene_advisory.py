#!/usr/bin/env python3
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
"""Deterministic import-hygiene advisory checks for Lean 4 projects.

The checker intentionally avoids external import-graph tooling and uses only
source-level facts:

* duplicate import lines inside a module;
* local project imports that do not exist on disk;
* source-level cycles among local project imports.

It is advisory, not a semantic unused-import prover.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class ImportRef:
    module: str
    imported: str
    file: Path
    line: int


def module_name(root: Path, file: Path, project: str) -> str:
    rel = file.relative_to(root).with_suffix("")
    return ".".join((project, *rel.parts))


def module_path(project_root: Path, module: str) -> Path:
    parts = module.split(".")
    return project_root.joinpath(*parts).with_suffix(".lean")


def iter_lean_files(root: Path):
    for path in sorted(root.rglob("*.lean")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        yield path


def build_import_re(project: str) -> re.Pattern[str]:
    return re.compile(rf"^import\s+({re.escape(project)}(?:\.[A-Za-z0-9_']+)*)\s*$")


def collect_modules(root: Path, project: str) -> dict[str, Path]:
    return {module_name(root, path, project): path for path in iter_lean_files(root)}


def collect_imports(root: Path, project: str) -> dict[str, list[ImportRef]]:
    imports: dict[str, list[ImportRef]] = {}
    import_re = build_import_re(project)
    for path in iter_lean_files(root):
        module = module_name(root, path, project)
        refs: list[ImportRef] = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = import_re.match(line.strip())
            if match:
                refs.append(ImportRef(module, match.group(1), path, line_no))
        imports[module] = refs
    return imports


def find_duplicate_imports(imports: dict[str, list[ImportRef]]) -> list[tuple[ImportRef, list[int]]]:
    duplicates: list[tuple[ImportRef, list[int]]] = []
    for refs in imports.values():
        by_import: dict[str, list[ImportRef]] = defaultdict(list)
        for ref in refs:
            by_import[ref.imported].append(ref)
        for same_import_refs in by_import.values():
            if len(same_import_refs) > 1:
                first = same_import_refs[0]
                duplicates.append((first, [ref.line for ref in same_import_refs]))
    return duplicates


def find_missing_targets(
    project_root: Path,
    modules: dict[str, Path],
    imports: dict[str, list[ImportRef]],
) -> list[ImportRef]:
    missing: list[ImportRef] = []
    for refs in imports.values():
        for ref in refs:
            if ref.imported in modules:
                continue
            if not module_path(project_root, ref.imported).exists():
                missing.append(ref)
    return missing


def find_cycles(imports: dict[str, list[ImportRef]], modules: dict[str, Path]) -> list[list[str]]:
    graph = {
        module: sorted({ref.imported for ref in refs if ref.imported in modules})
        for module, refs in imports.items()
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []
    seen_cycles: set[tuple[str, ...]] = set()

    def normalize(cycle: list[str]) -> tuple[str, ...]:
        body = cycle[:-1]
        if not body:
            return tuple(cycle)
        rotations = [tuple(body[i:] + body[:i]) for i in range(len(body))]
        best = min(rotations)
        return best + (best[0],)

    def dfs(module: str) -> None:
        if module in visited:
            return
        if module in visiting:
            idx = stack.index(module)
            cycle = stack[idx:] + [module]
            key = normalize(cycle)
            if key not in seen_cycles:
                seen_cycles.add(key)
                cycles.append(list(key))
            return
        visiting.add(module)
        stack.append(module)
        for dep in graph.get(module, []):
            dfs(dep)
        stack.pop()
        visiting.remove(module)
        visited.add(module)

    for module in sorted(graph):
        dfs(module)
    return cycles


def print_text(
    root: Path,
    modules: dict[str, Path],
    imports: dict[str, list[ImportRef]],
    duplicates: list[tuple[ImportRef, list[int]]],
    missing: list[ImportRef],
    cycles: list[list[str]],
) -> None:
    edge_count = sum(len(refs) for refs in imports.values())
    print("Lean 4 Import Hygiene Advisory")
    print("=" * 30)
    print(f"Root: {root}")
    print(f"Modules scanned: {len(modules)}")
    print(f"Local import edges: {edge_count}")
    print(f"Duplicate imports: {len(duplicates)}")
    print(f"Missing local import targets: {len(missing)}")
    print(f"Source-level import cycles: {len(cycles)}")

    if duplicates:
        print("\nDuplicate imports")
        for ref, lines in duplicates:
            rel = ref.file.relative_to(root.parent)
            print(f"- {rel}:{','.join(map(str, lines))}: {ref.imported}")

    if missing:
        print("\nMissing local import targets")
        for ref in missing:
            rel = ref.file.relative_to(root.parent)
            print(f"- {rel}:{ref.line}: {ref.imported}")

    if cycles:
        print("\nSource-level import cycles")
        for cycle in cycles:
            print("- " + " -> ".join(cycle))


def print_markdown(
    root: Path,
    modules: dict[str, Path],
    imports: dict[str, list[ImportRef]],
    duplicates: list[tuple[ImportRef, list[int]]],
    missing: list[ImportRef],
    cycles: list[list[str]],
) -> None:
    edge_count = sum(len(refs) for refs in imports.values())
    print("# Import Hygiene Advisory")
    print()
    print("This report checks only source-level duplicate imports, missing local")
    print("project targets, and local import cycles.")
    print()
    print("## Summary")
    print()
    print(f"- Root: `{root}`")
    print(f"- Modules scanned: {len(modules)}")
    print(f"- Local import edges: {edge_count}")
    print(f"- Duplicate imports: {len(duplicates)}")
    print(f"- Missing local import targets: {len(missing)}")
    print(f"- Source-level import cycles: {len(cycles)}")
    print()

    def section(title: str, rows: list[str]) -> None:
        print(f"## {title}")
        print()
        if rows:
            for row in rows:
                print(f"- {row}")
        else:
            print("None.")
        print()

    section(
        "Duplicate imports",
        [
            f"`{ref.file.relative_to(root.parent)}` lines {', '.join(map(str, lines))}: `{ref.imported}`"
            for ref, lines in duplicates
        ],
    )
    section(
        "Missing local import targets",
        [
            f"`{ref.file.relative_to(root.parent)}` line {ref.line}: `{ref.imported}`"
            for ref in missing
        ],
    )
    section("Source-level import cycles", [" -> ".join(f"`{m}`" for m in cycle) for cycle in cycles])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Lean 4 import hygiene checks")
    parser.add_argument("--root", type=Path, required=True, help="Lean source root")
    parser.add_argument("--project", default="MyProject", help="Lean namespace prefix used in local imports")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown report")
    args = parser.parse_args()

    root = args.root
    if not root.exists():
        print(f"error: root does not exist: {root}", file=sys.stderr)
        return 2

    project_root = root.parent
    modules = collect_modules(root, args.project)
    imports = collect_imports(root, args.project)
    duplicates = find_duplicate_imports(imports)
    missing = find_missing_targets(project_root, modules, imports)
    cycles = find_cycles(imports, modules)

    if args.markdown:
        print_markdown(root, modules, imports, duplicates, missing, cycles)
    else:
        print_text(root, modules, imports, duplicates, missing, cycles)

    return 1 if duplicates or missing or cycles else 0


if __name__ == "__main__":
    raise SystemExit(main())
