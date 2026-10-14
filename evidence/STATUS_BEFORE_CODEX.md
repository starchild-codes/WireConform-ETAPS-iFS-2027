# Evidence cutoff and truthful baseline — October 13, 2026

This handoff is a continuation of the v0.4 project, not an experiment reporting third-party SDK outcomes.

## Established via offline commands in current workspace

- `python -m pytest -q tests` — 60 passed.
- `python tools/check_handoff.py` — 117 defined cases, 14 pilot case IDs, 117 bundled operations, required files present.
- `bash runner/codex_stages.sh offline` — completed successfully; logs under `evidence/stage_logs/`.
- `node validation/independent_reference.mjs ...` — Python/JavaScript restricted reference agreement from shipped v0.4 (117/117 cases).
- Original manuscript contains eight PDF pages with work-in-progress warning and **no real-generator results**.
- DNS in this container failed for `registry.npmjs.org`, `repo.maven.apache.org`, and `github.com`; online generator installation was not executed here.

## NOT established

- No generated third-party TypeScript SDK built here.
- No third-party typed operation successfully called and captured here.
- No actual generator-level conformance rate, software bug, novel defect, or comparative performance result.
- No official external schema validator run here.
- No final submission-ready empirical paper.

All future added empirical claims must have independently reviewable generated-source and raw HTTP evidence in `experiments/` and `evidence/`.
