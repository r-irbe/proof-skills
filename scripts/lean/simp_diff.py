#!/usr/bin/env python3
"""W14-B2 @[simp] surface drift checker.

Compares the current RL Core/Bellman simp surface against the immutable
pre-Phase-D baseline and routing v2 expectations.

Exit codes:
- 0: clean (exact baseline state or expected post-migration state)
- 2: drift detected
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from simp_baseline import (
    BELLMAN_REL,
    CORE_REL,
    DEFAULT_JSON_OUT,
    ROUTING_PATH,
    capture_simp_entries,
    compact_ws,
)

EXIT_OK = 0
EXIT_DRIFT = 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Diff the current @[simp] surface against the W14-B2 baseline.')
    parser.add_argument('--baseline', type=Path, default=DEFAULT_JSON_OUT,
                        help='Saved baseline JSON to compare against.')
    parser.add_argument('--routing', type=Path, default=ROUTING_PATH,
                        help='Routing v2 JSON used to classify expected Core->Bellman moves.')
    return parser.parse_args(argv)


def load_entries(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    entries = payload.get('entries')
    if not isinstance(entries, list):
        raise ValueError(f'baseline file {path} does not contain an entries list')
    return entries


def identity(entry: dict) -> str:
    return entry.get('qualified_name') or entry['decl_name']


def build_identity_map(entries: list[dict], label: str) -> dict[str, dict]:
    mapping: dict[str, dict] = {}
    duplicates: list[str] = []
    for entry in entries:
        key = identity(entry)
        if key in mapping:
            duplicates.append(key)
        mapping[key] = entry
    if duplicates:
        dup_list = ', '.join(sorted(set(duplicates)))
        raise ValueError(f'duplicate simp declaration identities in {label}: {dup_list}')
    return mapping


def load_migrate_keys(baseline_entries: list[dict], routing_path: Path) -> set[str]:
    routing = json.loads(routing_path.read_text(encoding='utf-8'))
    route_map = {(int(item['line']), item['name']): item for item in routing}
    migrate: set[str] = set()
    for entry in baseline_entries:
        if entry['file'] != CORE_REL:
            continue
        route = route_map.get((int(entry['line']), entry['decl_name']))
        if route and str(route.get('verdict', '')).startswith('MIGRATE'):
            migrate.add(identity(entry))
    return migrate


def same_surface(base: dict, current: dict) -> bool:
    return (
        base['decl_kind'] == current['decl_kind']
        and compact_ws(base.get('signature')) == compact_ws(current.get('signature'))
        and compact_ws(base.get('lhs_pattern')) == compact_ws(current.get('lhs_pattern'))
    )


def fmt_entry(entry: dict) -> str:
    return f"{identity(entry)} ({entry['file']}:{entry['line']})"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        baseline_entries = load_entries(args.baseline)
        current_entries = capture_simp_entries()
        baseline_map = build_identity_map(baseline_entries, 'baseline')
        current_map = build_identity_map(current_entries, 'current state')
        migrate_keys = load_migrate_keys(baseline_entries, args.routing)
    except Exception as err:  # pragma: no cover - CLI failure path
        print(f'ERROR: {err}', file=sys.stderr)
        return EXIT_DRIFT

    added = [current_map[key] for key in sorted(set(current_map) - set(baseline_map))]
    removed = [baseline_map[key] for key in sorted(set(baseline_map) - set(current_map))]
    signature_changes: list[tuple[dict, dict]] = []
    for key in sorted(set(baseline_map) & set(current_map)):
        base = baseline_map[key]
        current = current_map[key]
        if not same_surface(base, current):
            signature_changes.append((base, current))

    unexpected_nonmigrate_moves: list[tuple[dict, dict]] = []
    unexpected_locations: list[tuple[dict, dict]] = []
    migrate_still_in_core: list[tuple[dict, dict]] = []
    migrate_moved_to_bellman: list[tuple[dict, dict]] = []

    for key in sorted(set(baseline_map) & set(current_map)):
        base = baseline_map[key]
        current = current_map[key]
        if key in migrate_keys:
            if current['file'] == base['file']:
                migrate_still_in_core.append((base, current))
            elif current['file'] == BELLMAN_REL:
                migrate_moved_to_bellman.append((base, current))
            else:
                unexpected_locations.append((base, current))
        elif current['file'] != base['file']:
            unexpected_nonmigrate_moves.append((base, current))

    issues: list[str] = []
    if added:
        issues.append(f'added simp declarations: {len(added)}')
    if removed:
        issues.append(f'removed simp declarations: {len(removed)}')
    if signature_changes:
        issues.append(f'signature/lhs drift: {len(signature_changes)}')
    if unexpected_nonmigrate_moves:
        issues.append(f'unexpected file moves for non-migrating decls: {len(unexpected_nonmigrate_moves)}')
    if unexpected_locations:
        issues.append(f'migrating decls moved to unexpected files: {len(unexpected_locations)}')

    baseline_clean = len(migrate_still_in_core) == len(migrate_keys) and not migrate_moved_to_bellman
    post_clean = len(migrate_moved_to_bellman) == len(migrate_keys) and not migrate_still_in_core
    mixed_migration = not baseline_clean and not post_clean
    if mixed_migration:
        issues.append('partial migration state across routing-v2 MIGRATE simp declarations')

    if not issues:
        if post_clean:
            print(f'OK: simp surface matches expected post-migration state ({len(migrate_keys)} routed moves, {len(baseline_entries)} total decls).')
            for base, current in migrate_moved_to_bellman:
                print(f'  moved: {identity(base)} -> {current["file"]}:{current["line"]}')
        else:
            print(f'OK: simp surface matches the saved pre-Phase-D baseline exactly ({len(baseline_entries)} decls).')
        return EXIT_OK

    print('DRIFT: simp surface differs from the saved W14-B2 baseline/expectation set.')
    for issue in issues:
        print(f'- {issue}')

    if added:
        print('Added @[simp] declarations:')
        for entry in added:
            print(f'  + {fmt_entry(entry)}')
    if removed:
        print('Removed @[simp] declarations:')
        for entry in removed:
            print(f'  - {fmt_entry(entry)}')
    if signature_changes:
        print('Signature/LHS drift:')
        for base, current in signature_changes:
            print(f'  * {identity(base)}')
            print(f'    baseline: {compact_ws(base.get("signature"))}')
            print(f'    current : {compact_ws(current.get("signature"))}')
    if unexpected_nonmigrate_moves:
        print('Unexpected moves for non-migrating declarations:')
        for base, current in unexpected_nonmigrate_moves:
            print(f'  * {identity(base)}: {base["file"]} -> {current["file"]}')
    if unexpected_locations:
        print('Migrating declarations moved to unexpected files:')
        for base, current in unexpected_locations:
            print(f'  * {identity(base)}: {base["file"]} -> {current["file"]}')
    if mixed_migration:
        if migrate_moved_to_bellman:
            print('Routed MIGRATE decls already moved to Bellman:')
            for base, current in migrate_moved_to_bellman:
                print(f'  * {identity(base)} -> {current["file"]}:{current["line"]}')
        if migrate_still_in_core:
            print('Routed MIGRATE decls still in Core:')
            for base, current in migrate_still_in_core:
                print(f'  * {identity(base)} @ {current["file"]}:{current["line"]}')

    return EXIT_DRIFT


if __name__ == '__main__':
    sys.exit(main())
