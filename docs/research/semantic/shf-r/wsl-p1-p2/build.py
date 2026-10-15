import pathlib,subprocess,os,json,hashlib,time,platform
os.environ['PATH']='/home/WSL_USER/.cargo/bin:'+os.environ['PATH']
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015')
def run(cmd,**kw): return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,**kw)
manifest={'commands':{},'builds':{}}
for cmd in [['uname','-a'],['rustc','--version','--verbose'],['cargo','--version'],['gcc','--version'],['git','--version'],['lscpu'],['free','-b'],['df','-T',str(r)],['ldconfig','-p'],['ps','-eo','pid,comm,pcpu,pmem,args']]: manifest['commands'][' '.join(cmd)]=run(cmd).stdout
manifest['os_release']=pathlib.Path('/etc/os-release').read_text()
manifest['env']={k:os.environ[k] for k in ['RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CC','CXX','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'] if k in os.environ}
for label in ['baseline','p1','p2']:
    repo=r/label
    env=os.environ.copy(); env.update(CARGO_TARGET_DIR=str(r/('target-'+label)),CARGO_NET_OFFLINE='true',CARGO_BUILD_JOBS='2')
    cmd=['cargo','build','--release','-p','smc-cli','--locked','--offline']
    print('BUILD',label,flush=True); start=time.time()
    with (r/('build-'+label+'.log')).open('w') as log: result=subprocess.run(cmd,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT)
    entry={'exit':result.returncode,'seconds':time.time()-start,'command':cmd,'env':{k:env[k] for k in ['CARGO_TARGET_DIR','CARGO_NET_OFFLINE','CARGO_BUILD_JOBS']},'sha':run(['git','rev-parse','HEAD'],cwd=repo).stdout.strip(),'lock_sha256':hashlib.sha256((repo/'Cargo.lock').read_bytes()).hexdigest()}
    manifest['builds'][label]=entry
    (r/'environment-builds.json').write_text(json.dumps(manifest,indent=2))
    print(label,entry,flush=True)
    if result.returncode: print((r/('build-'+label+'.log')).read_text()[-4000:],flush=True); break

