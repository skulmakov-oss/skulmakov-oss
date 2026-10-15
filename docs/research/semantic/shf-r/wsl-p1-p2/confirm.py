import pathlib,statistics,json,csv
r=pathlib.Path('/home/WSL_USER/shf-r-comparison-20261015')
code=(r/'measure.py').read_text();prefix=code[:code.index('for idx,(f,n) in enumerate(cases):')]
ns={};exec(compile(prefix,'frozen-measure-prefix','exec'),ns);measure=ns['measure']
results=[]
for family,n in [(f,32000) for f in ['map_set','map_get','map_versions','state_record_map','seq_push','seq_read','record_with','text_scan']]+[('map_set',n) for n in [1000,4000,16000]]+[('lex_calls',16000)]:
    for label in ['p1','p2']:measure(label,family,n,-1,'confirmation-warm')
    for trial in range(6):
        for label in (['p1','p2'] if trial%2==0 else ['p2','p1']):
            x=measure(label,family,n,trial,'confirmation');results.append(x)
    print('CONFIRMED SERIES',family,n,flush=True)
(r/'confirmation.json').write_text(json.dumps(results,indent=2))
with (r/'confirmation.csv').open('w') as out:
    w=csv.writer(out);w.writerow(['family','N','revision','median_ms','min_ms','max_ms','successes'])
    for family,n in sorted(set((x['family'],x['n']) for x in results)):
        for label in ['p1','p2']:
            xs=[x for x in results if x['family']==family and x['n']==n and x['revision']==label]
            good=[x['wall_ms'] for x in xs if x['exit']==0 and not x['timeout'] and x['metrics'] and x['metrics']['outcome']=='ok']
            w.writerow([family,n,label,statistics.median(good) if len(good)==6 else '',min(good) if good else '',max(good) if good else '',len(good)])
print('CONFIRMATIONS COMPLETE',flush=True)

