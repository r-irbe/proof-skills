#!/usr/bin/env python3
# Originally extracted from a Lean 4 verification project and genericized for the proof-skills toolkit.
"""
Proof Quality Analyzer for Lean 4 projects.

Static analysis of Lean 4 proof quality:
  - Detect potential vacuous truths (empty hypotheses → trivial conclusions)
  - Find overly long proofs (candidate for decomposition)
  - Detect redundant hypotheses (hypothesis never used in proof term)
  - Find tactic diversity (over-reliance on omega/simp)
  - Detect potential duplication (similarly-structured theorems)

Usage:
    python3 scripts/lean/proof_quality.py [--lean-dir MyProject] [--output proof_quality.md]
"""

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def analyze_module(filepath: Path) -> dict:
    """Analyze proof quality for one module."""
    text = filepath.read_text(encoding='utf-8')
    lines = text.splitlines()
    module = filepath.stem

    findings = []
    stats = {
        'module': module,
        'tactic_usage': Counter(),
        'proof_lengths': [],
        'theorem_count': 0,
    }

    # Parse theorem blocks from the comment-stripped source so that
    # interspersed `/- Remark: ... -/` blocks between theorems do not
    # leak into the previous theorem's body line-count.  Stripping
    # preserves line numbers (each comment char becomes a space) so
    # `thm['line']` and the rest of the analysis remain accurate.
    # (W12 r03, replaces an earlier column-0 `/-` halt-condition
    # heuristic that was unsafe inside `by`-blocks.)
    stripped_text = '\n'.join(_strip_lean_comments(lines))
    theorem_blocks = extract_theorem_blocks(stripped_text)

    for thm in theorem_blocks:
        stats['theorem_count'] += 1

        # Count tactics used
        tactics_used = extract_tactics(thm['body'])
        for tactic in tactics_used:
            stats['tactic_usage'][tactic] += 1

        # Proof length (count non-blank, non-comment lines only)
        proof_lines = [l for l in thm['body'].splitlines()
                       if l.strip() and not l.strip().startswith('--')]
        body_lines = len(proof_lines)
        stats['proof_lengths'].append((thm['name'], body_lines))

        # Long-proof bands (W12 r04, after rubber-duck critique):
        # Mathlib4 routinely contains substantive proofs of 50–100
        # lines without enforcing a hard limit.  Splitting the
        # severity reflects this: 31–59 is advisory (P3), 60–99 is
        # improvement (P2), and ≥100 is a strong-signal P1 outlier.
        # Bands preserve visibility while reserving the loud signal
        # for genuine outliers.
        if body_lines >= 100:
            findings.append({
                'type': 'long-proof',
                'severity': 'P1',
                'theorem': thm['name'],
                'line': thm['line'],
                'detail': (
                    f'Proof is {body_lines} lines — strongly consider '
                    f'decomposition or extraction of reusable lemmas'
                ),
            })
        elif body_lines >= 60:
            findings.append({
                'type': 'long-proof',
                'severity': 'P2',
                'theorem': thm['name'],
                'line': thm['line'],
                'detail': (
                    f'Proof is {body_lines} lines — consider decomposition'
                ),
            })
        elif body_lines > 30:
            findings.append({
                'type': 'long-proof',
                'severity': 'P3',
                'theorem': thm['name'],
                'line': thm['line'],
                'detail': (
                    f'Proof is {body_lines} lines — review for natural '
                    f'helper-lemma extraction (advisory)'
                ),
            })

        # Check for potential vacuous truth
        if is_vacuous_candidate(thm['signature'], thm['body']):
            findings.append({
                'type': 'vacuous-candidate',
                'severity': 'P1',
                'theorem': thm['name'],
                'line': thm['line'],
                'detail': 'May be vacuously true — proof uses False.elim or absurd with impossible hypothesis',
            })

        # Check hypothesis usage
        unused = find_unused_hypotheses(thm['signature'], thm['body'])
        for hyp in unused:
            findings.append({
                'type': 'unused-hypothesis',
                'severity': 'P2',
                'theorem': thm['name'],
                'line': thm['line'],
                'detail': f'Hypothesis {hyp} appears unused in proof body',
            })

    # @[simp] loop-risk scan (W9 HITL B-1): for each `@[simp]` rewrite rule,
    # if the head symbol of the LHS occurs as a function application in the
    # RHS, flag it as a potential rewrite loop. False positives are possible
    # for terminating simp lemmas that recurse on a strictly smaller
    # argument; manual review of any flagged rule is required.
    findings.extend(find_simp_loops(text, theorem_blocks))

    # Heartbeat-budget scan (W10 r27): file-level `set_option maxHeartbeats N`
    # values that exceed sane review thresholds are flagged. The rule is:
    #   * N ≤ 200_000 — clean (default Lean budget is 200_000)
    #   * 200_000 < N ≤ 1_000_000 — P2 warning (consider proof split / hint)
    #   * N > 1_000_000 — P1 (almost always indicates an unfinished refactor
    #     or a perf regression that should be tracked).
    # `set_option maxHeartbeats 0` disables the budget entirely and is also
    # flagged as P1 (defeats the elaborator's safety net).
    findings.extend(find_heartbeat_overrides(text, filepath))

    # Tactic diversity check
    total_tactics = sum(stats['tactic_usage'].values())
    if total_tactics > 0:
        top_tactic, top_count = stats['tactic_usage'].most_common(1)[0]
        if top_count / total_tactics > 0.5 and total_tactics > 10:
            findings.append({
                'type': 'low-tactic-diversity',
                'severity': 'P3',
                'theorem': '(module-level)',
                'line': 0,
                'detail': f'{top_tactic} used {top_count}/{total_tactics} times ({top_count/total_tactics:.0%})',
            })

    return {'findings': findings, 'stats': stats}


