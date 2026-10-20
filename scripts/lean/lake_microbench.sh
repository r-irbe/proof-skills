#!/usr/bin/env bash
# Generic Lake microbenchmark suite for Lean 4 corpora.
#
# Usage:
#   bash scripts/w14b2_lake_microbench.sh
#   bash scripts/w14b2_lake_microbench.sh --quick
#   bash scripts/w14b2_lake_microbench.sh \
#     --output docs/refactor/findings/lake-microbench-pre-phaseD.json
#
# Full mode:
#   * Deletes only `.lake/build/{lib/lean,ir}/EASCI*` artifacts, preserving Mathlib cache.
#   * Times `lake build EASCI` as the cold full-corpus baseline.
#   * Then re-times each benchmark module by deleting only that module's own EASCI
#     artifacts before an incremental `lake build ...` rebuild.
#
# Quick mode (`--quick`):
#   * Skips the global cold delete and the cold `lake build EASCI` pass.
#   * Still deletes each benchmark module's own artifacts before timing it, so local
#     iteration stays incremental (~2-3 min instead of the 15-25 min cold pass).
#
# Output:
#   * JSON summary at `docs/refactor/findings/lake-microbench-<timestamp>.json`
#     unless `--output PATH` is supplied.
#   * Per-run stdout/stderr logs in a sibling `*.logs/` directory.
#
# Manual pre-Phase-D baseline capture:
#   bash scripts/w14b2_lake_microbench.sh \
#     --output docs/refactor/findings/lake-microbench-pre-phaseD.json

set -euo pipefail

repo_root="${LAKE_MICROBENCH_REPO_ROOT:-$(pwd)}"
cd "$repo_root"

python3 - "$repo_root" "$@" <<'PY'
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REQUESTED_MODULES = (
    "EASCI.AgenticSafety",
    "EASCI.CCVGating",
    "EASCI.CuspCatastrophe",
    "EASCI.LyapunovStability",
    "EASCI.PhasePortrait",
    "EASCI.PipelineAdaptive",
    "EASCI.Probability",
    "EASCI.ProvenanceChain",
    "EASCI.QualityGates",
    "EASCI.ReinforcementLearning",
    "EASCI.StochasticCCV",
)

NON_SYNTHETIC_MODULES = tuple(
    module for module in REQUESTED_MODULES if module != "EASCI.Probability"
)


@dataclass(frozen=True)
class ModuleSpec:
    label: str
    targets: tuple[str, ...]
    artifact_prefix: str
    synthetic: bool = False
    note: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture W14-B2 lake build microbenchmarks for the EASCI corpus.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip the cold full-corpus rebuild and time only per-module incremental rebuilds.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the JSON snapshot to this path (default: docs/refactor/findings/lake-microbench-<timestamp>.json).",
    )
    return parser.parse_args(list(argv))


def run_text(cmd: Sequence[str], cwd: Path) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def module_from_relative_path(path: Path) -> str:
    without_suffix = path.with_suffix("")
    return ".".join(without_suffix.parts)


def load_easci_imports(repo_root: Path) -> list[str]:
    easci_path = repo_root / "EASCI.lean"
    imports: list[str] = []
    for raw_line in easci_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("import "):
            continue
        imported = line.split(None, 1)[1].strip()
        if imported.startswith("EASCI."):
            imports.append(imported)
    return imports


def discover_group_targets(repo_root: Path, label: str, include_root: bool) -> tuple[str, ...]:
    suffix = label.removeprefix("EASCI.")
    root_file = repo_root / "EASCI" / f"{suffix}.lean"
    group_dir = repo_root / "EASCI" / suffix

    targets = [
        module_from_relative_path(path.relative_to(repo_root))
        for path in sorted(group_dir.rglob("*.lean"))
    ] if group_dir.exists() else []
    if include_root and root_file.exists():
        targets.append(label)
    return tuple(targets)


