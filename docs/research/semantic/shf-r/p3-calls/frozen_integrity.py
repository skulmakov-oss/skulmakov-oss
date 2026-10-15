from pathlib import Path
import json,hashlib
out=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-P3-20261016')
old=Path('/home/WSL_USER/shf-r-comparison-20261015')
rows=[]
for root in [old,Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-R-WSL-20261015')]:
 manifest=json.loads((root/'input-hashes.json').read_text())
 mismatch=[p for p,h in manifest.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
 rows.append(dict(root=str(root),inputs=len(manifest),mismatches=mismatch))
(out/'frozen-integrity.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
assert all(not r['mismatches'] for r in rows)
