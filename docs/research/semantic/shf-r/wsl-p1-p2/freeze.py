import pathlib,re,json,hashlib,subprocess
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015'); src=(r/'p2/crates/sm-vm/src/semcode_vm.rs').read_text()
additional=[]
for k in [5,10]:
    match=re.search(r'let make_state'+str(k)+r' = \|n: usize\| \{\s*format!\(\s*"((?:\\.|[^"\\])*)"',src,re.S)
    if not match: print('MISSING State',k); continue
    raw=re.sub(r'\\\n\s*','',match.group(1))
    template=json.loads('"'+raw+'"')
    for n in [8000,16000,32000]:
        text=template.replace('{{','\x00').replace('}}','\x01').replace('{n}',str(n)).replace('\x00','{').replace('\x01','}')
        path=r/'workloads'/f'state{k}_{n}.sm'; path.write_text(text); additional.append(str(path))
files={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((r/'workloads').rglob('*')) if p.is_file()}
(r/'input-hashes.json').write_text(json.dumps(files,indent=2))
(r/'additional-provenance.json').write_text(json.dumps({'source_sha':'188dec7eddfafaab5926af2d30f528bfe3d89a2c','source_path':'crates/sm-vm/src/semcode_vm.rs','generator':'benchmark_multi_field_state_scaling_sweep make_state5/make_state10','files':additional},indent=2))
print('Frozen',len(files),'files; additional',len(additional))
