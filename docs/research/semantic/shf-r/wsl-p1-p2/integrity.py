import pathlib,json,hashlib,subprocess,collections,statistics,copy,datetime
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015');w=pathlib.Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-R-WSL-20261015')
def git(label,*args):return subprocess.check_output(['git','-C',str(r/label),*args],text=True).strip()
a=json.loads((w/'active-before.json').read_text(encoding='utf-8-sig'));b=json.loads((w/'active-after.json').read_text(encoding='utf-8-sig'))
env=json.loads((r/'environment-builds.json').read_text());pres={'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'active_repository':str(pathlib.Path('C:/Users/OWNER_USER/Desktop/EXOcode/Semantic_ui_dna2_3b_artifact_v1')),'active_snapshot_unchanged':a==b,'active_before':a,'active_after':b,'remote_main_after_fetch':'188dec7eddfafaab5926af2d30f528bfe3d89a2c','remote_main_final':(w/'remote-main-final.txt').read_text(encoding='utf-8-sig').strip(),'isolated_origin_main_final':git('git','rev-parse','origin/main'),'checkouts':{}}
for label in ['baseline','p1','p2']:
 pres['checkouts'][label]={'head':git(label,'rev-parse','HEAD'),'status':git(label,'status','--porcelain=v1','--untracked-files=all'),'lock_unchanged':hashlib.sha256((r/label/'Cargo.lock').read_bytes()).hexdigest()==env['builds'][label]['lock_sha256'],'binary_unchanged':hashlib.sha256((r/('target-'+label)/'release/smc-cli').read_bytes()).hexdigest()==env['builds'][label]['binary_sha256'],'quota_source_blob':git(label,'rev-parse','HEAD:crates/sm-runtime-core/src/lib.rs'),'cli_source_blob':git(label,'rev-parse','HEAD:crates/smc-cli/src/app.rs')}
pres['frozen_input_mismatches']=[p for p,d in json.loads((r/'input-hashes.json').read_text()).items() if hashlib.sha256((r/p).read_bytes()).hexdigest()!=d]
(r/'repository-preservation.json').write_text(json.dumps(pres,indent=2));print('PRESERVATION',json.dumps(pres,ensure_ascii=False))
rows=[json.loads(x) for x in (r/'measurements.jsonl').read_text().splitlines()]
groups=collections.defaultdict(list)
for x in rows:
 if x['kind']=='run' and x['metrics']:groups[(x['family'],x['n'])].append(x)
def normalized(x):
 m=copy.deepcopy(x['metrics']);m.pop('nondeterministic',None)
 stderr=pathlib.Path(x['stderr']).read_text();non_metrics='\n'.join(line for line in stderr.splitlines() if not line.startswith('{"schema":"semantic.run.metrics/'))
 return json.dumps(m,sort_keys=True),pathlib.Path(x['stdout']).read_bytes().hex(),non_metrics,x['exit']
differences=[str(k) for k,v in groups.items() if len(set(normalized(x) for x in v))>1]
(r/'determinism-results.json').write_text(json.dumps({'completed_primary_case_groups':len(groups),'normalized_metrics_stdout_audit_error_exit_differences':differences},indent=2));print('DETERMINISM',len(groups),differences)
confirm=json.loads((r/'confirmation.json').read_text());paired=[]
for family,n in sorted(set((x['family'],x['n']) for x in confirm)):
 ratios=[]
 for trial in range(6):
  pair={x['revision']:x for x in confirm if x['family']==family and x['n']==n and x['trial']==trial};ratios.append(pair['p2']['wall_ms']/pair['p1']['wall_ms'])
 row={'family':family,'n':n,'p2_slower_pairs':sum(v>1 for v in ratios),'pair_ratios':ratios,'median_pair_ratio':statistics.median(ratios)};paired.append(row);print('PAIRED',json.dumps(row))
(r/'confirmation-paired.json').write_text(json.dumps(paired,indent=2))
