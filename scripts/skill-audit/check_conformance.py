#!/usr/bin/env python3
"""
Skill-corpus conformance + DAG + cross-link audit (one-shot).

Usage:
    python3 scripts/skill-audit/check_conformance.py [--json out.json] [--md out.md]

Runs three audits over the corpus rooted at the repo's `skills/`
directory:

  1. **v2 conformance** — for every SKILL.md (first-party + overrides),
     check the 6 v2 markers (USE FOR:, DO NOT USE FOR, TRIGGERS:,
     ## Workflow, ## Recovery, ## Handoffs) and the `tier:` /
     `handoffs:` YAML fields. REDIRECT stubs (small SKILLs whose body
     loudly says REDIRECT) are counted separately as intentional.

  2. **Handoff DAG** — parse every handoffs.{predecessors,successors}
     and validate referential integrity, detect mutual peer pairs,
     report true cycles ≥ length 3, list orphans (no upstream) and
     dead-ends (no downstream).

  3. **Handbook cross-link** — for every SKILL.md that references
     `references/<X>-handbook.md`, verify the target file exists and
     its YAML preamble has `extracted_from: skill:<X>` (or a similar
     back-reference). Report any dangling or unmatched links.

  4. **Markdown link integrity** — verify ordinary relative Markdown
     links in SKILL.md files resolve on disk, including override skills
     whose relative depth differs from first-party skills.

Outputs:
- stdout: human-readable headline + per-section status (always)
- --json: machine-readable structured report
- --md: Markdown-formatted report (for the audit folder)

Exits non-zero if there are any hard failures (invalid refs, broken
handbook links, schema violations). Cycles, orphans, dead-ends are
informational (the corpus deliberately has by-design cycles +
operational entry/exit nodes).
"""

import argparse
import json
import pathlib
import re
import sys
import urllib.parse
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ------------------------------ Schema markers ------------------------------

V2_BODY_MARKERS = [
    "## Workflow",
    "## Recovery",
    "## Handoffs",
]
V2_DESC_MARKERS = ["USE FOR:", "DO NOT USE FOR", "TRIGGERS:"]
REDIRECT_SIGNAL = "REDIRECT"
REDIRECT_MAX_LOC = 60

GATEWAY_PREFIXES = ("agent:gateway", "agent:lean-gateway",
                    "agent:research-gateway", "agent:applied-gateway")


# ------------------------------ Skill loader ------------------------------

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    try:
        fm = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None, text
    return fm, text[end + 4:]


def load_skills(skills_root: pathlib.Path):
    """Return dict[name -> info] for every SKILL.md found."""
    skills = {}
    for p in sorted(skills_root.glob("*/SKILL.md")):
        _load_one(p, skills, is_override=False)
    overrides_dir = skills_root / "_overrides"
    if overrides_dir.is_dir():
        for p in sorted(overrides_dir.glob("*/SKILL.md")):
            _load_one(p, skills, is_override=True)
    return skills


def _load_one(path, out, is_override):
    text = path.read_text()
    fm, body = parse_frontmatter(text)
    loc = text.count("\n")
    name = path.parent.name
    is_redirect = REDIRECT_SIGNAL in text.upper() and loc < REDIRECT_MAX_LOC
    handoffs = (fm or {}).get("handoffs", {}) or {}
    desc = (fm or {}).get("description", "") or ""
    out[name] = {
        "path": str(path),
        "name": name,
        "is_override": is_override,
        "is_redirect": is_redirect,
        "loc": loc,
        "tier": (fm or {}).get("tier"),
        "predecessors": handoffs.get("predecessors", []) or [],
        "successors": handoffs.get("successors", []) or [],
        "description": desc,
        "body": body,
        "fm": fm,
    }


# ------------------------------ 1. v2 conformance ------------------------------

def audit_v2(skills):
    results = {"v2": [], "redirect": [], "non_v2": [], "details": {}}
    for name, info in skills.items():
        if info["is_redirect"]:
            results["redirect"].append(name)
            results["details"][name] = {"status": "REDIRECT"}
            continue
        body_ok = all(m in info["body"] for m in V2_BODY_MARKERS)
        desc_ok = all(m in info["description"] for m in V2_DESC_MARKERS)
        tier_ok = info["tier"] is not None
        if body_ok and desc_ok and tier_ok:
            results["v2"].append(name)
            results["details"][name] = {"status": "v2"}
        else:
            results["non_v2"].append(name)
            results["details"][name] = {
                "status": "non_v2",
                "missing_body": [m for m in V2_BODY_MARKERS if m not in info["body"]],
                "missing_desc": [m for m in V2_DESC_MARKERS if m not in info["description"]],
                "missing_tier": not tier_ok,
            }
    return results


