#!/usr/bin/env bash
# Explicit stages; does not bless unreviewed generated SDK results.
set -euo pipefail
cd "$(dirname "$0")/.."
step="${1:-help}"
mkdir -p evidence/stage_logs
case "$step" in
  offline)
    python tools/check_handoff.py
    python tools/preflight.py
    python -m pytest -q tests | tee evidence/stage_logs/offline_pytest.log
    python artifact/validate_corpus.py outputs/corpus validation/structural_audit_v04.json | tee evidence/stage_logs/offline_corpus.log
    python runner/build_bundle.py | tee evidence/stage_logs/offline_bundle.log
    node validation/independent_reference.mjs outputs/corpus/manifest.json validation/reference_agreement.json | tee evidence/stage_logs/offline_reference.log
    python runner/pilot_diagnostics.py | tee evidence/stage_logs/offline_pilot.log
    ;;
  generation)
    echo 'Running networked source generation; not yet conformance testing.'
    bash runner/generate_bundle_online.sh 2>&1 | tee evidence/stage_logs/online_generation.log
    ;;
  pilot|full)
    for gen in openapi-generator orval hey-api; do
      audit="evidence/reviews/${gen}_adapter_audit.json"
      if [[ ! -f "$audit" ]]; then
        echo "REFUSING $step run: missing independent generated SDK and adapter audit: $audit" >&2
        echo 'Use codex/SCIENTIFIC_GUARDRAILS.md and ADAPTER_ATTESTATION_TEMPLATE.json.' >&2
        exit 3
      fi
      python - "$audit" <<'PY'
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]); r=json.loads(p.read_text())
a=Path('runner/adapters/bundle_probe.mts')
b=Path('outputs/bundle/all_117.json')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert r.get('audit_status')=='APPROVED_FOR_EXECUTION', 'adapter audit not approved'
assert r.get('adapter_sha256')==sha(a), 'adapter code changed after review'
assert r.get('bundle_sha256')==sha(b), 'bundle changed after review'
assert all(r.get('verified_operations',{}).get(k) for k in ('query','path','header')), 'all three locations must be audited'
print('Audited adapter and bundle hashes:',p)
PY
      python runner/execute_bundle_clients.py --generator "$gen" --selection "$step" 2>&1 | tee "evidence/stage_logs/${gen}_${step}.log"
    done
    ;;
  *)
    echo 'Usage: bash runner/codex_stages.sh {offline|generation|pilot|full}'
    echo 'Read START_HERE.md and codex/CODEX_FULL_TASK.md before running.'
    ;;
esac
