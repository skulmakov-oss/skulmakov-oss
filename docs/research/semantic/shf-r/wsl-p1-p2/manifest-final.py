import pathlib,json,hashlib,shutil,datetime,subprocess
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015');w=pathlib.Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-R-WSL-20261015')
for name in ['confirm.py','integrity.py','finalize.py','inspect.py','determinism.py','run_all.py']:
 shutil.copy2(w/name,r/name)
files=['gen_original.py','prepare.py','freeze.py','build.py','measure.py','phases.py','report.py','confirm.py','integrity.py','run_all.py','finalize.py']
(r/'harness-hashes.json').write_text(json.dumps({name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in files},indent=2))
(r/'environment-final.txt').write_text(subprocess.check_output(['bash','-lc','rustc --version --verbose; cargo --version; gcc --version | head -1; git --version; uname -a'],text=True))
# Fix methodology wording to match the balanced rotation actually executed.
p=r/'METHODOLOGY.md';p.write_text(p.read_text(encoding='utf-8-sig').replace('rotating and reversing revision order','balanced rotating revision order'))
