"""Conservative generated-source trace: never confuse generated file presence with execution.

This is a *static name audit* only. It deliberately does not infer wire fidelity.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
OP_NAMES=['probeC'+str(i).zfill(3) for i in range(1,118)]

def main():
    summaries=[]
    for gen in ('openapi-generator','orval','hey-api'):
        p=ROOT/'experiments/bundle'/gen
        ledger=p/'bundle_generation.json'
        if not ledger.exists():
            summaries.append({'generator':gen,'status':'NOT_GENERATED','operation_name_hits':0})
            continue
        rec=json.loads(ledger.read_text())
        data=[]
        for f in (p/'generated').rglob('*'):
            if f.is_file() and f.suffix in {'.ts','.js','.tsx'}:
                try:data.append(f.read_text(encoding='utf8',errors='replace'))
                except OSError:pass
        joined='\n'.join(data)
        names=[name for name in OP_NAMES if re.search(r'\b'+name+r'\b',joined,re.I)]
        summaries.append({'generator':gen,'status':rec['status'],'typescript_js_files':len(data),
                          'operation_name_hits':len(names),'operation_name_examples':names[:5],
                          'full_named_operation_coverage':len(names)==117,
                          'warning':'Static string check only; no SDK invoked, no HTTP capture'})
    target=ROOT/'experiments/bundle/source_audit.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(summaries,indent=2)+'\n')
    print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
