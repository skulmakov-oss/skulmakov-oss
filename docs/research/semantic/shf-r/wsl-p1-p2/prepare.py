import pathlib,subprocess,json,re,hashlib,os
root=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015')
revs={'baseline':'94c5c50d16c3f2efc7691456755461bedae83b18','p1':'758738a2edf0e984d6067fb372f003a381723d02','p2':'188dec7eddfafaab5926af2d30f528bfe3d89a2c'}
for label,sha in revs.items():
    subprocess.run(['git','-C',str(root/'git'),'show','-s','--format=fuller',sha],check=True)
    subprocess.run(['git','-C',str(root/'git'),'worktree','add','--detach',str(root/label),sha],check=True)
comments=json.loads(pathlib.Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-R-WSL-20261015/issue2030-comments.json').read_text(encoding='utf-8-sig'))
body=next(c['body'] for c in comments if c['id']==6168428649)
generator=re.search(r'```python\n(.*?)```',body,re.S).group(1)
(root/'gen_original.py').write_text(generator)
(root/'issue2030-original.md').write_text(body)
subprocess.run(['python3',str(root/'gen_original.py'),str(root/'workloads'),'1000,4000,16000,32000'],check=True)
for path in ['rust-toolchain.toml','AGENTS.md','CONSTRAINTS.md','.agents/skills/semantic-source-authoring-guard/SKILL.md','.agents/skills/semantic-verifier-runtime-guard/SKILL.md']:
    print('\nFILE',path,flush=True); print((root/'p2'/path).read_text())
