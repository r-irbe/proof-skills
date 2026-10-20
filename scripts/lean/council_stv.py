#!/usr/bin/env python3
"""Deterministic STV counter for the alt-proof council ballots.

Charter: docs/investigation-garden/altproof/COUNCIL_CHARTER.md (STV
mechanics).  Single-winner STV with whole-ballot transfer, the
majority quota floor(n_valid / 2) + 1, and a documented deterministic
tiebreak (fewest first preferences, then lexicographically smallest
option id).  Abstentions (empty rankings) are invalid and only shrink
the quota base.  Exhausted ballots are set aside for the round; if
every remaining option is eliminated and no option ever met the
quota, the last surviving option wins with a NO_QUORUM flag (recorded
in the minutes; the caller decides reject/default semantics).

Stdlib only; no I/O in the counting core (the CLI is a thin wrapper).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field


@dataclass
class Ballot:
    voter: str
    ranking: list[str] = field(default_factory=list)


def count_stv(options: list[str], ballots: list[Ballot]) -> dict:
    """Count one single-winner STV ballot.  Returns the minutes dict."""
    valid = [b for b in ballots if b.ranking]
    quota = len(valid) // 2 + 1 if valid else 0
    remaining = list(options)
    active = list(valid)
    rounds: list[dict] = []

    while True:
        tally = dict.fromkeys(remaining, 0)
        for b in active:
            top = next((o for o in b.ranking if o in tally), None)
            if top is not None:
                tally[top] += 1
        leader, lead_votes = max(tally.items(), key=lambda kv: (kv[1], [-ord(c) for c in kv[0]]))
        rounds.append({"tally": dict(tally), "quota": quota})
        if lead_votes >= quota:
            return {
                "winner": leader,
                "quota": quota,
                "no_quorum": False,
                "rounds": rounds,
            }
        if len(remaining) == 1:
            return {
                "winner": remaining[0],
                "quota": quota,
                "no_quorum": True,
                "rounds": rounds,
            }
        # eliminate: fewest votes; tie -> lexicographically smallest id
        loser = min(remaining, key=lambda o: (tally[o], o))
        remaining.remove(loser)
        rounds[-1]["eliminated"] = loser


def ballots_from_json(payload: dict) -> list[Ballot]:
    return [Ballot(voter=b["voter"], ranking=list(b["ranking"])) for b in payload["ballots"]]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: council_stv.py <ballots.json (options, ballots)>", file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        payload = json.load(fh)
    minutes = count_stv(payload["options"], ballots_from_json(payload))
    json.dump(minutes, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
