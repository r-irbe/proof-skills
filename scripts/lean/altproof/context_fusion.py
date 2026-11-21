"""Typed list/branch-context e-graph trace replay with eta contraction and context fusion.

Ported from kernel egraph-successors-2026-11-18/list-context-fusion/eta_bridge.py.
Reconstructs kernel-checked Lean 4 congruence & branch-guard proofs from
rewrite traces without inventing unprovided branch or sortedness hypotheses.

Scoped Unicode policy (INV-001; typographic-free by default).
"""

from __future__ import annotations

import re

OPS = {
    "+": ("Nat", "Nat", "Nat"),
    "*": ("Nat", "Nat", "Nat"),
    "-": ("Nat", "Nat", "Nat"),
    "le": ("Bool", "Nat", "Nat"),
    "if": ("Nat", "Bool", "Nat", "Nat"),
    "cons": ("ListNat", "Nat", "ListNat"),
    "oldPhi": ("Nat", "ListNat", "Nat"),
    "prefix": ("Nat", "ListNat", "Nat"),
    "wheel": ("Nat", "Nat"),
    "/": ("Nat", "Nat", "Nat"),
}
PATTERNS = {"small-run"}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def sort(term) -> str:
    if term[0] in {"nil", "lvar"}:
        return "ListNat"
    if term[0] in {"nat", "nvar"}:
        return "Nat"
    if term[0] in {"bool", "bvar"}:
        return "Bool"
    signature = OPS[term[0]]
    require(tuple(sort(arg) for arg in term[1:]) == signature[1:], "Sort mismatch")
    return signature[0]


def parse_trace(text: str, nvars: int, bvars: int, lvars: int):
    require(type(text) is str and 0 < len(text) <= 65536, "Invalid trace size")
    require(
        type(nvars) is int
        and type(bvars) is int
        and type(lvars) is int
        and 0 <= nvars <= 16
        and 0 <= bvars <= 16
        and 0 <= lvars <= 16,
        "Invalid scope",
    )
    tokens = re.findall(r"[()]|[^()\s]+", text)
    require(len(tokens) <= 4096, "Token limit exceeded")
    cursor = 0

    def read(depth: int):
        nonlocal cursor
        require(depth <= 32 and cursor < len(tokens), "Depth/truncation error")
        token = tokens[cursor]
        cursor += 1
        require(token != ")", "Unexpected closing parenthesis")
        if token != "(":
            return token
        children = []
        while cursor < len(tokens) and tokens[cursor] != ")":
            children.append(read(depth + 1))
        require(cursor < len(tokens), "Unclosed parenthesis")
        cursor += 1
        return children

    def decode(node, path=()):
        if type(node) is str:
            if node == "nil":
                return ("nil",), []
            if node in {"true", "false"}:
                return ("bool", node), []
            if re.fullmatch(r"[xbl](?:0|[1-9][0-9]*)", node):
                limit = {"x": nvars, "b": bvars, "l": lvars}[node[0]]
                require(len(node) <= 3 and int(node[1:]) < limit, "Variable outside scope")
                kind = {"x": "nvar", "b": "bvar", "l": "lvar"}[node[0]]
                return (kind, int(node[1:])), []
            require(
                re.fullmatch(r"0|[1-9][0-9]*", node) is not None and len(node) <= 1234,
                "Invalid atom",
            )
            value = int(node)
            require(value.bit_length() <= 4096, "Literal too large")
            return ("nat", value), []
        require(type(node) is list and len(node) > 0 and type(node[0]) is str, "Malformed term")
        if node[0] in {"Rewrite=>", "Rewrite<="}:
            require(len(node) == 3 and type(node[1]) is str and node[1] in PATTERNS, "Unknown rule")
            term, marks = decode(node[2], path)
            return term, [(path, node[0], node[1]), *marks]
        require(node[0] in OPS and len(node) == len(OPS[node[0]]), "Unknown operator/arity")
        children = [decode(child, (*path, idx)) for idx, child in enumerate(node[1:])]
        term = (node[0], *(child[0] for child in children))
        sort(term)
        return term, [mark for child in children for mark in child[1]]

    forms = []
    while cursor < len(tokens):
        forms.append(decode(read(0)))
        require(len(forms) <= 65, "Too many trace terms")
    return forms


