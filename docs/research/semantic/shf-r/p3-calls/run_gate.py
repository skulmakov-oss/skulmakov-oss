import os,sys,json,subprocess,time
from pathlib import Path
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-P3-20261016')
label=sys.argv[1]; cmd=sys.argv[2:]
env=os.environ.copy();env.update(CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='2',CARGO_TARGET_DIR='/home/WSL_USER/shf-p3-20261016/target',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
env['PATH']='/home/WSL_USER/.cargo/bin:'+env.get('PATH','')
start=time.monotonic()
with (root/(label+'.log')).open('w') as f:
 p=subprocess.run(cmd,cwd=root/'repo',env=env,stdout=f,stderr=subprocess.STDOUT)
r={'label':label,'command':cmd,'exit':p.returncode,'seconds':time.monotonic()-start,'target':env['CARGO_TARGET_DIR']}
(root/(label+'.json')).write_text(json.dumps(r,indent=2))
print(json.dumps(r),flush=True)
print((root/(label+'.log')).read_text()[-4000:],flush=True)
sys.exit(p.returncode)
