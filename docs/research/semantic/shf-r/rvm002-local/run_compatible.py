from pathlib import Path
import subprocess,hashlib,json
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-002')
models={x:Path(f'/home/WSL_USER/sem-rvm002-{x}/target/release/examples/map_scale') for x in ['reference','prototype']}
(root/'compatible-binary-identities.json').write_text(json.dumps({k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in models.items()},indent=2))
with (root/'compatible-scale.csv').open('w',buffering=1) as out:
    out.write('model,case,n,sample,ns,allocations,allocated_bytes,peak_extra_live_bytes,steps,calls,frames,outcome\n')
    for n in [16,128,1024,4096,8192,16384,32768]:
        for sample in range(3):
            for model in (['prototype','reference'] if sample%2==0 else ['reference','prototype']):
                if model=='reference' and n==32768 and sample>0:
                    out.write(f'compatible,build,{n},{sample},,,,,,,,NOT_RUN_BOUNDED_BUDGET\n');continue
                try:run=subprocess.run([str(models[model]),str(n),'1','build',str(root/model)],capture_output=True,text=True,timeout=90)
                except subprocess.TimeoutExpired:
                    out.write(f'compatible,build,{n},{sample},,,,,,,,INCOMPLETE_TIMEOUT\n');raise SystemExit('bounded compatible baseline timed out; no extension')
                assert run.returncode==0,run.stderr
                row=run.stdout.strip().split(',');row[2]=str(sample);label='compatible' if model=='reference' else 'prototype'
                out.write(label+','+','.join(row)+'\n');print(label,n,sample,row[3],flush=True)
            ref=root/'reference'/f'build-{n}.smc';proto=root/'prototype'/f'build-{n}.smc';assert ref.read_bytes()==proto.read_bytes()
