import subprocess, hashlib, json, platform
from pathlib import Path
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-002')
models={'reference':Path('/home/WSL_USER/sem-rvm002-reference'),'prototype':Path('/home/WSL_USER/sem-rvm002-prototype')}
for name in models: (root/name).mkdir(exist_ok=True)
identity={name:hashlib.sha256((p/'target/release/examples/map_scale').read_bytes()).hexdigest() for name,p in models.items()}
(root/'binary-identities.json').write_text(json.dumps({'platform':platform.platform(),'binaries':identity},indent=2))
with (root/'scale.csv').open('w',buffering=1) as out:
    out.write('model,case,n,sample,ns,allocations,allocated_bytes,peak_extra_live_bytes,steps,calls,frames,outcome\n')
    for kind in ['build','replace']:
        for n in [16,128,1024,4096,8192,16384,32768]:
            for sample in range(3):
                for name in (['reference','prototype'] if sample%2==0 else ['prototype','reference']):
                    cmd=[str(models[name]/'target/release/examples/map_scale'),str(n),'1',kind,str(root/name)]
                    try: result=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
                    except subprocess.TimeoutExpired:
                        out.write(f'{name},{kind},{n},{sample},,,,,,,,INCOMPLETE_TIMEOUT\n')
                        raise SystemExit('bounded run timed out; stopped without retry')
                    if result.returncode:
                        (root/'scale-failure.log').write_text(result.stderr)
                        raise SystemExit(f'{name} {kind} {n}: exit {result.returncode}')
                    fields=result.stdout.strip().split(','); fields[2]=str(sample)
                    out.write(name+','+','.join(fields)+'\n')
                    print(name,kind,n,sample,fields[3],flush=True)
            a=(root/'reference'/f'{kind}-{n}.smc').read_bytes(); b=(root/'prototype'/f'{kind}-{n}.smc').read_bytes()
            assert a==b, 'artifact mismatch'
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'reference').glob('*.smc')}
    (root/'artifact-identities.json').write_text(json.dumps(hashes,indent=2))
