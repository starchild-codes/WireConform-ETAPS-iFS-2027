"""Independent structural/semantic audit of the restricted OpenAPI corpus.

Not a substitute for official JSON-Schema-based OpenAPI validation. Works offline.
The checks below do not call generate_spec or serialize.
"""
import collections
import json
from pathlib import Path
import sys

VALID = {'query': {'form','spaceDelimited','pipeDelimited','deepObject'},
         'path': {'simple','label','matrix'},'header':{'simple'}}
DEFAULT_STYLES = {'query':'form','path':'simple','header':'simple'}


def audit(root):
    root=Path(root)
    records=json.loads((root/'manifest.json').read_text())
    problems=[]; groups=collections.defaultdict(list); counts=collections.Counter()
    visited=set()
    def issue(case, msg): problems.append(f'{case}: {msg}')
    for r in records:
        id=r['id']; groups[r['pair']].append(r) if r['pair'] else None
        counts[r['location']]+=1
        f=root/r['spec_file']
        if id in visited:issue(id,'duplicate ID')
        visited.add(id)
        try:d=json.loads(f.read_text())
        except Exception as e:issue(id,f'parse/file error {e}');continue
        if d.get('openapi')!='3.1.1': issue(id,'version')
        if not d.get('info',{}).get('title') or not d.get('info',{}).get('version'):issue(id,'info')
        if d.get('servers')!=[{'url':'http://127.0.0.1:8765'}]:issue(id,'unexpected server')
        paths=d.get('paths',{})
        if len(paths)!=1:issue(id,'not one path');continue
        path,methods=next(iter(paths.items()))
        if set(methods)!={'get'}:issue(id,'not single GET');continue
        op=methods['get']
        if op.get('operationId')!='probe': issue(id,'operation')
        if not op.get('responses',{}).get('204',{}).get('description'):issue(id,'response missing description')
        params=op.get('parameters',[])
        if len(params)!=1:issue(id,'parameters count');continue
        p=params[0]
        loc=r['location'];style=r['style'];expl=r['explode'];kind=r['kind'];value=r['value']
        name='X-Test-Param' if loc=='header' else 'item'
        if loc not in VALID or style not in VALID[loc]: issue(id,f'invalid location/style {loc}/{style}')
        if p.get('name')!=name or p.get('in')!=loc:issue(id,'wrong parameter name/location')
        if p.get('required')!=(loc=='path'): issue(id,'path must be required')
        if p.get('style',DEFAULT_STYLES.get(loc))!=style: issue(id,'incorrect effective style')
        if p.get('explode',style=='form')!=expl: issue(id,'incorrect effective explode')
        if ('style' not in p)!=r['omit_style']:issue(id,'omitted style flag wrong')
        if ('explode' not in p)!=r['omit_explode']:issue(id,'omitted explode flag wrong')
        if 'content' in p:issue(id,'schema/content alternative forbidden')
        if not isinstance(value,(str,int,list,dict)) or isinstance(value,bool):issue(id,'bad value class')
        if (kind=='array')!=(isinstance(value,list)):issue(id,'array mismatch')
        if (kind=='object')!=(isinstance(value,dict)):issue(id,'object mismatch')
        s=p.get('schema',{})
        typ={'array':'array','object':'object','scalar': 'integer' if isinstance(value,int) else 'string'}[kind]
        if s.get('type')!=typ: issue(id,'schema type mismatch')
        if kind=='array':
            if not value or s.get('items',{}).get('type')!=('integer' if isinstance(value[0],int) else 'string'):issue(id,'array items')
        if kind=='object':
            if not value or set(s.get('properties',{}))!=set(value) or s.get('additionalProperties') is not False:issue(id,'object properties')
        if loc=='path' and path!=f'/cases/{id}/p/{{item}}':issue(id,'path template missing/malformed')
        if loc!='path' and path!=f'/cases/{id}':issue(id,'unexpected path template')
        if style in ('spaceDelimited','pipeDelimited') and (loc!='query' or expl):issue(id,'unsupported delimited style')
        if style=='deepObject' and (kind!='object' or not expl):issue(id,'undefined deepObject')
    if len(records)!=117:issue('corpus',f'expected 117, observed {len(records)}')
    if len(groups)!=27:issue('corpus',f'expected 27 pairs observed {len(groups)}')
    for key,rs in groups.items():
        if len(rs)!=2:issue(key,'not pair of two');continue
        a,b=rs
        for k in ('location','style','kind','explode','value','profile'):
            if a[k]!=b[k]:issue(key,f'mismatched metamorphic {k}')
        if not (a['omit_style']!=b['omit_style'] and a['omit_explode']!=b['omit_explode']):issue(key,'pair does not vary both omissions')
    return {'n_cases':len(records),'counts_by_location':dict(counts),'n_metamporphic_pairs':len(groups),
            'n_problems':len(problems),'problems':problems,
            'scope':'offline structural and restricted semantic checks only; NOT official full OpenAPI 3.1 schema validation'}

if __name__=='__main__':
    report=audit(sys.argv[1])
    if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    sys.exit(1 if report['n_problems'] else 0)
