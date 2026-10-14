"""Frozen examples transcribed from OpenAPI 3.1.1 §4.8.12.4 and RFC 6570 §3.2.

Citation: https://spec.openapis.org/oas/v3.1.1.html#style-examples
The expected strings here are handwritten constants, not generated from the oracle.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'artifact'))
import pytest
from spec_oracle import Case,serialize

A=['blue','black','brown']
O={'R':100,'G':200,'B':150}
# Values below transcribe the published normative table using parameter name 'item'.
# For header examples, the header value (not a URI) is compared.
@pytest.mark.parametrize('loc,style,exp,kind,expected',[
('path','matrix',False,'scalar',';item=blue'),
('path','matrix',False,'array',';item=blue,black,brown'),
('path','matrix',False,'object',';item=R,100,G,200,B,150'),
('path','matrix',True,'scalar',';item=blue'),
('path','matrix',True,'array',';item=blue;item=black;item=brown'),
('path','matrix',True,'object',';R=100;G=200;B=150'),
('path','label',False,'scalar','.blue'),
('path','label',False,'array','.blue,black,brown'),
('path','label',False,'object','.R,100,G,200,B,150'),
('path','label',True,'scalar','.blue'),
('path','label',True,'array','.blue.black.brown'),
('path','label',True,'object','.R=100.G=200.B=150'),
('path','simple',False,'scalar','blue'),
('path','simple',False,'array','blue,black,brown'),
('path','simple',False,'object','R,100,G,200,B,150'),
('path','simple',True,'scalar','blue'),
('path','simple',True,'array','blue,black,brown'),
('path','simple',True,'object','R=100,G=200,B=150'),
('query','form',False,'scalar','?item=blue'),
('query','form',False,'array','?item=blue,black,brown'),
('query','form',False,'object','?item=R,100,G,200,B,150'),
('query','form',True,'scalar','?item=blue'),
('query','form',True,'array','?item=blue&item=black&item=brown'),
('query','form',True,'object','?R=100&G=200&B=150'),
('query','spaceDelimited',False,'array','?item=blue%20black%20brown'),
('query','spaceDelimited',False,'object','?item=R%20100%20G%20200%20B%20150'),
('query','pipeDelimited',False,'array','?item=blue%7Cblack%7Cbrown'),
('query','pipeDelimited',False,'object','?item=R%7C100%7CG%7C200%7CB%7C150'),
('query','deepObject',True,'object','?item%5BR%5D=100&item%5BG%5D=200&item%5BB%5D=150'),
('header','simple',False,'scalar','blue'),
('header','simple',False,'array','blue,black,brown'),
('header','simple',False,'object','R,100,G,200,B,150'),
('header','simple',True,'object','R=100,G=200,B=150')
])
def test_normative_example(loc,style,exp,kind,expected):
    value = 'blue' if kind=='scalar' else A if kind=='array' else O
    c=Case('test',loc,style,kind,exp,value)
    url,headers=serialize(c)
    if loc=='query': actual='?'+url.split('?',1)[1]
    elif loc=='path':actual=url.split('/p/',1)[1]
    else:actual=headers['X-Test-Param']
    assert actual==expected, (loc,style,exp,kind,actual,expected)
