import sys,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'artifact'))
from build_corpus import make_cases
from spec_oracle import serialize
from metamorphic import analyze
from score import main as scorer_main
from mutation_control import evaluate

def run_fixture(path, rows):
    Path(path).write_text(''.join(json.dumps(x)+'\n' for x in rows))

def test_metamorphic_all_equal_then_unequal(tmp_path):
    cases=make_cases(); manifest=tmp_path/'manifest.json'; obs=tmp_path/'obs.jsonl'
    from dataclasses import asdict
    manifest.write_text(json.dumps([asdict(c) for c in cases]))
    rows=[{'case_id':c.id,'url':serialize(c)[0],'headers':serialize(c)[1]} for c in cases]
    run_fixture(obs,rows)
    result=analyze(manifest,obs)
    assert result['summary']['statuses']=={'EQUAL':27}
    a=next(c for c in cases if c.location=='query' and c.style=='form' and c.kind=='array' and c.omit_explode and len(c.value)>1)
    row=next(r for r in rows if r['case_id']==a.id)
    row['url']=row['url'].replace('&item=',',')
    run_fixture(obs,rows)
    assert analyze(manifest,obs)['summary']['statuses']=={'EQUAL':26,'UNEQUAL':1}

def test_scorer_quarantines_encoded_path(tmp_path):
    cases=make_cases();c=next(c for c in cases if c.location=='path' and c.style=='label' and c.kind=='array' and not c.explode and len(c.value)>1)
    from dataclasses import asdict
    manifest=tmp_path/'m.json';manifest.write_text(json.dumps([asdict(c)]))
    url,h=serialize(c)
    obs=tmp_path/'o.jsonl';run_fixture(obs,[{'case_id':c.id,'url':url.replace(',','%2C'),'headers':h}])
    out=tmp_path/'out.json';scorer_main(manifest,obs,out)
    assert json.loads(out.read_text())['summary']['status_counts']=={'ENCODING_REVIEW':1}

def test_synthetic_mutants_are_nontrivially_detected(tmp_path):
    from dataclasses import asdict
    m=tmp_path/'m.json';m.write_text(json.dumps([asdict(c) for c in make_cases()]))
    result=evaluate(m)
    assert result['total_mutant_cases']==25 and result['total_detected']==21