def extract_theorem_blocks(text: str) -> list[dict]:
    """Extract theorem name, signature, body, and line number.

    Uses indentation-aware body extraction: the proof body starts
    after `:= by` and ends when a line at column 0 begins a new
    top-level declaration (theorem, lemma, def, structure, etc.)
    or a section marker (`-- §`).
    """
    blocks = []
    lines = text.splitlines()
    i = 0
    # Top-level declaration starters.  Includes `private theorem`/
    # `private lemma` and attribute-prefixed `@[…] theorem` since the
    # body extractor uses this regex to know when to stop collecting
    # proof lines.  Without these, the comment-stripping introduced in
    # W12 r03 caused the extractor to swallow subsequent
    # `private theorem ...` declarations into the previous theorem's
    # body (the old extraction relied on `-- §N` block-headers as
    # accidental terminators).  (W12 r03b.)
    TOP_LEVEL = re.compile(
        r'^(?:@\[[^\]]*\]\s*)*'
        r'(?:theorem|lemma|private\s+theorem|private\s+lemma|'
        r'def|noncomputable\s+def|noncomputable\s+instance|'
        r'abbrev|structure|inductive|class|instance|end|namespace|section|'
        r'open|set_option|attribute|#|/--|--\s*[§=])'
    )
    while i < len(lines):
        # Match theorem/lemma at column 0, with optional leading
        # `@[...]` attribute markers (e.g., `@[simp] theorem foo`).
        m = re.match(
            r'^(?:@\[[^\]]*\]\s*)*(theorem|lemma|private\s+theorem|private\s+lemma)\s+(\S+)',
            lines[i])
        if not m:
            i += 1
            continue
        kind = m.group(1)
        raw_name = m.group(2).split('(')[0].split(':')[0].strip()
        start_line = i + 1  # 1-based

        # Collect signature lines until `:= by`
        sig_lines = []
        j = i
        found_by = False
        while j < len(lines):
            line = lines[j]
            # If we hit a NEW top-level declaration (not the current one),
            # this theorem doesn't use `by` — skip it
            if j > i and line and line[0] != ' ' and line[0] != '\t':
                if TOP_LEVEL.match(line) or re.match(
                    r'^(?:theorem|lemma|private\s+theorem|private\s+lemma)\s', line
                ):
                    break
            sig_lines.append(line)
            if ':= by' in line or ':=by' in line:
                found_by = True
                break
            if re.search(r':=\s*$', line) and j + 1 < len(lines) and lines[j+1].strip().startswith('by'):
                sig_lines.append(lines[j+1])
                j += 1
                found_by = True
                break
            j += 1
        if not found_by:
            i += 1
            continue

        # Extract signature (before `:= by`) and find body start
        full_sig = '\n'.join(sig_lines)
        by_idx = full_sig.find(':= by')
        if by_idx == -1:
            by_idx = full_sig.find(':=by')
        if by_idx == -1:
            by_idx = full_sig.rfind(':=')
        signature = full_sig[:by_idx] if by_idx >= 0 else full_sig

        # Collect body lines: everything indented after `:= by` until
        # the next top-level declaration at column 0
        body_lines = []
        # Remainder of the `:= by` line after `by`
        by_line = lines[j]
        after_by = by_line[by_line.index('by') + 2:] if 'by' in by_line else ''
        if after_by.strip():
            body_lines.append(after_by)
        j += 1
        while j < len(lines):
            line = lines[j]
            # Blank or indented lines are part of the body
            if line == '' or (line[0:1] == ' ' or line[0:1] == '\t'):
                body_lines.append(line)
                j += 1
                continue
            # Non-indented non-blank line: check if it's a top-level start
            if TOP_LEVEL.match(line):
                break
            # Otherwise, might be a continuation (e.g., `| pattern =>`)
            body_lines.append(line)
            j += 1

        body = '\n'.join(body_lines)
        blocks.append({
            'kind': kind,
            'name': raw_name,
            'signature': signature,
            'body': body,
            'line': start_line,
        })
        i = j  # advance past body
    return blocks


