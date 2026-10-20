#!/usr/bin/env python3
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
"""
Cross-module bridge validator for Lean 4 projects.

Checks that declarations referencing structures/types from other modules use
visible names and that cross-module dependencies are explicit in the import
graph.

Usage:
    python3 scripts/lean/bridge_validator.py --lean-dir MyProject --project MyProject
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPT_PARENT = SCRIPT_DIR.parent
for _p in (str(SCRIPT_DIR), str(SCRIPT_PARENT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from axiom_audit import strip_comments_preserving_newlines

IGNORED_CROSS_REFERENCE_NAMES = {
    "apply",
    "case",
    "cases",
    "classical",
    "constructor",
    "def",
    "else",
    "end",
    "exact",
    "false",
    "fun",
    "have",
    "if",
    "intro",
    "le_antisymm",
    "le_refl",
    "le_total",
    "le_trans",
    "let",
    "match",
    "measurable",
    "mono",
    "next",
    "open",
    "refine",
    "rfl",
    "show",
    "simp",
    "subst",
    "target",
    "then",
    "true",
    "where",
    "with",
    "zero",
}


def iter_lean_files(lean_dir: Path):
    """Yield `(path, module_name)` pairs for the full recursive Lean tree."""
    for f in sorted(lean_dir.rglob('*.lean')):
        if any(part.startswith('.') for part in f.relative_to(lean_dir).parts):
            continue
        module = f.relative_to(lean_dir).with_suffix('').as_posix().replace('/', '.')
        yield f, module


DECL_PATTERN = re.compile(
    r'^(?:theorem|lemma|def|noncomputable\s+def|structure|inductive|class|abbrev|instance)\s+(\S+)',
    re.MULTILINE
)

LOCAL_DECL_PATTERN = re.compile(
    r'^(?:@\[[^\]]*\]\s*)*'
    r'(?:(?:private|protected|noncomputable|unsafe|partial|meta)\s+)*'
    r'(?:theorem|lemma|def|structure|inductive|class|abbrev|instance)\s+(\S+)',
    re.MULTILINE
)


def transitive_import_closure(module: str, imports: dict[str, set[str]]) -> set[str]:
    """Compute the recursive import closure of one module."""
    closure: set[str] = set()
    stack = list(imports.get(module, set()))
    while stack:
        current = stack.pop()
        if current in closure:
            continue
        closure.add(current)
        stack.extend(imports.get(current, set()) - closure)
    return closure


def strip_string_literals_preserving_layout(text: str) -> str:
    """Remove string literal contents while preserving line structure."""
    out: list[str] = []
    in_string = False
    escaped = False

    for ch in text:
        if in_string:
            if ch == '\n':
                out.append('\n')
            elif escaped:
                escaped = False
                out.append(' ')
            elif ch == '\\':
                escaped = True
                out.append(' ')
            elif ch == '"':
                in_string = False
                out.append(' ')
            else:
                out.append(' ')
            continue

        if ch == '"':
            in_string = True
            out.append(' ')
        else:
            out.append(ch)

    return ''.join(out)


def extract_exports(lean_dir: Path) -> dict[str, set[str]]:
    """Extract all top-level names exported by each module."""
    exports: dict[str, set[str]] = {}

    for f, module in iter_lean_files(lean_dir):
        text = strip_comments_preserving_newlines(f.read_text(encoding='utf-8'))
        names = set()
        for m in LOCAL_DECL_PATTERN.finditer(text):
            name = m.group(1)
            # Strip type annotations that might be on the same line
            name = name.split('(')[0].split(':')[0].split('{')[0].strip()
            if name:
                names.add(name)
                if '.' in name:
                    names.add(name.rsplit('.', 1)[-1])
        exports[module] = names

    return exports


def extract_local_declarations(text: str) -> set[str]:
    """Extract top-level names declared in one file, including private ones."""
    names: set[str] = set()
    for m in LOCAL_DECL_PATTERN.finditer(text):
        name = m.group(1)
        name = name.split('(')[0].split(':')[0].split('{')[0].strip()
        if name:
            names.add(name)
            if '.' in name:
                names.add(name.rsplit('.', 1)[-1])

    lines = text.splitlines()
    in_inductive = False
    in_structure = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if re.match(r'^(?:private\s+)?inductive\s+\S+', stripped):
            in_inductive = True
            in_structure = False
            continue
        if re.match(r'^(?:private\s+)?structure\s+\S+', stripped):
            in_structure = True
            in_inductive = False
            continue
        if in_inductive:
            ctor = re.match(r'^\|\s*\.?([A-Za-z_][A-Za-z0-9_\']*)', stripped)
            if ctor:
                names.add(ctor.group(1))
                continue
            if stripped and not stripped.startswith('|') and re.match(
                r'^(?:theorem|lemma|def|structure|inductive|class|abbrev|instance|end|namespace|section|open|set_option|#)',
                stripped,
            ):
                in_inductive = False
        if in_structure:
            field = re.match(r'^([A-Za-z_][A-Za-z0-9_\']*)\s*:', stripped)
            if field:
                names.add(field.group(1))
                continue
            if stripped and re.match(
                r'^(?:theorem|lemma|def|structure|inductive|class|abbrev|instance|end|namespace|section|open|set_option|#)',
                stripped,
            ):
                in_structure = False
    return names


def _extract_binder_names(text: str) -> set[str]:
    """Extract theorem-local binder and let/have/fun parameter names."""
    names: set[str] = set()

    for match in re.finditer(r'[\(\{]\s*([^:=\)\}]+?)\s*:', text):
        prefix = match.group(1)
        for name in re.findall(r'\b[A-Za-z_][A-Za-z0-9_\']*\b', prefix):
            if name not in {'Type', 'Prop'}:
                names.add(name)

    for match in re.finditer(r'\b(?:fun|intro|let|have|show|suffices)\s+([A-Za-z_][A-Za-z0-9_\']*)', text):
        names.add(match.group(1))

    for match in re.finditer(r'\b(?:for|from|via|then)\s+([A-Za-z_][A-Za-z0-9_\']*)', text):
        names.add(match.group(1))

    for match in re.finditer(r'^\s*([A-Za-z_][A-Za-z0-9_\']*)\s*:=', text, re.MULTILINE):
        names.add(match.group(1))

    return names


def extract_imports(lean_dir: Path, project: str) -> dict[str, set[str]]:
    """Extract import graph."""
    imports: dict[str, set[str]] = {}
    import_re = re.compile(rf'^import\s+{re.escape(project)}\.(\S+)')
    for f, module in iter_lean_files(lean_dir):
        deps = set()
        text = strip_comments_preserving_newlines(f.read_text(encoding='utf-8'))
        for line in text.splitlines():
            m = import_re.match(line)
            if m:
                deps.add(m.group(1))
        imports[module] = deps
    return imports


def find_cross_references(lean_dir: Path, exports: dict[str, set[str]]) -> list[dict]:
    """Find uses of names defined in other modules, filtering local binders and keywords."""
    issues = []
    providers_by_name: dict[str, set[str]] = {}

    for provider, names in exports.items():
        for name in names:
            if (
                len(name) >= 4
                and name not in IGNORED_CROSS_REFERENCE_NAMES
                and '.' not in name
            ):
                providers_by_name.setdefault(name, set()).add(provider)

    identifier_re = re.compile(r"\b[A-Za-z_][A-Za-z0-9_']*\b")

    for f, module in iter_lean_files(lean_dir):
        text = strip_string_literals_preserving_layout(
            strip_comments_preserving_newlines(f.read_text(encoding='utf-8'))
        )
        local_names = extract_local_declarations(text) | _extract_binder_names(text)
        lines = text.splitlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('import'):
                continue
            if re.match(r'^(?:namespace|end|open|section|variable)\b', stripped):
                continue
            if '`(' in line or 'evalTactic' in line:
                continue

            for match in identifier_re.finditer(line):
                name = match.group(0)
                if name in local_names:
                    continue
                if match.start() > 0 and line[match.start() - 1] == '.':
                    continue

                for other_module in providers_by_name.get(name, set()):
                    if other_module == module:
                        continue
                    issues.append({
                        'user_module': module,
                        'used_name': name,
                        'defined_in': other_module,
                        'line': i,
                    })

    return issues


def validate_bridges(lean_dir: Path, project: str) -> tuple[list[dict], list[dict]]:
    """Main validation: check that cross-module uses have proper imports."""
    exports = extract_exports(lean_dir)
    imports = extract_imports(lean_dir, project)
    import_closure = {
        module: transitive_import_closure(module, imports)
        for module in imports
    }

    cross_refs = find_cross_references(lean_dir, exports)

    missing_imports = []
    valid_bridges = []

    for ref in cross_refs:
        user = ref['user_module']
        visible_modules = import_closure.get(user, set()) | {user}
        visible_providers = {
            candidate
            for candidate, names in exports.items()
            if ref['used_name'] in names and candidate in visible_modules
        }

        # Any visible module exporting the referenced name satisfies it.
        if visible_providers:
            valid_bridges.append(ref)
        else:
            missing_imports.append(ref)

    return valid_bridges, missing_imports


def main():
    parser = argparse.ArgumentParser(description='Validate cross-module bridges for a Lean 4 project')
    parser.add_argument('--lean-dir', type=Path, default=Path('MyProject'),
                        help='Directory containing .lean files')
    parser.add_argument('--project', '--namespace', dest='project', default=None,
                        help='Lean namespace prefix used in local imports (defaults to --lean-dir basename)')
    args = parser.parse_args()

    project = args.project or args.lean_dir.resolve().name
    valid, missing = validate_bridges(args.lean_dir, project)

    print("Cross-Module Bridge Validation")
    print("=" * 50)
    print(f"Valid bridges: {len(valid)}")
    print(f"Missing imports: {len(missing)}")

    if missing:
        print("\nMissing Import Candidates:")
        by_pair = defaultdict(list)
        for m in missing:
            key = (m['user_module'], m['defined_in'])
            by_pair[key].append(m)

        for (user, provider), refs in sorted(by_pair.items()):
            print(f"\n  {user} uses names from {provider} (no import):")
            for ref in refs[:5]:
                print(f"    L{ref['line']}: {ref['used_name']}")
            if len(refs) > 5:
                print(f"    ... and {len(refs) - 5} more")
        sys.exit(1)
    else:
        print("\nAll cross-module references have proper imports.")
        sys.exit(0)


if __name__ == '__main__':
    main()
