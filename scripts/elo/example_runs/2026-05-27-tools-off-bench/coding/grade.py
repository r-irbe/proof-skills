#!/usr/bin/env python3
"""Grade the 5 model responses for the coding benchmark."""
from __future__ import annotations
import re, json
from pathlib import Path
import importlib.util
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tests", str(HERE / "tests.py"))
tests_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(tests_mod)
PROBLEMS = tests_mod.PROBLEMS

MODELS = [
    "claude-opus-4.7-high",
    "claude-opus-4.7",
    "claude-sonnet-4.6",
    "gpt-5.4",
    "claude-haiku-4.5",
]

def split_response(text):
    """Return dict {Pn: source_code}."""
    out = {}
    parts = re.split(r"^===\s*P(\d+)\s*===\s*$", text, flags=re.MULTILINE)
    # parts: ['preamble', '1', 'code1', '2', 'code2', ...]
    for i in range(1, len(parts), 2):
        pid = f"P{parts[i]}"
        code = parts[i+1]
        code = re.sub(r"```(?:python)?\s*", "", code)
        code = re.sub(r"```\s*", "", code)
        out[pid] = code.strip()
    return out

def grade_model(name, response_text):
    chunks = split_response(response_text)
    per_problem = {}
    for pid, (fname, _ref, tests) in PROBLEMS.items():
        code = chunks.get(pid, "")
        if not code:
            per_problem[pid] = {"pass": 0, "total": len(tests), "err": "no-chunk"}
            continue
        ns = {}
        try:
            exec(code, ns)
            fn = ns.get(fname)
            if fn is None:
                per_problem[pid] = {"pass": 0, "total": len(tests), "err": f"missing-fn:{fname}"}
                continue
            passes = 0; first_fail = None
            for i, (inp, exp) in enumerate(tests):
                try:
                    got = fn(inp) if not isinstance(inp, tuple) else fn(*inp)
                    if got == exp:
                        passes += 1
                    elif first_fail is None:
                        first_fail = f"t{i}:inp={inp!r} exp={exp!r} got={got!r}"
                except Exception as e:
                    if first_fail is None:
                        first_fail = f"t{i}:raised {type(e).__name__}:{e}"
            per_problem[pid] = {"pass": passes, "total": len(tests), "err": first_fail}
        except Exception as e:
            per_problem[pid] = {"pass": 0, "total": len(tests), "err": f"exec:{type(e).__name__}:{e}"}
    return per_problem


def main():
    raw_dir = HERE / "responses"
    results = {}
    for m in MODELS:
        text = (raw_dir / f"{m}.txt").read_text()
        results[m] = grade_model(m, text)
    # print scoreboard
    print(f"\n{'model':30s} " + " ".join(f"{p:>7s}" for p in PROBLEMS) + "   total")
    print("-" * 80)
    for m in MODELS:
        cells = []
        total = 0
        for p in PROBLEMS:
            r = results[m][p]
            cells.append(f"{r['pass']:>2d}/{r['total']:<2d} ")
            total += r["pass"]
        print(f"{m:30s} " + " ".join(cells) + f"   {total:>3d}/50")
    # err report
    print("\nFirst-fail by (model, problem):")
    for m in MODELS:
        for p in PROBLEMS:
            r = results[m][p]
            if r["err"]:
                print(f"  {m} {p}: {r['err']}")
    Path(HERE / "scores.json").write_text(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
