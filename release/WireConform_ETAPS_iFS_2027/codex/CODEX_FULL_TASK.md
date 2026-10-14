# Execute-to-completion task specification — ETAPS 2027 iFS paper

## Mission

**Produce the strongest scientifically defensible, fully reproducible version of this EXISTING study by the official 15 October 2026 Anywhere-on-Earth submission deadline.** This is a focused engineering-and-research completion request, not an invitation to propose another topic. Prioritize real generator execution and independently validated empirical evidence; paper writing comes after measurements.

### Known state (never misrepresent)

- Paper: *From OpenAPI to the Wire: Specification-Grounded Conformance Testing of Generated API Clients*.
- Targets: OpenAPI Generator `typescript-fetch`, Orval `fetch`, Hey API `@hey-api/client-fetch`.
- Frozen 117 OAS 3.1.1 test specifications, 27 implicit/explicit default pairs, bundled 117-operation generation spec, Python oracle, independently written JS reference, 33 golden test examples.
- 60 passing local automated tests; 117/117 Python-JS reference agreement; 21/25 restricted artificial mutants detected in full corpus; handpicked 14-case pilot covers 7 known mutants.
- **ZERO third-party generated-SDK conformance results exist in this handoff.** Existing fixture observations and simulated defects are not real generator data.
- Existing provisional adapter is unaudited; header invocations are deliberately unsupported; source-generation scripts never successfully downloaded generators on the source machine.

### Phase 0 — Verify environment and freeze baseline (mandatory)

1. Record `date -u`, OS/CPU, Python, Node/npm, Java, TeX versions, available network. Use `python tools/preflight.py` to write `evidence/preflight.json`.
2. Run `python -m pytest -q tests`, `python artifact/validate_corpus.py outputs/corpus validation/structural_audit_v04.json`, `python runner/build_bundle.py`, independent JS reference, synthetic checks. Store logs and hashes without overwriting original pre-experiment file baselines (copy original to evidence).
3. Pin package versions in lockfiles. Avoid surprise auto-upgrades during the experiment; record all executable versions, generator flags and configs, Node/Java runtime.
4. Validate merged 117 spec and sample originals using a completely separate third-party OpenAPI validator; resolve validation errors without retrofitting cases to observed generator outputs.

### Phase 1 — Run actual generator source generation (CRITICAL PATH)

1. `bash runner/generate_bundle_online.sh`. Diagnose each failed tool individually. Fix configs/versions independently and write exact working commands to `evidence/generator_version_manifest.json`.
2. Preserve raw generation logs, package-lock.json, generated TypeScript, and source hash list; no direct edits to generated code as a proposed fix. If required, use a derived compilation-only tsconfig and explain.
3. Check generated API names/export signatures/config. `python runner/audit_generated_bundle.py` only scans names and is insufficient by itself. Record entrypoint, method signatures for representative types, serialization call chain, and whether any operation is ignored by a generator.
4. Where merged file triggers a generator-specific parsing/operation collision issue, execute the 14 frozen original per-case specs directly rather than giving up. Keep that generator's generation support separate from wire fidelity.

### Phase 2 — Typed SDK invoker and local observation (CRITICAL PATH)

1. Start from `runner/adapters/bundle_probe.mts` and `runner/execute_bundle_clients.py`. Current adapter is a candidate and specifically refuses `header` cases. Inspect actual generated TypeScript and write verified adapter calling genuine SDK methods for `path`, `query`, `header`. It is forbidden to build the path/query/header strings manually in the adapter.
2. Compile or transpile generated files with their declared dependencies. Correct import paths and ESM/CJS resolution, base URL and fetch polyfill only as needed to invoke generated clients. Track each fix and regression tests. Maintain access only to loopback `127.0.0.1:8765`.
3. Run positive smoke cases for all three generators, proving: generated method called, one HTTP request captured, expected case ID and supplied value traced, method returned successful status. If 204 causes client-side exception, modify response-only behavior of local capture server and document the change. Never patch request-serialization path in the adapter.
4. Execute frozen 14-case pilot **for each generator**. Audit all captures, especially the header examples. Eligible vs excluded statuses must follow `codex/SCIENTIFIC_GUARDRAILS.md`.
5. Confirm any initial unexpected FAIL against raw HTTP and normative OAS 3.1.1 clauses; fix oracle ambiguity before proceeding. Record all decisions to `evidence/reviews/`.

### Phase 3 — Complete full 117-case study