def render(term) -> str:
    head = term[0]
    if head == "nil":
        return "(List.nil : List Nat)"
    if head == "lvar":
        return f"_l{term[1]}"
    if head == "hole":
        return "hole"
    if head == "nat":
        return str(term[1])
    if head == "bool":
        return term[1]
    if head in {"nvar", "bvar"}:
        return f'_{"x" if head == "nvar" else "b"}{term[1]}'
    args = " ".join(render(arg) for arg in term[1:])
    name = {
        "+": "Nat.add",
        "*": "Nat.mul",
        "-": "Nat.sub",
        "le": "Nat.ble",
        "if": "ListRules.choose",
        "cons": "List.cons",
        "oldPhi": "Submission.phiW3RunBase",
        "prefix": "Submission.smallRunCount",
        "wheel": "Submission.phiW3Base",
        "/": "Nat.div",
    }[head]
    return f"({name} {args})"


def selected(term, path):
    for idx in path:
        require(term[0] in OPS and 0 <= idx < len(term) - 1, "Invalid context path")
        term = term[idx + 1]
    return term


def replace(term, path, value):
    if not path:
        return value
    require(term[0] in OPS and 0 <= path[0] < len(term) - 1, "Invalid context path")
    args = list(term[1:])
    args[path[0]] = replace(args[path[0]], path[1:], value)
    return (term[0], *args)


