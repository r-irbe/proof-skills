#!/usr/bin/env python3
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
"""
Lean 4 axiom contamination audit.

Discovers declarations in a Lean source tree, optionally generates a Lean
`#print axioms` script, parses captured output, and reports forbidden or
unexpected axiom dependencies by module.

Usage:
    python3 scripts/lean/axiom_audit.py --lean-dir MyProject \
        [--project MyProject] \
        [--axiom-output axiom_output.txt] \
        [--output axiom_audit.md] \
        [--expected-axioms expected_axioms.json]

`--expected-axioms` loads a JSON file containing a list of fully-qualified
axiom names that are expected for your project, for example:

    ["MyProject.Foundations.some_imported_result"]

For a full refresh:
    1. python3 scripts/lean/axiom_audit.py --lean-dir MyProject --generate-script
    2. lake env lean scripts/_axiom_check.lean 2>&1 | tee axiom_output.txt
    3. python3 scripts/lean/axiom_audit.py --lean-dir MyProject
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Axioms that are expected and acceptable
EXPECTED_AXIOMS = {
    'propext',           # Propositional extensionality (Lean core)
    'Quot.sound',        # Quotient soundness (Lean core)
    'Classical.choice',  # Classical choice (used by Mathlib)
}

# Project-specific axioms that are expected and acceptable. Empty by
# default; populate with --expected-axioms JSON list when needed.
PROJECT_EXPECTED_AXIOMS: set[str] = set()

# Axioms that indicate problems
FORBIDDEN_PATTERNS = [
    'sorryAx',           # From sorry — proof incomplete
    'Decidable.decide',  # Sometimes indicates missing decidability
]


AXIOM_DEPS_RE = re.compile(r"^'(.+)' depends on axioms: \[(.*)$")
AXIOM_NONE_RE = re.compile(r"^'(.+)' does not depend on any axioms$")
ERROR_RE = re.compile(r'error(?:\(|:|$)')
NAMESPACE_RE = re.compile(r'^namespace\s+(\S+)$')
SECTION_RE = re.compile(r'^section(?:\s+(\S+))?$')
END_RE = re.compile(r'^end(?:\s+(\S+))?$')
# W19-B1-a3 (W18-R-05 Blocker fix): widened to capture instance / example /
# Prop-valued @[simp] def declarations that were silently dropped pre-W19
# (W18-B4 counted ~265 audit-miss rows attributable to these kinds).  We
# also keep consuming @[...] attribute prefixes and the standard modifier
# bag (noncomputable / private / protected / unsafe / partial / meta /
# local) per common Lean project migration patterns.
DECLARATION_RE = re.compile(
    r'^(?P<attrs>(?:@\[[^\]]*\]\s*)*)'
    r'(?P<modifiers>(?:(?:private|local|protected|noncomputable|unsafe|partial|meta)\s+)*)'
    r'(?P<kind>theorem|lemma|instance|example|def)\b'
    r'(?:\s+(?P<name>[^\s(:{\[\u27e8|]+))?'
    r'(?P<rest>.*)$'
)
# A `def` is only audit-relevant when it carries @[simp] AND returns Prop
# (i.e. it acts as a propositional rewrite rule).  Detected post-match.
SIMP_ATTR_RE = re.compile(r'@\[[^\]]*\bsimp\b[^\]]*\]')
PROP_RETURN_RE = re.compile(r':\s*[^:=]*\bProp\b')

# C240 (Wave 9 HITL, 2026-04-29): scan post-comment-strip source for the raw
# `axiom` keyword.  Previously the script only parsed `#print axioms` output
# captured from a separate Lean run, so any user-introduced `axiom Foo : ...`
# declarations were invisible to this audit.  We now grep the live source as
# well and surface findings in a dedicated section of the report.
RAW_AXIOM_RE = re.compile(
    r'^(?:@\[[^\]]*\]\s*)*'
    r'(?:(?:private|local|protected|noncomputable|unsafe|partial|meta)\s+)*'
    r'axiom\s+(?P<name>[^\s(:{]+)'
)


def strip_comments_preserving_newlines(source: str) -> str:
    """Remove Lean line/doc/block comments while preserving line structure."""
    cleaned: list[str] = []
    i = 0
    block_depth = 0
    line_comment = False

    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ''

        if line_comment:
            if ch == '\n':
                cleaned.append('\n')
                line_comment = False
            i += 1
            continue

        if block_depth > 0:
            if ch == '\n':
                cleaned.append('\n')
                i += 1
            elif ch == '/' and nxt == '-':
                block_depth += 1
                i += 2
            elif ch == '-' and nxt == '/':
                block_depth -= 1
                i += 2
            else:
                i += 1
            continue

        if ch == '/' and nxt == '-':
            if cleaned and not cleaned[-1].isspace():
                cleaned.append(' ')
            block_depth = 1
            i += 2
            continue

        if ch == '-' and nxt == '-':
            line_comment = True
            i += 2
            continue

        cleaned.append(ch)
        i += 1

    return ''.join(cleaned)


def current_namespace(scope_stack: list[tuple[str, str | None, str | None]]) -> str | None:
    """Return the innermost active namespace, if any."""
    for kind, _, full_name in reversed(scope_stack):
        if kind == 'namespace':
            return full_name
    return None


def resolve_namespace_name(name: str, scope_stack: list[tuple[str, str | None, str | None]]) -> str:
    """Resolve a namespace line against the current stack.

    Lean namespace names are relative to the current namespace unless they use
    `_root_.`; preserve already-qualified repeats to avoid double-prefixing.
    """
    if name.startswith('_root_.'):
        return name.removeprefix('_root_.')
    parent = current_namespace(scope_stack)
    if parent is None:
        return name
    if name == parent or name.startswith(f'{parent}.'):
        return name
    return f'{parent}.{name}'


def qualify_declaration_name(name: str, scope_stack: list[tuple[str, str | None, str | None]]) -> str:
    """Resolve a theorem/lemma name against the current namespace stack."""
    if name.startswith('_root_.'):
        return name.removeprefix('_root_.')

    namespace = current_namespace(scope_stack)
    if namespace is None:
        return name
    if name == namespace or name.startswith(f'{namespace}.'):
        return name
    return f'{namespace}.{name}'


def unwind_scope(scope_stack: list[tuple[str, str | None, str | None]], end_name: str | None) -> None:
    """Pop the matching scope for an `end` line, preserving namespace balance."""
    if not scope_stack:
        return

    if end_name is None:
        scope_stack.pop()
        return

    for index in range(len(scope_stack) - 1, -1, -1):
        kind, scope_name, full_name = scope_stack[index]
        candidates = {candidate for candidate in (scope_name, full_name) if candidate is not None}
        if full_name is not None and '.' in full_name:
            candidates.add(full_name.rsplit('.', 1)[-1])
        if end_name in candidates:
            del scope_stack[index:]
            return

    scope_stack.pop()


def extract_theorems_from_file(lean_file: Path) -> list[dict]:
    """Extract theorem names from one Lean file with comment-aware scope tracking.

    W19-B1.5-a1 (B-01 fix): return per-declaration records carrying both the
    qualified `name` and the syntactic `kind` (theorem / lemma / instance /
    example / simp-def), plus an `anon` flag for synthesised `_anon_*`
    surrogates so `generate_axiom_check_script` can drop them and the audit
    table can show them in a dedicated `count_only` bucket instead of
    flipping the module to `script-error (N missing)`.
    """
    scope_stack: list[tuple[str, str | None, str | None]] = []
    names: list[dict] = []

    with open(lean_file, 'r', encoding='utf-8') as f:
        source = strip_comments_preserving_newlines(f.read())

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        namespace_match = NAMESPACE_RE.match(line)
        if namespace_match is not None:
            name = namespace_match.group(1)
            scope_stack.append(('namespace', name, resolve_namespace_name(name, scope_stack)))
            continue

        section_match = SECTION_RE.match(line)
        if section_match is not None:
            scope_stack.append(('section', section_match.group(1), None))
            continue

        end_match = END_RE.match(line)
        if end_match is not None:
            unwind_scope(scope_stack, end_match.group(1))
            continue

        declaration_match = DECLARATION_RE.match(line)
        if declaration_match is None:
            continue

        modifiers = set(declaration_match.group('modifiers').split())
        if {'private', 'local'} & modifiers:
            continue

        kind = declaration_match.group('kind')
        raw_name = declaration_match.group('name')
        attrs = declaration_match.group('attrs') or ''
        rest = declaration_match.group('rest') or ''

        # W19-B1-a3: only Prop-valued @[simp] defs count as audit-relevant.
        if kind == 'def':
            if not SIMP_ATTR_RE.search(attrs):
                continue
            if not PROP_RETURN_RE.search(rest):
                continue

        # W19-B1.5-a1: classify `@[simp] def Prop` as simp-def for the
        # decl_kind column.
        decl_kind = 'simp-def' if kind == 'def' else kind

        # `instance` / `example` are frequently anonymous; synthesise
        # a stable surrogate so the audit counter stays accurate even when
        # `#print axioms` cannot reach them.  These surrogates are *not*
        # emitted into `_axiom_check.lean` (handled in generate_axiom_check_script).
        anon = raw_name is None
        if anon:
            raw_name = f'_anon_{kind}_{lean_file.stem}_{len(names)}'

        name = qualify_declaration_name(raw_name, scope_stack)
        names.append({'name': name, 'kind': decl_kind, 'anon': anon})

    return names


def extract_theorems(lean_dir: Path) -> dict[str, list[dict]]:
    """Extract decl records per module from the live recursive Lean source tree.

    W19-B1.5-a1: values are now `list[dict]` with keys `name`/`kind`/`anon`
    (was `list[str]`).  All downstream consumers in this script have been
    updated; external consumers should call `decl_names(records)` /
    `named_decl_names(records)` helpers below.
    """
    results: dict[str, list[dict]] = {}
    for lean_file in sorted(lean_dir.rglob('*.lean')):
        module = lean_file.relative_to(lean_dir).with_suffix('').as_posix().replace('/', '.')
        records = extract_theorems_from_file(lean_file)
        if records:
            results[module] = records
    return results


# W19-B1.5-a1 helpers (B-01): expose name projections for downstream callers.
def decl_names(records: list[dict]) -> list[str]:
    """Return all qualified names (named + anon) — useful for set membership."""
    return [r['name'] for r in records]


def named_decl_names(records: list[dict]) -> list[str]:
    """Return only names resolvable by `#print axioms`."""
    return [r['name'] for r in records if not r['anon'] and '$' not in r['name']]


def count_only_names(records: list[dict]) -> list[str]:
    """Return declarations tracked by count but not probed with `#print axioms`."""
    return [r['name'] for r in records if r['anon'] or '$' in r['name']]


def kind_breakdown(records: list[dict]) -> dict[str, int]:
    """Return per-kind counts (theorem/lemma/instance/example/simp-def)."""
    out: dict[str, int] = {}
    for r in records:
        out[r['kind']] = out.get(r['kind'], 0) + 1
    return out


def extract_raw_axioms_from_file(lean_file: Path) -> list[tuple[int, str]]:
    """Return (line-number, qualified-name) pairs for every `axiom` declaration.

    The line number refers to the comment-stripped source so it lines up with
    the original file (we preserve newlines while stripping comments).

    W37-B4-a1 (K37-AUDIT-01): the returned name is namespace-qualified using
    the same scope tracker as `extract_theorems_from_file` so raw `axiom`
    decls land in the regular "unexpected axioms" reporting channel under
    their fully-qualified identity (matching how `#print axioms` surfaces
    them and how `PROJECT_EXPECTED_AXIOMS` is keyed).
    """
    with open(lean_file, 'r', encoding='utf-8') as f:
        source = strip_comments_preserving_newlines(f.read())

    scope_stack: list[tuple[str, str | None, str | None]] = []
    findings: list[tuple[int, str]] = []
    for line_no, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        ns_match = NAMESPACE_RE.match(line)
        if ns_match is not None:
            name = ns_match.group(1)
            scope_stack.append(('namespace', name, resolve_namespace_name(name, scope_stack)))
            continue
        sec_match = SECTION_RE.match(line)
        if sec_match is not None:
            scope_stack.append(('section', sec_match.group(1), None))
            continue
        end_match = END_RE.match(line)
        if end_match is not None:
            unwind_scope(scope_stack, end_match.group(1))
            continue
        match = RAW_AXIOM_RE.match(line)
        if match is not None:
            qualified = qualify_declaration_name(match.group('name'), scope_stack)
            findings.append((line_no, qualified))
    return findings


def scan_raw_axioms(lean_dir: Path) -> dict[str, list[tuple[int, str]]]:
    """Source-scan every `.lean` file under `lean_dir` for raw `axiom` decls."""
    results: dict[str, list[tuple[int, str]]] = {}
    for lean_file in sorted(lean_dir.rglob('*.lean')):
        findings = extract_raw_axioms_from_file(lean_file)
        if findings:
            module = lean_file.relative_to(lean_dir).with_suffix('').as_posix().replace('/', '.')
            results[module] = findings
    return results


def generate_axiom_check_script(theorems: dict[str, list[str]], project: str) -> str:
    """Generate a Lean script that prints axioms for all audited theorems."""
    imports = sorted({f'{project}.{module}' for module in theorems})
    lines = [
        *[f'import {module}' for module in imports],
        '',
        '-- Auto-generated axiom audit script',
        '-- Run with: lake env lean scripts/_axiom_check.lean',
        '',
    ]

    for module, records in sorted(theorems.items()):
        lines.append(f'-- Module: {module}')
        for name in named_decl_names(records):
            # W19-B1.5-a1 (B-01): `_anon_*` surrogates are unreachable by
            # `#print axioms`; they are tracked in the count_only bucket
            # via `parse_axiom_output` and rendered in the audit table
            # under the `Count-only` column instead of `script-error`.
            lines.append(f'#print axioms {name}')
        lines.append('')

    return '\n'.join(lines)


def parse_axiom_list(payload: str) -> list[str]:
    """Parse the comma-separated axiom list emitted by `#print axioms`."""
    if ']' in payload:
        payload = payload.split(']', 1)[0]
    return [ax.strip() for ax in payload.replace('\n', ' ').split(',') if ax.strip()]


def record_theorem_report(theorem_name: str, axioms: list[str], theorem_to_module: dict[str, str],
                          module_data: dict[str, dict], unmapped: list[str]) -> None:
    """Accumulate one parsed theorem report into the per-module audit summary."""
    module = theorem_to_module.get(theorem_name)
    if module is None:
        unmapped.append(theorem_name)
        return

    info = module_data[module]
    info['reported'] += 1
    info['missing'].discard(theorem_name)

    forbidden = [ax for ax in axioms if any(pattern in ax for pattern in FORBIDDEN_PATTERNS)]
    unexpected = [
        ax for ax in axioms
        if ax not in EXPECTED_AXIOMS and ax not in PROJECT_EXPECTED_AXIOMS and ax not in forbidden
    ]

    if forbidden:
        info['forbidden'].update(forbidden)
    if unexpected:
        info['unexpected'].update(unexpected)
    if not forbidden and not unexpected:
        info['clean'] += 1


def parse_axiom_output(theorems: dict[str, list[str]], axiom_output: Path,
                      raw_axioms: dict[str, list[tuple[int, str]]] | None = None) -> dict | None:
    """Parse `#print axioms` output into per-module status data.

    Returns `None` when no audit output is available yet.

    W37-B4-a1 (K37-AUDIT-01): if `raw_axioms` is supplied, every raw `axiom`
    declaration is injected into the corresponding module's `unexpected`
    set so it surfaces in the regular reporting channel (previously they
    were source-scan-only).
    """
    if not axiom_output.exists():
        return None

    theorem_to_module: dict[str, str] = {}
    for module, records in theorems.items():
        for name in named_decl_names(records):
            theorem_to_module[name] = module

    # W19-B1.5-a1 (B-01): `missing` is seeded from NAMED decls only so the
    # `script-error (N missing)` status no longer fires on `_anon_*`
    # surrogates that `#print axioms` cannot reach.  Surrogate counts are
    # surfaced separately via `count_only`.
    module_data = {
        module: {
            'theorems': len(records),
            'named': len(named_decl_names(records)),
            'count_only': len(count_only_names(records)),
            'kinds': kind_breakdown(records),
            'reported': 0,
            'clean': 0,
            'forbidden': set(),
            'unexpected': set(),
            'missing': set(named_decl_names(records)),
        }
        for module, records in theorems.items()
    }
    errors: list[str] = []
    unmapped: list[str] = []
    pending_theorem: str | None = None
    pending_axiom_lines: list[str] = []

    with open(axiom_output, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if ERROR_RE.search(line):
                errors.append(line)

            if pending_theorem is not None:
                pending_axiom_lines.append(line)
                if ']' not in line:
                    continue
                record_theorem_report(
                    pending_theorem,
                    parse_axiom_list('\n'.join(pending_axiom_lines)),
                    theorem_to_module,
                    module_data,
                    unmapped,
                )
                pending_theorem = None
                pending_axiom_lines = []
                continue

            theorem_name: str | None = None
            axioms: list[str] = []

            match = AXIOM_DEPS_RE.match(line)
            if match is not None:
                theorem_name = match.group(1)
                axiom_payload = match.group(2)
                if ']' in axiom_payload:
                    axioms = parse_axiom_list(axiom_payload)
                else:
                    pending_theorem = theorem_name
                    pending_axiom_lines = [axiom_payload]
                    continue
            else:
                match = AXIOM_NONE_RE.match(line)
                if match is not None:
                    theorem_name = match.group(1)

            if theorem_name is None:
                continue

            record_theorem_report(theorem_name, axioms, theorem_to_module, module_data, unmapped)

    # W37-B4-a1: inject raw `axiom` declarations into the reported channel.
    if raw_axioms:
        for module, items in raw_axioms.items():
            info = module_data.get(module)
            if info is None:
                continue
            for _, qualified in items:
                
                if qualified not in PROJECT_EXPECTED_AXIOMS:
                    info['unexpected'].add(qualified)

    return {
        'modules': module_data,
        'errors': errors,
        'unmapped': unmapped,
        'total_theorems': sum(len(records) for records in theorems.values()),
        'named_theorems': sum(len(named_decl_names(r)) for r in theorems.values()),
        'count_only_total': sum(len(count_only_names(r)) for r in theorems.values()),
        'reported_theorems': sum(info['reported'] for info in module_data.values()),
        'clean_theorems': sum(info['clean'] for info in module_data.values()),
        'forbidden_module_count': sum(1 for info in module_data.values() if info['forbidden']),
        'unexpected_module_count': sum(1 for info in module_data.values() if info['unexpected']),
    }


def module_status(module_info: dict) -> tuple[str, str]:
    """Compute a human-readable status and notes cell for one module.

    `missing` is counted against the NAMED-decl cohort only; `_anon_*`
    surrogates and generated dollar-sigil names live in the `count_only`
    bucket and never trigger `script-error`.  When a module has zero named
    decls but non-zero count_only decls, status is `count-only` (no axiom
    probe possible).
    """
    missing_count = len(module_info['missing'])
    named = module_info.get('named', module_info['theorems'])
    count_only = module_info.get('count_only', 0)
    if missing_count > 0:
        return (
            f'script-error ({missing_count} missing)',
            f"reported {module_info['reported']}/{named} (+{count_only} count-only)"
        )
    if module_info['forbidden']:
        forbidden = ', '.join(sorted(module_info['forbidden']))
        return ('forbidden', forbidden)
    if module_info['unexpected']:
        unexpected = ', '.join(sorted(module_info['unexpected']))
        return ('unexpected axioms', unexpected)
    if named == 0 and count_only > 0:
        return ('count-only', f'{count_only} unprobeable decls (no #print axioms probe)')
    return ('clean', f"reported {module_info['reported']}/{named} (+{count_only} count-only)")


def generate_report(theorems: dict[str, list[dict]], output: Path, analysis: dict | None,
                    raw_axioms: dict[str, list[tuple[int, str]]] | None = None) -> None:
    """Generate the axiom audit report, optionally populated from audit output.

    W19-B1.5-a1 (B-01): table now carries a `decl_kind` breakdown column
    (theorem / lemma / instance / example / simp-def) and a `Count-only`
    column for anonymous/generated names that cannot be probed by
    `#print axioms`.
    """
    total_theorems = sum(len(records) for records in theorems.values())
    total_named = sum(len(named_decl_names(r)) for r in theorems.values())
    total_count_only = sum(len(count_only_names(r)) for r in theorems.values())

    report_lines = [
        '# Axiom Audit Report',
        '## Generated: 2026-04-29',
        '',
        '## Summary',
        f'- Modules: {len(theorems)}',
        f'- Total declarations: {total_theorems}',
        f'- Named (axiom-probeable): {total_named}',
        f'- Count-only (unprobeable by `#print axioms`): {total_count_only}',
        f'- Standard expected axioms: {", ".join(sorted(EXPECTED_AXIOMS))}',
        f'- Forbidden patterns: {", ".join(FORBIDDEN_PATTERNS)}',
    ]

    if raw_axioms is None:
        report_lines.append('- Source-scan for `axiom` keyword: skipped')
    else:
        total_raw = sum(len(items) for items in raw_axioms.values())
        report_lines.append(
            f'- Source-scan for `axiom` keyword: {total_raw} declarations across {len(raw_axioms)} modules'
        )
        # Reconcile raw source axioms against the project-specific expected list.
        all_raw = [qn for items in raw_axioms.values() for _, qn in items]
        expected_hits = [qn for qn in all_raw if qn in PROJECT_EXPECTED_AXIOMS]
        report_lines.append(
            f'- Project-expected source axioms: source = {len(all_raw)}, '
            f'expected = {len(expected_hits)}, '
            f'source − expected = {len(all_raw) - len(expected_hits)}, '
            f"script-error = {len(analysis['errors']) if analysis is not None else 0}"
        )

    if analysis is None:
        report_lines.append('- Audit output parsed: no (run the generated Lean script first)')
    else:
        report_lines.extend([
            '- Audit output parsed: yes (`axiom_output.txt`)',
            f"- Reported theorems: {analysis['reported_theorems']}/{analysis['total_theorems']}",
            f"- Clean theorem reports: {analysis['clean_theorems']}",
            f"- Modules with forbidden axioms: {analysis['forbidden_module_count']}",
            f"- Modules with unexpected axioms: {analysis['unexpected_module_count']}",
            f"- Script / lookup errors: {len(analysis['errors'])}",
        ])

    report_lines.extend([
        '',
        '## Per-Module Status',
        '',
        '| Module | Decls | Decl kinds (thm/lem/inst/ex/simp) | Count-only | Status | Notes |',
        '|---|---:|---|---:|---|---|',
    ])

    KIND_ORDER = ['theorem', 'lemma', 'instance', 'example', 'simp-def']
    for module, records in sorted(theorems.items()):
        kb = kind_breakdown(records)
        kind_cell = '/'.join(str(kb.get(k, 0)) for k in KIND_ORDER)
        co = len(count_only_names(records))
        if analysis is None:
            report_lines.append(
                f'| {module} | {len(records)} | {kind_cell} | {co} | pending | awaiting audit output |'
            )
        else:
            status, notes = module_status(analysis['modules'][module])
            report_lines.append(
                f'| {module} | {len(records)} | {kind_cell} | {co} | {status} | {notes} |'
            )

    if analysis is not None and analysis['errors']:
        report_lines.extend([
            '',
            '## Script / Lookup Errors',
            '',
        ])
        report_lines.extend([f'- `{line}`' for line in analysis['errors'][:20]])

    if analysis is not None and analysis['unmapped']:
        report_lines.extend([
            '',
            '## Unmapped Theorem Lines',
            '',
        ])
        report_lines.extend([f'- `{name}`' for name in analysis['unmapped'][:20]])

    # C240 (Wave 9 HITL, 2026-04-29): always include a source-scan section so
    # any locally-introduced `axiom` keyword surfaces here regardless of
    # whether `#print axioms` was rerun.
    report_lines.extend([
        '',
        '## Source Scan: `axiom` Keyword Declarations',
        '',
    ])
    if raw_axioms is None:
        report_lines.append('Source scan was not performed.')
    elif not raw_axioms:
        report_lines.append(
            'No `axiom` declarations found in any `.lean` file under the audit root.'
        )
    else:
        report_lines.append('| Module | Line | Name |')
        report_lines.append('|---|---:|---|')
        for module in sorted(raw_axioms.keys()):
            for line_no, name in raw_axioms[module]:
                report_lines.append(f'| {module} | {line_no} | `{name}` |')

    report_lines.extend([
        '',
        '## Instructions',
        '',
        'Refresh the generated Lean script, run it, then regenerate this report:',
        '```bash',
        'python3 scripts/lean/axiom_audit.py --lean-dir MyProject --project MyProject --generate-script',
        'lake env lean scripts/_axiom_check.lean 2>&1 | tee axiom_output.txt',
        'python3 scripts/lean/axiom_audit.py --lean-dir MyProject --project MyProject',
        '```',
        '',
        'A clean module report should show only standard axioms or no axioms at all.',
    ])

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines) + '\n')


def load_expected_axioms(path: Path | None) -> set[str]:
    """Load a JSON list of fully-qualified expected axiom names."""
    if path is None:
        return set()
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise ValueError('--expected-axioms must be a JSON list of strings')
    return set(data)


def main():
    parser = argparse.ArgumentParser(description='Lean 4 axiom contamination audit')
    parser.add_argument('--lean-dir', type=Path, default=Path('MyProject'),
                        help='Directory containing .lean files')
    parser.add_argument('--project', default='MyProject',
                        help='Lean namespace prefix used for generated imports')
    parser.add_argument('--expected-axioms', type=Path, default=None,
                        help='JSON file containing a list of fully-qualified expected axiom names')
    parser.add_argument('--output', type=Path, default=Path('axiom_audit.md'),
                        help='Output report path')
    parser.add_argument('--axiom-output', type=Path, default=Path('axiom_output.txt'),
                        help='Captured output of the generated Lean axiom check script')
    parser.add_argument('--generate-script', action='store_true',
                        help='Also generate the Lean axiom check script')
    args = parser.parse_args()

    global PROJECT_EXPECTED_AXIOMS
    try:
        PROJECT_EXPECTED_AXIOMS = load_expected_axioms(args.expected_axioms)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: could not load --expected-axioms: {exc}", file=sys.stderr)
        sys.exit(2)

    theorems = extract_theorems(args.lean_dir)

    if not theorems:
        print(f"No theorems found in {args.lean_dir}")
        sys.exit(1)

    total = sum(len(v) for v in theorems.values())
    named = sum(len(named_decl_names(v)) for v in theorems.values())
    count_only = sum(len(count_only_names(v)) for v in theorems.values())
    print(f"Found {total} declarations ({named} named, {count_only} count-only) across {len(theorems)} modules")

    raw_axioms = scan_raw_axioms(args.lean_dir)
    raw_total = sum(len(v) for v in raw_axioms.values())
    print(f"Source scan: {raw_total} `axiom` declarations across {len(raw_axioms)} modules")

    analysis = parse_axiom_output(theorems, args.axiom_output, raw_axioms=raw_axioms)
    generate_report(theorems, args.output, analysis, raw_axioms=raw_axioms)
    print(f"Report written to {args.output}")

    all_raw = [qn for items in raw_axioms.values() for _, qn in items]
    expected_hits = [qn for qn in all_raw if qn in PROJECT_EXPECTED_AXIOMS]
    source_n = len(all_raw)
    expected_n = len(expected_hits)
    delta = source_n - expected_n
    script_err = len(analysis['errors']) if analysis is not None else 0
    print(
        f"Project-expected source axioms: source = {source_n}, "
        f"expected = {expected_n}, "
        f"source − expected = {delta}, "
        f"script-error = {script_err}"
    )

    if args.generate_script:
        script_path = Path('scripts/_axiom_check.lean')
        script_content = generate_axiom_check_script(theorems, args.project)
        script_path.parent.mkdir(parents=True, exist_ok=True)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"Lean axiom check script written to {script_path}")
        print(f"Run: lake env lean {script_path}")


if __name__ == '__main__':
    main()
