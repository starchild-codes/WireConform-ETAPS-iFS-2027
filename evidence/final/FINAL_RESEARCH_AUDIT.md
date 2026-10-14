# Final research and submission-readiness audit

Audit date: 2026-10-14 (Asia/Calcutta). Target: ETAPS 2027 iFS short empirical evaluation paper, deadline 2026-10-15 Anywhere on Earth.

## Executive finding

The empirical study is complete and scientifically auditable. All three pinned generators were genuinely run, their typed SDK operations were invoked, eligible requests were captured on loopback, every reported mismatch was reproduced from its individual specification, and synthetic controls remain segregated. The paper compiles in Springer LNCS format to seven pages total (six pages through the mandatory data-availability statement and one reference page).

The package is **not yet externally submittable without author action** because iFS empirical papers are not covered by the iFS double-blind exception stated for regular research papers: the placeholder author block must be replaced with real names/affiliations, conflicts must be entered in EasyChair, originality/concurrent-submission assurances require human confirmation, and a human must perform the upload.

## Evidence audit

| Requirement | Status | Auditable evidence |
|---|---|---|
| Frozen OpenAPI 3.1.1 oracle | PASS | `outputs/corpus/manifest.json`, `artifact/spec_oracle.py` |
| Independent oracle comparison | PASS: 117/117 | `validation/reference_agreement.json`, `validation/independent_reference.mjs` |
| Frozen normative examples | PASS: 33 | `tests/test_normative_golden.py`, 60-test log |
| Automated suite | PASS: 60/60 | `evidence/stage_logs/final_pytest.log` |
| External OAS validation | PASS with documentation warnings only | `evidence/stage_logs/redocly_bundle.log` |
| Merged/original equivalence | PASS: 117/117 operations | `outputs/bundle/sources.json`, `experiments/bundle/source_audit.json` |
| Generator versions pinned | PASS | `package-lock.json`, `openapitools.json`, `evidence/generator_version_manifest.json` |
| Genuine generated source retained | PASS | `experiments/bundle/*/generated/`, generation JSON/logs |
| Typed adapter audit | PASS | `evidence/reviews/*_adapter_audit.json` |
| Pilot executed | PASS | `experiments/bundle/*/pilot/` |
| Full 117-case ledgers | PASS | `experiments/bundle/*/full/` |
| Encoding ambiguities adjudicated | PASS, none left pending | `evidence/reviews/encoding_adjudication.json` |
| Mismatch replay | PASS: 177/177 exact | `experiments/reproduction/`, `evidence/reviews/pilot_reproduction.json` |
| Complete mutually exclusive classifications | PASS: 351/351 | `evidence/final/EXPERIMENT_RESULTS.csv` |
| Synthetic results excluded | PASS | status provenance and separate `validation/`/`outputs/synthetic_*` paths |
| Final manuscript/PDF | PASS | `manuscript/etaps_openapi_draft.tex`, `evidence/final/ETAPS_iFS_2027_submission.pdf` |
| Visual PDF inspection | PASS: 7/7 pages | rendered page audit in `evidence/pdf_render/` |

## Numerical consistency audit

- OpenAPI Generator: 117 defined/generated/invokable/captured/eligible; 54 pass, 63 confirmed fail.
- Orval: 117 defined/generated; 93 invokable/captured/eligible; 32 pass, 61 confirmed fail; 24 unsupported generated header signatures.
- Hey API: 117 defined/generated; 111 invokable/captured/eligible; 58 pass, 53 confirmed fail; six generated-source compilation failures.
- Totals: 351 defined records, 321 eligible captures, 144 passes, 177 confirmed mismatches, 30 exclusions.
- Default pairs: OpenAPI Generator 27 equal; Orval 18 equal and nine ineligible; Hey API 27 equal.
- Individual mismatch replay: 63/63, 61/61, and 53/53 exact, zero differences.
- The manuscript abstract, results table, conclusion, CSV, JSON, and aggregate summary use the same counts.

## Scientific-integrity review

1. No handwritten or synthetic request is presented as generator evidence.
2. No unsupported signature or compilation failure appears in a pass/fail denominator.
3. Adapters configure transport and pass typed values but do not hand-serialize tested parameters.
4. Raw targets are retained; percent-encoding judgments were made against OpenAPI 3.1.1 and recorded explicitly.
5. Claims are restricted to the exact versions, Fetch targets, runtime, and flat/unreserved input domain.
6. Wilson intervals are described as finite-benchmark summaries, not population inference.
7. Existing issue reports are cited; the paper claims current-version reproduction and comparative measurement, not novelty for every defect.
8. The OpenAPI Generator warning that 3.1 support is beta is retained in generation evidence and the version scope is explicit.

## Manuscript audit

- Class: Springer `llncs.cls` v2.21 as resolved by Tectonic.
- PDF: seven letter-size pages, no encryption, JavaScript, forms, or suspicious objects.
- Length: six pages through the Data Availability Statement plus one page of references; within the iFS short limit of 8 main + 1 references. The mandatory statement is immediately before references.
- Visual review: all seven rendered pages inspected; no clipping, overlap, blank page, broken reference, missing glyph, or table overflow. Table 1 was shortened after inspection.
- All citations resolve; compilation has no undefined reference/citation. Remaining messages are benign underfull-box warnings and a local Fontconfig configuration warning that does not affect embedded Latin Modern output.
- Scope and threats are explicit; the text avoids ecosystem-wide prevalence claims.

## Official requirement check

Verified against the ETAPS 2027 joint call on 2026-10-14:

- iFS empirical evaluation papers may be short (8 pages + 1 page references).
- LNCS formatting and electronic PDF submission are required.
- A Data Availability Statement immediately before references is mandatory and page-exempt.
- Deadline is 2026-10-15 Anywhere on Earth.
- Double-blind review for iFS applies only to regular research papers, not this empirical category.
- Papers must be original, unpublished, and not simultaneously submitted; an author must attend and present if accepted.
- iFS artifact evaluation is voluntary and occurs after paper notification.

## Remaining human/external actions

1. Replace `Anonymous Author(s)` and `Affiliation withheld for review` with the actual authors and affiliations, then recompile and recheck pagination.
2. Confirm the author order, conflicts of interest, originality, and absence of concurrent submission.
3. Decide whether the artifact will be publicly archived now or prepared for voluntary post-notification artifact evaluation; replace the local-stage sentence in the Data Availability Statement if a persistent URL is created.
4. Enter metadata and upload the final PDF in the iFS EasyChair portal before the AoE deadline.
5. Confirm at least one author can attend ETAPS 2027 in Copenhagen if accepted.

No empirical or manuscript-content repair remains open.
