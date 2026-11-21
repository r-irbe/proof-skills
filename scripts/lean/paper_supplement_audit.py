#!/usr/bin/env python3
"""Deterministic Joint Paper + Lean 4 Supplement Fidelity, Terminology & INV-001 Auditor.

Automates the six verification gates required before submitting a formalized mathematics
or CS paper alongside an anonymized or open-source Lean 4 supplementary artifact:

  1. LaTeX & BibTeX Integrity (`--tex`, `--bib`, `--max-content-pages`):
     - Embedded `filecontents*` `.bib` byte-for-byte parity with standalone `.bib`;
     - `.blg` zero BibTeX warnings and 100% `.bib` entry citation parity;
     - `.log` zero Overfull `\\hbox`/`\\vbox` and zero undefined references/citations;
     - `.aux` `lastcontentpage <= max_content_pages` budget check;
     - Knuth Ch. 18 inline-math checks (`$a$, $b$` comma splice, bare `($x$)`);
     - Optional `--forbid-first-person` prose pronoun check.
  2. Skeptical Mathematical Terminology & Anti-AI Tell Scanner:
     - Flags known mathematical misnomers/splices (`Presburger` applied to quadratic
       expressions, `Polyak step` / `Polyak-Doob` for Robbins-Monro schedules,
       `Manipulation Leverage` / `MLev`, `Dirichlet-Beta`, `minority protection`
       slogans on arithmetic quotas, `Little's law` on closed renewal cycle rates,
       and `Aware` defined as `K_i(B) = B` partition measurability);
     - Flags banned AI-tell buzzwords (`delve`, `tapestry`, `holistic`, `multifaceted`,
       `synergy`, `game-changing`, formulaic `In conclusion,`, `Notably,`).
  3. Zero `@[deprecated]` Shim Policy:
     - Rejects `@[deprecated` attributes in `.lean` files (historical renames belong
       in external Markdown ledgers, never polluting `.lean` namespaces).
  4. Lean 4 Corpus / Shaken Supplement Hygiene (`--lean-dir`, `--supplement-mode`):
     - Rejects `sorry`, `admit`, `native_decide`, `decide +native`, `decide!`, and
       source `axiom` declarations;
     - Checks `LICENSE` presence (`--supplement-mode`), `0` scrubbing scars
       (`"an upstream module"`, 4+ consecutive blank lines), `0` deprecated
       `Mathlib.Data.Real.Basic` or bare `import Mathlib` umbrella imports, and
       `0` dangling backticked references to unshipped `.lean` files.
  5. Double-Blind Anonymity (`--forbid` + workstation path scan).
  6. Scoped Three-Tier `INV-001` Unicode Policy:
     - `ascii` on `.sh` and manifests (`package.json`, `lake-manifest.json`);
     - `typographic-free` on `.lean`, `.tex`, `.bib`, `.md`, `.py`, `.ts` (mathematical
       Unicode allowed; curly quotes, en/em-dashes, horizontal ellipsis, NBSP banned);
     - Universal zero-tolerance ban on invisible/bidi/tag/surrogate carriers.

Referenced by `@lean-doc-sync`, `@lean-verification-gate`, and `@lean-proof-review`.
Scoped Unicode policy (INV-001; typographic-free source).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ASCII_MANIFEST_NAMES = {"package.json", "package-lock.json", "lake-manifest.json"}

BANNED_TYPOGRAPHIC = {
    "\u2018": "LEFT SINGLE QUOTATION MARK (use ASCII ')",
    "\u2019": "RIGHT SINGLE QUOTATION MARK (use ASCII ')",
    "\u201c": "LEFT DOUBLE QUOTATION MARK (use ASCII \")",
    "\u201d": "RIGHT DOUBLE QUOTATION MARK (use ASCII \")",
    "\u2013": "EN DASH (use ASCII - or --)",
    "\u2014": "EM DASH (use ASCII --)",
    "\u2026": "HORIZONTAL ELLIPSIS (use ASCII ...)",
    "\u00a0": "NO-BREAK SPACE (use ASCII space)",
    "\u202f": "NARROW NO-BREAK SPACE (use ASCII space)",
    "\u2009": "THIN SPACE (use ASCII space)",
    "\u200a": "HAIR SPACE (use ASCII space)",
    "\u2007": "FIGURE SPACE (use ASCII space)",
}

SUSPICIOUS_TERMINOLOGY_RULES: list[tuple[str, re.Pattern[str], str]] = [
    (
        "misnomer-polyak-step",
        re.compile(r"\b(?:IsPolyakStepSize|PolyakStepSize|Polyak[-\u2013\u2014]+Doob|PolyakDoob)\b"),
        "Robbins-Monro schedules (sum alpha = inf, sum alpha^2 < inf) are due to Robbins & Monro (1951), not Polyak or Polyak-Doob.",
    ),
    (
        "misnomer-manipulation-leverage",
        re.compile(r"\b(?:Manipulation\s+Leverage|manipulation_leverage|MLev)\b"),
        "Use Berker et al. 'Manipulation Potential' (MP), never the invented 'Manipulation Leverage' / MLev label.",
    ),
    (
        "misnomer-dirichlet-beta",
        re.compile(r"\bDirichlet\s*(?:--|[-/])\s*Beta\s+uncertainty\b", re.IGNORECASE),
        "State conjugate Beta (binomial) or Dirichlet (multinomial) evidence-count parameterization separately.",
    ),
    (
        "misnomer-minority-protection-slogan",
        re.compile(r"\bDroop\s+minority\s+protection\b|\bminority\s+protection\b", re.IGNORECASE),
        "State the exact arithmetic quota inequality (e.g. Q_Droop < floor(N/2)+1) rather than political slogans.",
    ),
    (
        "misnomer-littles-law-renewal",
        re.compile(r"\bprop:littles_law\b|validat(?:es|ing)\s+Little's\s+law", re.IGNORECASE),
        "Reciprocal cycle normalization pi_k * r = 1/Z in a closed Markov renewal loop is the renewal cycle-rate identity (Ross), not queueing Little's law L = lambda * W.",
    ),
    (
        "misnomer-presburger-quadratic",
        re.compile(r"Presburger[^\n]{0,80}(?:\^2|\u00b2|quadratic|Brier)", re.IGNORECASE),
        "Presburger arithmetic is strictly linear (N, 0, 1, +, <=) and excludes squares; call {0,...,100}^n an integer percentage grid.",
    ),
]

AI_TELL_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("ai-tell-buzzword", re.compile(r"\b(?:delve|delves|delving|tapestry|holistic|multifaceted|synergy|game-changing)\b", re.IGNORECASE)),
    ("ai-tell-formulaic-summary", re.compile(r"(?:^|\.\s+)(?:In conclusion,|In summary,|It is important to note that|Notably,)")),
]

WORKSTATION_PATH_RE = re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+/")


@dataclass
class AuditFinding:
    category: str
    severity: str
    file: str
    line: int
    rule: str
    message: str


def _is_invisible_carrier(cp: int) -> bool:
    if 0x200B <= cp <= 0x200F or cp == 0xFEFF:
        return True
    if 0x202A <= cp <= 0x202E or 0x2066 <= cp <= 0x2069:
        return True
    if 0xE0000 <= cp <= 0xE007F:
        return True
    if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:
        return True
    if 0xD800 <= cp <= 0xDFFF:
        return True
    return False


def scan_inv001_unicode(path: Path, text: str, rel_label: str) -> list[AuditFinding]:
    """Enforce three-tier INV-001 Unicode policy on a single text file."""
    findings: list[AuditFinding] = []
    strict_ascii = path.suffix == ".sh" or path.name in ASCII_MANIFEST_NAMES

    for lineno, line in enumerate(text.splitlines(), start=1):
        for ch in line:
            cp = ord(ch)
            if _is_invisible_carrier(cp):
                findings.append(
                    AuditFinding(
                        category="inv001-unicode",
                        severity="error",
                        file=rel_label,
                        line=lineno,
                        rule="invisible-or-bidi-carrier",
                        message=f"Banned invisible/bidi/variation carrier U+{cp:04X}",
                    )
                )
                break
            if strict_ascii and cp > 127:
                findings.append(
                    AuditFinding(
                        category="inv001-unicode",
                        severity="error",
                        file=rel_label,
                        line=lineno,
                        rule="strict-ascii-manifest-or-shell",
                        message=f"Non-ASCII code point U+{cp:04X} ({ch!r}) in strict-ASCII file",
                    )
                )
                break
            if not strict_ascii and ch in BANNED_TYPOGRAPHIC:
                findings.append(
                    AuditFinding(
                        category="inv001-unicode",
                        severity="error",
                        file=rel_label,
                        line=lineno,
                        rule="banned-typographic-punctuation",
                        message=f"Banned typographic character U+{cp:04X}: {BANNED_TYPOGRAPHIC[ch]}",
                    )
                )
                break
    return findings


def scan_terminology_and_anonymity(
    text: str,
    rel_label: str,
    forbidden_patterns: list[str],
    *,
    skip_tex_filecontents: bool = False,
) -> list[AuditFinding]:
    """Scan prose/comments for misnomers, AI-tell buzzwords, and anonymity leaks."""
    findings: list[AuditFinding] = []
    in_filecontents = False
    forbid_res = [
        (
            pat.strip(),
            re.compile(rf"(?<![A-Za-z]){re.escape(pat.strip())}(?![A-Za-z])", re.IGNORECASE),
        )
        for pat in forbidden_patterns
        if pat.strip()
    ]

    for lineno, line in enumerate(text.splitlines(), start=1):
        if skip_tex_filecontents:
            if r"\begin{filecontents" in line:
                in_filecontents = True
            if r"\end{filecontents" in line:
                in_filecontents = False
                continue
        if WORKSTATION_PATH_RE.search(line):
            findings.append(
                AuditFinding(
                    category="anonymity",
                    severity="error",
                    file=rel_label,
                    line=lineno,
                    rule="workstation-path-leak",
                    message="Local workstation home directory path leaked",
                )
            )
        for pat_str, pat_re in forbid_res:
            if pat_re.search(line):
                findings.append(
                    AuditFinding(
                        category="anonymity",
                        severity="error",
                        file=rel_label,
                        line=lineno,
                        rule=f"forbidden-token:{pat_str}",
                        message=f"Matched forbidden double-blind token {pat_str!r}",
                    )
                )
        if in_filecontents:
            continue
        for rule_id, pat_re, hint in SUSPICIOUS_TERMINOLOGY_RULES:
            if pat_re.search(line):
                findings.append(
                    AuditFinding(
                        category="terminology",
                        severity="error",
                        file=rel_label,
                        line=lineno,
                        rule=rule_id,
                        message=hint,
                    )
                )
        for rule_id, pat_re in AI_TELL_RULES:
            if pat_re.search(line):
                findings.append(
                    AuditFinding(
                        category="writing-quality",
                        severity="error",
                        file=rel_label,
                        line=lineno,
                        rule=rule_id,
                        message=f"Matched banned AI-tell phrasing: {pat_re.search(line).group(0)!r}",
                    )
                )
    return findings


def audit_latex_and_bib(
    tex_path: Path,
    bib_path: Path | None,
    *,
    max_content_pages: int | None = None,
    forbid_first_person: bool = False,
    forbidden_patterns: list[str] | None = None,
) -> list[AuditFinding]:
    """Audit `.tex`, `.bib`, `.log`, `.blg`, and `.aux` artifacts."""
    findings: list[AuditFinding] = []
    tex_text = tex_path.read_text(encoding="utf-8")
    tex_label = tex_path.name

    findings.extend(scan_inv001_unicode(tex_path, tex_text, tex_label))
    findings.extend(
        scan_terminology_and_anonymity(
            tex_text,
            tex_label,
            forbidden_patterns or [],
            skip_tex_filecontents=True,
        )
    )

    # Embedded filecontents* vs standalone .bib parity
    fc_match = re.search(
        r"\\begin\{filecontents\*\}\{[^}]+\.bib\}\n(.*?)\n\\end\{filecontents\*\}",
        tex_text,
        re.DOTALL,
    )
    if bib_path is not None and bib_path.is_file():
        bib_text = bib_path.read_text(encoding="utf-8")
        findings.extend(scan_inv001_unicode(bib_path, bib_text, bib_path.name))
        if fc_match is not None and fc_match.group(1).strip() != bib_text.strip():
            findings.append(
                AuditFinding(
                    category="latex-bib",
                    severity="error",
                    file=tex_label,
                    line=1,
                    rule="filecontents-bib-drift",
                    message=f"Embedded filecontents* bibliography differs from {bib_path.name}",
                )
            )
        bib_keys = set(re.findall(r"^@[A-Za-z]+\{\s*([^,\s]+)\s*,", bib_text, re.MULTILINE))
        cited_keys: set[str] = set()
        for m in re.finditer(r"\\cite[a-zA-Z*]*\{([^}]+)\}", tex_text):
            for k in m.group(1).split(","):
                if k.strip():
                    cited_keys.add(k.strip())
        if r"\nocite{*}" not in tex_text:
            uncited = sorted(bib_keys - cited_keys)
            if uncited:
                findings.append(
                    AuditFinding(
                        category="latex-bib",
                        severity="error",
                        file=bib_path.name,
                        line=1,
                        rule="uncited-bib-entries",
                        message=f"{len(uncited)} uncited .bib entries: {', '.join(uncited[:8])}",
                    )
                )

    # First-person pronouns & Knuth Ch. 18 checks outside comments and filecontents
    in_fc = False
    fp_re = re.compile(r"\b(?:we|our|us|ours|ourselves)\b", re.IGNORECASE)
    comma_math_re = re.compile(
        r"\$[^$\n]{1,24}(?:=|<|>|\\(?:in|le|ge|ne|subset|subseteq))\b[^$\n]{0,20}\$,\s+"
        r"\$[^$\n]{1,24}(?:=|<|>|\\(?:in|le|ge|ne|subset|subseteq))\b[^$\n]{0,20}\$(?!\s*,?\s*(?:and|or)\b)"
    )
    bare_paren_math_re = re.compile(r"\(\$[A-Za-z0-9_\\{}^]{1,16}\$\)")

    for lineno, raw_line in enumerate(tex_text.splitlines(), start=1):
        if r"\begin{filecontents" in raw_line:
            in_fc = True
        if r"\end{filecontents" in raw_line:
            in_fc = False
            continue
        if in_fc:
            continue
        # Strip LaTeX % comments (unescaped)
        code_line = re.sub(r"(?<!\\)%.*$", "", raw_line)
        if not code_line.strip():
            continue
        if forbid_first_person:
            no_math = re.sub(r"\$[^$]*\$", " ", code_line)
            if fp_re.search(no_math):
                findings.append(
                    AuditFinding(
                        category="writing-quality",
                        severity="error",
                        file=tex_label,
                        line=lineno,
                        rule="first-person-pronoun",
                        message=f"First-person pronoun {fp_re.search(no_math).group(0)!r} in prose",
                    )
                )
        if comma_math_re.search(code_line):
            findings.append(
                AuditFinding(
                    category="knuth-typography",
                    severity="warning",
                    file=tex_label,
                    line=lineno,
                    rule="comma-separated-inline-math",
                    message="Prefer '$a, b$' or prose connector over '$a$, $b$' (Knuth Ch. 18)",
                )
            )
        if bare_paren_math_re.search(code_line):
            findings.append(
                AuditFinding(
                    category="knuth-typography",
                    severity="warning",
                    file=tex_label,
                    line=lineno,
                    rule="bare-parenthesized-math",
                    message="Avoid bare parenthesized math '($x$)'; integrate into grammar",
                )
            )

    # Check .log, .blg, .aux if present alongside .tex
    log_path = tex_path.with_suffix(".log")
    if log_path.is_file():
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        for lineno, ln in enumerate(log_text.splitlines(), start=1):
            if ln.startswith("Overfull \\hbox") or ln.startswith("Overfull \\vbox"):
                findings.append(
                    AuditFinding(
                        category="latex-build",
                        severity="error",
                        file=log_path.name,
                        line=lineno,
                        rule="overfull-box",
                        message=ln.strip(),
                    )
                )
            if "LaTeX Warning: Reference" in ln or "LaTeX Warning: Citation" in ln or "There were undefined" in ln:
                findings.append(
                    AuditFinding(
                        category="latex-build",
                        severity="error",
                        file=log_path.name,
                        line=lineno,
                        rule="unresolved-ref-or-citation",
                        message=ln.strip(),
                    )
                )

    blg_path = tex_path.with_suffix(".blg")
    if blg_path.is_file():
        blg_text = blg_path.read_text(encoding="utf-8", errors="replace")
        for lineno, ln in enumerate(blg_text.splitlines(), start=1):
            if ln.startswith("Warning--"):
                findings.append(
                    AuditFinding(
                        category="latex-bib",
                        severity="error",
                        file=blg_path.name,
                        line=lineno,
                        rule="bibtex-warning",
                        message=ln.strip(),
                    )
                )

    aux_path = tex_path.with_suffix(".aux")
    if max_content_pages is not None and aux_path.is_file():
        aux_text = aux_path.read_text(encoding="utf-8", errors="replace")
        m_page = re.search(r"\\newlabel\{lastcontentpage\}\{\{[^}]*\}\{(\d+)\}", aux_text)
        if m_page and int(m_page.group(1)) > max_content_pages:
            findings.append(
                AuditFinding(
                    category="latex-build",
                    severity="error",
                    file=aux_path.name,
                    line=1,
                    rule="page-budget-exceeded",
                    message=f"lastcontentpage={m_page.group(1)} exceeds max_content_pages={max_content_pages}",
                )
            )

    return findings


def audit_lean_directory(
    lean_dir: Path,
    *,
    supplement_mode: bool = False,
    forbidden_patterns: list[str] | None = None,
) -> list[AuditFinding]:
    """Audit a Lean 4 directory or shaken standalone supplement."""
    findings: list[AuditFinding] = []
    lean_files = [
        p
        for p in sorted(lean_dir.rglob("*.lean"))
        if ".lake" not in p.parts and ".git" not in p.parts
    ]
    shipped_basenames = {p.name for p in lean_files}

    if supplement_mode and not (lean_dir / "LICENSE").is_file():
        findings.append(
            AuditFinding(
                category="supplement-hygiene",
                severity="error",
                file=str(lean_dir),
                line=1,
                rule="missing-supplement-license",
                message="Standalone Lean supplement is missing a root LICENSE file",
            )
        )

    for extra_name in ("README.md", "LICENSE", "lake-manifest.json"):
        ep = lean_dir / extra_name
        if ep.is_file():
            txt = ep.read_text(encoding="utf-8")
            findings.extend(scan_inv001_unicode(ep, txt, extra_name))
            findings.extend(scan_terminology_and_anonymity(txt, extra_name, forbidden_patterns or []))

    deprecated_re = re.compile(r"@\[deprecated\b")
    sorry_re = re.compile(r"\b(?:sorry|admit)\b")
    native_decide_re = re.compile(r"\bnative_decide\b|\bdecide\s*\+\s*native\b|\bdecide!")
    source_axiom_re = re.compile(r"^\s*(?:private\s+|protected\s+)?axiom\s+[A-Za-z_]")
    backtick_lean_re = re.compile(r"`([A-Za-z0-9_./-]+\.lean)(?::\d+)?`")
    upstream_top_dirs = {
        "Mathlib", "Cslib", "Batteries", "Aesop", "Std", "Lean", "Init",
        "Algebra", "Analysis", "CategoryTheory", "Combinatorics", "Computability",
        "Condensed", "Control", "Data", "Dynamics", "FieldTheory", "Geometry",
        "GroupTheory", "InformationTheory", "LinearAlgebra", "Logic",
        "MeasureTheory", "ModelTheory", "NumberTheory", "Order", "Probability",
        "RepresentationTheory", "RingTheory", "SetTheory", "Tactic", "Topology", "Util",
    }

    for lp in lean_files:
        rel = str(lp.relative_to(lean_dir))
        text = lp.read_text(encoding="utf-8")
        findings.extend(scan_inv001_unicode(lp, text, rel))
        findings.extend(scan_terminology_and_anonymity(text, rel, forbidden_patterns or []))

        if supplement_mode and "\n\n\n\n\n" in text:
            findings.append(
                AuditFinding(
                    category="supplement-hygiene",
                    severity="error",
                    file=rel,
                    line=1,
                    rule="excessive-blank-line-scar",
                    message="Found 4+ consecutive blank lines (pruning scar)",
                )
            )

        in_block_comment = 0
        for lineno, line in enumerate(text.splitlines(), start=1):
            if deprecated_re.search(line):
                findings.append(
                    AuditFinding(
                        category="lean-hygiene",
                        severity="error",
                        file=rel,
                        line=lineno,
                        rule="deprecated-shim-banned",
                        message="Remove @[deprecated] shims from .lean files; record renames in an external Markdown ledger",
                    )
                )
            if supplement_mode:
                if "an upstream module" in line:
                    findings.append(
                        AuditFinding(
                            category="supplement-hygiene",
                            severity="error",
                            file=rel,
                            line=lineno,
                            rule="scrubbing-scar-upstream-module",
                            message="Scrubbing scar 'an upstream module' found in comment",
                        )
                    )
                if re.match(r"^\s*import\s+Mathlib\.Data\.Real\.Basic\s*$", line):
                    findings.append(
                        AuditFinding(
                            category="supplement-hygiene",
                            severity="error",
                            file=rel,
                            line=lineno,
                            rule="deprecated-mathlib-real-import",
                            message="Replace deprecated 'import Mathlib.Data.Real.Basic' with 'import Mathlib.Basic.Real.Basic'",
                        )
                    )
                if re.match(r"^\s*import\s+Mathlib\s*$", line):
                    findings.append(
                        AuditFinding(
                            category="supplement-hygiene",
                            severity="error",
                            file=rel,
                            line=lineno,
                            rule="umbrella-mathlib-import",
                            message="Avoid bare umbrella 'import Mathlib' in standalone supplements",
                        )
                    )
                for bm in backtick_lean_re.finditer(line):
                    cited_raw = bm.group(1)
                    top_seg = cited_raw.split("/", 1)[0]
                    if "/" in cited_raw and top_seg in upstream_top_dirs:
                        continue
                    cited_base = Path(cited_raw).name
                    if cited_base not in shipped_basenames and cited_base != "lakefile.lean":
                        findings.append(
                            AuditFinding(
                                category="supplement-hygiene",
                                severity="error",
                                file=rel,
                                line=lineno,
                                rule="unshipped-lean-file-citation",
                                message=f"Docstring/comment cites unshipped file {bm.group(0)}",
                            )
                        )

            # Track block comments so code-only checks ignore comments
            i = 0
            code_chars: list[str] = []
            while i < len(line):
                if in_block_comment == 0 and line[i : i + 2] == "--":
                    break
                if line[i : i + 2] == "/-":
                    in_block_comment += 1
                    i += 2
                    continue
                if in_block_comment > 0 and line[i : i + 2] == "-/":
                    in_block_comment -= 1
                    i += 2
                    continue
                if in_block_comment == 0:
                    code_chars.append(line[i])
                i += 1
            code_only = "".join(code_chars)
            if not code_only.strip():
                continue
            if sorry_re.search(code_only):
                findings.append(
                    AuditFinding(
                        category="lean-soundness",
                        severity="error",
                        file=rel,
                        line=lineno,
                        rule="sorry-or-admit",
                        message="Admitted goal (sorry/admit) found in code",
                    )
                )
            if native_decide_re.search(code_only):
                findings.append(
                    AuditFinding(
                        category="lean-soundness",
                        severity="error",
                        file=rel,
                        line=lineno,
                        rule="native-decide-banned",
                        message="Compiler-trusted native_decide is banned (GT-30); use decide or kernel_decide",
                    )
                )
            if source_axiom_re.search(code_only):
                findings.append(
                    AuditFinding(
                        category="lean-soundness",
                        severity="error",
                        file=rel,
                        line=lineno,
                        rule="custom-source-axiom",
                        message="Custom source 'axiom' declaration found",
                    )
                )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit LaTeX paper, BibTeX records, and Lean 4 corpus/supplement for semantic, terminology, anonymity, and INV-001 hygiene."
    )
    parser.add_argument("--tex", type=Path, default=None, help="Path to primary .tex manuscript")
    parser.add_argument("--bib", type=Path, default=None, help="Path to standalone .bib bibliography")
    parser.add_argument("--lean-dir", type=Path, default=None, help="Path to Lean 4 corpus or shaken supplement directory")
    parser.add_argument("--supplement-mode", action="store_true", help="Enable standalone double-blind supplement checks (LICENSE, unshipped .lean citations, umbrella imports)")
    parser.add_argument("--max-content-pages", type=int, default=None, help="Maximum allowed page number for \\label{lastcontentpage} in .aux")
    parser.add_argument("--forbid-first-person", action="store_true", help="Flag first-person pronouns (we/our/us) in LaTeX prose")
    parser.add_argument("--forbid", action="append", dest="forbidden_patterns", default=[], help="Case-insensitive double-blind leak token to forbid (repeatable)")
    parser.add_argument("--strict", action="store_true", help="Treat typography warnings as blocking errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)

    if args.tex is None and args.lean_dir is None:
        parser.error("Provide at least one of --tex or --lean-dir")

    all_findings: list[AuditFinding] = []
    if args.tex is not None:
        all_findings.extend(
            audit_latex_and_bib(
                args.tex.resolve(),
                args.bib.resolve() if args.bib else None,
                max_content_pages=args.max_content_pages,
                forbid_first_person=args.forbid_first_person,
                forbidden_patterns=args.forbidden_patterns,
            )
        )
    if args.lean_dir is not None:
        all_findings.extend(
            audit_lean_directory(
                args.lean_dir.resolve(),
                supplement_mode=args.supplement_mode,
                forbidden_patterns=args.forbidden_patterns,
            )
        )

    blocking = [
        f for f in all_findings if f.severity == "error" or (args.strict and f.severity == "warning")
    ]

    if args.json:
        print(
            json.dumps(
                {
                    "passed": len(blocking) == 0,
                    "findings_count": len(all_findings),
                    "blocking_count": len(blocking),
                    "findings": [asdict(f) for f in all_findings],
                },
                indent=2,
            )
        )
    else:
        if all_findings:
            for f in all_findings[:50]:
                print(f"[{f.severity.upper()}] {f.file}:{f.line} ({f.rule}): {f.message}", file=sys.stderr)
            print(
                f"{'FAIL' if blocking else 'WARN'}: {len(all_findings)} finding(s) ({len(blocking)} blocking)",
                file=sys.stderr,
            )
        else:
            print("PASS: paper_supplement_audit found 0 defects.")

    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
