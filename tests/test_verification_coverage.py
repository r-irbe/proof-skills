"""Coverage regressions for namespace extraction and source/paper metrics."""
import importlib.util
from pathlib import Path
import subprocess
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts/lean'

def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value

axioms = module('axiom_audit')
metrics = module('metric_sync')


def test_mutual_end_preserves_namespace_and_nested_sections(tmp_path):
    source = tmp_path / 'Sample.lean'
    source.write_text('namespace Outer\nsection Local\nmutual\n  def a := 1\n  def b := a\nend\nlemma inside : True := by trivial\nend Local\nnamespace Inner\nlemma nested : True := by trivial\nend Inner\nend Outer\nlemma outside : True := by trivial\n')
    names = axioms.decl_names(axioms.extract_theorems_from_file(source))
    assert names == ['Outer.inside', 'Outer.Inner.nested', 'outside']


def audit_cli(tmp_path, capture):
    project = tmp_path / 'Demo'; project.mkdir()
    (project / 'Sample.lean').write_text('namespace Demo\ntheorem sample : True := by trivial\nend Demo\n')
    output = tmp_path / 'capture.txt'; output.write_text(capture)
    return subprocess.run([sys.executable, str(SCRIPTS/'axiom_audit.py'), '--lean-dir',str(project), '--project','Demo','--axiom-output',str(output),'--output',str(tmp_path/'report.md')], capture_output=True,text=True)


def test_audit_rejects_incomplete_capture(tmp_path):
    assert audit_cli(tmp_path, '').returncode != 0


def test_audit_rejects_kernel_errors(tmp_path):
    assert audit_cli(tmp_path, "'Demo.sample' does not depend on any axioms\nprobe.lean:1:0: error(lean.unknownIdentifier): Unknown constant bad\n").returncode != 0


def test_audit_rejects_forbidden_axioms(tmp_path):
    assert audit_cli(tmp_path, "'Demo.sample' depends on axioms: [sorryAx]\n").returncode != 0


def test_audit_accepts_complete_clean_capture(tmp_path):
    assert audit_cli(tmp_path, "'Demo.sample' depends on axioms: [propext]\n").returncode == 0


def test_metrics_scan_nested_sources_and_mask_comments_strings(tmp_path):
    (tmp_path/'Nested').mkdir(); (tmp_path/'.scratch').mkdir()
    (tmp_path/'Nested'/'Sample.lean').write_text('/- theorem fake : False := by sorry /- nested -/ -/\nprivate lemma actual : True := by trivial\n@[simp] theorem other : True := by trivial\ndef text := "sorry theorem fake"\n-- sorry\n')
    (tmp_path/'.scratch'/'Nope.lean').write_text('theorem fake : False := by sorry\n')
    result = metrics.compute_lean_metrics(tmp_path)
    assert result['module_count'] == 1
    assert result['total_theorems'] == 1
    assert result['total_lemmas'] == 1
    assert result['total_definitions'] == 1
    assert result['total_sorry'] == 0


def test_metrics_cli_missing_paper_never_passes(tmp_path):
    (tmp_path/'Sample.lean').write_text('theorem x : True := by trivial\n')
    result = subprocess.run([sys.executable,str(SCRIPTS/'metric_sync.py'),'--lean-dir',str(tmp_path),'--paper',str(tmp_path/'missing.tex')],capture_output=True,text=True)
    assert result.returncode != 0


def test_metrics_empty_source_never_passes(tmp_path):
    paper=tmp_path/'paper.tex'; paper.write_text('No comparable source metrics.')
    result=subprocess.run([sys.executable,str(SCRIPTS/'metric_sync.py'),'--lean-dir',str(tmp_path),'--paper',str(paper)],capture_output=True,text=True)
    assert result.returncode != 0


def test_audit_ignores_scope_words_inside_strings(tmp_path):
    source=tmp_path/'Sample.lean'
    source.write_text('namespace Real\ndef text := "\nend\nnamespace Fake\n"\ntheorem kept : True := by trivial\nend Real\n')
    assert axioms.decl_names(axioms.extract_theorems_from_file(source)) == ['Real.kept']


