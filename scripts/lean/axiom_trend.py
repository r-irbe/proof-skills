#!/usr/bin/env python3
"""W14-B2 theorem / axiom trend monitor across recent commits.

Default mode avoids worktree churn by streaming historical file contents from
`git show`-equivalent object access (`git ls-tree` + `git cat-file --batch`).
The metric definitions intentionally match `w14b2_axiom_diff.py`:
- theorem total comes from `docs/tracking/axiom_audit.md`
- axiom / sorry / admit / simp counts come from comment-aware source scans of
  `EASCI/**/*.lean`
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from axiom_diff import GIT_ROOT, REPO, REPO_IN_GIT, SUMMARY_PATTERNS, scan_text

EASCI_TREE = (REPO_IN_GIT / "EASCI").as_posix()
AUDIT_REL = "docs/tracking/axiom_audit.md"
AUDIT_PATH_IN_GIT = (REPO_IN_GIT / AUDIT_REL).as_posix()
SPARK_BARS = "▁▂▃▄▅▆▇█"


@dataclass(frozen=True)
class CommitMeta:
    sha: str
    short_sha: str
    date: str
    subject: str


@dataclass(frozen=True)
class MetricRow:
    commit: CommitMeta
    theorems: int
    axioms: int
    sorry: int
    admit: int
    simp_attrs: int


class TrendError(RuntimeError):
    """Raised when the trend capture cannot produce a stable series."""


def run_git(args: list[str], *, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=GIT_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )


def current_branch() -> str:
    proc = run_git(["branch", "--show-current"])
    branch = proc.stdout.strip()
    return branch or "HEAD"


def current_checkout_target() -> str:
    proc = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
        cwd=GIT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode == 0:
        branch = proc.stdout.strip()
        if branch:
            return branch
    return run_git(["rev-parse", "HEAD"]).stdout.strip()


def tracked_worktree_is_clean() -> bool:
    unstaged = subprocess.run(["git", "diff", "--quiet"], cwd=GIT_ROOT)
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=GIT_ROOT)
    return unstaged.returncode == 0 and staged.returncode == 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit theorem/axiom/sorry/admit/simp trends across recent commits."
    )
    parser.add_argument(
        "--commits",
        type=int,
        default=10,
        help="Number of recent commits to inspect (default: %(default)s)",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Branch or ref to inspect (default: current branch)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--checkout",
        dest="no_checkout",
        action="store_false",
        help="Inspect commits by checking them out in-place (requires clean tracked files).",
    )
    mode.add_argument(
        "--no-checkout",
        dest="no_checkout",
        action="store_true",
        help="Inspect commits via git object streaming without changing the worktree.",
    )
    parser.set_defaults(no_checkout=True)
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output path; report is always written to stdout as well.",
    )
    args = parser.parse_args(argv)
    if args.commits <= 0:
        parser.error("--commits must be positive")
    return args


def recent_commits(branch: str, limit: int) -> list[CommitMeta]:
    proc = run_git(
        [
            "log",
            f"--max-count={limit}",
            "--format=%H%x1f%h%x1f%cs%x1f%s",
            branch,
        ]
    )
    commits: list[CommitMeta] = []
    for line in proc.stdout.splitlines():
        sha, short_sha, date, subject = line.split("\x1f", 3)
        commits.append(
            CommitMeta(
                sha=sha,
                short_sha=short_sha,
                date=date,
                subject=" ".join(subject.split()),
            )
        )
    if not commits:
        raise TrendError(f"no commits found for {branch!r}")
    commits.reverse()
    return commits


def parse_audit_summary_text(text: str, source: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, pattern in SUMMARY_PATTERNS.items():
        match = pattern.search(text)
        if not match:
            raise TrendError(f"failed to parse {key} from {source}")
        out[key] = int(match.group(1))
    return out


def read_ref_texts(ref: str) -> dict[str, str]:
    ls_tree = run_git(["ls-tree", "-r", "--full-tree", ref, "--", EASCI_TREE, AUDIT_PATH_IN_GIT])

    blobs_by_oid: dict[str, list[str]] = {}
    ordered_oids: list[str] = []
    for line in ls_tree.stdout.splitlines():
        if not line:
            continue
        head, path = line.split("\t", 1)
        _, object_type, oid = head.split()
        if object_type != "blob":
            continue
        if oid not in blobs_by_oid:
            blobs_by_oid[oid] = []
            ordered_oids.append(oid)
        blobs_by_oid[oid].append(path)

    if AUDIT_PATH_IN_GIT not in {path for paths in blobs_by_oid.values() for path in paths}:
        raise TrendError(f"{AUDIT_REL} not found at {ref}")

    cat = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=GIT_ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert cat.stdin is not None
    assert cat.stdout is not None
    cat.stdin.write(("\n".join(ordered_oids) + "\n").encode("utf-8"))
    cat.stdin.close()

    contents_by_oid: dict[str, str] = {}
    for oid in ordered_oids:
        header = cat.stdout.readline()
        if not header:
            raise TrendError(f"unexpected EOF while reading git objects for {ref}")
        header_text = header.decode("utf-8", errors="replace").rstrip("\n")
        parts = header_text.split()
        if len(parts) == 2 and parts[1] == "missing":
            raise TrendError(f"missing object {oid} while reading {ref}")
        if len(parts) != 3 or parts[1] != "blob":
            raise TrendError(f"unexpected cat-file header for {oid}: {header_text}")
        size = int(parts[2])
        data = cat.stdout.read(size)
        terminator = cat.stdout.read(1)
        if terminator != b"\n":
            raise TrendError(f"malformed cat-file payload terminator for {oid}")
        contents_by_oid[oid] = data.decode("utf-8")

    stderr = cat.stderr.read().decode("utf-8", errors="replace") if cat.stderr else ""
    returncode = cat.wait()
    if returncode != 0:
        raise TrendError(stderr.strip() or f"git cat-file failed for {ref}")

    out: dict[str, str] = {}
    for oid, paths in blobs_by_oid.items():
        for path in paths:
            out[path] = contents_by_oid[oid]
    return out


def capture_ref_metrics(ref: str) -> dict[str, int]:
    texts = read_ref_texts(ref)
    audit_text = texts[AUDIT_PATH_IN_GIT]
    audit = parse_audit_summary_text(audit_text, f"{ref}:{AUDIT_REL}")

    totals = {
        "theorems": int(audit["theorems"]),
        "axioms": 0,
        "sorry": 0,
        "admit": 0,
        "simp_attrs": 0,
    }
    for path, text in texts.items():
        if path == AUDIT_PATH_IN_GIT or not path.endswith(".lean"):
            continue
        metrics = scan_text(text)
        totals["axioms"] += int(metrics["axioms"])
        totals["sorry"] += int(metrics["sorry_tactical"])
        totals["admit"] += int(metrics["admit_tactical"])
        totals["simp_attrs"] += int(metrics["simp"])
    return totals


def capture_worktree_metrics() -> dict[str, int]:
    audit_text = (REPO / AUDIT_REL).read_text(encoding="utf-8")
    audit = parse_audit_summary_text(audit_text, AUDIT_REL)

    totals = {
        "theorems": int(audit["theorems"]),
        "axioms": 0,
        "sorry": 0,
        "admit": 0,
        "simp_attrs": 0,
    }
    for lean_file in sorted((REPO / "EASCI").rglob("*.lean")):
        metrics = scan_text(lean_file.read_text(encoding="utf-8"))
        totals["axioms"] += int(metrics["axioms"])
        totals["sorry"] += int(metrics["sorry_tactical"])
        totals["admit"] += int(metrics["admit_tactical"])
        totals["simp_attrs"] += int(metrics["simp"])
    return totals


def capture_trend_rows(commits: list[CommitMeta], *, no_checkout: bool) -> list[MetricRow]:
    if no_checkout:
        return [MetricRow(commit=commit, **capture_ref_metrics(commit.sha)) for commit in commits]

    if not tracked_worktree_is_clean():
        raise TrendError("checkout mode requires a clean tracked worktree; use --no-checkout")

    original_target = current_checkout_target()
    rows: list[MetricRow] = []
    try:
        for commit in commits:
            run_git(["-c", "advice.detachedHead=false", "checkout", "--quiet", commit.sha])
            rows.append(MetricRow(commit=commit, **capture_worktree_metrics()))
    finally:
        run_git(["checkout", "--quiet", original_target])
    return rows


def truncate_subject(subject: str, limit: int = 60) -> str:
    if len(subject) <= limit:
        return subject
    if limit <= 3:
        return subject[:limit]
    return subject[: limit - 3] + "..."


def markdown_cell(text: str) -> str:
    return text.replace("|", "\\|")


def sparkline(values: list[int]) -> str:
    if not values:
        return ""
    lo = min(values)
    hi = max(values)
    if lo == hi:
        return SPARK_BARS[0] * len(values)
    span = hi - lo
    last_index = len(SPARK_BARS) - 1
    chars: list[str] = []
    for value in values:
        scaled = (value - lo) * last_index / span
        chars.append(SPARK_BARS[round(scaled)])
    return "".join(chars)


def metric_series(rows: list[MetricRow], field: str) -> list[int]:
    return [int(getattr(row, field)) for row in rows]


def render_report(rows: list[MetricRow], branch: str, *, no_checkout: bool) -> str:
    mode_label = "no-checkout" if no_checkout else "checkout"
    lines = [
        f"# W14-B2 axiom trend ({branch}, last {len(rows)} commits, mode={mode_label})",
        "",
        "| short_sha | commit_subject | date | theorems | axioms | sorry | admit | simp_attrs |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.commit.short_sha}` | {markdown_cell(truncate_subject(row.commit.subject))} | {row.commit.date} | {row.theorems} | {row.axioms} | {row.sorry} | {row.admit} | {row.simp_attrs} |"
        )

    lines.extend(["", "## Sparklines", "", "```text"])
    metric_specs = [
        ("theorems", "theorems"),
        ("axioms", "axioms"),
        ("sorry", "sorry"),
        ("admit", "admit"),
        ("simp_attrs", "simp_attrs"),
    ]
    width = max(len(label) for label, _ in metric_specs)
    for label, field in metric_specs:
        values = metric_series(rows, field)
        lines.append(f"{label.rjust(width)}: {min(values)} {sparkline(values)} {max(values)}")
    lines.append("```")
    return "\n".join(lines) + "\n"


def write_output(path_str: str, report: str) -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        branch = args.branch or current_branch()
        commits = recent_commits(branch, args.commits)
        rows = capture_trend_rows(commits, no_checkout=args.no_checkout)
        report = render_report(rows, branch, no_checkout=args.no_checkout)
        sys.stdout.write(report)
        if args.out:
            write_output(args.out, report)
        return 0
    except (subprocess.CalledProcessError, TrendError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