def extract_tactics(body: str) -> list[str]:
    """Extract tactic names from a proof body."""
    # Common Lean 4 tactics
    known_tactics = [
        'simp', 'omega', 'linarith', 'nlinarith', 'norm_num', 'ring', 'ring_nf',
        'exact', 'apply', 'intro', 'intros', 'constructor', 'cases', 'induction',
        'rfl', 'ext', 'funext', 'congr', 'rw', 'rewrite', 'subst',
        'have', 'let', 'obtain', 'rcases', 'rintro',
        'contradiction', 'absurd', 'exfalso',
        'aesop', 'decide', 'trivial', 'assumption',
        'calc', 'conv', 'show', 'suffices',
        'refine', 'use', 'existsi',
        'push_neg', 'by_contra', 'by_cases',
        'gcongr', 'positivity', 'bound_tac',
        'auto', 'duper',
    ]

    found = []
    for tactic in known_tactics:
        pattern = re.compile(rf'\b{re.escape(tactic)}\b')
        count = len(pattern.findall(body))
        found.extend([tactic] * count)

    return found


def is_vacuous_candidate(signature: str, body: str) -> bool:
    """Heuristic: check if proof might be vacuously true.

    Only flags proofs where:
    1. The conclusion is `False` (disjointness/impossibility), AND
    2. The body doesn't use `rw [..._iff]` (which means the
       hypotheses are being rewritten to extract real content).

    Intentional disjointness proofs (e.g., two regimes can't overlap)
    that use `rw [classify_stable_iff]` etc. are NOT flagged, because
    they derive `False` from genuinely contradictory semantic conditions
    rather than from structurally impossible hypotheses.
    """
    if 'False.elim' in body or 'absurd' in body or 'exfalso' in body:
        # If conclusion is False and proof rewrites iff-lemmas,
        # it's an intentional disjointness proof → skip
        if re.search(r'rw\s*\[.*_iff', body):
            return False
        # Only flag if the hypotheses look structurally impossible
        if 'False' in signature or '0 > 1' in signature or '¬ True' in signature:
            return True
    return False


