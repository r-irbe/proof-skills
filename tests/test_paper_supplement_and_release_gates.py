"""Regression tests for `paper_supplement_audit.py`, `cold_kernel_replay.lean`,
handbook table compilation parity, and `< 4,000`-byte `SKILL.md` discipline.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT_SCRIPT = ROOT / "scripts" / "lean" / "paper_supplement_audit.py"
COMPILE_TABLES = ROOT / "scripts" / "lean" / "compile_handbook_tables.py"


def _run_audit(*args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(AUDIT_SCRIPT), *args, "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    payload = json.loads(proc.stdout)
    return proc.returncode, payload


def test_paper_supplement_audit_passes_clean_bundle(tmp_path: Path):
    bib_body = (
        "@book{doob1953,\n"
        "  author = {Doob, Joseph L.},\n"
        "  title = {Stochastic Processes},\n"
        "  publisher = {Wiley},\n"
        "  year = {1953}\n"
        "}\n"
    )
    bib_path = tmp_path / "paper.bib"
    bib_path.write_text(bib_body, encoding="utf-8")

    tex_body = (
        "\\begin{filecontents*}{paper.bib}\n"
        + bib_body
        + "\\end{filecontents*}\n"
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "For all $x \\in \\mathbb{R}$ and $n \\ge 1$, the bound $a/b \\le 1$ holds~\\cite{doob1953}.\n"
        "\\label{lastcontentpage}\n"
        "\\end{document}\n"
    )
    tex_path = tmp_path / "paper.tex"
    tex_path.write_text(tex_body, encoding="utf-8")
    (tmp_path / "paper.aux").write_text(
        "\\newlabel{lastcontentpage}{{1}{8}{Conclusion}{section.1}{}}\n",
        encoding="utf-8",
    )
    (tmp_path / "paper.log").write_text("Output written on paper.pdf (9 pages).\n", encoding="utf-8")
    (tmp_path / "paper.blg").write_text("You've used 1 entry.\n", encoding="utf-8")

    supp = tmp_path / "supplement"
    (supp / "Demo").mkdir(parents=True)
    (supp / "LICENSE").write_text("Apache License 2.0\n", encoding="utf-8")
    (supp / "lake-manifest.json").write_text('{"version": "1.2.0", "packages": []}\n', encoding="utf-8")
    # Mathematical Unicode (∀, ℝ, ≤) is permitted in typographic-free mode, and upstream Mathlib paths are allowed
    (supp / "Demo" / "Core.lean").write_text(
        "import Mathlib.Basic.Real.Basic\n"
        "set_option autoImplicit false\n"
        "/-- Adapted upstream helper (compare `Geometry/Convex/ConvexSpace/Defs.lean`). -/\n"
        "theorem nonneg_sq (x : ℝ) : 0 ≤ x ^ 2 := sq_nonneg x\n",
        encoding="utf-8",
    )

    rc, payload = _run_audit(
        "--tex",
        str(tex_path),
        "--bib",
        str(bib_path),
        "--lean-dir",
        str(supp),
        "--supplement-mode",
        "--max-content-pages",
        "9",
        "--forbid-first-person",
        "--strict",
    )
    assert rc == 0, f"Expected clean pass, got: {payload}"
    assert payload["passed"] is True
    assert payload["findings_count"] == 0


def test_paper_supplement_audit_catches_misnomers_deprecated_and_inv001(tmp_path: Path):
    bib_path = tmp_path / "bad.bib"
    bib_path.write_text(
        "@article{used2024, author={A}, title={B}, year={2024}}\n"
        "@article{unused2025, author={C}, title={D}, year={2025}}\n",
        encoding="utf-8",
    )
    tex_path = tmp_path / "bad.tex"
    tex_path.write_text(
        "\\begin{filecontents*}{bad.bib}\n"
        "@article{used2024, author={A}, title={Different}, year={2024}}\n"
        "\\end{filecontents*}\n"
        "We delve into Droop minority protection and Dirichlet--Beta uncertainty~\\cite{used2024}.\n",
        encoding="utf-8",
    )

    supp = tmp_path / "bad_supp"
    supp.mkdir()
    # Missing LICENSE, non-ASCII in lake-manifest.json, @[deprecated], IsPolyakStepSize, unshipped LocalSecret.lean, and bidi/em-dash
    (supp / "lake-manifest.json").write_text('{"note": "\u2014"}\n', encoding="utf-8")
    (supp / "Bad.lean").write_text(
        "import Mathlib.Data.Real.Basic\n"
        "/-- Validates Little's law \u2014 see `LocalSecret.lean:10`\u200b. -/\n"
        "def IsPolyakStepSize (n : Nat) : Bool := true\n"
        "@[deprecated IsPolyakStepSize (since := \"2026-11-01\")]\n"
        "abbrev oldAlias := IsPolyakStepSize\n",
        encoding="utf-8",
    )

    rc, payload = _run_audit(
        "--tex",
        str(tex_path),
        "--bib",
        str(bib_path),
        "--lean-dir",
        str(supp),
        "--supplement-mode",
        "--forbid-first-person",
        "--strict",
    )
    assert rc == 1
    rules = {f["rule"] for f in payload["findings"]}
    expected_rules = {
        "filecontents-bib-drift",
        "uncited-bib-entries",
        "first-person-pronoun",
        "ai-tell-buzzword",
        "misnomer-minority-protection-slogan",
        "misnomer-dirichlet-beta",
        "missing-supplement-license",
        "strict-ascii-manifest-or-shell",
        "deprecated-mathlib-real-import",
        "deprecated-shim-banned",
        "misnomer-polyak-step",
        "misnomer-littles-law-renewal",
        "unshipped-lean-file-citation",
        "banned-typographic-punctuation",
    }
    missing = expected_rules - rules
    assert not missing, f"Expected rules {missing} not triggered; got {rules}"


def test_handbook_tables_up_to_date_and_skill_byte_budgets():
    chk = subprocess.run(
        [sys.executable, str(COMPILE_TABLES), "--check"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert chk.returncode == 0, f"handbook-tables.v1.json out of date:\n{chk.stdout}\n{chk.stderr}"

    oversized: list[tuple[str, int]] = []
    for sk in sorted((ROOT / "skills").glob("*/SKILL.md")):
        sz = len(sk.read_bytes())
        if sz >= 4000:
            oversized.append((str(sk.relative_to(ROOT)), sz))
    assert not oversized, f"SKILL.md files must stay strictly < 4,000 bytes: {oversized}"

    struct = subprocess.run(
        [str(ROOT / "scripts" / "check-structure")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert struct.returncode == 0
    assert "PASS: 0 warning(s)" in struct.stdout, f"Unexpected check-structure warnings:\n{struct.stdout}"

    assert (ROOT / "scripts" / "lean" / "cold_kernel_replay.lean").is_file()
    assert (ROOT / "references" / "protocols" / "double-blind-paper-and-supplement-release.md").is_file()
