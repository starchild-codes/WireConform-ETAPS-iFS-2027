"""Conservatively execute generated SDK methods and capture HTTP requests.

NO results are inferred from missing generated SDKs. Non-zero adapter exits remain
excluded even if capture occurs (manual review needed for post-request errors).
Runtime must be run on a machine with npm packages and genuine generated sources.
"""
import argparse,hashlib,json,subprocess,sys,threading,time
from pathlib import Path
from http.server import HTTPServer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'artifact'))
from capture_server import Handler
from score import main as make_scores
from analyze_results import assess
from metamorphic import analyze as compare_pairs


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--generator',choices=['openapi-generator','orval','hey-api'],required=True)
    ap.add_argument('--selection',choices=['pilot','full'],default='pilot')
    ap.add_argument('--timeout',type=int,default=40)
    args=ap.parse_args()
    meta=ROOT/'experiments/bundle'/args.generator/'bundle_generation.json'
    if not meta.exists():raise SystemExit('NO_GENERATED_SDK: run runner/generate_bundle_online.sh first')
    metadata=json.loads(meta.read_text())
    bundle=ROOT/'outputs/bundle/all_117.json'
    if metadata['status']!='GENERATED' or metadata['bundle_sha256']!=sha(bundle):
        raise SystemExit('Generator result missing or bundle hash mismatch')
    assert metadata['generated_file_count']>0
    generated_root=ROOT/'experiments/bundle'/args.generator
    for generated in metadata['generated_source_hashes']:
        candidate=(generated_root/generated['path']).resolve()
        if not candidate.is_relative_to(generated_root.resolve()) or not candidate.is_file() or sha(candidate)!=generated['sha256']:
            raise SystemExit(f'Generated source changed or disappeared: {generated["path"]}')
    print('IMPORTANT: Generated-operation signatures and adapter source must be audited before any findings are attributed to SDKs.',flush=True)
    out=ROOT/'experiments/bundle'/args.generator/args.selection
    out.mkdir(parents=True,exist_ok=True)
    manifest=ROOT/'outputs/corpus/manifest.json'
    rows=json.loads(manifest.read_text())
    if args.selection=='pilot':
        selection=json.loads((ROOT/'runner/pilot_cases.json').read_text())['case_ids']
        cases={row['id']:row for row in rows}
        rows=[cases[cid] for cid in selection]
    capture=out/'observations.jsonl'
    capture.write_text('')
    adapter=ROOT/'runner/adapters/bundle_probe.mts'
    ledger=[]
    srv=HTTPServer(('127.0.0.1',8765),Handler)
    srv.lock=threading.Lock();srv.output=capture
    thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
    try:
        for c in rows:
            cid=c['id'];payload={'case_id':cid,'value':c['value'],'location':c['location'],
               'generator':args.generator,'base_url':'http://127.0.0.1:8765',
               'generated_dir':str(ROOT/'experiments/bundle'/args.generator/'generated')}
            # Source-audited generator-specific exclusions.  Neither case is a
            # wire-format FAIL: no admissible generated typed invocation exists.
            if args.generator=='orval' and c['location']=='header':
                ledger.append({'case_id':cid,'status':'UNSUPPORTED_GENERATED_SIGNATURE',
                    'generation_status':'GENERATED','synthetic_fixture':False,
                    'source_generation_bundle_hash_valid':True,
                    'spec_sha256':sha(manifest.parent/c['spec_file']),
                    'adapter_sha256':sha(adapter),'elapsed_seconds':0,
                    'new_captures':0,'returncode':None,'stderr_tail':'',
                    'stdout_tail':'Orval fetch operation exposes no typed in:header parameter; RequestInit.headers bypass is prohibited.'})
                print(cid,'UNSUPPORTED_GENERATED_SIGNATURE',flush=True)
                continue
            if (args.generator=='hey-api' and c['location']=='query' and
                    c['style'] in {'spaceDelimited','pipeDelimited'} and c['kind']=='object'):
                ledger.append({'case_id':cid,'status':'COMPILE_ERROR_GENERATED_SOURCE',
                    'generation_status':'GENERATED','synthetic_fixture':False,
                    'source_generation_bundle_hash_valid':True,
                    'spec_sha256':sha(manifest.parent/c['spec_file']),
                    'adapter_sha256':sha(adapter),'elapsed_seconds':0,
                    'new_captures':0,'returncode':None,
                    'stderr_tail':'Generated querySerializer object style is rejected by generated ObjectStyle type (TS2322).',
                    'stdout_tail':''})
                print(cid,'COMPILE_ERROR_GENERATED_SOURCE',flush=True)
                continue
            command=['node','--import','tsx',str(adapter),json.dumps(payload,separators=(',',':'))]
            prior=sum(json.loads(s).get('case_id')==cid for s in capture.read_text().splitlines() if s.strip())
            start=time.monotonic()
            try:
                p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=args.timeout)
                rc=p.returncode;stderr=p.stderr[-2500:]
                stdout=p.stdout[-2500:]
            except (subprocess.TimeoutExpired,FileNotFoundError) as e:
                rc=None;stderr=str(e)[:2500];stdout=''
            seen=sum(json.loads(s).get('case_id')==cid for s in capture.read_text().splitlines() if s.strip())-prior
            if rc is None: status='EXECUTION_TIMEOUT_OR_UNAVAILABLE'
            elif seen>1:status='CAPTURED_MULTIPLE'
            elif rc!=0 and seen:status='CAPTURED_WITH_SDK_ERROR_REVIEW'
            elif rc!=0:status='EXECUTION_ERROR'
            elif seen==1:status='CAPTURED_ONE'
            else:status='NO_CAPTURE'
            row={'case_id':cid,'status':status,'generation_status':'GENERATED','synthetic_fixture':False,
                 'source_generation_bundle_hash_valid':True,
                 'spec_sha256':sha(manifest.parent/c['spec_file']),
                 'adapter_sha256':sha(adapter),'elapsed_seconds':round(time.monotonic()-start,3),
                 'new_captures':seen,'returncode':rc,'stderr_tail':stderr,'stdout_tail':stdout}
            ledger.append(row)
            print(cid,status,flush=True)
    finally:
        srv.shutdown();srv.server_close();thread.join(timeout=2)
    (out/'runtime_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
    scores=out/'scored.json'
    make_scores(str(manifest),str(capture),str(scores))
    summary=assess(json.loads(manifest.read_text()),json.loads(scores.read_text()),ledger)
    (out/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
    metamorph=compare_pairs(str(manifest),str(capture))
    (out/'metamorphic.json').write_text(json.dumps(metamorph,indent=2)+'\n')
    print(json.dumps({'generator':args.generator,'selection':args.selection,'eligible':summary['overall']['eligible'],
                     'statuses':summary['overall']['all_status_counts'],'default_pair_analysis':metamorph['summary']},indent=2))

if __name__=='__main__':main()
