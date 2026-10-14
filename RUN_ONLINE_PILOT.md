# Generator pilot — not yet run

The local execution environment has no npm registry DNS. This repository
contains an *unexecuted* GitHub Actions **generation-only** pilot, plus a CLI
script that creates reproducible per-case generation ledgers. The workflow
must be executed on a networked computer or uploaded to a repository and
manually triggered in Actions. Do **not** infer wire-level conformance from
success/failure of generation alone.

## Execution on a supported networked computer

```bash
bash runner/bootstrap_online.sh
```

This installs the three codegen CLIs locally, records all resolved package
versions, and generates the first six specifications with each generator. It
preserves full generation diagnostics in `experiments/<generator>/cNNN/` and
summary ledgers in `experiments/<generator>/generation_ledger.json`.

Then inspect and version-pin these generators. Freeze `package-lock.json`
and OpenAPI Generator's Java JAR version, replace the first-run floating
versions, and audit each generated SDK's parameter interface. **Do not pass
pre-serialized query strings or synthetic headers into invocations.** Invoke
typed API operations with raw typed values. Then separately capture requests
and score using `artifact/capture_server.py` and `artifact/score.py`. Where a
generator does not offer an API for a given parameter shape, log it as an
unsupported/unexecutable feature and include it in coverage denominators.

For the full generation step, after a verified pilot:

```bash
export PATH="$PWD/node_modules/.bin:$PATH"
python runner/generate_clients.py --generator openapi-generator
python runner/generate_clients.py --generator orval
python runner/generate_clients.py --generator hey-api
```

The script has **not** been exercised against the live npm generators in this
environment; validate its CLI arguments, JDK compatibility, and output
layout before relying on the ledger.

## Why no automatic conformance claims?

Generated client signatures are generator-version-specific. In particular,
manual injection of serialized query strings or explicit HTTP header text into
`fetch()` would bypass the SDK's own serialization logic. Doing so would
invalidate the experiment. Such adapters need inspection after installation.
