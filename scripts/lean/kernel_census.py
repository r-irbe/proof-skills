#!/usr/bin/env python3
"""Check or rebuild a compiled census for an explicit source-backed module set."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import shutil
import stat
import sys
import time
import signal
from contextlib import contextmanager

HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(regular_bytes(path, 512*1024*1024)).hexdigest()


def source_files(project, prefix):
    if not re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*',prefix):
        raise ValueError('Invalid module prefix')
    project=project.resolve();stem=Path(*prefix.split('.'));directory=project/stem;sources=[]
    root_source=directory.with_suffix('.lean')
    if root_source.exists() or root_source.is_symlink():sources.append(root_source)
    def walk(folder):
        if folder.is_symlink():raise ValueError('Symlink source directory is not admitted')
        for item in sorted(folder.iterdir()):
            if item.name.startswith('.'):continue
            if item.is_dir():walk(item)
            elif item.suffix=='.lean':sources.append(item)
    if directory.is_dir():walk(directory)
    if not sources:raise ValueError('No source modules in requested scope')
    for source in sources:
        if not stat.S_ISREG(source.lstat().st_mode) or not source.resolve().is_relative_to(project):
            raise ValueError('Expected confined regular Lean source')
    return sorted(sources)


def select_modules(project, lib, prefix):
    sources=source_files(project,prefix)
    modules={'.'.join(p.relative_to(project).with_suffix('').parts):p for p in sources}
    missing=[n for n in modules if not (lib/Path(*n.split('.'))).with_suffix('.olean').is_file()]
    if missing:raise ValueError('Missing compiled modules after build: '+', '.join(missing))
    stale=[];outside=[]
    for p in sorted(lib.rglob('*.olean')):
        name='.'.join(p.relative_to(lib).with_suffix('').parts)
        if name in modules:continue
        (stale if name==prefix or name.startswith(prefix+'.') else outside).append(str(p.relative_to(lib)))
    return {'modules':sorted(modules),'sources':{str(p.relative_to(project)):digest(p) for p in sorted(sources)},'excludedStale':stale,'excludedOutsidePrefix':outside}

def artifacts(lib, modules):
    result={}
    for name in modules:
        base=(lib/Path(*name.split('.'))).with_suffix('.olean')
        for p in [base,Path(str(base)+'.server'),Path(str(base)+'.private')]:
            if p.is_file():result[str(p.relative_to(lib))]=digest(p)
    return result

def validate_kernel(kernel, modules):
    counts=['modules','constants','theorems','definitions','declaredAxioms','eligible','replayed',
            'axiomAudited','skippedUnsafe','skippedPartial','privateTheorems','loadedParts','disallowedAxiomUses']
    if any(type(kernel.get(k)) is not int or kernel[k]<0 for k in counts):raise ValueError('Invalid kernel count')
    if kernel['modules']!=len(modules) or not modules:raise ValueError('Module coverage mismatch')
    if not len(modules)<=kernel['loadedParts']<=4*len(modules):raise ValueError('Invalid loaded module parts')
    if kernel['replayed']!=kernel['eligible'] or kernel['axiomAudited']!=kernel['eligible']:raise ValueError('Incomplete replay/axiom coverage')
    if kernel['eligible']+kernel['skippedUnsafe']+kernel['skippedPartial']!=kernel['constants']:raise ValueError('Invalid replay partition')
    if kernel['privateTheorems']>kernel['theorems'] or kernel['theorems']>kernel['eligible']:raise ValueError('Invalid theorem partition')
    if kernel['theorems']+kernel['definitions']+kernel['declaredAxioms']>kernel['constants']:raise ValueError('Invalid declaration partition')
    for field,count in [('constantNames','constants'),('theoremNames','theorems')]:
        names=kernel.get(field)
        if not isinstance(names,list) or any(not isinstance(n,str) or not n for n in names):raise ValueError('Invalid name manifest')
        if len(names)!=kernel[count] or len(set(names))!=len(names):raise ValueError('Incomplete/duplicate name manifest')
    if not set(kernel['theoremNames'])<=set(kernel['constantNames']):raise ValueError('Theorem outside constant manifest')
    for field in ['badAxiomUses','distinctAxioms','repeatedIdenticalTheorems']:
        if not isinstance(kernel.get(field),list) or any(not isinstance(v,str) for v in kernel[field]):raise ValueError('Invalid axiom/repeated-theorem manifest')
    if len(kernel['badAxiomUses'])!=kernel['disallowedAxiomUses']:raise ValueError('Invalid forbidden axiom count')
    if len(set(kernel['distinctAxioms']))!=len(kernel['distinctAxioms']):raise ValueError('Duplicate axiom footprint')
    if not set(kernel['repeatedIdenticalTheorems'])<=set(kernel['theoremNames']):raise ValueError('Invalid repeated-theorem manifest')


CONFIG_FILES = ('lean-toolchain', 'lakefile.lean', 'lakefile.toml', 'lake-manifest.json')
MAX_RECEIPT_BYTES = 64 * 1024 * 1024


def ambient_environment():
    return {key: os.environ.get(key) for key in
            ('PATH', 'LEAN_PATH', 'LEAN_SYSROOT', 'ELAN_TOOLCHAIN', 'ELAN_HOME', 'LAKE_HOME')}


def environment_fingerprint():
    # Transport/session variables are not admitted build inputs. Custom semantic
    # environment variables are hashed without recording their secret values.
    volatile={'_','SHLVL','PWD','OLDPWD'}
    values={k:v for k,v in os.environ.items() if k not in volatile and not k.startswith('CODEX_')}
    return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()


def resolve_compiler(project):
    if shutil.which('elan'):
        result=command(['elan','which','lean'],cwd=project,capture_output=True,text=True,timeout=5,check=True)
        return result.stdout.strip()
    found=shutil.which('lean')
    if not found:raise ValueError('Cannot resolve active compiler')
    return found


def config_hashes(project):
    return {name: digest(project/name) for name in CONFIG_FILES if (project/name).is_file()}


def tool_hashes():
    return {name: digest(HERE/name) for name in ('kernel_census.py', 'kernel_census.lean')}


def regular_bytes(path, limit=MAX_RECEIPT_BYTES):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_NOFOLLOW', 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError('Expected bounded regular file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError('Receipt exceeds size limit')
        return data
    finally:
        os.close(fd)


def confined(project, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('Manifest path escapes project')
    candidate = project/relative
    if not candidate.resolve().is_relative_to(project.resolve()):
        raise ValueError('Manifest path escapes project')
    return candidate


def context_hashes(context, cache=None):
    roots=context['libraryRoots']
    if not isinstance(roots,list) or not roots or len(set(roots))!=len(roots) or any(not isinstance(r,str) or not Path(r).is_absolute() for r in roots):
        raise ValueError('Invalid or empty compiled import context')
    result = {'libraryOrder':roots}
    compiler = Path(context['compilerPath'])
    if not compiler.is_absolute():raise ValueError('Invalid compiler path')
    result['compiler'] = {'path': str(compiler.resolve()), 'sha256': hashlib.sha256(regular_bytes(compiler, 512*1024*1024)).hexdigest()}
    for raw in context['libraryRoots']:
        root = Path(raw)
        if not root.is_dir():
            result['library:'+raw] = None
            continue
        entries = {}
        old_entries=(cache or {}).get('library:'+raw,{}) or {}
        old_entries=old_entries.get('files',{})
        seen = set()
        def walk(directory):
            resolved = directory.resolve()
            if resolved in seen:
                raise ValueError('Cyclic or aliased compiled dependency directory')
            seen.add(resolved)
            for item in sorted(directory.iterdir()):
                if item.is_dir():
                    walk(item)
                elif item.name.endswith(('.olean', '.olean.server', '.olean.private')):
                    relative=str(item.relative_to(root));info=item.lstat()
                    if not stat.S_ISREG(info.st_mode):raise ValueError('Expected regular compiled import')
                    identity={'device':info.st_dev,'inode':info.st_ino,'size':info.st_size,
                              'mtimeNs':info.st_mtime_ns,'ctimeNs':info.st_ctime_ns}
                    resolved=str(item.resolve());previous=old_entries.get(relative,{})
                    reusable=(previous.get('path')==resolved and previous.get('stat')==identity
                              and info.st_ino>0 and 2_000_000_000<=time.time_ns()-info.st_ctime_ns
                              and isinstance(previous.get('sha256'),str)
                              and re.fullmatch('[a-f0-9]{64}',previous['sha256']) is not None)
                    hashed=previous['sha256'] if reusable else digest(item)
                    final=item.lstat()
                    if (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)!=(final.st_dev,final.st_ino,final.st_size,final.st_mtime_ns,final.st_ctime_ns):
                        raise ValueError('Compiled import changed during hashing')
                    entries[relative]={'path':resolved,'sha256':hashed,'stat':identity}
        walk(root)
        result['library:'+raw] = {'path':str(root.resolve()),'files':entries}
    return result


def command(argv, **kwargs):
    prefix = ['rtk', 'proxy'] if shutil.which('rtk') else []
    return subprocess.run(prefix + argv, **kwargs)


def capture_context(project):
    code = 'import json,os,shutil; print(json.dumps({"compilerPath":shutil.which("lean"),"leanPath":os.environ.get("LEAN_PATH","")}))'
    probe = command(['lake', 'env', sys.executable, '-c', code], cwd=project, capture_output=True, text=True, check=True)
    data = json.loads(probe.stdout)
    if not data['compilerPath']:
        raise ValueError('Compiler unavailable')
    compiler = Path(data['compilerPath'])
    roots = [str((project/p).absolute()) if not Path(p).is_absolute() else str(Path(p))
             for p in data['leanPath'].split(os.pathsep) if p]
    roots.append(str(compiler.parent.parent/'lib/lean'))
    return {'compilerPath':str(compiler), 'libraryRoots':list(dict.fromkeys(roots)), 'environment':ambient_environment(), 'environmentFingerprint':environment_fingerprint()}


def result_record(status, receipt, reasons, data=None):
    output = {'status':status, 'evidenceKind':'compiled-kernel-replay',
              'gateEligible':status == 'verified', 'receiptPath':str(receipt), 'reasons':reasons,
              'scope':{'externalLibrariesReplayed':False, 'discardedExamplesIncluded':False,
                       'unsafeAndPartialIncluded':False}}
    if data:
        output['prefix'] = data.get('prefix')
        output['counts'] = {k:v for k,v in data.get('kernel', {}).items()
                            if k not in ('constantNames','theoremNames','badAxiomUses','repeatedIdenticalTheorems')}
    return output


def inspect_receipt(project, prefix, receipt, rehash_imports=False):
    project = project.resolve()
    if not receipt.exists():
        return result_record('missing', receipt, ['No receipt; mode=rebuild is required'])
    try:
        raw = regular_bytes(receipt)
        data = json.loads(raw)
        if data.get('schemaVersion') != 2:
            raise ValueError('Legacy/unsupported receipt; rebuild required')
        if Path(data['projectRoot']).resolve() != project or data['prefix'] != prefix:
            raise ValueError('Receipt project/prefix does not match request')
        manifest = data['manifest']
        if not isinstance(manifest['modules'],list) or any(not isinstance(n,str) for n in manifest['modules']):raise ValueError('Invalid module manifest')
        expected_bases={str(Path(*name.split('.')).with_suffix('.olean')) for name in manifest['modules']}
        if not expected_bases<=set(data['artifactHashes']):raise ValueError('Missing base compiled artifact coverage')
        context=data['context']
        required_roots={str(project/'.lake/build/lib/lean'),str(Path(context['compilerPath']).parent.parent/'lib/lean')}
        if not required_roots<=set(context['libraryRoots']):raise ValueError('Incomplete compiler/project import roots')
        for name in manifest['sources']:
            confined(project, name)
        for name in data['artifactHashes']:
            confined(project/'.lake/build/lib/lean', name)
        validate_kernel(data['kernel'], manifest['modules'])
        kernel = data['kernel']
        if any(type(data.get(key)) is not int or data[key] != 0 for key in ('buildExitCode','replayExitCode')):
            raise ValueError('Receipt records failed/incomplete build or replay')
        if kernel['declaredAxioms'] != 0 or kernel['disallowedAxiomUses'] != 0 or kernel['badAxiomUses']:
            raise ValueError('Receipt records disallowed axioms')
        if set(kernel['distinctAxioms']) - {'propext','Classical.choice','Quot.sound'}:
            raise ValueError('Receipt records forbidden axiom footprint')
        reasons = []
        sources = {str(p.relative_to(project)):digest(p) for p in source_files(project,prefix)}
        expected_modules = sorted('.'.join(Path(p).with_suffix('').parts) for p in sources)
        if manifest['modules'] != expected_modules or len(set(manifest['modules'])) != len(manifest['modules']):
            reasons.append('Source/module set changed')
        if manifest['sources'] != sources: reasons.append('Source contents changed')
        if data['artifactHashes'] != artifacts(project/'.lake/build/lib/lean',expected_modules):
            reasons.append('Compiled artifacts changed')
        if data['configHashes'] != config_hashes(project): reasons.append('Compiler/project configuration changed')
        if data['toolHashes'] != tool_hashes(): reasons.append('Census adapter/helper changed')
        if data['context']['environment'] != ambient_environment() or context['environmentFingerprint']!=environment_fingerprint(): reasons.append('Compiler/import environment changed')
        if Path(resolve_compiler(project)).resolve()!=Path(context['compilerPath']).resolve():reasons.append('Active compiler resolution changed')
        if reasons:
            return result_record('stale',receipt,reasons,data)
        if data['contextHashes'] != context_hashes(data['context'],None if rehash_imports else data['contextHashes']): reasons.append('Compiler/import artifacts changed')
        if {str(p.relative_to(project)):digest(p) for p in source_files(project,prefix)} != sources:
            reasons.append('Sources changed during receipt check')
        if regular_bytes(receipt) != raw: reasons.append('Receipt changed during check')
        result=result_record('stale' if reasons else 'verified',receipt,reasons,data)
        result['importHashPolicy']='full-rehash' if rehash_imports else 'verified-digest-plus-file-identity'
        result['receiptSha256']=hashlib.sha256(raw).hexdigest()
        result['contextFingerprint']=hashlib.sha256(json.dumps(data['contextHashes'],sort_keys=True).encode()).hexdigest()
        return result
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        return result_record('unverified',receipt,[str(error)])


@contextmanager
def output_parent(output):
    if os.name!='posix':raise ValueError('Secure kernel census rebuild currently requires POSIX')
    absolute=output.absolute();fd=os.open(absolute.anchor,os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in absolute.parent.parts[1:]:
            try:os.mkdir(part,mode=0o700,dir_fd=fd)
            except FileExistsError:pass
            next_fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|getattr(os,'O_NOFOLLOW',0),dir_fd=fd)
            os.close(fd);fd=next_fd
        yield fd
    finally:os.close(fd)


@contextmanager
def receipt_lock(output):
    with output_parent(output) as parent:
        name=output.name+'.lock'
        fd=os.open(name,os.O_CREAT|os.O_RDWR|os.O_NONBLOCK|getattr(os,'O_NOFOLLOW',0),0o600,dir_fd=parent)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):raise ValueError('Invalid receipt lock file')
            if os.name=='posix':
                import fcntl
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError as error:raise RuntimeError('Receipt rebuild lock is busy') from error
            else:
                import msvcrt
                if os.fstat(fd).st_size==0:os.write(fd,b'0')
                os.lseek(fd,0,os.SEEK_SET)
                try:msvcrt.locking(fd,msvcrt.LK_NBLCK,1)
                except OSError as error:raise RuntimeError('Receipt rebuild lock is busy') from error
            yield parent
        finally:os.close(fd)


@contextmanager
def atomic_log(output,parent):
    name=output.name+'.tmp-'+str(os.getpid())
    fd=os.open(name,os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0),0o600,dir_fd=parent)
    try:
        with os.fdopen(fd,'w') as stream:yield stream
        os.replace(name,output.name,src_dir_fd=parent,dst_dir_fd=parent)
    finally:
        try:os.unlink(name,dir_fd=parent)
        except FileNotFoundError:pass


def rebuild(project,prefix,output):
    project=project.resolve();output=output.absolute();lib=project/'.lake/build/lib/lean'
    if output.suffix!='.json' or output.name in CONFIG_FILES+('package.json','package-lock.json'):raise ValueError('Receipt output must be a census JSON cache')
    if output.exists() or output.is_symlink():
        previous=json.loads(regular_bytes(output))
        if previous.get('schemaVersion')!=2 or previous.get('mutableCache') is not True or previous.get('prefix')!=prefix or Path(previous.get('projectRoot','')).resolve()!=project:
            raise ValueError('Refusing unrelated, legacy or frozen receipt output; select a new cache path')
    with receipt_lock(output) as parent:
        # Revalidate after acquiring the OS lock. Atomic logs never truncate an
        # existing inode or its hard links. The lock releases even on SIGKILL.
        if output.exists():
            previous=json.loads(regular_bytes(output))
            if previous.get('mutableCache') is not True or previous.get('prefix')!=prefix or Path(previous.get('projectRoot','')).resolve()!=project:raise ValueError('Refusing unrelated receipt output')
        try:os.unlink(output.name,dir_fd=parent)
        except FileNotFoundError:pass
        build_log=output.with_suffix('.build.log');replay_log=output.with_suffix('.replay.log')
        source_before={str(p.relative_to(project)):digest(p) for p in source_files(project,prefix)}
        tools_before=tool_hashes();config_initial=config_hashes(project)
        compiler_initial=Path(resolve_compiler(project));compiler_identity=(str(compiler_initial.resolve()),digest(compiler_initial))
        environment_initial=environment_fingerprint()
        build_targets=['+'+'.'.join(Path(p).with_suffix('').parts)+':olean' for p in source_before]
        with atomic_log(build_log,parent) as log:
            build=command(['lake','build'],cwd=project,stdout=log,stderr=subprocess.STDOUT)
            if build.returncode==0:build=command(['lake','build',*build_targets],cwd=project,stdout=log,stderr=subprocess.STDOUT)
        if build.returncode:raise RuntimeError('Build failed: '+str(build_log))
        config_before=config_hashes(project)
        if any(config_before.get(k)!=v for k,v in config_initial.items()) or set(config_before)-set(config_initial)-{'lake-manifest.json'}:
            raise RuntimeError('Project/compiler configuration changed during build')
        compiler_now=Path(resolve_compiler(project))
        if (str(compiler_now.resolve()),digest(compiler_now))!=compiler_identity:raise RuntimeError('Active compiler changed during build')
        manifest=select_modules(project,lib,prefix);before=artifacts(lib,manifest['modules'])
        context=capture_context(project);context_before=context_hashes(context)
        if Path(context['compilerPath']).resolve()!=compiler_now.resolve():raise RuntimeError('Lake/compiler resolution mismatch')
        with tempfile.TemporaryDirectory(prefix='kernel-census-view-') as scratch:
            view=Path(scratch)
            for rel in before:
                target=view/rel;target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(lib/rel)
            env=dict(os.environ,KERNEL_CENSUS_LIB_DIR=str(view))
            with atomic_log(replay_log,parent) as log:
                replay=command(['lake','env','lean',str(HERE/'kernel_census.lean')],cwd=project,env=env,stdout=log,stderr=subprocess.STDOUT)
        if source_before!={str(p.relative_to(project)):digest(p) for p in source_files(project,prefix)}:raise RuntimeError('Sources changed during census')
        compiler_final=Path(resolve_compiler(project))
        if (str(compiler_final.resolve()),digest(compiler_final))!=compiler_identity or environment_initial!=environment_fingerprint():raise RuntimeError('Compiler/environment changed during census')
        if tools_before!=tool_hashes() or config_before!=config_hashes(project) or before!=artifacts(lib,manifest['modules']) or context_before!=context_hashes(context):raise RuntimeError('Tool/configuration/compiler/artifact snapshot changed during census')
        payloads=[line.removeprefix('KERNEL_CENSUS_JSON:') for line in replay_log.read_text().splitlines() if line.startswith('KERNEL_CENSUS_JSON:')]
        if len(payloads)!=1:raise RuntimeError('Missing/ambiguous kernel receipt: '+str(replay_log))
        receipt={'schemaVersion':2,'mutableCache':True,'projectRoot':str(project),'prefix':prefix,'manifest':manifest,'artifactHashes':before,
                 'kernel':json.loads(payloads[0]),'buildExitCode':0,'buildTargets':build_targets,'replayExitCode':replay.returncode,
                 'toolchain':(project/'lean-toolchain').read_text().strip(),'helperSha256':tools_before['kernel_census.lean'],
                 'toolHashes':tools_before,'configHashes':config_before,'context':context,'contextHashes':context_before}
        validate_kernel(receipt['kernel'],manifest['modules'])
        with atomic_log(output,parent) as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
        return receipt


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--prefix',required=True)
    parser.add_argument('--receipt','--output',dest='receipt',type=Path,required=True)
    parser.add_argument('--mode',choices=['check','rebuild'],default='check')
    parser.add_argument('--rehash-imports',action='store_true',help='Rehash every imported artifact instead of reusing verified file-identity digests')
    args=parser.parse_args(argv);start=time.monotonic()
    def interrupted(_signal, _frame):
        raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, interrupted)
    try:
        if args.mode == 'rebuild':rebuild(args.project_root,args.prefix,args.receipt)
        result=inspect_receipt(args.project_root,args.prefix,args.receipt,rehash_imports=args.rehash_imports)
    except KeyboardInterrupt:
        result=result_record('unverified',args.receipt,['Kernel census interrupted'])
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as error:
        result=result_record('unverified',args.receipt,[str(error)])
    result['mode']=args.mode;result['elapsedMs']=round((time.monotonic()-start)*1000)
    print(json.dumps(result))
    return 0 if result['gateEligible'] else 2

if __name__=='__main__':raise SystemExit(main())
