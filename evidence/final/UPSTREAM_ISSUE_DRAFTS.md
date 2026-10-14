# Upstream issue drafts (not posted)

These drafts intentionally separate already-reported behavior from independently measured extensions. Posting requires author approval and a final check against each project's current main branch.

## OpenAPI Generator TypeScript Fetch 7.26.0: parameter styles ignored or object values routed through generic query serialization

**Prior report:** issue 22252 already documents incorrect exploded `form` object nesting. This draft should be framed as additional style/location coverage, not a duplicate novelty claim.

Environment: `@openapitools/openapi-generator-cli` 2.41.0, generator JAR 7.26.0, `typescript-fetch`, Node 24.17.0, Windows 11. Minimal specs are `outputs/corpus/c021.json`, `c034.json`, `c036.json`, and `c038.json`.

Observed after calling the generated `DefaultApi` methods:

- label/exploded object: expected `/p/.a=red.b=blue`, observed `/p/%5Bobject%20Object%5D`;
- simple/exploded header object: expected `a=red,b=blue`, observed `[object Object]`;
- non-exploded `spaceDelimited` object: expected `item=a%20red%20b%20blue`, observed deep-object query keys;
- non-exploded `pipeDelimited` object: expected `item=a%7Cred%7Cb%7Cblue`, observed deep-object query keys.

All examples validate as OpenAPI 3.1.1 and reproduce identically from isolated one-operation generation. The invoker passes the typed object to the generated method and does not serialize it.

## Orval Fetch 8.42.0: generated signatures omit header parameters and non-form styles are not serialized

**Prior report:** issue 3231 fixed the default `form`/explode behavior and explicitly noted other styles were not handled. This draft documents behavior in the post-fix 8.42.0 release.

Environment: Orval 8.42.0 Fetch target, Node 24.17.0, Windows 11. Minimal specs: `c021`, `c034`, `c037`, and `c039`.

- All 24 header operations are generated without a typed header argument. Passing `RequestInit.headers` would bypass generated parameter serialization, so no request was forced.
- label/exploded object: expected `/p/.a=red.b=blue`, observed `/p/[object%20Object]`.
- pipe-delimited array: expected `item=red%7Cblue`, observed `item=red%2Cblue`.
- deep object: expected encoded brackets `item%5Ba%5D`, observed literal brackets `item[a]` with `allowReserved=false`.

The full benchmark found 93 invokable cases, of which 61 mismatched; every mismatch reproduced from its isolated specification.

## Hey API 0.99.0 Fetch: style-sensitive wire discrepancies and valid object-delimiter specs emit uncompilable source

**Prior report:** issue 393 requested query-serialization style support. This draft supplies current-version typed SDK and compiler evidence.

Environment: `@hey-api/openapi-ts` 0.99.0, `@hey-api/client-fetch` 0.13.1, TypeScript 6.0.3, Node 24.17.0, Windows 11. Minimal specs: `c021`, `c034`, `c036`, `c037`, `c038`, and `c039`.

- label/exploded object: expected `/p/.a=red.b=blue`, observed `/p/a,red,b,blue`;
- simple/exploded header object: expected `a=red,b=blue`, observed JSON-like `{"a":"red","b":"blue"}`;
- pipe-delimited array: expected percent-encoded `%7C`, observed a literal pipe;
- deep object: expected encoded brackets, observed literal brackets;
- all six valid object-valued `spaceDelimited`/`pipeDelimited`, `explode=false` cases generate TypeScript that fails compilation (`c036`, `c038`, `c075`, `c077`, `c114`, `c116`).

The 53 eligible mismatches reproduce exactly from isolated one-operation specs. Compiler output is retained in `evidence/stage_logs/hey-api_compile.log`.

## Common attachments

For an upstream report, attach only the one-operation spec, the exact generator command, the smallest generated source excerpt, and the raw capture/compiler diagnostic. Do not attach aggregate pass rates unless maintainers ask; the minimal reproduction is the actionable evidence.
