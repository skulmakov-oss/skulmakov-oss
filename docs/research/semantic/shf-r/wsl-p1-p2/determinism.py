import pathlib,json,collections
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015');p=[json.loads(l) for l in (r/'phases.jsonl').read_text().splitlines()]
g=collections.defaultdict(set)
for x in p:
 if x['kind']=='verify-CLI':g[(x['source'],x['revision'])].add(x['artifact_sha256'])
print('compile within-revision stable',sum(len(v)==1 for v in g.values()),'/',len(g))
by=collections.defaultdict(set)
for (source,label),v in g.items():by[source].update(v)
print('cross revision artifact identity',sum(len(v)==1 for v in by.values()),'/',len(by))
rows=[json.loads(l) for l in (r/'measurements.jsonl').read_text().splitlines()];gg=collections.defaultdict(list)
for x in rows:
 if x['kind']=='run':gg[(x['family'],x['n'])].append(x)
print('counter differences',[(k,len(set(json.dumps((x['metrics'] or {}).get('counters'),sort_keys=True) for x in v if x['metrics']))) for k,v in gg.items() if len(set(json.dumps((x['metrics'] or {}).get('counters'),sort_keys=True) for x in v if x['metrics']))>1])
