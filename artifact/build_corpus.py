"""Deterministically generate a compact, semantic-in-scope OAS corpus."""
from pathlib import Path
import json, sys
from dataclasses import asdict
from spec_oracle import Case, generate_spec, serialize, style_default, explode_default

VALUES={
 'words': {'scalar':'azure','array':['red','blue'],'object':{'a':'red','b':'blue'}},
 'numeric': {'scalar':7,'array':[1,2,3],'object':{'a':1,'b':2}},
 'singleton': {'scalar':'z','array':['z'],'object':{'a':'z'}}
}

def make_cases():
    cases=[]; n=0
    def add(loc,style,kind,ex,profile,variant, pair=None):
        nonlocal n
        n+=1
        # omit flag variants only used where relevant defaults are the same
        omit_style=variant in ('omit_style','omit_both')
        omit_explode=variant in ('omit_explode','omit_both')
        cases.append(Case(f'c{n:03}',loc,style,kind,ex,VALUES[profile][kind],omit_style,omit_explode,profile,pair))
    for profile in VALUES:
        for location,styling in [('query','form'),('path','simple'),('path','label'),('path','matrix'),('header','simple')]:
            for kind in ('scalar','array','object'):
                for ex in ([False,True] if kind!='scalar' else [explode_default(styling)]):
                    pair=f'{profile}-{location}-{styling}-{kind}-default' if styling==style_default(location) and ex==explode_default(styling) else None
                    add(location,styling,kind,ex,profile,'explicit',pair)
                    # Metamorphic pair: explicit defaults vs both omitted.
                    if pair: add(location,styling,kind,ex,profile,'omit_both',pair)
        for sty in ('spaceDelimited','pipeDelimited'):
            for kind in ('array','object'):
                add('query',sty,kind,False,profile,'explicit')
        add('query','deepObject','object',True,profile,'explicit')
    return cases


def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent/'outputs'/'corpus'
    root.mkdir(parents=True,exist_ok=True)
    cases=make_cases()
    for c in cases:
        (root/f'{c.id}.json').write_text(json.dumps(generate_spec(c),indent=2)+'\n')
    index=[]
    for c in cases:
        u,h=serialize(c)
        index.append({**asdict(c),'expected_url':u,'expected_headers':h,'spec_file':c.id+'.json'})
    (root/'manifest.json').write_text(json.dumps(index,indent=2)+'\n')
    # Pair audit: no metamorphic pair accepted unless both specs differ and the wire contracts coincide.
    pairs={}
    for c in cases:
        if c.pair:pairs.setdefault(c.pair,[]).append(c)
    for pair,group in pairs.items():
        assert len(group)==2, (pair,len(group))
        e1=serialize(group[0]);e2=serialize(group[1]);
        # URLs use distinct probe IDs. Compare suffix after ID, and headers.
        assert e1[0].replace(group[0].id,'X')==e2[0].replace(group[1].id,'X') and e1[1]==e2[1],pair
        assert generate_spec(group[0])!=generate_spec(group[1]), pair
    print(json.dumps({'cases':len(cases),'explicit_implicit_pairs':len(pairs),'profiles':list(VALUES)},indent=2))

if __name__=='__main__': main()