def find_unused_hypotheses(signature: str, body: str) -> list[str]:
    """Find named hypotheses that don't appear in the proof body.

    Heuristic — precision-over-recall.  The detector intentionally
    suppresses ALL findings for a theorem whose proof body contains
    any whole-context automation tactic (`omega`, `simp`, `simpa`,
    `nlinarith`, `linarith`, `ring`, `decide`, `positivity`, `norm_num`,
    `aesop`, `tauto`, `trivial`, `assumption`, `simp_all`, `grind`,
    `exact_mod_cast`).  These tactics consume the entire local context
    without naming individual hypotheses; deciding *which* hypothesis is
    actually unused would require running Lean.  We accept the precision
    tradeoff: a hypothesis that is genuinely unused but happens to live
    in a `grind`-using proof will not be flagged.  False positives are
    much more harmful than missed findings here, because every false
    positive prompts a manual investigation that confirms "consumed by
    automation".

    Other accounting:
    - Parameters starting with `_` are intentionally unused by convention
    - Parameters appearing in the goal/conclusion (after the last
      top-level `:`) are needed by the type system even if the proof
      text never names them
    - `unfold`/`rfl`/`rw`/`cases`/`simp_all` similarly consume structure
      parameters
    """
    # Precision-over-recall: any whole-context automation tactic in the
    # body suppresses unused-hyp findings for this theorem (see
    # docstring).  `grind` is Mathlib's modern hammer (Lean 4.x+) and
    # `simpa` is `simp ... using h`; both behave like simp/linarith.
    # (W12 r01.)
    AUTOMATION_TACTICS = [
        'omega', 'simp', 'simpa', 'nlinarith', 'linarith', 'ring', 'decide',
        'positivity', 'norm_num', 'auto', 'duper', 'aesop', 'tauto',
        'trivial', 'assumption', 'exact_mod_cast', 'simp_all', 'grind',
    ]
    for tactic in AUTOMATION_TACTICS:
        if re.search(rf'\b{re.escape(tactic)}\b', body):
            return []  # cannot determine unused-ness via text matching

    # Also skip if proof uses `unfold` (consumes structure parameters)
    if 'unfold' in body:
        return []

    # Extract the conclusion/goal part (after the last top-level `:`)
    # Parameters appearing in the conclusion are needed by the type system
    conclusion = ''
    # Find conclusion: everything after the last `:` that's not inside parens
    # OR braces (the latter matters for struct-literal `{ field := ... }` in
    # the goal, where ad-hoc `:` characters appear inside `{...}` and would
    # otherwise displace `last_colon_pos` away from the true top-level
    # signature colon).  (W12 r02.)
    paren_depth = 0
    brace_depth = 0
    bracket_depth = 0
    last_colon_pos = -1
    i = 0
    while i < len(signature):
        ch = signature[i]
        # Skip `:=` (binding marker), it must not be counted as a top-level `:`
        if ch == ':' and i + 1 < len(signature) and signature[i + 1] == '=':
            i += 2
            continue
        if ch == '(':
            paren_depth += 1
        elif ch == ')':
            paren_depth -= 1
        elif ch == '{':
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
        elif ch == '[':
            bracket_depth += 1
        elif ch == ']':
            bracket_depth -= 1
        elif (
            ch == ':'
            and paren_depth == 0
            and brace_depth == 0
            and bracket_depth == 0
        ):
            last_colon_pos = i
        i += 1
    if last_colon_pos >= 0:
        conclusion = signature[last_colon_pos:]

    # Build the full context: conclusion + body + all hypothesis types
    # (a parameter used in another hypothesis's type is still "used")
    full_context = conclusion + '\n' + body

    unused = []
    # Extract hypothesis names: (hName : Type)
    hyp_pattern = re.compile(r'\((\w+)\s*:')
    hyps = list(hyp_pattern.finditer(signature))
    hyp_names = {m.group(1) for m in hyps}
    for m in hyps:
        hyp_name = m.group(1)
        # Skip single-char type variables
        if len(hyp_name) <= 1:
            continue
        # Skip intentionally unused (underscore prefix)
        if hyp_name.startswith('_'):
            continue
        # Skip if appears in the conclusion (needed by type system)
        if hyp_name in conclusion:
            continue
        # Skip if appears in any OTHER hypothesis's type in the signature
        # (the text between this param's `:` and the next `(` or end)
        used_in_other_hyp = False
        for other in hyps:
            if other.start() == m.start():
                continue
            # Check the type text of the other hypothesis
            other_start = other.end()  # after the `:`
            other_end = signature.find(')', other_start)
            if other_end == -1:
                other_end = len(signature)
            other_type = signature[other_start:other_end]
            if hyp_name in other_type:
                used_in_other_hyp = True
                break
        if used_in_other_hyp:
            continue
        # Check if hypothesis name appears in body
        if hyp_name not in body:
            unused.append(hyp_name)
    return unused


