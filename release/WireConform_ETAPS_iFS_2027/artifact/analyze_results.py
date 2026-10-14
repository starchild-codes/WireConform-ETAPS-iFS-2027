"""Pre-registered, denominator-safe summary for actual generator trials.

Never infer an SDK defect from failure to generate, compile, invoke, or capture.
Inputs must come from actual execution; this module creates NO observations.
The same logic can be unit-tested on labelled synthetic fixtures, which
must never be presented as findings about real SDKs.
"""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
from math import sqrt

INELIGIBLE = {'NOT_RUN','INVALID_MULTIPLE_OBSERVATIONS','ENCODING_REVIEW',
              'EXECUTION_ERROR','EXECUTION_TIMEOUT','NO_CAPTURE',
              'ADAPTER_UNAVAILABLE','GENERATE_ERROR','GENERATOR_UNAVAILABLE',
              'COMPILE_ERROR','UNSUPPORTED','CONFIG_ERROR'}
SCORED = {'PASS','FAIL'}


def wilson(k, n, z=1.96):
    """Descriptive finite-benchmark interval only; not population inference."""
    if not n: return None
    p = k/n
    den=1+z*z/n
    cent=(p+z*z/(2*n))/den
    half=z*sqrt((p*(1-p)+z*z/(4*n))/n)/den
    return [round(max(0,cent-half),6),round(min(1,cent+half),6)]


def assess(manifest, score, run_ledger):
    info={x['id']:x for x in manifest}
    by_score={}
    for s in score.get('cases',[]):
        cid=s.get('case_id')
        if cid not in info: raise ValueError(f'unknown score case {cid}')
        if cid in by_score: raise ValueError(f'duplicate score case {cid}')
        by_score[cid]=s
    by_run={}
    for r in run_ledger:
        cid=r.get('case_id')
        if cid not in info: raise ValueError(f'unknown run case {cid}')
        if cid in by_run: raise ValueError(f'duplicate run case {cid}')
        by_run[cid]=r
    counts=Counter(); groups=defaultdict(lambda: Counter())
    rows=[]
    for cid,c in info.items():
        sr=by_score.get(cid,{'status':'NOT_RUN'})
        rr=by_run.get(cid)
        generation=rr.get('generation_status','UNKNOWN') if rr else 'UNKNOWN'
        execution=rr.get('status','NOT_RUN') if rr else 'NOT_RUN'
        if rr and rr.get('synthetic_fixture'):
            status='SYNTHETIC_CONTROL'
        elif generation in {'GENERATE_ERROR','GENERATOR_UNAVAILABLE','GENERATE_TIMEOUT'}:
            status='GENERATION_FAILURE'
        elif execution not in {'CAPTURED_ONE','NOT_RUN'}:
            status=execution
        elif generation!='GENERATED' and execution!='NOT_RUN':
            status='MISSING_GENERATION_ATTESTATION'
        elif execution=='NOT_RUN':
            status='NOT_RUN'
        else:
            status=sr['status']
            if status not in SCORED|INELIGIBLE:
                raise ValueError(f'unexpected scorer status {status} for {cid}')
            if status=='NOT_RUN':
                # Inconsistency between runtime success and score ledger
                status='MISSING_SCORE'
        counts[status]+=1
        fam=(c['location'],c['style'],c['kind'])
        groups[fam][status]+=1
        rows.append({'case_id':cid,'location':c['location'],'style':c['style'],
                     'kind':c['kind'],'profile':c['profile'],
                     'generation':generation,'execution':execution,'status':status})
    def summarise(q):
        n=q['PASS']+q['FAIL']; total=sum(q.values())
        return {'total':total,'eligible':n,'pass':q['PASS'],'fail':q['FAIL'],
                'coverage_fraction':round(n/total,6) if total else None,
                'conditional_conformance_fraction':round(q['PASS']/n,6) if n else None,
                'descriptive_wilson_95':wilson(q['PASS'],n),
                'all_status_counts':dict(sorted(q.items()))}
    return {'status':'VALIDATED_ANALYSIS_OF_SUPPLIED_LEDGERS_NOT_PROOF_OF_REAL_EXPERIMENTS',
            'overall':summarise(counts),
            'by_family':[{'location':a,'style':b,'kind':c,**summarise(v)}
                         for (a,b,c),v in sorted(groups.items())],
            'rows':rows,
            'interpretation':'Synthetic controls and executions without a verified generation ledger are excluded. Conditional conformance is among executed, captured, scored cases only; report coverage and all failure classes. Case selection is deterministic, not a random sample of production OpenAPI usage.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('manifest');ap.add_argument('score');ap.add_argument('runtime_ledger');ap.add_argument('output')
    opt=ap.parse_args()
    result=assess(json.loads(Path(opt.manifest).read_text()),json.loads(Path(opt.score).read_text()),json.loads(Path(opt.runtime_ledger).read_text()))
    out=Path(opt.output);out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    with (out.parent/(out.stem+'.csv')).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['rows'][0]));writer.writeheader();writer.writerows(result['rows'])
    print(json.dumps(result['overall'],indent=2))

if __name__=='__main__':main()
