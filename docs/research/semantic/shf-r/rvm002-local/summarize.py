from pathlib import Path
import csv,statistics,json,math,hashlib
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-002')
rows=[]
for filename in ['scale.csv','remaining.csv']:
    rows.extend(csv.DictReader((root/filename).open()))
for filename,model in [('prototype-large.csv','prototype'),('snapshot-reference.csv','reference'),('snapshot-prototype.csv','prototype')]:
    if (root/filename).exists():
        with (root/filename).open() as f:
            for row in csv.DictReader(f,fieldnames=['case','n','sample','ns','allocations','allocated_bytes','peak_extra_live_bytes','steps','calls','frames','outcome']):row['model']=model;rows.append(row)
groups={}
for row in rows:
    if row['outcome']!='OK':continue
    groups.setdefault((row['case'],int(row['n']),row['model']),[]).append(row)
lines=['| Case | n | Model | Samples | Median ms | Range ms | Allocations | Requested bytes | Peak extra bytes | Steps / Calls |','|---|---:|---|---:|---:|---|---:|---:|---:|---|']
for (case,n,model),samples in sorted(groups.items()):
    ns=[int(s['ns'])/1e6 for s in samples];counts={k:sorted({int(s[k]) for s in samples}) for k in ['allocations','allocated_bytes','peak_extra_live_bytes','steps','calls']}
    lines.append(f'| {case} | {n} | {model} | {len(ns)} | {statistics.median(ns):.3f} | {min(ns):.3f}–{max(ns):.3f} | {counts["allocations"]} | {counts["allocated_bytes"]} | {counts["peak_extra_live_bytes"]} | {counts["steps"]} / {counts["calls"]} |')
for model in ['reference','prototype']:
    x=[math.log(n) for c,n,m in groups if c=='build' and m==model and 1024<=n<=16384]
    y=[math.log(statistics.median(int(s['ns']) for s in samples)) for (c,n,m),samples in groups.items() if c=='build' and m==model and 1024<=n<=16384]
    slope=sum((a-statistics.mean(x))*(b-statistics.mean(y)) for a,b in zip(x,y))/sum((a-statistics.mean(x))**2 for a in x)
    lines.append(f'\n{model} log-log least-squares slope (1024–16384, four sizes): {slope:.3f}. Descriptive, not a worst-case proof.')
for model in ['reference','prototype']:
    data=list(csv.DictReader((root/f'compiler-{model}.csv').open()))
    s=[r for r in data if r['case']=='semseed']; ns=[int(r['ns'])/1e6 for r in s]
    lines.append(f'\nSemSeed {model}: median {statistics.median(ns):.3f} ms, range {min(ns):.3f}–{max(ns):.3f}, outcome {sorted({r["outcome"] for r in s})}, allocations {sorted({r["allocations"] for r in s})}, bytes {sorted({r["allocated_bytes"] for r in s})}.')
(root/'summary.md').write_text('\n'.join(lines))
identities={}
for p in (root/'prototype').glob('*.smc'):
    ref=root/'reference'/p.name
    if ref.exists():assert ref.read_bytes()==p.read_bytes()
    identities[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reference_identical':ref.exists()}
(root/'artifact-identities.json').write_text(json.dumps(identities,indent=2))
print('\n'.join(lines))
