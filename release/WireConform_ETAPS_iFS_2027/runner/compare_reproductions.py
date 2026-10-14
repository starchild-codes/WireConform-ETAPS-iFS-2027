"""Compare bundled and clean single-spec wire captures without changing scores."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read_jsonl(path):
    return {r['case_id']:r for r in (json.loads(line) for line in path.read_text().splitlines() if line.strip())}

def relevant(row):
    headers={k.lower():str(v) for k,v in row.get('headers',{}).items()}
    return {'url':row['url'],'x-test-param':headers.get('x-test-param')}

report={'status':'INDEPENDENT_SINGLE_SPEC_REPRODUCTION','phases':{}}
for phase,bundle_phase,repro_phase in (('pilot','pilot','pilot'),('full_mismatches','full','full_mismatches')):
    report['phases'][phase]={}
    for generator in ('openapi-generator','orval','hey-api'):
        bundled=read_jsonl(ROOT/'experiments'/'bundle'/generator/bundle_phase/'observations.jsonl')
        single=read_jsonl(ROOT/'experiments'/'reproduction'/generator/repro_phase/'observations.jsonl')
        # Full reproduction contains only post-adjudication mismatch IDs.
        ids=sorted(single) if phase=='full_mismatches' else sorted(set(bundled)|set(single))
        rows=[]
        for cid in ids:
            b=relevant(bundled[cid]) if cid in bundled else None
            s=relevant(single[cid]) if cid in single else None
            rows.append({'case_id':cid,'bundle':b,'single_spec':s,'exact_match':b==s})
        report['phases'][phase][generator]={
            'bundled_population_captures':len(bundled),'single_spec_captures':len(single),
            'compared':len(rows),'exact_matches':sum(r['exact_match'] for r in rows),
            'differences':[r for r in rows if not r['exact_match']],
            'rows':rows}
out=ROOT/'evidence'/'reviews'/'pilot_reproduction.json'
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({phase:{g:{k:v for k,v in d.items() if k not in {'rows','differences'}}|{'differences':len(d['differences'])}
                         for g,d in generators.items()}
                  for phase,generators in report['phases'].items()},indent=2))
