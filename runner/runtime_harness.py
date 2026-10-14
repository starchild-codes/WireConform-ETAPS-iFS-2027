"""Execute third-party SDK *adapters* against a genuine local HTTP capture server.

This wrapper DOES NOT generate or alter SDK code. Adapter source must be
reviewed to establish it invokes the actual generated operation with typed
values; an adapter that serializes HTTP requests itself is inadmissible.
Synthetic fixture mode exists only to test instrumentation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from http.server import HTTPServer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'artifact'))
from capture_server import Handler


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(manifest_path, adapter_path, output_dir, case_ids, *, synthetic=False, timeout=25, generation_ledger=None, generated_root=None, tsx=False, generator=None):
    manifest_path=Path(manifest_path).resolve();adapter_path=Path(adapter_path).resolve()
    output_dir=Path(output_dir).resolve();output_dir.mkdir(parents=True,exist_ok=True)
    cases={x['id']:x for x in json.loads(manifest_path.read_text())}
    for cid in case_ids:
        if cid not in cases:raise ValueError(f'unknown case {cid}')
    # Explicitly marked demo paths must never be confused with SDK results.
    if 'fixtures' in adapter_path.parts and not synthetic:
        raise ValueError('Fixture adapters require --synthetic')
    if not synthetic and (generation_ledger is None or generated_root is None):
        raise ValueError('Real trials require --generation-ledger and --generated-root')
    if not synthetic and generator not in {'openapi-generator','orval','hey-api'}:
        raise ValueError('Real trials require --generator')
    by_generation={}
    if generation_ledger:
        for gr in json.loads(Path(generation_ledger).read_text()):
            if gr['case_id'] in by_generation:raise ValueError('duplicate generation ledger ID')
            by_generation[gr['case_id']]=gr
    capture_file=output_dir/'observations.jsonl'
    capture_file.write_text('')
    srv=HTTPServer(('127.0.0.1',8765),Handler)
    srv.lock=threading.Lock();srv.output=capture_file
    thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
    ledger=[]
    try:
        for cid in case_ids:
            c=cases[cid]
            g=by_generation.get(cid)
            gen_status='SYNTHETIC_FIXTURE' if synthetic else ('UNKNOWN' if not g else g.get('status','UNKNOWN'))
            if not synthetic and (gen_status!='GENERATED' or g.get('sha256')!=sha(manifest_path.parent/c['spec_file'])):
                ledger.append({'case_id':cid,'status':'SKIPPED_GENERATION_FAILURE','generation_status':gen_status,
                               'generation_hash_valid':bool(g and g.get('sha256')==sha(manifest_path.parent/c['spec_file'])),
                               'synthetic_fixture':False})
                continue
            input_record={'case_id':cid,'value':c['value'],'location':c['location'],
                          'generator':generator,
                          'base_url':'http://127.0.0.1:8765',
                          'generated_dir':str((Path(generated_root)/cid/'generated').resolve()) if generated_root else None}
            command=['node']+(['--import','tsx'] if tsx else [])+[str(adapter_path),json.dumps(input_record,separators=(',',':'))]
            began=time.monotonic()
            prior=[json.loads(s) for s in capture_file.read_text().splitlines() if s.strip()]
            prior_count=sum(x.get('case_id')==cid for x in prior)
            try:
                proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
                status='EXECUTION_ERROR' if proc.returncode else 'NO_CAPTURE'
                code=proc.returncode;so=proc.stdout[-4000:];se=proc.stderr[-4000:]
            except subprocess.TimeoutExpired as exc:
                status='EXECUTION_TIMEOUT';code=None
                so=str(exc.stdout or '')[-4000:];se=str(exc.stderr or '')[-4000:]
            except FileNotFoundError as exc:
                status='ADAPTER_UNAVAILABLE';code=None;so='';se=str(exc)
            captured=[json.loads(s) for s in capture_file.read_text().splitlines() if s.strip()]
            fresh=sum(x.get('case_id')==cid for x in captured)-prior_count
            if status=='NO_CAPTURE':
                if fresh==1:status='CAPTURED_ONE'
                elif fresh>1:status='CAPTURED_MULTIPLE'
            ledger.append({'case_id':cid,'status':status,'generation_status':gen_status,'generation_hash_valid':not synthetic,
                           'adapter_sha256':sha(adapter_path),
                           'spec_sha256':sha(manifest_path.parent/c['spec_file']),
                           'elapsed_seconds':round(time.monotonic()-began,3),
                           'returncode':code,'new_captures':fresh,
                           'stdout_tail':so,'stderr_tail':se,
                           'synthetic_fixture':synthetic})
    finally:
        srv.shutdown();srv.server_close();thread.join(timeout=3)
    result={'synthetic_fixture':synthetic,'notice': 'SYNTHETIC: NO THIRD-PARTY GENERATOR TESTED' if synthetic else 'Adapter provenance must be independently audited',
            'observations_file':str(capture_file),'runs':ledger}
    (output_dir/'runtime_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
    (output_dir/'run_metadata.json').write_text(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2)+'\n')
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',default=str(ROOT/'outputs/corpus/manifest.json'))
    ap.add_argument('--adapter',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--cases',nargs='+',required=True)
    ap.add_argument('--timeout',type=int,default=25)
    ap.add_argument('--synthetic',action='store_true')
    ap.add_argument('--generation-ledger',default=None)
    ap.add_argument('--generated-root',default=None)
    ap.add_argument('--tsx',action='store_true',help='use Node --import tsx for generated TypeScript')
    ap.add_argument('--generator',choices=['openapi-generator','orval','hey-api'],default=None)
    opt=ap.parse_args()
    data=execute(opt.manifest,opt.adapter,opt.output,opt.cases,synthetic=opt.synthetic,timeout=opt.timeout,
                 generation_ledger=opt.generation_ledger,generated_root=opt.generated_root,tsx=opt.tsx,generator=opt.generator)
    print(json.dumps({'synthetic':data['synthetic_fixture'],'statuses':[(r['case_id'],r['status'],r['new_captures']) for r in data['runs']]},indent=2))

if __name__=='__main__':main()
