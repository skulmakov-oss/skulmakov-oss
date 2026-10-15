import pathlib,json,hashlib,subprocess,shutil,csv,collections,statistics,math
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015');w=pathlib.Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-R-WSL-20261015')
report=(r/'REPORT.md').read_text();env=json.loads((r/'environment-builds.json').read_text());cmds=env['commands']
meta=['','### Exact host and builds','','```text',env['os_release'].splitlines()[0],cmds['uname -a'].strip(),cmds['rustc --version --verbose'].strip(),cmds['cargo --version'].strip(),cmds['gcc --version'].splitlines()[0],cmds['git --version'].strip()]
meta.extend(x for x in cmds['lscpu'].splitlines() if x.startswith(('CPU(s):','Model name:','Architecture:','Thread(s)','Core(s)')))
meta.extend([cmds['free -b'].strip(),cmds['df -T '+str(r)].strip(),*(x for x in cmds['ldconfig -p'].splitlines() if 'openblas' in x),'```','','WSL runtime version:','','```text',(w/'wsl-version.txt').read_text(encoding='utf-8-sig').strip(),'```','','Build settings: `opt-level=3`, `lto=true`, `codegen-units=1`, `panic=abort`, `strip=symbols`; `CARGO_BUILD_JOBS=2`. Execution thread env: `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`.','','|Revision|Source SHA|Cargo.lock SHA-256|Binary SHA-256|','|---|---|---|---|'])
for label,b in env['builds'].items():meta.append(f'|{label}|`{b["sha"]}`|`{b["lock_sha256"]}`|`{b["binary_sha256"]}`|')
meta.extend(['','Compiler binary SHA-256: `'+env['builds']['p2']['compiler_sha256']+'`.','','Build command for each detached checkout: `CARGO_NET_OFFLINE=true CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR=<separate target> cargo build --release -p smc-cli --locked --offline`. All builds exit 0.','','Execution template: `target-<revision>/release/smc-cli run workloads/<family>_<N>.sm --profile <pure|cli-read-only> --root workloads/root --envelope trusted-compiler --max-steps 200000000 --metrics json`. Text and lex use cli-read-only; remaining cases use pure. Warm-up trial -1 excluded from statistics; measured order rotates B/P1/P2, P1/P2/B, P2/B/P1. Timeout 120 seconds per invocation.','','OpenBLAS package metadata / Linux contention snapshot:','','```text',json.dumps(json.loads((r/'supplemental-environment.json').read_text()),indent=2),'```',''])
report=report.replace('## B. End-to-end CLI comparison','\n'.join(meta)+'\n## B. End-to-end CLI comparison')
rows=[json.loads(l) for l in (r/'measurements.jsonl').read_text().splitlines()]
extra=['','## H. Artifact and failure inventory','','### Frozen source and input SHA-256','','|Path|SHA-256|','|---|---|']
for path,digest in json.loads((r/'input-hashes.json').read_text()).items():extra.append(f'|`{path}`|`{digest}`|')
extra+=['','The original generator also writes tuple_loop; it is retained for provenance but is outside the requested timing families. Original text inputs have floor(N/12)*12 bytes, following the generator exactly.','','### All timeout attempts (including warm-up)','']
for x in rows:
    if x['timeout']:extra.append(f'- {x["family"]} N={x["n"]} {x["revision"]}, trial={x["trial"]}, {x["wall_ms"]:.1f} ms: TIMEOUT. RSS/counters unavailable if the killed CLI did not finish metrics.')
extra+=['','### E2 activation test','','```text',(r/'e2-activation-test.log').read_text()[-3500:],'```','', 'This existing test is independent of timed CLI measurements. Its passing activation counters cover only its own fixtures; do not treat it as counters collected for every timed State5/State10 run.','','### Tracked tree preservation','','```json',(r/'repository-preservation.json').read_text(),'```','']
# Standalone emitted O0 artifact identity comparison across the same input/revisions.
art=json.loads((r/'artifact-hashes.json').read_text()); by=collections.defaultdict(dict)
for path,digest in art.items():
    name=pathlib.Path(path).name
    for label in ['baseline','p1','p2']:
        if name.startswith(label+'-') and name.endswith('-O0.smc'):by[name[len(label)+1:]][label]=digest
same=sum(len(v)==3 and len(set(v.values()))==1 for v in by.values())
extra+=['',f'Standalone O0 SemCode byte identity: {same}/{len(by)} workload artifacts have identical hashes across all three revisions. Full hashes in artifact-hashes.json; identical source is not assumed to imply byte identity without this comparison.','']
resource_lines=['','## I. Runtime counters and peak RSS','','Counters shown are actual P2 measured observations; cross-revision equality/availability is reported in section D. RSS columns are maximum observed process peak across the three measured repetitions, not allocation traffic or a heap bound.','','|Workload|N|P2 Steps|Calls|Peak frames|Effects|Baseline RSS KiB|P1 RSS KiB|P2 RSS KiB|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for family,n in sorted(set((x['family'],x['n']) for x in rows if x['kind']=='run')):
    samples=[x for x in rows if x['kind']=='run' and x['family']==family and x['n']==n and x['trial']>=0]
    metrics=next((x['metrics'] for x in samples if x['revision']=='p2' and x['metrics']),{})
    counters=metrics.get('counters') or {}
    rss=[]
    for label in ['baseline','p1','p2']:
        vals=[x['peak_rss_kib'] for x in samples if x['revision']==label and x['peak_rss_kib'] is not None]
        rss.append(str(max(vals)) if vals else 'NOT MEASURED')
    resource_lines.append('|'+ '|'.join([family,str(n)]+[str(counters.get(k,'NOT MEASURED')) for k in ['steps','calls','peak_frames','effect_calls']]+rss)+'|')
extra+=resource_lines
(r/'REPORT.md').write_text(report+'\n'.join(extra))
# Copy evidence only, not Git objects or Cargo caches. Native originals remain authoritative/preserved.
for name in ['REPORT.md','METHODOLOGY.md','environment-builds.json','supplemental-environment.json','input-hashes.json','artifact-hashes.json','measurements.jsonl','phases.jsonl','summary.csv','repository-preservation.json','additional-provenance.json','e2-test-result.json','e2-activation-test.log','build-baseline.log','build-p1.log','build-p2.log','measure-progress.log','phases-progress.log']:
    shutil.copy2(r/name,w/name)
for name in ['workloads','artifacts','runs','phase-logs']:
    shutil.copytree(r/name,w/name,dirs_exist_ok=True)
print('FINAL EVIDENCE COPIED',same,len(by),flush=True)

