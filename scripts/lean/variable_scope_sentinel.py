#!/usr/bin/env python3
"""W14-B2 Phase D F2 sentinel for Bellman.lean.

Scans `EASCI/ReinforcementLearning/Core/Bellman.lean` for declarations that
appear to rely on scoped `variable` contamination from `Core.lean`:

- `[Fintype MDPState]`
- `[Fintype GovAction]`
- `[DecidableEq MDPState]`
- `{Ω : Type*}` / `{Ω : Type u}`
- `{m0 : MeasurableSpace Ω}`
- `{μ : Measure Ω}`
- `{ℱ : Filtration ℕ m0}`

The sentinel is deliberately heuristic and biased toward warning rather than
silently missing a contaminated declaration. Exit status:

- 0: clean
- 2: one or more likely contamination violations
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import os as _os
import sys as _sys
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in _sys.path:
    _sys.path.insert(0, str(_HERE))
try:
    from project_config import load_project_config
    _CFG = load_project_config()
    REPO = _CFG.root
except Exception:
    REPO = Path(_os.environ.get("LEAN_PROJECT_ROOT", Path.cwd())).resolve()
DEFAULT_TARGET = REPO / _os.environ.get("VARIABLE_SENTINEL_TARGET", "EASCI/ReinforcementLearning/Core/Bellman.lean")
EXIT_OK = 0
EXIT_VIOLATIONS = 2

DECL_START_RE = re.compile(
    r'^\s*(?:@\[[^\]]+\]\s*)*'
    r'(?:(?:unsafe|noncomputable|protected|private|local|scoped)\s+)*'
    r'(theorem|lemma|def|instance)\b'
)
SECTION_START_RE = re.compile(r'^\s*(?:noncomputable\s+)?(?:section|namespace)\b')
END_RE = re.compile(r'^\s*end\b')
VARIABLE_RE = re.compile(r'^\s*variable\b')
OMIT_RE = re.compile(r'^\s*omit\b')
INCLUDE_RE = re.compile(r'^\s*include\b')
IDENTIFIER_RE = re.compile(r'((?:_root_\.)?[A-Za-z_][\w\'.]*(?:\.(?:[A-Za-z_][\w\'.]*))*)')


@dataclass(frozen=True)
class RequirementSpec:
    key: str
    label: str
    explicit_patterns: tuple[re.Pattern[str], ...]
    inference_patterns: tuple[re.Pattern[str], ...]


@dataclass
class Declaration:
    kind: str
    name: str
    start_line: int
    end_line: int
    text: str
    clean_text: str
    header_text: str
    active_requirements: frozenset[str]


@dataclass
class Violation:
    declaration: Declaration
    missing_keys: list[str]
    evidence: dict[str, list[tuple[int, str]]]


REQ_SPECS: tuple[RequirementSpec, ...] = (
    RequirementSpec(
        key='fintype_mdpstate',
        label='[Fintype MDPState]',
        explicit_patterns=(
            re.compile(r'\[[^\]]*\bFintype\s+MDPState\b[^\]]*\]'),
        ),
        inference_patterns=(
            re.compile(r'Fintype\.card\s+MDPState\b'),
            re.compile(r'Fintype\.equivFin\s+MDPState\b'),
            re.compile(r'∑\s+[^\n]*:\s*MDPState\b'),
            re.compile(r'Finset\.univ[^\n]*\bMDPState\b'),
            re.compile(r'\bMDPState\s*×\s*GovAction\b[^\n]*(?:Finset\.univ|Fintype\.card)'),
            re.compile(r'(?:Finset\.univ|Fintype\.card)[^\n]*\bMDPState\s*×\s*GovAction\b'),
        ),
    ),
    RequirementSpec(
        key='fintype_govaction',
        label='[Fintype GovAction]',
        explicit_patterns=(
            re.compile(r'\[[^\]]*\bFintype\s+GovAction\b[^\]]*\]'),
        ),
        inference_patterns=(
            re.compile(r'Fintype\.card\s+GovAction\b'),
            re.compile(r'Fintype\.equivFin\s+GovAction\b'),
            re.compile(r'∑\s+[^\n]*:\s*GovAction\b'),
            re.compile(r'Finset\.univ[^\n]*\bGovAction\b'),
            re.compile(r'\bMDPState\s*×\s*GovAction\b[^\n]*(?:Finset\.univ|Fintype\.card)'),
            re.compile(r'(?:Finset\.univ|Fintype\.card)[^\n]*\bMDPState\s*×\s*GovAction\b'),
        ),
    ),
    RequirementSpec(
        key='decidable_eq_mdpstate',
        label='[DecidableEq MDPState]',
        explicit_patterns=(
            re.compile(r'\[[^\]]*\bDecidableEq\s+MDPState\b[^\]]*\]'),
        ),
        inference_patterns=(
            re.compile(r'Finset\.(?:univ\.)?filter'),
            re.compile(r'Finset\.disjoint_filter'),
            re.compile(r'Finset\.mem_filter'),
            re.compile(r'Finset\.erase'),
        ),
    ),
    RequirementSpec(
        key='omega_type',
        label='{Ω : Type*}',
        explicit_patterns=(
            re.compile(r'\bΩ\s*:\s*Type(?:\s*\*|\s+[A-Za-z0-9_\'.]+|\s+_)?'),
        ),
        inference_patterns=(
            re.compile(r'\bΩ\b'),
        ),
    ),
    RequirementSpec(
        key='measurable_space_omega',
        label='{_ : MeasurableSpace Ω}',
        explicit_patterns=(
            re.compile(r':\s*(?:[A-Za-z0-9_.]+\.)?MeasurableSpace\s+Ω\b'),
        ),
        inference_patterns=(
            re.compile(r'(?:[A-Za-z0-9_.]+\.)?Measure\s+Ω\b'),
            re.compile(r'\bFiltration\b'),
            re.compile(r'\bSubmartingale\b'),
            re.compile(r'\bSupermartingale\b'),
            re.compile(r'\b∀ᵐ\b'),
            re.compile(r'∂μ'),
        ),
    ),
    RequirementSpec(
        key='mu_measure',
        label='{μ : Measure Ω}',
        explicit_patterns=(
            re.compile(r'\bμ\s*:\s*(?:[A-Za-z0-9_.]+\.)?Measure\s+Ω\b'),
        ),
        inference_patterns=(
            re.compile(r'\bμ\b'),
            re.compile(r'∂μ'),
            re.compile(r'\beLpNorm\b[^\n]*\bμ\b'),
        ),
    ),
    RequirementSpec(
        key='m0_measurable_space',
        label='{m0 : MeasurableSpace Ω}',
        explicit_patterns=(
            re.compile(r'\bm0\s*:\s*(?:[A-Za-z0-9_.]+\.)?MeasurableSpace\s+Ω\b'),
        ),
        inference_patterns=(
            re.compile(r'\bm0\b'),
        ),
    ),
    RequirementSpec(
        key='filtration_F',
        label='{ℱ : Filtration ℕ m0}',
        explicit_patterns=(
            re.compile(r'\bℱ\s*:\s*(?:[A-Za-z0-9_.]+\.)?Filtration\b'),
        ),
        inference_patterns=(
            re.compile(r'\bℱ\b'),
            re.compile(r'\bSubmartingale\b'),
            re.compile(r'\bSupermartingale\b'),
        ),
    ),
)
REQ_BY_KEY = {spec.key: spec for spec in REQ_SPECS}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Detect W14-B2 F2 variable/typeclass contamination in Bellman.lean.'
    )
    parser.add_argument(
        '--path',
        type=Path,
        default=DEFAULT_TARGET,
        help='Lean file to scan (default: %(default)s)',
    )
    return parser.parse_args(argv)


def strip_comments_preserve_layout(text: str) -> str:
    """Replace Lean comments with spaces while preserving line numbers."""
    out: list[str] = []
    i = 0
    block_depth = 0
    in_string = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ''

        if block_depth > 0:
            if ch == '\n':
                out.append('\n')
                i += 1
                continue
            if ch == '/' and nxt == '-':
                out.extend((' ', ' '))
                block_depth += 1
                i += 2
                continue
            if ch == '-' and nxt == '/':
                out.extend((' ', ' '))
                block_depth -= 1
                i += 2
                continue
            out.append(' ')
            i += 1
            continue

        if in_string:
            out.append(ch)
            if ch == '\\' and i + 1 < len(text):
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == '/' and nxt == '-':
            out.extend((' ', ' '))
            block_depth = 1
            i += 2
            continue

        if ch == '-' and nxt == '-':
            out.extend((' ', ' '))
            i += 2
            while i < len(text) and text[i] != '\n':
                out.append(' ')
                i += 1
            continue

        out.append(ch)
        i += 1

    return ''.join(out)


def collect_indented_block(lines: list[str], start_idx: int) -> str:
    parts = [lines[start_idx]]
    idx = start_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == '':
            parts.append(line)
            idx += 1
            continue
        if line[:1].isspace():
            parts.append(line)
            idx += 1
            continue
        break
    return '\n'.join(parts)


def find_decl_end(lines: list[str], start_idx: int) -> int:
    end_idx = start_idx
    idx = start_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == '':
            idx += 1
            continue
        if line[:1].isspace():
            end_idx = idx
            idx += 1
            continue
        break
    return end_idx + 1  # 1-indexed inclusive


def split_header(clean_text: str) -> str:
    depth_round = 0
    depth_curly = 0
    depth_square = 0
    in_string = False
    idx = 0
    while idx < len(clean_text):
        ch = clean_text[idx]
        if in_string:
            if ch == '\\' and idx + 1 < len(clean_text):
                idx += 2
                continue
            if ch == '"':
                in_string = False
            idx += 1
            continue
        if ch == '"':
            in_string = True
            idx += 1
            continue
        if ch == '(':
            depth_round += 1
        elif ch == ')':
            depth_round = max(depth_round - 1, 0)
        elif ch == '{':
            depth_curly += 1
        elif ch == '}':
            depth_curly = max(depth_curly - 1, 0)
        elif ch == '[':
            depth_square += 1
        elif ch == ']':
            depth_square = max(depth_square - 1, 0)
        elif depth_round == depth_curly == depth_square == 0:
            if clean_text.startswith(':=', idx):
                return clean_text[:idx]
            if clean_text.startswith('where', idx):
                prev_ok = idx == 0 or clean_text[idx - 1].isspace()
                next_idx = idx + len('where')
                next_ok = next_idx >= len(clean_text) or clean_text[next_idx].isspace()
                if prev_ok and next_ok:
                    return clean_text[:idx]
        idx += 1
    return clean_text


def extract_decl_name(kind: str, line: str, line_no: int) -> str:
    match = DECL_START_RE.match(line)
    if not match:
        return f'<unknown@L{line_no}>'
    rest = line[match.end():].lstrip()
    if kind == 'instance' and rest[:1] in ':([{':
        return f'instance@L{line_no}'
    name_match = IDENTIFIER_RE.match(rest)
    if name_match:
        return name_match.group(1)
    return f'{kind}@L{line_no}'


def requirements_from_text(text: str) -> set[str]:
    found: set[str] = set()
    for spec in REQ_SPECS:
        if any(pattern.search(text) for pattern in spec.explicit_patterns):
            found.add(spec.key)
    return found


def compute_active_requirements_by_line(clean_lines: list[str]) -> list[frozenset[str]]:
    active = set()
    snapshots: list[set[str]] = []
    active_before: list[frozenset[str]] = [frozenset() for _ in range(len(clean_lines) + 1)]
    for line_no, line in enumerate(clean_lines, start=1):
        active_before[line_no] = frozenset(active)
        if line.strip() == '':
            continue
        if SECTION_START_RE.match(line):
            snapshots.append(set(active))
            continue
        if END_RE.match(line):
            if snapshots:
                active = snapshots.pop()
            continue
        if VARIABLE_RE.match(line):
            active |= requirements_from_text(collect_indented_block(clean_lines, line_no - 1))
            continue
        if OMIT_RE.match(line):
            active -= requirements_from_text(collect_indented_block(clean_lines, line_no - 1))
            continue
        if INCLUDE_RE.match(line):
            active |= requirements_from_text(collect_indented_block(clean_lines, line_no - 1))
            continue
    return active_before


def parse_declarations(raw_lines: list[str], clean_lines: list[str], active_by_line: list[frozenset[str]]) -> list[Declaration]:
    declarations: list[Declaration] = []
    for idx, clean_line in enumerate(clean_lines, start=1):
        match = DECL_START_RE.match(clean_line)
        if not match:
            continue
        kind = match.group(1)
        end_line = find_decl_end(clean_lines, idx - 1)
        raw_text = '\n'.join(raw_lines[idx - 1:end_line])
        clean_text = '\n'.join(clean_lines[idx - 1:end_line])
        declarations.append(
            Declaration(
                kind=kind,
                name=extract_decl_name(kind, clean_line, idx),
                start_line=idx,
                end_line=end_line,
                text=raw_text,
                clean_text=clean_text,
                header_text=split_header(clean_text),
                active_requirements=active_by_line[idx],
            )
        )
    return declarations


def infer_requirements(decl: Declaration) -> set[str]:
    inferred: set[str] = set()
    text = decl.clean_text
    for spec in REQ_SPECS:
        if spec.key == 'decidable_eq_mdpstate':
            has_decidable_trigger = any(pattern.search(text) for pattern in spec.inference_patterns)
            if has_decidable_trigger and 'MDPState' in text:
                inferred.add(spec.key)
            continue
        if any(pattern.search(text) for pattern in spec.inference_patterns):
            inferred.add(spec.key)
    return inferred


def explicit_requirements(decl: Declaration) -> set[str]:
    return requirements_from_text(decl.header_text)


def collect_evidence(decl: Declaration, key: str) -> list[tuple[int, str]]:
    spec = REQ_BY_KEY[key]
    evidence: list[tuple[int, str]] = []
    for offset, line in enumerate(decl.clean_text.splitlines(), start=0):
        if any(pattern.search(line) for pattern in spec.inference_patterns):
            snippet = decl.text.splitlines()[offset].strip()
            if snippet:
                evidence.append((decl.start_line + offset, snippet))
    return evidence[:3]


def analyze_declarations(declarations: list[Declaration]) -> list[Violation]:
    violations: list[Violation] = []
    for decl in declarations:
        inferred = infer_requirements(decl)
        explicit = explicit_requirements(decl)
        available = set(decl.active_requirements) | explicit
        missing = sorted(key for key in inferred if key not in available)
        if missing:
            evidence = {key: collect_evidence(decl, key) for key in missing}
            violations.append(Violation(declaration=decl, missing_keys=missing, evidence=evidence))
    return violations


def format_report(path: Path, declarations: list[Declaration], violations: list[Violation]) -> str:
    rel_path = path.relative_to(REPO) if path.is_absolute() and path.is_relative_to(REPO) else path
    lines: list[str] = []
    if not violations:
        lines.append(
            f'OK: scanned {len(declarations)} theorem/lemma/def/instance declarations in {rel_path}; 0 F2 contamination violations.'
        )
        return '\n'.join(lines)

    lines.append(
        f'F2 contamination violations in {rel_path}: {len(violations)} declaration(s) flagged.'
    )
    for item in violations:
        decl = item.declaration
        labels = ', '.join(REQ_BY_KEY[key].label for key in item.missing_keys)
        lines.append(
            f'- L{decl.start_line}-{decl.end_line} {decl.kind} {decl.name}: missing {labels}'
        )
        for key in item.missing_keys:
            snippets = item.evidence.get(key) or []
            for line_no, snippet in snippets:
                lines.append(f'    evidence L{line_no}: {snippet}')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = args.path.resolve()
    try:
        raw_text = path.read_text(encoding='utf-8')
    except OSError as err:
        print(f'error: cannot read {path}: {err}', file=sys.stderr)
        return 1

    clean_text = strip_comments_preserve_layout(raw_text)
    raw_lines = raw_text.splitlines()
    clean_lines = clean_text.splitlines()
    active_by_line = compute_active_requirements_by_line(clean_lines)
    declarations = parse_declarations(raw_lines, clean_lines, active_by_line)
    violations = analyze_declarations(declarations)
    print(format_report(path, declarations, violations))
    return EXIT_VIOLATIONS if violations else EXIT_OK


if __name__ == '__main__':
    raise SystemExit(main())
