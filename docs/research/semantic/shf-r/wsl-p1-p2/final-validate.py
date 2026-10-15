import pathlib,json,hashlib,collections,copy,subprocess,shutil,datetime
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015');w=pathlib.Path('/mnt/c/Users/OWNER_USER/Documents/Codex/SHF-R-WSL-20261015')
rows=[json.loads(l) for l in (r/'measurements.jsonl').read_text().splitlines()];groups=collections.defaultdict(list)
for x in rows:
 if x['kind'] in ['run','confirmation','confirmation-warm'] and x['metrics']:
  m=copy.deepcopy(x['metrics']);m.pop('nondeterministic',None)
  audit='\n'.join(line for line in pathlib.Path(x['stderr']).read_text().splitlines() if not line.startswith('{"schema":"semantic.run.metrics/'))
  groups[(x['family'],x['n'])].append((json.dumps(m,sort_keys=True),pathlib.Path(x['stdout']).read_bytes().hex(),audit,x['exit']))
differences=[str(k) for k,v in groups.items() if len(set(v))>1];assert not differences,differences
phases=[json.loads(l) for l in (r/'phases.jsonl').read_text().splitlines()];ag=collections.defaultdict(set);ac=collections.defaultdict(set)
for x in phases:
 if x['kind']=='verify-CLI':ag[(x['source'],x['revision'])].add(x['artifact_sha256']);ac[x['source']].add(x['artifact_sha256'])
assert len(ag)==138 and all(len(x)==1 for x in ag.values())
assert len(ac)==46 and all(len(x)==1 for x in ac.values())
pres=json.loads((r/'repository-preservation.json').read_text());assert pres['active_snapshot_unchanged'] and not pres['frozen_input_mismatches']
assert all(not x['status'] and x['lock_unchanged'] and x['binary_unchanged'] for x in pres['checkouts'].values())
assert pres['remote_main_final']==pres['remote_main_after_fetch']==pres['isolated_origin_main_final']
toolchains={label:(r/label/'rust-toolchain.toml').read_text() for label in ['baseline','p1','p2']};assert len(set(toolchains.values()))==1
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime_invocations':len(rows),'phase_invocations':len(phases),'normalized_completed_case_groups':len(groups),'normalized_difference_groups':differences,'within_revision_artifact_groups_stable':len(ag),'cross_revision_artifact_groups_identical':len(ac),'toolchains':toolchains,'report_sha256':None}
p=r/'REPORT.md';text=p.read_text();text=text.replace('Repeated mixed-field/nested Sequence benchmarks: NOT RUN as independent families; State5/State10 are the exact available multi-field cases.','State5/State10 cover repeated mixed scalar/Sequence field updates. A separately recorded mixed-update generator and a Record+nested-Sequence benchmark were not identified: NOT RUN as independent families.')
p.write_text(text);result['report_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(r/'REPORT.sha256').write_text(result['report_sha256']+'  REPORT.md\n');(r/'final-validation.json').write_text(json.dumps(result,indent=2))
for name in ['analysis.py','manifest-final.py','final-validate.py']:
 shutil.copy2(w/name,r/name)
(r/'harness-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.glob('*.py')},indent=2))
for name in ['REPORT.md','REPORT.sha256','final-validation.json','harness-hashes.json']:shutil.copy2(r/name,w/name)
print(json.dumps(result,indent=2))
