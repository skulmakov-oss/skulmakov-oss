from pathlib import Path
source=Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-002/map_scale.rs').read_text()
old='let tail=if kind=="replace" {format!("i = 0; while i < {n} {{ m = map_set(m,i,i+1); i=i+1; }} assert(map_get(m,{},-1)=={n});",n-1)}'
new='let tail=if kind=="snapshot" {format!("let old: Map(i32,i32)=m; i=0; while i < {n} {{ m=map_set(m,i,i+1); i=i+1; }} assert(map_get(old,{},-1)=={}); assert(map_get(m,{},-1)=={n});",n-1,n-1,n-1)} else if kind=="replace" {format!("i = 0; while i < {n} {{ m = map_set(m,i,i+1); i=i+1; }} assert(map_get(m,{},-1)=={n});",n-1)}'
assert old in source
source=source.replace(old,new)
Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SEM-RVM-002/map_snapshot.rs').write_text(source)
for model in ['reference','prototype']:
    Path(f'/home/WSL_USER/sem-rvm002-{model}/crates/sm-vm/examples/map_snapshot.rs').write_text(source)
