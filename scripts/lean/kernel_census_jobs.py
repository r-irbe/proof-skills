#!/usr/bin/env python3
"""Durable Linux census workers with bounded start/status/cancel controllers."""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import stat
import ctypes
import sys
import time
import uuid

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_census_engine',HERE/'kernel_census.py')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
TERMINAL={'succeeded','failed','cancelled','interrupted','timed_out'}
STATES=TERMINAL|{'queued','running','cancelling'}


def job_root(project):return project.resolve()/'.lake/kernel-census/jobs'


def job_path(project,job_id):
    if not isinstance(job_id,str) or re.fullmatch('[a-f0-9]{32}',job_id) is None:raise ValueError('Invalid census job ID')
    path=job_root(project)/job_id/'job.json'
    current=project.resolve()
    for part in path.relative_to(current).parts:
        current=current/part
        if current.is_symlink():raise ValueError('Symlink census job path refused')
    return path


def read_job(project,job_id):
    path=job_path(project,job_id);data=json.loads(engine.regular_bytes(path,1024*1024))
    if not isinstance(data,dict):raise ValueError('Expected job record object')
    if type(data.get('timeoutMs')) is not int or not 1000<=data['timeoutMs']<=3600000 or type(data.get('rehashImports')) is not bool:raise ValueError('Invalid job options')
    if data.get('schemaVersion')!=1 or data.get('id')!=job_id or Path(data.get('projectRoot','')).resolve()!=project.resolve() or data.get('state') not in STATES:
        raise ValueError('Invalid census job record')
    if re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*',data.get('prefix','')) is None:raise ValueError('Invalid job prefix')
    receipt=Path(data['receiptPath'])
    if not receipt.is_absolute() or not receipt.resolve().is_relative_to(project.resolve()) or receipt.suffix!='.json':raise ValueError('Job receipt escapes project')
    if not isinstance(data.get('token'),str) or re.fullmatch('[a-f0-9]{32}',data['token']) is None:raise ValueError('Invalid job token')
    return data


def write_job(project,data):
    path=job_path(project,data['id'])
    with engine.output_parent(path) as parent:
        with engine.atomic_log(path,parent) as stream:json.dump(data,stream,indent=2);stream.write('\n')


@contextmanager
def state_lock(path):
    import fcntl
    with engine.output_parent(path) as parent:
        fd=os.open(path.name+'.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK,0o600,dir_fd=parent)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):raise ValueError('Expected regular job lock')
            fcntl.flock(fd,fcntl.LOCK_EX)
            yield
        finally:os.close(fd)


def update_job(project,job_id,**changes):
    path=job_path(project,job_id)
    with state_lock(path):
        data=read_job(project,job_id)
        if data['state'] in TERMINAL:return data
        if data.get('cancelRequested') and changes.get('state') in TERMINAL:changes['state']='cancelled'
        data.update(changes);data['updatedAt']=time.time();write_job(project,data)
    return data


def process_identity(pid):
    try:
        root=Path('/proc')/str(pid);text=(root/'stat').read_text();fields=text[text.rfind(')')+2:].split()
        return {'pid':pid,'startTicks':fields[19],'state':fields[0],
                'boot':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                'namespace':os.readlink(root/'ns/pid')}
    except (OSError,IndexError):return None


def worker_matches(data):
    saved=data.get('worker')
    if not isinstance(saved,dict) or type(saved.get('pid')) is not int:return False
    current=process_identity(saved['pid'])
    if current is None or current['state']=='Z':return False
    if any(current.get(key)!=saved.get(key) for key in ['pid','startTicks','boot','namespace']):return False
    try:
        argv=(Path('/proc')/str(saved['pid'])/'cmdline').read_bytes().split(b'\0')
        args=[item.decode() for item in argv if item]
        return (str(HERE/'kernel_census_jobs.py') in args and '--worker' in args
                and args[args.index('--worker')+1]==data['id'] and '--token' in args
                and args[args.index('--token')+1]==data['token'] and '--project-root' in args
                and Path(args[args.index('--project-root')+1]).resolve()==Path(data['projectRoot']).resolve() and os.getpgid(saved['pid'])==saved['pid'])
    except (OSError,ValueError,IndexError,UnicodeError):return False


def execution_busy(project,job_id):
    import fcntl
    path=job_path(project,job_id).with_name('execution.lock')
    if not path.exists():return False
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):raise ValueError('Expected regular execution lock')
        try:fcntl.flock(fd,fcntl.LOCK_SH|fcntl.LOCK_NB);return False
        except BlockingIOError:return True
    finally:os.close(fd)


