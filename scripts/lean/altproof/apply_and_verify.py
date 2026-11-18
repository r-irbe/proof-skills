"""Automated candidate patch verification loop for AltProof (Track 1).

Orchestrates candidate patching (A4), tactic dispatching (A5), and regression-safety
evaluation to generate atomic transformation receipts.

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import sys as _sys
from pathlib import Path as _Path

if str(_Path(__file__).resolve().parent) not in _sys.path:
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
if __package__:
    from .autoslim import run_autoslim
else:
    from autoslim import run_autoslim
if __package__:
    from .candidate_patcher import patch_candidate
else:
    from candidate_patcher import patch_candidate
if __package__:
    from .tactic_dispatcher import TacticRecommendation, recommend_tactics
else:
    from tactic_dispatcher import TacticRecommendation, recommend_tactics


@dataclass
class PatchVerificationResult:
    """Structural patch receipt, not a Lean proof-verification result.

    Structural success means the returned source text changed. Kernel success
    means a verified change was published; lean_verified also covers proposals.
    """

    file_path: str
    target_pattern: str
    success: bool
    original_text: str
    transformed_text: str
    tactic_recommendation: TacticRecommendation | None = None
    verification_notes: list[str] = field(default_factory=list)
    verification_level: str = "structural-only"
    lean_verified: bool = False
    trust_audited: bool = False
    changed: bool = False
    applied: bool = False


def apply_and_verify_tactic(
    source_text: str,
    file_path: str = "InMemory.lean",
    target_pattern: str = "linarith",
) -> PatchVerificationResult:
    """Apply structural tactic recommendation and verify transform integrity."""
    notes = ["Lean verification, trust auditing, and timing measurements were not performed."]

    # 1. Recommend tactic based on goal / context
    recs = recommend_tactics(source_text)
    primary_rec = recs[0] if recs else None
    tactic_name = primary_rec.tactic if primary_rec else target_pattern

    if primary_rec:
        notes.append(
            f"Recommended primary tactic: {primary_rec.tactic} (confidence: {primary_rec.confidence:.2f})"
        )
    else:
        notes.append(f"No specific automated tactic inferred; using fallback {tactic_name}")

    # 2. Patch candidate if pattern matches
    patch_res = patch_candidate(source_text, target_pattern=target_pattern, replacement=tactic_name)

    if patch_res.patched:
        notes.append(f"Successfully patched pattern '{target_pattern}' with '{tactic_name}'")
        notes.append(
            f"Lines before: {patch_res.lines_before}, Lines after: {patch_res.lines_after}"
        )
        success = True
    else:
        notes.append(f"Pattern '{target_pattern}' not found or replacement identical; text unmodified")
        success = False

    return PatchVerificationResult(
        file_path=file_path,
        target_pattern=target_pattern,
        success=success,
        original_text=source_text,
        transformed_text=patch_res.transformed_text,
        changed=patch_res.patched,
        tactic_recommendation=primary_rec,
        verification_notes=notes,
    )


def verify_file_with_lean(
    file_path: str | Path,
    *,
    apply: bool = False,
    mode: str = "auto",
    allow_altproof_import: bool = False,
) -> PatchVerificationResult:
    """Run real Lean 4 kernel-verified auto-slimming via `lean-autoslim`."""
    target = Path(file_path).expanduser().resolve()
    original_text = target.read_bytes().decode("utf-8")
    report = run_autoslim(
        target,
        apply=apply,
        mode=mode,
        allow_altproof_import=allow_altproof_import,
    )
    transformed_text = target.read_bytes().decode("utf-8") if apply else original_text
    accepted = int(report.get("verifiedCount", report.get("candidatesAccepted", 0)))
    found = int(report.get("candidatesDiscovered", report.get("candidatesFound", 0)))
    saved = int(report.get("netLinesSaved", report.get("totalLinesSaved", 0)))
    mode_used = str(report.get("backendUsed", report.get("modeUsed", "unknown")))
    verified = (accepted > 0 and mode_used in {"batch", "lsp"}
                and report.get("completed", True) is True
                and report.get("finalCheckPassed", True) is True)
    attempted = int(report.get("verificationAttempts", 0)) > 0 and mode_used in {"batch", "lsp"}
    notes = [
        f"Kernel verification backend: {mode_used} (accepted {accepted}/{found}, saved {saved} lines)",
    ]
    for e in report.get("edits") or []:
        notes.append(
            f"{e.get('theoremName', '')} [{e.get('route', '')}] -> "
            f"{e.get('newText', '')} (-{e.get('linesSaved', 0)} lines)"
        )
    return PatchVerificationResult(
        file_path=str(target),
        target_pattern="ALTPROOF-ROUTE",
        success=verified and apply and report.get("applied") is True and transformed_text != original_text,
        changed=transformed_text != original_text,
        applied=verified and apply and report.get("applied") is True and transformed_text != original_text,
        original_text=original_text,
        transformed_text=transformed_text,
        tactic_recommendation=None,
        verification_notes=notes,
        verification_level=(f"lean-kernel-{mode_used}" if verified else
                            f"lean-kernel-{mode_used}-rejected" if attempted else "not-performed"),
        lean_verified=verified,
        trust_audited=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose a structural AltProof patch or run Lean kernel-verified auto-slimming"
    )
    parser.add_argument("file", type=Path, help="Target Lean 4 file")
    parser.add_argument("--pattern", default="linarith", help="Target pattern to replace (structural mode)")
    parser.add_argument(
        "--kernel-verify",
        action="store_true",
        help="Verify proof replacements through Lean 4 via lean-autoslim",
    )
    parser.add_argument("--apply", action="store_true", help="Write verified slimmed file (with --kernel-verify)")
    parser.add_argument(
        "--mode",
        choices=("auto", "lsp", "batch"),
        default="auto",
        help="Verification backend when --kernel-verify is active",
    )
    parser.add_argument(
        "--allow-altproof-import",
        action="store_true",
        help="Permit custom AltProof tactics when --kernel-verify is active",
    )
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"Error: {args.file} not found", file=sys.stderr)
        return 1

    if args.kernel_verify:
        res = verify_file_with_lean(
            args.file,
            apply=args.apply,
            mode=args.mode,
            allow_altproof_import=args.allow_altproof_import,
        )
        print(f"File: {res.file_path}")
        status = ("TRANSFORMED_KERNEL_VERIFIED" if res.success else
                  "PROPOSED_KERNEL_VERIFIED" if res.lean_verified else "NO_VERIFIED_TRANSFORMATION")
        print(f"Status: {status}")
        for n in res.verification_notes or []:
            print(f"  - {n}")
        return 0 if res.lean_verified else 2

    content = args.file.read_text(encoding="utf-8")
    res = apply_and_verify_tactic(content, file_path=str(args.file), target_pattern=args.pattern)

    print(f"File: {res.file_path}")
    print(f"Status: {'TRANSFORMED_UNVERIFIED' if res.success else 'SKIPPED_UNVERIFIED'}")
    for n in res.verification_notes or []:
        print(f"  - {n}")

    return 0 if res.success else 2


if __name__ == "__main__":
    raise SystemExit(main())
