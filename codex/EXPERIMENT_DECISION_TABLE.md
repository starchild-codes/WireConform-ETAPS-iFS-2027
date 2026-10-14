# Classification reference for Codex

| Event | Reporting class | In eligible PASS/FAIL? |
|---|---|---|
| OpenAPI spec fails independent OAS validation | INVALID_SPEC (fix study design) | No |
| Generator CLI does not support spec/target | GENERATOR_UNAVAILABLE | No |
| No generated operation or documented unsupported style | UNSUPPORTED | No |
| Generated code fails compilation/import | COMPILE_OR_IMPORT_ERROR | No |
| Adapter uses wrong typed SDK signature | ADAPTER_ERROR (repair first) | No |
| No HTTP request captured | NO_CAPTURE | No |
| More than one unambiguous request captured | MULTIPLE_CAPTURE_REVIEW | No |
| Request captured but SDK returns exception | POST_REQUEST_ERROR_REVIEW | No until reviewed |
| Raw query and decoded query differ in reserved structural delimiters | ENCODING_REVIEW | No until reviewed |
| One request captured, standard independently established, matches | PASS | Yes |
| One request captured, definite standard violation, replayed with standalone original | CONFIRMED_FAIL | Yes |
| One request captured, apparent violation but not yet reproduced | PROVISIONAL_FAIL_REVIEW | No until confirmed |
| Case not executed | NOT_RUN | No |

**Every generator has 117 defined case records in the release ledger regardless of coverage.** Include exact exclusion reason and retry notes. Do not silently omit difficult tests.
