import pathlib,json,statistics,math,csv,collections,hashlib,subprocess
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015')
rows=[json.loads(l) for l in (r/'measurements.jsonl').read_text().splitlines()]
groups=collections.defaultdict(list)
for x in rows:
    if x['kind']=='run' and x['trial']>=0:groups[(x['family'],x['n'],x['revision'])].append(x)
def summary(xs):
    good=[x for x in xs if x['exit']==0 and not x['timeout'] and x['metrics'] and x['metrics']['outcome']=='ok']
    ok=len(good)==3
    vals=[x['wall_ms'] for x in good]; internal=[x['metrics']['nondeterministic']['wall_ms'] for x in good]
    return {'ok':ok,'samples':len(xs),'successes':len(good),'median_ms':statistics.median(vals) if ok else None,'min_ms':min(vals) if ok else None,'max_ms':max(vals) if ok else None,'internal_median_ms':statistics.median(internal) if ok else None,'outcomes':sorted(set('TIMEOUT' if x['timeout'] else (x['metrics'] or {}).get('outcome','NO METRICS') for x in xs)),'peak_rss_kib':max((x['peak_rss_kib'] or 0) for x in xs),'counters':[(x['metrics'] or {}).get('counters') for x in xs]}
stats={k:summary(v) for k,v in groups.items()}
with (r/'summary.csv').open('w') as out:
    w=csv.writer(out);w.writerow(['family','N','revision','median_ms','min_ms','max_ms','internal_median_ms','peak_rss_kib','outcomes'])
    for (f,n,l),s in sorted(stats.items()):w.writerow([f,n,l,s['median_ms'],s['min_ms'],s['max_ms'],s['internal_median_ms'],s['peak_rss_kib'],','.join(s['outcomes'])])
def slope(points):
    if len(points)<3:return None
    xx=[math.log(n) for n,t in points];yy=[math.log(t) for n,t in points];xm=statistics.mean(xx);ym=statistics.mean(yy)
    return sum((x-xm)*(y-ym) for x,y in zip(xx,yy))/sum((x-xm)**2 for x in xx)
labels=['baseline','p1','p2'];families=sorted(set(k[0] for k in stats));lines=['# SHF-R — WSL Ubuntu VM Performance: Baseline vs P1 vs P2','','## A. Environment and provenance','', 'Actual Ubuntu-24.04 WSL2, native ext4. No source patches or dependency installation. See environment-builds.json, input-hashes.json, artifact-hashes.json and METHODOLOGY.md for full provenance.','', 'BASELINE `94c5c50d16c3f2efc7691456755461bedae83b18`; P1 `758738a2edf0e984d6067fb372f003a381723d02`; P2 `188dec7eddfafaab5926af2d30f528bfe3d89a2c`.','','## B. End-to-end CLI comparison','','Times are milliseconds, external wall clock; three measured samples after warm-up. Success requires exit 0 plus metrics outcome ok (self-asserting sources). No failed sample is used for speedup.','','|Workload|N|Baseline ms [range]|P1 ms [range]|P2 ms [range]|B/P2|B/P1|P1/P2|Outcome|','|---|---:|---:|---:|---:|---:|---:|---:|---|']
for f,n in sorted(set((k[0],k[1]) for k in stats)):
    ss=[stats.get((f,n,l),{}) for l in labels]
    fmt=lambda s: f"{s['median_ms']:.2f} [{s['min_ms']:.2f}–{s['max_ms']:.2f}]" if s.get('ok') else '/'.join(s.get('outcomes',['NOT RUN']))
    ratio=lambda a,b:f"{a['median_ms']/b['median_ms']:.2f}x" if a.get('ok') and b.get('ok') else '—'
    lines.append('|'+ '|'.join([f,str(n)]+[fmt(s) for s in ss]+[ratio(ss[0],ss[2]),ratio(ss[0],ss[1]),ratio(ss[1],ss[2]),' / '.join(','.join(s.get('outcomes',[])) for s in ss)])+'|')
lines+=['','## C. Scaling','','OLS slope log(T) vs log(N), successful medians only. Startup and noise affect small cases. Range of adjacent slopes is descriptive, not a confidence interval.','','|Workload|Baseline p|P1 p|P2 p|','|---|---:|---:|---:|']
scaling={}
for f in families:
    ps=[]
    for label in labels:
        points=sorted((n,s['median_ms']) for (ff,n,l),s in stats.items() if ff==f and l==label and s['ok'])
        p=slope(points);adj=[math.log(b[1]/a[1])/math.log(b[0]/a[0]) for a,b in zip(points,points[1:])]
        scaling[(f,label)]={'p':p,'adjacent':adj,'n':len(points)}
        ps.append(f'{p:.2f} (adj {min(adj):.2f}..{max(adj):.2f}; {len(points)} pts)' if p is not None else 'INCONCLUSIVE (<3 successful sizes)')
    lines.append('|'+ '|'.join([f]+ps)+'|')
