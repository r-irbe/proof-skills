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
  "module": "MyProject.Domain.Example",     # lake module for the gate
  "full_build": false,                       # optional full lake build after
  "edits": [
    {"op": "insert_before", "file": "MyProject/X.lean",
     "anchor": "theorem foo", "content": "abbrev shared ...\n"},
    {"op": "replace", "file": "MyProject/X.lean",
     "old": "  have h : T := by omega", "new": "  have h := shared_T ..."}
  ],
  "message": "pilot: <name>"
}
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
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


def _replace_text(path: Path, text: str) -> None:
    """Replace one file without exposing a truncated destination; preserve mode."""
    mode = stat.S_IMODE(path.stat().st_mode)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=".altproof-",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run_pilot(spec: dict, timeout_s: int = 3600) -> dict:
    project = Path(spec["project"]).resolve(strict=True)
    edits = [Edit.from_dict(e) for e in spec["edits"]]
    # Precondition: every anchor/site must match BEFORE any write.
    touched: dict[Path, str] = {}
    for e in edits:
        relative = Path(e.file)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"edit path must be project-relative: {e.file}")
        p = (project / relative).resolve(strict=True)
        if not p.is_relative_to(project):
            raise ValueError(f"edit path outside project: {e.file}")
        src = touched[p] if p in touched else p.read_text(encoding="utf-8")
        touched[p] = apply_edit(src, e)
    paths = [str(p.relative_to(project)) for p in touched]
    if not paths:
        raise ValueError("pilot requires at least one edited file")
    if spec.get("commit", True):
        staged = subprocess.run(
            ["git", "--literal-pathspecs", "diff", "--cached", "--name-only", "-z", "--", *paths],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        if staged.returncode != 0:
            raise ValueError(f"cannot inspect staged targets: {staged.stderr}")
        if staged.stdout:
            raise ValueError("pilot target already has staged changes")
    originals = {p: p.read_text(encoding="utf-8") for p in touched}
    written: list[Path] = []
    # Build gate.
    cmd = ["lake", "build", spec["module"]]
    if spec.get("full_build"):
        cmd = ["lake", "build"]

    def rollback(log: str) -> dict:
        conflicts = []
        for path in reversed(written):
            original = originals[path]
            try:
                # Refuse to overwrite a change observed after our own write.
                if path.read_text(encoding="utf-8") != touched[path]:
                    conflicts.append(str(path.relative_to(project)))
                    continue
                _replace_text(path, original)
            except OSError:
                conflicts.append(str(path.relative_to(project)))
        return {
            "status": "FAILED",
            "gate": " ".join(cmd),
            "log_tail": log[-2000:],
            "rollback_conflicts": conflicts,
        }

    try:
        for path, text in touched.items():
            if path.read_text(encoding="utf-8") != originals[path]:
                return rollback(f"concurrent change before write: {path}")
            _replace_text(path, text)
            written.append(path)
        proc = subprocess.run(cmd, cwd=project, capture_output=True, text=True, timeout=timeout_s)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return rollback(str(exc))
    if proc.returncode != 0:
        return rollback(proc.stdout + proc.stderr)
    commit = None
    if spec.get("commit", True):
        # --only keeps unrelated staged changes out of this commit.
        try:
            published = subprocess.run(
                [
                    "git",
                    "--literal-pathspecs",
                    "commit",
                    "--only",
                    "-m",
                    spec.get("message", "pilot"),
                    "--",
                    *paths,
                ],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
            if published.returncode != 0:
                return {
                    "status": "FAILED",
                    "phase": "publication",
                    "commit": None,
                    "files": paths,
                    "log_tail": (published.stdout + published.stderr)[-2000:],
                }
            rev = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
            if rev.returncode != 0 or not rev.stdout.strip():
                return {
                    "status": "FAILED",
                    "phase": "commit-identification",
                    "commit": None,
                    "files": paths,
                    "log_tail": rev.stderr[-2000:],
                }
            commit = rev.stdout.strip()
        except (subprocess.TimeoutExpired, OSError) as exc:
            return {
                "status": "FAILED",
                "phase": "publication-uncertain",
                "commit": None,
                "files": paths,
                "log_tail": str(exc)[-2000:],
            }
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
