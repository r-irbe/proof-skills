#!/usr/bin/env python3
"""Axiom-profile tiers over the corpus's declaration listing.

Recreated 2026-10-16: the original tool was referenced by AXIOM_PROFILES.md
but was never committed and was lost to a working-tree clobber; this
reconstruction reads the canonical audit listing instead of probing the
build itself, so it needs no lake environment.

Classification (per named, axiom-probeable declaration):
  - constructive        : no axioms at all
  - standard-classical  : every dependency within {propext, Quot.sound,
                          Classical.choice} (Lean's standard classical trio)
  - non-standard        : anything else (the failure class; must be 0)

Usage: python3 tools/altproof/axiom_profiles.py [listing path]
Default listing: docs/easci/lean/docs/tracking/axiom_output.txt
Regenerate the listing first with:
  cd docs/easci/lean && python3 scripts/axiom_audit.py --generate-script \
    && lake env lean scripts/_axiom_check.lean > docs/tracking/axiom_output.txt
"""
import re
import sys

STD = {'propext', 'Quot.sound', 'Classical.choice'}


def parse_listing(path):
    text = open(path, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r"^'(.+?)'\s+depends on axioms:\s*\[([^\]]*)\]", text, re.M | re.S):
        deps = [a.strip() for a in m.group(2).replace('\n', ' ').split(',') if a.strip()]
        out[m.group(1)] = deps
    for m in re.finditer(r"^'(.+?)'\s+does not depend on any axioms", text, re.M):
        out[m.group(1)] = []
    return out


def main(argv=None):
    import argparse
    import os
    default_listing = (
        'docs/tracking/axiom_output.txt'
        if os.path.exists('docs/tracking/axiom_output.txt')
        else 'docs/easci/lean/docs/tracking/axiom_output.txt'
    )
    parser = argparse.ArgumentParser(description="Axiom-profile tiers over a Lean corpus's declaration listing.")
    parser.add_argument("pos_listing", nargs="?", default=None, help="Optional positional path to axiom_output.txt")
    parser.add_argument("--listing", default=default_listing, help="Path to axiom_output.txt")
    parser.add_argument(
        "--allow-axioms",
        default=None,
        help="Comma-separated allowed standard axioms (defaults to propext,Quot.sound,Classical.choice)",
    )
    parser.add_argument(
        "--extra-axioms",
        default=os.environ.get("ALTPROOF_EXTRA_AXIOMS", ""),
        help="Comma-separated additional allowed custom axioms",
    )
    args = parser.parse_args(argv)
    listing = args.pos_listing if args.pos_listing is not None else args.listing
    allowed = (
        {a.strip() for a in args.allow_axioms.split(",") if a.strip()}
        if args.allow_axioms is not None
        else set(STD)
    )
    if args.extra_axioms:
        allowed |= {a.strip() for a in args.extra_axioms.split(",") if a.strip()}

    ax = parse_listing(listing)
    tiers = {'constructive': 0, 'standard-classical': 0, 'non-standard': 0}
    bad = []
    for name, deps in ax.items():
        if not deps:
            tiers['constructive'] += 1
        elif set(deps) <= allowed:
            tiers['standard-classical'] += 1
        else:
            tiers['non-standard'] += 1
            bad.append((name, deps))
    total = sum(tiers.values())
    print(f"declarations profiled: {total}")
    for k in ('constructive', 'standard-classical', 'non-standard'):
        share = (100.0 * tiers[k] / total) if total else 0.0
        print(f"  {k}: {tiers[k]} ({share:.1f}%)")
    for name, deps in bad[:10]:
        print(f"  NON-STANDARD: {name}: {deps}")
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
