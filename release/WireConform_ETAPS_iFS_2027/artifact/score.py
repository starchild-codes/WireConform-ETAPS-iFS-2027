"""Score captured wire observations against the manifest; never conflate failures."""
import json,sys,collections
from pathlib import Path
from spec_oracle import Case,compare_observation


def main(manifest,observations,destination):
    cases={c['id']:Case(**{k:c[k] for k in ('id','location','style','kind','explode','value','omit_style','omit_explode','profile','pair')}) for c in json.loads(Path(manifest).read_text())}
    rows=[json.loads(s) for s in Path(observations).read_text().splitlines() if s.strip()]
    grouped=collections.defaultdict(list)
    for o in rows:
        if o['case_id'] in cases:
            grouped[o['case_id']].append(o)
    detailed=[]
    for c_id,case in cases.items():
        obs=grouped.get(c_id,[])
        if not obs:
            detailed.append({'case_id':c_id,'status':'NOT_RUN'});continue
        if len(obs)!=1:
            detailed.append({'case_id':c_id,'status':'INVALID_MULTIPLE_OBSERVATIONS','count':len(obs)});continue
        comp=compare_observation(case,obs[0]['url'],obs[0].get('headers',{}))
        status=('ENCODING_REVIEW' if comp['needs_encoding_review'] and comp['query_ok'] and comp['header_ok']
                and (comp['path_ok'] or comp['path_decoded_equivalent']) else ('PASS' if comp['pass'] else 'FAIL'))
        detailed.append({**comp,'status':status})
    counts=dict(collections.Counter(c['status'] for c in detailed))
    summary={'n_defined':len(cases),'n_observations':len(rows),'status_counts':counts,
             'note':'NOT_RUN, INVALID_MULTIPLE_OBSERVATIONS, and ENCODING_REVIEW are excluded from untriaged conformance pass rates'}
    Path(destination).write_text(json.dumps({'summary':summary,'cases':detailed},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main(*sys.argv[1:4])