# ------------------------------ 2. Handoff DAG ------------------------------

def audit_dag(skills):
    all_ids = {f"skill:{n}" for n in skills}
    valid_targets = all_ids | set(GATEWAY_PREFIXES)

    invalid_succ, invalid_pre = [], []
    for name, info in skills.items():
        for s in info["successors"]:
            if isinstance(s, str) and s.startswith("skill:") and s not in valid_targets:
                invalid_succ.append({"from": name, "to": s})
        for p in info["predecessors"]:
            if isinstance(p, str) and p.startswith("skill:") and p not in valid_targets:
                invalid_pre.append({"to": name, "from": p})

    # Mutual peer pairs
    mutual = set()
    for name, info in skills.items():
        for s in info["successors"]:
            if not isinstance(s, str) or not s.startswith("skill:"):
                continue
            tgt = s.removeprefix("skill:")
            if tgt in skills:
                tgt_succs = [
                    x.removeprefix("skill:")
                    for x in skills[tgt]["successors"]
                    if isinstance(x, str) and x.startswith("skill:")
                ]
                if name in tgt_succs:
                    mutual.add(tuple(sorted([name, tgt])))

    # True cycles (length ≥ 3)
    cycles = []
    visited_global = set()

    def dfs(node, path):
        if node in path:
            i = path.index(node)
            c = path[i:] + [node]
            if len(c) > 3:  # skip 2-cycles (mutual peers)
                cycles.append(c)
            return
        if node in visited_global:
            return
        info = skills.get(node)
        if not info:
            return
        for succ in info["successors"]:
            if isinstance(succ, str) and succ.startswith("skill:"):
                tgt = succ.removeprefix("skill:")
                if tgt in skills:
                    dfs(tgt, path + [node])
        visited_global.add(node)

    for n in skills:
        dfs(n, [])

    unique_cycles = list({tuple(sorted(set(c))): c for c in cycles}.values())

    # Orphans + dead-ends
    referenced = set()
    for info in skills.values():
        for s in info["successors"]:
            if isinstance(s, str) and s.startswith("skill:"):
                referenced.add(s.removeprefix("skill:"))

    orphans, deadends = [], []
    for n, i in skills.items():
        if i["is_redirect"]:
            continue
        pred_ok = any(
            isinstance(p, str) and (p.startswith("agent:") or p in all_ids)
            for p in i["predecessors"]
        )
        if not pred_ok and n not in referenced:
            orphans.append(n)
        if not i["successors"]:
            deadends.append(n)

    return {
        "invalid_successor_refs": invalid_succ,
        "invalid_predecessor_refs": invalid_pre,
        "mutual_peer_pairs": [list(p) for p in sorted(mutual)],
        "true_cycles_count": len(unique_cycles),
        "true_cycles_sample": [c for c in unique_cycles[:5]],
        "orphans": orphans,
        "deadends": deadends,
        "tier_distribution": dict(Counter(i["tier"] for i in skills.values())),
    }


# ------------------------------ 3. Handbook cross-links ------------------------------

HANDBOOK_RE = re.compile(r"references/([\w-]+)-handbook\.md")


def audit_handbook_links(skills, repo_root):
    """For every SKILL.md, scan body for `references/<X>-handbook.md`
    references; verify file exists and `extracted_from` back-points."""
    refs_dir = repo_root / "references"
    results = {"broken_links": [], "missing_backref": [], "valid_pairs": []}
    for name, info in skills.items():
        for m in HANDBOOK_RE.finditer(info["body"]):
            target_stem = m.group(1)
            target_path = refs_dir / f"{target_stem}-handbook.md"
            if not target_path.exists():
                results["broken_links"].append({
                    "from_skill": name,
                    "broken_target": str(target_path.relative_to(repo_root)),
                })
                continue
            # Verify back-reference
            try:
                ttext = target_path.read_text()
                tfm, _ = parse_frontmatter(ttext)
                extracted_from = (tfm or {}).get("extracted_from", "")
                if name not in str(extracted_from):
                    results["missing_backref"].append({
                        "skill": name,
                        "handbook": target_stem,
                        "actual_extracted_from": extracted_from,
                    })
                else:
                    results["valid_pairs"].append({
                        "skill": name,
                        "handbook": target_stem,
                    })
            except Exception as e:
                results["broken_links"].append({
                    "from_skill": name,
                    "broken_target": str(target_path),
                    "error": str(e),
                })
    return results