def recover(project,data):
    if data['state'] in TERMINAL:return data
    if execution_busy(project,data['id']) or worker_matches(data):return data
    own=process_identity(os.getpid());saved=data.get('worker')
    if saved and own and saved.get('boot')!=own['boot']:
        return update_job(project,data['id'],state='interrupted',finishedAt=time.time(),issue='Worker belongs to a previous boot')
    if saved and own and saved.get('namespace')!=own['namespace']:
        return dict(data,identityWarning='Worker identity belongs to a different PID namespace')
    return update_job(project,data['id'],state='cancelled' if data.get('cancelRequested') else 'interrupted',finishedAt=time.time(),issue='Worker is no longer running')


def progress(data):
    receipt=Path(data['receiptPath']);pid=data.get('enginePid');phase=data['state'];tail=''
    if data['state']=='running' and pid:
        build=receipt.with_suffix('.build.log').with_name(receipt.with_suffix('.build.log').name+'.tmp-'+str(pid))
        replay=receipt.with_suffix('.replay.log').with_name(receipt.with_suffix('.replay.log').name+'.tmp-'+str(pid))
        current=build if build.exists() else replay if replay.exists() else None
        phase='building' if current==build else 'kernel-replay' if current==replay else 'receipt-check' if receipt.exists() else 'snapshotting'
        if current:
            try:
                fd=os.open(current,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW)
                try:
                    size=os.fstat(fd).st_size;os.lseek(fd,max(0,size-4096),os.SEEK_SET);tail=os.read(fd,4096).decode(errors='replace')
                finally:os.close(fd)
            except OSError:pass
    return {'phase':phase,'logTail':tail}


def status_job(project,prefix,job_id,rehash_imports=False):
    data=read_job(project,job_id)
    if data['prefix']!=prefix:raise ValueError('Job prefix does not match request')
    data=recover(project,data)
    receipt=Path(data['receiptPath'])
    if data['state']=='succeeded':
        try:
            raw=engine.regular_bytes(receipt)
            if hashlib.sha256(raw).hexdigest()!=data.get('receiptSha256'):
                result=engine.result_record('unverified',receipt,['Job receipt was superseded'])
            else:
                result=engine.inspect_receipt(project,prefix,receipt,rehash_imports=rehash_imports)
                if result.get('gateEligible') and result.get('receiptSha256')!=data.get('receiptSha256'):
                    result=engine.result_record('unverified',receipt,['Job receipt was superseded during validation'])
        except (OSError,ValueError) as error:result=engine.result_record('unverified',receipt,[str(error)])
    else:
        result=engine.result_record(data['state'],receipt,[data['issue']] if data.get('issue') else [])
    result['job']={key:data.get(key) for key in ['id','state','createdAt','updatedAt','startedAt','finishedAt','issue']}
    result['job'].update(progress(data))
    if data.get('identityWarning'):result['reasons'].append(data['identityWarning'])
    return result


def validate_start(project,prefix,receipt,timeout_ms):
    if sys.platform!='linux' or not Path('/proc/self/stat').exists():raise ValueError('Durable census jobs currently require Linux/proc')
    if not project.is_dir() or not (project/'lean-toolchain').is_file():raise ValueError('Expected a Lean project')
    if re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*',prefix) is None:raise ValueError('Invalid module prefix')
    if not receipt.is_absolute() or not receipt.resolve().is_relative_to(project.resolve()) or receipt.suffix!='.json' or receipt.name in engine.CONFIG_FILES+('package.json','package-lock.json'):raise ValueError('Invalid confined job receipt')
    if type(timeout_ms) is not int or not 1000<=timeout_ms<=3600000:raise ValueError('Invalid worker timeout')
    if receipt.exists():
        old=json.loads(engine.regular_bytes(receipt))
        if old.get('mutableCache') is not True:raise ValueError('Refusing frozen or unrelated receipt output')