def _strip_lean_comments(lines: list[str]) -> list[str]:
    """Replace text inside Lean comments with spaces (preserving line
    numbers and column positions). Handles single-line `--` comments,
    block comments `/- ... -/`, and docstring blocks `/-- ... -/`.

    The Lean spec allows `/-` blocks to nest, but for the purposes of
    avoiding `@[simp]` false positives a single-level scanner is
    sufficient since the corpus does not nest comments inside docstrings.
    """
    out: list[str] = []
    in_block = False
    for raw in lines:
        chars = list(raw)
        i = 0
        n = len(chars)
        while i < n:
            if in_block:
                if i + 1 < n and chars[i] == '-' and chars[i + 1] == '/':
                    chars[i] = ' '
                    chars[i + 1] = ' '
                    in_block = False
                    i += 2
                    continue
                chars[i] = ' '
                i += 1
                continue
            # Single-line comment: rest of line becomes whitespace
            if i + 1 < n and chars[i] == '-' and chars[i + 1] == '-':
                for j in range(i, n):
                    chars[j] = ' '
                break
            # Start of block / docstring
            if i + 1 < n and chars[i] == '/' and chars[i + 1] == '-':
                in_block = True
                chars[i] = ' '
                chars[i + 1] = ' '
                i += 2
                continue
            i += 1
        out.append(''.join(chars))
    return out


def find_simp_loops(text: str, theorem_blocks: list[dict]) -> list[dict]:
    """Detect `@[simp]` rewrite rules whose LHS head symbol re-appears in
    the RHS — a classic source of simp-set non-termination (W9 HITL B-1).

    Heuristic:
    1. Scan source for any `@[...simp...]` attribute marker (handles
       priorities, bundled attributes, pre/post arrows, and `@[simp ←]`).
    2. Pair each marker with the next theorem/lemma block on the same or
       a nearby (≤ 5 lines away) following line.
    3. Extract the conclusion of that block, split on the first top-level
       `=` or `↔`, identify the LHS head symbol, then check whether the
       same head symbol appears as a whole word in the RHS.

    The check is intentionally conservative — it only flags when the LHS
    head IS a real Lean identifier (alphabetic/underscore initial) and is
    distinct from the theorem name itself. Manual review is required for
    any hit.
    """
    findings: list[dict] = []
    lines = text.splitlines()

    # Strip Lean comments before scanning so docstrings that mention
    # `@[simp]` literally (e.g., in a "this is NOT @[simp]" note) don't
    # trigger false positives. We replace docstring/comment characters
    # with spaces (preserving line numbers and column positions).
    stripped_lines = _strip_lean_comments(lines)

    # Step 1: collect every `@[simp]`-bearing attribute line
    simp_marker_re = re.compile(r'@\[\s*([^\]]*)\]')
    simp_lines: list[tuple[int, str, str]] = []  # (1-based line, attr text, raw line)
    for idx, line in enumerate(stripped_lines, start=1):
        for m in simp_marker_re.finditer(line):
            attr = m.group(1)
            tokens = [t.strip() for t in attr.split(',') if t.strip()]
            head_tokens = [t.split()[0] if t.split() else '' for t in tokens]
            if 'simp' in head_tokens:
                simp_lines.append((idx, attr, line))
                break  # one simp annotation per line is enough

    # Step 2: pair each simp marker with a theorem/lemma block
    by_start_line = {thm['line']: thm for thm in theorem_blocks}
    for attr_line, attr_text, attr_raw in simp_lines:
        target_thm = None

        # Same-line attribute: `@[simp] theorem foo : ...`
        # If a theorem keyword is already on this line, we ONLY accept the
        # match coming from `by_start_line[attr_line]`. Falling through to
        # the look-ahead would incorrectly bind this attribute to the next
        # theorem. (Bug fix surfaced by W9 HITL B-1 false positives.)
        same_line_thm = bool(re.search(r'(?:theorem|lemma)\s+\S+', attr_raw))
        if same_line_thm:
            target_thm = by_start_line.get(attr_line)
            if target_thm is None:
                continue  # parser missed this theorem; skip rather than misattribute

        # Otherwise look ahead a few lines for the next theorem block
        if target_thm is None:
            candidates = [t for t in theorem_blocks if t['line'] > attr_line]
            if candidates:
                nearest = min(candidates, key=lambda t: t['line'])
                if nearest['line'] - attr_line <= 5:
                    target_thm = nearest

        if target_thm is None:
            continue

        loop_detail = check_simp_lhs_in_rhs(target_thm['signature'],
                                            target_thm['name'])
        if loop_detail:
            findings.append({
                'type': 'simp-loop-risk',
                'severity': 'P1',
                'theorem': target_thm['name'],
                'line': target_thm['line'],
                'detail': loop_detail,
            })

    return findings


