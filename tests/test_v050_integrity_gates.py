"""End-to-end `v0.5.0` governance, confidentiality, link, soul, eval, and WASM rule gates."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def test_all_24_souls_parse_and_bind_active_skills():
    reg = json.loads((ROOT / "agents" / "facets" / "registry.json").read_text(encoding="utf-8"))
    active_core = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    soul_files = sorted((ROOT / "agents" / "souls").glob("*.md"))
    assert len(soul_files) == 24
    assert len(reg["soul_overlays"]) == 24

    for sp in soul_files:
        lines = sp.read_text(encoding="utf-8").splitlines()
        assert lines and lines[0].strip() == "---", f"{sp.name}: missing opening ---"
        end_idx = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
        assert end_idx is not None, f"{sp.name}: missing closing ---"
        fm = yaml.safe_load("\n".join(lines[1:end_idx]))
        assert isinstance(fm, dict), f"{sp.name}: frontmatter is not a dict"
        assert fm.get("name") == sp.stem
        assert fm.get("role_container") in reg["role_containers"]
        assert fm.get("primary_skill") in active_core, (
            f"{sp.name}: primary_skill {fm.get('primary_skill')!r} not in active 43 core skills"
        )
        assert fm.get("primary_skill") == reg["soul_overlays"][sp.stem]["primary_skill"]


def test_all_json_files_parse_and_uniform_v050_versions():
    json_files = [
        p
        for p in sorted(ROOT.rglob("*.json"))
        if not any(part in p.parts for part in (".git", "node_modules"))
    ]
    assert len(json_files) >= 20
    for jf in json_files:
        json.loads(jf.read_text(encoding="utf-8"))

    apm = yaml.safe_load((ROOT / "apm.yml").read_text(encoding="utf-8"))
    assert str(apm.get("version")) == "0.5.0"

    plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    assert plugin["version"] == "0.5.0"

    gemini_ext = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
    assert gemini_ext["version"] == "0.5.0"
    assert gemini_ext["capabilities"]["knowledgeGraph"] == "kuzu/prover_knowledge.kz"
    assert (ROOT / "kuzu" / "prover_knowledge.kz").is_file()
    assert not (ROOT / "kuzu" / "lean-knowledge.kz").exists()


def test_zero_broken_relative_markdown_links():
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    broken: list[tuple[str, str]] = []
    for md in sorted(ROOT.rglob("*.md")):
        if any(p in md.parts for p in (".git", "node_modules", "tools")):
            continue
        stripped = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.DOTALL)
        for m in link_re.finditer(stripped):
            raw = m.group(1).strip()
            if not raw or raw.startswith(("http://", "https://", "mailto:", "#", "file://", "<")):
                continue
            target_str = raw.split("#", 1)[0].split(" ", 1)[0]
            if not target_str or "{" in target_str or "<" in target_str or "*" in target_str:
                continue
            if not (md.parent / target_str).resolve().exists():
                broken.append((str(md.relative_to(ROOT)), raw))
    assert not broken, f"Broken relative Markdown links found: {broken[:10]}"


def test_50_smoke_cases_and_no_retired_handoffs():
    core_slugs = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    pack_slugs = {p.parent.name for p in (ROOT / "packs" / "applied-strategy" / "skills").glob("*/SKILL.md")}
    assert len(core_slugs) == 43
    assert len(pack_slugs) == 7

    smoke_files = sorted((ROOT / "scripts" / "eval" / "cases").glob("*-smoke.yaml"))
    assert len(smoke_files) == 50
    smoke_slugs = {p.stem[:-6] for p in smoke_files}
    assert smoke_slugs == (core_slugs | pack_slugs)

    # All 9 skills/*/tests/*.yaml files must be linked in their parent SKILL.md
    test_yamls = sorted((ROOT / "skills").glob("*/tests/*.yaml"))
    assert len(test_yamls) == 9
    for ty in test_yamls:
        sk_text = (ty.parents[1] / "SKILL.md").read_text(encoding="utf-8")
        assert ty.name in sk_text, f"{ty.relative_to(ROOT)} not linked in SKILL.md"

    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "eval" / "run_eval.py")],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert res.returncode == 0, f"run_eval.py failed:\n{res.stdout}\n{res.stderr}"


def test_lean_rules_core_profile_and_privacy_audit_clean():
    priv = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "lint" / "privacy_audit.py"), "--json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert priv.returncode == 0, f"privacy_audit.py failed:\n{priv.stdout}\n{priv.stderr}"
    payload = json.loads(priv.stdout)
    assert payload["passed"] is True and payload["violations_count"] == 0

    node_bin = shutil.which("node")
    lean_rules_js = ROOT / "tools" / "lean-lsp-mcp" / "bin" / "lean-rules.js"
    if node_bin and lean_rules_js.is_file():
        lr = subprocess.run(
            [
                node_bin,
                str(lean_rules_js),
                "--profile=core",
                str(ROOT / "packages" / "altproof"),
                str(ROOT / "templates" / "core" / "examples"),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert lr.returncode == 0, f"lean-rules --profile=core failed:\n{lr.stdout}\n{lr.stderr}"


def test_public_graph_ignores_local_garden_and_matches_shipped_projection(tmp_path):
    garden = tmp_path / "private-garden"
    book = garden / "source-materials" / "books" / "private-book"
    book.mkdir(parents=True)
    (book / "anchors.v1.json").write_text(json.dumps({"rows": [{
        "anchor": "private-anchor", "heading_text": "Private notebook",
        "leittext": "private-excerpt-marker", "print_page": 7,
    }]}), encoding="ascii")
    output = tmp_path / "release"
    command = [sys.executable, str(ROOT / "graph" / "export_kuzu.py")]
    subprocess.run(command + ["--garden-root", str(garden), "--out-dir", str(output)],
                   check=True)
    archive = output / "prover_knowledge.kz"
    subprocess.run(command + ["--check-public", str(archive)], check=True)
    subprocess.run(command + ["--check-public", str(ROOT / "kuzu" / archive.name)],
                   check=True)
    local = tmp_path / "local"
    subprocess.run(command + ["--profile", "prover", "--garden-root", str(garden),
                              "--out-dir", str(local), "--export-public", str(output)],
                   check=True)
    subprocess.run(command + ["--check-public", str(archive)], check=True)
    rejected = subprocess.run(command + ["--check-public", str(local / archive.name)],
                              capture_output=True)
    assert rejected.returncode != 0
