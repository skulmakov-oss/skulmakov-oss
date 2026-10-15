import pathlib,subprocess,os,time,json,hashlib,threading,signal
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015'); artifacts=r/'artifacts'; artifacts.mkdir(exist_ok=True); logs=r/'phase-logs'; logs.mkdir(exist_ok=True)
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def call(cmd,name,meta):
    start=time.perf_counter(); expired=threading.Event()
    with (logs/(name+'.out')).open('wb') as out,(logs/(name+'.err')).open('wb') as err:
        p=subprocess.Popen(cmd,cwd=r/'workloads',env=env,stdout=out,stderr=err,start_new_session=True)
        def kill():
            expired.set()
            try:os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        timer=threading.Timer(120,kill);timer.start(); status=p.wait();timer.cancel()
    row=dict(meta,command=cmd,exit=status,timeout=expired.is_set(),wall_ms=(time.perf_counter()-start)*1000,stdout=str(logs/(name+'.out')),stderr=str(logs/(name+'.err')))
    with (r/'phases.jsonl').open('a') as file:file.write(json.dumps(row)+'\n')
    return row
families=['map_set','map_get','map_versions','state_record_map','state_record_seq','seq_push','seq_read','record_with','text_scan','lex_calls']
sources=[r/'workloads'/f'{f}_{n}.sm' for f in families for n in [1000,4000,16000,32000]]+[r/'workloads'/f'state{k}_{n}.sm' for k in [5,10] for n in [8000,16000,32000]]
for source in sources:
    for trial in [-1,0,1,2]:
        labels=['baseline','p1','p2'];shift=trial%3;labels=labels[shift:]+labels[:shift]
        for label in labels:
            binary=str(r/('target-'+label)/'release/smc-cli');artifact=artifacts/f'{label}-{source.stem}-O0.smc'
            m={'revision':label,'source':source.name,'trial':trial,'kind':'compile-O0'}
            result=call([binary,'compile',str(source),'-o',str(artifact),'--opt-level','O0'],f'compile-{label}-{source.stem}-{trial}',m)
            if result['exit']==0:
                m=dict(m,kind='verify-CLI',artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest())
                call([binary,'verify',str(artifact)],f'verify-{label}-{source.stem}-{trial}',m)
    print('PHASE',source.name,flush=True)
# Existing CLI run-smc (default quotas, no host capabilities) supports only functional comparisons here.
for family in families:
    for label in ['baseline','p1','p2']:
        source=r/'workloads'/f'{family}_1000.sm';binary=str(r/('target-'+label)/'release/smc-cli')
        for opt in ['O0','O1']:
            artifact=artifacts/f'{label}-{source.stem}-{opt}.smc'
            result=call([binary,'compile',str(source),'-o',str(artifact),'--opt-level',opt],f'parity-compile-{label}-{family}-{opt}',{'kind':'parity-compile','revision':label,'family':family,'opt':opt})
            if result['exit']==0:
                call([binary,'run-smc',str(artifact)],f'parity-run-{label}-{family}-{opt}',{'kind':'parity-run','revision':label,'family':family,'opt':opt,'artifact_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest()})
(r/'artifact-hashes.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(artifacts.glob('*'))},indent=2))
print('PHASE COMPLETE',flush=True)
