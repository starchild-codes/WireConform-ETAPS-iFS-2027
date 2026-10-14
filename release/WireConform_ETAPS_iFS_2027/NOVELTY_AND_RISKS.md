# Novelty/risk register — updated 13 October 2026

## Strong contribution candidates

1. Formal, restricted OpenAPI serialization oracle plus default-expansion metamorphic tests at the wire level.
2. Diagnostic pilot design that covers known synthetic fault categories with few requests.
3. Source-provenance and denominator-safe analysis framework for comparing actual generated Fetch SDKs.
4. Reproducible minimized counterexamples, **if** real generator defects are discovered and prior art checked.

## Not novel on their own

- OpenAPI serialization styles or their defaults, which are standardized.
- Existing known issues in Orval, Hey API, or OpenAPI Generator.
- A generic JSON Schema or OpenAPI contract test suite, or combining OpenAPI operation definitions in one file.
- The observation that single-element arrays can mask delimiter errors.
- An optimized synthetic fault-test set without evidence of impact on real generator behavior.

## Core risks

- **Highest:** No real generated SDKs have been executed. An empirical-evaluation submission without results is weak. Do not claim 9.5+/10 final-paper quality.
- **Next:** SDK runtime adapters may fail or inadvertently bypass generated serialization. Every adapter must be inspected against generated source; header tests remain excluded.
- **Specifications:** Official OpenAPI 3.1.1 style table and RFC 6570 are nuanced; external schema validation is pending.
- **Novelty:** Nearby studies of REST API testing and SDK generation must be revisited. Issue reports prove practical relevance, not research novelty.
- **Generalization:** Deliberately restricted ASCII corpus, convenience tool selection, and mutation-optimized pilot make any measured percentages corpus-specific.
- **Bundling:** Shared SDK helpers may cause behavior not seen in individual specifications. New failures require individual-spec reproduction.
- **Time:** October 15, 2026 is the firm official AoE deadline.

## Citation starting points

- OpenAPI Specification 3.1.1: https://spec.openapis.org/oas/v3.1.1.html
- ETAPS 2027 joint CFP: https://etaps.org/2027/cfp/
- Orval Fetch guide: https://orval.dev/docs/guides/fetch/
- OpenAPI Generator TypeScript Fetch docs: https://openapi-generator.tech/docs/generators/typescript-fetch/
- Hey API repository documentation: https://github.com/hey-api/hey-api

## Editorial red line

Never present synthetic controls as generator findings. If runtime conformance measurements are not secured, revise category/claims or do not submit as a finished empirical evaluation.
