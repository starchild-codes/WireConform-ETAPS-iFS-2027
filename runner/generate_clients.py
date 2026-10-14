"""Cross-generator *source generation* ledger.

Generation is not execution or a conformance result. Uses installed CLIs and
records exact invocations, dependency versions, stdout/stderr and output paths.
Run ONLY in an environment with the required tools installed. Test the pilot
first. Does not create/fabricate HTTP observations.
"""
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path


def run(argv, cwd=None, timeout=180):
    t=time.monotonic()
    resolved=shutil.which(argv[0])
    run_argv=argv
    use_shell=False
    if os.name=='nt' and resolved and Path(resolved).suffix.lower() in {'.cmd','.bat'}:
        run_argv=subprocess.list2cmdline([resolved,*argv[1:]])
        use_shell=True
    try:
        p=subprocess.run(run_argv,cwd=cwd,capture_output=True,text=True,
                         encoding='utf-8',errors='replace',timeout=timeout,
                         shell=use_shell)
        return {'exit':p.returncode,'stdout':p.stdout[-8000:],'stderr':p.stderr[-8000:],'elapsed_seconds':round(time.monotonic()-t,2)}
    except subprocess.TimeoutExpired as e:
        return {'exit':None,'status':'TIMEOUT','stdout':str(e.stdout)[-1000:],'stderr':str(e.stderr)[-1000:],'elapsed_seconds':round(time.monotonic()-t,2)}
    except FileNotFoundError as e:
        return {'exit':None,'status':'MISSING_EXECUTABLE','stderr':str(e),'elapsed_seconds':0}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--generator',choices=['openapi-generator','orval','hey-api'],required=True)
    ap.add_argument('--manifest',default='outputs/corpus/manifest.json')
    ap.add_argument('--output-root',default='experiments')
    ap.add_argument('--limit',type=int,default=0,help='0 means all cases')
    ap.add_argument('--selection',default=None,help='JSON file with pre-registered case_ids, mutually exclusive with --limit')
    ap.add_argument('--timeout',type=int,default=180)
    opt=ap.parse_args()
    root=Path(__file__).resolve().parent.parent
    manifest=(root/opt.manifest).resolve();rows=json.loads(manifest.read_text())
    if opt.limit>0 and opt.selection: ap.error('--selection and --limit may not be combined')
    if opt.selection:
        selected=json.loads((root/opt.selection).read_text())['case_ids']
        byid={r['id']:r for r in rows}
        assert len(set(selected))==len(selected), 'duplicate case in pilot selection'
        assert all(cid in byid for cid in selected), 'pilot selects nonexistent case'
        rows=[byid[cid] for cid in selected]
    elif opt.limit>0: rows=rows[:opt.limit]
    dst=root/opt.output_root/opt.generator;dst.mkdir(parents=True,exist_ok=True)
    infos={'python':sys.version,'platform':platform.platform(),
           'node':run(['node','--version'],timeout=20),
           'npm':run(['npm','--version'],timeout=20)}
    if opt.generator=='openapi-generator':
        bundle_meta=root/'experiments'/'bundle'/'openapi-generator'/'bundle_generation.json'
        infos[opt.generator]={'source':'previous successful bundled generation metadata',
                              'value':json.loads(bundle_meta.read_text())['environment']['generator']}
    else:
        version_command={'orval':['orval','--version'],
                         'hey-api':['openapi-ts','--version']}[opt.generator]
        infos[opt.generator]=run(version_command,timeout=30)
    (dst/'environment.json').write_text(json.dumps(infos,indent=2))
    ledger=[]
    for c in rows:
        src=manifest.parent/c['spec_file']; out=dst/c['id'];out.mkdir(exist_ok=True)
        if opt.generator=='openapi-generator':
            command=['openapi-generator-cli','generate','-i',str(src),'-g','typescript-fetch','-o',str(out/'generated')]
        elif opt.generator=='orval':
            config=out/'orval.config.mjs'
            config.write_text('export default {wireconform: {input: {target: '+json.dumps(str(src))+\
                '}, output: {target: '+json.dumps(str(out/'generated.ts'))+\
                ', client: "fetch", mock: false, baseUrl: "http://127.0.0.1:8765"}}};\n')
            command=['orval','--config',str(config)]
        else:
            command=['openapi-ts','-i',str(src),'-o',str(out/'generated')]
        result=run(command,cwd=str(root),timeout=opt.timeout)
        status=('GENERATED' if result['exit']==0 else 'GENERATE_TIMEOUT' if result.get('status')=='TIMEOUT'
                else 'GENERATOR_UNAVAILABLE' if result.get('status')=='MISSING_EXECUTABLE' else 'GENERATE_ERROR')
        row={'case_id':c['id'],'generator':opt.generator,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
             'command':command,**result,'status':status}
        ledger.append(row)
        (out/'generation.json').write_text(json.dumps(row,indent=2)+'\n')
        print(c['id'],status,flush=True)
    (dst/'generation_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
    from collections import Counter
    print(json.dumps({'generator':opt.generator,'attempted':len(ledger),'status_counts':dict(Counter(x['status'] for x in ledger))},indent=2))

if __name__=='__main__': main()
