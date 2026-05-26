#!/usr/bin/env python3
"""
check_skill.py — Prototype linter for SKILL.md files.

Validates a SKILL.md against the filab skill-template contract:
  specs/templates/skill-template.md (FSIA W5-02)
plus forward references to ADR-0076 (FM schema) and ADR-0080 (handoff DAG).

Status: PROTOTYPE. Shape-only checks (not semantic adequacy).
Python 3 stdlib + PyYAML. ~300 LOC.

Usage:
    check_skill.py PATH [PATH ...]      # files or directories
    check_skill.py --report PATH        # markdown compliance table
    check_skill.py --json PATH          # machine-readable

Exit code: 0 if every file passes, 1 if any file fails.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML required (pip install pyyaml)\n")
    sys.exit(2)


# ---------- contract constants ----------

REQUIRED_FM_KEYS = ("name", "description", "tier")
VALID_TIERS = ("hot", "warm", "cold")
DESC_MARKERS = ("USE FOR:", "DO NOT USE FOR:")
REQUIRED_SECTIONS = (
    "## Routing",
    "## Behavioural rules",
    "## Workflow",
    "## Recovery & STOP",
    "## Handoffs",
)
WORKFLOW_TAGS = {"discover", "execute", "validate", "persist"}
HANDOFF_KINDS = {"agent", "skill", "spec", "adr", "task"}

G_RULE_RE = re.compile(r"^\s*[-*]?\s*\*?\*?G-(\d+)\*?\*?\s*[:\(]", re.MULTILINE)
G_RULE_LINE_RE = re.compile(r"G-\d+.*?(MUST NOT|MUST|SHOULD NOT|SHOULD)", re.DOTALL)
NUMBERED_STEP_RE = re.compile(r"^\s*(\d+)\.\s+", re.MULTILINE)
WORKFLOW_TAG_RE = re.compile(r"\[(discover|execute|validate|persist)\]")
HANDOFF_ID_RE = re.compile(r"^([a-z]+):([a-z0-9][a-z0-9-]*)$")
SECTION_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
MANDATORY_BLOCK_RE = re.compile(r"MANDATORY", re.IGNORECASE)


# ---------- result types ----------

@dataclass
class Finding:
    level: str          # "fail" | "warn" | "pass"
    check: str
    detail: str = ""

    def fmt(self) -> str:
        sym = {"fail": "✗", "warn": "!", "pass": "✓"}[self.level]
        msg = f"  {sym} [{self.level.upper():4s}] {self.check}"
        if self.detail:
            msg += f" — {self.detail}"
        return msg


@dataclass
class SkillReport:
    path: str
    findings: list[Finding] = field(default_factory=list)
    tier: str | None = None
    skipped: bool = False

    def add(self, level: str, check: str, detail: str = "") -> None:
        self.findings.append(Finding(level, check, detail))

    @property
    def fails(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "fail"]

    @property
    def warns(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "warn"]

    @property
    def passed(self) -> bool:
        return not self.fails and not self.skipped

    def to_dict(self) -> dict:
        d = asdict(self)
        d["passed"] = self.passed
        return d


# ---------- parsing ----------

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (fm_dict, body, error_msg). fm_dict is None on failure."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text, "no YAML frontmatter (expected `---` block at file head)"
    raw_fm, body = m.group(1), m.group(2)
    try:
        data = yaml.safe_load(raw_fm) or {}
    except yaml.YAMLError as exc:
        return None, body, f"YAML parse error: {exc}"
    if not isinstance(data, dict):
        return None, body, "frontmatter is not a mapping"
    return data, body, None


# ---------- individual checks ----------

def check_frontmatter(fm: dict, rep: SkillReport) -> None:
    for key in REQUIRED_FM_KEYS:
        if key not in fm or fm[key] in (None, "", []):
            rep.add("fail", f"frontmatter.{key}", "missing or empty")
        else:
            rep.add("pass", f"frontmatter.{key}")

    tier = fm.get("tier")
    rep.tier = tier if isinstance(tier, str) else None
    if tier and tier not in VALID_TIERS:
        rep.add("fail", "frontmatter.tier valid",
                f"got {tier!r}, expected one of {VALID_TIERS}")
    elif tier in VALID_TIERS:
        rep.add("pass", "frontmatter.tier valid")


def check_description_markers(fm: dict, rep: SkillReport) -> None:
    desc = fm.get("description") or ""
    if not isinstance(desc, str):
        rep.add("fail", "description markers", "description is not a string")
        return
    for marker in DESC_MARKERS:
        if marker in desc:
            rep.add("pass", f"description has `{marker}`")
        else:
            rep.add("fail", f"description has `{marker}`",
                    "literal uppercase marker required (FSIA-R-06-01)")
    if "TRIGGERS:" in desc:
        rep.add("pass", "description has `TRIGGERS:`")
    else:
        rep.add("warn", "description has `TRIGGERS:`",
                "recommended (FSIA-R-06-01)")


def check_sections(body: str, rep: SkillReport) -> None:
    headers = [h.strip().lower() for _, h in SECTION_HEADER_RE.findall(body)]
    body_low = body.lower()
    for sec in REQUIRED_SECTIONS:
        needle = sec.lower().lstrip("# ").strip()
        # match either as a header or anywhere prefixed with ##
        if any(needle in h for h in headers) or sec.lower() in body_low:
            rep.add("pass", f"section `{sec}`")
        else:
            rep.add("fail", f"section `{sec}`", "header not found")


def check_g_rules(body: str, rep: SkillReport) -> None:
    matches = G_RULE_RE.findall(body)
    if not matches:
        rep.add("fail", "G-rules present", "no `G-N:` lines found")
        return
    nums = sorted({int(m) for m in matches})
    rep.add("pass", "G-rules present", f"{len(nums)} unique (G-{nums[0]}..G-{nums[-1]})")

    # check at least one modal keyword usage
    if not G_RULE_LINE_RE.search(body):
        rep.add("fail", "G-rules carry MUST/SHOULD/MUST NOT",
                "no modal keyword adjacent to G-* anchor")
    else:
        rep.add("pass", "G-rules carry MUST/SHOULD/MUST NOT")


def check_workflow(body: str, rep: SkillReport) -> None:
    # find the Workflow section's slice
    sections = list(SECTION_HEADER_RE.finditer(body))
    workflow_slice = ""
    for i, m in enumerate(sections):
        if m.group(2).strip().lower().startswith("workflow"):
            start = m.end()
            end = sections[i + 1].start() if i + 1 < len(sections) else len(body)
            workflow_slice = body[start:end]
            break
    if not workflow_slice:
        # already reported by section check; skip
        return

    steps = NUMBERED_STEP_RE.findall(workflow_slice)
    if len(steps) >= 2:
        rep.add("pass", "workflow numbered steps", f"{len(steps)} steps")
    else:
        rep.add("fail", "workflow numbered steps",
                f"found {len(steps)} numbered steps, expected ≥2")

    tags = set(WORKFLOW_TAG_RE.findall(workflow_slice))
    missing = WORKFLOW_TAGS - tags
    if not missing:
        rep.add("pass", "workflow phase tags",
                f"all four tags present ({sorted(WORKFLOW_TAGS)})")
    elif tags:
        rep.add("warn", "workflow phase tags",
                f"missing tags: {sorted(missing)}")
    else:
        rep.add("warn", "workflow phase tags",
                "no [discover|execute|validate|persist] tags found")


def check_mandatory_block(body: str, rep: SkillReport, tier: str | None) -> None:
    has_block = bool(MANDATORY_BLOCK_RE.search(body))
    if tier == "hot":
        if has_block:
            rep.add("pass", "hot-tier MANDATORY block")
        else:
            rep.add("warn", "hot-tier MANDATORY block",
                    "hot-tier skill missing MANDATORY notice (FSIA-R-04-39)")
    else:
        if has_block:
            rep.add("pass", "MANDATORY notice (informational)")
        # not required for warm/cold


def check_handoffs_schema(fm: dict, rep: SkillReport) -> None:
    h = fm.get("handoffs")
    if not isinstance(h, dict):
        return  # optional; absence is fine for now
    for side in ("predecessors", "successors"):
        vals = h.get(side, [])
        if vals in (None, []):
            continue
        if not isinstance(vals, list):
            rep.add("fail", f"handoffs.{side} is list",
                    f"got {type(vals).__name__}")
            continue
        bad = []
        for v in vals:
            if not isinstance(v, str) or not HANDOFF_ID_RE.match(v):
                bad.append(repr(v))
                continue
            kind = v.split(":", 1)[0]
            if kind not in HANDOFF_KINDS:
                bad.append(f"{v} (unknown kind {kind!r})")
        if bad:
            rep.add("fail", f"handoffs.{side} <kind>:<slug> grammar",
                    f"invalid: {', '.join(bad)} (ADR-0080)")
        else:
            rep.add("pass", f"handoffs.{side} <kind>:<slug> grammar",
                    f"{len(vals)} entries")


# ---------- top-level lint ----------

def lint_file(path: Path) -> SkillReport:
    rep = SkillReport(path=str(path))
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        rep.add("fail", "readable", str(exc))
        rep.skipped = True
        return rep

    fm, body, err = split_frontmatter(text)
    if fm is None:
        rep.add("fail", "frontmatter present", err or "unknown error")
        return rep
    rep.add("pass", "frontmatter present")

    check_frontmatter(fm, rep)
    check_description_markers(fm, rep)
    check_sections(body, rep)
    check_g_rules(body, rep)
    check_workflow(body, rep)
    check_mandatory_block(body, rep, rep.tier)
    check_handoffs_schema(fm, rep)
    return rep


def discover_files(paths: Iterable[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            out.extend(sorted(path.rglob("SKILL.md")))
        elif path.is_file():
            out.append(path)
    # de-dup, preserve order
    seen, uniq = set(), []
    for p in out:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


# ---------- output ----------

def category_results(rep: SkillReport) -> dict[str, str]:
    """Roll findings up to the six columns used in the compliance table."""
    def status_of(prefixes: tuple[str, ...]) -> str:
        sub = [f for f in rep.findings
               if any(f.check.startswith(p) for p in prefixes)]
        if not sub:
            return "—"
        if any(f.level == "fail" for f in sub):
            return "✗"
        if any(f.level == "warn" for f in sub):
            return "!"
        return "✓"

    return {
        "tier_present":      status_of(("frontmatter.tier",)),
        "desc_markers":      status_of(("description has",)),
        "required_sections": status_of(("section `",)),
        "g_rules":           status_of(("G-rules",)),
        "workflow_tagged":   status_of(("workflow phase tags",
                                        "workflow numbered steps")),
    }


def print_human(reports: list[SkillReport], verbose: bool) -> None:
    for rep in reports:
        status = "PASS" if rep.passed else "FAIL"
        warn_n = len(rep.warns)
        fail_n = len(rep.fails)
        print(f"{status}  {rep.path}  ({fail_n} fail, {warn_n} warn)")
        if verbose or fail_n:
            for f in rep.findings:
                if verbose or f.level != "pass":
                    print(f.fmt())
    print()
    print(f"summary: {sum(r.passed for r in reports)}/{len(reports)} files passed")


def render_markdown_table(reports: list[SkillReport]) -> str:
    rows = ["| skill | tier | desc_markers | sections | g_rules | workflow | overall |",
            "|---|---|---|---|---|---|---|"]
    for rep in reports:
        cats = category_results(rep)
        name = Path(rep.path).parent.name or Path(rep.path).name
        overall = "✓" if rep.passed else "✗"
        rows.append(f"| {name} | {cats['tier_present']} | "
                    f"{cats['desc_markers']} | {cats['required_sections']} | "
                    f"{cats['g_rules']} | {cats['workflow_tagged']} | {overall} |")
    return "\n".join(rows)


# ---------- CLI ----------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("paths", nargs="+", help="SKILL.md files or directories")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every check, including passes")
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    ap.add_argument("--report", action="store_true",
                    help="emit markdown compliance table only")
    args = ap.parse_args(argv)

    files = discover_files(args.paths)
    if not files:
        print("no SKILL.md files found", file=sys.stderr)
        return 2

    reports = [lint_file(f) for f in files]

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    elif args.report:
        print(render_markdown_table(reports))
    else:
        print_human(reports, args.verbose)

    return 0 if all(r.passed for r in reports) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
