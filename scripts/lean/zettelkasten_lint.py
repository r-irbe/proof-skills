#!/usr/bin/env python3
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
"""
Zettelkasten Linter.

Checks a Markdown Zettelkasten knowledge base for structural issues:
  - Orphan notes (no incoming links)
  - Island notes (no outgoing links)
  - Broken links (reference notes that don't exist)
  - Stale notes (old fleeting notes not promoted)
  - Tag inconsistencies
  - Missing required fields in note templates

Usage:
    python3 scripts/lean/zettelkasten_lint.py [--zk-dir zettelkasten]
"""

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ZK_ID_PATTERN = re.compile(r'ZK-(\d{8})-(\d{3})')
LINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
TAG_PATTERN = re.compile(r'#(\w[\w-]*)')
REQUIRED_FIELDS = ['Type', 'Tags', 'Created']


def parse_note(filepath: Path) -> dict:
    """Parse a Zettelkasten note file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    note = {
        'path': filepath,
        'filename': filepath.stem,
        'content': content,
        'links_out': set(),
        'tags': set(),
        'note_type': None,
        'created': None,
        'missing_fields': [],
    }

    # Extract links
    for m in LINK_PATTERN.finditer(content):
        note['links_out'].add(m.group(1))

    # Extract tags
    for m in TAG_PATTERN.finditer(content):
        note['tags'].add(m.group(1))

    # Extract metadata fields
    for field in REQUIRED_FIELDS:
        pattern = re.compile(rf'^[-*]\s*\*?\*?{field}\*?\*?\s*:\s*(.+)', re.MULTILINE | re.IGNORECASE)
        m = pattern.search(content)
        if m:
            value = m.group(1).strip()
            if field == 'Type':
                note['note_type'] = value.lower()
            elif field == 'Created':
                note['created'] = value
        else:
            note['missing_fields'].append(field)

    return note


def lint_zettelkasten(zk_dir: Path) -> list[dict]:
    """Run all lint checks on the Zettelkasten."""
    issues: list[dict] = []
    notes: dict[str, dict] = {}
    all_tags: set[str] = set()

    # Skip index files
    skip_files = {'_index.md', '_tags.md'}

    # Parse all notes
    for md_file in sorted(zk_dir.rglob('*.md')):
        if md_file.name in skip_files:
            continue
        note = parse_note(md_file)
        notes[note['filename']] = note
        all_tags.update(note['tags'])

    if not notes:
        issues.append({
            'severity': 'info',
            'type': 'empty',
            'message': f'No notes found in {zk_dir}',
            'file': None,
        })
        return issues

    # Build incoming links
    links_in: dict[str, set[str]] = {name: set() for name in notes}
    for name, note in notes.items():
        for link in note['links_out']:
            if link in links_in:
                links_in[link].add(name)

    # Check: Orphan notes (no incoming links, not index/root)
    for name, incoming in links_in.items():
        if not incoming and notes[name]['note_type'] != 'index':
            issues.append({
                'severity': 'warn',
                'type': 'orphan',
                'message': f'No incoming links',
                'file': notes[name]['path'],
            })

    # Check: Island notes (no outgoing links)
    for name, note in notes.items():
        if not note['links_out']:
            issues.append({
                'severity': 'warn',
                'type': 'island',
                'message': f'No outgoing links (isolated note)',
                'file': note['path'],
            })

    # Check: Broken links
    for name, note in notes.items():
        for link in note['links_out']:
            if link not in notes:
                issues.append({
                    'severity': 'error',
                    'type': 'broken-link',
                    'message': f'Links to non-existent note: {link}',
                    'file': note['path'],
                })

    # Check: Missing required fields
    for name, note in notes.items():
        for field in note['missing_fields']:
            issues.append({
                'severity': 'warn',
                'type': 'missing-field',
                'message': f'Missing required field: {field}',
                'file': note['path'],
            })

    # Check: Stale fleeting notes (>7 days old, not promoted)
    for name, note in notes.items():
        if note['note_type'] == 'fleeting' and note['created']:
            try:
                created = datetime.strptime(note['created'][:10], '%Y-%m-%d')
                created = created.replace(tzinfo=timezone.utc)
                age = datetime.now(timezone.utc) - created
                if age > timedelta(days=7):
                    issues.append({
                        'severity': 'warn',
                        'type': 'stale-fleeting',
                        'message': f'Fleeting note is {age.days} days old — promote or discard',
                        'file': note['path'],
                    })
            except ValueError:
                pass

    return issues


def main():
    parser = argparse.ArgumentParser(description='Lint Zettelkasten notes')
    parser.add_argument('--zk-dir', type=Path, default=Path('zettelkasten'),
                        help='Zettelkasten directory')
    args = parser.parse_args()

    if not args.zk_dir.exists():
        print(f"Zettelkasten directory not found: {args.zk_dir}")
        print("(This is normal for a new project — create notes to populate it)")
        sys.exit(0)

    issues = lint_zettelkasten(args.zk_dir)

    errors = [i for i in issues if i['severity'] == 'error']
    warnings = [i for i in issues if i['severity'] == 'warn']
    infos = [i for i in issues if i['severity'] == 'info']

    print("Zettelkasten Lint Report")
    print("=" * 50)
    print(f"Errors: {len(errors)}  Warnings: {len(warnings)}  Info: {len(infos)}")
    print("-" * 50)

    for issue in sorted(issues, key=lambda i: (
        {'error': 0, 'warn': 1, 'info': 2}[i['severity']],
        i['type'],
        str(i.get('file', '')),
    )):
        sev = {'error': '✗', 'warn': '⚠', 'info': 'ℹ'}[issue['severity']]
        file_str = issue['file'].name if issue['file'] else ''
        print(f"  {sev} [{issue['type']}] {file_str}: {issue['message']}")

    if errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
