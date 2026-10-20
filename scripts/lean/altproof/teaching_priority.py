"""Teaching-priority list (S7 completion): rank report blocks by
extraction value and low legibility.

Parses a generated report directory (corpus_report output): each block
header carries theorem + lines + verbose score; each candidate sketch
carries its estimated saving ('estimated saving ~N lines'). Priority score =
total estimated saving * (1 - verbose_score): high-value blocks that
are ALSO hard to read are where a rewrite teaches the most.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HEADER_RE = re.compile(
    r"^#### `([^`]+)` \(lines (\d+)-(\d+)\)(?: . verbose score ([\d.]+))?",
    re.MULTILINE,
)
SAVES_RE = re.compile(r"estimated saving ~(\d+) lines")
KERNEL_SAVING_RE = re.compile(r"(?:kernel saving ~|kernel delta ~|kernel_saving ~)([\d.]+)")
VERBOSE_DEFAULT = 0.5  # blocks without a score: assume middling


def priority_list(
    report_dir: Path,
    top: int = 20,
    kernel_weight: float = 1.0,
    sair_mode: bool = False,
) -> list[dict]:
    rows: list[dict] = []
    for md in sorted(report_dir.rglob("*.md")):
        if md.name == "INDEX.md":
            continue
        text = md.read_text(encoding="utf-8")
        matches = list(HEADER_RE.finditer(text))
        for i, m in enumerate(matches):
            section = text[m.end() : matches[i + 1].start() if i + 1 < len(matches) else len(text)]
            saving = sum(int(x) for x in SAVES_RE.findall(section))
            kernel_savings = [float(x) for x in KERNEL_SAVING_RE.findall(section)]
            kernel_saving = sum(kernel_savings)
            verbose = float(m.group(4)) if m.group(4) else VERBOSE_DEFAULT
            if saving <= 0 and kernel_saving <= 0:
                continue
            priority = (saving + kernel_weight * kernel_saving) * (1.0 - verbose)
            sair_priority = (kernel_saving if kernel_saving > 0 else float(saving)) * (1.0 - verbose)
            rows.append(
                {
                    "file": str(md.relative_to(report_dir))[: -len(".md")],
                    "theorem": m.group(1),
                    "lines": f"{m.group(2)}-{m.group(3)}",
                    "verbose": verbose,
                    "saving": saving,
                    "kernel_saving": kernel_saving,
                    "priority": sair_priority if sair_mode else priority,
                    "sair_priority": sair_priority,
                }
            )
    rows.sort(key=lambda r: -r["priority"])
    return rows[:top]


def render(rows: list[dict], show_kernel: bool = False) -> str:
    has_kernel = show_kernel or any(r.get("kernel_saving", 0.0) > 0 for r in rows)
    if has_kernel:
        out = [
            "# Teaching-priority blocks (extraction value + kernel cost x low legibility)",
            "",
            "| priority | file | theorem | lines | saving | kernel_saving | verbose |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in rows:
            out.append(
                f"| {r['priority']:.1f} | {r['file']} | `{r['theorem']}` "
                f"| {r['lines']} | ~{r['saving']} | ~{r.get('kernel_saving', 0.0):.1f} | {r['verbose']:.2f} |"
            )
    else:
        out = [
            "# Teaching-priority blocks (extraction value x low legibility)",
            "",
            "| priority | file | theorem | lines | saving | verbose |",
            "|---|---|---|---|---|---|",
        ]
        for r in rows:
            out.append(
                f"| {r['priority']:.1f} | {r['file']} | `{r['theorem']}` "
                f"| {r['lines']} | ~{r['saving']} | {r['verbose']:.2f} |"
            )
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    report_dir = Path(argv[1])
    rows = priority_list(report_dir)
    print(render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