1. Run all 117 cases with each generator whenever supported. If bundling has abnormal effects, use per-case generation for excluded/mismatch cases; report split by protocol.
2. Preserve observations, runtime ledger, generated source hashes, adapter hashes, lockfile, run metadata, per-case spec SHA. Do not change frozen case IDs/values after viewing results.
3. Classify every one of 117 x 3 attempted cases into explicit mutually-exclusive states. Calculate **support coverage** separately from **conditional serialization conformance** with `n/N`, feature stratification by `location/style/kind/explode`, implicit-vs-explicit pair statistics, and 95% Wilson intervals *only as descriptive finite-benchmark summaries*. Avoid inferential claims about all API clients.
4. For each substantive mismatch: regenerate on clean single-case original, re-execute, independently interpret standard, inspect specific generated-source serializer, inspect known upstream issues, save minimal counterexample and command. Record 'known vs possibly new' and caveats; if appropriate, prepare upstream issue draft without posting unapproved.
5. Include negative and positive controls. Demonstrate solver catches deliberate faults but do not confuse these with independent real-world evidence. Do not optimize pilot after observing real SDK outcomes.
6. Ensure results substantiate at least one genuine contribution beyond already known issue reports: reusable conformance infrastructure, cross-tool comparisons, root-cause classes, standards-aware false-positive control, artifact and replication.

### Phase 4 — Complete manuscript (after Phase 3)

1. Read `manuscript/etaps_openapi_draft.tex` end-to-end. Revise title/abstract/introduction/RQs/method/results/discussion/threats/related work/conclusion. Make **real results** the empirical centerpiece, with precise denominators and evidence citations.
2. Remove work-in-progress notice only after its claims are no longer true. Replace frozen provisional synthetic-only results table with a table summarizing real SDK outcomes, plus meaningful case-level representative examples.
3. Preserve exactly what was measured (restricted flat values and ASCII tokens). No claim of testing all OpenAPI features or all generated API clients.
4. Differentiate known issue reports/reproductions and new findings; verify publication info, versions, original source links. Read authoritative ETAPS CFP and OpenAPI 3.1.1 clauses directly.
5. Conform to Springer LNCS `llncs.cls`, 8 pages main text plus 1 page references, mandatory pre-reference Data Availability Statement (page-exempt). Check anonymization per iFS empirical category and safe author placeholder.
6. Compile PDF, visually inspect each page for overflow, clipped tables, broken refs, weird fonts, and wrong pagination. Include figure/table if supported by executed data. Save final as `evidence/final/ETAPS_iFS_2027_submission.pdf`.
7. Write `evidence/final/EXPERIMENT_RESULTS.csv` (one row per generator-case and full classification) and .json, plus analysis scripts, `evidence/final/REPRODUCE.md`, `evidence/final/FINAL_RESEARCH_AUDIT.md`, `evidence/final/SUBMISSION_DECISION.md`. The last must be GO/NO-GO and list any unresolved external submission requirements.

### Phase 5 — Quality gate

A successful completion means: (a) generator artifacts confirmed genuine and version-pinned, (b) at least a meaningful pilot and ideally 117 full cases across 3 tools actually exercised, (c) all real results tied to captured wire requests and audited invocations, (d) any asserted bug independently reproduced, (e) complete accurate results with exclusions, (f) updated PDF/TeX and mandatory statement, (g) detailed reproduce-and-audit files, (h) self-contained final ZIP produced, (i) honest GO/NO-GO.

If these criteria cannot be satisfied, **do not claim submission-ready**. Finish the best possible verified subset, package all raw logs, explain the blocker, and put a NO-GO recommendation in the final decision. The user's time is more valuable than fabricated success.

### Additional insights and pitfalls to investigate

- OpenAPI Generator's `DefaultApi` and typed request-parameter object, plus operation names, may differ from provisional `probeC###`; inspect actual emitted code instead of guessing.
- Orval may generate a single `client.ts`, with functions whose signatures vary by location, object type or version; inspect exact current exports. Hey API plugins, `client.gen.ts`, SDK exports and base URL setup have changed across releases; verify config through current documentation.
- Capture `Handler` returns HTTP 204 (no body); some generated SDK response parsers may legitimately reject an empty response even after sending a valid request. Resolve server response to avoid inadvertently discarding valid captures.
- Path encoding and query key ordering require careful comparison; percent-encoding equivalence can obscure literal delimiters. Current `ENCODING_REVIEW` gate is intentional.
- For `form` with exploded object, generated query keys differ from the named parameter. Confirm all oracle transformations to the exact standard. Check OpenAPI 3.1.1 fixes relative to 3.1.0 examples.
- Seeded pilot's comparison to random subsets is **optimized against known synthetic faults**; this is not evidence of real-world test adequacy and should not dominate the final paper.
- ETAPS CFP: https://etaps.org/2027/cfp/ . The original iFS short empirical category and page limits MUST be checked. No publication claims without meeting evidence criteria.