def find_heartbeat_overrides(text: str, filepath: Path) -> list[dict]:
    """Detect `set_option maxHeartbeats N` (or `synthInstance.maxHeartbeats`)
    overrides that exceed sane review thresholds.

    Returns one finding per offending occurrence. The line number is the
    1-based line of the override in the file.

    Severity rules (W10 r27):
      * `maxHeartbeats N`, N > 1_000_000  → P1 (heartbeat-budget-excessive)
      * `maxHeartbeats 0`                  → P1 (heartbeat-budget-disabled)
      * `maxHeartbeats N`, 200_000 < N ≤ 1_000_000 → P2 (heartbeat-budget-elevated)

    `set_option maxHeartbeats N` *inside* a `set_option ... in` clause is
    detected the same way (the regex matches the option name and number).
    """
    findings = []
    pattern = re.compile(
        r'^\s*set_option\s+'
        r'(?P<opt>(?:synthInstance\.)?maxHeartbeats)\s+'
        r'(?P<n>\d+)\b'
    )
    for idx, line in enumerate(text.splitlines(), start=1):
        m = pattern.match(line)
        if not m:
            continue
        n = int(m.group('n'))
        opt = m.group('opt')
        if n == 0:
            findings.append({
                'type': 'heartbeat-budget-disabled',
                'severity': 'P1',
                'theorem': '(file-level)',
                'line': idx,
                'detail': (
                    f'`set_option {opt} 0` disables the elaborator safety net '
                    f'in {filepath.name}; never ship 0'
                ),
            })
        elif n > 1_000_000:
            findings.append({
                'type': 'heartbeat-budget-excessive',
                'severity': 'P1',
                'theorem': '(file-level)',
                'line': idx,
                'detail': (
                    f'`set_option {opt} {n}` exceeds 1_000_000 in '
                    f'{filepath.name}; almost always indicates a perf '
                    f'regression that should be tracked'
                ),
            })
        elif n > 200_000:
            findings.append({
                'type': 'heartbeat-budget-elevated',
                'severity': 'P2',
                'theorem': '(file-level)',
                'line': idx,
                'detail': (
                    f'`set_option {opt} {n}` is above the 200_000 default in '
                    f'{filepath.name}; consider proof split or term-mode hint'
                ),
            })
    return findings


