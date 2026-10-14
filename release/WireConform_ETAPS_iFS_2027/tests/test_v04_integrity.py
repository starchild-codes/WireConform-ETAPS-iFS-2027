"""Release v0.4 structural verification; no internet/generator installations."""
import json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
from build_bundle import build
from pilot_diagnostics import analyze,SELECTION


def test_117_case_bundle_preserves_each_operation():
    spec,lines=build(ROOT/'outputs/corpus/manifest.json')
    assert len(spec['paths'])==len(lines)==117
    assert len({x['operation_id'] for x in lines})==117
    assert len({x['path'] for x in lines})==117
    assert set(x['operation_id'] for x in lines)=={f'probeC{i:03}' for i in range(1,118)}


def test_bundle_file_matches_reconstructed_bundle():
    spec,_=build(ROOT/'outputs/corpus/manifest.json')
    saved=json.loads((ROOT/'outputs/bundle/all_117.json').read_text())
    assert saved==spec


def test_pilot_fault_and_feature_coverage():
    result=analyze()
    assert len(SELECTION)==14
    assert result['pilot']['mutants_detectable']==7
    assert result['pilot']['complete_default_pairs']==2
    assert set(result['pilot']['styles'])=={'form','simple','label','matrix','spaceDelimited','pipeDelimited','deepObject'}
    assert result['pilot']['distinct_serialization_families']>=10


def test_js_reference_agreement_is_independent_process():
    output=subprocess.run(['node',str(ROOT/'validation/independent_reference.mjs'),str(ROOT/'outputs/corpus/manifest.json')],
        capture_output=True,text=True,check=True)
    report=json.loads(output.stdout)
    assert report=={'cases':117,'agreement':117,'disagreement':0}


def test_pilot_selection_is_frozen_in_file():
    s=json.loads((ROOT/'runner/pilot_cases.json').read_text())
    assert s['case_ids']==SELECTION


def test_adapters_never_contain_manual_fetch():
    adapter=(ROOT/'runner/adapters/bundle_probe.mts').read_text()
    assert 'fetch(' not in adapter
    assert "{xTestParam:value}" in adapter
    assert "{headers:{'X-Test-Param':value}}" in adapter
    assert 'UNSUPPORTED_GENERATED_SIGNATURE_HEADER' in adapter
    assert 'Generated module' in adapter


def test_generated_source_audit_is_static_and_complete():
    static=json.loads((ROOT/'experiments/bundle/source_audit.json').read_text())
    assert len(static)==3
    for r in static:
        assert r['operation_name_hits']==117
        assert r['status']=='GENERATED'
        assert r['full_named_operation_coverage'] is True
        assert 'no SDK invoked' in r['warning']
