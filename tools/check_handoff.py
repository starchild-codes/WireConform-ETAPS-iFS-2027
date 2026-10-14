"""Verify this handoff is internally complete and has not invented SDK results."""
import hashlib
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
required=['START_HERE.md','AGENTS.md','codex/CODEX_FULL_TASK.md',
 'codex/SCIENTIFIC_GUARDRAILS.md','manuscript/etaps_openapi_draft.tex',
 'manuscript/etaps_openapi_draft.pdf','outputs/corpus/manifest.json',
 'outputs/bundle/all_117.json','runner/adapters/bundle_probe.mts',
 'runner/generate_bundle_online.sh','runner/execute_bundle_clients.py',
 'validation/independent_reference.mjs','runner/pilot_cases.json',
 'tests/test_v04_integrity.py','requirements-dev.txt']
missing=[x for x in required if not (root/x).is_file()]
manifest=json.loads((root/'outputs/corpus/manifest.json').read_text())
pilot=json.loads((root/'runner/pilot_cases.json').read_text())['case_ids']
ids={x['id'] for x in manifest}
allop=json.loads((root/'outputs/bundle/all_117.json').read_text())
assert len(manifest)==117 and len(ids)==117
assert len(pilot)==14 and len(set(pilot))==14 and set(pilot).issubset(ids)
assert len(allop['paths'])==117
assert not missing, 'Missing crucial files: '+', '.join(missing)
print(json.dumps({'status':'HANDOFF_VALIDATED_NOT_SDK_EXECUTION',
  'defined_cases':len(manifest),'pilot_cases':len(pilot),'bundle_operations':len(allop['paths']),
  'required_files_present':len(required)},indent=2))
