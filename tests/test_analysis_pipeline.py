import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'artifact'))
from analyze_results import assess,wilson

CASES=[{'id':'a','location':'query','style':'form','kind':'array','profile':'words'},
       {'id':'b','location':'query','style':'form','kind':'array','profile':'words'},
       {'id':'c','location':'path','style':'matrix','kind':'scalar','profile':'words'}]

def test_missing_captures_not_counted_as_failures():
    scores={'cases':[{'case_id':'a','status':'PASS'}, {'case_id':'b','status':'FAIL'}]}
    runs=[{'case_id':'a','status':'CAPTURED_ONE','generation_status':'GENERATED'}, {'case_id':'b','status':'NO_CAPTURE'}, {'case_id':'c','status':'EXECUTION_ERROR'}]
    out=assess(CASES,scores,runs)['overall']
    assert out['eligible']==1 and out['pass']==1 and out['fail']==0
    assert out['all_status_counts']['NO_CAPTURE']==1
    assert out['all_status_counts']['EXECUTION_ERROR']==1

def test_score_does_not_mask_generation_failure():
    scores={'cases':[{'case_id':'a','status':'FAIL'}]}
    runs=[{'case_id':'a','status':'CAPTURED_ONE','generation_status':'GENERATE_ERROR'}]
    out=assess(CASES,scores,runs)['overall']
    assert out['eligible']==0 and out['all_status_counts']['GENERATION_FAILURE']==1

def test_duplicate_unknown_scores_are_rejected():
    try:assess(CASES,{'cases':[{'case_id':'a','status':'PASS'},{'case_id':'a','status':'FAIL'}]},[])
    except ValueError:pass
    else:raise AssertionError('duplicate scorer records accepted')

def test_unattested_sdk_run_is_excluded():
    scores={'cases':[{'case_id':'a','status':'PASS'}]}
    runs=[{'case_id':'a','status':'CAPTURED_ONE','generation_status':'UNKNOWN'}]
    out=assess(CASES,scores,runs)['overall']
    assert out['eligible']==0 and out['all_status_counts']['MISSING_GENERATION_ATTESTATION']==1

def test_synthetic_fixture_is_never_counted_as_sdk_conformance():
    scores={'cases':[{'case_id':'a','status':'PASS'}]}
    runs=[{'case_id':'a','status':'CAPTURED_ONE','synthetic_fixture':True}]
    out=assess(CASES,scores,runs)['overall']
    assert out['eligible']==0 and out['all_status_counts']['SYNTHETIC_CONTROL']==1

def test_wilson_endpoints():
    assert wilson(0,1)[0]==0
    assert wilson(1,1)[1]==1
    assert wilson(0,0) is None
