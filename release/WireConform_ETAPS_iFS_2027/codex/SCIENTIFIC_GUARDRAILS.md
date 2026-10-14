# Scientific integrity, eligibility, and decision rules

## Definitions and mandatory distinctions

- `DEFINED`: A frozen corpus row exists (117 defined cases).
- `GENERATED`: Tool emitted client source successfully. Not proof that it compiles, invokes, or conforms.
- `COMPILE_OK`: Transpiled/type-checked appropriate generated source and dependencies (document runtime caveats).
- `INVOKE_OK`: A real generated SDK typed method accepted the intended value, without assistant/adapter manually serializing it.
- `CAPTURE_OK`: Exactly one request was observed locally and associated unambiguously with the intended case; successful invocation (exit 0).
- `PASS`: An eligible captured request matches a spec-validated oracle under the recorded comparison policy.
- `FAIL`: An eligible captured request violates a clear normative requirement, survives manual raw HTTP review and independent per-case regeneration; no known adapter/oracle flaw.
- `REVIEW`: Encoded paths/query ambiguity, environmental/compilation/transport issue, nonzero exit with capture, multiple captures, ambiguous behavior, or oracle uncertainty. Exclude from the PASS/FAIL denominator until resolved.
- `UNSUPPORTED`: Generator documents or demonstrates lack of the feature. Count separately and report support coverage.

**For headline reports:** provide `N_defined`, `N_generated`, `N_invokable`, `N_captured`, `N_eligible`, `N_pass`, `N_fail`, `N_unsupported`, `N_review`, and exact reasons. `N_pass/N_eligible` must never be presented without `N_eligible/N_defined` and relevant feature breakdowns.

## Mandatory controls

1. Freeze target OpenAPI 3.1.1 data and ensure the standard's version is recorded. Validate the input with a second, independent OAS schema validator (not solely local checks). Investigate invalid cases and decide before examining defect outcomes; never post hoc drop hard cases from denominator silently.
2. Confirm at least one ordinary control can successfully invoke and capture each generator. If not, diagnose invocation rather than labelling all tests as failures.
3. Inspect generated signatures and serialization pipeline for representative query/path/header operations. The current adapter `runner/adapters/bundle_probe.mts` is explicitly unaudited; `HEADER_NOT_ADAPTED` blocks header cases. Codex MUST repair it and preserve source audit notes. The 14-case pilot includes header cases: claims of 14 fully run tests require those to execute.
4. Be cautious with JavaScript property names, `operationId` case normalization, exports, generated-module import paths, required parameters, global fetch, headers, `baseURL` settings, and HTTP client response handling.
5. Ensure capture server returns a response acceptable to each generator (204 may cause throws despite a genuine request). The current protocol excludes nonzero invocation exits; consider a 200 JSON response or patch only server **response body**, not the request serialization. Document this to prevent systematic false exclusions.
6. Confirm the bundled 117-operation generation behaves equivalently to individual-case generation on multiple randomly selected operations AND every candidate mismatch. Record bundled-versus-single-case effect.
7. Reproduce discrepancies with clean generated outputs. Capture raw URL and case-relevant headers (remove sensitive headers before release). Do not assert defects from form-style URI encoding differences without checking OAS 3.1.1 RFC6570 structural delimiter rules.
8. Distinguish `deepObject` and non-RFC6570 rules, object field ordering, metadata default behavior, media types, and any cases the standard calls implementation-defined. Exclude genuine ambiguity and cite precise clauses.
9. Evaluate 27 default-equivalence pairs **only when both cases were run and were eligible**. Missing one side is an incomplete pair, not a success or defect.
10. No cherry-picked examples. Include all defined cases and a complete result ledger (including NOT_RUN and unsupported). Prefer conservative scope with exact verified examples over inflated benchmarks.
11. Before 'novel bug' claim, search upstream issues and related publications. Label previously known issues as reproductions, not new discoveries.
12. If experiments show no failures, report zero failures with coverage and limitations. Do not change input/data after seeing results to force a finding. If study is insufficiently novel/compelling for iFS, say so in final audit.

## Main manuscript guards

- iFS 2027 short empirical: max 8 pages main text + 1 references. `llncs.cls`. Data Availability Statement immediately before references, page-exempt per official CFP.
- Abstract must discuss real results once verified, with denominators, and not simply claimed methodology.
- No synthetic mutation as *external* validation. Synthetic tests may be auxiliary pipeline tests only.
- Do not use claims like 'novel bug' or 'first comprehensive test' without convincing literature evidence.
- Run `pdflatex` twice (or latexmk), inspect log for overfull boxes, visually render every page, count actual pages; preserve PDF and TeX.
- Use author information only if actually known to Codex/user; draft can retain placeholder until user completes submission. Empirical category is not automatically double-blind under ETAPS joint CFP, but confirm actual iFS instructions.
- Do not submit a paper that lacks a solid empirical contribution merely to beat the deadline. Final audit must state GO/NO-GO with reasons.
