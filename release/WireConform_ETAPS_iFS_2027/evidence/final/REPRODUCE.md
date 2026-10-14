# Reproducing WireConform

All commands run from the artifact root. The recorded run used Windows 11 AMD64, Python 3.12.14, Node 24.17.0, npm 11.13.0, and the pinned `package-lock.json`. Network access is needed only for a clean dependency/JAR installation; the release includes generated source and observations for offline audit.

## 1. Install pinned dependencies

```powershell
npm ci
python -m pip install -r requirements-dev.txt
```

OpenAPI Generator CLI 2.41.0 selects generator JAR 7.26.0 through `openapitools.json`. Do not run an unpinned upgrade.

## 2. Validate the frozen infrastructure

```powershell
python -m pytest -q tests
python artifact/validate_corpus.py outputs/corpus validation/structural_audit_v04.json
python runner/build_bundle.py
node validation/independent_reference.mjs outputs/corpus/manifest.json validation/reference_agreement.json
python runner/pilot_diagnostics.py
python artifact/mutation_control.py outputs/corpus/manifest.json validation/synthetic_mutation_report_v04.json
npx redocly lint outputs/bundle/all_117.json
```

Expected checkpoints: 60 tests pass; 117 cases with zero structural problems; 117/117 Python--JavaScript oracle agreement; 27 default pairs; and no Redocly validation error. Documentation warnings are expected and preserved in `evidence/stage_logs/redocly_bundle.log`.

## 3. Regenerate genuine SDKs

```powershell
python runner/generate_bundle_clients.py --generator openapi-generator
python runner/generate_bundle_clients.py --generator orval
python runner/generate_bundle_clients.py --generator hey-api
```

The commands and generated-source hashes are recorded in each `experiments/bundle/<tool>/bundle_generation.json` and summarized in `evidence/generator_version_manifest.json`. Do not edit generated serialization code.

## 4. Execute the frozen pilot and full corpus

```powershell
python runner/execute_bundle_clients.py --generator openapi-generator --selection pilot
python runner/execute_bundle_clients.py --generator orval --selection pilot
python runner/execute_bundle_clients.py --generator hey-api --selection pilot

python runner/execute_bundle_clients.py --generator openapi-generator --selection full
python runner/execute_bundle_clients.py --generator orval --selection full
python runner/execute_bundle_clients.py --generator hey-api --selection full
```

Each run invokes generated operations through `runner/adapters/bundle_probe.mts`, captures loopback HTTP on `127.0.0.1:8765`, and writes observations, ledgers, scores, analysis, and metamorphic results under `experiments/bundle/`. The adapter must not be changed after seeing results without a new audit and hash.

## 5. Audit individual-spec reproductions

The pre-registered mismatch selections are in `evidence/reviews/*_mismatch_selection.json`; clean generated sources and captures are under `experiments/reproduction/`. Verify exact agreement with:

```powershell
python runner/compare_reproductions.py
```

Expected full-mismatch result: OpenAPI Generator 63/63 exact, Orval 61/61 exact, Hey API 53/53 exact, with zero differences. Pilot comparisons are 14/14, 13/13, and 14/14 respectively. The Hey API compile log independently records the six isolated delimited-object generated-source failures.

## 6. Rebuild final results

```powershell
python artifact/finalize_real_results.py
```

Expected aggregate counts:

| Tool | Defined | Eligible | Pass | Confirmed fail | Excluded |
|---|---:|---:|---:|---:|---:|
| OpenAPI Generator | 117 | 117 | 54 | 63 | 0 |
| Orval | 117 | 93 | 32 | 61 | 24 unsupported signatures |
| Hey API | 117 | 111 | 58 | 53 | 6 compile failures |

## 7. Compile the paper

Use Springer `llncs.cls`. The supplied PDF was compiled with Tectonic 0.17.0:

```powershell
tectonic manuscript/etaps_openapi_draft.tex --keep-logs
```

The final PDF is seven pages total: six pages of main text/data statement and one page of references. Visual render evidence was checked page by page. The canonical submitted copy is `evidence/final/ETAPS_iFS_2027_submission.pdf`.

## Scientific-integrity checks

- Synthetic mutation/control outputs live under `validation/` or `outputs/synthetic_*` and never enter generator statistics.
- `UNSUPPORTED_GENERATED_SIGNATURE` and `COMPILE_ERROR_GENERATED_SOURCE` are excluded from pass/fail denominators.
- Every `CONFIRMED_FAIL` has exactly one genuine capture and an exact individual-spec replay.
- Raw encoding adjudications are in `evidence/reviews/encoding_adjudication.json`.
- File integrity is checked with `evidence/final/SHA256SUMS.json`.
