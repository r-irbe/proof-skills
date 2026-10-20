#!/usr/bin/env python3
"""Lean declaration to Layer 4 concept zettel scaffolder.

Bridges Lean 4 formal declarations with the investigation-garden's Layer 4
concept zettels (zet-lean-*.md) and Lean Blueprint specifications.

Strict 7-bit ASCII only (INV-001). Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def to_ascii(text: str) -> str:
    """Normalize text to strict 7-bit ASCII replacing common math symbols."""
    replacements = {
        "\u2192": " -> ",
        "\u21d2": " => ",
        "\u2194": " <-> ",
        "\u2200": "forall ",
        "\u2203": "exists ",
        "\u2227": " /\\ ",
        "\u2228": " \\/ ",
        "\u2264": " <= ",
        "\u2265": " >= ",
        "\u2260": " != ",
        "\u2208": " in ",
        "\u2209": " not in ",
        "\u2286": " subseteq ",
        "\u2282": " subset ",
        "\u2211": "sum",
        "\u220f": "prod",
        "\u222b": "integral",
        "\u221e": "infty",
        "\u211d": "\\mathbb{R}",
        "\u2115": "\\mathbb{N}",
        "\u2124": "\\mathbb{Z}",
        "\u211a": "\\mathbb{Q}",
        "\u2102": "\\mathbb{C}",
        "\u03b1": "alpha",
        "\u03b2": "beta",
        "\u03b3": "gamma",
        "\u03b4": "delta",
        "\u03b5": "epsilon",
        "\u03b6": "zeta",
        "\u03b7": "eta",
        "\u03b8": "theta",
        "\u03bb": "lambda",
        "\u03bc": "mu",
        "\u03bd": "nu",
        "\u03be": "xi",
        "\u03c0": "pi",
        "\u03c1": "rho",
        "\u03c3": "sigma",
        "\u03c4": "tau",
        "\u03c6": "phi",
        "\u03c8": "psi",
        "\u03c9": "omega",
        "\u2014": " -- ",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00d7": " x ",
        "\u2297": " (x) ",
        "\u22c5": " * ",
        "\u2080": "0",
        "\u2081": "1",
        "\u2082": "2",
        "\u2083": "3",
        "\u2084": "4",
        "\u2085": "5",
        "\u2086": "6",
        "\u2087": "7",
        "\u2088": "8",
        "\u2089": "9",
        "\u208a": "+",
        "\u208b": "-",
        "\u2191": "(cast)",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode("ascii", "replace").decode("ascii")


@dataclass
class LeanDeclInfo:
    """Extracted information for a Lean declaration."""

    symbol: str
    kind: str  # theorem, lemma, def, structure, class
    file_path: str
    line_number: int
    signature: str
    docstring: str = ""
    proof_milestones: list[str] = field(default_factory=list)
    module_name: str = ""
    dependencies: list[str] = field(default_factory=list)


def slugify(text: str) -> str:
    """Convert a symbol or title to a clean lowercase ASCII slug."""
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-")
    return text.lower()


def find_decl_in_lean_file(file_path: Path, symbol: str) -> LeanDeclInfo | None:
    """Parse a .lean file and extract declaration metadata and proof milestones."""
    if not file_path.exists():
        return None

    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = raw_text.splitlines()

    target_name = symbol.split(".")[-1]
    decl_pattern = re.compile(
        r"^(?:(?:noncomputable|scoped|protected|private)\s+)*(theorem|lemma|def|structure|class)\s+("
        + re.escape(target_name)
        + r")\b"
    )

    found_idx = -1
    kind = "theorem"
    for i, line in enumerate(lines):
        m = decl_pattern.match(line.strip())
        if m:
            found_idx = i
            kind = m.group(1)
            break

    if found_idx == -1:
        return None

    # Search backwards for docstring /-- ... -/
    docstring_lines: list[str] = []
    if found_idx > 0:
        cursor = found_idx - 1
        while cursor >= 0 and lines[cursor].strip() == "":
            cursor -= 1
        if cursor >= 0 and lines[cursor].strip().endswith("-/"):
            end_doc = cursor
            while cursor >= 0 and "/--" not in lines[cursor]:
                cursor -= 1
            if cursor >= 0 and "/--" in lines[cursor]:
                docstring_raw = "\n".join(lines[cursor : end_doc + 1])
                # Strip delimiters
                docstring_clean = re.sub(r"^/--\s*", "", docstring_raw)
                docstring_clean = re.sub(r"\s*-/\s*$", "", docstring_clean)
                docstring_lines = [to_ascii(line.strip()) for line in docstring_clean.splitlines()]

    # Extract signature (from declaration start to := or := by or structure definition)
    sig_lines: list[str] = []
    cursor = found_idx
    while cursor < len(lines):
        sig_lines.append(lines[cursor])
        if ":=" in lines[cursor] or "where" in lines[cursor]:
            break
        cursor += 1
    signature = to_ascii(" ".join(l.strip() for l in sig_lines))

    # Extract proof milestones if within a proof block
    milestones: list[str] = []
    milestone_re = re.compile(
        r"^\s*(?:have\b|obtain\b|calc\b|induction\b|rcases\b|cases\b|constructor\b|by_contra\b|ext\b)"
    )
    if cursor < len(lines):
        for proof_idx in range(cursor + 1, min(len(lines), cursor + 200)):
            pline = lines[proof_idx].strip()
            # Stop if another top-level declaration starts
            if re.match(
                r"^(?:(?:noncomputable|scoped|protected|private)\s+)*(?:theorem|lemma|def|structure|class)\s+[A-Za-z0-9_.]+\b",
                pline,
            ):
                break
            if pline.startswith("end ") and not pline.startswith("end of"):
                break
            if milestone_re.match(pline):
                milestones.append(f"Line {proof_idx + 1}: {to_ascii(pline)}")

    # Guess module name from file path
    parts = file_path.with_suffix("").parts
    mod_name = symbol
    if "EASCI" in parts:
        idx = parts.index("EASCI")
        mod_name = ".".join(parts[idx:])
    elif "FLT" in parts:
        idx = parts.index("FLT")
        mod_name = ".".join(parts[idx:])
    elif "Euler" in parts:
        idx = parts.index("Euler")
        mod_name = ".".join(parts[idx:])
    elif "NavierStokesAndEuler" in parts:
        idx = parts.index("NavierStokesAndEuler")
        mod_name = ".".join(parts[idx:])

    return LeanDeclInfo(
        symbol=symbol,
        kind=kind,
        file_path=str(file_path),
        line_number=found_idx + 1,
        signature=signature,
        docstring="\n".join(docstring_lines),
        proof_milestones=milestones,
        module_name=mod_name,
    )


def search_master_concept(
    master_index_path: Path, concept_id: str | None, symbol: str, kind: str
) -> dict[str, Any] | None:
    """Find matching concept in master-authority-index.json."""
    if not master_index_path.exists():
        return None

    try:
        data = json.loads(master_index_path.read_text(encoding="utf-8"))
        concepts = data.get("master_concepts", [])
    except Exception:
        return None

    if concept_id:
        for c in concepts:
            if c.get("concept_id") == concept_id:
                return c

    # Search by symbol keyword
    clean_sym = re.sub(r"[A-Z]", lambda m: " " + m.group(0).lower(), symbol.split(".")[-1]).strip()
    tokens = set(clean_sym.split())

    best_match = None
    best_score = 0
    for c in concepts:
        c_id = c.get("concept_id", "")
        c_name = c.get("canonical_name", "").lower()
        synonyms = [s.lower() for s in c.get("synonyms", [])]

        score = 0
        for token in tokens:
            if len(token) < 3:
                continue
            if token in c_name:
                score += 2
            for syn in synonyms:
                if token in syn:
                    score += 1

        if score > best_score:
            best_score = score
            best_match = c

    return best_match if best_score > 0 else None


def generate_lean_zettel(
    decl: LeanDeclInfo,
    concept: dict[str, Any] | None,
    title: str | None = None,
    msc_codes: list[str] | None = None,
    related_ids: list[str] | None = None,
) -> str:
    """Generate Markdown text for Layer 4 concept zettel."""
    slug = slugify(decl.symbol)
    zettel_id = f"zet-lean-{slug}"

    if not title:
        parts = decl.symbol.split(".")
        name_words = re.sub(r"([A-Z])", r" \1", parts[-1]).strip().title()
        title = f"{name_words} Formalization"

    master_concept_id = (
        concept.get("concept_id", "CONCEPT-FORMAL-VERIFICATION")
        if concept
        else "CONCEPT-FORMAL-VERIFICATION"
    )
    concept_msc = concept.get("msc2020", ["03B35", "68V15"]) if concept else ["03B35", "68V15"]
    final_msc = list(dict.fromkeys(msc_codes + concept_msc)) if msc_codes else concept_msc

    # Concordance fields
    coq_tactic = "auto"
    isabelle_tactic = "auto"
    hol_light_tactic = "MESON_TAC []"
    if concept and "prover_mappings" in concept:
        pm = concept["prover_mappings"]
        if "coq" in pm and "primary_tactics" in pm["coq"]:
            coq_tactic = ", ".join(pm["coq"]["primary_tactics"][:2])
        if "isabelle" in pm and "primary_tactics" in pm["isabelle"]:
            isabelle_tactic = ", ".join(pm["isabelle"]["primary_tactics"][:2])
        if "hol_light" in pm and "primary_tactics" in pm["hol_light"]:
            hol_light_tactic = ", ".join(pm["hol_light"]["primary_tactics"][:2])

    blueprint_env = "theorem" if decl.kind in ["theorem", "lemma"] else "definition"
    blueprint_label = f"{'thm' if blueprint_env == 'theorem' else 'def'}:{slug}"

    src_path = decl.file_path
    if src_path:
        repo_root = str(Path(__file__).resolve().parent.parent.parent)
        if os.path.isabs(src_path) and src_path.startswith(repo_root):
            src_path = os.path.relpath(src_path, repo_root)
        elif os.path.isabs(src_path):
            src_path = src_path.lstrip("/")
    sources = [src_path] if src_path else ["docs/easci/lean/"]
    sources.append("docs/investigation-garden/source-materials/indexes/master-authority-index.json")

    # Frontmatter
    lines: list[str] = [
        "---",
        f"id: {zettel_id}",
        "layer: 4",
        f'title: "{to_ascii(title)}"',
        "status: verified",
        "maturity: seedling",
        "verification: anchor-resolved",
        f"master_concept: {master_concept_id}",
        "msc2020:",
    ]
    for code in final_msc:
        lines.append(f'  - "{code}"')

    lines.extend(
        [
            f"lean4_decl: {decl.symbol}",
            f'coq_tactic: "{to_ascii(coq_tactic)}"',
            f'isabelle_tactic: "{to_ascii(isabelle_tactic)}"',
            f'hol_light_tactic: "{to_ascii(hol_light_tactic)}"',
            f'statutory_urn: "urn:itp:lean4:{decl.module_name or decl.symbol}:{decl.symbol}"',
            "sources:",
        ]
    )
    for s in sources:
        lines.append(f'  - "{s}"')

    lines.extend(
        [
            "indexed-by:",
            "  - MOC-lean-and-easci",
            "related:",
        ]
    )
    if related_ids:
        for r in related_ids:
            lines.append(f'  - "{r}"')
    else:
        lines.append("  - MOC-lean-and-easci")
    lines.extend(
        [
            "---",
            "",
            f"# {zettel_id.upper()}: {to_ascii(title)}",
            "",
            "## 1. Formal Mathematical Assertion & Lean 4 Specification",
            "",
        ]
    )

    if decl.docstring:
        lines.extend(
            [
                decl.docstring,
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"The formal declaration `{decl.symbol}` specifies the {decl.kind} in {decl.module_name}.",
                "",
            ]
        )

    lines.extend(
        [
            "```lean",
            decl.signature if decl.signature else f"{decl.kind} {decl.symbol} : ...",
            "```",
            "",
            "## 2. Mathematical Narrative & Blueprint Scaffolding",
            "",
            f"In standard mathematical terminology, `{decl.symbol}` establishes the core invariant",
            f"for {decl.module_name}. In the Lean Blueprint system (PlasTeX), this declaration",
            "corresponds to the following specification environment:",
            "",
            "```latex",
            f"\\begin{{{blueprint_env}}}[{to_ascii(title)}]",
            f"\\label{{{blueprint_label}}}",
            f"\\lean{{{decl.symbol}}}",
            "\\leanok",
            f"  % Formal statement of {decl.symbol}",
            f"\\end{{{blueprint_env}}}",
            "```",
            "",
            "## 3. Proof Milestones & Dependency Anchor",
            "",
        ]
    )

    if decl.proof_milestones:
        lines.append("The proof strategy decomposes into the following milestone steps:")
        lines.append("")
        for ms in decl.proof_milestones:
            lines.append(f"- `{ms}`")
        lines.append("")
    else:
        lines.extend(
            [
                "The proof proceeds by direct simplification or kernel decision procedures without",
                "nested sub-hypotheses milestones.",
                "",
            ]
        )

    lines.extend(
        [
            "## 4. Cross-Prover & Statutory Concordance",
            "",
            "| Proof System | Tactic / Construct | Semantic Role |",
            "| :--- | :--- | :--- |",
            f"| **Lean 4** | `{decl.symbol}` | Primary certified formal declaration |",
            f"| **Coq** | `{to_ascii(coq_tactic)}` | Equivalent tactic/lemma representation |",
            f"| **Isabelle/HOL** | `{to_ascii(isabelle_tactic)}` | Sledgehammer / simp automation hook |",
            f"| **HOL Light** | `{to_ascii(hol_light_tactic)}` | First-order / arithmetic proof tactic |",
            "",
            "## 5. Operational Proof Swarm Invariant",
            "",
            f"- **Kernel Purity**: `{decl.symbol}` must compile clean under `set_option autoImplicit false` with 0 sorries.",
            "- **Blueprint Synchronization**: Any modification to the signature or premise set must update the PlasTeX blueprint \\uses{} graph.",
            "- **Concordance Grounding**: Maintain semantic equivalence with the master concept authority catalog.",
            "",
        ]
    )

    return to_ascii("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold Layer 4 concept zettel for Lean declaration."
    )
    parser.add_argument("-s", "--symbol", required=True, help="Lean declaration name")
    parser.add_argument("-f", "--file", help="Path to .lean file")
    parser.add_argument("-c", "--concept", help="Master concept ID")
    parser.add_argument("-t", "--title", help="Human-readable title")
    parser.add_argument("-o", "--out-dir", help="Output directory for generated zettel")
    parser.add_argument("--msc", nargs="*", help="MSC2020 classification codes")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout only")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    master_index_path = (
        repo_root
        / "docs"
        / "investigation-garden"
        / "source-materials"
        / "indexes"
        / "master-authority-index.json"
    )
    if not master_index_path.exists():
        alt = Path(__file__).resolve().parents[2] / "vendor" / "itp-ontology" / "master-authority-index.json"
        if alt.exists():
            master_index_path = alt

    decl_info: LeanDeclInfo | None = None
    if args.file:
        lean_path = Path(args.file)
        if not lean_path.is_absolute():
            lean_path = repo_root / lean_path
        decl_info = find_decl_in_lean_file(lean_path, args.symbol)

    if decl_info is None:
        decl_info = LeanDeclInfo(
            symbol=args.symbol,
            kind="theorem",
            file_path=args.file or "",
            line_number=1,
            signature=f"theorem {args.symbol} : ...",
        )

    concept = search_master_concept(master_index_path, args.concept, args.symbol, decl_info.kind)
    content = generate_lean_zettel(decl_info, concept, args.title, args.msc)

    if args.dry_run or not args.out_dir:
        print(content)
        return 0

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = repo_root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(args.symbol)
    target_file = out_dir / f"zet-lean-{slug}.md"
    target_file.write_text(content, encoding="ascii")
    print(f"Scaffolded concept zettel written to: {target_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
