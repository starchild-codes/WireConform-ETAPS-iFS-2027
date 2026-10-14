#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python runner/build_bundle.py
# npm package versions are saved in package-lock.json and recorded in the
# generation ledger. Do not use the resulting outputs as conformance claims.
npm install --no-audit --no-fund --save-exact --save-dev \
  '@openapitools/openapi-generator-cli' 'orval' '@hey-api/openapi-ts' \
  '@hey-api/client-fetch' 'typescript' 'tsx'
export PATH="$PWD/node_modules/.bin:$PATH"
mkdir -p experiments/bundle
npm ls --depth=0 > experiments/bundle/npm_versions.txt || true
for sdk in openapi-generator orval hey-api; do
  python runner/generate_bundle_clients.py --generator "$sdk" || true
done
python runner/audit_generated_bundle.py
