"""Unit tests for Proposals 9A, 9B, 10A, 10B, and 10C.

Covers:
  - `TraceIndex` (`.ilean` + `.ast.json`), S2 `attribute_theorem_spans`, and S3 `detect_v4`
  - Numina 6-Pattern Structural Logic Golfer (`detect_structural_golf_opportunities`) + semicolon detector
  - `nanoproof` hardest-subgoal bottleneck scorer (`score_subgoal_bottleneck`), `is_cycling`, and `leanprogress_scorer`
  - `lemma_evolver.py` (4 LEGO-Prover operators, STP conjecture generator, 3-Verifier `0/0.5/1` panel, `GenSelect`)
  - `lean_serve_broker.py` telemetry (`read_proc_rss_mb`, `get_system_load`, `error_ring`)
  - `check_citations.py` and `check_canary_validation.py`

Strict 7-bit ASCII only (INV-001).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lean"))
sys.path.insert(0, str(ROOT / "scripts" / "lean" / "altproof"))
sys.path.insert(0, str(ROOT / "tools" / "lean-serve-broker"))

from candidate_evaluator import score_tactic_branch
from check_canary_validation import (
    evaluate_canary_response,
    validate_canary_spec,
)
from check_citations import verify_markdown_citations, write_last_verified_stamp
from cost_ranker import (
    is_cycling,
    leanprogress_scorer,
    score_subgoal_bottleneck,
)
from detect_v4 import detect_v4, detect_v4_file
from have_cluster import GOLF_PATTERNS, detect_structural_golf_opportunities
from lean_serve_broker import Broker, get_system_load, read_proc_rss_mb
from legibility import score_block
from lemma_evolver import (
    MUTATION_OPERATORS,
    evolve_lemma,
    generate_stp_conjectures,
    genselect_tournament,
    score_informal_proof_rubric,
    verify_with_panel,
)
from trace_symbols import (
    TraceIndex,
    attribute_theorem_spans,
    find_enclosing_theorem,
)


def test_ilean_trace_index_s2_spans_and_s3_detect_v4(tmp_path: Path):
    ilean_dir = tmp_path / ".lake" / "build" / "lib" / "lean" / "Demo"
    ilean_dir.mkdir(parents=True)
    ilean_payload = {
        "version": 4,
        "module": "Demo.Basic",
        "directImports": ["Init"],
        "decls": {
            "Demo.Basic.my_thm": [3, 0, 10, 12, 3, 8, 3, 14],
        },
        "references": {
            "Demo.Helper.crossModHelper": {
                "definition": ["Demo.Helper", 1, 0, 1, 10],
                "usages": [[5, 4, 5, 18]],
            }
        },
    }
    (ilean_dir / "Basic.ilean").write_text(
        json.dumps(ilean_payload), encoding="utf-8"
    )

    idx = TraceIndex(tmp_path)
    assert "crossModHelper" in idx.symbols_for("Demo/Basic.lean")
    spans = idx.theorem_spans_for("Demo/Basic.lean")
    assert len(spans) == 1
    assert spans[0].name == "my_thm"
    assert spans[0].start_line == 3 and spans[0].end_line == 10
    assert find_enclosing_theorem(6, spans) == "my_thm"

    # Cross-module helper application is demoted by detect_v4 when in .ilean index,
    # while genuinely unnamed repeated subterms are retained.
    proof = (
        "  have h1 := crossModHelper (a + b) (c + d)\n"
        "  have h2 := crossModHelper (a + b) (c + d)\n"
        "  have h3 := (x * y + z) + (x * y + z)\n"
    )
    cands = detect_v4(proof, theorem="my_thm", index=idx, source_rel="Demo/Basic.lean")
    evidences = [c.evidence for c in cands]
    assert not any(ev.startswith("crossModHelper") for ev in evidences)


def test_six_pattern_structural_golfer_and_semicolon_detector():
    proof = (
        "  have h_dup1 : a + b = c := by omega\n"
        "  have h_dup2 : a + b = c := by omega\n"
        "  have h_unused : x = x := by rfl\n"
        "  have h_triv := h_dup1.symm\n"
        "  have h_eq : d = e := by omega\n"
        "  have p1 := hpair.1\n"
        "  have p2 := hpair.2\n"
        "  rw [h_triv, h_eq]; omega\n"
    )
    opps = detect_structural_golf_opportunities(proof)
    found_patterns = {o["pattern"] for o in opps}
    assert set(GOLF_PATTERNS).issubset(found_patterns)

    leg = score_block(proof)
    assert leg["has_semicolons"] is True
    assert len(leg["semicolon_lines"]) == 1
    assert len(leg["golf_opportunities"]) >= 6


def test_nanoproof_bottleneck_scorer_and_leanprogress():
    assert score_subgoal_bottleneck([]) == 1.0
    assert score_subgoal_bottleneck([0.9, 0.25, 0.8]) == 0.25

    history = ["x : Nat\n|- x + 1 = 1 + x"]
    assert is_cycling(history, "  x : Nat \n |- x + 1 = 1 + x ") is True
    assert is_cycling(history, "x : Nat\n|- x = x") is False

    s_simple = leanprogress_scorer("|- a = a")
    s_complex = leanprogress_scorer("|- forall x, exists y, (P x /\\ Q y) <-> Finset.sum s f <= 0")
    assert s_simple > s_complex > 0.0

    branch = score_tactic_branch(["|- a = a", "|- forall x, P x /\\ Q x"], state_history=history, current_state="|- a = a")
    assert branch["is_cycling"] is False
    assert branch["bottleneck_score"] == min(branch["subgoal_scores"])


def test_lemma_evolver_stp_conjecturer_and_3_verifier_panel():
    sample_lean = (
        "theorem scale_bound (x : Real) (h : 0 <= x) : x * 100 >= 0 := by\n"
        "  exact mul_nonneg h (by norm_num)\n"
    )
    ev = evolve_lemma(sample_lean)
    assert set(ev["operators_applied"]) == set(MUTATION_OPERATORS)

    conj = generate_stp_conjectures(sample_lean, empirical_pass_rate=0.35)
    assert conj["in_stp_target_band"] is True
    assert conj["pair_count"] == 1
    assert conj["conjectures"][0]["stp_reward"] == 1.0

    bad_sketch = "Obviously by symmetry this holds trivially."
    good_sketch = (
        "1. Apply `Finset.sum_le_sum` to reduce the global inequality to pointwise terms.\n"
        "2. For each index `i`, invoke `mul_le_mul_of_nonneg_left` using hypothesis `hc i`.\n"
        "3. Conclude by `linarith`."
    )
    assert verify_with_panel("prob", bad_sketch)["approved"] is False
    assert score_informal_proof_rubric(bad_sketch)["score"] == 0.5
    assert verify_with_panel("prob", good_sketch)["approved"] is True

    tour = genselect_tournament("prob", [bad_sketch, good_sketch])
    assert tour["winner_index"] == 1
    assert tour["winner_approved"] is True


def test_lean_serve_broker_telemetry():
    rss = read_proc_rss_mb(os.getpid())
    assert rss > 0.0
    load = get_system_load()
    assert len(load) == 3

    b = Broker("/tmp", ["true"])
    for idx in range(25):
        b.record_error("test_err", f"msg {idx}")
    assert len(b.error_ring) == 20
    assert b.error_ring[0]["detail"] == "msg 5"


def test_check_citations_and_canary_validation(tmp_path: Path):
    src_file = tmp_path / "Sample.lean"
    src_file.write_text("line1\nline2\nline3\n", encoding="utf-8")

    skills_dir = tmp_path / "skills" / "demo"
    skills_dir.mkdir(parents=True)
    md_good = skills_dir / "SKILL.md"
    md_good.write_text("See `Sample.lean:2` for details.\n", encoding="utf-8")

    rep_ok = verify_markdown_citations(tmp_path)
    assert rep_ok["ok"] is True
    assert rep_ok["citations_checked"] == 1

    stamp_path = tmp_path / "LAST_VERIFIED.md"
    write_last_verified_stamp(stamp_path, rep_ok)
    assert "PASS" in stamp_path.read_text(encoding="utf-8")

    # Out-of-range line citation must be flagged
    md_good.write_text("See `Sample.lean:99` for details.\n", encoding="utf-8")
    rep_bad = verify_markdown_citations(tmp_path)
    assert rep_bad["ok"] is False
    assert rep_bad["broken_count"] == 1

    canary_spec = {
        "skill": "lean-proof",
        "prompt": "Prove finite sum linearity",
        "expected_patterns": ["sum_congr_ring", "Finset\\.sum"],
        "forbidden_patterns": ["native_decide", "sorry"],
    }
    assert validate_canary_spec(canary_spec)["ok"] is True
    assert evaluate_canary_response(canary_spec, "Use sum_congr_ring on Finset.sum")["passed"] is True
    assert evaluate_canary_response(canary_spec, "Use native_decide")["passed"] is False


def test_altproof_cli_and_standalone_lake_package():
    import cli
    pkg_dir = ROOT / "packages" / "altproof"
    assert (pkg_dir / "lean-toolchain").is_file()
    assert (pkg_dir / "lakefile.lean").is_file()
    assert (pkg_dir / "AltProof.lean").is_file()
    assert (pkg_dir / "AltProof" / "Tactics.lean").is_file()
    assert (pkg_dir / "AltProof" / "Tests.lean").is_file()
    assert (pkg_dir / "README.md").is_file()
    assert (ROOT / "scripts" / "lean" / "altproof" / "pyproject.toml").is_file()

    assert cli.main(["--help"]) == 0
    assert cli.main(["routes", "--json"]) == 0
    assert cli.main(["dispatch", "--self-test"]) == 0
    assert cli.main(["rank", "--lines", "10", "--shared-lemmas", "1"]) == 0
    assert cli.main(["detect-v4", str(pkg_dir / "AltProof" / "Tests.lean")]) == 0
    assert cli.main(["extract", str(pkg_dir / "AltProof" / "Tests.lean")]) == 0
    assert cli.main(["cluster", str(pkg_dir)]) == 0


def test_init_project_bootstrapper_and_compile_handbooks(tmp_path: Path):
    import compile_handbook_tables
    import init_project

    res = init_project.init_project(
        tmp_path / "demo-lean-proj",
        mode="weftd",
        profiles=["core", "math", "pack-altproof"],
        agents=["claude", "gemini", "cursor", "pi", "opencode", "dsh", "zed", "weftd"],
    )
    assert res["ok"] is True
    proj_dir = tmp_path / "demo-lean-proj"
    assert (proj_dir / "lean-project.toml").is_file()
    assert (proj_dir / "skills-overrides" / "subst_table.json").is_file()
    assert (proj_dir / ".mcp.json").is_file()
    assert (proj_dir / ".claude" / "settings.json").is_file()
    assert (proj_dir / ".gemini" / "settings.json").is_file()
    assert (proj_dir / ".cursor" / "mcp.json").is_file()
    assert (proj_dir / ".pi" / "settings.json").is_file()
    assert (proj_dir / "opencode.json").is_file()
    assert (proj_dir / ".dsh" / "config.json").is_file()
    assert (proj_dir / ".zed" / "settings.json").is_file()
    assert (proj_dir / ".weft" / "config.json").is_file()

    hb_path = ROOT / "vendor" / "itp-ontology" / "handbook-tables.v1.json"
    assert hb_path.is_file()
    hb_data = json.loads(hb_path.read_text(encoding="ascii"))
    assert hb_data["handbooks_count"] >= 15
    assert hb_data["counts"]["goal_shape_templates"] >= 50
    assert hb_data["counts"]["intent_phrasebook"] >= 50
    assert hb_data["counts"]["error_to_fix"] >= 50
    assert compile_handbook_tables.main(["--check"]) == 0

