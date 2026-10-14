# Copyable execution commands for a networked Codex machine

From the **WireConform_Codex** directory, not the parent of the ZIP:

```bash
python -m pip install -r requirements-dev.txt
bash runner/codex_stages.sh offline
bash runner/codex_stages.sh generation
```

After inspecting generated code, repairing and independently auditing SDK method adapters, create `evidence/reviews/openapi-generator_adapter_audit.json`, `.../orval_adapter_audit.json`, `.../hey-api_adapter_audit.json`. Refer to `evidence/reviews/ADAPTER_ATTESTATION_TEMPLATE.json`. Mark `audit_status: APPROVED_FOR_EXECUTION` and include exact current SHA256 of adapter and bundle only when verified. If a generator lacks header support, document separately and do not falsely attest coverage. The stage wrapper intentionally refuses to run unaudited adapters.

```bash
bash runner/codex_stages.sh pilot
# audit 14-case results and reproduce any suspected mismatch independently
bash runner/codex_stages.sh full
```

If a generator's underlying generated API signature is incompatible with the shared provisional adapter, Codex should implement reviewed generator-specific adapters and update `runner/execute_bundle_clients.py` to call the correct adapter per generator, not bypass generated serialization. Logs and SHA256 must follow the chosen adapter.

If bundling causes failures, use `runner/bootstrap_online.sh` for the frozen 14 original single-operation specs and `runner/generate_clients.py` as a fallback, then write source-audited invokers for that path. Always distinguish bundle vs single-spec outcomes in final tables.

For manuscript:

```bash
cd manuscript
pdflatex -interaction=nonstopmode -halt-on-error etaps_openapi_draft.tex
pdflatex -interaction=nonstopmode -halt-on-error etaps_openapi_draft.tex
pdfinfo etaps_openapi_draft.pdf | grep Pages
```

`llncs.cls` must be accessible through local LaTeX installation (it may be provided already). Use official LNCS template if necessary. Inspect rendered pages and count main/references, not merely total PDF pages.
