from pathlib import Path
import csv,statistics,math
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-002');rows=list(csv.DictReader((root/'compatible-scale.csv').open()));groups={}
for r in rows:
    if r['outcome']=='OK':groups.setdefault((int(r['n']),r['model']),[]).append(r)
lines=['| n | Model | Samples | Median ms | Range ms | Allocations | Requested bytes | Peak extra bytes | Steps |','|---:|---|---:|---:|---|---:|---:|---:|---:|']
for (n,model),samples in sorted(groups.items()):
    vals=[int(r['ns'])/1e6 for r in samples];r=samples[0]
    lines.append(f'| {n} | {model} | {len(vals)} | {statistics.median(vals):.3f} | {min(vals):.3f}–{max(vals):.3f} | {r["allocations"]} | {r["allocated_bytes"]} | {r["peak_extra_live_bytes"]} | {r["steps"]} |')
for model in ['compatible','prototype']:
    ns=[n for n,m in groups if m==model and 1024<=n<=16384];x=[math.log(n) for n in ns];y=[math.log(statistics.median(int(r['ns']) for r in groups[(n,model)])) for n in ns]
    slope=sum((a-statistics.mean(x))*(b-statistics.mean(y)) for a,b in zip(x,y))/sum((a-statistics.mean(x))**2 for a in x)
    lines.append(f'\n{model} descriptive log-log slope on 1024–16384: {slope:.3f}.')
lines.append('\nCompatible baseline 32768: INCOMPLETE at 90 seconds. No extension/retry. Largest candidate matched-series sample count is one; earlier three candidate samples remain separate raw evidence.')
(root/'compatible-summary.md').write_text('\n'.join(lines));print('\n'.join(lines))
