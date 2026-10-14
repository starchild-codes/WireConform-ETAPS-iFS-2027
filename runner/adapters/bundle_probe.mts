/**
 * Candidate thin invoker for genuine generated SDK operations.
 * NO HTTP serialization code and NO direct fetch/axios calls.
 * This must be reviewed against the emitted generated method signatures
 * before requests are considered admissible empirical observations.
 *
 * Usage: node --import tsx runner/adapters/bundle_probe.mts '<JSON>'
 */
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const record=JSON.parse(process.argv[2] || '{}');
const {case_id, location, value, generator, generated_dir, base_url}=record;
if(!/^c\d{3}$/.test(case_id) || !['path','query','header'].includes(location)){
  throw new Error('Invalid case metadata');
}
const method=`probeC${case_id.slice(1)}`;
const load=(p:string) => import(pathToFileURL(p).href);
const must=(p:string) => {if(!fs.existsSync(p))throw new Error(`Generated module not found: ${p}`);return p;};

if(generator==='openapi-generator'){
  const mod=await load(must(path.join(generated_dir,'index.ts')));
  const api=new mod.DefaultApi(new mod.Configuration({basePath:base_url}));
  if(typeof api[method]!=='function')throw new Error(`MISSING_SDK_OPERATION ${method}`);
  // The generated typescript-fetch API names header parameters xTestParam;
  // query and path parameters retain the OpenAPI name item.
  await api[method](location==='header' ? {xTestParam:value} : {item:value});
}else if(generator==='orval'){
  const mod=await load(must(path.join(generated_dir,'client.ts')));
  const fn=mod[method];
  if(typeof fn!=='function')throw new Error(`MISSING_SDK_OPERATION ${method}`);
  if(location==='header'){
    // Orval 8.42.0's generated Fetch operation has no typed parameter for
    // in:header. Passing RequestInit.headers would bypass generated parameter
    // serialization and is therefore scientifically inadmissible.
    throw new Error('UNSUPPORTED_GENERATED_SIGNATURE_HEADER');
  }else if(location==='path')await fn(value);
  else await fn({item:value});
}else if(generator==='hey-api'){
  const mod=await load(must(path.join(generated_dir,'sdk.gen.ts')));
  const clientmod=await load(must(path.join(generated_dir,'client.gen.ts')));
  // The spec itself fixes http://127.0.0.1:8765 as the server; changing the
  // base URL here only ensures execution stays within local-loopback scope.
  if(typeof clientmod.client?.setConfig==='function')clientmod.client.setConfig({baseUrl:base_url,baseURL:base_url});
  const fn=mod[method];
  if(typeof fn!=='function')throw new Error(`MISSING_SDK_OPERATION ${method}`);
  if(location==='path')await fn({path:{item:value}});
  else if(location==='query')await fn({query:{item:value}});
  else await fn({headers:{'X-Test-Param':value}});
}else{
  throw new Error(`Unsupported generator ${generator}`);
}
