#!/usr/bin/env bash
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
# check-native-decide.sh — audit `native_decide` justifications in a Lean source tree.
#
# Usage:
#   check-native-decide.sh LEAN_DIR
#
# Counts `native_decide` occurrences under LEAN_DIR/**/*.lean and reports any
# call-site that lacks a documented KEEP marker.
#
# A `native_decide` call-site is considered JUSTIFIED iff one of the five
# lines preceding it (inclusive of the call line itself) contains the string:
#
#     KEEP per native-decide playbook
#
# inside a Lean comment (`--` or `/- ... -/`). Any unmarked occurrence is
# reported as an UNJUSTIFIED site and the script exits 1.
#
# Exit codes:
#   0  — every native_decide site is justified (or there are zero sites)
#   1  — at least one unjustified site
#   2  — usage / I/O error

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 LEAN_DIR" >&2
  exit 2
fi

LEAN_DIR="$1"
if [[ ! -d "$LEAN_DIR" ]]; then
  echo "check-native-decide: cannot find $LEAN_DIR" >&2
  exit 2
fi

LEAN_DIR="$(cd "$LEAN_DIR" && pwd)"

# Per-call-site KEEP justification window: the marker may live on the
# call line itself or up to 5 lines above (6-line inclusive window).
WINDOW=6

# Marker that authorizes a KEEP. Kept as a single string so it can be
# documented and grepped consistently.
KEEP_MARKER="KEEP per native-decide playbook"

total=0
justified=0
unjustified=0
unjustified_report=""

# Use NUL-delimited find to be safe with unusual paths.
while IFS= read -r -d '' file; do
  # awk pass: emit one line per native_decide occurrence:
  #   <lineno>\t<JUSTIFIED|UNJUSTIFIED>\t<trimmed source line>
  while IFS=$'\t' read -r lineno status line; do
    total=$((total + 1))
    if [[ "$status" == "JUSTIFIED" ]]; then
      justified=$((justified + 1))
    else
      unjustified=$((unjustified + 1))
      unjustified_report+="  ${file#$LEAN_DIR/}:${lineno}: ${line}"$'\n'
    fi
  done < <(awk -v window="$WINDOW" -v marker="$KEEP_MARKER" '
    BEGIN { depth = 0 }
    {
      raw = $0
      buf[NR % window] = raw

      # Strip text inside /- ... -/ block comments (handles nesting and
      # /-! ... -/ doc blocks). Walk the line char-by-char while
      # respecting current depth.
      out = ""
      i = 1
      n = length(raw)
      while (i <= n) {
        if (depth == 0 && i < n && substr(raw, i, 2) == "/-") {
          depth = 1
          i += 2
          continue
        }
        if (depth > 0 && i < n && substr(raw, i, 2) == "/-") {
          depth += 1
          i += 2
          continue
        }
        if (depth > 0 && i < n && substr(raw, i, 2) == "-/") {
          depth -= 1
          if (depth < 0) depth = 0
          i += 2
          continue
        }
        if (depth == 0) {
          out = out substr(raw, i, 1)
        }
        i += 1
      }

      # Strip `--` line comments from the surviving code text.
      pos = index(out, "--")
      if (pos > 0) out = substr(out, 1, pos - 1)

      if (index(out, "native_decide") == 0) next

      # Scan the WINDOW preceding lines (including current) for the
      # KEEP marker. The marker may itself live inside a comment, which
      # is the whole point.
      justified = 0
      for (k = 0; k < window; k++) {
        idx = (NR - k) % window
        if (idx in buf && index(buf[idx], marker) > 0) {
          justified = 1
          break
        }
      }
      trimmed = raw
      sub(/^[[:space:]]+/, "", trimmed)
      printf "%d\t%s\t%s\n", NR, (justified ? "JUSTIFIED" : "UNJUSTIFIED"), trimmed
    }
  ' "$file")
done < <(find "$LEAN_DIR" -type f -name '*.lean' -print0)

echo "check-native-decide: ${total} total, ${justified} justified, ${unjustified} unjustified"

if (( unjustified == 0 )); then
  exit 0
fi

echo
echo "Unjustified native_decide sites (need '${KEEP_MARKER}' within 5 lines above):"
printf '%s' "$unjustified_report"
exit 1