def group_targets(repo_root: Path, label: str) -> tuple[tuple[str, ...], bool, str | None]:
    suffix = label.removeprefix("EASCI.")
    root_file = repo_root / "EASCI" / f"{suffix}.lean"
    group_dir = repo_root / "EASCI" / suffix

    if label == "EASCI.Probability":
        targets = discover_group_targets(repo_root, label, include_root=True)
        if not targets:
            raise SystemExit(
                f"Cannot benchmark {label}: neither {root_file.relative_to(repo_root)} nor any "
                f"{group_dir.relative_to(repo_root)}/**/*.lean files exist."
            )
        note = (
            f"Synthetic umbrella: {root_file.relative_to(repo_root)} does not exist yet, "
            f"so this benchmark times the {label} leaf modules in one lake invocation."
        )
        return targets, True, note

    if not root_file.exists():
        raise SystemExit(
            f"Cannot benchmark {label}: expected umbrella file {root_file.relative_to(repo_root)}."
        )

    if label == "EASCI.ReinforcementLearning":
        # Root-only incremental `lake build EASCI.ReinforcementLearning` can miss the
        # Core/Bellman dependency edge after purging RL artifacts, so expand this one group.
        return (
            discover_group_targets(repo_root, label, include_root=True),
            False,
            "Expanded target list avoids a root-only incremental rebuild failure in ReinforcementLearning.",
        )

    return (label,), False, None


def build_module_specs(repo_root: Path) -> tuple[list[ModuleSpec], list[str]]:
    imports = load_easci_imports(repo_root)
    missing = [module for module in NON_SYNTHETIC_MODULES if module not in imports]
    if missing:
        missing_text = ", ".join(missing)
        raise SystemExit(
            f"EASCI.lean is missing expected benchmark imports: {missing_text}. "
            "Update the benchmark list before running the suite."
        )

    ordered_import_modules = [module for module in imports if module in NON_SYNTHETIC_MODULES]

    specs: list[ModuleSpec] = []
    probability_inserted = False
    for module in ordered_import_modules:
        if module == "EASCI.ReinforcementLearning" and not probability_inserted:
            probability_targets, probability_synthetic, probability_note = group_targets(
                repo_root, "EASCI.Probability"
            )
            specs.append(
                ModuleSpec(
                    label="EASCI.Probability",
                    targets=probability_targets,
                    artifact_prefix="EASCI/Probability",
                    synthetic=probability_synthetic,
                    note=probability_note,
                )
            )
            probability_inserted = True
        targets, synthetic, note = group_targets(repo_root, module)
        specs.append(
            ModuleSpec(
                label=module,
                targets=targets,
                artifact_prefix=module.replace(".", "/"),
                synthetic=synthetic,
                note=note,
            )
        )

    if not probability_inserted:
        probability_targets, probability_synthetic, probability_note = group_targets(
            repo_root, "EASCI.Probability"
        )
        specs.append(
            ModuleSpec(
                label="EASCI.Probability",
                targets=probability_targets,
                artifact_prefix="EASCI/Probability",
                synthetic=probability_synthetic,
                note=probability_note,
            )
        )

    expected = set(REQUESTED_MODULES)
    actual = {spec.label for spec in specs}
    if actual != expected:
        raise SystemExit(
            "Resolved benchmark modules do not match the W14-B2 target set. "
            f"expected={sorted(expected)} actual={sorted(actual)}"
        )

    return specs, imports


