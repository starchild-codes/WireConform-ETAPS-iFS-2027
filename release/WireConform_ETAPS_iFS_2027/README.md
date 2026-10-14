# WireConform: OpenAPI-generated client conformance study

This is the completed local research artifact for the ETAPS 2027 iFS short-paper submission, *From OpenAPI to the Wire: Specification-Grounded Conformance Testing of Generated API Clients*.

## Validated empirical result

The study executed genuine generated TypeScript Fetch SDK operations against a loopback capture server. The fixed OpenAPI 3.1.1 corpus contains 117 cases and 27 implicit/explicit-default pairs.

| Generator target | Defined | Eligible captures | Pass | Confirmed wire mismatch | Other |
|---|---:|---:|---:|---:|---:|
| OpenAPI Generator 7.26.0 `typescript-fetch` | 117 | 117 | 54 | 63 | 0 |
| Orval 8.42.0 `fetch` | 117 | 93 | 32 | 61 | 24 unsupported typed header signatures |
| Hey API 0.99.0 Fetch | 117 | 111 | 58 | 53 | 6 generated-source compile failures |

Every confirmed mismatch was regenerated from its original one-operation specification and reproduced exactly: 63/63, 61/61, and 53/53. All eligible default pairs emitted equivalent requests (27/27, 18/18, and 27/27). Synthetic controls are kept separate and do not enter these counts.

## Start here

- Final manuscript: `evidence/final/ETAPS_iFS_2027_submission.pdf`
- Case-level data: `evidence/final/EXPERIMENT_RESULTS.csv` and `.json`
- Aggregate data: `evidence/final/RESULTS_SUMMARY.json`
- Reproduction guide: `evidence/final/REPRODUCE.md`
- Scientific audit: `evidence/final/FINAL_RESEARCH_AUDIT.md`
- Submission decision: `evidence/final/SUBMISSION_DECISION.md`
- Version/command record: `evidence/generator_version_manifest.json`
- Hash manifest: `evidence/final/SHA256SUMS.json`

## Artifact map

- `artifact/`: corpus oracle, validation, scoring, analysis, and synthetic controls
- `outputs/corpus/`: 117 original OpenAPI documents and manifest
- `outputs/bundle/`: verified 117-operation merged generation document
- `runner/`: generation, genuine typed invocation, capture, reproduction, and comparison scripts
- `experiments/bundle/`: generated SDKs, raw captures, ledgers, and scores
- `experiments/reproduction/`: clean one-spec mismatch replays
- `evidence/reviews/`: adapter audits and encoding adjudication
- `validation/`: independent JavaScript reference and offline controls
- `manuscript/`: LNCS source and compiled PDF
- `tests/`: 60-test automated suite

## Integrity boundary

The measured claim is restricted to the pinned versions, Fetch targets, runtime, and flat/unreserved-value corpus. Unsupported and compilation-failed cases are not counted as serialization failures. The artifact does not claim that the pass fractions estimate all APIs, all client generators, or other versions and configurations.

See `evidence/final/REPRODUCE.md` for commands and expected outcomes.
