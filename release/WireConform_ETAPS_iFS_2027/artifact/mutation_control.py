"""Synthetic, explicitly non-generator mutation sensitivity controls.

Generates malformed wire requests from a correct contract to ensure a corpus +
scorer detects plausible categories of implementation deviations. These are
controlled fault injections, NOT findings about any real generator.
"""
from collections import Counter
from dataclasses import replace
from pathlib import Path
import json,sys
from spec_oracle import Case, serialize, compare_observation


def affected(c, mutant):
    return {
     'ignore_form_array_explode': c.location=='query' and c.style=='form' and c.kind=='array' and c.explode,
     'omit_default_array_explode': c.location=='query' and c.style=='form' and c.kind=='array' and c.explode and c.omit_explode,
     'ignore_label_object_explode': c.location=='path' and c.style=='label' and c.kind=='object' and c.explode,
     'ignore_matrix_array_explode': c.location=='path' and c.style=='matrix' and c.kind=='array' and c.explode,
     'discard_last_exploded_pair': c.location=='query' and c.style=='form' and c.kind=='array' and c.explode and len(c.value)>1,
     'header_object_nonexploded': c.location=='header' and c.style=='simple' and c.kind=='object' and c.explode,
     'flatten_deep_object': c.location=='query' and c.style=='deepObject' and c.kind=='object'
    }[mutant]


def mutated(c, mutant):
    if mutant=='flatten_deep_object':
        from urllib.parse import quote
        u,_=serialize(c);return u.split('?',1)[0]+'?item='+quote(','.join(f'{k},{v}' for k,v in c.value.items()),safe=','),{}
    if mutant=='discard_last_exploded_pair':
        u,_=serialize(c);return u.rsplit('&',1)[0],{}
    u,h=serialize(replace(c,explode=False))
    return u,h

def evaluate(manifest):
    rows=json.loads(Path(manifest).read_text()); names=['ignore_form_array_explode','omit_default_array_explode','ignore_label_object_explode','ignore_matrix_array_explode','discard_last_exploded_pair','header_object_nonexploded','flatten_deep_object']
    report=[]
    for m in names:
        scores=[];examples=[]
        for r in rows:
            c=Case(**{k:r[k] for k in ('id','location','style','kind','explode','value','omit_style','omit_explode','profile','pair')})
            if not affected(c,m):continue
            url,h=mutated(c,m)
            result=compare_observation(c,url,h)
            detectable=not result['pass'] and not result['needs_encoding_review']
            scores.append(detectable)
            if not detectable:examples.append({'case_id':c.id,'url':url,'reason':result})
        report.append({'mutant':m,'eligible':len(scores),'detected':sum(scores),'undetected':len(scores)-sum(scores),'examples':examples[:3]})
    return {'kind':'SYNTHETIC_MUTATION_CONTROLS_NOT_REAL_CLIENT_MEASUREMENTS','mutants':report,'total_mutant_cases':sum(x['eligible'] for x in report),'total_detected':sum(x['detected'] for x in report)}

if __name__=='__main__':
    r=evaluate(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='mutants'},indent=2))
    print(json.dumps([{k:v for k,v in x.items() if k!='examples'} for x in r['mutants']],indent=2))
