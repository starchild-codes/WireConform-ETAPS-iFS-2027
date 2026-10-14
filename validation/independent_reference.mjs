/** Independently engineered, dependency-free second reference implementation.
 * Scope strictly nonempty RFC3986-unreserved tokens in the frozen corpus.
 * This file does not import/use the Python oracle or its expected outputs.
 * Its agreement alone is not normative proof: frozen spec examples are a third check.
 */
import fs from 'node:fs';

const lines = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const enc = x => encodeURIComponent(String(x));
const flat = x => Array.isArray(x) ? x.map(String) : typeof x === 'object' ? Object.entries(x).flatMap(([a,b])=>[a,String(b)]) : [String(x)];
function secondReference(c) {
 const {location,kind,style,explode,value,id}=c;
 const name=location==='header' ? 'X-Test-Param' : 'item';
 const arr=flat(value);
 const prefix=`/cases/${id}`;
 if (location==='query') {
   let parts=[];
   if(style==='deepObject') {
     if(kind!=='object'||!explode) throw Error('invalid deepObject');
     parts=Object.entries(value).map(([k,v])=>`${enc(`${name}[${k}]`)}=${enc(v)}`);
   } else if(style==='form') {
     if(kind==='scalar') parts=[`${enc(name)}=${enc(value)}`];
     else if(explode&&kind==='array') parts=value.map(v=>`${enc(name)}=${enc(v)}`);
     else if(explode&&kind==='object') parts=Object.entries(value).map(([k,v])=>`${enc(k)}=${enc(v)}`);
     else parts=[`${enc(name)}=${arr.map(enc).join(',')}`];
   } else if(style==='pipeDelimited'||style==='spaceDelimited') {
     const delimiter=style==='pipeDelimited'?'%7C':'%20';
     parts=[`${enc(name)}=${arr.map(enc).join(delimiter)}`];
   } else throw Error('query style invalid');
   return {url:prefix+'?'+parts.join('&'),headers:{}};
 }
 let payload='';
 if(style==='simple') {
    payload=kind==='object'&&explode ? Object.entries(value).map(([k,v])=>`${enc(k)}=${enc(v)}`).join(',') : arr.map(enc).join(',');
 } else if(style==='label') {
    const joiner=explode?'.':',';
    const pieces=kind==='object'&&explode?Object.entries(value).map(([k,v])=>`${enc(k)}=${enc(v)}`):arr.map(enc);
    payload='.'+pieces.join(joiner);
 } else if(style==='matrix') {
    if(kind==='object'&&explode) payload=Object.entries(value).map(([k,v])=>`;${enc(k)}=${enc(v)}`).join('');
    else if(kind==='array'&&explode) payload=value.map(v=>`;${enc(name)}=${enc(v)}`).join('');
    else payload=`;${enc(name)}=${arr.map(enc).join(',')}`;
 } else throw Error('path or header style invalid');
 if(location==='header') return {url:prefix,headers:{[name]:payload}};
 if(location==='path') return {url:`${prefix}/p/${payload}`,headers:{}};
 throw Error('location invalid');
}
let agreement=0;
let disagreement=[];
for(const c of lines){
 const actual=secondReference(c);
 if(actual.url===c.expected_url && JSON.stringify(actual.headers)===JSON.stringify(c.expected_headers)) agreement++;
 else disagreement.push({id:c.id,reference:actual,python:{url:c.expected_url,headers:c.expected_headers}});
}
const report={kind:'INDEPENDENT_REFERENCE_AGREEMENT_NOT_GENERATOR_RESULTS',cases:lines.length,agreement,disagreement};
if(process.argv[3]) fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({cases:lines.length,agreement,disagreement:disagreement.length}));
if(disagreement.length)process.exitCode=1;
