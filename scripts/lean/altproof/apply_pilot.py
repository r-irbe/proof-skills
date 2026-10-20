"""Repeatable pilot pipeline (S4): apply a reviewed extraction to a
Lean project with a build gate.

Pilots 1-2 were handmade. This packages the recipe: a JSON pilot spec
(named edits with asserted anchors) is applied to a target project,
an incremental `lake build <module>` runs as the gate (optional full
build), and on green the change is committed in the target repo's git;
on red every file is restored and the pilot is reported FAILED with
the build log tail. Nothing is applied without every anchor matching,
so a spec written against a stale tree fails BEFORE touching anything.

Spec format:
{
  "project": "/abs/path/to/project",        # or --project
  "module": "EASCI.CuspCatarophe.Example",  # lake module for the gate
  "full_build": false,                       # optional full lake build after
  "edits": [
    {"op": "insert_before", "file": "EASCI/X.lean",
     "anchor": "theorem foo", "content": "abbrev shared ...\n"},
    {"op": "replace", "file": "EASCI/X.lean",
     "old": "  have h : T := by omega", "new": "  have h := shared_T ..."}
  ],
  "message": "pilot: <name>"
}
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Edit:
    op: str
    file: str
    anchor: str = ""
    content: str = ""
    old: str = ""
    new: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Edit:
        return cls(
            op=d["op"],
            file=d["file"],
            anchor=d.get("anchor", ""),
            content=d.get("content", ""),
            old=d.get("old", ""),
            new=d.get("new", ""),
        )


def apply_edit(source: str, edit: Edit) -> str:
    if edit.op == "insert_before":
        if edit.anchor not in source:
            raise ValueError(f"anchor not found for {edit.file}: {edit.anchor[:60]!r}")
        return source.replace(edit.anchor, edit.content + edit.anchor, 1)
    if edit.op == "replace":
        if edit.old not in source:
            raise ValueError(f"replace site not found in {edit.file}: {edit.old[:60]!r}")
        return source.replace(edit.old, edit.new, 1)
    raise ValueError(f"unknown op: {edit.op}")


def run_pilot(spec: dict, timeout_s: int = 3600) -> dict:
    project = Path(spec["project"])
    edits = [Edit.from_dict(e) for e in spec["edits"]]
    # Precondition: every anchor/site must match BEFORE any write.
    touched: dict[Path, str] = {}
    for e in edits:
        p = project / e.file
        src = touched.get(p) or p.read_text(encoding="utf-8")
        touched[p] = apply_edit(src, e)
    originals = {p: p.read_text(encoding="utf-8") for p in touched}
    for p, src in touched.items():
        p.write_text(src, encoding="utf-8")
    # Build gate.
    cmd = ["lake", "build", spec["module"]]
    if spec.get("full_build"):
        cmd = ["lake", "build"]
    proc = subprocess.run(
        cmd, cwd=project, capture_output=True, text=True, timeout=timeout_s
    )
    if proc.returncode != 0:
        for p, src in originals.items():
            p.write_text(src, encoding="utf-8")
        return {
            "status": "FAILED",
            "gate": " ".join(cmd),
            "log_tail": (proc.stdout + proc.stderr)[-2000:],
        }
    commit = None
    if spec.get("commit", True):
        project_res = subprocess.run(
            ["git", "add", "-A"], cwd=project, capture_output=True, text=True
        )
        if project_res.returncode == 0:
            subprocess.run(
                ["git", "commit", "-m", spec.get("message", "pilot")],
                cwd=project,
                capture_output=True,
                text=True,
            )
            rev = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project,
                capture_output=True,
                text=True,
            )
            commit = rev.stdout.strip()
    return {
        "status": "OK",
        "gate": " ".join(cmd),
        "files": [str(p.relative_to(project)) for p in touched],
        "commit": commit,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", help="pilot spec JSON")
    args = ap.parse_args(argv[1:])
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    result = run_pilot(spec)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
