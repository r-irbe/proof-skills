#!/usr/bin/env python3
"""
Skill Ecosystem Health Monitor
Validates the integrity of the entire skill ecosystem:
  - All skills referenced in the gateway registry or v2 handoff graph exist
  - All skills have required fields (name, description)
  - Cross-skill references are valid
  - No orphan skills (exist but not in registry/handoffs)
  - Enforcement scripts are callable and have valid shebang
  - Tracking documents exist and are populated

Usage:
    python3 scripts/ecosystem_health.py [--skills-dir skills/skills] [--scripts-dir scripts]
"""

import argparse
import re
import sys
from pathlib import Path


def check_skill_registry(gateway_path: Path, skills_dir: Path) -> list[dict]:
    """Verify gateway registry or v2 handoff graph matches actual skills."""
    issues = []

    if not gateway_path.exists():
        issues.append(
            {
                "severity": "error",
                "component": "gateway",
                "message": f"Gateway skill not found: {gateway_path}",
            }
        )
        return issues

    gateway_text = gateway_path.read_text(encoding="utf-8")
    ref_dir = gateway_path.parent / "references"
    if ref_dir.is_dir():
        for ref_md in sorted(ref_dir.glob("*.md")):
            gateway_text += "\n" + ref_md.read_text(encoding="utf-8")

    registry_pattern = re.compile(r"\|\s*([A-Za-z0-9_-]+)\s*\|")
    sk_pattern = re.compile(r"\|\s*(SK-\d+)\s*\|\s*([A-Za-z0-9_-]+)\s*\|")
    registry_skills = {}
    for m in sk_pattern.finditer(gateway_text):
        sk_id = m.group(1)
        skill_name = m.group(2)
        registry_skills[sk_id] = skill_name

    for sk_id, skill_name in sorted(registry_skills.items()):
        skill_path = skills_dir / skill_name / "SKILL.md"
        if not skill_path.exists():
            issues.append(
                {
                    "severity": "error",
                    "component": "registry",
                    "message": f"{sk_id} ({skill_name}) registered but SKILL.md not found at {skill_path}",
                }
            )

    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if skill_dir.is_dir() and skill_md.exists():
                name = skill_dir.name
                text = skill_md.read_text(encoding="utf-8")
                is_redirect = "REDIRECT" in text[:400]
                has_v2_handoffs = "handoffs:" in text and "predecessors:" in text
                if name not in registry_skills.values() and not is_redirect and not has_v2_handoffs:
                    issues.append(
                        {
                            "severity": "warn",
                            "component": "registry",
                            "message": f"Skill {name} exists but is not in gateway registry or handoff graph",
                        }
                    )

    return issues


def check_skill_structure(skills_dir: Path) -> list[dict]:
    """Validate each skill has required structure."""
    issues = []
    required_fields = ["name", "description"]

    if not skills_dir.exists():
        return issues

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.exists():
            continue

        name = skill_dir.name
        text = skill_md.read_text(encoding="utf-8")
        is_redirect = "REDIRECT" in text[:400]

        if text.startswith("---"):
            frontmatter_end = text.find("---", 3)
            if frontmatter_end == -1:
                issues.append(
                    {
                        "severity": "error",
                        "component": f"skill/{name}",
                        "message": "Unclosed YAML frontmatter",
                    }
                )
            else:
                frontmatter = text[3:frontmatter_end]
                for field in required_fields:
                    if f"{field}:" not in frontmatter:
                        issues.append(
                            {
                                "severity": "warn",
                                "component": f"skill/{name}",
                                "message": f"Missing frontmatter field: {field}",
                            }
                        )
        else:
            issues.append(
                {
                    "severity": "warn",
                    "component": f"skill/{name}",
                    "message": "Missing YAML frontmatter block",
                }
            )

        if is_redirect:
            continue

        parts = re.findall(r"^## (?:Part \d+|When to use|Workflow|Recovery|Handoffs)", text, re.MULTILINE)
        if not parts:
            issues.append(
                {
                    "severity": "info",
                    "component": f"skill/{name}",
                    "message": "No v1/v2 section headers found",
                }
            )

        lines = len(text.splitlines())
        if lines < 40:
            issues.append(
                {
                    "severity": "warn",
                    "component": f"skill/{name}",
                    "message": f"Very short skill ({lines} lines) -- may need expansion",
                }
            )

    return issues