def remove_path(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_dir():
        count = sum(1 for _ in path.rglob("*")) + 1
        shutil.rmtree(path)
        return count
    path.unlink()
    return 1


def purge_artifact_prefix(repo_root: Path, artifact_prefix: str) -> int:
    deleted = 0
    roots = [repo_root / ".lake" / "build" / "lib" / "lean", repo_root / ".lake" / "build" / "ir"]
    for root in roots:
        if not root.exists():
            continue
        for candidate in sorted(root.glob(f"{artifact_prefix}.*")):
            deleted += remove_path(candidate)
        dir_candidate = root / artifact_prefix
        deleted += remove_path(dir_candidate)
    return deleted


def run_build(repo_root: Path, cmd: Sequence[str], log_path: Path) -> dict[str, object]:
    started_at = now_iso()
    display_cmd = " ".join(shlex.quote(part) for part in cmd)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[w14b2] running: {display_cmd}")
    print(f"[w14b2] log: {display_path(log_path, repo_root)}")

    start = time.perf_counter()
    proc = subprocess.Popen(
        list(cmd),
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert proc.stdout is not None
    with log_path.open("w", encoding="utf-8") as log_file:
        header = (
            f"# started_at={started_at}\n"
            f"# cwd={repo_root}\n"
            f"# command={display_cmd}\n"
        )
        sys.stdout.write(header)
        sys.stdout.flush()
        log_file.write(header)
        log_file.flush()

        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log_file.write(line)
            log_file.flush()

        proc.wait()
        elapsed = round(time.perf_counter() - start, 3)
        footer = f"# exit_code={proc.returncode}\n# wall_clock_seconds={elapsed:.3f}\n"
        sys.stdout.write(footer)
        sys.stdout.flush()
        log_file.write(footer)
        log_file.flush()

    return {
        "command": list(cmd),
        "started_at": started_at,
        "completed_at": now_iso(),
        "exit_code": proc.returncode,
        "wall_clock_seconds": elapsed,
    }


def write_snapshot(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        raise SystemExit("expected repo root as argv[1]")
    repo_root = Path(argv[1]).resolve()
    args = parse_args(argv[2:])

    if shutil.which("lake") is None:
        raise SystemExit("lake is not available on PATH; cannot run the microbenchmark suite.")

    findings_dir = repo_root / "docs" / "refactor" / "findings"
    default_output = findings_dir / f"lake-microbench-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    output_path = (repo_root / args.output).resolve() if args.output and not args.output.is_absolute() else (args.output.resolve() if args.output else default_output)
    log_dir = output_path.with_suffix("")
    log_dir = log_dir.with_name(f"{log_dir.name}.logs")

    if log_dir.exists():
        shutil.rmtree(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    module_specs, easci_imports = build_module_specs(repo_root)

    metadata = {
        "captured_at": now_iso(),
        "git_branch": run_text(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root),
        "git_commit": run_text(["git", "rev-parse", "HEAD"], repo_root),
        "lake_version": run_text(["lake", "--version"], repo_root),
        "lean_toolchain": (repo_root / "lean-toolchain").read_text(encoding="utf-8").strip(),
        "repo_root": str(repo_root),
        "requested_modules": list(REQUESTED_MODULES),
        "easci_imports": easci_imports,
    }

    print(f"[w14b2] output JSON: {display_path(output_path, repo_root)}")
    print(f"[w14b2] logs dir: {display_path(log_dir, repo_root)}")
    print(f"[w14b2] quick_mode={args.quick}")
    print(f"[w14b2] benchmark modules: {', '.join(spec.label for spec in module_specs)}")

    suite_start = time.perf_counter()
    errors: list[str] = []

    full_corpus: dict[str, object]
    if args.quick:
        full_corpus = {
            "skipped": True,
            "reason": "--quick skips the cold EASCI purge and cold full-corpus lake build.",
        }
    else:
        purged = purge_artifact_prefix(repo_root, "EASCI")
        print(f"[w14b2] purged {purged} artifacts for cold full-corpus run")
        full_log = log_dir / "full-corpus-EASCI.log"
        full_corpus = {
            "artifact_prefix": "EASCI",
            "log_path": display_path(full_log, repo_root),
            "purged_artifacts": purged,
            "skipped": False,
            "targets": ["EASCI"],
        }
        full_corpus.update(run_build(repo_root, ["lake", "build", "EASCI"], full_log))
        if int(full_corpus["exit_code"]) != 0:
            errors.append("cold full-corpus build failed")

    module_results: dict[str, dict[str, object]] = {}
    if not errors:
        for spec in module_specs:
            purged = purge_artifact_prefix(repo_root, spec.artifact_prefix)
            print(f"[w14b2] purged {purged} artifacts for {spec.label}")
            safe_name = spec.label.replace(".", "_")
            log_path = log_dir / f"{safe_name}.log"
            result = {
                "artifact_prefix": spec.artifact_prefix,
                "log_path": display_path(log_path, repo_root),
                "purged_artifacts": purged,
                "synthetic": spec.synthetic,
                "targets": list(spec.targets),
            }
            if spec.note:
                result["note"] = spec.note
            result.update(run_build(repo_root, ["lake", "build", *spec.targets], log_path))
            module_results[spec.label] = result
            if int(result["exit_code"]) != 0:
                errors.append(f"module build failed: {spec.label}")
                break

    snapshot = {
        "capture_status": "complete" if not errors else "failed",
        "captured_at": now_iso(),
        "errors": errors,
        "full_corpus": full_corpus,
        "metadata": metadata,
        "module_order": [spec.label for spec in module_specs],
        "modules": module_results,
        "quick_mode": args.quick,
        "schema_version": 1,
        "suite_wall_clock_seconds": round(time.perf_counter() - suite_start, 3),
    }
    write_snapshot(output_path, snapshot)

    print(f"[w14b2] wrote {display_path(output_path, repo_root)}")
    if errors:
        for error in errors:
            print(f"[w14b2] ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
PY