def start_job(project,prefix,receipt,timeout_ms=1200000,rehash_imports=False):
    project=project.resolve();receipt=receipt.absolute();validate_start(project,prefix,receipt,timeout_ms)
    pointer=job_root(project)/('active-'+hashlib.sha256(str(receipt).encode()).hexdigest()+'.json')
    with state_lock(pointer):
        if pointer.exists():
            prior=json.loads(engine.regular_bytes(pointer,16384));old=recover(project,read_job(project,prior['jobId']))
            if old['state'] not in TERMINAL:
                result=status_job(project,prefix,old['id']);result['deduplicated']=True;return result
        job_id=uuid.uuid4().hex;token=uuid.uuid4().hex;now=time.time()
        data={'schemaVersion':1,'id':job_id,'token':token,'projectRoot':str(project),'prefix':prefix,'receiptPath':str(receipt),
              'state':'queued','createdAt':now,'updatedAt':now,'timeoutMs':timeout_ms,'rehashImports':rehash_imports,'worker':None}
        write_job(project,data)
        with engine.output_parent(pointer) as parent:
            with engine.atomic_log(pointer,parent) as stream:json.dump({'jobId':job_id},stream)
        log=job_path(project,job_id).with_name('worker.log')
        fd=os.open(log,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
        try:
            argv=[sys.executable,str(HERE/'kernel_census_jobs.py'),'--project-root',str(project),'--worker',job_id,'--token',token]
            pid=os.posix_spawn(sys.executable,argv,os.environ,setsid=True,file_actions=[
                (os.POSIX_SPAWN_OPEN,0,os.devnull,os.O_RDONLY,0),
                (os.POSIX_SPAWN_DUP2,fd,1),(os.POSIX_SPAWN_DUP2,fd,2),(os.POSIX_SPAWN_CLOSE,fd)])
        except OSError as error:
            update_job(project,job_id,state='failed',issue=str(error),finishedAt=time.time());raise
        finally:os.close(fd)
        identity=process_identity(pid)
        with state_lock(job_path(project,job_id)):
            data=read_job(project,job_id)
            if data.get('worker') is None:data['worker']=identity;write_job(project,data)
    return status_job(project,prefix,job_id)


def cancel_job(project,prefix,job_id):
    data=read_job(project,job_id)
    if data['prefix']!=prefix:raise ValueError('Job prefix does not match request')
    data=recover(project,data)
    if data['state'] in TERMINAL:return status_job(project,prefix,job_id)
    if not worker_matches(data):
        result=engine.result_record('unverified',Path(data['receiptPath']),['Worker identity cannot be safely signalled']);result['job']={'id':job_id,'state':data['state']};return result
    data=update_job(project,job_id,state='cancelling',cancelRequested=True)
    if data['state'] in TERMINAL:return status_job(project,prefix,job_id)
    pid=data['worker']['pid'];fd=os.pidfd_open(pid) if hasattr(os,'pidfd_open') else None
    try:
        if worker_matches(data):os.killpg(pid,signal.SIGTERM)
        if fd is not None:select.select([fd],[],[],1)
        else:time.sleep(.1)
        if worker_matches(data):os.killpg(pid,signal.SIGKILL)
        if fd is not None:select.select([fd],[],[],1)
    finally:
        if fd is not None:os.close(fd)
    if worker_matches(data):return status_job(project,prefix,job_id)
    update_job(project,job_id,state='cancelled',finishedAt=time.time(),issue='Cancelled explicitly')
    return status_job(project,prefix,job_id)


def runner(project,job_id,token,parent,completion_fd):
    # Keep this process alive until the supervisor kills the job group. If the
    # supervisor dies first, Linux delivers SIGUSR1 and the whole group stops.
    # Conversely, EOF on this runner's completion pipe lets the supervisor
    # detect runner death. No one-process crash leaves producer descendants.
    def parent_gone(_signal,_frame):os.killpg(os.getpgrp(),signal.SIGKILL)
    signal.signal(signal.SIGUSR1,parent_gone)
    if ctypes.CDLL(None,use_errno=True).prctl(1,signal.SIGUSR1,0,0,0)!=0:raise OSError(ctypes.get_errno(),'Cannot fence runner parent lifetime')
    if os.getppid()!=parent or os.getpgid(0)!=parent:parent_gone(None,None)
    data=read_job(project,job_id)
    if data['token']!=token:parent_gone(None,None)
    argv=['--project-root',str(project),'--prefix',data['prefix'],'--receipt',data['receiptPath'],'--mode','rebuild']
    if data['rehashImports']:argv.append('--rehash-imports')
    code=engine.main(argv)
    sys.stdout.flush();sys.stderr.flush()
    os.write(completion_fd,str(code).encode());os.close(completion_fd)
    while True:signal.pause()


def worker(project,job_id,token):
    path=job_path(project,job_id)
    def stop(_signal,_frame):os.killpg(os.getpid(),signal.SIGKILL)
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    child=None;notify_read=None
    with engine.receipt_lock(path.with_name('execution')):
        try:
            data=read_job(project,job_id)
            if data['token']!=token or data['state'] not in ('queued','running'):return
            update_job(project,job_id,state='running',worker=process_identity(os.getpid()),startedAt=time.time())
            argv=[sys.executable,str(HERE/'kernel_census_jobs.py'),'--project-root',str(project),'--runner',job_id,'--token',token,'--parent',str(os.getpid())]
            stdout_path=path.with_name('producer.stdout');stderr_path=path.with_name('producer.stderr')
            out_fd=os.open(stdout_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
            err_fd=os.open(stderr_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
            notify_read,notify_write=os.pipe();argv.extend(['--completion-fd',str(notify_write)])
            try:child=subprocess.Popen(argv,cwd=project,stdin=subprocess.DEVNULL,stdout=out_fd,stderr=err_fd,pass_fds=(notify_write,))
            finally:os.close(out_fd);os.close(err_fd);os.close(notify_write)
            update_job(project,job_id,enginePid=child.pid)
            ready,_,_=select.select([notify_read],[],[],data['timeoutMs']/1000)
            if not ready:
                update_job(project,job_id,state='timed_out',finishedAt=time.time(),issue='Worker timeout expired');return
            completion=os.read(notify_read,64)
            producer_code=int(completion) if completion else None
            stdout=engine.regular_bytes(stdout_path,1024*1024);stderr=engine.regular_bytes(stderr_path,1024*1024)
            try:result=json.loads(stdout)
            except (ValueError,UnicodeError):result={}
            if producer_code==0 and result.get('status')=='verified' and result.get('gateEligible') is True:
                raw=engine.regular_bytes(Path(data['receiptPath']));hashed=hashlib.sha256(raw).hexdigest()
                if hashed!=result.get('receiptSha256'):raise ValueError('Producer receipt identity mismatch')
                update_job(project,job_id,state='succeeded',receiptSha256=hashed,finishedAt=time.time())
            else:update_job(project,job_id,state='failed',finishedAt=time.time(),issue=(stderr.decode(errors='replace') or str(result))[-4096:])
        except Exception as error:
            try:update_job(project,job_id,state='failed',finishedAt=time.time(),issue=str(error))
            except Exception:pass
        finally:
            if notify_read is not None:os.close(notify_read)
            if child is not None:os.killpg(os.getpid(),signal.SIGKILL)


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--project-root',type=Path,required=True);parser.add_argument('--prefix');parser.add_argument('--receipt',type=Path)
    parser.add_argument('--mode',choices=['start','status','cancel']);parser.add_argument('--job-id');parser.add_argument('--timeout-ms',type=int,default=1200000)
    parser.add_argument('--rehash-imports',action='store_true');parser.add_argument('--worker');parser.add_argument('--runner');parser.add_argument('--parent',type=int);parser.add_argument('--completion-fd',type=int);parser.add_argument('--token')
    args=parser.parse_args()
    if args.runner:runner(args.project_root.resolve(),args.runner,args.token,args.parent,args.completion_fd);return 0
    if args.worker:worker(args.project_root.resolve(),args.worker,args.token);return 0
    try:
        if args.mode=='start':result=start_job(args.project_root,args.prefix,args.receipt,timeout_ms=args.timeout_ms,rehash_imports=args.rehash_imports)
        elif args.mode=='status':result=status_job(args.project_root,args.prefix,args.job_id,rehash_imports=args.rehash_imports)
        elif args.mode=='cancel':result=cancel_job(args.project_root,args.prefix,args.job_id)
        else:raise ValueError('Missing job mode')
    except (OSError,ValueError,RuntimeError,KeyError,TypeError) as error:result=engine.result_record('unverified',args.receipt or args.project_root,[str(error)])
    print(json.dumps(result));return 0 if result.get('status') not in ('unverified','failed','interrupted','timed_out') else 2

if __name__=='__main__':raise SystemExit(main())