lines+=['','## D. Determinism and correctness','','|Workload|N|Within-revision counters stable|Across-revision counters equal|Outcomes equal|','|---|---:|---|---|---|']
for f,n in sorted(set((k[0],k[1]) for k in stats)):
    per=[groups.get((f,n,l),[]) for l in labels]
    signatures=lambda xs:[json.dumps((x['metrics'] or {}).get('counters'),sort_keys=True) for x in xs]
    executed=all(x['metrics'] and x['metrics'].get('execution_started') for xs in per for x in xs)
    timedout=any(x['timeout'] for xs in per for x in xs)
    stable=executed and all(len(set(signatures(xs)))==1 and all(x['metrics'] for x in xs) for xs in per)
    across=len(set(v for xs in per for v in signatures(xs)))==1 and stable
    outcomes=len(set((x['exit'],x['timeout'],(x['metrics'] or {}).get('outcome')) for xs in per for x in xs))==1
    lines.append(f'|{f}|{n}|{"PASS" if stable else ("NOT MEASURED (timeout/no execution)" if not executed else "FAIL")}|{"PASS" if across else ("NOT COMPARABLE" if not executed else "COUNTERS DIFFER")}|{"PASS" if outcomes else ("NOT COMPARABLE (timeout)" if timedout else "OUTCOMES DIFFER")}|')
lines+=['','## E. Resources, failures and unsupported measurements','','Full quotas/counters/error classes and RSS are preserved in measurements.jsonl. Peak RSS includes compilation+verification+execution inside the CLI process. Aggregate allocations, VM-only execution time and isolated planner time: NOT MEASURED.','','### Every non-successful measured run / negative control','']
for x in rows:
    if (x['trial']>=0 and x['exit']!=0) or x['kind']!='run':
        m=x['metrics'] or {};lines.append(f"- {x['kind']} {x['family']} N={x['n']} {x['revision']} trial={x['trial']}: exit={x['exit']}, timeout={x['timeout']}, outcome={m.get('outcome')}, counters={m.get('counters')}, quota={m.get('quota_exceeded')}; error={m.get('error')}")
phasepath=r/'phases.jsonl'
if phasepath.exists():
    phases=[json.loads(l) for l in phasepath.read_text().splitlines()];pg=collections.defaultdict(list)
    for x in phases:
        if x.get('trial',-1)>=0:pg[(x['source'],x['revision'],x['kind'])].append(x)
    lines+=['','### Separate CLI compilation and verification','','Standalone compile/verify times include command overhead; they are not isolated application-run phases.','','|Source|Revision|Compile median ms|Verify median ms|','|---|---|---:|---:|']
    for source,label in sorted(set((k[0],k[1]) for k in pg)):
        cells=[]
        for kind in ['compile-O0','verify-CLI']:
            xs=pg.get((source,label,kind),[]);cells.append(f"{statistics.median(x['wall_ms'] for x in xs):.3f}" if len(xs)==3 and all(x['exit']==0 for x in xs) else 'FAIL / NOT RUN')
        lines.append('|'+ '|'.join([source,label]+cells)+'|')
    lines+=['','### O0/O1 controlled-observation parity','','run-smc has its own default quotas and no application host profile. This is not elevated-envelope O1 performance evidence.','']
    parity=collections.defaultdict(dict)
    for x in phases:
        if x['kind']=='parity-run':parity[(x['family'],x['revision'])][x['opt']]=x
    for (f,l),opts in sorted(parity.items()):
        if set(opts)!={'O0','O1'}:lines.append(f'- {f} {l}: NOT RUN / incomplete pair');continue
        def output(x):return pathlib.Path(x['stdout']).read_text(errors='replace'),pathlib.Path(x['stderr']).read_text(errors='replace')
        a,b=opts['O0'],opts['O1'];aa,bb=output(a),output(b)
        # Preserve observations without masking source-location/diagnostic differences.
        same=a['exit']==b['exit'] and aa==bb
        lines.append(f'- {f} {l}: exact output/exit parity={same}; O0 exit={a["exit"]}, O1 exit={b["exit"]}; logs {a["stdout"]}, {b["stdout"]}.')
lines+=['','## F. Interpretation and limitations','','See final analysis below; numerical tables above derive only from saved runs. Small absolute differences and single-host measurements are not portable guarantees. Known historical container results used a Xeon host rather than this Core i5 WSL host; compare scaling and matched-revision ratios, not absolute milliseconds. Original internal wall_ms is retained alongside external process wall time.','','MiniLang lexer/parser original sources and frozen inputs: NOT RUN unless separately identified in this experiment. Repeated mixed-field/nested Sequence benchmarks: NOT RUN as independent families; State5/State10 are the exact available multi-field cases. No replacement workload is labeled MiniLang.','','Fast-path move/fallback counters are test-only in the existing VM and are not exposed by this release CLI; fast-path activation counts: NOT MEASURED. Timing improvement alone is not a direct proof of activation.','','## G. Repository preservation','','See repository-preservation.json and active-before/after snapshots. No GitHub mutations, source changes, branch changes in the active repository, quota changes, installation, or Checkpoint B implementation. Disposable checkouts and caches retained.']
(r/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('REPORT',r/'REPORT.md', 'rows',len(rows),'groups',len(stats),flush=True)
print(json.dumps({str(k):v for k,v in scaling.items()},indent=2))

