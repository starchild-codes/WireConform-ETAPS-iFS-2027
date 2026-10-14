# Instructions for Codex: WireConform / ETAPS iFS 2027

You are continuing an existing research project with an imminent deadline, not brainstorming. Act like a rigorous research software engineer, reproducibility auditor, and technical paper coauthor. Full requirements are in `codex/CODEX_FULL_TASK.md` and `codex/SCIENTIFIC_GUARDRAILS.md`.

## Hard requirements

- **Truth first.** Never fabricate observational results, numbers, novelty, bug reports, validations, accepted status, statistical significance, or executed commands. Never pass off synthetic tests as SDK findings.
- **Finish real experiments before polishing the paper.** A presentable PDF without real third-party results does not complete the empirical study.
- **No paid services, human participants, or proprietary API keys.** Prefer local standard CLIs, Node, Java, Python, and publicly available documentation. No user-identifying personal information in artifacts.
- **Reproducibility:** pin tools/version lockfiles, preserve generated code where licensing allows, store SHA256 of specs/adapters/observations, logs/commands/errors, and rerun instructions.
- **Separate failures**: unsupported/generation/compile/adapter/runtime/no-capture/multiple-capture/encoding-review from true eligible PASS/FAIL cases.
- **Do not bypass generated request serialization.** Call generated methods from typed SDKs; no custom query string, path, or header serialization in the invocation adapter. Verify source code method-by-method.
- **No cherry-picking.** The 117-case corpus and 14-case diagnostic pilot are frozen prior to real observations. Track exceptions. Report full population of defined cases and actual eligible denominators.
- **Do not assume previous method implementation is correct.** Inspect and independently verify the oracle, spec validity, SDK method signatures, and capture/scoring behavior. Fix defects with regression tests before interpreting SDK outcomes.
- **Deadline:** Oct 15, 2026 AoE. Optimize for real research, output, and final PDF; don't spend time on aesthetic decoration.
- **Submission:** Prepare final submission-ready files; do not make an external submission or payment without user's explicit permission.

## Immediate actions

1. Read `START_HERE.md`, `codex/CODEX_FULL_TASK.md`, `codex/SCIENTIFIC_GUARDRAILS.md` and `SUBMISSION_READINESS.md`.
2. Run unit tests and preflight; preserve log. Check internet resolution and available Java/Node/LaTeX.
3. Generate the actual SDKs, repair generator/version/config issues, check source hashes.
4. Inspect/repair adapter for query, path **AND header**. Audit exactly how values reach SDK serialization; establish a valid local capture.
5. Run the 14-case pilot for each generator; inspect and independently reproduce any failures; then all 117 cases where supported.
6. Verify standard rules and genuine defects; classify all cases with correct denominators, run default pairs, produce reproducible analysis.
7. Rewrite abstract/results/discussion/conclusion **from verified observations only**; verify novelty/prior work and page count; compile PDF and render-check.
8. Write final independent research audit and honest submission decision.

If a task fails, debug the failure and try a reasonable alternative (e.g. per-case generation instead of bundle). Record failure as evidence, not as a software correctness defect. No vague 'needs someone to do X' unless a genuine unfixable environmental or permission blocker exists.