def check_simp_lhs_in_rhs(signature: str, theorem_name: str) -> str | None:
    """Return a description if the LHS head symbol of the conclusion
    appears in the RHS, signalling a possible simp loop. Otherwise None.
    """
    conclusion = _extract_conclusion(signature)
    if not conclusion:
        return None

    eq = _find_top_level_eq(conclusion)
    if eq is None:
        return None
    idx, op = eq
    lhs = conclusion[:idx].strip()
    rhs = conclusion[idx + len(op):].strip()
    if not lhs or not rhs:
        return None

    head = _extract_head_symbol(lhs)
    if not head:
        return None
    # Skip if head is the theorem name itself — circular by construction
    if head == theorem_name:
        return None
    # Skip operator-shaped heads (e.g. `=`, `+`, `≤`)
    if not re.match(r'^[A-Za-z_]', head):
        return None
    # Skip common Lean keywords that may appear at LHS head accidentally
    KEYWORDS = {'fun', 'if', 'then', 'else', 'let', 'match', 'with', 'do'}
    if head in KEYWORDS:
        return None
    # Skip if head is a bound variable from the theorem signature.
    # Bound variables are introduced by `(name : ...)`, `{name : ...}`,
    # `[name : ...]` or `⦃name : ...⦄` binders; using one of them as
    # head is not a function-symbol rewrite, so simp cannot loop.
    if head in _bound_variable_names(signature):
        return None

    if re.search(r'(?<![A-Za-z0-9_])' + re.escape(head) + r'(?![A-Za-z0-9_])',
                 rhs):
        return (f"@[simp] LHS head `{head}` appears in RHS — potential "
                f"rewrite loop")
    return None


def _bound_variable_names(signature: str) -> set[str]:
    """Collect identifier names introduced by binders in the signature.
    Handles `(x y z : T)`, `{x : T}`, `[inst : T]`, and `⦃a : T⦄` forms.
    """
    names: set[str] = set()
    # Match each binder group; capture the variable list before the colon.
    binder_re = re.compile(r'[\(\{\[⦃]\s*([^\):\}\]⦄]+?)\s*:\s*[^\)\}\]⦄]+[\)\}\]⦄]')
    for m in binder_re.finditer(signature):
        for tok in m.group(1).split():
            if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok):
                names.add(tok)
    return names


def _extract_conclusion(signature: str) -> str:
    """Strip the leading `theorem foo` / `lemma foo` and binders, returning
    the conclusion type (the text after the first depth-0 `:` that isn't
    `:=`).
    """
    sig = signature
    m = re.match(
        r'^\s*(?:theorem|lemma|private\s+theorem|private\s+lemma)\s+\S+',
        sig)
    if m:
        sig = sig[m.end():]

    depth = 0
    in_string = False
    i = 0
    colon_pos = -1
    while i < len(sig):
        c = sig[i]
        if c == '"':
            in_string = not in_string
            i += 1
            continue
        if in_string:
            i += 1
            continue
        if c in '([{⟨':
            depth += 1
        elif c in ')]}⟩':
            depth -= 1
        elif c == ':' and depth == 0:
            if i + 1 < len(sig) and sig[i + 1] == '=':
                break  # `:=` ends the signature without a colon-typed conclusion
            colon_pos = i
            break
        i += 1

    if colon_pos < 0:
        return ''
    conclusion = sig[colon_pos + 1:]
    # Strip trailing `:= ...` or `:= by ...` if signature included it
    conclusion = re.sub(r':=.*$', '', conclusion, flags=re.DOTALL)
    return conclusion.strip()


def _find_top_level_eq(text: str) -> tuple[int, str] | None:
    """Locate the leftmost depth-0 `=` (not part of `:=`, `==`, `≤`, `≥`,
    `≠`, etc.) or `↔` in the text. Returns (index, operator) or None.
    """
    depth = 0
    in_string = False
    i = 0
    while i < len(text):
        c = text[i]
        if c == '"':
            in_string = not in_string
            i += 1
            continue
        if in_string:
            i += 1
            continue
        if c in '([{⟨':
            depth += 1
            i += 1
            continue
        if c in ')]}⟩':
            depth -= 1
            i += 1
            continue
        if depth != 0:
            i += 1
            continue
        if text[i:i + 1] == '↔':
            return (i, '↔')
        if c == '=':
            prev = text[i - 1] if i > 0 else ''
            nxt = text[i + 1] if i + 1 < len(text) else ''
            if prev in ':=<>!≤≥≠≡↔':
                i += 1
                continue
            if nxt == '=':
                i += 2
                continue
            return (i, '=')
        i += 1
    return None


