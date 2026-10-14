# Real-client experiment protocol, release v0.4

### Minimum machine requirements

Linux with Node 22+, npm, Python 3.11+, Java 17+, and internet access to npm and Maven. Use a disposable working directory. The local HTTP capture server binds only to `127.0.0.1:8765`.

### Preparation and generation

```bash
python -m pytest -q tests
python runner/build_bundle.py
node validation/independent_reference.mjs outputs/corpus/manifest.json validation/reference_agreement.json
bash runner/generate_bundle_online.sh
```

Read all three `experiments/bundle/*/bundle_generation.json` files. `GENERATED` only means output source files exist. Check `generated_file_count`, source hashes, stdout/stderr, invocation command, pinned package versions in npm dependency record and package-lock.json. Any tool that cannot parse the OpenAPI 3.1.1 bundle is **generation-unavailable on this target/configuration**, not a request serialization failure.

### Source and invocation audit

Generated APIs evolve. Before running the fixed diagnostic set, compare each operation method's typed parameters with the provisional adapter in `runner/adapters/bundle_probe.mts`. The adapter may pass user values into SDK parameters but MUST NOT hand-format a path, query string, header, or request URL. For generated header operations, current adapter explicitly errors and excludes those cases. If an adapter does not match the generated SDK signatures, fix the adapter, record its SHA-256 and explain why the revised invocation still calls the intended generated serialization path. No selective adaptation after viewing conformance outcomes.

### Prespecified diagnostic pilot

Read `runner/pilot_cases.json` (14 IDs frozen on 2026-10-13 before third-party observations). For each SDK run:

```bash
python runner/execute_bundle_clients.py --generator openapi-generator --selection pilot
python runner/execute_bundle_clients.py --generator orval --selection pilot
python runner/execute_bundle_clients.py --generator hey-api --selection pilot
```

The runner checks generated hashes and captures local network requests. It segregates runtime errors and missing capture from the actual scored URL/header comparisons. A captured request during a failing SDK invocation is review-only, not auto-admitted.

### Full benchmark and analysis

Only after pilot provenance checks, run `--selection full` for each generator. The file `analysis.json` reports correct denominator classes. Do **not** conflate the conditional percentage among eligible captures with support coverage across all 117 cases. Summarize failures by `(location, style, kind, explode)` and by implicit/default pair. Record the full dependency lockfile, OS, Node version, Java version, package versions and raw observations.

### Reproduction of potential new bugs

Repeat any mismatch using the original single-operation file from `outputs/corpus/<id>.json`, rebuild the SDK independently, audit typed invocation, and compare with the OAS 3.1.1 serialization rule. Eliminate other operation definitions; preserve the parameter/value causing the difference; rerun on a fresh environment and check existing upstream reports. Only then is a new finding eligible for the manuscript.

### Scope of verified results

All executable results shipped in v0.4 are offline reference, audit, and synthetic mutation controls. There are **no SDK conformance measurements in the shipped files**.
