"""One-shot source generation (117 independent operations per generator).

Records all commands, exact generator versions and hashes. This script DOES NOT
claim successful runtime execution or serialize requests itself.
"""
import argparse,hashlib,json,os,platform,shutil,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def invoke(cmd,timeout=600):
    # npm exposes package binaries as .cmd shims on Windows.  CreateProcess
    # cannot execute those directly when subprocess is given an argv list, so
    # resolve and dispatch only that launcher through cmd.exe.  The generator
    # arguments remain an explicit list and are recorded unchanged below.
    resolved=shutil.which(cmd[0])
    run_cmd=cmd
    use_shell=False
    if os.name=='nt' and resolved and Path(resolved).suffix.lower() in {'.cmd','.bat'}:
        run_cmd=subprocess.list2cmdline([resolved,*cmd[1:]])
        use_shell=True
    start=time.monotonic()
    try:
        p=subprocess.run(run_cmd,cwd=ROOT,capture_output=True,text=True,
                         encoding='utf-8',errors='replace',timeout=timeout,
                         shell=use_shell)
        return {'exit':p.returncode,'stdout_tail':p.stdout[-12000:],
                'stderr_tail':p.stderr[-12000:],'seconds':round(time.monotonic()-start,3)}
    except (FileNotFoundError,subprocess.TimeoutExpired) as e:
        status='TIMEOUT' if isinstance(e,subprocess.TimeoutExpired) else 'MISSING_CLI'
        return {'exit':None,'status':status,'error':str(e)[:2000],'seconds':round(time.monotonic()-start,3)}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--generator',choices=['openapi-generator','orval','hey-api'],required=True)
    args=ap.parse_args(); g=args.generator
    spec=ROOT/'outputs/bundle/all_117.json'
    if not spec.exists():raise SystemExit('First run python runner/build_bundle.py')
    out=ROOT/'experiments/bundle'/g
    out.mkdir(parents=True,exist_ok=True)
    destination=out/'generated'
    versions={'node':invoke(['node','--version']), 'npm':invoke(['npm','--version'])}
    if g=='openapi-generator':
        versions['generator']=invoke(['openapi-generator-cli','version'])
        cmd=['openapi-generator-cli','generate','-i',str(spec),'-g','typescript-fetch','-o',str(destination),
             '--additional-properties','supportsES6=true,typescriptThreePlus=true']
    elif g=='orval':
        versions['generator']=invoke(['orval','--version'])
        cfg=out/'orval.config.mjs'
        cfg.write_text('export default {wc: {input: {target: '+json.dumps(str(spec))+\
                       '}, output: {target: '+json.dumps(str(destination/'client.ts'))+\
                       ', client: "fetch", mode:"single", mock: false, baseUrl: "http://127.0.0.1:8765"}}};\n')
        cmd=['orval','--config',str(cfg)]
    else:
        versions['generator']=invoke(['openapi-ts','--version'])
        cfg=ROOT/'openapi-ts.config.mjs'  # CLI auto-loads the standard config name
        cfg.write_text('import { defineConfig } from "@hey-api/openapi-ts";\n'+
            'export default defineConfig({ input: '+json.dumps(str(spec))+', output: {path:'+json.dumps(str(destination))+\
            '}, plugins: ["@hey-api/client-fetch", "@hey-api/typescript",'+
            ' {name:"@hey-api/sdk", paramsStructure:"grouped", operations:"flat"}] });\n')
        cmd=['openapi-ts']
    r=invoke(cmd)
    # Store generated tree hashes separately. No arbitrary egress.
    files=[{'path':str(p.relative_to(out)),'sha256':sha(p)} for p in sorted(destination.rglob('*')) if p.is_file()] if destination.exists() else []
    row={'generator':g,'mode':'MERGED_117_OPERATIONS_NOT_INDIVIDUAL_SPECS',
         'bundle_sha256':sha(spec),'command':cmd,'environment':{'python':sys.version,'platform':platform.platform(),**versions},
         'result':r,'status':'GENERATED' if r.get('exit')==0 and files else 'UNAVAILABLE_OR_ERROR',
         'generated_file_count':len(files),'generated_source_hashes':files}
    (out/'bundle_generation.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps({'generator':g,'status':row['status'],'files':len(files),'output':str(out)},indent=2))
    if row['status']!='GENERATED':raise SystemExit(2)

if __name__=='__main__':main()
