import pathlib,subprocess,os,json,time,shutil
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015');win=pathlib.Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-R-WSL-20261015')
while True:
    path=r/'environment-builds.json'
    if path.exists():
        try: manifest=json.loads(path.read_text())
        except ValueError: time.sleep(1);continue
        if 'p2' in manifest['builds']:
            assert all(manifest['builds'][x]['exit']==0 for x in ['baseline','p1','p2']);break
        if any(x['exit'] for x in manifest['builds'].values()): raise SystemExit('Build blocker')
    time.sleep(1)
for name in ['build.py','prepare.py','freeze.py','measure.py','phases.py','report.py','METHODOLOGY.md','active-before.json','issue2030-comments.json']:shutil.copy2(win/name,r/name)
with (r/'pre-measurement-processes.txt').open('w') as out:subprocess.run(['ps','-eo','pid,comm,pcpu,pmem,args'],stdout=out)
for name in ['measure','phases']:
    print('START',name,flush=True)
    with (r/(name+'-progress.log')).open('w') as out: result=subprocess.run(['python3',str(r/(name+'.py'))],stdout=out,stderr=subprocess.STDOUT)
    print('FINISH',name,result.returncode,flush=True)
    if result.returncode:raise SystemExit(result.returncode)
print('START focused E2 test',flush=True)
env=os.environ.copy();env.update(PATH='/home/WSL_USER/.cargo/bin:'+env['PATH'],CARGO_TARGET_DIR=str(r/'target-p2'),CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='2')
cmd=['cargo','test','--release','--locked','--offline','-p','sm-vm','e2_fast_path_activation_and_moves_count','--','--nocapture']
with (r/'e2-activation-test.log').open('w') as out:result=subprocess.run(cmd,cwd=r/'p2',env=env,stdout=out,stderr=subprocess.STDOUT)
(r/'e2-test-result.json').write_text(json.dumps({'command':cmd,'exit':result.returncode},indent=2))
print('TEST FINISH',result.returncode,flush=True)
subprocess.run(['python3',str(r/'report.py')],check=True)
print('ALL MEASUREMENTS COMPLETE',flush=True)
