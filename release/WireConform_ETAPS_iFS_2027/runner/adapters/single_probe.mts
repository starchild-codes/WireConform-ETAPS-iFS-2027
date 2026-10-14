/** Clean single-spec reproduction adapter. Calls only the generated `probe` operation. */
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const record=JSON.parse(process.argv[2] || '{}');
const {case_id,location,value,generator,generated_dir,base_url}=record;
if(!/^c\d{3}$/.test(case_id) || !['path','query','header'].includes(location)) throw new Error('Invalid case metadata');
const load=(p:string)=>import(pathToFileURL(p).href);
const must=(p:string)=>{if(!fs.existsSync(p))throw new Error(`Generated module not found: ${p}`);return p;};

if(generator==='openapi-generator'){
  const mod=await load(must(path.join(generated_dir,'index.ts')));
  const api=new mod.DefaultApi(new mod.Configuration({basePath:base_url}));
  if(typeof api.probe!=='function')throw new Error('MISSING_SDK_OPERATION probe');
  await api.probe(location==='header' ? {xTestParam:value} : {item:value});
}else if(generator==='orval'){
  const mod=await load(must(path.join(path.dirname(generated_dir),'generated.ts')));
  if(typeof mod.probe!=='function')throw new Error('MISSING_SDK_OPERATION probe');
  if(location==='header')throw new Error('UNSUPPORTED_GENERATED_SIGNATURE_HEADER');
  if(location==='path')await mod.probe(value); else await mod.probe({item:value});
}else if(generator==='hey-api'){
  const sdk=await load(must(path.join(generated_dir,'sdk.gen.ts')));
  const clientmod=await load(must(path.join(generated_dir,'client.gen.ts')));
  clientmod.client.setConfig({baseUrl:base_url});
  if(typeof sdk.probe!=='function')throw new Error('MISSING_SDK_OPERATION probe');
  if(location==='path')await sdk.probe({path:{item:value}});
  else if(location==='query')await sdk.probe({query:{item:value}});
  else await sdk.probe({headers:{'X-Test-Param':value}});
}else throw new Error(`Unsupported generator ${generator}`);
