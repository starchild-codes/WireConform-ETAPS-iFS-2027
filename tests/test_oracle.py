import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'artifact'))
from spec_oracle import Case,serialize,compare_observation,generate_spec
from build_corpus import make_cases


def mk(style,kind,val,explode=False,loc='query'):
 return Case('c000',loc,style,kind,explode,val)

def test_official_examples_form():
 assert serialize(mk('form','array',['blue','black','brown'],True))[0].endswith('?item=blue&item=black&item=brown')
 assert serialize(mk('form','array',['blue','black','brown'],False))[0].endswith('?item=blue,black,brown')
 assert serialize(mk('form','object',{'R':100,'G':200,'B':150},True))[0].endswith('?R=100&G=200&B=150')
 assert serialize(mk('form','object',{'R':100,'G':200,'B':150},False))[0].endswith('?item=R,100,G,200,B,150')

def test_official_examples_path():
 obj={'R':100,'G':200,'B':150}
 assert serialize(mk('matrix','object',obj,True,'path'))[0].endswith('/;R=100;G=200;B=150')
 assert serialize(mk('label','object',obj,True,'path'))[0].endswith('/.R=100.G=200.B=150')
 assert serialize(mk('simple','object',obj,True,'path'))[0].endswith('/R=100,G=200,B=150')
 assert serialize(mk('matrix','array',['blue','black'],True,'path'))[0].endswith('/;item=blue;item=black')
 assert serialize(mk('label','array',['blue','black'],True,'path'))[0].endswith('/.blue.black')

def test_non_rfc_form_styles():
 assert serialize(mk('spaceDelimited','array',['blue','black']))[0].endswith('item=blue%20black')
 assert serialize(mk('pipeDelimited','array',['blue','black']))[0].endswith('item=blue%7Cblack')
 assert serialize(mk('deepObject','object',{'a':'red','b':'blue'},True))[0].endswith('?item%5Ba%5D=red&item%5Bb%5D=blue')

def test_multi_value_query_multiplicity_matters():
 c=mk('form','array',['red','blue'],True)
 assert compare_observation(c,'/cases/c000?item=blue&item=red',{})['pass']
 assert not compare_observation(c,'/cases/c000?item=red',{})['pass']
 assert not compare_observation(c,'/cases/c000?item=red,blue',{})['pass']

def test_header_case_insensitive():
 c=mk('simple','object',{'a':'red','b':'blue'},True,'header')
 assert compare_observation(c,'/cases/c000',{'x-test-param':'a=red,b=blue'})['pass']
 assert not compare_observation(c,'/cases/c000',{'x-test-param':'a=red'})['pass']

def test_emitted_specs_have_required_fields():
 for c in make_cases():
    doc=generate_spec(c)
    assert doc['openapi']=='3.1.1'
    path,methods=next(iter(doc['paths'].items()))
    p=methods['get']['parameters'][0]
    assert p['name'] in ('item','X-Test-Param')
    assert p['in']==c.location
    assert p['required']==(c.location=='path')
    assert ('style' not in p)==c.omit_style
    assert ('explode' not in p)==c.omit_explode

def test_every_case_round_trips_through_scorer():
 for c in make_cases():
    url, headers=serialize(c)
    result=compare_observation(c,url,headers)
    assert result['pass'], c.id


def test_corrupted_paths_are_rejected():
 for c in make_cases():
    url, headers=serialize(c)
    assert not compare_observation(c,url.replace(f'/cases/{c.id}',f'/cases/different-{c.id}'),headers)['pass'], c.id


def test_encoded_structural_delimiter_requires_manual_triage():
 c=mk('form','array',['red','blue'],False)
 url,_=serialize(c)
 alt=url.replace('red,blue','red%2Cblue')
 result=compare_observation(c,alt,{})
 assert result['query_ok'] and result['needs_encoding_review']
 assert not result['query_raw_exact']

def test_query_pair_reordering_does_not_require_triage():
 c=mk('form','array',['red','blue'],True)
 result=compare_observation(c,'/cases/c000?item=blue&item=red',{})
 assert result['pass'] and result['query_raw_exact'] and not result['needs_encoding_review']

def test_encoded_path_separator_quarantined():
    c=mk('label','array',['red','blue'],False,'path')
    url,h=serialize(c)
    from score import compare_observation as compare
    result=compare(c,url.replace('red,blue','red%2Cblue'),{})
    assert result['needs_encoding_review'] and result['path_decoded_equivalent']
