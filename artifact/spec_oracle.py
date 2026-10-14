"""Restricted, auditable OpenAPI 3.1 parameter-serialization oracle.

Domain: nonempty string/number scalars and flat arrays/objects containing
RFC3986 unreserved ASCII tokens; no nested structures, nulls, empty values,
allowReserved, reserved-character user data or multipart content.
Based on OpenAPI 3.1.1 section 4.8.12 and the normative examples table.
The 3.1.0 table disagrees with RFC 6570 for label/explode=false;
3.1.1 aligns with RFC 6570. This corpus explicitly declares 3.1.1.
This is NOT a general-purpose OpenAPI implementation.
"""
from dataclasses import dataclass, asdict
from urllib.parse import quote, unquote, urlsplit, parse_qsl
import re


@dataclass(frozen=True)
class Case:
    id: str
    location: str
    style: str
    kind: str
    explode: bool
    value: object
    omit_style: bool = False
    omit_explode: bool = False
    profile: str = 'words'
    pair: str | None = None


def plain(v):
    s = str(v)
    assert s and all(c.isalnum() or c in '-._~' for c in s) and s.isascii(), ("outside oracle scope", s)
    return s


def flattened(value):
    if isinstance(value, dict):
        return [plain(x) for pair in value.items() for x in pair]
    if isinstance(value, list):
        return [plain(x) for x in value]
    return [plain(value)]


def style_default(location):
    return {'query': 'form', 'path': 'simple', 'header': 'simple'}[location]


def explode_default(style):
    return style == 'form'


def serialize(case):
    """Return (expected URL path with optional query, expected headers)."""
    style, kind, value, exp, loc = case.style, case.kind, case.value, case.explode, case.location
    n = 'item' if loc != 'header' else 'X-Test-Param'
    scalar = kind == 'scalar'
    vals = flattened(value)
    assert (kind, type(value)) in [('scalar', str), ('array', list), ('object', dict)] or (kind == 'scalar' and isinstance(value, int))
    if loc == 'query':
        if style == 'form':
            if scalar: pairs = [(n, vals[0])]
            elif kind == 'array': pairs = [(n, z) for z in vals] if exp else [(n, ','.join(vals))]
            else: pairs = list(zip(value.keys(), [plain(v) for v in value.values()])) if exp else [(n, ','.join(vals))]
        elif style in ('spaceDelimited', 'pipeDelimited'):
            assert not exp and kind in ('array','object')
            pairs = [(n, (' ' if style=='spaceDelimited' else '|').join(vals))]
        elif style == 'deepObject':
            assert exp and kind=='object'
            pairs = [(f'{n}[{k}]', plain(v)) for k,v in value.items()]
        else: raise ValueError(style)
        # Quote all reserved characters; delimiters introduced by style are encoded.
        query = '&'.join(f'{quote(str(k),safe="-._~")}={quote(str(v),safe="-._~,") if style=="form" and not exp else quote(str(v),safe="-._~")}' for k,v in pairs)
        # A comma produced by form explode=false is a literal RFC6570 delimiter.
        return f'/cases/{case.id}?{query}', {}
    if loc in ('path', 'header'):
        if style == 'simple':
            if kind=='object' and exp: v = ','.join(f'{plain(k)}={plain(x)}' for k,x in value.items())
            else: v = ','.join(vals)
        elif style == 'label' and loc=='path':
            if kind=='object' and exp: v = '.' + '.'.join(f'{plain(k)}={plain(x)}' for k,x in value.items())
            elif kind=='array' and exp: v = '.'+'.'.join(vals)
            else: v='.'+','.join(vals)
        elif style == 'matrix' and loc=='path':
            if kind=='object' and exp: v=''.join(f';{plain(k)}={plain(x)}' for k,x in value.items())
            elif kind=='array' and exp: v=''.join(f';{n}={x}' for x in vals)
            else: v=f';{n}='+','.join(vals)
        else: raise ValueError((loc, style))
        if loc == 'path': return f'/cases/{case.id}/p/{v}', {}
        return f'/cases/{case.id}', {'X-Test-Param': v}
    raise ValueError(loc)


def generate_spec(case):
    """One-case OAS 3.1.0 spec; generated client executes GET operation once."""
    pname = 'X-Test-Param' if case.location=='header' else 'item'
    p = {'name':pname, 'in':case.location, 'required':case.location=='path'}
    if not case.omit_style: p['style'] = case.style
    if not case.omit_explode: p['explode'] = case.explode
    if case.kind=='scalar': schema={'type':'integer' if isinstance(case.value,int) else 'string'}
    elif case.kind=='array': schema={'type':'array','items': {'type':'integer' if isinstance(case.value[0],int) else 'string'}}
    else:
        schema={'type':'object','properties': {k: {'type':'integer' if isinstance(v,int) else 'string'} for k,v in case.value.items()}, 'additionalProperties':False}
    p['schema']=schema
    path=f'/cases/{case.id}/p/{{item}}' if case.location=='path' else f'/cases/{case.id}'
    return {'openapi':'3.1.1','info':{'title':'WireConform restricted probe','version':'0.1.0'},
            'servers':[{'url':'http://127.0.0.1:8765'}],
            'paths':{path:{'get':{'operationId':'probe','parameters':[p],
                      'responses':{'204': {'description':'Recorded request'}}}}}}


def compare_observation(case, actual_url, actual_headers):
    """Return a result with explainable, independently inspectable components."""
    expected_url, expected_headers = serialize(case)
    au, eu = urlsplit(actual_url), urlsplit(expected_url)
    # Query pair ordering is semantically irrelevant; multiplicity is preserved.
    ap=sorted(parse_qsl(au.query,keep_blank_values=True))
    ep=sorted(parse_qsl(eu.query,keep_blank_values=True))
    path_ok=au.path==eu.path
    query_ok=ap==ep
    # Decoding can erase distinctions that matter for structural delimiters
    # (e.g. comma vs %2C, or literal '[' vs required %5B).
    # Do NOT count such cases as passes or normative failures automatically.
    def normraw(q):
        parts=q.split('&') if q else []
        return sorted(re.sub(r'%[0-9a-fA-F]{2}', lambda m:m.group(0).upper(), part) for part in parts)
    query_raw_exact=normraw(au.query)==normraw(eu.query)
    path_decoded_equivalent=unquote(au.path)==unquote(eu.path)
    needs_encoding_review=(query_ok and not query_raw_exact) or (not path_ok and path_decoded_equivalent)
    hs={k.lower():str(v).strip() for k,v in actual_headers.items()}
    header_ok=all(hs.get(k.lower())==v for k,v in expected_headers.items())
    return {'case_id':case.id,'pass':path_ok and query_ok and header_ok,
            'path_ok':path_ok,'query_ok':query_ok,'header_ok':header_ok,
            'query_raw_exact':query_raw_exact,'needs_encoding_review':needs_encoding_review,
            'path_decoded_equivalent':path_decoded_equivalent,
            'expected_url':expected_url,'observed_url':actual_url,
            'expected_query_pairs':ep,'observed_query_pairs':ap,
            'expected_headers':expected_headers,
            'observed_parameter_headers':{k:hs.get(k.lower()) for k in expected_headers}}