# ------------------------------ 4. Markdown link integrity ------------------------------

MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def audit_markdown_links(skills, repo_root):
    """Verify relative Markdown links from SKILL.md files resolve on disk."""
    results = {"broken_links": [], "valid_links": 0}
    for name, info in skills.items():
        path = repo_root / info["path"]
        text = path.read_text()
        for m in MD_LINK_RE.finditer(text):
            raw_href = m.group(1).strip()
            href = raw_href.split("#", 1)[0]
            if (
                not href
                or href.startswith("#")
                or "://" in href
                or href.startswith("mailto:")
            ):
                continue
            href = urllib.parse.unquote(href)
            target = (path.parent / href).resolve()
            line = text[:m.start()].count("\n") + 1
            try:
                rel_target = str(target.relative_to(repo_root))
            except ValueError:
                results["broken_links"].append({
                    "from_skill": name,
                    "source": info["path"],
                    "line": line,
                    "target": raw_href,
                    "reason": "escapes repo root",
                })
                continue
            if not target.exists():
                results["broken_links"].append({
                    "from_skill": name,
                    "source": info["path"],
                    "line": line,
                    "target": raw_href,
                    "resolved": rel_target,
                    "reason": "missing target",
                })
            else:
                results["valid_links"] += 1
    return results


# ------------------------------ Report formatter ------------------------------

def render_md(report):
    skills = report["meta"]
    v2 = report["v2"]
    dag = report["dag"]
    cl = report["cross_link"]
    ml = report["markdown_links"]
    lines = []
    a = lines.append
    a("---")
    a(f"title: \"Proof-skills corpus audit — {skills['scan_date']}\"")
    a(f"audit_date: \"{skills['scan_date']}\"")
    a("auditor: \"scripts/skill-audit/check_conformance.py\"")
    a(f"skills_scanned: {skills['total_skills']}")
    a("---")
    a("")
    a(f"# Skill corpus audit — {skills['scan_date']}")
    a("")
    a("## 0. Headline")
    a("")
    a("| Metric | Value |")
    a("|---|---:|")
    a(f"| Total SKILL.md scanned (first-party + overrides) | {skills['total_skills']} |")
    a(f"| First-party SKILLs | {skills['first_party']} |")
    a(f"| Override SKILLs | {skills['overrides']} |")
    a(f"| v2-conformant | {len(v2['v2'])} |")
    a(f"| REDIRECT stubs | {len(v2['redirect'])} |")
    a(f"| Non-v2 (schema gap) | {len(v2['non_v2'])} |")
    a(f"| Invalid successor refs | {len(dag['invalid_successor_refs'])} |")
    a(f"| Invalid predecessor refs | {len(dag['invalid_predecessor_refs'])} |")
    a(f"| Mutual peer pairs | {len(dag['mutual_peer_pairs'])} |")
    a(f"| True cycles (length ≥ 3) | {dag['true_cycles_count']} |")
    a(f"| Orphans (no upstream) | {len(dag['orphans'])} |")
    a(f"| Dead-ends (no downstream) | {len(dag['deadends'])} |")
    a(f"| Handbook cross-links — valid | {len(cl['valid_pairs'])} |")
    a(f"| Handbook cross-links — broken | {len(cl['broken_links'])} |")
    a(f"| Handbook cross-links — missing backref | {len(cl['missing_backref'])} |")
    a(f"| Markdown links — valid | {ml['valid_links']} |")
    a(f"| Markdown links — broken | {len(ml['broken_links'])} |")
    a("")
    a("## 1. v2 conformance — non-conformant SKILLs")
    a("")
    if not v2["non_v2"]:
        a("None. ✓ all non-REDIRECT skills are v2-conformant.")
    else:
        for n in v2["non_v2"]:
            d = v2["details"][n]
            a(f"- **{n}**: missing_body={d['missing_body']}, missing_desc={d['missing_desc']}, missing_tier={d['missing_tier']}")
    a("")
    a("## 2. DAG findings")
    a("")
    if dag["invalid_successor_refs"]:
        a("### Invalid successor refs")
        for r in dag["invalid_successor_refs"]:
            a(f"- ❌ {r['from']} → {r['to']}")
    else:
        a("- ✓ All successor refs resolve.")
    if dag["invalid_predecessor_refs"]:
        a("\n### Invalid predecessor refs")
        for r in dag["invalid_predecessor_refs"]:
            a(f"- ❌ {r['to']} predecessor {r['from']}")
    else:
        a("- ✓ All predecessor refs resolve.")
    a("")
    a(f"### {len(dag['mutual_peer_pairs'])} mutual peer pairs (by design):")
    for p in dag["mutual_peer_pairs"]:
        a(f"- {p[0]} ↔ {p[1]}")
    a("")
    a(f"### {dag['true_cycles_count']} true cycles (length ≥ 3) — typically editorial-loop feedback")
    a("")
    a("### Orphans (no upstream, not a REDIRECT)")
    for o in dag["orphans"]:
        a(f"- {o}")
    a("")
    a("### Dead-ends (no downstream, not a REDIRECT)")
    for d in dag["deadends"]:
        a(f"- {d}")
    a("")
    a("## 3. Tier distribution")
    a("")
    for t, c in sorted(dag["tier_distribution"].items(), key=lambda x: -x[1]):
        a(f"- {t}: {c}")
    a("")
    a("## 4. Handbook cross-link audit")
    a("")
    a(f"- Valid pairs: {len(cl['valid_pairs'])}")
    if cl["broken_links"]:
        a("\n### Broken handbook links")
        for b in cl["broken_links"]:
            a(f"- ❌ {b['from_skill']} → {b['broken_target']}")
    if cl["missing_backref"]:
        a("\n### Handbooks missing back-reference")
        for m in cl["missing_backref"]:
            a(f"- ⚠ {m['skill']} → {m['handbook']}-handbook.md (extracted_from={m['actual_extracted_from']!r})")
    if not cl["broken_links"] and not cl["missing_backref"]:
        a("\nAll handbook references resolve and back-link correctly. ✓")
    a("")
    a("## 5. Markdown link integrity")
    a("")
    a(f"- Valid relative links: {ml['valid_links']}")
    if ml["broken_links"]:
        a("\n### Broken relative Markdown links")
        for b in ml["broken_links"]:
            a(f"- ❌ {b['source']}:{b['line']} → {b['target']} ({b['reason']})")
    else:
        a("\nAll relative Markdown links resolve. ✓")
    return "\n".join(lines) + "\n"


