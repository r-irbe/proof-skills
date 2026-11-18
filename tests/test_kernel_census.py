"""Receipt checks are read-only and must never promote stale/failed evidence."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch

ENGINE=Path(__file__).resolve().parents[1]/'scripts/lean/kernel_census.py'

def load():
    spec=importlib.util.spec_from_file_location('kernel_census',ENGINE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='census-receipt-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.m=load()
        (self.root/'Fixture.lean').write_text('set_option autoImplicit false\ntheorem ok : True := by trivial\n')
        (self.root/'lean-toolchain').write_text('leanprover/lean4:v0.0.0\n')
        (self.root/'lakefile.toml').write_text('name="fixture"\n')
        lib=self.root/'.lake/build/lib/lean';lib.mkdir(parents=True);(lib/'Fixture.olean').write_bytes(b'compiled')
        compiler=self.root/'toolchain/bin/lean';compiler.parent.mkdir(parents=True);compiler.write_bytes(b'compiler')
        deps=self.root/'deps';deps.mkdir();(deps/'Dep.olean').write_bytes(b'dep')
        standard=self.root/'toolchain/lib/lean';standard.mkdir(parents=True);(standard/'Init.olean').write_bytes(b'init')
        self.context={'compilerPath':str(compiler),'libraryRoots':[str(lib),str(deps),str(standard)],'environment':self.m.ambient_environment(),'environmentFingerprint':self.m.environment_fingerprint()}
        manifest=self.m.select_modules(self.root,lib,'Fixture')
        self.receipt=self.root/'receipt.json'
        self.data={'schemaVersion':2,'mutableCache':True,'projectRoot':str(self.root),'prefix':'Fixture','manifest':manifest,'artifactHashes':self.m.artifacts(lib,manifest['modules']),'kernel':dict(modules=1,constants=1,theorems=1,definitions=0,declaredAxioms=0,eligible=1,replayed=1,axiomAudited=1,skippedUnsafe=0,skippedPartial=0,privateTheorems=0,loadedParts=1,repeatedIdenticalTheorems=[],constantNames=['ok'],theoremNames=['ok'],distinctAxioms=[],disallowedAxiomUses=0,badAxiomUses=[]),'buildExitCode':0,'replayExitCode':0,'context':self.context,'contextHashes':self.m.context_hashes(self.context),'toolHashes':self.m.tool_hashes(),'configHashes':self.m.config_hashes(self.root)}
        self.resolver=patch.object(self.m,'resolve_compiler',return_value=str(compiler));self.resolver.start();self.addCleanup(self.resolver.stop)
        self.write()

    def write(self):self.receipt.write_text(json.dumps(self.data))
    def inspect(self):return self.m.inspect_receipt(self.root,'Fixture',self.receipt)

    def test_fresh_receipt_has_kernel_kind_and_scope(self):
        result=self.inspect();self.assertEqual(result['status'],'verified');self.assertTrue(result['gateEligible'])
        self.assertEqual(result['evidenceKind'],'compiled-kernel-replay');self.assertEqual(result['counts']['replayed'],1)
        self.assertNotIn('constantNames',result['counts'])

    def test_fresh_check_launches_no_lean_or_build(self):
        with patch.object(self.m, 'command', side_effect=AssertionError('check launched a process')):
            self.assertEqual(self.inspect()['status'],'verified')

    def test_source_byte_change_with_same_metadata_is_stale(self):
        p=self.root/'Fixture.lean';st=p.stat();p.write_text(p.read_text().replace('trivial','decide '));os.utime(p,ns=(st.st_atime_ns,st.st_mtime_ns))
        self.assertEqual(self.inspect()['status'],'stale')

    def test_new_source_sidecar_config_compiler_and_dependency_invalidate(self):
        for kind in ['source','artifact','config','compiler','dependency']:
            with self.subTest(kind=kind):
                p={'source':self.root/'Fixture/New.lean','artifact':self.root/'.lake/build/lib/lean/Fixture.olean.private','config':self.root/'lake-manifest.json','compiler':Path(self.context['compilerPath']),'dependency':self.root/'deps/New.olean'}[kind]
                old=p.read_bytes() if p.exists() else None;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'changed')
                try:self.assertEqual(self.inspect()['status'],'stale')
                finally:
                    if old is None:p.unlink()
                    else:p.write_bytes(old)

    def test_failed_legacy_truncated_and_duplicate_coverage_refuse(self):
        original=json.loads(json.dumps(self.data))
        for patch in [{'replayExitCode':1},{'schemaVersion':1},{'kernel':dict(original['kernel'],replayed=0)},{'kernel':dict(original['kernel'],constantNames=['ok','ok'])},{'kernel':dict(original['kernel'],disallowedAxiomUses=1,badAxiomUses=['ok: bad'])}]:
            self.data=dict(original,**patch);self.write();result=self.inspect();self.assertNotEqual(result['status'],'verified');self.assertFalse(result['gateEligible'])
        self.receipt.write_text('{');self.assertEqual(self.inspect()['status'],'unverified')

    def test_missing_fifo_and_path_escape_refuse_without_commands(self):
        self.receipt.unlink();self.assertEqual(self.inspect()['status'],'missing')
        os.mkfifo(self.receipt);self.assertEqual(self.inspect()['status'],'unverified');self.receipt.unlink()
        self.data['manifest']['sources']={'../escape.lean':'0'*64};self.write();self.assertEqual(self.inspect()['status'],'unverified')

    def test_rebuild_refuses_existing_lock_and_protected_outputs(self):
        original=self.receipt.read_bytes()
        with self.m.receipt_lock(self.receipt):
            with self.assertRaisesRegex((ValueError,RuntimeError), 'lock|busy'):
                self.m.rebuild(self.root,'Fixture',self.receipt)
        self.assertEqual(self.receipt.read_bytes(),original)
        with self.assertRaisesRegex(ValueError,'JSON|receipt'):
            self.m.rebuild(self.root,'Fixture',self.root/'Fixture.lean')

    def test_impossible_counts_empty_context_and_missing_base_refuse(self):
        original=json.loads(json.dumps(self.data))
        for field,value in [('definitions',2),('theorems',2),('privateTheorems',2),('loadedParts',0)]:
            self.data=json.loads(json.dumps(original));self.data['kernel'][field]=value;self.write()
            self.assertNotEqual(self.inspect()['status'],'verified')
        self.data=json.loads(json.dumps(original));self.data['context']['libraryRoots']=[];self.data['contextHashes']={};self.write()
        self.assertNotEqual(self.inspect()['status'],'verified')
        self.data=json.loads(json.dumps(original));(self.root/'.lake/build/lib/lean/Fixture.olean').unlink();self.data['artifactHashes']={};self.write()
        self.assertNotEqual(self.inspect()['status'],'verified')

    def test_unrelated_json_and_hardlinked_logs_are_preserved(self):
        output=self.root/'settings.json';output.write_text('{"editor":"keep"}')
        with self.assertRaisesRegex(ValueError,'receipt|cache|unrelated'):
            self.m.rebuild(self.root,'Fixture',output)
        self.assertEqual(output.read_text(),'{"editor":"keep"}')
        protected=self.root/'protected.txt';protected.write_text('keep')
        log=self.root/'receipt.build.log';os.link(protected,log)
        with self.m.output_parent(log) as parent:
            with self.m.atomic_log(log,parent) as stream:stream.write('new log')
        self.assertEqual(protected.read_text(),'keep');self.assertEqual(log.read_text(),'new log')

        with self.m.receipt_lock(output):pass
        with self.m.receipt_lock(output):pass

    def test_source_fifo_and_symlink_refuse_without_reading(self):
        directory=self.root/'Fixture';directory.mkdir()
        fifo=directory/'Bad.lean';os.mkfifo(fifo)
        with self.assertRaises(ValueError):self.m.source_files(self.root,'Fixture')
        fifo.unlink()
        outside=self.root.parent/(self.root.name+'-outside.lean');outside.write_text('external');self.addCleanup(outside.unlink)
        fifo.symlink_to(outside)
        with self.assertRaises(ValueError):self.m.source_files(self.root,'Fixture')

    def test_build_configuration_and_compiler_changes_refuse(self):
        from types import SimpleNamespace
        for kind in ['config','compiler']:
            self.write()
            target=self.root/'lakefile.toml' if kind=='config' else Path(self.context['compilerPath'])
            previous=target.read_bytes()
            def mutate(argv,**kwargs):
                target.write_bytes(b'changed during build')
                return SimpleNamespace(returncode=0)
            with patch.object(self.m,'capture_context',return_value=self.context),patch.object(self.m,'command',side_effect=mutate):
                with self.assertRaisesRegex(RuntimeError,'configuration|compiler'):
                    self.m.rebuild(self.root,'Fixture',self.receipt)
            target.write_bytes(previous)

    def test_os_lock_recovers_after_abrupt_exit(self):
        code="import importlib.util,os;from pathlib import Path;s=importlib.util.spec_from_file_location('k',%r);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.receipt_lock(Path(%r));c.__enter__();os._exit(9)" % (str(ENGINE),str(self.receipt))
        process=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
        self.assertEqual(process.returncode,9,process.stderr)
        with self.m.receipt_lock(self.receipt):pass

    def test_active_compiler_and_custom_environment_change_are_stale(self):
        other=self.root/'other-lean';other.write_bytes(b'other')
        with patch.object(self.m,'resolve_compiler',return_value=str(other)):
            self.assertEqual(self.inspect()['status'],'stale')
        with patch.dict(os.environ,{'CUSTOM_LEAN_IMPORT_PATH':'new-context'}):
            self.assertEqual(self.inspect()['status'],'stale')

if __name__=='__main__':unittest.main()
