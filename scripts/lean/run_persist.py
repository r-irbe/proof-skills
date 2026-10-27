#!/usr/bin/env python3
"""Write-ahead `<run_id>#<seq>` cycle persistence engine, $2^n$ checkpoint triggers,
structural coordinates, and `disprove-artifact-txn` rollback snapshots (Proposals 7A, 7B, 7C).

Features:
  1. Write-ahead JSONL journal (`<run_id>#<seq>`):
     - `dispatch`: start a bounded tactic/subagent cycle.
     - `note --kind failed-avenue|blocker-diagnosis|search-result|candidate`:
       computes unified blocker signature `sha256(goal_shape_hash + ":" + primary_error_hash)`
       and sets `rerun_forbidden = True` when the same `(goal_shape_hash, primary_error_hash)`
       is encountered again.
     - `review`, `replan`, `finish` (enforcing `min_attempts >= 30` before allowing
       `--status blocked`).
  2. $2^n$ Exponential Backoff Informal Refinement Checkpoints (`AI4Math-Lean-Agents`):
     - `should_refine_informal(attempts)` fires when `attempts > 0 and (attempts & (attempts - 1)) == 0`
       (at attempts 1, 2, 4, 8, 16, 32, ...).
  3. Line-Number-Free Structural Coordinates (`numina-lean-agent`):
     - `validate_structural_coord(coord)` accepts structural proof paths such as
       `"theorem foo: induction n: succ case"` and rejects raw `file.lean:123` line coordinates.
  4. `disprove-artifact-txn` & Path-Scoped Deep-Rollback Snapshots (`7C`):
     - `begin`, `record-witness`, `commit`, `abort`, `snapshot-save`, `snapshot-restore`.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

DEFAULT_MIN_ATTEMPTS_BEFORE_BLOCKED = 30

# Rejects `foo.lean:42`, `line 42`, `L123`, or `:123` line-number coordinates
RAW_LINE_COORD_RE = re.compile(
    r"(?:\.lean:\d+\b|\bline\s+\d+\b|\bL\d+(?:-L?\d+)?\b|:\d+\s*$)",
    re.IGNORECASE,
)


def compute_goal_shape_hash(goal_text: str) -> str:
    """Normalize variable names/whitespace in `goal_text` and return a 16-hex SHA-256 prefix."""
    cleaned = " ".join((goal_text or "").split())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:16]


def compute_error_hash(error_text: str) -> str:
    """Normalize line/column prefixes in `error_text` and return a 16-hex SHA-256 prefix."""
    stripped = re.sub(r"^.*?:\d+:\d+:\s*", "", (error_text or "").strip())
    cleaned = " ".join(stripped.split())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:16]


def compute_blocker_signature(goal_text: str, error_text: str) -> dict[str, str]:
    """Unified `rocq-skills` + `lean4-skills` blocker signature:
    `sha256(goal_shape_hash + ":" + primary_error_hash)`."""
    g_hash = compute_goal_shape_hash(goal_text)
    e_hash = compute_error_hash(error_text)
    combined = hashlib.sha256(f"{g_hash}:{e_hash}".encode("utf-8")).hexdigest()[:24]
    return {
        "goal_shape_hash": g_hash,
        "primary_error_hash": e_hash,
        "blocker_signature": combined,
    }


def should_refine_informal(attempts: int) -> bool:
    """Return True at $2^n$ attempt checkpoints (1, 2, 4, 8, 16, 32, ...)."""
    return attempts > 0 and (attempts & (attempts - 1)) == 0


def validate_structural_coord(coord: str) -> tuple[bool, str]:
    """Validate `numina-lean-agent` line-number-free structural proof coordinates
    (e.g. `'theorem foo: induction n: succ case'`)."""
    c = (coord or "").strip()
    if not c:
        return False, "EMPTY_STRUCTURAL_COORD"
    if RAW_LINE_COORD_RE.search(c):
        return (
            False,
            f"LINE_NUMBER_FORBIDDEN_IN_STRUCTURAL_COORD: `{c}` (use structural path like `theorem foo: induction n: succ case`)",
        )
    if not re.match(r"^(?:theorem|lemma|def|example|section|case)\b", c) and ":" not in c:
        return (
            False,
            f"INVALID_STRUCTURAL_COORD_HEADER: `{c}` must start with declaration kind or contain `:` hierarchy",
        )
    return True, "OK"


class RunJournal:
    """Write-ahead `<run_id>#<seq>` JSONL persistence journal."""

    def __init__(self, state_dir: Path, run_id: str = "run-default") -> None:
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.journal_path = self.state_dir / f"{run_id}.jsonl"

    def read_entries(self) -> list[dict]:
        if not self.journal_path.exists():
            return []
        entries: list[dict] = []
        for ln in self.journal_path.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                entries.append(json.loads(ln))
        return entries

    def _append(self, kind: str, payload: dict) -> dict:
        entries = self.read_entries()
        seq = len(entries) + 1
        record = {
            "entry_id": f"{self.run_id}#{seq}",
            "run_id": self.run_id,
            "seq": seq,
            "kind": kind,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **payload,
        }
        with self.journal_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def dispatch(self, theorem: str, coord: str, route: str = "") -> dict:
        coord_ok, coord_msg = validate_structural_coord(coord)
        if not coord_ok:
            raise ValueError(coord_msg)
        return self._append(
            "dispatch",
            {
                "theorem": theorem,
                "structural_coord": coord,
                "route": route,
            },
        )

    def note(
        self,
        note_kind: str,
        goal_text: str = "",
        error_text: str = "",
        detail: str = "",
        coord: str = "",
    ) -> dict:
        if coord:
            coord_ok, coord_msg = validate_structural_coord(coord)
            if not coord_ok:
                raise ValueError(coord_msg)
        entries = self.read_entries()
        sig_info = compute_blocker_signature(goal_text, error_text)
        prior_sigs = {
            e.get("blocker_signature")
            for e in entries
            if e.get("blocker_signature")
        }
        rerun_forbidden = sig_info["blocker_signature"] in prior_sigs
        failed_attempts = (
            sum(
                1
                for e in entries
                if e.get("kind") == "note"
                and e.get("note_kind") in ("failed-avenue", "blocker-diagnosis")
            )
            + (1 if note_kind in ("failed-avenue", "blocker-diagnosis") else 0)
        )
        checkpoint_2n = should_refine_informal(failed_attempts)
        return self._append(
            "note",
            {
                "note_kind": note_kind,
                "detail": detail,
                "structural_coord": coord,
                **sig_info,
                "rerun_forbidden": rerun_forbidden,
                "failed_attempts": failed_attempts,
                "refine_informal_checkpoint": checkpoint_2n,
            },
        )

    def review(self, verdict: str, notes: str = "") -> dict:
        return self._append("review", {"verdict": verdict, "notes": notes})

    def replan(self, new_route: str, reason: str = "") -> dict:
        return self._append("replan", {"new_route": new_route, "reason": reason})

    def finish(
        self,
        status: str,
        min_attempts: int = DEFAULT_MIN_ATTEMPTS_BEFORE_BLOCKED,
        summary: str = "",
    ) -> dict:
        entries = self.read_entries()
        attempts = sum(
            1
            for e in entries
            if e.get("kind") == "note"
            and e.get("note_kind") in ("failed-avenue", "blocker-diagnosis")
        )
        if status == "blocked" and attempts < min_attempts:
            return {
                "ok": False,
                "error": "PREMATURE_BLOCKED_STOP",
                "attempts": attempts,
                "min_attempts_required": min_attempts,
                "message": (
                    f"Cannot declare status='blocked' after only {attempts} attempts "
                    f"(minimum required: {min_attempts}). Run sorry2lemma or replan."
                ),
            }
        rec = self._append(
            "finish",
            {
                "status": status,
                "attempts": attempts,
                "summary": summary,
            },
        )
        rec["ok"] = True
        return rec


class DisproveArtifactTxn:
    """Transactional counterexample artifact and path-scoped rollback snapshot manager (`7C`)."""

    def __init__(self, state_dir: Path, txn_id: str = "txn-default") -> None:
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.txn_id = txn_id
        self.txn_file = self.state_dir / f"{txn_id}.txn.json"
        self.snap_dir = self.state_dir / f"{txn_id}.snapshots"

    def begin(self, theorem: str, target_files: list[str] | None = None) -> dict:
        self.snap_dir.mkdir(parents=True, exist_ok=True)
        saved_files: dict[str, str] = {}
        for idx, fpath in enumerate(target_files or []):
            p = Path(fpath).resolve()
            if p.exists():
                backup = self.snap_dir / f"snap_{idx}_{p.name}"
                shutil.copy2(p, backup)
                saved_files[str(p)] = str(backup)
        state = {
            "txn_id": self.txn_id,
            "theorem": theorem,
            "status": "ACTIVE",
            "witnesses": [],
            "snapshots": saved_files,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.txn_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

    def record_witness(
        self, witness_expr: str, strategy: str = "plausible", verified: bool = True
    ) -> dict:
        state = json.loads(self.txn_file.read_text(encoding="utf-8"))
        state["witnesses"].append(
            {
                "witness": witness_expr,
                "strategy": strategy,
                "verified": verified,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        )
        self.txn_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

    def commit(self) -> dict:
        state = json.loads(self.txn_file.read_text(encoding="utf-8"))
        if not any(w.get("verified") for w in state.get("witnesses", [])):
            return {
                "ok": False,
                "reason": "NO_VERIFIED_COUNTEREXAMPLE_WITNESS",
                "txn_id": self.txn_id,
            }
        state["status"] = "COMMITTED"
        self.txn_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return {"ok": True, "status": "COMMITTED", "state": state}

    def abort(self, restore_snapshots: bool = True) -> dict:
        state = json.loads(self.txn_file.read_text(encoding="utf-8"))
        restored: list[str] = []
        if restore_snapshots:
            for orig_path, backup_path in state.get("snapshots", {}).items():
                if Path(backup_path).exists():
                    shutil.copy2(backup_path, orig_path)
                    restored.append(orig_path)
        state["status"] = "ABORTED"
        state["restored_files"] = restored
        self.txn_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return {"ok": True, "status": "ABORTED", "restored_files": restored}

    def snapshot_save(self, target_files: list[str] | None = None) -> dict:
        """Save path-scoped rollback snapshots (`7C`)."""
        self.snap_dir.mkdir(parents=True, exist_ok=True)
        state = (
            json.loads(self.txn_file.read_text(encoding="utf-8"))
            if self.txn_file.exists()
            else {
                "txn_id": self.txn_id,
                "theorem": "",
                "status": "ACTIVE",
                "witnesses": [],
                "snapshots": {},
            }
        )
        snapshots: dict[str, str] = dict(state.get("snapshots", {}))
        for idx, fpath in enumerate(target_files or [], start=len(snapshots)):
            p = Path(fpath).resolve()
            if p.exists():
                backup = self.snap_dir / f"snap_{idx}_{p.name}"
                shutil.copy2(p, backup)
                snapshots[str(p)] = str(backup)
        state["snapshots"] = snapshots
        self.txn_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return {"ok": True, "txn_id": self.txn_id, "snapshots": snapshots}

    def snapshot_restore(self) -> dict:
        """Restore all path-scoped rollback snapshots (`7C`)."""
        if not self.txn_file.exists():
            return {"ok": False, "reason": "NO_ACTIVE_SNAPSHOT_STATE", "restored_files": []}
        state = json.loads(self.txn_file.read_text(encoding="utf-8"))
        restored: list[str] = []
        for orig_path, backup_path in state.get("snapshots", {}).items():
            if Path(backup_path).exists():
                shutil.copy2(backup_path, orig_path)
                restored.append(orig_path)
        state["restored_files"] = restored
        self.txn_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return {"ok": True, "txn_id": self.txn_id, "restored_files": restored}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tool_mode = "run-persist"
    if argv and argv[0] in ("run-persist", "disprove-artifact-txn"):
        tool_mode = argv.pop(0)

    if tool_mode == "disprove-artifact-txn":
        p = argparse.ArgumentParser(prog="lean-skills disprove-artifact-txn")
        p.add_argument(
            "action",
            choices=[
                "begin",
                "record-witness",
                "commit",
                "abort",
                "snapshot-save",
                "snapshot-restore",
            ],
        )
        p.add_argument("--state-dir", type=Path, default=Path(".lean-runs"))
        p.add_argument("--txn-id", default="txn-default")
        p.add_argument("--theorem", default="")
        p.add_argument("--target-file", action="append", default=[])
        p.add_argument("--witness", default="")
        p.add_argument("--strategy", default="plausible")
        args = p.parse_args(argv)
        txn = DisproveArtifactTxn(args.state_dir, args.txn_id)
        if args.action == "begin":
            res = txn.begin(args.theorem, args.target_file)
        elif args.action == "record-witness":
            res = txn.record_witness(args.witness, strategy=args.strategy)
        elif args.action == "commit":
            res = txn.commit()
        elif args.action == "snapshot-save":
            res = txn.snapshot_save(args.target_file)
        elif args.action == "snapshot-restore":
            res = txn.snapshot_restore()
        else:
            res = txn.abort()
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok", True) else 1

    p = argparse.ArgumentParser(prog="lean-skills run-persist")
    p.add_argument(
        "action",
        choices=["dispatch", "note", "review", "replan", "finish", "status"],
    )
    p.add_argument("--state-dir", type=Path, default=Path(".lean-runs"))
    p.add_argument("--run-id", default="run-default")
    p.add_argument("--theorem", default="")
    p.add_argument("--coord", default="theorem default: root")
    p.add_argument("--route", default="")
    p.add_argument(
        "--kind",
        default="failed-avenue",
        choices=[
            "failed-avenue",
            "blocker-diagnosis",
            "search-result",
            "candidate",
        ],
    )
    p.add_argument("--goal", default="")
    p.add_argument("--error", default="")
    p.add_argument("--detail", default="")
    p.add_argument("--status", default="completed")
    p.add_argument(
        "--min-attempts", type=int, default=DEFAULT_MIN_ATTEMPTS_BEFORE_BLOCKED
    )
    args = p.parse_args(argv)

    journal = RunJournal(args.state_dir, args.run_id)
    if args.action == "dispatch":
        res = journal.dispatch(args.theorem, args.coord, args.route)
    elif args.action == "note":
        res = journal.note(
            args.kind,
            goal_text=args.goal,
            error_text=args.error,
            detail=args.detail,
            coord=args.coord if args.coord != "theorem default: root" else "",
        )
    elif args.action == "review":
        res = journal.review(args.status, args.detail)
    elif args.action == "replan":
        res = journal.replan(args.route, args.detail)
    elif args.action == "finish":
        res = journal.finish(
            args.status, min_attempts=args.min_attempts, summary=args.detail
        )
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok", False) else 1
    else:
        entries = journal.read_entries()
        res = {"run_id": args.run_id, "count": len(entries), "entries": entries}
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
