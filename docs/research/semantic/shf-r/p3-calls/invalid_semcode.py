from pathlib import Path
import json,subprocess
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-P3-20261016')
f=root/'invalid.smc';f.write_bytes(b'not SemCode')
rows=[]
for name,b in [('main','/home/WSL_USER/shf-r-comparison-20261015/target-p2/release/smc-cli'),('p3','/home/WSL_USER/shf-p3-20261016/target/release/smc-cli')]:
 r=subprocess.run([b,'run-smc',str(f)],capture_output=True,text=True,timeout=15,cwd=root)
 rows.append(dict(name=name,exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
(root/'invalid-semcode.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
assert rows[0]['exit']!=0 and rows[1]['exit']==rows[0]['exit'] and rows[0]['stderr']==rows[1]['stderr']
