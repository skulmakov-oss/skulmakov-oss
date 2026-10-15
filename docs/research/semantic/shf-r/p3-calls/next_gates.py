import subprocess,sys
from pathlib import Path
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-P3-20261016')
steps=[('api-check',['cargo','test','--release','--locked','--offline','--test','public_api_contracts']),('build-cli',['cargo','build','--release','--locked','--offline','-p','smc-cli'])]
for label,cmd in steps:
 r=subprocess.run([sys.executable,str(root/'run_gate.py'),label]+cmd)
 if r.returncode: sys.exit(r.returncode)
subprocess.run([sys.executable,str(root/'ab.py')],check=True)
