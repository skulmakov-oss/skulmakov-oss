from pathlib import Path
source=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-001/repo/crates/sm-vm/examples/map_cost.rs').read_text()
for model in ['reference','prototype']:
    text=source.replace('host.output.contains("ok:int:14")','host.output == "ok:int:14"')
    if model=='prototype': text=text.replace('.collect(),','.collect::<Vec<_>>().into(),')
    Path(f'/home/WSL_USER/sem-rvm002-{model}/crates/sm-vm/examples/map_cost.rs').write_text(text)
