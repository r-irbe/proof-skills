#!/usr/bin/env bash
# Generic Lake build timing probe for proof-skills.
#
# Usage:
#   bash scripts/lean/lake_timer.sh SLICE [lake-target ...]
#
# Environment overrides:
#   LAKE_TIMER_OUTDIR  (or W14B2_TIMER_OUTDIR)             default: /tmp
#   LAKE_TIMER_PREFIX                                      default: w14b2-slice
#   LAKE_TIMER_SLOW_SEC (or W14B2_TIMER_SLOW_SEC)          default: 120
#   LAKE_TIMER_BELLMAN_BUDGET_SEC (or W14B2_TIMER_BELLMAN_BUDGET_SEC) default: 180
#   LAKE_TIMER_CORE_BUDGET_SEC (or W14B2_TIMER_CORE_BUDGET_SEC)       default: 480
#   LAKE_TIMER_OTHER_BUDGET_SEC (or W14B2_TIMER_OTHER_BUDGET_SEC)     default: 30
#   LAKE_TIMER_REPO_ROOT                                   default: auto-detected CWD or caller repo root

set -euxo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/lean/lake_timer.sh SLICE [lake-target ...]

Examples:
  bash scripts/lean/lake_timer.sh 3
  bash scripts/lean/lake_timer.sh 0 MyProject.Core
EOF
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

slice="$1"
shift
if ! [[ "$slice" =~ ^[0-9]+$ ]]; then
  echo "slice must be a non-negative integer (use 0 for a baseline run)" >&2
  exit 1
fi

if [[ -n "${LAKE_TIMER_REPO_ROOT:-}" ]]; then
  repo_root="$LAKE_TIMER_REPO_ROOT"
else
  repo_root="$(pwd)"
fi
cd "$repo_root"

out_dir="${LAKE_TIMER_OUTDIR:-${W14B2_TIMER_OUTDIR:-/tmp}}"
prefix="${LAKE_TIMER_PREFIX:-w14b2-slice}"
slow_threshold="${LAKE_TIMER_SLOW_SEC:-${W14B2_TIMER_SLOW_SEC:-120}}"
bellman_budget="${LAKE_TIMER_BELLMAN_BUDGET_SEC:-${W14B2_TIMER_BELLMAN_BUDGET_SEC:-180}}"
core_budget="${LAKE_TIMER_CORE_BUDGET_SEC:-${W14B2_TIMER_CORE_BUDGET_SEC:-480}}"
other_budget="${LAKE_TIMER_OTHER_BUDGET_SEC:-${W14B2_TIMER_OTHER_BUDGET_SEC:-30}}"

mkdir -p "$out_dir"
log_path="${out_dir}/${prefix}-${slice}-build-timing.log"
json_path="${out_dir}/${prefix}-${slice}-build-timing.json"

if [[ $# -eq 0 ]]; then
  build_cmd=(lake build --verbose)
else
  build_cmd=(lake build --verbose "$@")
fi

: > "$log_path"
printf '# lake_timer slice=%s\n' "$slice" | tee -a "$log_path"
printf '# log=%s\n' "$log_path" | tee -a "$log_path"
printf '# json=%s\n' "$json_path" | tee -a "$log_path"
printf '# slow_threshold_sec=%s bellman_budget_sec=%s core_budget_sec=%s other_budget_sec=%s\n' \
  "$slow_threshold" "$bellman_budget" "$core_budget" "$other_budget" | tee -a "$log_path"
printf '# command=%s\n' "${build_cmd[*]}" | tee -a "$log_path"

build_rc=0
if ! "${build_cmd[@]}" 2>&1 | tee -a "$log_path"; then
  statuses=("${PIPESTATUS[@]}")
  build_rc="${statuses[0]}"
  tee_rc="${statuses[1]:-0}"
  if [[ "$build_rc" -eq 0 && "$tee_rc" -ne 0 ]]; then
    build_rc="$tee_rc"
  fi
fi

set +e
parse_output="$({ python3 - "$log_path" "$json_path" "$slow_threshold" "$bellman_budget" "$core_budget" "$other_budget" "$build_rc" <<'PY'
import json
import re
import sys
from pathlib import Path

log_path = Path(sys.argv[1])
json_path = Path(sys.argv[2])
slow_threshold = float(sys.argv[3])
bellman_budget = float(sys.argv[4])
core_budget = float(sys.argv[5])
other_budget = float(sys.argv[6])
build_rc = int(sys.argv[7])

ansi_re = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
built_re = re.compile(r"Built\s+([^\s]+)\s+\(([^()]+)\)")
num_unit_re = re.compile(r"(\d+(?:\.\d+)?)(ms|s|m|h)")


def parse_duration(raw: str) -> float:
    total = 0.0
    matches = list(num_unit_re.finditer(raw))
    if not matches:
        raise ValueError(f"unrecognized duration format: {raw!r}")
    residue = num_unit_re.sub("", raw).strip()
    if residue:
        raise ValueError(f"unrecognized duration residue: {raw!r}")
    for match in matches:
        value = float(match.group(1))
        unit = match.group(2)
        if unit == "ms":
            total += value / 1000.0
        elif unit == "s":
            total += value
        elif unit == "m":
            total += value * 60.0
        elif unit == "h":
            total += value * 3600.0
        else:
            raise ValueError(f"unhandled duration unit: {unit!r}")
    return total


def budget_for(target: str) -> float:
    if target.endswith(".Bellman") or ".Bellman:" in target or target.endswith("/Bellman.lean"):
        return bellman_budget
    if target.endswith(".Core") or ".Core:" in target or target.endswith("/Core.lean"):
        return core_budget
    return other_budget


raw_text = log_path.read_text(encoding="utf-8", errors="replace")
normalized = ansi_re.sub("", raw_text.replace("\r", "\n"))

timings: dict[str, float] = {}
for match in built_re.finditer(normalized):
    target = match.group(1)
    seconds = round(parse_duration(match.group(2).strip()), 3)
    if target not in timings or seconds > timings[target]:
        timings[target] = seconds

json_path.write_text(
    json.dumps({k: timings[k] for k in sorted(timings)}, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

ordered = sorted(timings.items(), key=lambda item: (-item[1], item[0]))
slow = [(target, sec) for target, sec in ordered if sec > slow_threshold]
regressions = [
    (target, sec, budget_for(target))
    for target, sec in ordered
    if sec > budget_for(target)
]

print(f"timed_targets={len(ordered)}")
if ordered:
    for target, sec in ordered:
        budget = budget_for(target)
        print(f"timing {target}={sec:.3f}s budget={budget:.3f}s")
else:
    print("timing none (build likely replayed cached artifacts only)")

print(f"slow_threshold_sec={slow_threshold:.3f}")
if slow:
    print(f"slow_targets={len(slow)}")
    for target, sec in slow:
        print(f"slow {target}={sec:.3f}s")
else:
    print("slow_targets=0")

if regressions:
    print(f"budget_regressions={len(regressions)}")
    for target, sec, budget in regressions:
        print(f"regression {target}={sec:.3f}s budget={budget:.3f}s over={sec - budget:.3f}s")
else:
    print("budget_regressions=0")

if build_rc != 0:
    print(f"lake_build_rc={build_rc}")

sys.exit(2 if build_rc != 0 or regressions else 0)
PY
} 2>&1)"
parse_rc=$?
set -e

printf '%s\n' "$parse_output" | tee -a "$log_path"

exit "$parse_rc"
