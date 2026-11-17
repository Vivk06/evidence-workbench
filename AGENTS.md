---
workbench:
  schema: 1
  archetypes: [code]
  git: normal
  test_budget: {max: 20, paths: [tests]}
---
# Develop evidence-workbench

Read [docs/maintaining.md](docs/maintaining.md), [docs/principles.md](docs/principles.md)
and [manifest/policy.yaml](manifest/policy.yaml) before changing the repository.
When `docs/decisions.md` exists, read its current amendments too. That private decision
log is append-only and is excluded from the public export.

## Scope and permissions

Keep shipped plugins general and self-contained. Project-specific policy belongs in
that project's instructions or optional profile. Do not change another repository or
personal client settings while developing this one.

Local checks and reversible edits are allowed. Run a project's documented environment
activation before its checks when that activation exists. Solvers, training, installs
and publishing need a separate user request. Give the user git commands at handoff
unless they explicitly ask you to run them.

Keep changes proportional to the task. Follow the project's current document and commit
conventions. Handoffs, patch series and fresh sessions are optional. This repository
chooses a ceiling of 20 tests; new user profiles do not inherit that ceiling.

## Verification

Run `bash scripts/check.sh` for bounded local checks. Never weaken a check to obtain a
passing result. Report evidence and any checks that did not run. A solver exit status
alone does not prove numerical or physical correctness.

`print-install.sh` prints commands only. `verify.sh` must not change personal settings,
credentials, databases, transcripts, caches, papers or other repositories.

## Known mistakes

- Split comma-separated source arguments into paths before using the file system.
- Read a profile only from the target's own `AGENTS.md`, rather than a parent project.
- Name test analyzers so discovery skips them, for example `audit_tests.py`.
- Cap search depth when detecting repository facts and choose the shallowest match.

The optional pre-push hook runs `scripts/check.sh`. The user enables it with
`git config core.hooksPath hooks`.