def test_metrics_explicit_source_claims_can_match(tmp_path):
    project=tmp_path/'Demo';project.mkdir()
    (project/'Sample.lean').write_text('theorem sample : True := by trivial\n')
    values={'total_lines':1,'total_theorems':1,'total_lemmas':0,'total_definitions':0,'total_sorry':0,'module_count':1}
    paper=tmp_path/'paper.tex';paper.write_text('\n'.join(f'% lean-metric {k}: {v}' for k,v in values.items()))
    result=subprocess.run([sys.executable,str(SCRIPTS/'metric_sync.py'),'--lean-dir',str(project),'--paper',str(paper)],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr


def test_metrics_unscoped_prose_is_not_verified(tmp_path):
    (tmp_path/'Sample.lean').write_text('theorem sample : True := by trivial\n')
    paper=tmp_path/'paper.tex';paper.write_text('1 lines of Lean, 1 theorems, 0 lemmas, 0 definitions, zero sorry, 1 modules')
    result=subprocess.run([sys.executable,str(SCRIPTS/'metric_sync.py'),'--lean-dir',str(tmp_path),'--paper',str(paper)],capture_output=True,text=True)
    assert result.returncode!=0


def test_audit_rejects_stale_capture_even_when_names_match(tmp_path):
    import os,time
    result=audit_cli(tmp_path,"'Demo.sample' does not depend on any axioms\n")
    os.utime(tmp_path/'Demo/Sample.lean',(time.time()+10,time.time()+10))
    result=subprocess.run(result.args,capture_output=True,text=True)
    assert result.returncode!=0


def test_audit_missing_explicit_capture_refuses_equals_syntax(tmp_path):
    project=tmp_path/'Demo';project.mkdir()
    (project/'Sample.lean').write_text('theorem x : True := by trivial\n')
    result=subprocess.run([sys.executable,str(SCRIPTS/'axiom_audit.py'),'--lean-dir',str(project),f'--axiom-output={tmp_path}/missing.txt','--output',str(tmp_path/'report.md')],capture_output=True,text=True)
    assert result.returncode!=0


def test_metrics_conflicting_explicit_claims_refuse(tmp_path):
    paper=tmp_path/'paper.tex';paper.write_text('% lean-metric module_count: 1\n% lean-metric module_count: 2\n')
    import pytest
    with pytest.raises(ValueError,match='Conflicting'):
        metrics.extract_paper_metrics(paper)


def test_lean_literals_do_not_hide_following_declarations_or_active_holes(tmp_path):
    samples = ["def quote : Char := '\"'\n", 'def text := r#"a "\nnamespace Fake\n"#\n', 'theorem «a"b» : True := by trivial\n', 'theorem «a--b» : True := by trivial\n']
    for index,sample in enumerate(samples):
        source=tmp_path/f'Sample{index}.lean'
        source.write_text('namespace Real\ntheorem before : True := by trivial\n'+sample+'theorem after : False := by sorry\nend Real\n')
        names=axioms.decl_names(axioms.extract_theorems_from_file(source))
        assert 'Real.after' in names,(sample,names)
    (tmp_path/'Interpolation.lean').write_text('def text := s!"{(by sorry : Nat)}"\n')
    assert metrics.compute_lean_metrics(tmp_path)['total_sorry']==5


def test_quoted_identifiers_are_complete_names(tmp_path):
    source=tmp_path/'Sample.lean';source.write_text('namespace Real\ntheorem «a"b» : True := by trivial\ntheorem «a b» : True := by trivial\nend Real\n')
    assert axioms.decl_names(axioms.extract_theorems_from_file(source))==['Real.«a"b»','Real.«a b»']


def test_raw_axiom_strings_are_not_declarations(tmp_path):
    source=tmp_path/'Sample.lean';source.write_text('def text := "\naxiom bogus : False\n"\n')
    assert axioms.scan_raw_axioms(tmp_path)=={}


def test_audit_rejects_truncated_and_duplicate_records(tmp_path):
    capture="'Demo.sample' does not depend on any axioms\n'Demo.sample' depends on axioms: [sorryAx"
    assert audit_cli(tmp_path,capture).returncode!=0


def test_audit_explicit_capture_abbreviation_is_not_bypassed(tmp_path):
    project=tmp_path/'Demo';project.mkdir();(project/'Sample.lean').write_text('theorem sample : True := by trivial\n')
    result=subprocess.run([sys.executable,str(SCRIPTS/'axiom_audit.py'),'--lean-dir',str(project),'--axiom-out',str(tmp_path/'missing.txt'),'--output',str(tmp_path/'report.md')],capture_output=True,text=True)
    assert result.returncode!=0


def test_metrics_quoted_identifier_is_not_a_proof_hole(tmp_path):
    (tmp_path/'Sample.lean').write_text('def «sorry» := 0\n')
    assert metrics.compute_lean_metrics(tmp_path)['total_sorry']==0


def test_metrics_message_interpolation_keeps_active_holes(tmp_path):
    (tmp_path/'Sample.lean').write_text('def text := m!"{(by sorry : Nat)}"\n')
    assert metrics.compute_lean_metrics(tmp_path)['total_sorry']==1


def test_raw_axiom_namespace_survives_mutual_and_quoted_names(tmp_path):
    source=tmp_path/'Sample.lean';source.write_text('namespace Real\nmutual\ndef x := 0\nend\naxiom «a b» : False\nend Real\n')
    assert axioms.scan_raw_axioms(tmp_path)=={'Sample':[(5,'Real.«a b»')]}
