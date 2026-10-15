import pathlib,subprocess,os,time,json,hashlib,signal,resource,statistics,re,threading
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015'); logs=r/'runs'; logs.mkdir(exist_ok=True)
labels=['baseline','p1','p2']; families=['map_set','map_get','map_versions','state_record_map','state_record_seq','seq_push','seq_read','record_with','text_scan','lex_calls']; sizes=[1000,4000,16000,32000]
cases=[(f,n) for f in families for n in sizes]+[(f'state{k}',n) for k in [5,10] for n in [8000,16000,32000]]
env=os.environ.copy(); env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
manifest=json.loads((r/'environment-builds.json').read_text())
for label in labels:
    b=r/('target-'+label)/'release/smc-cli'; assert b.is_file(),b
    manifest['builds'][label]['binary_sha256']=hashlib.sha256(b.read_bytes()).hexdigest()
    manifest['builds'][label]['compiler_sha256']=hashlib.sha256(pathlib.Path('/home/WSL_USER/.rustup/toolchains/1.97.1-x86_64-unknown-linux-gnu/bin/rustc').read_bytes()).hexdigest()
(r/'environment-builds.json').write_text(json.dumps(manifest,indent=2))
def measure(label,f,n,trial,kind='run',extra=None):
    name=f'{kind}-{f}-{n}-{label}-{trial}'; b=r/('target-'+label)/'release/smc-cli'; source=r/'workloads'/f'{f}_{n}.sm'
    profile='cli-read-only' if f in ['text_scan','lex_calls'] else 'pure'
    cmd=[str(b),'run',str(source),'--profile',profile,'--root',str(r/'workloads/root'),'--envelope','trusted-compiler','--max-steps','200000000','--metrics','json']
    if extra: cmd=extra
    stdout=logs/(name+'.stdout'); stderr=logs/(name+'.stderr'); rss=logs/(name+'.time')
    timed=['/usr/bin/time','-f','%M', '-o',str(rss)]+cmd
    start=time.perf_counter(); load=os.getloadavg()
    with stdout.open('wb') as out,stderr.open('wb') as err:
        p=subprocess.Popen(timed,cwd=r/'workloads',env=env,stdout=out,stderr=err,start_new_session=True)
        expired=threading.Event()
        def kill_timeout():
            expired.set()
            try: os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError: pass
        timer=threading.Timer(120,kill_timeout); timer.start()
        status=p.wait(); timer.cancel(); timeout=expired.is_set()
    wall=(time.perf_counter()-start)*1000
    metrics=None
    for line in stderr.read_text(errors='replace').splitlines():
        try:
            obj=json.loads(line)
            if isinstance(obj,dict) and ('schema' in obj or 'effective_quotas' in obj): metrics=obj
        except ValueError: pass
    obj={'kind':kind,'family':f,'n':n,'revision':label,'trial':trial,'command':cmd,'wall_ms':wall,'exit':status,'timeout':timeout,'metrics':metrics,'loadavg_before':load,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'stdout_sha256':hashlib.sha256(stdout.read_bytes()).hexdigest(),'peak_rss_kib':None,'stderr':str(stderr),'stdout':str(stdout)}
    if rss.exists():
        nums=re.findall(r'^\d+$',rss.read_text(),re.M)
        if nums: obj['peak_rss_kib']=int(nums[-1])
    with (r/'measurements.jsonl').open('a') as out: out.write(json.dumps(obj)+'\n')
    return obj
for idx,(f,n) in enumerate(cases):
    for trial in [-1,0,1,2]:
        order=labels[trial%3:]+labels[:trial%3]
        # Balanced rotating order: each revision occupies each measured position once.
        for label in order:
            obj=measure(label,f,n,trial)
            print(f'{f} {n} {label} trial={trial} {obj["wall_ms"]:.1f}ms exit={obj["exit"]} timeout={obj["timeout"]}',flush=True)
# Calls without step override and denied-capability controls use original unchanged workloads.
for label in labels:
    binary=str(r/('target-'+label)/'release/smc-cli')
    src=str(r/'workloads/lex_calls_32000.sm')
    measure(label,'lex_calls',32000,0,'calls-default-steps',[binary,'run',src,'--profile','cli-read-only','--root',str(r/'workloads/root'),'--envelope','trusted-compiler','--metrics','json'])
    src=str(r/'workloads/text_scan_1000.sm')
    measure(label,'text_scan',1000,0,'capability-denial',[binary,'run',src,'--profile','pure','--root',str(r/'workloads/root'),'--envelope','trusted-compiler','--max-steps','200000000','--metrics','json'])
print('RUN COMPLETE',flush=True)



