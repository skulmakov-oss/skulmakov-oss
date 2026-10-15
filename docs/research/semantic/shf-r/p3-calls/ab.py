import subprocess,time,hashlib,json,os
from pathlib import Path
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-P3-20261016')
old=Path('/home/WSL_USER/shf-r-comparison-20261015')
src=old/'workloads/lex_calls_32000.sm'; inp=old/'workloads/root/input_32000.txt'
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for name,binary,extra in [('A-main',old/'target-p2/release/smc-cli',[]),('B-p3',Path('/home/WSL_USER/shf-p3-20261016/target/release/smc-cli'),['--max-calls','1000000'])]:
 cmd=[str(binary),'run',str(src),'--profile','cli-read-only','--root',str(old/'workloads/root'),'--envelope','trusted-compiler','--max-steps','200000000','--metrics','json']+extra
 t=time.monotonic()
 try:
  r=subprocess.run(cmd,cwd=root,env=env,capture_output=True,timeout=120)
  stdout=r.stdout.decode();stderr=r.stderr.decode();code=r.returncode
 except subprocess.TimeoutExpired as e:
  stdout=(e.stdout or b'').decode();stderr=(e.stderr or b'').decode();code='TIMEOUT'
 (root/(name+'.stdout')).write_text(stdout);(root/(name+'.stderr')).write_text(stderr)
 metrics=[json.loads(x) for x in stderr.splitlines() if x.startswith('{"schema":"semantic.run.metrics/')]
 record=dict(name=name,command=cmd,exit=code,wall_seconds=time.monotonic()-t,binary_sha256=sha(binary),source_sha256=sha(src),input_sha256=sha(inp),metrics=metrics)
 # Independently compute the frozen source's digit-count assertion oracle.
 artifact=root/(name+'.smc')
 compile_cmd=[str(binary),'compile',str(src),'-o',str(artifact),'--opt-level','O0']
 c=subprocess.run(compile_cmd,cwd=root,env=env,capture_output=True,timeout=120)
 (root/(name+'-compile.log')).write_bytes(c.stdout+c.stderr)
 v=subprocess.run([str(binary),'verify',str(artifact)],cwd=root,env=env,capture_output=True,timeout=120) if c.returncode==0 else None
 if v is not None: (root/(name+'-verify.log')).write_bytes(v.stdout+v.stderr)
 record.update(compile_command=compile_cmd,compile_exit=c.returncode,verify_exit=v.returncode if v is not None else None,artifact_sha256=sha(artifact) if c.returncode==0 else None)
 record['oracle_digits']=sum(48<=b<=57 for b in inp.read_bytes())
 records.append(record)
 print(json.dumps(record),flush=True)
(root/'AB.json').write_text(json.dumps(records,indent=2))
