#!/usr/bin/env python3
"""Reference solutions + hidden test suites for the coding battery.

Verify all references pass all tests before sending prompts to models.
"""
from __future__ import annotations

# ---------- P1: count_inversions ----------
def ref_count_inversions(arr):
    n = len(arr); c = 0
    for i in range(n):
        for j in range(i+1, n):
            if arr[i] > arr[j]:
                c += 1
    return c

TESTS_P1 = [
    ([], 0),
    ([1], 0),
    ([3,2,1], 3),
    ([1,2,3,4,5], 0),
    ([5,4,3,2,1], 10),
    ([1,3,2,5,4], 2),
    ([2,4,1,3,5], 3),
    ([10,9,8,7,6,5,4,3,2,1], 45),
    ([1,1,1], 0),
    ([2,1,2,1], 3),
]

# ---------- P2: is_balanced ----------
def ref_is_balanced(s):
    stk = []
    pairs = {')':'(', ']':'[', '}':'{'}
    openers = set("([{")
    closers = set(")]}")
    for ch in s:
        if ch in openers:
            stk.append(ch)
        elif ch in closers:
            if not stk or stk[-1] != pairs[ch]:
                return False
            stk.pop()
    return not stk

TESTS_P2 = [
    ("", True),
    ("()", True),
    ("([])", True),
    ("([)]", False),
    ("abc(def)ghi", True),
    ("(", False),
    (")", False),
    ("{[()]}", True),
    ("{[(])}", False),
    ("(){}[]", True),
]

# ---------- P3: longest_palindrome_subseq ----------
def ref_lps(s):
    n = len(s)
    if n == 0: return 0
    dp = [[0]*n for _ in range(n)]
    for i in range(n): dp[i][i] = 1
    for L in range(2, n+1):
        for i in range(n-L+1):
            j = i+L-1
            if s[i] == s[j]:
                dp[i][j] = (dp[i+1][j-1] if L > 2 else 0) + 2
            else:
                dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    return dp[0][n-1]

TESTS_P3 = [
    ("", 0),
    ("a", 1),
    ("bbbab", 4),
    ("cbbd", 2),
    ("abcba", 5),
    ("abcdef", 1),
    ("agbdba", 5),
    ("racecar", 7),
    ("level", 5),
    ("abcde", 1),
]

# ---------- P4: fizzbuzz_count(n): count k in 1..n where (k%3==0) XOR (k%5==0) ----------
def ref_fb(n):
    return sum(1 for k in range(1, n+1) if (k%3==0) ^ (k%5==0))

TESTS_P4 = [
    (0, 0),
    (1, 0),
    (3, 1),
    (5, 2),
    (14, 6),
    (15, 6),
    (100, 41),
    (1000, 401),
    (10000, 4001),
    (33, 13),
]

# ---------- P5: min_jumps ----------
def ref_min_jumps(arr):
    n = len(arr)
    if n <= 1: return 0
    if arr[0] == 0: return -1
    jumps = 0; cur_end = 0; farthest = 0
    for i in range(n-1):
        if arr[i] == 0 and i == cur_end:
            return -1
        farthest = max(farthest, i + arr[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
            if cur_end >= n-1: return jumps
    return jumps if cur_end >= n-1 else -1

TESTS_P5 = [
    ([0], 0),
    ([2,3,1,1,4], 2),
    ([1,1,1,1], 3),
    ([3,2,1,0,4], -1),
    ([1,0], 1),
    ([5,1,1,1,1,1], 1),
    ([2,1,0,4], -1),
    ([1,2,3], 2),
    ([10,1,1], 1),
    ([2,1,1,1,4], 3),
]

PROBLEMS = {
    "P1": ("count_inversions", ref_count_inversions, TESTS_P1),
    "P2": ("is_balanced",       ref_is_balanced,     TESTS_P2),
    "P3": ("longest_palindrome_subseq", ref_lps,     TESTS_P3),
    "P4": ("fizzbuzz_count",    ref_fb,              TESTS_P4),
    "P5": ("min_jumps",         ref_min_jumps,       TESTS_P5),
}

def verify_ref():
    for pid, (fname, fn, tests) in PROBLEMS.items():
        for i, (inp, exp) in enumerate(tests):
            got = fn(inp) if not isinstance(inp, tuple) else fn(*inp)
            assert got == exp, f"{pid}/{fname} t{i}: inp={inp} exp={exp} got={got}"
        print(f"{pid} {fname}: {len(tests)}/{len(tests)} ✓")

if __name__ == "__main__":
    verify_ref()
