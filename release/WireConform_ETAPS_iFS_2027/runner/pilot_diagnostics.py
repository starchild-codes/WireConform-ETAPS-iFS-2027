"""A priori 14-probe pilot sensitivity against seven synthetic fault operators.

Does not evaluate any actual generated SDK. Selection freezes independently of
real SDK observations. The random baseline is a computational control only.
"""
from collections import Counter
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'artifact'))
from spec_oracle import Case,compare_observation
from mutation_control import affected,mutated

MUTANTS=['ignore_form_array_explode','omit_default_array_explode',
         'ignore_label_object_explode','ignore_matrix_array_explode',
         'discard_last_exploded_pair','header_object_nonexploded','flatten_deep_object']
SELECTION=['c003','c004','c005','c007','c008','c016','c021','c024',
           'c034','c035','c037','c039','c040','c079']

def detectable(c,mutant):
    if not affected(c,mutant):return False
    u,h=mutated(c,mutant)
    result=compare_observation(c,u,h)
    return not result['pass'] and not result['needs_encoding_review']

def analyze():
    rows=json.loads((ROOT/'outputs/corpus/manifest.json').read_text())
    cases={r['id']:Case(**{k:r[k] for k in ('id','location','style','kind','explode','value','omit_style','omit_explode','profile','pair')}) for r in rows}
    if len(SELECTION)!=14 or len(set(SELECTION))!=14:raise ValueError('not 14 distinct cases')
    assert all(c in cases for c in SELECTION)
    matrix={cid:{m:detectable(c,m) for m in MUTANTS} for cid,c in cases.items()}
    def stats(ids):
        selected=[cases[i] for i in ids]
        styles={c.style for c in selected}
        locations={c.location for c in selected}
        kinds={c.kind for c in selected}
        profiles={c.profile for c in selected}
        covered=[m for m in MUTANTS if any(matrix[i][m] for i in ids)]
        paired=sum(sum(c.pair==p for c in selected)==2 for p in {c.pair for c in selected if c.pair})
        return {'mutants_detectable':len(covered),'mutants_total':len(MUTANTS),
                'covered_mutants':covered,'styles':sorted(styles),'locations':sorted(locations),
                'kinds':sorted(kinds),'profiles':sorted(profiles),
                'complete_default_pairs':paired,
                'distinct_serialization_families':len({(c.location,c.style,c.kind,c.explode) for c in selected})}
    selected=stats(SELECTION)
    rng=random.Random(20261013)
    draws=[stats(rng.sample(list(cases),14)) for _ in range(5000)]
    distribution=dict(sorted(Counter(s['mutants_detectable'] for s in draws).items()))
    report={'kind':'SYNTHETIC_TEST_DESIGN_NOT_GENERATOR_RESULT',
            'selection_policy':'14 cases frozen prior to external SDK trials; deliberate multi-element discriminators; two default pairs; all seven styles',
            'pilot_case_ids':SELECTION,'pilot':selected,'baseline':{
                'design':'5000 seeded uniform 14-of-117 samples, without SDK data',
                'seed':20261013,'sample_size':5000,
                'mean_detected_mutants':round(sum(s['mutants_detectable'] for s in draws)/len(draws),4),
                'distribution_detected_mutants':distribution,
                'fraction_cover_all_seven':round(sum(s['mutants_detectable']==7 for s in draws)/len(draws),6)
            }}
    assert selected['mutants_detectable']==7
    assert len(selected['styles'])==7 and len(selected['profiles'])==3
    assert selected['complete_default_pairs']==2
    return report

if __name__=='__main__':
    out=analyze();target=ROOT/'validation/pilot_diagnostic_v04.json';target.write_text(json.dumps(out,indent=2)+'\n')
    (ROOT/'runner/pilot_cases.json').write_text(json.dumps({'selection_policy':out['selection_policy'],'case_ids':SELECTION},indent=2)+'\n')
    print(json.dumps({'pilot':out['pilot'],'baseline':out['baseline']},indent=2))
