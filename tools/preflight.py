"""Record reproducibility environment without downloading anything or changing input.

Run: python tools/preflight.py
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'evidence/preflight.json'

def cmd(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=7)
        return {'exit_code':p.returncode,'stdout':p.stdout[-2000:].strip(),'stderr':p.stderr[-2000:].strip()}
    except (OSError,subprocess.TimeoutExpired) as e:
        return {'error':type(e).__name__+': '+str(e)[:250]}

def sha(path):
    p=ROOT/path
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None

out={'status':'ENVIRONMENT_SNAPSHOT_NOT_EXPERIMENTAL_RESULT',
     'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'platform':platform.platform(),'machine':platform.machine(),
     'python':sys.version,'cwd':str(ROOT),
     'commands':{name:cmd(args) for name,args in {
         'node':['node','--version'],'npm':['npm','--version'],
         'java':['java','-version'],'pdflatex':['pdflatex','--version'],
         'latexmk':['latexmk','-v'], 'git':['git','--version']}.items()},
     'inputs_sha256':{s:sha(s) for s in ['outputs/corpus/manifest.json','outputs/bundle/all_117.json',
         'runner/adapters/bundle_probe.mts','manuscript/etaps_openapi_draft.tex',
         'runner/pilot_cases.json','package-lock.json']}}
for host in ('registry.npmjs.org','repo.maven.apache.org','github.com'):
    try:
        addr=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
        out.setdefault('dns',{})[host]={'resolved':bool(addr)}
    except OSError as e:
        out.setdefault('dns',{})[host]={'resolved':False,'error':str(e)[:250]}
TARGET.parent.mkdir(parents=True,exist_ok=True)
TARGET.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'output':str(TARGET),'dns':out['dns'],
   'runtime_availability':{k:bool(shutil.which(k)) for k in ('python','node','npm','java','pdflatex','latexmk')}},indent=2))
