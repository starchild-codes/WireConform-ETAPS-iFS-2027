"""Evaluation of implicit-vs-explicit default metamorphic relation MR-D.

This tool only consumes captured wire requests. It does not compute them.
"""
from collections import defaultdict,Counter
from pathlib import Path
from urllib.parse import parse_qsl,urlsplit,unquote
import json,sys,re


def normalize(record, cid):
    u=urlsplit(record['url']); p=u.path.replace('/cases/'+cid,'/cases/CASE',1)
    query=tuple(sorted(parse_qsl(u.query,keep_blank_values=True)))
    rawquery=tuple(sorted(re.sub(r'%[0-9a-fA-F]{2}',lambda m:m.group().upper(),p) for p in u.query.split('&') if p))
    h={k.lower():str(v).strip() for k,v in record.get('headers',{}).items()}
    return {'path':p,'path_decoded':unquote(p),'query':query,'query_raw':rawquery,
            'header':h.get('x-test-param',None)}

def analyze(manifest_path, capture_path):
    manifest=json.loads(Path(manifest_path).read_text()); observations=defaultdict(list)
    for line in Path(capture_path).read_text().splitlines():
        if line.strip():
            obj=json.loads(line);observations[obj.get('case_id')].append(obj)
    pairs=defaultdict(list)
    for c in manifest:
        if c.get('pair'):pairs[c['pair']].append(c)
    results=[]
    for pair,cs in sorted(pairs.items()):
        assert len(cs)==2,(pair,cs)
        a,b=cs
        oa,ob=observations[a['id']],observations[b['id']]
        if len(oa)!=1 or len(ob)!=1:
            status='INELIGIBLE';reason=f'observation counts {len(oa)}/{len(ob)}'
        else:
            va,vb=normalize(oa[0],a['id']),normalize(ob[0],b['id'])
            if va==vb:
                status='EQUAL';reason=''
            elif va['path_decoded']==vb['path_decoded'] and va['query']==vb['query'] and va['header']==vb['header']:
                status='ENCODING_REVIEW';reason='decoded equivalent but raw bytes differ'
            else:
                status='UNEQUAL';reason='normalized on-wire values differ'
        results.append({'pair':pair,'left':a['id'],'right':b['id'],'status':status,'reason':reason})
    return {'summary':{'pairs':len(results),'statuses':dict(Counter(x['status'] for x in results))},'pairs':results}

if __name__=='__main__':
    result=analyze(sys.argv[1],sys.argv[2]); Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['summary'],indent=2))
