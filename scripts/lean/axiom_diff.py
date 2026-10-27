#!/usr/bin/env python3
"""W14-B2 Phase D axiom + declaration snapshot / diff tool.

Captures the Lean corpus baseline from:
- docs/tracking/axiom_audit.md (theorem / module totals)
- EASCI/**/*.lean (decl, simp, axiom, sorry/admit, noncomputable scans)
- EASCI/ReinforcementLearning/**/*.lean (per-module LOC)

Default mode diffs the current capture against the frozen snapshot and exits:
- 0 if clean
- 2 if a regression is detected

Useful invocations:
  python3 scripts/w14b2_axiom_diff.py
  python3 scripts/w14b2_axiom_diff.py --git-ref HEAD --write-snapshot
  python3 scripts/w14b2_axiom_diff.py --git-ref HEAD
  python3 scripts/w14b2_axiom_diff.py --print-current
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import os as _os
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
try:
    from project_config import load_project_config
    _CFG = load_project_config()
    REPO = _CFG.root
    _LEAN_DIR = _CFG.lean_dir
except Exception:
    REPO = Path(_os.environ.get("LEAN_PROJECT_ROOT", Path.cwd())).resolve()
    _LEAN_DIR = _os.environ.get("LEAN_CORPUS_DIR", "EASCI")
_GIT_ROOT_PROC = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    cwd=REPO,
    check=False,
    capture_output=True,
    text=True,
)
GIT_ROOT = Path(_GIT_ROOT_PROC.stdout.strip()) if _GIT_ROOT_PROC.returncode == 0 and _GIT_ROOT_PROC.stdout.strip() else REPO
try:
    REPO_IN_GIT = REPO.relative_to(GIT_ROOT)
except ValueError:
    REPO_IN_GIT = Path(".")
EASCI_ROOT = REPO if _LEAN_DIR in ("", ".") else (REPO / _LEAN_DIR)
AUDIT_PATH = REPO / "docs" / "tracking" / "axiom_audit.md"
DEFAULT_SNAPSHOT = REPO / "docs" / "refactor" / "wave-14" / "b2-prep-phaseD-axiom-snapshot.json"

RL_CORE = "EASCI/ReinforcementLearning/Core.lean"
RL_BELLMAN = "EASCI/ReinforcementLearning/Core/Bellman.lean"
DECL_KINDS = ("theorem", "lemma", "def", "instance", "structure", "inductive")
EXIT_OK = 0
EXIT_REGRESSION = 2

DECL_PAT = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*"
    r"(?:(?:protected|private|noncomputable|unsafe|partial|scoped|local)\s+)*"
    r"(theorem|lemma|def|instance|structure|inductive)\b",
    re.MULTILINE,
)
SIMP_ATTR_PAT = re.compile(r"@\[[^\]]*\bsimp\b[^\]]*\]")
AXIOM_DECL_PAT = re.compile(r"^\s*axiom\s+", re.MULTILINE)
SUMMARY_PATTERNS = {
    "modules": re.compile(r"^- Modules: (\d+)$", re.MULTILINE),
    "theorems": re.compile(r"^- Total (?:theorems|declarations): (\d+)$", re.MULTILINE),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Capture / diff the W14-B2 Phase D axiom + decl snapshot."
    )
    ap.add_argument(
        "--snapshot",
        default=str(DEFAULT_SNAPSHOT),
        help="Snapshot JSON path (default: %(default)s)",
    )
    ap.add_argument(
        "--git-ref",
        default=None,
        help="Read corpus files from a git ref instead of the working tree (e.g. HEAD).",
    )
    ap.add_argument(
        "--write-snapshot",
        action="store_true",
        help="Write the current capture to --snapshot and exit 0.",
    )
    ap.add_argument(
        "--print-current",
        action="store_true",
        help="Print the current capture JSON to stdout.",
    )
    return ap.parse_args(argv)


def relpath(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def repo_rel_to_git(rel: str) -> str:
    return (REPO_IN_GIT / rel).as_posix()


def git_resolve_sha(ref: str) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=GIT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def git_show_text(ref: str, rel: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{repo_rel_to_git(rel)}"],
        cwd=GIT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def lean_relpaths(ref: str | None = None) -> list[str]:
    if ref is None:
        return sorted(relpath(path) for path in EASCI_ROOT.rglob("*.lean"))

    proc = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--", repo_rel_to_git("EASCI")],
        cwd=GIT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    prefix = REPO_IN_GIT.as_posix() + "/"
    rels: list[str] = []
    for line in proc.stdout.splitlines():
        if line.endswith(".lean") and line.startswith(prefix):
            rels.append(line[len(prefix) :])
    return sorted(rels)


def read_text(rel: str, ref: str | None = None) -> str:
    if ref is None:
        return (REPO / rel).read_text(encoding="utf-8")
    return git_show_text(ref, rel)


def utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# Lean comment / string stripping -------------------------------------------------


def strip_lean_comments_and_strings(text: str) -> str:
    """Replace comments / strings with spaces while preserving newlines."""

    out: list[str] = []
    i = 0
    n = len(text)
    block_depth = 0
    in_line_comment = False
    in_string = False

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append("\n")
            else:
                out.append(" ")
            i += 1
            continue

        if block_depth:
            if ch == "/" and nxt == "-":
                block_depth += 1
                out.extend("  ")
                i += 2
                continue
            if ch == "-" and nxt == "/":
                block_depth -= 1
                out.extend("  ")
                i += 2
                continue
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        if in_string:
            if ch == "\\" and i + 1 < n:
                out.append(" ")
                out.append("\n" if text[i + 1] == "\n" else " ")
                i += 2
                continue
            if ch == '"':
                in_string = False
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(" ")
            i += 1
            continue

        if ch == "-" and nxt == "-":
            in_line_comment = True
            out.extend("  ")
            i += 2
            continue

        if ch == "/" and nxt == "-":
            block_depth = 1
            out.extend("  ")
            i += 2
            continue

        out.append(ch)
        i += 1

    return "".join(out)


# Metric helpers ------------------------------------------------------------------


def word_count(text: str, token: str) -> int:
    return len(re.findall(rf"\b{re.escape(token)}\b", text))


def first_token_hits(text: str, token: str, limit: int = 8) -> list[dict[str, object]]:
    pat = re.compile(rf"\b{re.escape(token)}\b")
    hits: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if pat.search(line):
            hits.append({"line": line_no, "text": line.strip()})
            if len(hits) >= limit:
                break
    return hits


def decl_counts(code: str) -> dict[str, int]:
    counts = Counter(match.group(1) for match in DECL_PAT.finditer(code))
    return {kind: int(counts.get(kind, 0)) for kind in DECL_KINDS}


def scan_text(text: str) -> dict[str, object]:
    code = strip_lean_comments_and_strings(text)
    return {
        "decls": decl_counts(code),
        "simp": len(SIMP_ATTR_PAT.findall(code)),
        "noncomputable": word_count(code, "noncomputable"),
        "axioms": len(AXIOM_DECL_PAT.findall(code)),
        "sorry_tactical": word_count(code, "sorry"),
        "admit_tactical": word_count(code, "admit"),
        "raw_sorry": word_count(text, "sorry"),
        "raw_admit": word_count(text, "admit"),
        "raw_sorry_examples": first_token_hits(text, "sorry"),
        "raw_admit_examples": first_token_hits(text, "admit"),
        "loc": len(text.splitlines()),
    }


def parse_audit_summary(ref: str | None = None) -> dict[str, int]:
    text = read_text(relpath(AUDIT_PATH), ref)
    out: dict[str, int] = {}
    for key, pattern in SUMMARY_PATTERNS.items():
        match = pattern.search(text)
        if not match:
            source = ref if ref is not None else str(AUDIT_PATH)
            raise SystemExit(f"failed to parse {key} from {source}")
        out[key] = int(match.group(1))
    return out


def aggregate_decls(
    file_metrics: dict[str, dict[str, object]], *, exclude: set[str] | None = None
) -> dict[str, int]:
    exclude = exclude or set()
    counter: Counter[str] = Counter()
    for rel, metrics in file_metrics.items():
        if rel in exclude:
            continue
        counter.update(metrics["decls"])
    return {kind: int(counter.get(kind, 0)) for kind in DECL_KINDS}


def capture_current(ref: str | None = None) -> dict[str, object]:
    audit = parse_audit_summary(ref)
    module_rels = lean_relpaths(ref)
    file_metrics = {rel: scan_text(read_text(rel, ref)) for rel in module_rels}

    raw_sorry_examples: list[dict[str, object]] = []
    raw_admit_examples: list[dict[str, object]] = []
    for rel, metrics in file_metrics.items():
        for hit in metrics["raw_sorry_examples"]:
            if len(raw_sorry_examples) < 8:
                raw_sorry_examples.append({"path": rel, **hit})
        for hit in metrics["raw_admit_examples"]:
            if len(raw_admit_examples) < 8:
                raw_admit_examples.append({"path": rel, **hit})

    simp_counts = {
        rel: int(metrics["simp"]) for rel, metrics in file_metrics.items() if metrics["simp"]
    }
    noncomputable_counts = {
        rel: int(metrics["noncomputable"])
        for rel, metrics in file_metrics.items()
        if metrics["noncomputable"]
    }
    loc_by_rl_module = {
        rel: int(metrics["loc"])
        for rel, metrics in file_metrics.items()
        if rel.startswith("EASCI/ReinforcementLearning/")
    }

    totals = {
        "theorems": int(audit["theorems"]),
        "modules": int(audit["modules"]),
        "axioms": int(sum(metrics["axioms"] for metrics in file_metrics.values())),
        "sorry_tactical": int(sum(metrics["sorry_tactical"] for metrics in file_metrics.values())),
        "admit_tactical": int(sum(metrics["admit_tactical"] for metrics in file_metrics.values())),
        "simp_total": int(sum(metrics["simp"] for metrics in file_metrics.values())),
        "noncomputable": int(sum(metrics["noncomputable"] for metrics in file_metrics.values())),
    }

    return {
        "captured_at_iso": utc_now_iso(),
        "capture_source": ref if ref is not None else "WORKTREE",
        "wave_3_sha": git_resolve_sha(ref if ref is not None else "HEAD"),
        "audit_path": relpath(AUDIT_PATH),
        "totals": totals,
        "decl_totals": aggregate_decls(file_metrics),
        "rl_core_decls": dict(file_metrics[RL_CORE]["decls"]),
        "rl_bellman_decls": dict(file_metrics[RL_BELLMAN]["decls"]),
        "other_easci_decls": aggregate_decls(file_metrics, exclude={RL_CORE, RL_BELLMAN}),
        "simp_count_rl": int(file_metrics[RL_CORE]["simp"]),
        "simp_count_bellman": int(file_metrics[RL_BELLMAN]["simp"]),
        "simp_counts": simp_counts,
        "noncomputable_counts": noncomputable_counts,
        "loc": {
            "Core.lean": int(file_metrics[RL_CORE]["loc"]),
            "Bellman.lean": int(file_metrics[RL_BELLMAN]["loc"]),
        },
        "loc_by_rl_module": loc_by_rl_module,
        "source_scan": {
            "axiom_declarations": int(totals["axioms"]),
            "raw_sorry": int(sum(metrics["raw_sorry"] for metrics in file_metrics.values())),
            "raw_admit": int(sum(metrics["raw_admit"] for metrics in file_metrics.values())),
            "raw_sorry_examples": raw_sorry_examples,
            "raw_admit_examples": raw_admit_examples,
        },
    }


# Diff / reporting ----------------------------------------------------------------


def fmt_delta(before: int, after: int) -> str:
    if after == before:
        return f"{before} -> {after} (=)"
    sign = "+" if after > before else ""
    return f"{before} -> {after} ({sign}{after - before})"


def diff_snapshot(snapshot: dict[str, object], current: dict[str, object]) -> dict[str, object]:
    regressions: list[str] = []
    notes: list[str] = []
    decl_layout_drift: list[str] = []
    simp_drift: list[str] = []

    def note_if_changed(label: str, before: int, after: int) -> None:
        if before != after:
            notes.append(f"{label}: {fmt_delta(before, after)}")

    for key in ("theorems", "modules"):
        before = int(snapshot["totals"][key])
        after = int(current["totals"][key])
        if after < before:
            regressions.append(f"{key}: {fmt_delta(before, after)}")
        else:
            note_if_changed(key, before, after)

    for key in ("axioms", "sorry_tactical", "admit_tactical"):
        before = int(snapshot["totals"][key])
        after = int(current["totals"][key])
        if after > before:
            regressions.append(f"{key}: {fmt_delta(before, after)}")
        else:
            note_if_changed(key, before, after)

    for kind in DECL_KINDS:
        before = int(snapshot["decl_totals"][kind])
        after = int(current["decl_totals"][kind])
        if after < before:
            regressions.append(f"decl_totals.{kind}: {fmt_delta(before, after)}")
        else:
            note_if_changed(f"decl_totals.{kind}", before, after)

    simp_total_before = int(snapshot["totals"]["simp_total"])
    simp_total_after = int(current["totals"]["simp_total"])
    if simp_total_after != simp_total_before:
        regressions.append(f"totals.simp_total: {fmt_delta(simp_total_before, simp_total_after)}")

    noncomputable_before = int(snapshot["totals"]["noncomputable"])
    noncomputable_after = int(current["totals"]["noncomputable"])
    note_if_changed("noncomputable", noncomputable_before, noncomputable_after)

    for bucket in ("rl_core_decls", "rl_bellman_decls", "other_easci_decls"):
        for kind in DECL_KINDS:
            before = int(snapshot[bucket][kind])
            after = int(current[bucket][kind])
            if before != after:
                decl_layout_drift.append(f"{bucket}.{kind}: {fmt_delta(before, after)}")

    all_simp_modules = sorted(
        set(snapshot.get("simp_counts", {}).keys()) | set(current.get("simp_counts", {}).keys())
    )
    for module in all_simp_modules:
        before = int(snapshot.get("simp_counts", {}).get(module, 0))
        after = int(current.get("simp_counts", {}).get(module, 0))
        if before != after:
            marker = " [RL/Core]" if module == RL_CORE else ""
            simp_drift.append(f"{module}: {fmt_delta(before, after)}{marker}")

    return {
        "regressions": regressions,
        "notes": notes,
        "decl_layout_drift": decl_layout_drift,
        "simp_drift": simp_drift,
    }


def emit_diff(snapshot_path: Path, snapshot: dict[str, object], current: dict[str, object]) -> int:
    result = diff_snapshot(snapshot, current)
    print(f"snapshot: {snapshot_path.relative_to(REPO).as_posix()}")
    print(
        f"snapshot_source: {snapshot.get('capture_source', 'UNKNOWN')} ({snapshot['wave_3_sha']})"
    )
    print(f"current_source:  {current.get('capture_source', 'UNKNOWN')} ({current['wave_3_sha']})")
    print()
    print("totals:")
    for key in (
        "theorems",
        "modules",
        "axioms",
        "sorry_tactical",
        "admit_tactical",
        "simp_total",
        "noncomputable",
    ):
        print(f"  {key}: {fmt_delta(int(snapshot['totals'][key]), int(current['totals'][key]))}")
    print()
    print("decl_totals:")
    for kind in DECL_KINDS:
        print(
            f"  {kind}: "
            f"{fmt_delta(int(snapshot['decl_totals'][kind]), int(current['decl_totals'][kind]))}"
        )

    if result["decl_layout_drift"]:
        print()
        print("decl_layout_drift:")
        for line in result["decl_layout_drift"]:
            print(f"  - {line}")

    if result["simp_drift"]:
        print()
        print("simp_drift:")
        for line in result["simp_drift"]:
            print(f"  - {line}")
    else:
        print()
        print("simp_drift: none")

    if result["notes"]:
        print()
        print("notes:")
        for line in result["notes"]:
            print(f"  - {line}")

    if result["regressions"]:
        print()
        print("REGRESSION DETECTED:")
        for line in result["regressions"]:
            print(f"  - {line}")
        return EXIT_REGRESSION

    print()
    print("clean: no regression detected")
    return EXIT_OK


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    snapshot_path = Path(args.snapshot)
    if not snapshot_path.is_absolute():
        snapshot_path = (REPO / snapshot_path).resolve()

    current = capture_current(args.git_ref)

    if args.print_current:
        print(json.dumps(current, indent=2, sort_keys=True))
        if not args.write_snapshot:
            return EXIT_OK

    if args.write_snapshot:
        write_json(snapshot_path, current)
        print(f"wrote snapshot: {snapshot_path.relative_to(REPO).as_posix()}")
        return EXIT_OK

    if not snapshot_path.exists():
        print(
            f"snapshot does not exist: {snapshot_path.relative_to(REPO).as_posix()}",
            file=sys.stderr,
        )
        return EXIT_REGRESSION

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return emit_diff(snapshot_path, snapshot, current)


if __name__ == "__main__":
    raise SystemExit(main())
