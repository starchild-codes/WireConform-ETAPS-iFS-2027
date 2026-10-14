#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Installs in the project's working directory, not globally. Pin the generated
# package-lock.json with the research artifact after the first successful run.
npm install --no-audit --no-fund --save-exact --save-dev \
    '@openapitools/openapi-generator-cli' 'orval' '@hey-api/openapi-ts' '@hey-api/client-fetch' 'typescript' 'tsx'
npm ls --depth=0 > experiments/npm_dependency_versions.txt
node --version > experiments/node_version.txt
# Executable symlinks are local in node_modules/.bin.
export PATH="$PWD/node_modules/.bin:$PATH"
openapi-generator-cli version-manager list > experiments/openapi_java_versions.txt 2>&1 || true
python runner/generate_clients.py --generator openapi-generator --selection runner/pilot_cases.json
python runner/generate_clients.py --generator orval --selection runner/pilot_cases.json
python runner/generate_clients.py --generator hey-api --selection runner/pilot_cases.json
printf '\nPRESPECIFIED 14-CASE PILOT GENERATION ONLY. Check experiment logs and generated signatures before running clients.\n'
