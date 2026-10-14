"""Build the release ledger from genuine captures and independent reproductions."""
from __future__ import annotations
import collections,csv,hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'/'final'; OUT.mkdir(parents=True,exist_ok=True)
GENERATORS=('openapi-generator','orval','hey-api')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def jsonl(path): return {x['case_id']:x for x in (json.loads(s) for s in Path(path).read_text().splitlines() if s.strip())}
def wilson(k,n,z=1.96):
    if not n:return None
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/d
    return [round(max(0,c-h),6),round(min(1,c+h),6)]

manifest=json.loads((ROOT/'outputs/corpus/manifest.json').read_text())
decisions=json.loads((ROOT/'evidence/reviews/encoding_adjudication.json').read_text())['decisions']
repro=json.loads((ROOT/'evidence/reviews/pilot_reproduction.json').read_text())['phases']['full_mismatches']
rows=[]; summaries={}; families={}; pairs={}
for gen in GENERATORS:
    ledger={x['case_id']:x for x in json.loads((ROOT/'experiments/bundle'/gen/'full/runtime_ledger.json').read_text())}
    scores={x['case_id']:x for x in json.loads((ROOT/'experiments/bundle'/gen/'full/scored.json').read_text())['cases']}
    observations=jsonl(ROOT/'experiments/bundle'/gen/'full/observations.jsonl')
    confirmed={x['case_id'] for x in repro[gen]['rows'] if x['exact_match']}
    for case in manifest:
        cid=case['id']; run=ledger[cid]; score=scores[cid]; observed=observations.get(cid)
        execution=run['status']; raw=score['status']; encoding_decision=''
        if raw=='ENCODING_REVIEW':
            encoding_decision=decisions[gen][cid]; raw=encoding_decision
        if execution=='CAPTURED_ONE':
            if raw=='PASS': final='PASS'
            elif raw=='FAIL' and cid in confirmed: final='CONFIRMED_FAIL'
            elif raw=='FAIL': final='PROVISIONAL_FAIL_REVIEW'
            else: final=raw
        else: final=execution
        eligible=final in {'PASS','CONFIRMED_FAIL'}
        h={k.lower():str(v) for k,v in (observed or {}).get('headers',{}).items()}
        expected_h=score.get('expected_headers',{}).get('X-Test-Param','')
        observed_h=h.get('x-test-param','')
        row={
          'generator':gen,'case_id':cid,'location':case['location'],'style':case['style'],
          'explode':case['explode'],'kind':case['kind'],'profile':case['profile'],
          'omit_style':case['omit_style'],'omit_explode':case['omit_explode'],'pair':case['pair'] or '',
          'defined':True,'generated':run.get('generation_status')=='GENERATED',
          'compile_or_transpile_ok':execution not in {'COMPILE_ERROR_GENERATED_SOURCE'},
          'invoke_ok':execution=='CAPTURED_ONE','capture_ok':execution=='CAPTURED_ONE',
          'execution_status':execution,'raw_scorer_status':score['status'],
          'encoding_decision':encoding_decision,'single_spec_reproduced':cid in confirmed,
          'eligible':eligible,'final_status':final,
          'expected_url':score.get('expected_url',''),'observed_url':(observed or {}).get('url',''),
          'expected_parameter_header':expected_h,'observed_parameter_header':observed_h,
          'spec_sha256':run.get('spec_sha256',''),'adapter_sha256':run.get('adapter_sha256',''),
          'bundle_sha256':sha(ROOT/'outputs/bundle/all_117.json')}
        rows.append(row)
    cnt=collections.Counter(r['final_status'] for r in rows if r['generator']==gen)
    eligible_n=cnt['PASS']+cnt['CONFIRMED_FAIL']
    summaries[gen]={
      'N_defined':117,'N_generated':117,
      'N_invokable':sum(r['invoke_ok'] for r in rows if r['generator']==gen),
      'N_captured':sum(r['capture_ok'] for r in rows if r['generator']==gen),
      'N_eligible':eligible_n,'N_pass':cnt['PASS'],'N_fail':cnt['CONFIRMED_FAIL'],
      'N_unsupported':cnt['UNSUPPORTED_GENERATED_SIGNATURE'],
      'N_compile_error':cnt['COMPILE_ERROR_GENERATED_SOURCE'],
      'N_review':sum(v for k,v in cnt.items() if 'REVIEW' in k),
      'support_coverage':round(eligible_n/117,6),
      'conditional_conformance':round(cnt['PASS']/eligible_n,6) if eligible_n else None,
      'descriptive_wilson_95':wilson(cnt['PASS'],eligible_n),
      'all_status_counts':dict(sorted(cnt.items()))}
    fam=[]; grouped=collections.defaultdict(list)
    for r in rows:
        if r['generator']==gen: grouped[(r['location'],r['style'],r['kind'])].append(r)
    for key,vals in sorted(grouped.items()):
        c=collections.Counter(x['final_status'] for x in vals); n=c['PASS']+c['CONFIRMED_FAIL']
        fam.append({'location':key[0],'style':key[1],'kind':key[2],'defined':len(vals),'eligible':n,
                    'pass':c['PASS'],'fail':c['CONFIRMED_FAIL'],'other':len(vals)-n})
    families[gen]=fam
    meta=json.loads((ROOT/'experiments/bundle'/gen/'full/metamorphic.json').read_text())
    final_by_id={r['case_id']:r for r in rows if r['generator']==gen}
    pp=[]
    for p in meta['pairs']:
        both=all(final_by_id[x]['eligible'] for x in (p['left'],p['right']))
        pp.append({**p,'final_status':p['status'] if both else 'INELIGIBLE'})
    pc=collections.Counter(x['final_status'] for x in pp)
    pairs[gen]={'counts':dict(sorted(pc.items())),'pairs':pp}

payload={'study_status':'REAL_GENERATED_SDK_WIRE_OBSERVATIONS','oas_version':'3.1.1',
         'generators':summaries,'by_family':families,'default_pairs':pairs,'rows':rows,
         'scope_note':'Finite frozen benchmark; Wilson intervals are descriptive, not population inference.'}
(OUT/'EXPERIMENT_RESULTS.json').write_text(json.dumps(payload,indent=2)+'\n')
with (OUT/'EXPERIMENT_RESULTS.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'RESULTS_SUMMARY.json').write_text(json.dumps({'generators':summaries,'by_family':families,'default_pairs':{g:p['counts'] for g,p in pairs.items()}},indent=2)+'\n')
print(json.dumps(summaries,indent=2))
