"""Extraction detector v1 - turns tactic proof text into route-table
candidates (which inline blocks are extractable into named shared
lemmas).

Heuristics:

A. have-block promotion: every `have h : T := ...` block is a
   candidate for promotion to a named shared lemma.

B. duplicated subterm (v1): operates on DELIMITER-AWARE UNITS -
   innermost parenthesized groups (e.g. `(x * x)` -> unit `x * x`)
   and depth-0 operator chains - instead of raw atom windows. A
   unit sequence of length >= 2 repeated >= 2 times is a candidate.
   SUBSUMPTION PRUNING: only maximal spans are reported - a
   candidate whose span is contained in another reported candidate's
   span (with at least as many occurrences) is dropped. This fixes
   v0's overlapping-window noise.

Quality gate: candidates must contain an identifier atom and must
not be `:=`-definition artifacts.

Estimated lines saved stays CRUDE (documented): v1 generates
candidates for the ranker + the report, it does not account.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

HAVE_RE = re.compile(r"^\s*have\s+(\w+)\s*:", re.MULTILINE)
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_'!?]*")


@dataclass
class Candidate:
    """One extraction candidate for the route table / ranker."""

    theorem: str
    route: str = "extraction-general"
    kind: str = ""  # have-block | duplicated-subterm
    evidence: str = ""  # the matched text
    occurrences: int = 1
    estimated_lines_saved: int = 1
    details: dict = field(default_factory=dict)


def detect_have_blocks(proof_text: str, theorem: str = "") -> list[Candidate]:
    """Heuristic A: every named have-block is a promotion candidate."""
    out = []
    for m in HAVE_RE.finditer(proof_text or ""):
        out.append(
            Candidate(
                theorem=theorem,
                kind="have-block",
                evidence=m.group(1),
                occurrences=1,
                estimated_lines_saved=1,
                details={"name": m.group(1)},
            )
        )
    return out


# --------------------------------------------------------------------------
# Delimiter-aware unit tokenizer (v1)
# --------------------------------------------------------------------------


def _units(proof_text: str) -> list[str]:
    """Split proof text into meaningful units: innermost parenthesized
    groups become single units (parens stripped); what remains at
    paren depth 0 is split into operator/operand atoms."""
    text = proof_text or ""
    units: list[str] = []
    # extract innermost parenthesized groups, innermost first
    stack: list[int] = []
    spans: list[tuple[int, int]] = []
    for idx, ch in enumerate(text):
        if ch == "(":
            stack.append(idx)
        elif ch == ")" and stack:
            spans.append((stack.pop(), idx))
    # innermost = spans not containing another span's open
    inner = [s for s in spans if not any(o < s[0] and c > s[1] for o, c in spans)]
    occupied = [False] * len(text)
    events: list[tuple[int, str]] = []  # (position, unit-text), document order
    for o, c in inner:
        inner_text = text[o + 1 : c].strip()
        if inner_text:
            events.append((o, inner_text))
        for k in range(o, c + 1):
            occupied[k] = True
    # depth-0 remainder -> atoms, in position
    remainder = "".join(ch if not occupied[k] else " " for k, ch in enumerate(text))
    for m in ATOM_RE.finditer(remainder):
        events.append((m.start(), m.group(0)))
    events.sort(key=lambda e: e[0])
    return [u for _, u in events]


ATOM_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_'!?]*|\d+|[+\-*/=<>:^]")


def detect_duplicated_subterms(
    proof_text: str, theorem: str = "", min_units: int = 2, min_occurrences: int = 2
) -> list[Candidate]:
    """Heuristic B (v1): repeated unit sequences with subsumption
    pruning - only maximal spans are reported."""
    units = _units(proof_text)
    n = len(units)
    found: list[tuple[int, int, int, tuple[str, ...]]] = []  # start, length, count, seq
    for length in range(n, min_units - 1, -1):
        counts: Counter[tuple[str, ...]] = Counter()
        starts: dict[tuple[str, ...], int] = {}
        for i in range(n - length + 1):
            seq = tuple(units[i : i + length])
            counts[seq] += 1
            starts.setdefault(seq, i)
        for seq, cnt in counts.items():
            if cnt >= min_occurrences:
                found.append((starts[seq], length, cnt, seq))
    # subsumption pruning: drop candidates contained in another with >= count
    maximal = []
    for start, length, cnt, seq in found:
        subsumed = any(
            (
                o <= start
                and o + span_len >= start + length
                and (o, span_len) != (start, length)
                and c2 >= cnt
            )
            for o, span_len, c2, _ in found
        )
        if not subsumed:
            maximal.append((start, length, cnt, seq))
    out = []
    for _start, length, cnt, seq in maximal:
        text = " ".join(seq)
        # v3.1: skip only HEAD binders (`ident := ...` - the span IS a
        # definition/binding, not extractable as a term).  A span that
        # merely CONTAINS named arguments (`(f := x)`) is a valid
        # extraction target: the whole invocation gets named.  The old
        # anywhere-in-span check killed every named-argument invocation
        # wholesale - the pinned multi-line-argument recall gap.
        if (
            len(seq) >= 3
            and IDENT_RE.fullmatch(seq[0])
            and seq[1] == ":"
            and seq[2] == "="
        ):
            continue
        if not any(IDENT_RE.fullmatch(u) or IDENT_RE.search(u) for u in seq):
            continue
        out.append(
            Candidate(
                theorem=theorem,
                kind="duplicated-subterm",
                evidence=text,
                occurrences=cnt,
                estimated_lines_saved=(length - 1) * (cnt - 1),
                details={"units": list(seq)},
            )
        )
    out.sort(key=lambda c: -c.estimated_lines_saved)
    return out


COMMENT_BLOCK_RE = re.compile(r"/-.*?-/", re.DOTALL)
COMMENT_LINE_RE = re.compile(r"--[^\n]*")


def _strip_comments(proof_text: str) -> str:
    """Remove Lean comments: the detector wants TERMS, and comment
    duplication (changelog pins, doc fragments) is a measured noise
    class (v2 re-audit)."""
    return COMMENT_LINE_RE.sub(" ", COMMENT_BLOCK_RE.sub(" ", proof_text or ""))


def detect(proof_text: str, theorem: str = "") -> list[Candidate]:
    """Run all heuristics; candidates sorted by estimated saving.
    Comments are stripped first (v2b: comment duplication is noise)."""
    proof_text = _strip_comments(proof_text)
    out = detect_have_blocks(proof_text, theorem)
    out += detect_duplicated_subterms(proof_text, theorem)
    out.sort(key=lambda c: -c.estimated_lines_saved)
    return out


# --------------------------------------------------------------------------
# v2 noise gate (from the measured precision audit: 65% of v1 duplicated-
# subterm candidates were token artifacts). Rules:
#   1. evidence length >= 8 characters;
#   2. >= 3 identifier occurrences in the evidence;
#   3. no binder/tactic keyword as a standalone token;
#   4. prose detection: >= 4 long lowercase words with no operator at all
#      means comment/docstring duplication, not a term.
# The gate is a POST-FILTER on heuristic B candidates; heuristic A
# (have-blocks) is untouched.
# --------------------------------------------------------------------------

V2_KEYWORDS = {
    "intro",
    "exact",
    "rw",
    "simp",
    "have",
    "apply",
    "cases",
    "induction",
    "constructor",
    "refine",
    "tauto",
    "linarith",
    "omega",
    "ring",
    "unfold",
    "Tendsto",
    "def",
    "theorem",
    "lemma",
    "by",
    "at",
    "fun",
    "forall",
    "exists",
}
V2_MIN_EVIDENCE_LEN = 8
V2_MIN_IDENTIFIERS = 3
V2_PROSE_WORDS = 4


def passes_v2_gate(candidate: Candidate) -> bool:
    """The v2 noise gate for duplicated-subterm candidates."""
    if candidate.kind != "duplicated-subterm":
        return True  # have-blocks are not gated
    ev = candidate.evidence
    if len(ev) < V2_MIN_EVIDENCE_LEN:
        return False
    if ev.lstrip().startswith(":"):
        return False  # type-ascription fragment, not a term
    units = candidate.details.get("units", ev.split())
    tokens = []
    for u in units:
        tokens += IDENT_RE.findall(u) or ([u] if u.isalpha() else [])
    idents = [t for t in tokens if t not in V2_KEYWORDS]
    if len(idents) < V2_MIN_IDENTIFIERS:
        return False
    # v3.1: strip a LEADING run of tactic keywords before the keyword
    # check.  In a duplicated statement `apply <expr>` the keyword is
    # the anchor frame; the payload `<expr>` is the duplicated content.
    # Mid-span keywords still reject (mixed tactic-glue spans stay
    # killed); the anchor tactic no longer executes the whole span.
    body = list(units)
    while body and body[0] in V2_KEYWORDS:
        body = body[1:]
    if any(u in V2_KEYWORDS for u in body):
        return False
    long_words = [t for t in idents if len(t) >= 4 and t.islower()]
    has_operator = any(not (IDENT_RE.fullmatch(u) or u.isalpha()) for u in units)
    return not (len(long_words) >= V2_PROSE_WORDS and not has_operator)


def detect_v2(proof_text: str, theorem: str = "") -> list[Candidate]:
    """detect() with the v2 noise gate applied (the recommended entry)."""
    return [c for c in detect(proof_text, theorem) if passes_v2_gate(c)]


# --------------------------------------------------------------------------
# v3: named-term demotion (from pilot 2's rejection). High occurrence
# count != defect when the term is already named: demote a candidate
# whose head identifier (a) is a module-level declaration in the file
# (passed as file_symbols), or (b) is let-bound within the same block.
# --------------------------------------------------------------------------

DECL_RE = re.compile(
    r"^(?:noncomputable\s+|private\s+|protected\s+|omit\s+[^\n]*\s+in\s+)*"
    r"(?:def|theorem|lemma|abbrev|structure|inductive|instance)\s+([A-Za-z_][\w']*)",
    re.MULTILINE,
)
LET_RE = re.compile(r"\blet\s+([A-Za-z_][\w']*)\s*:?=")
HAVE_BIND_RE = re.compile(r"\bhave\s+([A-Za-z_][\w']*)\s*:")


def module_symbols(source: str) -> set:
    """Module-level declaration names in a Lean source (textual v3
    approximation - sufficient for the demotion class)."""
    return set(DECL_RE.findall(source or ""))


def _head_identifier(candidate: Candidate):
    for u in candidate.details.get("units", []):
        m = IDENT_RE.match(u)
        if m:
            return m.group(0)
    return None


def passes_v3_gate(candidate: Candidate, proof_text: str = "",
                   file_symbols: set | None = None) -> bool:
    """v3: v2 gate + named-term demotion."""
    if not passes_v2_gate(candidate):
        return False
    if candidate.kind != "duplicated-subterm":
        return True
    head = _head_identifier(candidate)
    if head is None:
        return False
    if file_symbols and head in file_symbols:
        return False
    local_names = set(LET_RE.findall(proof_text or ""))
    local_names |= set(HAVE_BIND_RE.findall(proof_text or ""))
    if head in local_names:
        return False
    # argument-spine class (pilot 2): the evidence is the ARGUMENT TAIL
    # of an application of a module symbol - demote if the proof text
    # contains <symbol> <arg> <evidence-prefix> for any module symbol.
    units = candidate.details.get("units", [])
    if file_symbols and len(units) >= 2:
        prefix = re.escape(units[0]) + r"\s+" + re.escape(units[1])
        for sym in file_symbols:
            if re.search(re.escape(sym) + r"\s+\S+\s+" + prefix, proof_text or ""):
                return False
    return True


def detect_v3(proof_text: str, theorem: str = "",
              file_symbols: set | None = None) -> list[Candidate]:
    """The recommended entry (v3): v2 gate + named-term demotion."""
    return [c for c in detect(proof_text, theorem)
            if passes_v3_gate(c, proof_text, file_symbols)]
