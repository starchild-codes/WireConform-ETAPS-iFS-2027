# ETAPS/iFS OpenAPI project — factual progress, 13 October 2026

## Completed in v0.4

| Artifact | Verified outcome | Interpretation |
|---|---:|---|
| Local Python tests | 60/60 pass | Repository integrity and offline unit tests |
| Restricted corpus | 117 specifications | Distinct OpenAPI 3.1.1 operations, not 117 SDK tests |
| Explicit-vs-implicit default pairs | 27 | RQ2 candidate comparisons, currently **no SDK captures** |
| Offline structural audit | 0 reported problems | Not official schema validation |
| Frozen normative examples | 33/33 pass | Reference cases sourced from OAS and RFC6570 examples |
| Independently written JS reference | 117/117 agree | Not a proof, and not an SDK measurement |
| Full-corpus injected faults | 21/25 detected | Synthetic error injections; four singleton-array undetectable controls |
| Redesigned 14-case pilot | 7/7 fault classes covered | Deliberate optimization on seven known synthetic mutants |
| Random subset design baseline | Mean 2.2194/7 (5,000 samples) | Uniform random baseline on same fixed corpus, not generalizable |
| Source generation optimization | 117 merged operations audited | No external generator execution completed |
| Local SDK generation | 0 | Network / installation unavailable |
| Real HTTP observations from SDKs | 0 | No eligible conformance rate |
| LNCS manuscript | 8 pages including references | Draft, NOT complete empirical paper |

## Improvements over v0.3

- Reduced projected generation overhead using a single validated merged OpenAPI workload per SDK. Material issues must still be replicated against the original single-operation specs.
- Added a completely separately implemented JavaScript restricted-reference evaluator and checked all 117 outcomes.
- Replaced first-six/previous diagnostic pilot with a fixed 14-case suite selected *before any third-party generated-client outcomes*. Both files and method are in `runner/`.
- Added SHA-256 verification of each generated source before attempting to invoke it; the provisional adapter never constructs its own request.
- Added publication-oriented infrastructure-evaluation, limitations, and conclusion sections; recompiled within eight LNCS pages total.
- Corrected Hey API code-generation launch to use a recognized root-level default configuration file instead of an ambiguous `-c` CLI flag.

## Required for scientific completion

1. Execute real generators with exact versions and capture generated-source files.
2. Inspect/validate provisional adapters against the generated signatures; correct mismatches without modifying generated serialization.
3. Run the frozen pilot and all eligible full-corpus cases; report every non-eligible status separately.
4. Independently validate representative wire mismatches with real requests, individual-case generation, a second environment, and prior issue comparison.
5. Replace the manuscript's no-results warnings with substantiated generator measurements, correct tables and final artifact link, then submit.

**Deadline: Thursday, October 15, 2026, Anywhere on Earth.** Failure to obtain real SDK results by then should trigger reconsideration of submission category, not fabricated empirical statistics.
