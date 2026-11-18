import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='census-jobs-');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.project=self.base/'project';self.project.mkdir();self.toolkit=self.base/'toolkit';self.toolkit.mkdir()
        shutil.copy2(ROOT/'scripts/lean/kernel_census_jobs.py',self.toolkit/'kernel_census_jobs.py')
        original=(ROOT/'scripts/lean/kernel_census.py').read_text().split("if __name__=='__main__'")[0]
        fake='''
def inspect_receipt(project,prefix,receipt,rehash_imports=False):
    raw=receipt.read_bytes();data=json.loads(raw)
    if not data.get('fixtureProof'):return result_record('unverified',receipt,['fixture receipt invalid'])
    return dict(status='verified',gateEligible=True,evidenceKind='compiled-kernel-replay',receiptPath=str(receipt),receiptSha256=hashlib.sha256(raw).hexdigest(),counts={})

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path);p.add_argument('--prefix');p.add_argument('--receipt',type=Path);p.add_argument('--mode');p.add_argument('--rehash-imports',action='store_true');a=p.parse_args()
    mode=(a.project_root/'behavior').read_text()
    with (a.project_root/'executions').open('a') as stream:stream.write('run\\n')
    if mode=='hang':
        child="import signal,time,pathlib;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(2);pathlib.Path(%r).write_text('escaped')" % str(a.project_root/'orphan')
        subprocess.Popen([sys.executable,'-c',child]);time.sleep(30)
    if mode=='fail':raise SystemExit(2)
    time.sleep(.3)
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps({'fixtureProof':True}))
    print(json.dumps(inspect_receipt(a.project_root,a.prefix,a.receipt)))
    return 0
'''
        fake=fake.replace("if __name__=='__main__':",'def main(argv=None):').replace('a=p.parse_args()','a=p.parse_args(argv)').replace('subprocess.Popen([sys.executable', '_descendant=subprocess.Popen([sys.executable')
        (self.toolkit/'kernel_census.py').write_text(original+fake)
        (self.project/'behavior').write_text('success');(self.project/'lean-toolchain').write_text('fixture')
        self.receipt=self.project/'.lake/kernel-census/Fixture.json'
        spec=importlib.util.spec_from_file_location('jobs_fixture',self.toolkit/'kernel_census_jobs.py');self.jobs=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.jobs)
        self.ids=[];self.addCleanup(self.cleanup_jobs)

    def cleanup_jobs(self):
        for job in self.ids:
            try:self.jobs.cancel_job(self.project,'Fixture',job)
            except Exception:pass

    def start(self,timeout_ms=10000):
        result=self.jobs.start_job(self.project,'Fixture',self.receipt,timeout_ms=timeout_ms);self.ids.append(result['job']['id']);return result

    def settled(self,job):
        until=time.monotonic()+8
        while time.monotonic()<until:
            result=self.jobs.status_job(self.project,'Fixture',job)
            if result['job']['state'] not in ('queued','running','cancelling'):return result
            time.sleep(.02)
        self.fail('job did not settle')

    def test_start_returns_quickly_deduplicates_and_survives_controller_reload(self):
        (self.project/'behavior').write_text('hang');start=time.monotonic();first=self.start();self.assertLess(time.monotonic()-start,2)
        second=self.start();self.assertEqual(first['job']['id'],second['job']['id']);self.assertFalse(second['gateEligible'])
        again=self.jobs.status_job(self.project,'Fixture',first['job']['id']);self.assertIn(again['job']['state'],('queued','running'))

    def test_success_binds_exact_receipt_and_superseded_receipt_refuses(self):
        first=self.start();result=self.settled(first['job']['id']);self.assertEqual(result['status'],'verified');self.assertTrue(result['gateEligible'])
        self.receipt.write_text(json.dumps({'fixtureProof':True,'other':'receipt'}))
        result=self.jobs.status_job(self.project,'Fixture',first['job']['id']);self.assertFalse(result['gateEligible']);self.assertIn('supersed',str(result).lower())

    def wait_started(self):
        until=time.monotonic()+3
        while time.monotonic()<until:
            if (self.project/'executions').exists():return
            time.sleep(.01)
        self.fail('producer did not start')

    def test_cancel_kills_descendants_and_is_idempotent(self):
        (self.project/'behavior').write_text('hang');first=self.start();job=first['job']['id'];self.wait_started()
        result=self.jobs.cancel_job(self.project,'Fixture',job);self.assertFalse(result['gateEligible']);self.assertEqual(result['job']['state'],'cancelled')
        time.sleep(2.2);self.assertFalse((self.project/'orphan').exists());self.assertEqual(self.jobs.cancel_job(self.project,'Fixture',job)['job']['state'],'cancelled')

    def test_dead_worker_recovers_as_interrupted_not_verified(self):
        (self.project/'behavior').write_text('hang');job=self.start()['job']['id'];self.wait_started()
        data=self.jobs.read_job(self.project,job);os.kill(data['worker']['pid'],signal.SIGKILL)
        result=self.settled(job);self.assertEqual(result['job']['state'],'interrupted');self.assertFalse(result['gateEligible'])
        time.sleep(2.2);self.assertFalse((self.project/'orphan').exists(),'Producer descendant survived worker death')

    def test_failure_and_timeout_are_not_kernel_success(self):
        for behavior in ['fail','hang']:
            (self.project/'behavior').write_text(behavior);job=self.start(timeout_ms=1000)['job']['id'];result=self.settled(job)
            self.assertIn(result['job']['state'],('failed','timed_out'));self.assertFalse(result['gateEligible'])

    def test_invalid_id_and_torn_state_refuse(self):
        with self.assertRaises(ValueError):self.jobs.status_job(self.project,'Fixture','../escape')
        job=self.start()['job']['id'];self.settled(job);path=self.project/'.lake/kernel-census/jobs'/job/'job.json';path.write_text('{')
        with self.assertRaises((ValueError,RuntimeError)):self.jobs.status_job(self.project,'Fixture',job)

    def test_pid_reuse_and_namespace_mismatch_refuse_cancellation(self):
        (self.project/'behavior').write_text('hang');job=self.start()['job']['id'];self.wait_started()
        original=self.jobs.read_job(self.project,job)
        for field,value in [('startTicks','0'),('namespace','other-namespace')]:
            altered=json.loads(json.dumps(original));altered['worker'][field]=value;self.jobs.write_job(self.project,altered)
            result=self.jobs.cancel_job(self.project,'Fixture',job);self.assertEqual(result['status'],'unverified')
            self.jobs.write_job(self.project,original)
        self.assertTrue(self.jobs.worker_matches(original))

    def test_wrong_project_cannot_signal_another_projects_worker(self):
        (self.project/'behavior').write_text('hang');job=self.start()['job']['id'];self.wait_started();original=self.jobs.read_job(self.project,job)
        other=self.base/'other';other.mkdir();altered=json.loads(json.dumps(original));altered['projectRoot']=str(other);altered['receiptPath']=str(other/'receipt.json');self.jobs.write_job(other,altered)
        result=self.jobs.cancel_job(other,'Fixture',job);self.assertFalse(result['gateEligible']);self.assertTrue(self.jobs.worker_matches(original))

    def test_terminal_states_are_immutable_and_missing_receipt_is_unknown(self):
        job=self.start()['job']['id'];self.assertEqual(self.settled(job)['status'],'verified')
        self.jobs.update_job(self.project,job,state='interrupted');self.assertEqual(self.jobs.read_job(self.project,job)['state'],'succeeded')
        self.receipt.unlink();result=self.jobs.status_job(self.project,'Fixture',job);self.assertEqual(result['status'],'unverified');self.assertEqual(result['job']['id'],job)


    def test_receipt_replacement_during_validation_never_rebinds_job(self):
        job=self.start()['job']['id'];self.assertEqual(self.settled(job)['status'],'verified')
        inspect=self.jobs.engine.inspect_receipt
        def replaced(*args,**kwargs):
            self.receipt.write_text(json.dumps({'fixtureProof':True,'replacement':True}))
            return inspect(*args,**kwargs)
        with patch.object(self.jobs.engine,'inspect_receipt',side_effect=replaced):
            result=self.jobs.status_job(self.project,'Fixture',job)
        self.assertEqual(result['status'],'unverified');self.assertFalse(result['gateEligible'])

    def test_previous_boot_recovers_even_when_namespace_changed(self):
        job=self.start()['job']['id'];self.settled(job);data=self.jobs.read_job(self.project,job)
        data['state']='running';data['worker']['boot']='previous-boot';data['worker']['namespace']='previous-namespace';self.jobs.write_job(self.project,data)
        result=self.jobs.status_job(self.project,'Fixture',job);self.assertEqual(result['job']['state'],'interrupted')


    def test_concurrent_subprocess_starts_share_one_job_and_execution(self):
        (self.project/'behavior').write_text('hang')
        barrier=self.base/'release-controllers'
        controllers=[]
        launcher="""
import pathlib,runpy,sys,time
barrier=pathlib.Path(sys.argv[1]);ready=pathlib.Path(sys.argv[2]);script=sys.argv[3]
arguments=sys.argv[4:];ready.write_text('ready');deadline=time.monotonic()+5
while not barrier.exists():
    if time.monotonic()>deadline:raise SystemExit('controller barrier timeout')
    time.sleep(.005)
sys.argv=[script]+arguments
runpy.run_path(script,run_name='__main__')
"""
        def reap(process):
            if process.poll() is None:process.kill()
            process.wait(timeout=5)
        for index in range(2):
            ready=self.base/('controller-ready-'+str(index))
            argv=[sys.executable,'-c',launcher,str(barrier),str(ready),
                  str(self.toolkit/'kernel_census_jobs.py'),'--project-root',str(self.project),
                  '--prefix','Fixture','--receipt',str(self.receipt),'--mode','start','--timeout-ms','10000']
            process=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            controllers.append((process,ready));self.addCleanup(reap,process)
        deadline=time.monotonic()+5
        while not all(ready.exists() for _,ready in controllers):
            if time.monotonic()>deadline:self.fail('separate controllers did not reach the start barrier')
            time.sleep(.005)
        barrier.write_text('release')
        results=[]
        for process,_ in controllers:
            stdout,stderr=process.communicate(timeout=10)
            self.assertEqual(process.returncode,0,stderr+'\n'+stdout)
            result=json.loads(stdout);self.ids.append(result['job']['id']);results.append(result)
        self.assertEqual(results[0]['job']['id'],results[1]['job']['id'])
        self.assertEqual(sum(result.get('deduplicated',False) is True for result in results),1)
        self.wait_started()
        self.assertEqual((self.project/'executions').read_text(),'run\n')
        self.assertEqual(len(list(self.jobs.job_root(self.project).glob('*/job.json'))),1)

    def test_progress_log_tail_is_bounded_for_build_and_replay(self):
        self.receipt.parent.mkdir(parents=True)
        content=b'old-line\n'*2000+b'latest-progress\n'
        for suffix,phase in [('.build.log','building'),('.replay.log','kernel-replay')]:
            with self.subTest(phase=phase):
                log=self.receipt.with_suffix(suffix).with_name(self.receipt.with_suffix(suffix).name+'.tmp-12345')
                log.write_bytes(content)
                result=self.jobs.progress({'receiptPath':str(self.receipt),'state':'running','enginePid':12345})
                self.assertEqual(result['phase'],phase)
                self.assertEqual(result['logTail'],content[-4096:].decode())
                self.assertLessEqual(len(result['logTail']),4096)
                log.unlink()

    def test_progress_refuses_symlink_log_without_disclosing_target(self):
        self.receipt.parent.mkdir(parents=True)
        outside=self.base/'unrelated-log';outside.write_text('unrelated-private-log-contents')
        log=self.receipt.with_suffix('.build.log').with_name(self.receipt.with_suffix('.build.log').name+'.tmp-12345')
        log.symlink_to(outside)
        start=time.monotonic()
        result=self.jobs.progress({'receiptPath':str(self.receipt),'state':'running','enginePid':12345})
        self.assertLess(time.monotonic()-start,1)
        self.assertEqual(result['logTail'],'')
        self.assertNotIn('unrelated-private-log-contents',json.dumps(result))
        self.assertEqual(outside.read_text(),'unrelated-private-log-contents')


if __name__=='__main__':unittest.main()
