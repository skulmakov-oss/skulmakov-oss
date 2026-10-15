import pathlib,json,collections
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015');rows=[json.loads(x) for x in (r/'measurements.jsonl').read_text().splitlines()]
print('ROWS',len(rows));print('outcomes',collections.Counter('TIMEOUT' if x['timeout'] else (x['metrics'] or {}).get('outcome','NO METRICS') for x in rows))
for kind in ['calls-default-steps','capability-denial']:
 for x in rows:
  if x['kind']==kind:print(kind,x['revision'],x['metrics'])
phases=[json.loads(x) for x in (r/'phases.jsonl').read_text().splitlines()];print('PHASES',len(phases),collections.Counter((x['kind'],x['exit']) for x in phases))
for x in phases:
 if x['kind']=='parity-run' and x['exit']!=0:print('PARITY FAILURE',x['family'],x['revision'],x['opt'],pathlib.Path(x['stderr']).read_text()[:220])