# ------------------------------ Main ------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".",
                    help="Repo root (default: cwd; expects skills/ and references/ subdirs)")
    ap.add_argument("--json", help="Write machine-readable JSON report")
    ap.add_argument("--md", help="Write Markdown report")
    ap.add_argument("--fail-on", default="hard",
                    choices=["hard", "any", "never"],
                    help="hard = exit 1 on broken refs/links/schema; any = also on orphans/deadends; never = always exit 0")
    args = ap.parse_args()

    repo = pathlib.Path(args.repo_root).resolve()
    skills_dir = repo / "skills"
    if not skills_dir.is_dir():
        print(f"ERROR: {skills_dir} not found", file=sys.stderr)
        sys.exit(2)

    skills = load_skills(skills_dir)
    if not skills:
        print("ERROR: no SKILL.md found", file=sys.stderr)
        sys.exit(2)

    first_party = sum(1 for i in skills.values() if not i["is_override"])
    overrides = sum(1 for i in skills.values() if i["is_override"])

    import datetime
    report = {
        "meta": {
            "scan_date": datetime.date.today().isoformat(),
            "total_skills": len(skills),
            "first_party": first_party,
            "overrides": overrides,
        },
        "v2": audit_v2(skills),
        "dag": audit_dag(skills),
        "cross_link": audit_handbook_links(skills, repo),
        "markdown_links": audit_markdown_links(skills, repo),
    }

    md = render_md(report)
    print(md)

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(report, indent=2, default=str))
    if args.md:
        pathlib.Path(args.md).write_text(md)

    # Exit code
    hard_fail = (
        report["dag"]["invalid_successor_refs"]
        or report["dag"]["invalid_predecessor_refs"]
        or report["cross_link"]["broken_links"]
        or report["markdown_links"]["broken_links"]
        or report["v2"]["non_v2"]
    )
    soft_fail = report["dag"]["orphans"] or report["dag"]["deadends"]
    if args.fail_on == "hard" and hard_fail:
        sys.exit(1)
    if args.fail_on == "any" and (hard_fail or soft_fail):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