def _extract_head_symbol(lhs: str) -> str | None:
    """Pull the leftmost non-paren identifier from a LHS expression."""
    s = lhs.strip()
    # Strip outer parens that wrap the whole expression
    while s.startswith('(') and s.endswith(')'):
        depth = 0
        balanced = True
        for j, c in enumerate(s):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0 and j < len(s) - 1:
                    balanced = False
                    break
        if balanced:
            s = s[1:-1].strip()
        else:
            break

    # First token (split on whitespace or dot, keeping namespaced heads)
    tok = re.split(r'[\s(){}\[\],]', s, maxsplit=1)[0]
    # Drop a `.` suffix used by dot notation like `Foo.bar baz`
    if '.' in tok:
        tok = tok.split('.')[-1]
    if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", tok):
        return tok
    return None


def generate_report(results: list[dict], output: Path) -> None:
    """Generate Markdown quality report."""
    all_findings = []
    all_stats = []
    for r in results:
        all_findings.extend(r['findings'])
        all_stats.append(r['stats'])

    total_thms = sum(s['theorem_count'] for s in all_stats)
    global_tactics = Counter()
    for s in all_stats:
        global_tactics += s['tactic_usage']

    lines = [
        '# Proof Quality Analysis',
        '',
        f'## Summary',
        f'- **Modules analyzed:** {len(all_stats)}',
        f'- **Theorems analyzed:** {total_thms}',
        f'- **Total findings:** {len(all_findings)}',
        f'- **P1 (important):** {sum(1 for f in all_findings if f["severity"] == "P1")}',
        f'- **P2 (improvement):** {sum(1 for f in all_findings if f["severity"] == "P2")}',
        f'- **P3 (style):** {sum(1 for f in all_findings if f["severity"] == "P3")}',
        '',
        '## Tactic Usage (Global)',
        '',
        '| Tactic | Count | % |',
        '|---|---|---|',
    ]

    total_tactic_count = sum(global_tactics.values())
    for tactic, count in global_tactics.most_common(15):
        pct = count / total_tactic_count * 100 if total_tactic_count > 0 else 0
        lines.append(f'| {tactic} | {count} | {pct:.1f}% |')

    if all_findings:
        lines.extend([
            '',
            '## Findings',
            '',
            '| Severity | Module | Theorem | Type | Detail |',
            '|---|---|---|---|---|',
        ])
        for f in sorted(all_findings, key=lambda x: (x['severity'], x['theorem'])):
            module = f['theorem'].split('.')[0] if '.' in f['theorem'] else '—'
            lines.append(
                f"| {f['severity']} | — | {f['theorem']} | {f['type']} | {f['detail']} |"
            )

    lines.extend([
        '',
        '---',
        '*Generated by proof_quality.py*',
    ])

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Proof quality analysis')
    parser.add_argument('--lean-dir', type=Path, default=Path('MyProject'),
                        help='Directory containing .lean files')
    parser.add_argument('--output', type=Path, default=Path('proof_quality.md'),
                        help='Output report path')
    args = parser.parse_args()

    results = []
    for f in sorted(args.lean_dir.rglob('*.lean')):
        rel = f.relative_to(args.lean_dir)
        print(f"Analyzing {rel}...")
        result = analyze_module(f)
        results.append(result)
        findings = result['findings']
        if findings:
            print(f"  {len(findings)} finding(s)")

    generate_report(results, args.output)
    total = sum(len(r['findings']) for r in results)
    print(f"\nTotal findings: {total}")
    print(f"Report: {args.output}")

    # Exit with error if P1 issues found
    p1_count = sum(1 for r in results for f in r['findings'] if f['severity'] == 'P1')
    if p1_count > 0:
        print(f"\n{p1_count} P1 issue(s) found")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
