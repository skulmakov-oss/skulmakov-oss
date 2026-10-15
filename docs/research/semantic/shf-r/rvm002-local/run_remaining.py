import subprocess,json,hashlib
from pathlib import Path
root=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-002')
models={x:Path(f'/home/WSL_USER/sem-rvm002-{x}/target/release/examples/map_scale') for x in ['reference','prototype']}
with (root/'remaining.csv').open('w',buffering=1) as out:
    out.write('model,case,n,sample,ns,allocations,allocated_bytes,peak_extra_live_bytes,steps,calls,frames,outcome\n')
    for kind in ['replace']:
        for n in [16,128,1024,4096,8192,16384,32768]:
            for sample in range(3):
                for model in (['reference','prototype'] if sample%2==0 else ['prototype','reference']):
                    # Baseline large replacement predictably exceeds bounded local budget.
                    if model=='reference' and n>8192:
                        out.write(f'{model},{kind},{n},{sample},,,,,,,,NOT_RUN_BOUNDED_BUDGET\n');continue
                    result=subprocess.run([str(models[model]),str(n),'1',kind,str(root/model)],capture_output=True,text=True,timeout=90)
                    if result.returncode: (root/'remaining-failure.log').write_text(result.stderr);raise SystemExit(result.returncode)
                    fields=result.stdout.strip().split(',');fields[2]=str(sample);out.write(model+','+','.join(fields)+'\n')
                    print(model,kind,n,sample,fields[3],flush=True)
    hashes={}
    for p in (root/'prototype').glob('*.smc'):
        ref=root/'reference'/p.name
        if ref.exists(): assert ref.read_bytes()==p.read_bytes()
        hashes[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reference_identical':ref.exists()}
    (root/'artifact-identities.json').write_text(json.dumps(hashes,indent=2))