def render_trace(
    text: str,
    nvars: int,
    bvars: int,
    lvars: int,
    guards: list,
    eta: bool = False,
    *,
    fuse: bool = False,
):
    """Render a Lean 4 proof replay script from a typed rewrite trace and explicit/branch guards."""
    require(type(eta) is bool, "Invalid eta mode")
    require(type(fuse) is bool, "Invalid fuse mode")
    eta_lifts = []
    forms = parse_trace(text, nvars, bvars, lvars)
    require(len(forms) >= 2 and not forms[0][1] and sort(forms[0][0]) == "Nat", "Invalid start")
    require(type(guards) is list and len(guards) <= 16, "Invalid guard list")
    parsed = []
    for guard in guards:
        require(
            type(guard) is dict
            and len(guard) == 1
            and next(iter(guard)) in {"sorted", "false"},
            "Invalid guard kind",
        )
        kind, value = next(iter(guard.items()))
        decoded = parse_trace(value, nvars, bvars, lvars)
        require(len(decoded) == 1 and not decoded[0][1], "Invalid guard expression")
        term = decoded[0][0]
        require(sort(term) == ("ListNat" if kind == "sorted" else "Bool"), "Guard sort mismatch")
        item = (kind, term)
        require(item not in parsed, "Duplicate guard")
        parsed.append(item)

    binders = (
        [f"(_x{i} : Nat)" for i in range(nvars)]
        + [f"(_b{i} : Bool)" for i in range(bvars)]
        + [f"(_l{i} : List Nat)" for i in range(lvars)]
    )
    for i, (kind, term) in enumerate(parsed):
        ty = (
            f"({render(term)}).Pairwise (fun a b : Nat => a < b)"
            if kind == "sorted"
            else f"{render(term)} = false"
        )
        binders.append(f"(_h{i} : {ty})")
    params = " ".join(binders)
    args = " ".join(
        [f"_x{i}" for i in range(nvars)]
        + [f"_b{i}" for i in range(bvars)]
        + [f"_l{i}" for i in range(lvars)]
        + [f"_h{i}" for i in range(len(parsed))]
    )
    first = previous = forms[0][0]
    source = ["import ListRules", "open Submission"]
    records = []

    for index, (current, marks) in enumerate(forms[1:]):
        require(sort(current) == "Nat" and len(marks) == 1, "Exactly one Nat rewrite required")
        path, direction, reason = marks[0]
        require(len(path) <= 16 and reason == "small-run", "Invalid rewrite")
        old, new = selected(previous, path), selected(current, path)
        require(sort(old) == sort(new) == "Nat", "Rewrite sort mismatch")
        require(replace(previous, path, new) == current, "Context changed outside rewrite")
        lhs, rhs = (old, new) if direction == "Rewrite=>" else (new, old)
        require(lhs[0] == "oldPhi" and lhs[1][0] == "cons", "Rule shape mismatch")
        lst, x = lhs[1:]
        p, ps = lst[1:]
        expected = ("-", ("wheel", x), ("prefix", lst, x))
        require(rhs == expected, "Rule endpoint mismatch")
        sorted_fact = ("sorted", lst)
        require(sorted_fact in parsed, "Missing exact sorted-list guard")
        sorted_index = parsed.index(sorted_fact)
        threshold = ("le", ("*", ("nat", 7), p), x)
        used = {}

        def lift(a, c, remaining, facts, depth):
            if not remaining:
                global_fact = ("false", threshold)
                if global_fact in parsed:
                    idx = parsed.index(global_fact)
                    false_proof = f"_h{idx}"
                    used.update(provider="explicit", guard_index=idx)
                else:
                    available = [f for f in facts if f[0] == threshold and f[1] is False]
                    require(available, "Missing exact false threshold guard")
                    false_proof = available[-1][2]
                    used.update(provider="branch-context", binder=false_proof)
                proof = (
                    f"ListRules.collapse {render(p)} {render(x)} {render(ps)} "
                    f"_h{sorted_index} {false_proof}"
                )
                return proof if direction == "Rewrite=>" else f"Eq.symm ({proof})"
            i = remaining[0]
            if a[0] == "if" and i in [1, 2]:
                condition = a[1]
                local = f"_c{depth}"
                child = lift(
                    a[i + 1],
                    c[i + 1],
                    remaining[1:],
                    facts + [(condition, i == 1, local)],
                    depth + 1,
                )
                if i == 1:
                    return (
                        f"ListRules.choose_true {render(condition)} {render(a[2])} "
                        f"{render(c[2])} {render(a[3])} (fun {local} => {child})"
                    )
                return (
                    f"ListRules.choose_false {render(condition)} {render(a[2])} "
                    f"{render(a[3])} {render(c[3])} (fun {local} => {child})"
                )
            if fuse:
                boundary = 0
                focus = a
                for edge in remaining:
                    if focus[0] == "if" and edge in (1, 2):
                        break
                    focus = focus[edge + 1]
                    boundary += 1
                if boundary > 1:
                    segment = remaining[:boundary]
                    child = lift(
                        focus,
                        selected(c, segment),
                        remaining[boundary:],
                        facts,
                        depth + boundary,
                    )
                    body = render(replace(a, segment, ("hole",)))
                    ty = {"Nat": "Nat", "Bool": "Bool", "ListNat": "List Nat"}[sort(focus)]
                    return f"congrArg (fun hole : {ty} => {body}) ({child})"
            child = lift(a[i + 1], c[i + 1], remaining[1:], facts, depth + 1)
            if eta and i == len(a) - 2:
                function = render((a[0], *a[1:-1]))
                function = function[:-1].rstrip() + ")"
                eta_lifts.append(
                    {
                        "step": index,
                        "depth": depth,
                        "operator": a[0],
                        "position": i,
                        "argument_sort": sort(a[i + 1]),
                    }
                )
                return f"congrArg {function} ({child})"
            context = list(a[1:])
            context[i] = ("hole",)
            body = render((a[0], *context))
            ty = {"Nat": "Nat", "Bool": "Bool", "ListNat": "List Nat"}[sort(a[i + 1])]
            return f"congrArg (fun hole : {ty} => {body}) ({child})"

        proof = lift(previous, current, path, [], 0)
        source += [
            f"theorem merge_{index} {params} : {render(previous)} = {render(current)} := {proof}",
            f"#print axioms merge_{index}",
        ]
        records.append(
            {
                "rule": reason,
                "direction": direction,
                "path": list(path),
                "sorted_guard_index": sorted_index,
                "false_guard": used,
                "end": current,
            }
        )
        previous = current

    source.append(f"theorem replay {params} : {render(first)} = {render(previous)} := by\n  calc")
    for idx, rec in enumerate(records):
        lhs_str = render(first) if idx == 0 else "_"
        source.append(f"    {lhs_str} = {render(rec['end'])} := merge_{idx} {args}")
    source.append("#print axioms replay")
    meta = {"guards": guards, "steps": records, "start": first, "end": previous}
    if eta:
        meta["eta_lifts"] = eta_lifts
    return "\n".join(source) + "\n", meta
