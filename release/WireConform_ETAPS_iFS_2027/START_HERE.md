# START HERE — ETAPS/iFS 2027 WireConform: Finish the Paper

**Priority: CRITICAL. Official iFS submission deadline: Thursday, 15 October 2026, Anywhere on Earth (AoE).**

This is a complete, self-contained handoff of an existing research project. The objective is to **finish a truthful, evidence-based short empirical evaluation paper and its reproducibility artifact**, not create another research outline or another synthetic-only benchmark.

**If you are Codex or another coding agent:** First read `AGENTS.md` and `codex/CODEX_FULL_TASK.md` in full. Follow them autonomously, inspect all files, use networked tooling if available, run and debug the three real generators, and complete as much as the environment permits. Do not ask the user to supply repeated context. Do not invent results. Reserve human intervention for genuinely unavoidable authorization/credentials and final submission.

## One-minute orientation

- Research question: Do generated TypeScript OpenAPI clients serialize HTTP path, query and header parameters as required by OpenAPI 3.1.1?
- Target: iFS at ETAPS 2027, **short empirical evaluation paper** (8 pages main text + 1 page references).
- Existing code: `artifact/`, `runner/`, `tests/`, `outputs/corpus/`, `outputs/bundle/`.
- Manuscript: `manuscript/etaps_openapi_draft.tex` and `.pdf`.
- Confirmed offline results on 13 Oct 2026: 117 corpus cases, 27 default pairs, 60/60 tests, 117/117 independent-reference agreement, 21/25 synthetic mutations found, 14 selected pilot cases covering seven synthetic fault classes.
- **NOT DONE:** Real SDK generation/invocation/conformance measurements. The 14-case pilot currently lacks a working audited header adapter. The existing typed SDK invoker is a candidate, NOT trustworthy evidence without review.
- Use `python -m pytest -q tests` immediately to verify you have the correct project. `requirements-dev.txt` specifies minimal Python test dependencies.

## Deliverable Codex should produce

Place completed assets under `evidence/final/` and keep editable sources in the project:

1. `evidence/final/ETAPS_iFS_2027_submission.pdf`: typeset submission draft based **only on verified empirical evidence**.
2. `manuscript/etaps_openapi_draft.tex`: corresponding compiled, up-to-date editable source.
3. `evidence/final/EXPERIMENT_RESULTS.csv`, `EXPERIMENT_RESULTS.json`: real per-case/per-generator data with denominators and exclusion statuses.
4. `evidence/final/REPRODUCE.md`: pinned commands, machine/version details, rerun directions, evidence provenance and SHA256 hashes.
5. `evidence/final/FINAL_RESEARCH_AUDIT.md`: truthfulness, novelty, possible false positives, page compliance, review checklist, remaining limitations.
6. `evidence/final/SUBMISSION_DECISION.md`: submission-ready YES/NO, with explicit reasons and fixes, no fabricated evidence.

**Do not mark as complete** if generated SDKs were not run or if conformance is inferred solely from synthetic fixtures or compiled generated-source existence. If blocked, produce the strongest honest manuscript possible, show the actual blocker, and keep a NO-GO decision for an empirical submission.

## Execute in stages

```bash
# from the WireConform_Codex directory
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
python tools/preflight.py
python runner/build_bundle.py
node validation/independent_reference.mjs outputs/corpus/manifest.json validation/reference_agreement.json
python runner/pilot_diagnostics.py
bash runner/generate_bundle_online.sh
```

Next: inspect generated files and implement/audit SDK invocations. See `codex/CODEX_FULL_TASK.md`. After the audited 14-case pilot runs, execute and validate the 117-case full study. Do not run adapters with handwritten request serialization.

## Authoritative sources

- Official submission call/deadline/categories: https://etaps.org/2027/cfp/
- OpenAPI 3.1.1 standard: https://spec.openapis.org/oas/v3.1.1.html
- OpenAPI Generator typescript-fetch: https://openapi-generator.tech/docs/generators/typescript-fetch/
- Orval Fetch: https://orval.dev/docs/guides/fetch/
- Hey API: https://heyapi.dev/docs/openapi/typescript/get-started

The official ETAPS call requires a **Data Availability Statement before references**, separate from the page limit. Short iFS empirical papers permit **8 pages of main content + 1 page of references**, use `llncs.cls`, and are submitted in PDF. The event is in person and requires an author to present if accepted. The deadline is firm. Re-verify changes on the official site.
