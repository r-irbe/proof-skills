#!/usr/bin/env python3
"""Build a Lean file per (model, problem) and run `lake build` to grade."""
import subprocess, json, re
from pathlib import Path

PROBLEMS = {
    "T1": "theorem t1 (a b c : Nat) : a + b + c = c + b + a := {proof}",
    "T2": "theorem t2 (n : Nat) : 2 * n = n + n := {proof}",
    "T3": "theorem t3 {{α : Type _}} (l : List α) : l.reverse.reverse = l := {proof}",
    "T4": "theorem t4 (a b : Nat) (h : a ≤ b) : a + 1 ≤ b + 1 := {proof}",
    "T5": "theorem t5 (n : Nat) (h : 0 < n) : ∃ m, n = m + 1 := {proof}",
}

MODELS = {
    "opus47high": "claude-opus-4.7-high",
    "opus47":     "claude-opus-4.7",
    "sonnet46":   "claude-sonnet-4.6",
    "gpt54":      "gpt-5.4",
    "haiku45":    "claude-haiku-4.5",
}

HERE = Path(__file__).resolve().parent
ROOT = HERE
BENCH = ROOT / "Bench"
RESP = ROOT / "responses"

def split_response(text):
    out = {}
    parts = re.split(r"^===\s*T(\d+)\s*===\s*$", text, flags=re.MULTILINE)
    for i in range(1, len(parts), 2):
        out[f"T{parts[i]}"] = parts[i+1].strip()
    return out

def write_files():
    for short, full in MODELS.items():
        text = (RESP / f"{full}.txt").read_text()
        chunks = split_response(text)
        mdir = BENCH / short
        mdir.mkdir(parents=True, exist_ok=True)
        for pid, tmpl in PROBLEMS.items():
            proof = chunks.get(pid, "sorry")
            # Indent multi-line proofs for substitution after `:=`
            if "\n" in proof:
                proof_body = "\n  " + proof.replace("\n", "\n  ")
            else:
                proof_body = " " + proof
            content = tmpl.format(proof=proof_body) + "\n"
            (mdir / f"{pid}.lean").write_text(content)

def build_one(short, pid):
    target = f"Bench.{short}.{pid}"
    r = subprocess.run(["lake", "build", target], cwd=ROOT,
                       capture_output=True, text=True, timeout=60)
    ok = (r.returncode == 0) and ("error" not in r.stdout.lower() + r.stderr.lower() or "0 errors" in (r.stdout + r.stderr).lower())
    # Tighter: just rely on returncode
    ok = (r.returncode == 0)
    return ok, (r.stdout + "\n" + r.stderr).strip()[-600:]

def main():
    write_files()
    scores = {}
    print(f"\n{'model':14s} " + " ".join(f"{p:>5s}" for p in PROBLEMS) + "   total")
    print("-" * 60)
    detail = {}
    for short, full in MODELS.items():
        row = {}
        for pid in PROBLEMS:
            ok, log = build_one(short, pid)
            row[pid] = {"ok": ok, "log": log if not ok else ""}
        scores[full] = row
        cells = [" 1   " if row[p]["ok"] else " 0   " for p in PROBLEMS]
        total = sum(1 for p in PROBLEMS if row[p]["ok"])
        print(f"{short:14s} " + " ".join(cells) + f"   {total}/5")
        detail[full] = row
    Path(HERE / "scores.json").write_text(json.dumps(detail, indent=2))
    print("\nFailures:")
    for full, row in detail.items():
        for pid in PROBLEMS:
            if not row[pid]["ok"]:
                # Compress: last 300 chars
                err = row[pid]["log"][-300:]
                print(f"  {full} {pid}:")
                for line in err.split("\n"):
                    if "error" in line.lower():
                        print(f"     {line.strip()}")

if __name__ == "__main__":
    main()