def check_scripts(scripts_dir: Path) -> list[dict]:
    """Validate enforcement scripts."""
    issues = []

    if not scripts_dir.exists():
        issues.append(
            {
                "severity": "error",
                "component": "scripts",
                "message": f"Scripts directory not found: {scripts_dir}",
            }
        )
        return issues

    expected_scripts = {
        "council_precheck.sh": "bash",
        "review_coverage.py": "python3",
        "axiom_audit.py": "python3",
        "metric_sync.py": "python3",
        "zettelkasten_lint.py": "python3",
        "retro_recon.py": "python3",
        "bridge_validator.py": "python3",
    }

    for script_name, expected_lang in expected_scripts.items():
        script_path = scripts_dir / script_name
        if not script_path.exists():
            issues.append(
                {
                    "severity": "warn",
                    "component": "scripts",
                    "message": f"Expected script not found: {script_name}",
                }
            )
            continue

        text = script_path.read_text(encoding="utf-8")

        if not text.startswith("#!"):
            issues.append(
                {
                    "severity": "warn",
                    "component": f"scripts/{script_name}",
                    "message": "Missing shebang line",
                }
            )

        if expected_lang == "python3" and '"""' not in text[:500]:
            issues.append(
                {
                    "severity": "info",
                    "component": f"scripts/{script_name}",
                    "message": "Missing module docstring",
                }
            )

        has_main = (
            "__name__ == '__main__'" in text
            or '__name__ == "__main__"' in text
            or "os.execv" in text
            or "subprocess.run" in text
            or "runpy.run_path" in text
        )
        if expected_lang == "python3" and not has_main:
            issues.append(
                {
                    "severity": "warn",
                    "component": f"scripts/{script_name}",
                    "message": 'Missing if __name__ == "__main__" guard',
                }
            )

    return issues


def check_tracking_docs(tracking_dir: Path) -> list[dict]:
    """Check that tracking documents exist."""
    issues = []
    expected_docs = [
        "recon_report.md",
        "coverage_matrix.md",
        "axiom_audit.md",
    ]

    if not tracking_dir.exists():
        issues.append(
            {
                "severity": "info",
                "component": "tracking",
                "message": f"Tracking directory not found: {tracking_dir} (create with retro_recon.py)",
            }
        )
        return issues

    for doc in expected_docs:
        doc_path = tracking_dir / doc
        if not doc_path.exists():
            issues.append(
                {
                    "severity": "info",
                    "component": "tracking",
                    "message": f"Missing tracking doc: {doc}",
                }
            )

    return issues


def main():
    parser = argparse.ArgumentParser(description="Skill ecosystem health check")
    parser.add_argument(
        "--root", type=Path, default=None, help="Lean project root"
    )
    parser.add_argument(
        "--skills-dir", type=Path, default=None, help="Skills directory"
    )
    parser.add_argument(
        "--scripts-dir", type=Path, default=None, help="Scripts directory"
    )
    parser.add_argument(
        "--tracking-dir",
        type=Path,
        default=None,
        help="Tracking documents directory",
    )
    args = parser.parse_args()

    base = args.root
    standalone_skills_repo = False
    if base is None:
        if Path("skills/skills").is_dir():
            base = Path(".")
        elif Path("docs/easci/lean/skills/skills").is_dir():
            base = Path("docs/easci/lean")
        elif Path("skills/lean-gateway/SKILL.md").is_file() and Path("scripts/lean").is_dir():
            base = Path(".")
            standalone_skills_repo = True
        else:
            parent_lean = Path(__file__).resolve().parents[3]
            if (parent_lean / "skills" / "skills").is_dir():
                base = parent_lean
            else:
                base = Path(__file__).resolve().parents[2]
                standalone_skills_repo = True
    elif (base / "skills" / "lean-gateway" / "SKILL.md").is_file() and (base / "scripts" / "lean").is_dir():
        standalone_skills_repo = True

    if standalone_skills_repo:
        skills_dir = args.skills_dir or (base / "skills")
        scripts_dir = args.scripts_dir or (base / "scripts" / "lean")
    else:
        skills_dir = args.skills_dir or (base / "skills" / "skills")
        scripts_dir = args.scripts_dir or (base / "scripts")
    tracking_dir = args.tracking_dir or (base / "docs" / "tracking")

    gateway_path = skills_dir / "lean-gateway" / "SKILL.md"

    all_issues = []
    all_issues.extend(check_skill_registry(gateway_path, skills_dir))
    all_issues.extend(check_skill_structure(skills_dir))
    all_issues.extend(check_scripts(scripts_dir))
    if not standalone_skills_repo or args.tracking_dir is not None:
        all_issues.extend(check_tracking_docs(tracking_dir))

    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warn"]
    infos = [i for i in all_issues if i["severity"] == "info"]

    print("Skill Ecosystem Health")
    print("=" * 60)
    print(f"Errors: {len(errors)}  Warnings: {len(warnings)}  Info: {len(infos)}")
    print("-" * 60)

    for issue in sorted(
        all_issues,
        key=lambda i: (
            {"error": 0, "warn": 1, "info": 2}[i["severity"]],
            i["component"],
        ),
    ):
        sev = {"error": "[ERR]", "warn": "[WARN]", "info": "[INFO]"}[issue["severity"]]
        print(f"  {sev} [{issue['component']}] {issue['message']}")

    print()
    if errors:
        print(f"FAIL: {len(errors)} error(s) found")
        sys.exit(1)
    elif warnings:
        print(f"WARN: {len(warnings)} warning(s)")
        sys.exit(0)
    else:
        print("OK: Ecosystem healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()
